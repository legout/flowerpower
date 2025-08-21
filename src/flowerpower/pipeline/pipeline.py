# -*- coding: utf-8 -*-
"""Active Pipeline class for FlowerPower."""

from __future__ import annotations

import datetime as dt
import importlib
import importlib.util
import random
import time
from typing import TYPE_CHECKING, Any, Callable

import humanize
import msgspec
from hamilton import driver
from hamilton.execution import executors
from hamilton.registry import disable_autoload
from hamilton.telemetry import disable_telemetry
from hamilton_sdk.api.clients import UnauthorizedException
from requests.exceptions import ConnectionError, HTTPError

from .. import settings

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

from hamilton.plugins import h_rich
from hamilton.plugins.h_threadpool import FutureAdapter
from hamilton_sdk.adapters import HamiltonTracker
from hamilton_sdk.tracking import constants
from loguru import logger

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

from ..cfg import PipelineConfig, ProjectConfig
from ..cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from ..cfg.pipeline.run import ExecutorConfig, WithAdapterConfig
from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig

if TYPE_CHECKING:
    from ..flowerpower import FlowerPowerProject


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

    def __post_init__(self):
        """Initialize Hamilton settings."""
        if not settings.HAMILTON_TELEMETRY_ENABLED:
            disable_telemetry()
        if not settings.HAMILTON_AUTOLOAD_EXTENSIONS:
            disable_autoload()

    def run(
        self,
        inputs: dict | None = None,
        final_vars: list[str] | None = None,
        config: dict | None = None,
        cache: dict | None = None,
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,
        log_level: str | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        jitter_factor: float | None = None,
        retry_exceptions: tuple = (
            Exception,
            HTTPError,
            UnauthorizedException,
        ),
        on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
    ) -> dict[str, Any]:
        """Execute the pipeline with the given parameters.

        Args:
            inputs: Override pipeline input values
            final_vars: Specify which output variables to return
            config: Configuration for Hamilton pipeline executor
            cache: Cache configuration for results
            executor_cfg: Execution configuration
            with_adapter_cfg: Adapter settings for pipeline execution
            pipeline_adapter_cfg: Pipeline-specific adapter configuration
            project_adapter_cfg: Project-wide adapter configuration
            adapter: Additional Hamilton adapters
            reload: Whether to reload the module
            log_level: Log level for execution
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
            jitter_factor: Factor to apply for jitter
            retry_exceptions: Exceptions to catch for retries
            on_success: Callback for successful execution
            on_failure: Callback for failed execution

        Returns:
            The result of executing the pipeline
        """
        start_time = dt.datetime.now()

        # Reload module if requested
        if reload:
            self._reload_module()

        # Set up configuration with defaults from pipeline config
        inputs = inputs or self.config.run.inputs or {}
        final_vars = final_vars or self.config.run.final_vars or []
        config = {**(self.config.run.config or {}), **(config or {})}
        cache = cache or self.config.run.cache or {}

        # Set up retry configuration
        max_retries = max_retries or self.config.run.max_retries or 0
        retry_delay = retry_delay or self.config.run.retry_delay or 1.0
        jitter_factor = jitter_factor or self.config.run.jitter_factor or 0.1

        # Convert string exceptions to actual exception classes
        if retry_exceptions and isinstance(retry_exceptions, (list, tuple)):
            converted_exceptions = []
            for exc in retry_exceptions:
                if isinstance(exc, str):
                    try:
                        exc_class = eval(exc)
                        # Ensure it's actually an exception class
                        if isinstance(exc_class, type) and issubclass(
                            exc_class, BaseException
                        ):
                            converted_exceptions.append(exc_class)
                        else:
                            logger.warning(
                                f"'{exc}' is not an exception class, using Exception"
                            )
                            converted_exceptions.append(Exception)
                    except (NameError, AttributeError):
                        logger.warning(
                            f"Unknown exception type: {exc}, using Exception"
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

        # Execute with retry logic
        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    f"🚀 Running pipeline '{self.name}' (attempt {attempt + 1}/{max_retries + 1})"
                )

                result = self._execute_pipeline(
                    inputs=inputs,
                    final_vars=final_vars,
                    config=config,
                    cache=cache,
                    executor_cfg=executor_cfg,
                    with_adapter_cfg=with_adapter_cfg,
                    pipeline_adapter_cfg=pipeline_adapter_cfg,
                    project_adapter_cfg=project_adapter_cfg,
                    adapter=adapter,
                    log_level=log_level,
                )

                end_time = dt.datetime.now()
                duration = humanize.naturaldelta(end_time - start_time)

                logger.success(
                    f"✅ Pipeline '{self.name}' completed successfully in {duration}"
                )

                # Execute success callback if provided
                if on_success:
                    self._execute_callback(on_success, result, None)

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
                    if on_failure:
                        self._execute_callback(on_failure, None, e)

                    raise
            except Exception as e:
                end_time = dt.datetime.now()
                duration = humanize.naturaldelta(end_time - start_time)

                logger.error(f"❌ Pipeline '{self.name}' failed in {duration}: {e}")

                # Execute failure callback if provided
                if on_failure:
                    self._execute_callback(on_failure, None, e)

                raise

    def _execute_pipeline(
        self,
        inputs: dict,
        final_vars: list[str],
        config: dict,
        cache: dict,
        executor_cfg: str | dict | ExecutorConfig | None,
        with_adapter_cfg: dict | WithAdapterConfig | None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None,
        adapter: dict[str, Any] | None,
        log_level: str | None,
    ) -> dict[str, Any]:
        """Execute the pipeline with Hamilton."""
        # Get executor and adapters
        executor, shutdown_func = self._get_executor(executor_cfg)
        adapters = self._get_adapters(
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            adapter=adapter,
        )

        try:
            # Create Hamilton driver
            dr = (
                driver.Builder()
                .with_config(config)
                .with_modules(self.module)
                .with_adapters(*adapters)
                .build()
            )

            # Execute the pipeline
            result = dr.execute(
                final_vars=final_vars,
                inputs=inputs,
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

        if executor_cfg.type is None or executor_cfg.type == "synchronous":
            logger.debug("Using SynchronousLocalTaskExecutor as default.")
            return executors.SynchronousLocalTaskExecutor(), None

        if executor_cfg.type == "threadpool":
            logger.debug(
                f"Using MultiThreadingExecutor with max_workers={executor_cfg.max_workers}"
            )
            return executors.MultiThreadingExecutor(
                max_tasks=executor_cfg.max_workers
            ), None
        elif executor_cfg.type == "processpool":
            logger.debug(
                f"Using MultiProcessingExecutor with max_workers={executor_cfg.max_workers}"
            )
            return executors.MultiProcessingExecutor(
                max_tasks=executor_cfg.max_workers
            ), None
        elif executor_cfg.type == "ray":
            if h_ray:
                logger.debug(
                    f"Using RayTaskExecutor with num_cpus={executor_cfg.num_cpus}"
                )

                # Handle temporary case where project_context is PipelineManager
                project_cfg = getattr(
                    self.project_context, "project_cfg", None
                ) or getattr(self.project_context, "_project_cfg", None)

                return (
                    h_ray.RayTaskExecutor(
                        num_cpus=executor_cfg.num_cpus,
                        ray_init_config=project_cfg.adapter.ray.ray_init_config,
                    ),
                    ray.shutdown
                    if project_cfg.adapter.ray.shutdown_ray_on_completion
                    else None,
                )
            else:
                logger.warning("Ray is not installed. Using local executor.")
                return executors.SynchronousLocalTaskExecutor(), None
        elif executor_cfg.type == "dask":
            if distributed:
                cluster = distributed.LocalCluster()
                client = distributed.Client(cluster)
                return h_dask.DaskExecutor(client=client), cluster.close
            else:
                logger.warning("Dask is not installed. Using local executor.")
                return executors.SynchronousLocalTaskExecutor(), None
        else:
            logger.warning(
                f"Unknown executor type: {executor_cfg.type}. Using local executor."
            )
            return executors.SynchronousLocalTaskExecutor(), None

    def _get_adapters(
        self,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
    ) -> list:
        """Set up the adapters for the pipeline."""
        logger.debug("Setting up adapters...")

        # Resolve adapter configurations
        if with_adapter_cfg:
            if isinstance(with_adapter_cfg, dict):
                with_adapter_cfg = WithAdapterConfig.from_dict(with_adapter_cfg)
            elif not isinstance(with_adapter_cfg, WithAdapterConfig):
                raise TypeError(
                    "with_adapter must be a dictionary or WithAdapterConfig instance."
                )

            with_adapter_cfg = self.config.run.with_adapter.merge(with_adapter_cfg)
        else:
            with_adapter_cfg = self.config.run.with_adapter

        if pipeline_adapter_cfg:
            if isinstance(pipeline_adapter_cfg, dict):
                pipeline_adapter_cfg = PipelineAdapterConfig.from_dict(
                    pipeline_adapter_cfg
                )
            elif not isinstance(pipeline_adapter_cfg, PipelineAdapterConfig):
                raise TypeError(
                    "pipeline_adapter_cfg must be a dictionary or PipelineAdapterConfig instance."
                )

            pipeline_adapter_cfg = self.config.adapter.merge(pipeline_adapter_cfg)
        else:
            pipeline_adapter_cfg = self.config.adapter

        if project_adapter_cfg:
            if isinstance(project_adapter_cfg, dict):
                project_adapter_cfg = ProjectAdapterConfig.from_dict(
                    project_adapter_cfg
                )
            elif not isinstance(project_adapter_cfg, ProjectAdapterConfig):
                raise TypeError(
                    "project_adapter_cfg must be a dictionary or ProjectAdapterConfig instance."
                )

            # Handle temporary case where project_context is PipelineManager
            manager_project_cfg = getattr(
                self.project_context, "project_cfg", None
            ) or getattr(self.project_context, "_project_cfg", None)
            if manager_project_cfg and hasattr(manager_project_cfg, "adapter"):
                project_adapter_cfg = manager_project_cfg.adapter.merge(
                    project_adapter_cfg
                )
            else:
                # Use project context directly if it's FlowerPowerProject
                if hasattr(self.project_context, "pipeline_manager"):
                    pm_cfg = getattr(
                        self.project_context.pipeline_manager, "project_cfg", None
                    ) or getattr(
                        self.project_context.pipeline_manager, "_project_cfg", None
                    )
                    base_cfg = pm_cfg.adapter if pm_cfg else None
                    if base_cfg:
                        project_adapter_cfg = base_cfg.merge(project_adapter_cfg)
                    else:
                        from ..cfg.project.adapter import \
                            AdapterConfig as ProjectAdapterConfig

                        project_adapter_cfg = ProjectAdapterConfig()
                else:
                    from ..cfg.project.adapter import \
                        AdapterConfig as ProjectAdapterConfig

                    project_adapter_cfg = ProjectAdapterConfig()
        else:
            # Handle temporary case where project_context is PipelineManager
            manager_project_cfg = getattr(
                self.project_context, "project_cfg", None
            ) or getattr(self.project_context, "_project_cfg", None)
            if manager_project_cfg and hasattr(manager_project_cfg, "adapter"):
                project_adapter_cfg = manager_project_cfg.adapter
            else:
                # Use project context directly if it's FlowerPowerProject
                if hasattr(self.project_context, "pipeline_manager"):
                    pm_cfg = getattr(
                        self.project_context.pipeline_manager, "project_cfg", None
                    ) or getattr(
                        self.project_context.pipeline_manager, "_project_cfg", None
                    )
                    project_adapter_cfg = pm_cfg.adapter if pm_cfg else None
                else:
                    project_adapter_cfg = None

            # Create default adapter config if none found
            if project_adapter_cfg is None:
                from ..cfg.project.adapter import \
                    AdapterConfig as ProjectAdapterConfig

                project_adapter_cfg = ProjectAdapterConfig()

        adapters = []

        # Hamilton Tracker adapter
        if with_adapter_cfg.hamilton_tracker:
            tracker_kwargs = project_adapter_cfg.hamilton_tracker.to_dict()
            tracker_kwargs.update(pipeline_adapter_cfg.hamilton_tracker.to_dict())
            tracker_kwargs["hamilton_api_url"] = tracker_kwargs.pop("api_url", None)
            tracker_kwargs["hamilton_ui_url"] = tracker_kwargs.pop("ui_url", None)

            constants.MAX_DICT_LENGTH_CAPTURE = (
                tracker_kwargs.pop("max_dict_length_capture", None)
                or settings.HAMILTON_MAX_DICT_LENGTH_CAPTURE
            )
            constants.MAX_LIST_LENGTH_CAPTURE = (
                tracker_kwargs.pop("max_list_length_capture", None)
                or settings.HAMILTON_MAX_LIST_LENGTH_CAPTURE
            )
            constants.CAPTURE_DATA_STATISTICS = (
                tracker_kwargs.pop("capture_data_statistics", None)
                or settings.HAMILTON_CAPTURE_DATA_STATISTICS
            )

            tracker = HamiltonTracker(**tracker_kwargs)
            adapters.append(tracker)

        # MLFlow adapter
        if with_adapter_cfg.mlflow:
            if h_mlflow is None:
                logger.warning("MLFlow is not installed. Skipping MLFlow adapter.")
            else:
                mlflow_kwargs = project_adapter_cfg.mlflow.to_dict()
                mlflow_kwargs.update(pipeline_adapter_cfg.mlflow.to_dict())
                mlflow_adapter = h_mlflow.MLFlowTracker(**mlflow_kwargs)
                adapters.append(mlflow_adapter)

        # OpenTelemetry adapter
        if with_adapter_cfg.opentelemetry:
            if h_opentelemetry is None:
                logger.warning(
                    "OpenTelemetry is not installed. Skipping OpenTelemetry adapter."
                )
            else:
                otel_kwargs = project_adapter_cfg.opentelemetry.to_dict()
                otel_kwargs.update(pipeline_adapter_cfg.opentelemetry.to_dict())
                init_tracer()
                otel_adapter = h_opentelemetry.OpenTelemetryTracker(**otel_kwargs)
                adapters.append(otel_adapter)

        # Progress bar adapter
        if with_adapter_cfg.progressbar:
            progressbar_kwargs = project_adapter_cfg.progressbar.to_dict()
            progressbar_kwargs.update(pipeline_adapter_cfg.progressbar.to_dict())
            progressbar_adapter = h_rich.ProgressBar(**progressbar_kwargs)
            adapters.append(progressbar_adapter)

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
        except Exception as e:
            logger.error(f"Failed to reload module for pipeline '{self.name}': {e}")
            raise
