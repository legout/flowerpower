import datetime as dt
import importlib
import importlib.util
import posixpath
import sys
from typing import Any, Callable
from uuid import UUID

from .fs import AbstractFileSystem
from hamilton import driver
from hamilton.execution import executors
from hamilton.telemetry import disable_telemetry

if importlib.util.find_spec("opentelemetry"):
    from hamilton.plugins import h_opentelemetry

    from .utils.open_telemetry import init_tracer

else:
    h_opentelemetry = None
    init_tracer = None
import rich
from hamilton.plugins import h_tqdm
from hamilton.plugins.h_threadpool import FutureAdapter
from hamilton_sdk.adapters import HamiltonTracker
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from .cfg import (  # PipelineRunConfig,; PipelineScheduleConfig,; PipelineTrackerConfig,
    Config,
    PipelineConfig,
)
from .fs import get_filesystem
from .fs.storage_options import BaseStorageOptions
from .utils.misc import view_img
from .utils.templates import PIPELINE_PY_TEMPLATE

# Import the new Worker class
from .worker import Worker #, BaseWorker, BaseTrigger # BaseWorker/BaseTrigger potentially needed for typing

# Keep conditional import for opentelemetry and other plugins
if importlib.util.find_spec("opentelemetry"):
    # ... (rest of conditional imports remain the same)
    pass # Placeholder, original code follows

# Remove the old SchedulerManager logic
# SchedulerManager = None # Removed
from pathlib import Path
from types import TracebackType

# if importlib.util.find_spec("paho"):
#     from .mqtt import MQTTClient
# else:
#     MQTTClient = None
from munch import Munch

from .worker.apscheduler.trigger import get_trigger  # Updated path
from .utils.executor import get_executor


class PipelineManager:
    def __init__(
        self,
        base_dir: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions = {},
        fs: AbstractFileSystem | None = None,
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        telemetry: bool = True,
        worker_type: str = "apscheduler",  # New parameter for worker backend
    ):
        """
        Initializes the Pipeline object.

        Args:
            base_dir (str | None): The flowerpower base path. Defaults to None.
            storage_options (dict | Munch | BaseStorageOptions, optional): The storage options. Defaults to {}.
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.

        Returns:
            None
        """
        self._telemetry = telemetry
        self._base_dir = base_dir or str(Path.cwd())
        self._storage_options = storage_options or {}
        if fs is None:
            fs = get_filesystem(self._base_dir, **self._storage_options)
        self._fs = fs

        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        self._worker_type = worker_type  # Store worker_type

        try:
            self._fs.makedirs(f"{self._cfg_dir}/pipelines", exist_ok=True)
            self._fs.makedirs(self._pipelines_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")

        self._sync_fs()
        self.load_config()

    def __enter__(self) -> "PipelineManager":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # Add any cleanup code here if needed
        pass

    def _get_schedules(self):
        # TODO: Make worker_type configurable, potentially via self.cfg.project.worker
        with Worker(
            type=self._worker_type,  # Use configured worker_type
            fs=self._fs,
            base_dir=self._base_dir,
            storage_options=self._storage_options,
            # name="schedule_reader" # Optional name
        ) as worker:
            return worker.get_schedules()
    def _sync_fs(self):
        """
        Sync the filesystem.

        Returns:
            None
        """
        if self._fs.is_cache_fs:
            self._fs.sync()

        modules_path = posixpath.join(self._fs.path, self._pipelines_dir)
        if modules_path not in sys.path:
            sys.path.append(modules_path)

    def load_module(self, name: str, reload: bool = False):
        """
        Load a module dynamically.

        Args:
            name (str): The name of the module to load.

        Returns:
            None
        """
        sys.path.append(posixpath.join(self._fs.path, self._pipelines_dir))

        if not hasattr(self, "_module"):
            self._module = importlib.import_module(name)

        else:
            if reload:
                importlib.reload(self._module)

    def load_config(self, name: str | None = None, reload: bool = False):
        """
        Load the configuration file.

        This method loads the configuration file specified by the `_cfg_dir` attribute and
        assigns it to the `cfg` attribute.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.

        Returns:
            None
        """
        if reload:
            del self.cfg
        self.cfg = Config.load(base_dir=self._base_dir, pipeline_name=name, fs=self._fs)

    def _get_driver(
        self,
        name: str,
        executor: str | None = None,
        with_tracker: bool = False,
        with_opentelemetry: bool = False,
        with_progressbar: bool = False,
        config: dict = {},
        reload: bool = False,
        **kwargs,
    ) -> tuple[driver.Driver, Callable | None]:
        """
        Get the driver and shutdown function for a given pipeline.

        Args:
            name (str): The name of the pipeline.
            executor (str | None, optional): The executor to use. Defaults to None.
            with_tracker (bool, optional): Whether to use the tracker. Defaults to False.
            with_opentelemetry (bool, optional): Whether to use OpenTelemetry. Defaults to False.
            with_progressbar (bool, optional): Whether to use a progress bar. Defaults to False.
            config (dict | None, optional): The config for the hamilton driver that executes the pipeline.
                Defaults to None.
            with_opentelemetry (bool, optional): Whether to use OpenTelemetry. Defaults to False.
            reload (bool, optional): Whether to reload the module. Defaults to False.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            max_tasks (int, optional): The maximum number of tasks. Defaults to 20.
            num_cpus (int, optional): The number of CPUs. Defaults to 4.
            project_id (str, optional): The project ID for the tracker. Defaults to None.
            username (str, optional): The username for the tracker. Defaults to None.
            dag_name (str, optional): The DAG name for the tracker. Defaults to None.
            tags (str, optional): The tags for the tracker. Defaults to None.
            api_url (str, optional): The API URL for the tracker. Defaults to None.
            ui_url (str, optional): The UI URL for the tracker. Defaults to None.

        Returns:
            tuple[driver.Driver, Callable | None]: A tuple containing the driver and shutdown function.
        """
        if not self.cfg.pipeline.name == name or reload:
            self.load_config(name=name, reload=reload)
        if not hasattr(self, "_module") or reload:
            self.load_module(name=name, reload=reload)
        if self._telemetry:
            disable_telemetry()

        max_tasks = kwargs.pop("max_tasks", 20)
        num_cpus = kwargs.pop("num_cpus", 4)
        executor_, shutdown = get_executor(
            executor or "local", max_tasks=max_tasks, num_cpus=num_cpus
        )
        adapters = []
        if with_tracker:
            tracker_cfg = {
                **self.cfg.pipeline.tracker.to_dict(),
                **self.cfg.project.tracker.to_dict(),
            }
            tracker_kwargs = {
                key: kwargs.pop(key, None) or tracker_cfg.get(key, None)
                for key in tracker_cfg
            }
            tracker_kwargs["hamilton_api_url"] = tracker_kwargs.pop("api_url", None)
            tracker_kwargs["hamilton_ui_url"] = tracker_kwargs.pop("ui_url", None)

            if tracker_kwargs.get("project_id", None) is None:
                raise ValueError(
                    "Please provide a project_id if you want to use the tracker"
                )

            tracker = HamiltonTracker(**tracker_kwargs)
            adapters.append(tracker)

        if with_opentelemetry and h_opentelemetry is not None:
            trace = init_tracer(
                host=kwargs.pop("host", "localhost"),
                port=kwargs.pop("port", 6831),
                name=f"{self.cfg.project.name}.{name}",
            )
            tracer = trace.get_tracer(__name__)
            adapters.append(h_opentelemetry.OpenTelemetryTracer(tracer=tracer))

        if with_progressbar:
            adapters.append(h_tqdm.ProgressBar(desc=f"{self.cfg.project.name}.{name}"))

        if executor == "future_adapter":
            adapters.append(FutureAdapter())

        dr = (
            driver.Builder()
            .enable_dynamic_execution(allow_experimental_mode=True)
            .with_modules(self._module)
            .with_config(config)
            .with_local_executor(executors.SynchronousLocalTaskExecutor())
        )

        if executor_ is not None:
            dr = dr.with_remote_executor(executor_)

        if len(adapters):
            dr = dr.with_adapters(*adapters)

        dr = dr.build()
        return dr, shutdown

    def _resolve_parameters(self, method_args: dict, config_section: Any, keys: list[str]) -> dict:
        """
        Merge method arguments with config section, giving precedence to explicit arguments.
        Args:
            method_args (dict): Arguments passed to the method.
            config_section (Any): Config section (e.g., self.cfg.pipeline.run).
            keys (list[str]): List of keys to resolve.
        Returns:
            dict: Merged parameters.
        """
        resolved = {}
        for key in keys:
            if key in method_args and method_args[key] is not None:
                resolved[key] = method_args[key]
            elif hasattr(config_section, key):
                resolved[key] = getattr(config_section, key)
            else:
                resolved[key] = None
        return resolved

    @property
    def worker(self):
        """
        Lazily instantiate and cache a Worker instance for this PipelineManager.
        Returns:
            Worker: The worker instance.
        """
        if not hasattr(self, '_worker') or self._worker is None:
            self._worker = Worker(
                type=self._worker_type,
                fs=self._fs,
                base_dir=self._base_dir,
                storage_options=self._storage_options,
            )
        return self._worker

    def run(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        reload: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Run the pipeline with the given parameters.

        Args:
            name (str): The name of the pipeline.
            executor (str | None, optional): The executor to use. Defaults to None.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            config (dict | None, optional): The config for the hamilton driver that executes the pipeline.
                Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry. Defaults to None.
            with_progressbar (bool | None, optional): Whether to use a progress bar. Defaults to None.
            reload (bool, optional): Whether to reload the pipeline. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            dict[str,Any]: The result of executing the pipeline.

        Examples:
            ```python
            pm = PipelineManager()
            final_vars = pm.run("my_pipeline")
            ```
        """
        if not self.cfg.pipeline.name == name or reload:
            self.load_config(name=name, reload=reload)

        if reload or not hasattr(self, "_module"):
            self.load_module(name=name, reload=reload)

        logger.info(
            f"Starting pipeline {self.cfg.project.name}.{name}"
        )  # in environment {environment}")

        run_params = self.cfg.pipeline.run

        # Use _resolve_parameters for merging
        method_args = locals()
        keys = ["executor", "with_tracker", "with_opentelemetry", "with_progressbar"]
        merged = self._resolve_parameters(method_args, run_params, keys)

        final_vars = final_vars or run_params.final_vars
        inputs = {
            **(run_params.inputs or {}),
            **(inputs or {}),
        }  # <-- inputs override and adds to run_params
        config = {
            **(run_params.config or {}),
            **(config or {}),
        }
        merged["config"] = config

        dr, shutdown = self._get_driver(
            name=name,
            **merged,
            **kwargs,
        )

        res = dr.execute(final_vars=final_vars, inputs=inputs)

        logger.success(f"Finished pipeline {self.cfg.project.name}.{name}")

        if shutdown is not None:
            shutdown()

        return res

    def run_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        reload: bool = False,
        worker_type: str | None = None,  # Allow override
        **kwargs,
    ) -> str:
        """
        Add a job to run the pipeline with the given parameters to the worker queue.
        Returns the job ID (always).

        Args:
            name (str): The name of the job (pipeline).
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            config (dict | None, optional): The configuration for the job. Defaults to None.
            executor (str | None, optional): Executor hint (behavior might depend on worker backend). Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the job. Defaults to None.
            with_progressbar (bool | None, optional): Whether to use a progress bar for the job. Defaults to None.
            reload (bool, optional): Whether to reload the job module. Defaults to False.
            **kwargs: Additional keyword arguments passed to the pipeline's run method.

        Returns:
            str: The ID of the enqueued job.

        Examples:
            ```python
            pm = PipelineManager()
            final_vars = pm.run_job("my_job")
            ```
        """
        kwargs.update({
            arg: eval(arg)
            for arg in [
                "name", "inputs", "final_vars", "config", "executor",
                "with_tracker", "with_opentelemetry", "with_progressbar", "reload"
            ]
        })
        job_id = self.worker.add_job(
            func=self.run,
            kwargs=kwargs,
        )
        return job_id

    def add_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        reload: bool = False,
        result_ttl: float | dt.timedelta = 0,
        worker_type: str | None = None,  # Allow override
        **kwargs,
    ) -> UUID:
        """
        Add a job to run the pipeline with the given parameters to the worker data store.
        Executes the job immediatly and returns the job id (UUID). The job result will be stored in the data store
        for the given `result_ttl` and can be fetched using the job id.

        Args:
            name (str): The name of the job (pipeline).
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            config (dict | None, optional): The configuration for the job. Defaults to None.
            executor (str | None, optional): Executor hint (behavior might depend on worker backend). Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the job. Defaults to None.
            with_progressbar (bool | None, optional): Whether to use a progress bar for the job. Defaults to None.
            reload (bool, optional): Whether to reload the job module. Defaults to False.
            result_ttl (float | dt.timedelta, optional): How long the job result should be stored.
                Defaults to 0 (don't store).
            **kwargs: Additional keyword arguments passed to the pipeline's run method.

        Returns:
            UUID: The ID of the added job.

        Examples:
            ```python
            pm = PipelineManager()
            job_id = pm.add_job("my_job")
            ```
        """
        kwargs.update({
            arg: eval(arg)
            for arg in [
                "name", "inputs", "final_vars", "config", "executor",
                "with_tracker", "with_opentelemetry", "with_progressbar", "reload"
            ]
        })
        id_ = self.worker.add_job(
            func=self.run,
            kwargs=kwargs,
            result_ttl=result_ttl,
        )
        rich.print(
            f"✅ Successfully added job for "
            f"[blue]{self.cfg.project.name}.{name}[/blue] with ID [green]{id_}[/green]"
        )
        return id_

    def schedule(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        trigger_type: str | None = None,
        id_: str | None = None,
        paused: bool = False,
        coalesce: str = "latest",
        misfire_grace_time: float | dt.timedelta | None = None,
        max_jitter: float | dt.timedelta | None = None,
        max_running_jobs: int | None = None,
        conflict_policy: str = "do_nothing",
        overwrite: bool = False,
        worker_type: str | None = None,  # Allow override
        **kwargs,
    ) -> str:
        """
        Schedule a pipeline for execution.

        Args:
            name (str): The name of the pipeline.
            executor (str | None, optional): The executor to use for running the pipeline. Defaults to None.
            trigger_type (str | None, optional): The type of trigger for the pipeline. Defaults to None.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            config (dict | None, optional): The config for the hamilton driver that executes the pipeline.
                Defaults to None.
            with_tracker (bool | None, optional): Whether to include a tracker for the pipeline. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to include OpenTelemetry for the pipeline.
                Defaults to None.
            with_progressbar (bool | None, optional): Whether to include a progress bar for the pipeline.
            id_ (str | None, optional): The ID of the scheduled pipeline. Defaults to None.
            paused (bool, optional): Whether the pipeline should be initially paused. Defaults to False.
            coalesce (str, optional): The coalesce strategy for the pipeline. Defaults to "latest".
            misfire_grace_time (float | dt.timedelta | None, optional): The grace time for misfired jobs.
                Defaults to None.
            max_jitter (float | dt.timedelta | None, optional): The maximum number of seconds to randomly add to the
                scheduled. Defaults to None.
            max_running_jobs (int | None, optional): The maximum number of running jobs for the pipeline.
                Defaults to None.
            conflict_policy (str, optional): The conflict policy for the pipeline. Defaults to "do_nothing".
            job_result_expiration_time (float | dt.timedelta | None, optional): The result expiration time for the job.
                Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing schedule with the same name. Defaults to False.
            **kwargs: Additional keyword arguments for the trigger.

        Returns:
            str: The ID of the scheduled pipeline.

        Raises:
            ValueError: If APScheduler4 is not installed.

        Examples:
            ```python
            pm = PipelineManager()
            schedule_id = pm.schedule("my_pipeline")
            ```
        """
        if not self.cfg.pipeline.name == name:
            self.load_config(name=name)

        schedule_cfg = self.cfg.pipeline.schedule  # .copy()
        run_cfg = self.cfg.pipeline.run

        method_args = locals()
        run_keys = list(run_cfg.to_dict().keys())
        merged = self._resolve_parameters(method_args, run_cfg, run_keys)

        trigger_type = trigger_type or schedule_cfg.trigger.type_

        trigger_keys = list(getattr(schedule_cfg.trigger, trigger_type).to_dict().keys())
        trigger_kwargs = self._resolve_parameters(method_args, getattr(schedule_cfg.trigger, trigger_type), trigger_keys)
        trigger_kwargs.pop("type_", None)

        schedule_keys = list(schedule_cfg.run.to_dict().keys())
        schedule_kwargs = self._resolve_parameters(method_args, schedule_cfg.run, schedule_keys)
        executor = executor or schedule_cfg.run.executor
        # id_ = id_ or schedule_cfg.run.id_

        def _get_id(name=name, id_=id_, overwrite=overwrite):
            if id_:
                return id_

            if overwrite:
                return f"{name}-1"

            ids = [schedule.id for schedule in self._get_schedules()]
            if any([name in id_ for id_ in ids]):
                id_num = sorted([id_ for id_ in ids if name in id_])[-1].split("-")[-1]
                return f"{name}-{int(id_num) + 1}"
            return f"{name}-1"

        id_ = _get_id()

        schedule_kwargs.pop("executor", None)
        schedule_kwargs.pop("id_", None)

        # TODO: Make worker_type configurable
        with Worker(
            type=worker_type or self._worker_type,
            name=f"{self.cfg.project.name}.{name}",
            fs=self._fs,
            base_dir=self._base_dir,
            storage_options=self._storage_options,
        ) as worker:
            trigger = get_trigger(type_=trigger_type, **trigger_kwargs)

            if overwrite:
                worker.remove_schedule(id_) # Use worker method

            # Pass run parameters via kwargs, remove job_executor
            id_ = worker.add_schedule(
                func=self.run,
                trigger=trigger, # Trigger object from get_trigger
                id=id_,
                # args=(name,), # Pass name as arg if self.run needs it directly
                kwargs=merged, # Pass all other run parameters here
                **schedule_kwargs, # Pass schedule-specific options like coalesce, etc.
            )
            rich.print(
                f"✅ Successfully added schedule for "
                f"[blue]{self.cfg.project.name}.{name}[/blue] with ID [green]{id_}[/green]"
            )
            return id_

    def schedule_all(
        self,
        inputs: dict | None,
        final_vars: list | None,
        config: dict | None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        trigger_type: str | None = None,
        id_: str | None = None,
        paused: bool = False,
        coalesce: str = "latest",
        misfire_grace_time: float | dt.timedelta | None = None,
        max_jitter: float | dt.timedelta | None = None,
        max_running_jobs: int | None = None,
        conflict_policy: str = "do_nothing",
        overwrite: bool = False,
        **kwargs,
    ):
        pipelines = self._get_names()
        for name in pipelines:
            self.schedule(
                name=name,
                inputs=inputs,
                final_vars=final_vars,
                config=config,
                executor=executor,
                with_tracker=with_tracker,
                with_opentelemetry=with_opentelemetry,
                with_progressbar=with_progressbar,
                trigger_type=trigger_type,
                id_=id_,
                paused=paused,
                coalesce=coalesce,
                misfire_grace_time=misfire_grace_time,
                max_jitter=max_jitter,
                max_running_jobs=max_running_jobs,
                conflict_policy=conflict_policy,
                overwrite=overwrite,
                **kwargs,
            )

    def new(
        self,
        name: str,
        overwrite: bool = False,
    ):
        """
        Adds a pipeline with the given name.

        Args:
            name (str | None, optional): The name of the pipeline.
                Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.

        Returns:
            None

        Raises:
            ValueError: If the configuration path or pipeline path does not exist.

        Examples:
            ```python
            pm = PipelineManager()
            pm.new("my_pipeline")
            ```
        """
        if not self._fs.exists(self._cfg_dir):
            raise ValueError(
                f"Configuration path {self._cfg_dir} does not exist. Please run flowerpower init first."
            )
        if not self._fs.exists(self._pipelines_dir):
            raise ValueError(
                f"Pipeline path {self._pipelines_dir} does not exist. Please run flowerpower init first."
            )

        if self._fs.exists(f"{self._pipelines_dir}/{name.replace('.', '/')}.py"):
            if overwrite:
                self._fs.rm(f"{self._pipelines_dir}/{name.replace('.', '/')}.py")
            else:
                raise ValueError(
                    f"Pipeline {self.cfg.project.name}.{name.replace('.', '/')} already exists. "
                    "Use `overwrite=True` to overwrite."
                )
        if self._fs.exists(f"{self._cfg_dir}/pipelines/{name.replace('.', '/')}.yml"):
            if overwrite:
                self._fs.rm(f"{self._cfg_dir}/pipelines/{name.replace('.', '/')}.yml")
            else:
                raise ValueError(
                    f"Pipeline {self.cfg.project.name}.{name.replace('.', '/')} already exists. "
                    "Use `overwrite=True` to overwrite."
                )

        pipeline_path = f"{self._pipelines_dir}/{name.replace('.', '/')}.py"
        cfg_path = f"{self._cfg_dir}/pipelines/{name.replace('.', '/')}.yml"

        self._fs.makedirs(pipeline_path.rsplit("/", 1)[0], exist_ok=True)
        self._fs.makedirs(cfg_path.rsplit("/", 1)[0], exist_ok=True)

        with self._fs.open(pipeline_path, "w") as f:
            f.write(
                PIPELINE_PY_TEMPLATE.format(
                    name=name,
                    date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
            )

        self.cfg.pipeline = PipelineConfig(name=name)
        self.cfg.save()

        rich.print(
            f"🔧 Created new pipeline [bold blue]{self.cfg.project.name}.{name}[/bold blue]"
        )

    def import_pipeline(
        self,
        name: str,
        path: str,
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        storage_options: dict | Munch | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
    ):
        """Import a pipeline from a given path.

        The path could be a local path or a remote path like an S3 bucket or GitHub repository.
        Any readable fsspec filesystem is supported.

        Args:
            name (str): The name of the pipeline.
            path (str): The path to import the pipeline from.
            cfg_dir (str, optional): The configuration directory. Defaults to "conf".
            pipelines_dir (str, optional): The pipeline directory. Defaults to "pipelines".
            storage_options (dict | Munch | BaseStorageOptions | None, optional): The storage options.
                Defaults to None.
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name.
                Defaults to False.

        Examples:
            ```python
            pm = PipelineManager()
            pm.import(
                "s3://bucket/path",
                "my_pipeline",
                storage_options={
                    "key": "my_key",
                    "secret": "my_secret",
                    "endpoint_url":"http://minio:9000"
                    }
                )
            ```
        """
        if fs is not None:
            fs = get_filesystem(path, fs=fs)
        else:
            fs = get_filesystem(path, **storage_options)

        conf_path = f"{fs.fs.protocol}://{fs.path}/{cfg_dir}"
        pipeline_path = f"{fs.fs.protocol}://{fs.path}/{pipelines_dir}"
        if not fs.exists(cfg_dir):
            raise ValueError(f"Configuration path {conf_path} does not exist.")
        if not fs.exists(pipelines_dir):
            raise ValueError(f"Pipeline path {pipeline_path} does not exist.")

        if self._fs.exists(f"{pipelines_dir}/{name.replace('.', '/')}.py"):
            if overwrite:
                self._fs.rm(f"{pipelines_dir}/{name.replace('.', '/')}.py")
            else:
                raise ValueError(
                    f"Pipeline {name} already exists at {self._fs.fs.protocol}://{fs.path}. "
                    "Use `overwrite=True` to overwrite."
                )
        if self._fs.exists(f"{cfg_dir}/pipelines/{name.replace('.', '/')}.yml"):
            if overwrite:
                self._fs.rm(f"{cfg_dir}/pipelines/{name.replace('.', '/')}.yml")
            else:
                raise ValueError(
                    f"Pipeline {name} already exists at {self._fs.fs.protocol}://{fs.path}. "
                    "Use `overwrite=True` to overwrite."
                )

        self._fs.write_bytes(
            f"{self._pipelines_dir}/{name.replace('.', '/')}.py",
            fs.read_bytes(f"{pipelines_dir}/{name.replace('.', '/')}.py"),
        )
        self._fs.write_bytes(
            f"{self._cfg_dir}/pipelines/{name.replace('.', '/')}.yml",
            fs.read_bytes(f"{cfg_dir}/pipelines/{name.replace('.', '/')}.yml"),
        )
        # fs.get(
        #    f"{pipelines_dir}/{name.replace('.', '/')}.py",
        #    f"{self._pipelines_dir}/{name.replace('.', '/')}.py",
        # )
        # fs.get(
        #    f"{cfg_dir}/pipelines/{name.replace('.', '/')}.yml",
        #    f"{self._cfg_dir}/pipelines/{name.replace('.', '/')}.yml",
        # )

        rich.print(
            f"🔧 Imported pipeline [bold blue]{name}[/bold blue] from {fs.fs.protocol}://{fs.path}"
        )

    def import_many(
        self,
        names: list[str],
        path: str,
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        storage_options: dict | Munch | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
    ):
        """Import many pipelines from a given path.

        The path could be a local path or a remote path like an S3 bucket or GitHub repository.
        Any readable fsspec filesystem is supported.

        Args:
            names (list[str]): The names of the pipelines.
            path (str): The path to import the pipelines from.
            cfg_dir (str, optional): The configuration directory. Defaults to "conf".
            pipelines_dir (str, optional): The pipeline directory. Defaults to "pipelines".
            storage_options (dict | Munch | BaseStorageOptions | None, optional): The storage options.
                Defaults to None.
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name.
                Defaults to False.

        Examples:
            ```python
            pm = PipelineManager()
            pm.import_many(
                "s3://bucket/path",
                ["my_pipeline", "my_pipeline2"],
                storage_options={
                    "key": "my_key",
                    "secret": "my_secret",
                    "endpoint_url":"http://minio:9000"
                    }
                )
            ```
        """
        for name in names:
            self.import_pipeline(
                path=path,
                name=name,
                cfg_dir=cfg_dir,
                pipelines_dir=pipelines_dir,
                storage_options=storage_options,
                fs=fs,
                overwrite=overwrite,
            )

    def import_all(
        self,
        path: str,
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        storage_options: dict | Munch | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
    ):
        """Import all pipelines from a given path.

        The path could be a local path or a remote path like an S3 bucket or GitHub repository.
        Any readable fsspec filesystem is supported.

        Args:
            path (str): The path to import the pipelines from.
            cfg_dir (str, optional): The configuration directory. Defaults to "conf".
            pipelines_dir (str, optional): The pipeline directory. Defaults to "pipelines".
            storage_options (dict | Munch | BaseStorageOptions | None, optional): The storage options.
                Defaults to None.
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name.
                Defaults to False.

        Examples:
            ```python
            pm = PipelineManager()
            pm.import_all(
                "s3://bucket/path",
                storage_options={
                    "key": "my_key",
                    "secret": "my_secret",
                    endpoint_url="http://minio:9000"
                    }
                )
            ```
        """
        names = [
            fn.replace(pipelines_dir, "").lstrip("/").rstric(".py").replace("/", ".")
            for fn in fs.glob(f"{pipelines_dir}/**/*.py")
        ]
        self.import_many(
            path=path,
            names=names,
            cfg_dir=cfg_dir,
            pipelines_dir=pipelines_dir,
            storage_options=storage_options,
            fs=fs,
            overwrite=overwrite,
        )

    def export(
        self,
        name: str,
        path: str,
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        storage_options: dict | Munch | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
    ):
        """Export a pipeline to a given path.

        The path could be a local path or a remote path like an S3 bucket or GitHub repository.
        Any writable fsspec filesystem is supported.

        Args:
            name (str): The name of the pipeline.
            path (str): The path to export the pipeline to.
            cfg_dir (str, optional): The configuration directory. Defaults to "conf".
            pipelines_dir (str, optional): The pipeline directory. Defaults to "pipelines".
            storage_options (dict | Munch | BaseStorageOptions | None, optional): The storage options.
                Defaults to None.
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name.
                Defaults to False.

        Examples:
            ```python
            pm = PipelineManager()
            pm.export(
                "my_pipeline",
                "s3://bucket/path",
                storage_options={
                    "key": "my_key",
                    "secret": "my_secret",
                    "endpoint_url":"http://minio:9000"
                    }
                )
            ```
        """
        fs = fs or get_filesystem(path, **storage_options)

        if fs.exists(posixpath.join(pipelines_dir, name.replace(".", "/") + ".py")):
            if overwrite:
                fs.rm(posixpath.join(pipelines_dir, name.replace(".", "/") + ".py"))
            else:
                raise ValueError(
                    f"Pipeline {name} already exists at {fs.fs.protocol}://{fs.path}. "
                    "Use `overwrite=True` to overwrite."
                )
        if fs.exists(
            posixpath.join(cfg_dir, "pipelines", name.replace(".", "/") + ".yml")
        ):
            if overwrite:
                fs.rm(
                    posixpath.join(
                        cfg_dir, "pipelines", name.replace(".", "/") + ".yml"
                    )
                )
            else:
                raise ValueError(
                    f"Pipeline {name} already exists at {fs.fs.protocol}://{fs.path}. "
                    "Use `overwrite=True` to overwrite."
                )

        fs.put_file(
            posixpath.join(self._pipelines_dir, name.replace(".", "/") + ".py"),
            posixpath.join(pipelines_dir, name.replace(".", "/") + ".py"),
        )

        fs.put_file(
            posixpath.join(self._cfg_dir, "pipelines", name.replace(".", "/") + ".yml"),
            posixpath.join(cfg_dir, "pipelines", name.replace(".", "/") + ".yml"),
        )

        rich.print(
            f"🔧 Exported pipeline [bold blue]{name}[/bold blue] to {fs.fs.protocol}://{fs.path}"
        )

    def export_many(
        self,
        path: str,
        names: list[str],
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        storage_options: dict | Munch | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
    ):
        """Export many pipelines to a given path.

        The path could be a local path or a remote path like an S3 bucket or GitHub repository.
        Any writable fsspec filesystem is supported.

        Args:
            path (str): The path to export the pipelines to.
            names (list[str]): The names of the pipelines.
            cfg_dir (str, optional): The configuration directory. Defaults to "conf".
            pipelines_dir (str, optional): The pipeline directory. Defaults to "pipelines".
            storage_options (dict | Munch | BaseStorageOptions | None, optional): The storage options.
                Defaults to None.
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name.
                Defaults to False.

        Examples:
            ```python
            pm = PipelineManager()
            pm.export_many(
                "s3://bucket/path",
                ["my_pipeline", "my_pipeline2"],
                storage_options={
                    "key": "my_key",
                    "secret": "my_secret",
                    "endpoint_url":"http://minio:9000"
                    }
                )
        """
        for name in names:
            self.export(
                path=path,
                name=name,
                cfg_dir=cfg_dir,
                pipelines_dir=pipelines_dir,
                storage_options=storage_options,
                fs=fs,
                overwrite=overwrite,
            )

    def export_all(
        self,
        path: str,
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        storage_options: dict | Munch | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
    ):
        """Export all pipelines to a given path.

        The path could be a local path or a remote path like an S3 bucket or GitHub repository.
        Any writable fsspec filesystem is supported.

        Args:
            path (str): The path to export the pipelines to.
            storage_options (dict | Munch | BaseStorageOptions | None, optional): The storage options.
                Defaults to None.
            cfg_dir (str, optional): The configuration directory. Defaults to "conf".
            pipelines_dir (str, optional): The pipeline directory. Defaults to "pipelines".
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name.
                Defaults to False.

        Examples:
            ```python
            pm = PipelineManager()
            pm.export_all(
                "s3://bucket/path",
                storage_options={
                    "key": "my_key",
                    "secret": "my_secret",
                    "endpoint_url":"http://minio:9000"
                    }
                )
        """
        names = [
            fn.replace(self._pipelines_dir, "")
            .lstrip("/")
            .rstric(".py")
            .replace("/", ".")
            for fn in self._fs.glob(f"{self._pipelines_dir}/**/*.py")
        ]
        self.export_many(
            path=path,
            names=names,
            cfg_dir=cfg_dir,
            pipelines_dir=pipelines_dir,
            storage_options=storage_options,
            fs=fs,
            overwrite=overwrite,
        )

    def delete(self, name: str, cfg: bool = True, module: bool = False):
        """
        Delete a pipeline.

        Args:
            name (str): The name of the pipeline to delete.
            cfg (bool, optional): Whether to delete the pipeline configuration. Defaults to True.
            module (bool, optional): Whether to delete the pipeline module file. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            pm.delete("my_pipeline")
            ```
        """

        if cfg:
            if self._fs.exists(f"{self._cfg_dir}/pipelines/{name}.yml"):
                self._fs.rm(f"{self._cfg_dir}/pipelines/{name}.yml")
                rich.print(f"🗑️ Deleted pipeline config for {name}")

        if module:
            if self._fs.exists(f"{self._pipelines_dir}/{name}.py"):
                self._fs.rm(f"{self._pipelines_dir}/{name}.py")
                rich.print(
                    f"🗑️ Deleted pipeline config for {self.cfg.project.name}.{name}"
                )

    def _display_all_function(self, name: str, reload: bool = True):
        dr, _ = self._get_driver(
            name=name, executor=None, with_tracker=False, reload=reload
        )
        return dr.display_all_functions()

    def save_dag(
        self,
        name: str,
        format: str = "png",
        reload: bool = False,
    ):
        """
        Save a image of the graph of functions for a given name.

        Args:
            name (str): The name of the graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            reload (bool, optional): Whether to reload the graph data. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            pm.save_dag("my_pipeline")
            ```
        """
        dag = self._display_all_function(name=name, reload=reload)

        self._fs.makedirs("graphs", exist_ok=True)
        dag.render(
            posixpath.join(self._base_dir, f"graphs/{name}"),
            format=format,
            cleanup=True,
        )
        rich.print(
            f"📊 Saved graph for {name} to {self._base_dir}/graphs/{name}.{format}"
        )

    def show_dag(
        self,
        name: str,
        format: str = "png",
        reload: bool = False,
        raw: bool = False,
    ):
        """
        Display the graph of functions for a given name. By choosing the `raw` option, the graph object is returned.
        The choosen format defines, which application is used to display the graph.

        Args:
            name (str): The name of the graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            show (bool, optional): Whether to open the graph file after generating it. Defaults to False.
            reload (bool, optional): Whether to reload the graph data. Defaults to False.
            raw (bool, optional): Whether to return the graph object. Defaults to False.

        Returns:
            graph: The generated graph object.

        Examples:
            ```python
            pm = PipelineManager()
            pm.show_dag("my_pipeline")
            ```
        """
        dag = self._display_all_function(name=name, reload=reload)
        if raw:
            return dag
        view_img(dag.pipe(format), format=format)

    def _get_files(self) -> list[str]:
        """
        Get the pipeline files.

        Returns:
            list[str]: A list of pipeline files.
        """
        return [f for f in self._fs.ls(self._pipelines_dir) if f.endswith(".py")]

    def _get_names(self) -> list[str]:
        """
        Get the pipeline names.

        Returns:
            list[str]: A list of pipeline names.
        """
        return [posixpath.splitext(posixpath.basename(f))[0] for f in self._get_files()]

    def get_summary(
        self, name: str | None = None, cfg: bool = True, module: bool = True
    ) -> dict[str, dict | str]:
        """
        Get a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            cfg (bool, optional): Whether to show the configuration. Defaults to True.
            module (bool, optional): Whether to show the module. Defaults to True.
        Returns:
            dict[str, dict | str]: A dictionary containing the pipeline summary.

        Examples:
            ```python
            pm = PipelineManager()
            summary=pm.get_summary()
            ```
        """
        if name:
            pipeline_names = [name]
        else:
            pipeline_names = self._get_names()

        pipeline_summary = {}
        for name in pipeline_names:
            self.load_config(name)
            if cfg:
                pipeline_summary[name] = {"cfg": self.cfg.pipeline.to_dict()}
            if module:
                pipeline_summary[name].update(
                    {
                        "module": self._fs.cat(
                            f"{self._pipelines_dir}/{name}.py"
                        ).decode(),
                    }
                )
        return pipeline_summary

    def show_summary(
        self,
        name: str | None = None,
        cfg: bool = True,
        module: bool = True,
        to_html: bool = False,
        to_svg: bool = False,
    ) -> None | str:
        """
        Show a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            cfg (bool, optional): Whether to show the configuration. Defaults to True.
            module (bool, optional): Whether to show the module. Defaults to True.
            to_html (bool, optional): Whether to export the summary to HTML. Defaults to False.
            to_svg (bool, optional): Whether to export the summary to SVG. Defaults to False.

        Returns:
            None | str: The summary of the pipelines. If `to_html` is True, returns the HTML string.
                If `to_svg` is True, returns the SVG string.

        Examples:
            ```python
            pm = PipelineManager()
            pm.show_summary()
            ```
        """

        pipeline_summary = self.get_summary(name=name, cfg=cfg, module=module)

        def add_dict_to_tree(tree, dict_data, style="green"):
            for key, value in dict_data.items():
                if isinstance(value, dict):
                    branch = tree.add(f"[cyan]{key}:", style="bold cyan")
                    add_dict_to_tree(branch, value, style)
                else:
                    tree.add(f"[cyan]{key}:[/] [green]{value}[/]")

        console = Console()
        for pipeline, info in pipeline_summary.items():
            # Create tree for config
            config_tree = Tree("📋 Configuration", style="bold magenta")
            add_dict_to_tree(config_tree, info["cfg"])

            # Create syntax-highlighted code view
            code_view = Syntax(
                info["module"],
                "python",
                theme="default",
                line_numbers=False,
                word_wrap=True,
                code_width=80,
                padding=2,
            )

            if cfg:
                # console.print(f"🔄 Pipeline: {pipeline}", style="bold blue")
                console.print(
                    Panel(
                        config_tree,
                        title=f"🔄 Pipeline: {pipeline}",
                        subtitle="Configuration",
                        border_style="blue",
                        padding=(2, 2),
                    )
                )
                console.print("\n")

            if module:
                # console.print(f"🔄 Pipeline: {pipeline}", style="bold blue")
                console.print(
                    Panel(
                        code_view,
                        title=f"🔄 Pipeline: {pipeline}",
                        subtitle="Module",
                        border_style="blue",
                        padding=(2, 2),
                    )
                )
                console.print("\n")
        if to_html:
            return console.export_html()
        elif to_svg:
            return console.export_svg()

    @property
    def summary(self) -> dict[str, dict | str]:
        """
        Get a summary of the pipelines.

        Returns:
            dict: A dictionary containing the pipeline summary.
        """
        return self.get_summary()

    def _all_pipelines(
        self, show: bool = True, to_html: bool = False, to_svg: bool = False
    ) -> list[str] | None:
        """
        Print all available pipelines in a formatted table.

        Args:
            show (bool, optional): Whether to print the table. Defaults to True.
            to_html (bool, optional): Whether to export the table to HTML. Defaults to False.
            to_svg (bool, optional): Whether to export the table to SVG. Defaults to False.

        Returns:
            list[str] | None: A list of pipeline names if `show` is False.

        Examples:
            ```python
            pm = PipelineManager()
            all_pipelines = pm._pipelines(show=False)
            ```
        """
        if to_html or to_svg:
            show = True

        pipeline_files = [
            f for f in self._fs.ls(self._pipelines_dir) if f.endswith(".py")
        ]
        pipeline_names = [
            posixpath.splitext(f)[0]
            .replace(self._pipelines_dir, "")
            .lstrip("/")
            .replace("/", ".")
            for f in pipeline_files
        ]

        if not pipeline_files:
            rich.print("[yellow]No pipelines found[/yellow]")
            return

        pipeline_info = []

        for path, name in zip(pipeline_files, pipeline_names):
            # path = posixpath.join( f)
            try:
                mod_time = self._fs.modified(path).strftime("%Y-%m-%d %H:%M:%S")
            except NotImplementedError:
                mod_time = "N/A"
            size = f"{self._fs.size(path) / 1024:.1f} KB"
            pipeline_info.append(
                {"name": name, "path": path, "mod_time": mod_time, "size": size}
            )

        if show:
            table = Table(title="Available Pipelines")
            table.add_column("Pipeline Name", style="blue")
            table.add_column("Path", style="magenta")
            table.add_column("Last Modified", style="green")
            table.add_column("Size", style="cyan")

            for info in pipeline_info:
                table.add_row(
                    info["name"], info["path"], info["mod_time"], info["size"]
                )
            console = Console(record=True)
            console.print(table)
            if to_html:
                return console.export_html()
            elif to_svg:
                return console.export_svg()

        else:
            return pipeline_info

    def show_pipelines(self) -> None:
        """
        Print all available pipelines in a formatted table.

        Examples:
            ```python
            pm = PipelineManager()
            pm.show_pipelines()
            ```
        """
        self._all_pipelines(show=True)

    def list_pipelines(self) -> list[str]:
        """
        Get a list of all available pipelines.

        Returns:
            list[str] | None: A list of pipeline names.

        Examples:
            ```python
            pm = PipelineManager()
            pipelines = pm.list_pipelines()
            ```
        """
        return self._all_pipelines(show=False)

    @property
    def pipelines(self) -> list[str]:
        """
        Get a list of all available pipelines.

        Returns:
            list[str] | None: A list of pipeline names.

        Examples:
            ```python
            pm = PipelineManager()
            pipelines = pm.pipelines
            ```
        """
        return self._all_pipelines(show=False)






