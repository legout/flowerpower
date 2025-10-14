# -*- coding: utf-8 -*-
"""Active Pipeline class for FlowerPower."""

from __future__ import annotations

import datetime as dt
import importlib
import importlib.util
import random
import time
from typing import TYPE_CHECKING, Any, Callable
from requests.exceptions import HTTPError, ConnectionError, Timeout  # Example exception

import humanize
import msgspec
from loguru import logger
from hamilton import driver
from hamilton.execution import executors
from hamilton.registry import disable_autoload
from hamilton.telemetry import disable_telemetry
from hamilton_sdk.api.clients import UnauthorizedException
from requests.exceptions import ConnectionError, HTTPError

from .. import settings
from ..utils.adapter import create_adapter_manager
from ..utils.executor import create_executor_factory
from ..utils.logging import setup_logging


if importlib.util.find_spec("opentelemetry"):
    from hamilton.plugins import h_opentelemetry

    from ..utils.open_telemetry import init_tracer
else:
    h_opentelemetry = None
    init_tracer = None

if importlib.util.find_spec("mlflow"):
    from hamilton.plugins import h_mlflow
else:
    h_mlflow = None


if importlib.util.find_spec("distributed"):
    from dask import distributed
    from hamilton.plugins import h_dask
else:
    distributed = None

if importlib.util.find_spec("ray"):
    import ray

    # from hamilton.plugins import h_ray
    h_ray = None
else:
    ray = None
    h_ray = None

from ..cfg import PipelineConfig
from ..cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from ..cfg.pipeline.run import ExecutorConfig, RunConfig
from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from ..utils.config import merge_run_config_with_kwargs

if TYPE_CHECKING:
    from ..flowerpower import FlowerPowerProject

setup_logging(level=settings.LOG_LEVEL)


class Pipeline(msgspec.Struct):
    """Active pipeline object that encapsulates its own execution logic.

    This class represents a single pipeline with its configuration, loaded module,
    and project context. It is responsible for its own execution, including
    setting up Hamilton drivers, managing adapters, and handling retries.

    Attributes:
        name: The name of the pipeline
        config: The pipeline configuration
        module: The loaded Python module containing Hamilton functions
        project_context: Reference to the FlowerPowerProject
    """

    name: str
    config: PipelineConfig
    module: Any
    project_context: FlowerPowerProject
    _adapter_manager: Any = None
    _executor_factory: Any = None

    def __post_init__(self):
        """Initialize Hamilton settings and utility managers."""
        if not settings.HAMILTON_TELEMETRY_ENABLED:
            disable_telemetry()
        if not settings.HAMILTON_AUTOLOAD_EXTENSIONS:
            disable_autoload()

        # Initialize utility managers
        self._adapter_manager = create_adapter_manager()
        self._executor_factory = create_executor_factory()

    def run(self, run_config: RunConfig | None = None, **kwargs) -> dict[str, Any]:
        """Execute the pipeline with the given parameters.

        Args:
            run_config: Run configuration object containing all execution parameters.
                       If None, uses the pipeline's default configuration.
            **kwargs: Additional parameters to override or extend the run_config.

        Returns:
            The result of executing the pipeline
        """
        start_time = dt.datetime.now()

        # Initialize run_config with pipeline defaults if not provided
        run_config = run_config or self.config.run

        # Merge kwargs into the run_config
        if kwargs:
            run_config = merge_run_config_with_kwargs(run_config, kwargs)

        # Reload module if requested
        if run_config.reload:
            self._reload_module()

        # Set up retry configuration
        retry_config = self._setup_retry_config(
            run_config.max_retries,
            run_config.retry_delay,
            run_config.jitter_factor,
            run_config.retry_exceptions,
        )
        max_retries = retry_config["max_retries"]
        retry_delay = retry_config["retry_delay"]
        jitter_factor = retry_config["jitter_factor"]
        retry_exceptions = retry_config["retry_exceptions"]

        # Execute with retry logic
        return self._execute_with_retry(
            run_config=run_config,
            max_retries=max_retries,
            retry_delay=retry_delay,
            jitter_factor=jitter_factor,
            retry_exceptions=retry_exceptions,
            start_time=start_time,
        )

    def _setup_retry_config(
        self,
        max_retries: int | None,
        retry_delay: float | None,
        jitter_factor: float | None,
        retry_exceptions: tuple | None,
    ) -> dict:
        """Set up retry configuration with defaults and validation."""
        max_retries = max_retries or self.config.run.max_retries or 0
        retry_delay = retry_delay or self.config.run.retry_delay or 1.0
        jitter_factor = jitter_factor or self.config.run.jitter_factor or 0.1

        # Convert string exceptions to actual exception classes
        if retry_exceptions and isinstance(retry_exceptions, (list, tuple)):
            converted_exceptions = []
            # Safe mapping of exception names to classes
            exception_mapping = {
                "Exception": Exception,
                "ValueError": ValueError,
                "TypeError": TypeError,
                "RuntimeError": RuntimeError,
                "FileNotFoundError": FileNotFoundError,
                "PermissionError": PermissionError,
                "ConnectionError": ConnectionError,
                "TimeoutError": TimeoutError,
                "KeyError": KeyError,
                "AttributeError": AttributeError,
                "ImportError": ImportError,
                "OSError": OSError,
                "IOError": IOError,
                "HTTPError": HTTPError,
                "ConnectionError": ConnectionError,
                "Timeout": Timeout,
            }
            for exc in retry_exceptions:
                if isinstance(exc, str):
                    exc_class = exception_mapping.get(exc)
                    if exc_class is not None:
                        converted_exceptions.append(exc_class)
                    else:
                        logger.warning(
                            f"Unknown exception '{exc}', using Exception as fallback"
                        )
                        converted_exceptions.append(Exception)
                elif isinstance(exc, type) and issubclass(exc, BaseException):
                    converted_exceptions.append(exc)
                else:
                    logger.warning(f"Invalid exception type: {exc}, using Exception")
                    converted_exceptions.append(Exception)
            retry_exceptions = tuple(converted_exceptions)
        elif not retry_exceptions:
            retry_exceptions = (Exception,)

        return {
            "max_retries": max_retries,
            "retry_delay": retry_delay,
            "jitter_factor": jitter_factor,
            "retry_exceptions": retry_exceptions,
        }

    def _execute_with_retry(
        self,
        run_config: RunConfig,
        max_retries: int,
        retry_delay: float,
        jitter_factor: float,
        retry_exceptions: tuple,
        start_time: dt.datetime,
    ) -> dict[str, Any]:
        """Execute pipeline with retry logic."""
        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    f"🚀 Running pipeline '{self.name}' (attempt {attempt + 1}/{max_retries + 1})"
                )

                result = self._execute_pipeline(run_config=run_config)

                end_time = dt.datetime.now()
                duration = humanize.naturaldelta(end_time - start_time)

                logger.success(
                    f"✅ Pipeline '{self.name}' completed successfully in {duration}"
                )

                # Execute success callback if provided
                if run_config.on_success:
                    self._execute_callback(run_config.on_success, result, None)

                return result

            except retry_exceptions as e:
                if attempt < max_retries:
                    delay = retry_delay * (2**attempt)
                    jitter = delay * jitter_factor * random.random()
                    total_delay = delay + jitter

                    logger.warning(
                        f"⚠️  Pipeline '{self.name}' failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                    )
                    logger.info(f"🔄 Retrying in {total_delay:.2f} seconds...")
                    time.sleep(total_delay)
                else:
                    end_time = dt.datetime.now()
                    duration = humanize.naturaldelta(end_time - start_time)

                    logger.error(
                        f"❌ Pipeline '{self.name}' failed after {max_retries + 1} attempts in {duration}: {e}"
                    )

                    # Execute failure callback if provided
                    if run_config.on_failure:
                        self._execute_callback(run_config.on_failure, None, e)

                    raise
            except Exception as e:
                end_time = dt.datetime.now()
                duration = humanize.naturaldelta(end_time - start_time)

                logger.error(f"❌ Pipeline '{self.name}' failed in {duration}: {e}")

                # Execute failure callback if provided
                if run_config.on_failure:
                    self._execute_callback(run_config.on_failure, None, e)

                raise

    def _setup_execution_context(
        self,
        run_config: RunConfig,
    ) -> tuple[executors.BaseExecutor, Callable | None, list]:
        """Set up executor and adapters for pipeline execution."""
        # Get executor and adapters
        executor, shutdown_func = self._get_executor(run_config.executor)
        adapters = self._get_adapters(
            with_adapter_cfg=run_config.with_adapter,
            pipeline_adapter_cfg=run_config.pipeline_adapter_cfg,
            project_adapter_cfg=run_config.project_adapter_cfg,
            adapter=run_config.adapter,
        )
        return executor, shutdown_func, adapters

    def _execute_pipeline(
        self,
        run_config: RunConfig,
    ) -> dict[str, Any]:
        """Execute the pipeline with Hamilton."""
        # Set up execution context
        executor, shutdown_func, adapters = self._setup_execution_context(
            run_config=run_config
        )
        if (
            run_config.executor.type != "synchronous"
            or run_config.executor.type == "local"
        ):
            allow_experimental_mode = True
            synchronous_executor = False
        else:
            allow_experimental_mode = True
        try:
            # Create Hamilton driver
            dr = (
                driver.Builder()
                .with_modules(self.module)
                .with_config(run_config.config)
                .with_adapters(*adapters)
                .enable_dynamic_execution(
                    allow_experimental_mode=allow_experimental_mode
                )
                .with_local_executor(executors.SynchronousLocalTaskExecutor())
            )
            if not synchronous_executor:
                dr = dr.with_remote_executor(executor)

            dr = dr.build()

            # Execute the pipeline
            result = dr.execute(
                final_vars=run_config.final_vars,
                inputs=run_config.inputs,
            )

            return result

        finally:
            # Clean up executor if needed
            if shutdown_func:
                try:
                    shutdown_func()
                except Exception as e:
                    logger.warning(f"Failed to shutdown executor: {e}")

    def _get_executor(
        self, executor_cfg: str | dict | ExecutorConfig | None = None
    ) -> tuple[executors.BaseExecutor, Callable | None]:
        """Get the executor based on the provided configuration."""
        logger.debug("Setting up executor...")

        # Merge with default configuration
        if executor_cfg:
            if isinstance(executor_cfg, str):
                executor_cfg = ExecutorConfig(type=executor_cfg)
            elif isinstance(executor_cfg, dict):
                executor_cfg = ExecutorConfig.from_dict(executor_cfg)
            elif not isinstance(executor_cfg, ExecutorConfig):
                raise TypeError(
                    "Executor must be a string, dictionary, or ExecutorConfig instance."
                )

            executor_cfg = self.config.run.executor.merge(executor_cfg)
        else:
            executor_cfg = self.config.run.executor

        # Create executor using factory
        executor = self._executor_factory.create_executor(executor_cfg)

        # Handle special cleanup for certain executor types
        cleanup_fn = None
        if executor_cfg.type == "ray" and h_ray:
            # Handle temporary case where project_context is PipelineManager
            project_cfg = getattr(self.project_context, "project_cfg", None) or getattr(
                self.project_context, "_project_cfg", None
            )

            if project_cfg and hasattr(project_cfg.adapter, "ray"):
                cleanup_fn = (
                    ray.shutdown
                    if project_cfg.adapter.ray.shutdown_ray_on_completion
                    else None
                )

        return executor, cleanup_fn

    def _get_adapters(
        self,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
    ) -> list:
        """Set up the adapters for the pipeline."""
        logger.debug("Setting up adapters...")

        # Resolve adapter configurations using the adapter manager
        with_adapter_cfg = self._adapter_manager.resolve_with_adapter_config(
            with_adapter_cfg, self.config.run.with_adapter
        )

        pipeline_adapter_cfg = self._adapter_manager.resolve_pipeline_adapter_config(
            pipeline_adapter_cfg, self.config.adapter
        )

        project_adapter_cfg = self._adapter_manager.resolve_project_adapter_config(
            project_adapter_cfg, self.project_context
        )

        # Create adapters
        adapters = self._adapter_manager.create_adapters(
            with_adapter_cfg, pipeline_adapter_cfg, project_adapter_cfg
        )

        # Add any additional adapters
        if adapter:
            for key, value in adapter.items():
                adapters.append(value)

        return adapters

    def _execute_callback(
        self,
        callback: Callable | tuple[Callable, tuple | None, dict | None],
        result: dict[str, Any] | None,
        exception: Exception | None,
    ):
        """Execute a callback function with proper error handling."""
        try:
            if isinstance(callback, tuple):
                func, args, kwargs = callback
                args = args or ()
                kwargs = kwargs or {}
                func(*args, **kwargs)
            else:
                callback(result, exception)
        except Exception as e:
            logger.error(f"Callback execution failed: {e}")

    def _reload_module(self):
        """Reload the pipeline module."""
        try:
            importlib.reload(self.module)
            logger.debug(f"Reloaded module for pipeline '{self.name}'")
        except (ImportError, ModuleNotFoundError, AttributeError) as e:
            logger.error(f"Failed to reload module for pipeline '{self.name}': {e}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error reloading module for pipeline '{self.name}': {e}"
            )
            raise
