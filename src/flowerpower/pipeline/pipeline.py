import datetime as dt
import importlib
import os
import posixpath
import random
import sys
import time
from types import TracebackType
from typing import Any, Callable

import humanize
import rich
from hamilton import driver
from hamilton.execution import executors
from hamilton.plugins import h_rich
from hamilton.plugins.h_threadpool import FutureAdapter
from hamilton.registry import disable_autoload
from hamilton.telemetry import disable_telemetry
from hamilton_sdk.adapters import HamiltonTracker
from hamilton_sdk.api.clients import UnauthorizedException
from hamilton_sdk.tracking import constants
from loguru import logger
from munch import Munch
from requests.exceptions import ConnectionError, HTTPError

from .. import settings
from ..cfg import PipelineConfig, ProjectConfig
from ..cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from ..cfg.pipeline.run import ExecutorConfig, RetryConfig, WithAdapterConfig
from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from ..fs import AbstractFileSystem, BaseStorageOptions, get_filesystem
from ..utils.logging import setup_logging
from ..utils.templates import PIPELINE_PY_TEMPLATE

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
    from hamilton.plugins import h_ray
else:
    h_ray = None


setup_logging(level=settings.LOG_LEVEL)


def load_module(name: str, reload: bool = False):
    """
    Load a module.

    Args:
        name (str): The name of the module.

    Returns:
        module: The loaded module.
    """
    if name in sys.modules:
        if reload:
            return importlib.reload(sys.modules[name])
        return sys.modules[name]
    return importlib.import_module(name)




class PipelineRunner:
    """PipelineRunner is responsible for executing a specific pipeline run.
    It handles the loading of the pipeline module, configuration, and execution"""

    def __init__(
        self,
        project_cfg: ProjectConfig,
        pipeline_cfg: PipelineConfig,
    ):
        self.project_cfg = project_cfg
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
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
    ) -> list:
        """
        Set the adapters for the pipeline.

        Args:
            with_adapter_cfg (dict | WithAdapterConfig | None): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): The pipeline adapter configuration.
                Overrides the adapter settings in the pipeline config.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): The project adapter configuration.
                Overrides the adapter settings in the project config.
            adapter (dict[str, Any] | None): Any additional hamilton adapters can be passed here.
        """
        logger.debug("Setting up adapters...")
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
        else:
            with_adapter_cfg = self.pipeline_cfg.run.with_adapter

        if pipeline_adapter_cfg:
            if isinstance(pipeline_adapter_cfg, dict):
                pipeline_adapter_cfg = PipelineAdapterConfig.from_dict(
                    pipeline_adapter_cfg
                )
            elif not isinstance(pipeline_adapter_cfg, PipelineAdapterConfig):
                raise TypeError(
                    "pipeline_adapter_cfg must be a dictionary or PipelineAdapterConfig instance."
                )

            pipeline_adapter_cfg = self.pipeline_cfg.adapter.merge(pipeline_adapter_cfg)
        else:
            pipeline_adapter_cfg = self.pipeline_cfg.adapter

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
        else:
            project_adapter_cfg = self.project_cfg.adapter

        adapters = []
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

        all_adapters = [
            f"{adp}: ✅" if enabled else f"{adp}: ❌"
            for adp, enabled in with_adapter_cfg.to_dict().items()
        ]

        if adapter:
            adapters += list(adapter.values())
            all_adapters += [f"{adp}: ✅" for adp in adapter.keys()]

        logger.debug(f"Adapters enabled: {' | '.join(all_adapters)}")
        return adapters

    def _get_driver(
        self,
        config: dict | None = None,
        cache: bool | dict = False,
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
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
            executor_cfg (str | dict | ExecutorConfig | None): The executor to use.
                Overrides the executor settings in the pipeline config.
            with_adapter_cfg (dict | WithAdapterConfig | None): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): The pipeline adapter configuration.
                Overrides the adapter settings in the pipeline config.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): The project adapter configuration.
                Overrides the adapter settings in the project config.
            adapter (dict[str, Any] | None): Any additional Hamilton adapters can be passed here.
            reload (bool): Whether to reload the module.


        Returns:
            tuple[driver.Driver, Callable | None]: A tuple containing the driver and shutdown function.
        """
        logger.debug("Setting up driver...")
        module = load_module(name=self.name, reload=reload)
        executor, shutdown = self._get_executor(executor_cfg)
        adapters = self._get_adapters(
            with_adapter_cfg,
            pipeline_adapter_cfg,
            project_adapter_cfg,
            adapter=adapter,
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
        retry: dict | RetryConfig | None = None,
        hamilton_adapter: dict[str, Any] | None = None,
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
            executor_cfg (str | dict | ExecutorConfig | None, optional): The executor to use.
                Overrides the executor settings in the pipeline config. Defaults to None.
            with_adapter_cfg (dict | WithAdapterConfig | None, optional): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config. Defaults to None.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None, optional): The pipeline adapter configuration.
                Overrides the adapter settings in the pipeline config. Defaults to None.
            project_adapter_cfg (dict | ProjectAdapterConfig | None, optional): The project adapter configuration.
                Overrides the adapter settings in the project config. Defaults to None.
            hamilton_adapter (dict[str, Any] | None, optional): Any additional Hamilton adapters can be passed here. Defaults to None.
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

        logger.info(f"Starting pipeline {self.project_cfg.name}.{self.name}")

        final_vars = final_vars or self.pipeline_cfg.run.final_vars
        inputs = {
            **(self.pipeline_cfg.run.inputs.to_ or {}),
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
                    executor_cfg=executor_cfg,
                    with_adapter_cfg=with_adapter_cfg,
                    pipeline_adapter_cfg=pipeline_adapter_cfg,
                    project_adapter_cfg=project_adapter_cfg,
                    adapter=hamilton_adapter,
                    reload=reload,
                )

                res = dr.execute(final_vars=final_vars, inputs=inputs)
                self.end_time = dt.datetime.now()
                self.execution_time = self.end_time - self.start_time
                logger.success(
                    f"Finished: Pipeline {self.project_cfg.name}.{self.name} executed in {humanize.naturaldelta(self.execution_time)}"
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
                    if with_adapter_cfg["hamilton_tracker"]:
                        logger.info(
                            "Hamilton Tracker is enabled. Disabling tracker for the next run."
                        )
                        with_adapter_cfg["hamilton_tracker"] = False

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


class Pipeline:
    """
    Base class for all pipelines.
    """

    def __init__(
        self,
        name: str | None = None,
        base_dir: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions = {},
        fs: AbstractFileSystem | None = None,
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        project_cfg: ProjectConfig | None = None,
        # job_queue_type: str | None = None,  # New parameter for worker backend
    ):
        self.name = name
        self._base_dir = base_dir or os.getcwd()
        self._storage_options = storage_options
        if fs is None:
            fs = get_filesystem(self._base_dir, **self._storage_options)
        self._fs = fs
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        # self._job_queue_type = job_queue_type
        self._cfg = self._load_pipeline_cfg
        self._project_cfg = project_cfg or self._load_project_cfg

        try:
            self._fs.makedirs(f"{self._cfg_dir}/pipelines", exist_ok=True)
            self._fs.makedirs(self._pipelines_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")

        self._add_modules_path()

    def __enter__(self) -> "Pipeline":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    def _add_modules_path(self):
        """
        Sync the filesystem.

        Returns:
            None
        """
        if self._fs.is_cache_fs:
            self._fs.sync_cache()
            modules_path = posixpath.join(
                self._fs._mapper.directory, self._fs.cache_path, self._pipelines_dir
            )
        else:
            modules_path = posixpath.join(self._fs.path, self._pipelines_dir)
        if modules_path not in sys.path:
            sys.path.insert(0, modules_path)

    def _load_project_cfg(self) -> ProjectConfig:
        """
        Load the project configuration.

        Returns:
            ProjectConfig: The loaded project configuration.
        """
        return ProjectConfig.load(
            base_dir=self._base_dir,
            job_queue_type=self._job_queue_type,
            fs=self._fs,
            storage_options=self._storage_options,
        )

    def _load_pipeline_cfg(self) -> PipelineConfig:
        """
        Load the pipeline configuration.

        Returns:
            PipelineConfig: The loaded pipeline configuration.
        """
        return PipelineConfig.load(
            base_dir=self._base_dir,
            name=self.name,
            fs=self._fs,
            storage_options=self._storage_options,
        )

    @property
    def cfg(self) -> PipelineConfig:
        """
        Get the pipeline configuration.

        Returns:
            PipelineConfig: The pipeline configuration.
        """
        if not isinstance(self._cfg, PipelineConfig):
            self._cfg = self._load_pipeline_cfg()
        return self._cfg

    @property
    def project_cfg(self) -> ProjectConfig:
        """
        Get the project configuration.

        Returns:
            ProjectConfig: The project configuration.
        """
        if not isinstance(self._project_cfg, ProjectConfig):
            self._project_cfg = self._load_project_cfg()
        return self._project_cfg

    # --- Methods moved from PipelineManager ---
    def new(self, name: str, overwrite: bool = False):
        """
        Adds a pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool): Whether to overwrite an existing pipeline. Defaults to False.
            job_queue_type (str | None): The type of worker to use. Defaults to None.

        Raises:
            ValueError: If the configuration or pipeline path does not exist, or if the pipeline already exists.

        Examples:
            >>> pm = PipelineManager()
            >>> pm.new("my_pipeline")
        """
        # Use attributes derived from self.project_cfg
        for dir_path, label in (
            (self._cfg_dir, "configuration"),
            (self._pipelines_dir, "pipeline"),
        ):
            if not self._fs.exists(dir_path):
                raise ValueError(
                    f"{label.capitalize()} path {dir_path} does not exist. Please run flowerpower init first."
                )

        formatted_name = name.replace(".", "/").replace("-", "_")
        pipeline_file = posixpath.join(self._pipelines_dir, f"{formatted_name}.py")
        cfg_file = posixpath.join(self._cfg_dir, "pipelines", f"{formatted_name}.yml")

        def check_and_handle(path: str):
            if self._fs.exists(path):
                if overwrite:
                    self._fs.rm(path)
                else:
                    raise ValueError(
                        f"Pipeline {self.project_cfg.name}.{formatted_name} already exists. Use `overwrite=True` to overwrite."
                    )

        check_and_handle(pipeline_file)
        check_and_handle(cfg_file)

        # Ensure directories for the new files exist
        for file_path in (pipeline_file, cfg_file):
            self._fs.makedirs(file_path.rsplit("/", 1)[0], exist_ok=True)

        # Write pipeline code template
        with self._fs.open(pipeline_file, "w") as f:
            f.write(
                PIPELINE_PY_TEMPLATE.format(
                    name=name,
                    date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
            )

        # Create default pipeline config and save it directly
        new_pipeline_cfg = PipelineConfig(name=name)
        new_pipeline_cfg.save(fs=self._fs)  # Save only the pipeline part

        rich.print(
            f"🔧 Created new pipeline [bold blue]{self.project_cfg.name}.{name}[/bold blue]"
        )

    def delete(self, name: str, cfg: bool = True, module: bool = False):
        """
        Delete a pipeline.

        Args:
            name (str): The name of the pipeline.
            cfg (bool, optional): Whether to delete the config file. Defaults to True.
            module (bool, optional): Whether to delete the module file. Defaults to False.

        Returns:
            None

        Raises:
            FileNotFoundError: If the specified files do not exist.

        Examples:
            >>> pm = PipelineManager()
            >>> pm.delete("my_pipeline")
        """
        deleted_files = []
        if cfg:
            pipeline_cfg_path = posixpath.join(
                self._cfg_dir, "pipelines", f"{name}.yml"
            )
            if self._fs.exists(pipeline_cfg_path):
                self._fs.rm(pipeline_cfg_path)
                deleted_files.append(pipeline_cfg_path)
                logger.debug(
                    f"Deleted pipeline config: {pipeline_cfg_path}"
                )  # Changed to DEBUG
            else:
                logger.warning(
                    f"Config file not found, skipping deletion: {pipeline_cfg_path}"
                )

        if module:
            pipeline_py_path = posixpath.join(self._pipelines_dir, f"{name}.py")
            if self._fs.exists(pipeline_py_path):
                self._fs.rm(pipeline_py_path)
                deleted_files.append(pipeline_py_path)
                logger.debug(
                    f"Deleted pipeline module: {pipeline_py_path}"
                )  # Changed to DEBUG
            else:
                logger.warning(
                    f"Module file not found, skipping deletion: {pipeline_py_path}"
                )

        if not deleted_files:
            logger.warning(
                f"No files found or specified for deletion for pipeline '{name}'."
            )

        # Sync filesystem if needed (using _fs)
        if hasattr(self._fs, "sync_cache") and callable(
            getattr(self._fs, "sync_cache")
        ):
            self._fs.sync_cache()
