# -*- coding: utf-8 -*-
"""Pipeline Runner."""

from __future__ import annotations

import importlib.util
from typing import Any, Callable

from hamilton import driver
from hamilton.execution import executors
from hamilton.registry import disable_autoload
from hamilton.telemetry import disable_telemetry

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

from ..cfg import PipelineConfig, ProjectConfig
from ..cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from ..cfg.pipeline.run import ExecutorConfig, WithAdapterConfig
from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from .base import load_module

from ..utils.logging import setup_logging
setup_logging()

# from .executor import get_executor


class PipelineRunner:
    """PipelineRunner is responsible for executing a specific pipeline run.
    It handles the loading of the pipeline module, configuration, and execution"""

    def __init__(
        self,
        name: str,
        project_cfg: ProjectConfig,
        pipeline_cfg: PipelineConfig,
        telemetry: bool = False,
        autoload: bool = False,
    ):
        self.name = name
        self.project_cfg = project_cfg
        self.pipeline_cfg = pipeline_cfg
        # self._telemetry = telemetry

        if not telemetry:
            disable_telemetry()
        if not autoload:
            disable_autoload()

    def _get_executor(
        self, executor_cfg: str | dict | ExecutorConfig | None = None
    ) -> tuple[executors.BaseExecutor, Callable | None]:
        """
        Get the executor based on the provided configuration.

        Args:
            executor (dict | None): Executor configuration.

        Returns:
            tuple[executors.BaseExecutor, Callable | None]: A tuple containing the executor and shutdown function.
        """
        logger.info("Setting up executor...")
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

        if executor_cfg.type is None:
            logger.info(
                "No executor type specified. Using  SynchronousLocalTaskExecutor as default."
            )
            return executors.SynchronousLocalTaskExecutor(), None

        if executor_cfg.type == "threadpool":
            logger.info(
                f"Using MultiThreadingExecutor with max_workers={executor_cfg.max_workers}"
            )
            return executors.MultiThreadingExecutor(
                max_tasks=executor_cfg.max_workers
            ), None
        elif executor_cfg.type == "processpool":
            logger.info(
                f"Using MultiProcessingExecutor with max_workers={executor_cfg.max_workers}"
            )
            return executors.MultiProcessingExecutor(
                max_tasks=executor_cfg.max_workers
            ), None
        elif executor_cfg.type == "ray":
            if h_ray:
                logger.info(
                    f"Using RayTaskExecutor with num_cpus={executor_cfg.num_cpus}"
                )

                return (
                    h_ray.RayTaskExecutor(
                        num_cpus=executor_cfg.num_cpus,
                        ray_init_config=self.project_cfg.adapter.ray.ray_init_config,
                    ),
                    ray.shutdown
                    if self.project_cfg.adapter.ray.shutdown_ray_on_completion
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
        with_adapter_cfg: dict | WithAdapterConfig | None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
    ) -> list:
        """
        Set the adapters for the pipeline.

        Args:
            adapter (dict): A dictionary containing adapter configurations.
        """
        logger.info("Setting up adapters...")
        if with_adapter_cfg:
            if isinstance(with_adapter_cfg, dict):
                with_adapter_cfg = WithAdapterConfig.from_dict(with_adapter_cfg)
            elif not isinstance(with_adapter_cfg, WithAdapterConfig):
                raise TypeError(
                    "with_adapter must be a dictionary or WithAdapterConfig instance."
                )

            with_adapter_cfg = self.pipeline_cfg.run.with_adapter.merge(
                with_adapter_cfg
            )

        if pipeline_adapter_cfg:
            if isinstance(pipeline_adapter_cfg, dict):
                pipeline_adapter_cfg = PipelineAdapterConfig.from_dict(
                    pipeline_adapter_cfg
                )
            elif not isinstance(pipeline_adapter_cfg, PipelineAdapterConfig):
                raise TypeError(
                    "pipeline_adapter_cfg must be a dictionary or PipelineAdapterConfig instance."
                )

            pipeline_adapter_cfg = self.pipeline_cfg.run.adapter.merge(
                pipeline_adapter_cfg
            )

        if project_adapter_cfg:
            if isinstance(project_adapter_cfg, dict):
                project_adapter_cfg = ProjectAdapterConfig.from_dict(
                    project_adapter_cfg
                )
            elif not isinstance(project_adapter_cfg, ProjectAdapterConfig):
                raise TypeError(
                    "project_adapter_cfg must be a dictionary or ProjectAdapterConfig instance."
                )

            project_adapter_cfg = self.project_cfg.adapter.merge(project_adapter_cfg)

        adapters = []
        if with_adapter_cfg.tracker:
            tracker_kwargs = project_adapter_cfg.tracker.to_dict()
            tracker_kwargs.update(pipeline_adapter_cfg.tracker.to_dict())
            tracker_kwargs["hamilton_api_url"] = tracker_kwargs.pop("api_url", None)
            tracker_kwargs["hamilton_ui_url"] = tracker_kwargs.pop("ui_url", None)
            tracker = HamiltonTracker(**tracker_kwargs)
            adapters.append(tracker)

        if with_adapter_cfg.mlflow:
            if h_mlflow is None:
                logger.warning("MLFlow is not installed. Skipping MLFlow adapter.")
            else:
                mlflow_kwargs = project_adapter_cfg.mlflow.to_dict()
                mlflow_kwargs.update(pipeline_adapter_cfg.mlflow.to_dict())
                mlflow_adapter = h_mlflow.MLFlowTracker(**mlflow_kwargs)
                adapters.append(mlflow_adapter)

        if with_adapter_cfg.opentelemetry:
            if h_opentelemetry is None:
                logger.warning(
                    "OpenTelemetry is not installed. Skipping OpenTelemetry adapter."
                )
            else:
                otel_kwargs = project_adapter_cfg.opentelemetry.to_dict()
                otel_kwargs.update(pipeline_adapter_cfg.opentelemetry.to_dict())
                trace = init_tracer(**otel_kwargs, name=self.project_cfg.name)
                tracer = trace.get_tracer(self.name)
                otel_adapter = h_opentelemetry.OpenTelemetryTracer(
                    tracer_name=f"{self.project_cfg.name}.{self.name}",
                    tracer=tracer,
                )
                adapters.append(otel_adapter)

        if with_adapter_cfg.progressbar:
            adapters.append(
                h_rich.RichProgressBar(run_desc=f"{self.project_cfg.name}.{self.name}")
            )

        if with_adapter_cfg.future:
            adapters.append(FutureAdapter())

        if with_adapter_cfg.ray:
            if h_ray is None:
                logger.warning("Ray is not installed. Skipping Ray adapter.")
            else:
                ray_kwargs = project_adapter_cfg.ray.to_dict()
                ray_kwargs.update(pipeline_adapter_cfg.ray.to_dict())
                ray_adapter = h_ray.RayGraphAdapter(**ray_kwargs)
                adapters.append(ray_adapter)

        logger.info(
            f"Adapters enabled: {' | '.join([f'{adapter}: ✅' if enabled else f'{adapter}: ❌' for adapter, enabled in with_adapter_cfg.items()])}"
        )
        return adapters

    def _get_driver(
        self,
        config: dict | None = None,
        cache: dict | None = None,
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        reload: bool = False,
    ) -> tuple[driver.Driver, Callable | None]:
        """
        Get the driver and shutdown function for a given pipeline.

        Args:
            config (dict | None): The configuration for the pipeline.
            cache (dict | None): The cache configuration.
            executor_cfg (str | dict | ExecutorConfig | None): The executor to use.
                Overrides the executor settings in the pipeline config.
            with_adapter_cfg (dict | WithAdapterConfig | None): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): The pipeline adapter configuration.
                Overrides the adapter settings in the pipeline config.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): The project adapter configuration.
                Overrides the adapter settings in the project config.
            reload (bool): Whether to reload the module.


        Returns:
            tuple[driver.Driver, Callable | None]: A tuple containing the driver and shutdown function.
        """
        logger.info("Setting up driver...")
        module = load_module(name=self.name, reload=reload)
        executor, shutdown = self._get_executor(executor_cfg)
        adapters = self._get_adapters(
            with_adapter_cfg,
            pipeline_adapter_cfg,
            project_adapter_cfg,
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
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        reload: bool = False,
    ) -> dict[str, Any]:
        """
        Run the pipeline with the given parameters.
        Args:
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            config (dict | None, optional): The config for the hamilton driver. Defaults to None.
            cache (dict | None, optional): The cache configuration. Defaults to None.
            executor_cfg (str | dict | ExecutorConfig | None, optional): The executor to use.
                Overrides the executor settings in the pipeline config. Defaults to None.
            with_adapter_cfg (dict | WithAdapterConfig | None, optional): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config. Defaults to None.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None, optional): The pipeline adapter configuration.
                Overrides the adapter settings in the pipeline config. Defaults to None.
            project_adapter_cfg (dict | ProjectAdapterConfig | None, optional): The project adapter configuration.
                Overrides the adapter settings in the project config. Defaults to None.
            reload (bool, optional): Whether to reload the module. Defaults to False.

        Returns:
            dict[str, Any]: The result of executing the pipeline.
        """

        logger.info(f"Starting pipeline {self.project_cfg.name}.{self.name}")
        # Load the module and get the driver
        dr, shutdown = self._get_driver(
            config=config,
            cache=cache,
            executor_cfg=executor_cfg,
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            reload=reload,
        )
        final_vars = final_vars or self.pipeline_cfg.run.final_vars
        inputs = {
            **(self.pipeline_cfg.run.inputs or {}),
            **(inputs or {}),
        }  # <-- inputs override and/or extend config inputs

        res = dr.execute(final_vars=final_vars, inputs=inputs)

        logger.success(f"Finished pipeline {self.project_cfg.name}.{self.name}")

        if shutdown is not None:
            logger.info("Shutting down executor...")
            shutdown()
            logger.info("Executor shut down.")

        return res
