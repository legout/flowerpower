# -*- coding: utf-8 -*-
"""Pipeline Runner."""

from __future__ import annotations

import datetime as dt
import importlib.util
import random
import time
from typing import Any, Callable

import humanize
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
    from hamilton.plugins import h_ray
else:
    h_ray = None

from ..cfg import PipelineConfig
from ..cfg.adapter import AdapterConfig
from ..cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from ..cfg.pipeline.run import ExecutorConfig, RetryConfig, WithAdapterConfig
from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from ..utils.logging import setup_logging
from .base import load_module

setup_logging(level=settings.LOG_LEVEL)

# from .executor import get_executor


class PipelineRunner:
    """PipelineRunner is responsible for executing a specific pipeline run.
    It handles the loading of the pipeline module, configuration, and execution"""

    def __init__(
        self,
        project_name: str,
        pipeline_cfg: PipelineConfig,
        adapter_cfg: AdapterConfig | None = None,
        project_adapter_cfg: ProjectAdapterConfig | None = None,
    ):
        self.project_name = project_name
        if adapter_cfg is None:
            if project_adapter_cfg is None:
                project_adapter_cfg = ProjectAdapterConfig()

            self.adapter_cfg = AdapterConfig.from_adapters(
                project_hamilton_tracker_cfg=project_adapter_cfg.hamilton_tracker,
                pipeline_hamilton_tracker_cfg=pipeline_cfg.adapter.hamilton_tracker,
                project_mlflow_cfg=project_adapter_cfg.mlflow,
                pipeline_mlflow_cfg=pipeline_cfg.adapter.mlflow,
                ray_cfg=project_adapter_cfg.ray,
                opentelemetry_cfg=project_adapter_cfg.opentelemetry,
            )
        else:
            self.adapter_cfg = adapter_cfg
        self.pipeline_cfg = pipeline_cfg
        self.name = pipeline_cfg.name

        if not settings.HAMILTON_TELEMETRY_ENABLED:
            disable_telemetry()
        if not settings.HAMILTON_AUTOLOAD_EXTENSIONS:
            disable_autoload()

    def __enter__(self):
        """Enable use as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """No special cleanup required."""
        pass

    def _get_executor(
        self, executor_cfg: str | dict | ExecutorConfig | None = None
    ) -> tuple[executors.Executor, Callable | None]:
        """
        Get the executor based on the provided configuration.

        Args:
            executor (dict | None): Executor configuration.

        Returns:
            tuple[executors.Executor, Callable | None]: A tuple containing the executor and shutdown function.
        """
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

            executor_cfg = self.pipeline_cfg.run.executor.merge(executor_cfg)
        else:
            executor_cfg = self.pipeline_cfg.run.executor

        if executor_cfg.type is None:
            logger.debug(
                "No executor type specified. Using  SynchronousLocalTaskExecutor as default."
            )
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

                return (
                    h_ray.RayTaskExecutor(
                        num_cpus=executor_cfg.num_cpus,
                        ray_init_config=self.adapter_cfg.ray.ray_init_config,
                    ),
                    ray.shutdown
                    if self.adapter_cfg.ray.shutdown_ray_on_completion
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
        elif executor_cfg.type == "local":
            logger.debug("Using SynchronousLocalTaskExecutor.")
            return executors.SynchronousLocalTaskExecutor(), None
        else:
            logger.warning(
                f"Unknown executor type: {executor_cfg.type}. Using local executor."
            )
            return executors.SynchronousLocalTaskExecutor(), None

    def _get_adapters(
        self,
        with_adapter: dict | WithAdapterConfig | None = None,
        adapter_cfg: dict | AdapterConfig | None = None,
        hamilton_adapters: dict[str, Any] | None = None,
    ) -> list:
        """
        Set the adapters for the pipeline.

        Args:
            with_adapter (dict | WithAdapterConfig | None): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config.
            adapter_cfg (dict | AdapterConfig | None): The adapter configuration for the pipeline.
                Overrides the adapter settings in the pipeline config.
            hamilton_adapters (dict[str, Any] | None): Any additional hamilton adapters can be passed here.
        """
        logger.debug("Setting up adapters...")
        if with_adapter:
            if isinstance(with_adapter, dict):
                with_adapter = WithAdapterConfig.from_dict(with_adapter)
            elif not isinstance(with_adapter, WithAdapterConfig):
                raise TypeError(
                    "with_adapter must be a dictionary or WithAdapterConfig instance."
                )

            with_adapter = self.pipeline_cfg.run.with_adapter.merge(with_adapter)
        else:
            with_adapter = self.pipeline_cfg.run.with_adapter

        if adapter_cfg:
            if isinstance(adapter_cfg, dict):
                adapter_cfg = AdapterConfig.from_dict(adapter_cfg)
            elif not isinstance(adapter_cfg, AdapterConfig):
                raise TypeError(
                    "adapter_cfg must be a dictionary or AdapterConfig instance."
                )

            adapter_cfg = self.adapter_cfg.merge(adapter_cfg)
        else:
            adapter_cfg = self.adapter_cfg

        adapters = []
        if with_adapter.hamilton_tracker:
            tracker_kwargs = adapter_cfg.hamilton_tracker.to_dict()
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

        if with_adapter.mlflow:
            if h_mlflow is None:
                logger.warning("MLFlow is not installed. Skipping MLFlow adapter.")
            else:
                mlflow_kwargs = adapter_cfg.mlflow.to_dict()
                mlflow_adapter = h_mlflow.MLFlowTracker(**mlflow_kwargs)
                adapters.append(mlflow_adapter)

        if with_adapter.opentelemetry:
            if h_opentelemetry is None:
                logger.warning(
                    "OpenTelemetry is not installed. Skipping OpenTelemetry adapter."
                )
            else:
                otel_kwargs = adapter_cfg.opentelemetry.to_dict()
                trace = init_tracer(**otel_kwargs, name=self.project_name)
                tracer = trace.get_tracer(self.name)
                otel_adapter = h_opentelemetry.OpenTelemetryTracer(
                    tracer_name=f"{self.project_name}.{self.name}",
                    tracer=tracer,
                )
                adapters.append(otel_adapter)

        if with_adapter.progressbar:
            adapters.append(
                h_rich.RichProgressBar(run_desc=f"{self.project_name}.{self.name}")
            )

        if with_adapter.future:
            adapters.append(FutureAdapter())

        if with_adapter.ray:
            if h_ray is None:
                logger.warning("Ray is not installed. Skipping Ray adapter.")
            else:
                ray_kwargs = adapter_cfg.ray.to_dict()
                ray_adapter = h_ray.RayGraphAdapter(**ray_kwargs)
                adapters.append(ray_adapter)

        all_adapters = [
            f"{adp}: ✅" if enabled else f"{adp}: ❌"
            for adp, enabled in with_adapter.to_dict().items()
        ]

        if hamilton_adapters:
            adapters += list(hamilton_adapters.values())
            all_adapters += [f"{adp}: ✅" for adp in hamilton_adapters.keys()]

        logger.debug(f"Adapters enabled: {' | '.join(all_adapters)}")
        return adapters

    def _get_driver(
        self,
        config: dict | None = None,
        cache: bool | dict = False,
        executor: str | dict | ExecutorConfig | None = None,
        with_adapter: dict | WithAdapterConfig | None = None,
        adapter_cfg: dict | PipelineAdapterConfig | None = None,
        hamilton_adapters: dict[str, Any] | None = None,
        reload: bool = False,
    ) -> tuple[driver.Driver, Callable | None]:
        """
        Get the driver and shutdown function for a given pipeline.

        Args:
            config (dict | None): The configuration for the pipeline.
            cache (bool): Use cache or not.
                To fine tune the cache settings, pass a dictionary with the cache settings
                or adjust the pipeline config.
                If set to True, the default cache settings will be used.
            executor (str | dict | ExecutorConfig | None): The executor to use.
                Overrides the executor settings in the pipeline config.
            with_adapter (dict | WithAdapterConfig | None): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config.
            adapter_cfg (dict | PipelineAdapterConfig | None): The adapter configuration for the pipeline.
                Overrides the adapter settings in the pipeline config.
            hamilton_adapters (dict[str, Any] | None): Any additional Hamilton adapters can be passed here.
            reload (bool): Whether to reload the module.


        Returns:
            tuple[driver.Driver, Callable | None]: A tuple containing the driver and shutdown function.
        """
        logger.debug("Setting up driver...")
        module = load_module(name=self.name, reload=reload)
        executor, shutdown = self._get_executor(executor)
        adapters = self._get_adapters(
            with_adapter=with_adapter,
            adapter_cfg=adapter_cfg,
            hamilton_adapters=hamilton_adapters,
        )

        config = config or self.pipeline_cfg.run.config

        dr = (
            driver.Builder()
            .enable_dynamic_execution(allow_experimental_mode=True)
            .with_modules(module)
            .with_config(config)
            .with_local_executor(executors.SynchronousLocalTaskExecutor())
        )

        if cache:
            if isinstance(cache, dict):
                cache = cache or self.pipeline_cfg.run.cache
                dr = dr.with_cache(**cache)
            else:
                dr = dr.with_cache()

        if executor:
            dr = dr.with_remote_executor(executor)

        if adapters:
            dr = dr.with_adapters(*adapters)

        dr = dr.build()
        return dr, shutdown

    def run(
        self,
        inputs: dict | None = None,
        final_vars: list[str] | None = None,
        config: dict | None = None,
        cache: dict | None = None,
        executor: str | dict | ExecutorConfig | None = None,
        with_adapter: dict | WithAdapterConfig | None = None,
        adapter_cfg: dict | PipelineAdapterConfig | None = None,
        retry: dict | RetryConfig | None = None,
        hamilton_adapters: dict[str, Any] | None = None,
        reload: bool = False,
        log_level: str | None = None,
    ) -> dict[str, Any]:
        """
        Run the pipeline with the given parameters.
        Args:
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            config (dict | None, optional): The config for the hamilton driver. Defaults to None.
            cache (dict | None, optional): The cache configuration. Defaults to None.
            executor (str | dict | ExecutorConfig | None, optional): The executor to use.
                Overrides the executor settings in the pipeline config. Defaults to None.
            with_adapter_cfg (dict | WithAdapterConfig | None, optional): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config. Defaults to None.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None, optional): The pipeline adapter configuration.
                Overrides the adapter settings in the pipeline config. Defaults to None.
            project_adapter_cfg (dict | ProjectAdapterConfig | None, optional): The project adapter configuration.
                Overrides the adapter settings in the project config. Defaults to None.
            adapter (dict[str, Any] | None, optional): Any additional Hamilton adapters can be passed here. Defaults to None.
            reload (bool, optional): Whether to reload the module. Defaults to False.
            log_level (str | None, optional): The log level to use. Defaults to None.
            retry (dict | RetryConfig | None, optional): The retry configuration.
                If provided, it overrides the retry settings in the pipeline config.

        Returns:
            dict[str, Any]: The result of executing the pipeline.
        """
        self.start_time = dt.datetime.now()

        if log_level or self.pipeline_cfg.run.log_level:
            setup_logging(level=log_level or self.pipeline_cfg.run.log_level)

        logger.info(f"Starting pipeline {self.project_name}.{self.name}")

        final_vars = final_vars or self.pipeline_cfg.run.final_vars
        inputs = {
            **(self.pipeline_cfg.run.inputs or {}),
            **(inputs or {}),
        }  # <-- inputs override and/or extend config inputs

        retry = {**(self.pipeline_cfg.run.retry.to_dict() or {}), **(retry or {})}

        if not isinstance(retry.get("exceptions"), (tuple, list)):
            retry["exceptions"] = [retry["exceptions"]]
        retry["exceptions"] = [
            eval(exc) if isinstance(exc, str) else exc for exc in retry["exceptions"]
        ]

        attempts = 0
        last_exception = None

        while attempts <= retry.get("max_retries", 0):
            logger.debug(
                f"Attempting to execute pipeline {attempts}/{retry.get('max_retries', 0)}"
            )
            try:
                dr, shutdown = self._get_driver(
                    config=config,
                    cache=cache,
                    executor=executor,
                    with_adapter=with_adapter,
                    adapter_cfg=adapter_cfg,
                    hamilton_adapters=hamilton_adapters,
                    reload=reload,
                )

                res = dr.execute(final_vars=final_vars, inputs=inputs)
                self.end_time = dt.datetime.now()
                self.execution_time = self.end_time - self.start_time
                logger.success(
                    f"Finished: Pipeline {self.project_name}.{self.name} executed in {humanize.naturaldelta(self.execution_time)}"
                )

                if shutdown is not None:
                    logger.info("Shutting down executor...")
                    shutdown()
                    logger.info("Executor shut down.")

                return res
            except tuple(retry.get("exceptions", [])) as e:
                # set success to False and handle retries

                if (
                    isinstance(e, HTTPError)
                    or isinstance(e, UnauthorizedException)
                    or isinstance(e, ConnectionError)
                ):
                    if with_adapter["hamilton_tracker"]:
                        logger.info(
                            "Hamilton Tracker is enabled. Disabling tracker for the next run."
                        )
                        with_adapter["hamilton_tracker"] = False

                attempts += 1
                last_exception = e

                if attempts <= retry.get("max_retries", 0):
                    logger.warning(
                        f"Pipeline execution failed (attempt {attempts}/{retry.get('max_retries', 0)}): {e}"
                    )

                    # Calculate base delay with exponential backoff
                    base_delay = retry.get("delay", 1) * (2 ** (attempts - 1))

                    # Add jitter: random value between -jitter_factor and +jitter_factor of the base delay
                    jitter = (
                        base_delay
                        * retry.get("jitter_factor", 0.1)
                        * (2 * random.random() - 1)
                    )
                    actual_delay = max(
                        0, base_delay + jitter
                    )  # Ensure non-negative delay

                    logger.debug(
                        f"Retrying in {actual_delay:.2f} seconds (base: {base_delay:.2f}s, jitter: {jitter:.2f}s)"
                    )
                    time.sleep(actual_delay)

                else:
                    # Last attempt failed
                    logger.error(
                        f"Pipeline execution failed after {retry.get('max_retries', 3)} attempts"
                    )
                    raise last_exception


def run_pipeline(
    project_name: str,
    pipeline_cfg: PipelineConfig,
    adapter_cfg: dict | AdapterConfig | None = None,
    inputs: dict | None = None,
    final_vars: list[str] | None = None,
    config: dict | None = None,
    cache: dict | None = None,
    executor: str | dict | ExecutorConfig | None = None,
    with_adapter: dict | WithAdapterConfig | None = None,
    retry: dict | RetryConfig | None = None,
    hamilton_adapters: dict[str, Any] | None = None,
    reload: bool = False,
    log_level: str | None = None,
) -> dict[str, Any]:
    """Run the pipeline with the given parameters.

    Args:

        project_name (str): The name of the project.
        pipeline_cfg (PipelineConfig): The pipeline configuration.
        inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
        final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
        config (dict | None, optional): The config for the hamilton driver. Defaults to None.
        cache (dict | None, optional): The cache configuration. Defaults to None.
        executor (str | dict | ExecutorConfig | None, optional): The executor to use.
            Overrides the executor settings in the pipeline config. Defaults to None.
        with_adapter (dict | WithAdapterConfig | None, optional): The adapter configuration.
            Overrides the with_adapter settings in the pipeline config. Defaults to None.
        adapter_cfg (dict | AdapterConfig | None, optional): The adapter configuration for the pipeline.
            Overrides the adapter settings in the pipeline config. Defaults to None.
        retry (dict | RetryConfig | None, optional): The retry configuration.
            If provided, it overrides the retry settings in the pipeline config.
        hamilton_adapters (dict[str, Any] | None, optional): Any additional Hamilton adapters can be passed here. Defaults to None.
        reload (bool, optional): Whether to reload the module. Defaults to False.
        log_level (str | None, optional): The log level to use. Defaults to None.

    Returns:

        dict[str, Any]: The result of executing the pipeline.

    Raises:
        Exception: If the pipeline execution fails after the maximum number of retries.
    """

    with PipelineRunner(
        project_name=project_name,
        adapter_cfg=adapter_cfg,
        pipeline_cfg=pipeline_cfg,
    ) as runner:
        return runner.run(
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            cache=cache,
            executor=executor,
            with_adapter=with_adapter,
            retry=retry,
            hamilton_adapters=hamilton_adapters,
            reload=reload,
            log_level=log_level,
        )
