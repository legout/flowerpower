# -*- coding: utf-8 -*-
"""Pipeline Runner."""

from __future__ import annotations

from typing import Any, Callable
import importlib.util
from hamilton import driver
from hamilton.execution import executors
from hamilton.telemetry import disable_telemetry

if importlib.util.find_spec("opentelemetry"):
    from hamilton.plugins import h_opentelemetry

    from ..utils.open_telemetry import init_tracer
else:
    h_opentelemetry = None
    init_tracer = None

from hamilton.plugins import h_rich
from hamilton.plugins.h_threadpool import FutureAdapter
from hamilton_sdk.adapters import HamiltonTracker
from loguru import logger
from munch import Munch


if importlib.util.find_spec("distributed"):
    from dask import distributed
else:
    distributed = None


if importlib.util.find_spec("ray"):
    import ray
else:
    ray = None
from .base import BasePipeline

# Assuming Config and PipelineConfig might be needed for type hints or logic
# If not directly used, these can be removed later.
from ..cfg import Config
from ..cfg.pipeline.run import ExecutorConfig, AdapterConfig
#from .executor import get_executor

from ..fs import AbstractFileSystem, BaseStorageOptions


class PipelineRunner(BasePipeline):
    """PipelineRunner is responsible for executing a specific pipeline run.
    It handles the loading of the pipeline module, configuration, and execution"""

    def __init__(
            self,
            project_cfg: ProjectConfig,
            pipeline_cfg: PipelineConfig,
            telemetry: bool = False,
    ):
        self._project_config = project_cfg
        self._pipeline_config = pipeline_cfg
        self._telemetry = telemetry
        

    def _get_executor(self, executor:str|dict|ExecutorConfig|None=None)->tuple[executors.BaseExecutor, Callable | None]:
        """
        Get the executor based on the provided configuration.

        Args:
            executor (dict | None): Executor configuration.

        Returns:
            tuple[executors.BaseExecutor, Callable | None]: A tuple containing the executor and shutdown function.
        """
        if executor is not None:
            if isinstance(executor, str):
                executor = ExecutorConfig(type=executor)
            elif isinstance(executor, dict):
                executor = ExecutorConfig(**executor)
            elif not isinstance(executor, ExecutorConfig):
                raise TypeError("Executor must be a string, dictionary, or ExecutorConfig instance.")
            
            executor = self._pipeline_config.run.executor.merge(executor)

        if executor.type is None:
            return executors.SynchronousLocalTaskExecutor(), None

        if executor.type == "threadpool":
            return executors.MultiThreadingExecutor(max_tasks=executor.max_workers), None
        elif executor.type == "processpool":
            return executors.MultiProcessingExecutor(max_tasks=executor.max_workers), None
        elif executor.type == "ray":
            if ray:
                from hamilton.plugins import h_ray
                return (
                    h_ray.RayTaskExecutor(num_cpus=executor.num_cpus),
                    ray.shutdown,
                )
            else:
                logger.warning("Ray is not installed. Using local executor.")
                return executors.SynchronousLocalTaskExecutor(), None
        elif executor.type == "dask":
            if distributed:
                from hamilton.plugins import h_dask

                cluster = distributed.LocalCluster()
                client = distributed.Client(cluster)
                return h_dask.DaskExecutor(client=client), cluster.close
            else:
                logger.warning("Dask is not installed. Using local executor.")
                return executors.SynchronousLocalTaskExecutor(), None
        else:
            logger.warning(f"Unknown executor type: {executor.type}. Using local executor.")
            return executors.SynchronousLocalTaskExecutor(), None
        
    
    def _get_adapters(self, adapter:dict|None=None)->list:
        """
        Set the adapters for the pipeline.

        Args:
            adapter (dict): A dictionary containing adapter configurations.
        """


        for key, value in adapter.items():

            logger.info(f"Setting adapter: {key} with value: {value}")

        pass

    def



class _PipelineRunner(BasePipeline):
    """Handles the execution of a specific pipeline run."""

    def __init__(
        self,
        fs: AbstractFileSystem,
        base_dir: str,
        pipelines_dir: str,
        telemetry: bool,
        load_config_func: Callable,
        load_module_func: Callable,
        get_project_name_func: Callable[[], str],
    ):
        """Initialize PipelineRunner.

        Args:
            fs: Filesystem object.
            base_dir: Base project directory.
            pipelines_dir: Directory containing pipeline modules.
            telemetry: Flag indicating if telemetry is enabled.
            load_config_func: Function to load pipeline configuration.
            load_module_func: Function to load pipeline module.
            get_project_name_func: Function to get the project name.
        """
        self._fs = fs
        self._base_dir = base_dir
        self._pipelines_dir = pipelines_dir
        self._telemetry = telemetry
        self._load_config_func = load_config_func
        self._load_module_func = load_module_func
        self._get_project_name_func = get_project_name_func

    def _resolve_parameters(
        self, method_args: dict, config_section: Any, keys: list[str]
    ) -> dict:
        """
        Merge method arguments with config section, giving precedence to explicit arguments.
        Args:
            method_args (dict): Arguments passed to the method.
            config_section (Any): Config section (e.g., pipeline_cfg.run).
            keys (list[str]): List of keys to resolve.
        Returns:
            dict: Merged parameters.
        """
        resolved = {}
        for key in keys:
            # Check if the key exists in method_args and is not None
            if key in method_args and method_args[key] is not None:
                resolved[key] = method_args[key]
            # Otherwise, try to get it from the config section
            elif (
                hasattr(config_section, key)
                and getattr(config_section, key) is not None
            ):
                resolved[key] = getattr(config_section, key)
            # Fallback to None if not found or explicitly None in config
            else:
                resolved[key] = None  # Keep None if explicitly set or not found
        return resolved
    
    def _get_executor(self, executor:dict|None=None)->tuple[executors.BaseExecutor, Callable | None]:
        """
        Get the executor based on the provided configuration.

        Args:
            executor (dict | None): Executor configuration.

        Returns:
            tuple[executors.BaseExecutor, Callable | None]: A tuple containing the executor and shutdown function.
        """

        if executor.type is None:
            return executors.SynchronousLocalTaskExecutor(), None

        if executor.type == "threadpool":
            return executors.MultiThreadingExecutor(max_tasks=executor.max_workers), None
        elif executor.type == "processpool":
            return executors.MultiProcessingExecutor(max_tasks=executor.max_workers), None
        elif executor.type == "ray":
            if ray:
                from hamilton.plugins import h_ray
                return (
                    h_ray.RayTaskExecutor(num_cpus=executor.num_cpus),
                    ray.shutdown,
                )
            else:
                logger.warning("Ray is not installed. Using local executor.")
                return executors.SynchronousLocalTaskExecutor(), None
        elif executor.type == "dask":
            if distributed:
                from hamilton.plugins import h_dask

                cluster = distributed.LocalCluster()
                client = distributed.Client(cluster)
                return h_dask.DaskExecutor(client=client), cluster.close
            else:
                logger.warning("Dask is not installed. Using local executor.")
                return executors.SynchronousLocalTaskExecutor(), None
        else:
            logger.warning(f"Unknown executor type: {executor.type}. Using local executor.")
            return executors.SynchronousLocalTaskExecutor(), None
        

    def _get_driver(
        self,
        name: str,  # Pipeline name
        executor: dict,
        module: Any | None = None,  # Pass loaded module
        **kwargs,
    ) -> tuple[driver.Driver, Callable | None]:
        """
        Get the driver and shutdown function for a given pipeline.

        Args:
            name (str): The name of the pipeline.
            config (Config): The flowerpower configuration.
            executor (str | None, optional): The executor to use. Defaults to None.
            adapter (dict | None, optional): The adapter configuration. Defaults to None.
            driver_config (dict, optional): The driver configuration. Defaults to {}.
            module (Any | None, optional): The loaded module. Defaults to None.
            **kwargs: Additional keyword arguments for tracker/opentelemetry.

        Returns:
            tuple[driver.Driver, Callable | None]: A tuple containing the driver and shutdown function.
        """
        if module is None:
            raise ValueError(
                "Pipeline module must be loaded and passed to _get_driver."
            )

        if not self._telemetry:
            disable_telemetry()

        max_tasks = kwargs.pop("max_tasks", 20)
        num_cpus = kwargs.pop("num_cpus", 4)
        executor_, shutdown = get_executor(
            executor or "local", max_tasks=max_tasks, num_cpus=num_cpus
        )
        
        adapters = []
        if with_tracker:
            # Assume tracker config comes from pipeline_cfg or project_cfg (passed via kwargs if needed)
            # For simplicity, let's assume tracker kwargs are passed directly if needed,
            # or rely on defaults/env vars if HamiltonTracker supports it.
            # We need project_id, which might come from project_cfg.
            # Let's refine this based on how PipelineManager passes tracker details.
            # Assuming kwargs might contain tracker-specific args like project_id, username etc.
            tracker_kwargs = {
                k: v
                for k, v in kwargs.items()
                if k
                in ["project_id", "username", "dag_name", "tags", "api_url", "ui_url"]
            }
            # Map API/UI URLs if provided
            if "api_url" in tracker_kwargs:
                tracker_kwargs["hamilton_api_url"] = tracker_kwargs.pop("api_url")
            if "ui_url" in tracker_kwargs:
                tracker_kwargs["hamilton_ui_url"] = tracker_kwargs.pop("ui_url")

            # Ensure project_id is present (could be passed in kwargs)
            if tracker_kwargs.get("project_id") is None:
                # Try getting from project_name as a fallback? Or require explicit pass.
                # Let's require it for now.
                logger.warning(
                    "Tracker enabled but 'project_id' not provided in kwargs. Tracker might fail."
                )
                # raise ValueError("Tracker enabled, but 'project_id' is required.")

            # Add default dag_name if not provided
            if tracker_kwargs.get("dag_name") is None:
                tracker_kwargs["dag_name"] = f"{project_name}.{name}"

            if tracker_kwargs.get(
                "project_id"
            ):  # Only add tracker if project_id is available
                try:
                    tracker = HamiltonTracker(**tracker_kwargs)
                    adapters.append(tracker)
                    logger.info(
                        f"Hamilton Tracker enabled for project_id: {tracker_kwargs['project_id']}"
                    )
                except Exception as e:
                    logger.error(f"Failed to initialize Hamilton Tracker: {e}")
            else:
                logger.warning(
                    "Hamilton Tracker not initialized due to missing 'project_id'."
                )

        if (
            with_opentelemetry
            and h_opentelemetry is not None
            and init_tracer is not None
        ):
            otel_host = kwargs.pop("otel_host", "localhost")  # Use specific prefix
            otel_port = kwargs.pop("otel_port", 6831)
            try:
                trace = init_tracer(
                    host=otel_host,
                    port=otel_port,
                    name=f"{project_name}.{name}",
                )
                tracer = trace.get_tracer(__name__)
                adapters.append(h_opentelemetry.OpenTelemetryTracer(tracer=tracer))
                logger.info(
                    f"OpenTelemetry enabled, exporting to {otel_host}:{otel_port}"
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenTelemetry tracer: {e}")

        if with_progressbar:
            adapters.append(h_rich.RichProgressBar(run_desc=f"{project_name}.{name}"))
            logger.info("Progress bar enabled.")

        if executor == "future_adapter":
            adapters.append(FutureAdapter())
            logger.info("FutureAdapter enabled.")

        dr_builder = (
            driver.Builder()
            .enable_dynamic_execution(allow_experimental_mode=True)
            .with_modules(module)
            .with_config(config)  # Pass driver config here
            .with_local_executor(executors.SynchronousLocalTaskExecutor())
        )

        if executor_ is not None:
            dr_builder = dr_builder.with_remote_executor(executor_)
            logger.info(f"Using remote executor: {executor}")
        else:
            logger.info("Using local synchronous executor.")

        if len(adapters):
            dr_builder = dr_builder.with_adapters(*adapters)

        final_dr = dr_builder.build()
        return final_dr, shutdown

    def run(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list[str] | None = None,
        driver_config: dict | None = None,
        cache: dict | None = None,
        executor: str | dict | None = None,
        adapter: dict | None = None,
        reload: bool = False,
        **kwargs,  # Pass tracker/otel specific args here
    ) -> dict[str, Any]:
        """
        Run the pipeline with the given parameters.

        Args:
            name (str): The name of the pipeline.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            config (dict | None, optional): The config for the hamilton driver. Defaults to None.
            executor (str | None, optional): The executor to use. Defaults to None.
            adapter (dict | None, optional): The adapter configuration. Defaults to None.
            **kwargs: Additional keyword arguments for tracker/opentelemetry (e.g., project_id, otel_host).

        Returns:
            dict[str,Any]: The result of executing the pipeline.
        """
        # Load config and module using the provided functions
        # Pass reload flag to the loading functions
        cfg = self._load_config_func(name=name, reload=reload)
        pipeline_cfg = cfg.pipeline  # Access pipeline config from loaded config
        project_cfg = cfg.project  # Access project config from loaded config
        module = self._load_module_func(name=name, reload=reload)
        project_name = project_cfg.name  # Get project name via function

        logger.info(f"Starting pipeline {project_name}.{name}")

        run_params = pipeline_cfg.run  # Access run params from loaded config

        # Use _resolve_parameters for merging run flags (executor, tracker, etc.)
        method_args = locals()  # Capture args passed to run()
        keys = ["executor", "with_tracker", "with_opentelemetry", "with_progressbar"]
        # Pass the run configuration section (pipeline_cfg.pipeline.run)
        merged_run_flags = self._resolve_parameters(method_args, run_params, keys)

        # Resolve final_vars, inputs, and driver config
        final_vars = final_vars or run_params.final_vars
        # Inputs passed to run() override/add to config inputs
        inputs = {
            **(run_params.inputs or {}),
            **(inputs or {}),
        }
        # Driver config passed to run() overrides/adds to config driver config
        driver_config = {
            **(run_params.config or {}),
            **(driver_config or {}),
        }
        # Add resolved driver config to the flags passed to _get_driver
        merged_run_flags["config"] = driver_config

        # Pass loaded config and module to _get_driver
        # Pass kwargs for tracker/otel details
        dr, shutdown = self._get_driver(
            name=name,
            pipeline_cfg=pipeline_cfg,  # Pass loaded pipeline config
            project_name=project_name,  # Pass project name
            module=module,  # Pass loaded module
            **merged_run_flags,  # Pass merged executor/tracker flags etc.
            **kwargs,  # Pass through extra kwargs (e.g., project_id)
        )

        res = dr.execute(final_vars=final_vars, inputs=inputs)

        logger.success(f"Finished pipeline {project_name}.{name}")

        if shutdown is not None:
            logger.info("Shutting down executor...")
            shutdown()
            logger.info("Executor shut down.")

        return res
