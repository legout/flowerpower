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
from ..cfg.pipeline.run import ExecutorConfig, RunConfig, WithAdapterConfig
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

    def _merge_run_config_with_kwargs(self, run_config: RunConfig, kwargs: dict) -> RunConfig:
        """Merge kwargs into the run_config object.
        
        Args:
            run_config: The base RunConfig object to merge into
            kwargs: Additional parameters to merge into the run_config
            
        Returns:
            Updated RunConfig object with merged kwargs
        """
        from copy import deepcopy
        
        # Create a deep copy of the run_config to avoid modifying the original
        merged_config = deepcopy(run_config)
        
        # Handle each possible kwarg
        for key, value in kwargs.items():
            if key == 'inputs' and value is not None:
                if merged_config.inputs is None:
                    merged_config.inputs = {}
                merged_config.inputs.update(value)
            elif key == 'final_vars' and value is not None:
                if merged_config.final_vars is None:
                    merged_config.final_vars = []
                merged_config.final_vars = value
            elif key == 'config' and value is not None:
                if merged_config.config is None:
                    merged_config.config = {}
                merged_config.config.update(value)
            elif key == 'cache' and value is not None:
                merged_config.cache = value
            elif key == 'executor_cfg' and value is not None:
                if isinstance(value, str):
                    merged_config.executor = ExecutorConfig(type=value)
                elif isinstance(value, dict):
                    merged_config.executor = ExecutorConfig.from_dict(value)
                elif isinstance(value, ExecutorConfig):
                    merged_config.executor = value
            elif key == 'with_adapter_cfg' and value is not None:
                if isinstance(value, dict):
                    merged_config.with_adapter = WithAdapterConfig.from_dict(value)
                elif isinstance(value, WithAdapterConfig):
                    merged_config.with_adapter = value
            elif key == 'pipeline_adapter_cfg' and value is not None:
                merged_config.pipeline_adapter_cfg = value
            elif key == 'project_adapter_cfg' and value is not None:
                merged_config.project_adapter_cfg = value
            elif key == 'adapter' and value is not None:
                if merged_config.adapter is None:
                    merged_config.adapter = {}
                merged_config.adapter.update(value)
            elif key == 'reload' and value is not None:
                merged_config.reload = value
            elif key == 'log_level' and value is not None:
                merged_config.log_level = value
            elif key == 'max_retries' and value is not None:
                merged_config.max_retries = value
            elif key == 'retry_delay' and value is not None:
                merged_config.retry_delay = value
            elif key == 'jitter_factor' and value is not None:
                merged_config.jitter_factor = value
            elif key == 'retry_exceptions' and value is not None:
                merged_config.retry_exceptions = value
            elif key == 'on_success' and value is not None:
                merged_config.on_success = value
            elif key == 'on_failure' and value is not None:
                merged_config.on_failure = value
        
        return merged_config

    def run(
        self,
        run_config: RunConfig | None = None,
        **kwargs
    ) -> dict[str, Any]:
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
            run_config = self._merge_run_config_with_kwargs(run_config, kwargs)

        # Reload module if requested
        if run_config.reload:
            self._reload_module()

        # Set up retry configuration
        retry_config = self._setup_retry_config(
            run_config.max_retries, run_config.retry_delay, run_config.jitter_factor, run_config.retry_exceptions
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
        executor, shutdown_func, adapters = self._setup_execution_context(run_config=run_config)

        try:
            # Create Hamilton driver
            dr = (
                driver.Builder()
                .with_config(run_config.config)
                .with_modules(self.module)
                .with_adapters(*adapters)
                .build()
            )

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
        except (ImportError, ModuleNotFoundError, AttributeError) as e:
            logger.error(f"Failed to reload module for pipeline '{self.name}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reloading module for pipeline '{self.name}': {e}")
            raise
