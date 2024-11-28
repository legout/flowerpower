import datetime as dt
import importlib
import importlib.util
import os
import sys
from typing import Any, Callable
from uuid import UUID

import rich
from fsspec.spec import AbstractFileSystem
from hamilton import driver

if importlib.util.find_spec("opentelemetry"):
    from hamilton.plugins import h_opentelemetry

    from .utils.open_telemetry import init_tracer

else:
    h_opentelemetry = None
    init_tracer = None
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
from .utils.filesystem import get_filesystem
from .utils.templates import PIPELINE_PY_TEMPLATE

if importlib.util.find_spec("apscheduler"):
    from .scheduler import SchedulerManager
else:
    SchedulerManager = None
# if importlib.util.find_spec("paho"):
#     from .mqtt import MQTTClient
# else:
#     MQTTClient = None


from pathlib import Path
from types import TracebackType

from .utils.executor import get_executor
from .utils.trigger import get_trigger  # , ALL_TRIGGER_KWARGS


class PipelineManager:
    def __init__(
        self,
        base_dir: str | None = None,
        storage_options: dict = {},
        fs: AbstractFileSystem | None = None,
    ):
        """
        Initializes the Pipeline object.

        Args:
            base_dir (str | None): The flowerpower base path. Defaults to None.
            storage_options (dict, optional): The fsspec storage options. Defaults to {}.
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.

        Returns:
            None
        """
        self._base_dir = base_dir or str(Path.cwd())
        self._storage_options = storage_options
        if fs is None:
            fs = get_filesystem(self._base_dir, **self._storage_options)
        self._fs = fs

        self._conf_dir = "conf"
        self._pipeline_dir = "pipelines"

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
        with SchedulerManager(
            # name=f"{self.cfg.project.name}.{self.name}",
            fs=self._fs,
            role="scheduler",
        ) as sm:
            return sm.get_schedules()

    def _sync_fs(self):
        """
        Sync the filesystem.

        Returns:
            None
        """
        if self._fs.is_cache_fs:
            self._fs.sync()

        modules_path = os.path.join(self._fs.path, self._pipeline_dir)
        if modules_path not in sys.path:
            sys.path.append(modules_path)

    def load_module(self, name: str):
        """
        Load a module dynamically.

        Args:
            name (str): The name of the module to load.

        Returns:
            None
        """
        sys.path.append(os.path.join(self._fs.path, self._pipeline_dir))

        if not hasattr(self, "_module"):
            self._module = importlib.import_module(name)
        else:
            self._module = importlib.reload(self._module)

    def load_config(self, name: str | None = None):
        """
        Load the configuration file.

        This method loads the configuration file specified by the `_conf_dir` attribute and
        assigns it to the `cfg` attribute.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.

        Returns:
            None
        """
        self.cfg = Config.load(base_dir=self._base_dir, pipeline_name=name, fs=self._fs)

    def _get_driver(
        self,
        name: str,
        executor: str | None = None,
        with_tracker: bool = False,
        with_opentelemetry: bool = False,
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
        if not self.cfg.pipeline.name == name:
            self.load_config(name=name)

        max_tasks = kwargs.pop("max_tasks", 20)
        num_cpus = kwargs.pop("num_cpus", 4)
        executor_, shutdown = get_executor(
            executor or "local", max_tasks=max_tasks, num_cpus=num_cpus
        )
        if reload or not hasattr(self, "_module"):
            self.load_module(name=name)

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
        if len(adapters):
            print("adapters len:", len(adapters))

            dr = (
                driver.Builder()
                .with_modules(self._module)
                .enable_dynamic_execution(allow_experimental_mode=True)
                .with_adapters(adapters[0])
                .with_remote_executor(executor_)
                .build()
            )
        else:
            dr = (
                driver.Builder()
                .with_modules(self._module)
                .enable_dynamic_execution(allow_experimental_mode=True)
                .with_remote_executor(executor_)
                .build()
            )

        return dr, shutdown

    def _run(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        """
        Run the pipeline with the given parameters.

        Args:
            name (str): The name of the pipeline.
            executor (str | None, optional): The executor to use. Defaults to None.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry. Defaults to None.
            reload (bool, optional): Whether to reload the pipeline. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The result of executing the pipeline.
        """
        if not self.cfg.pipeline.name == name:
            self.load_config(name=name)

        if reload or not hasattr(self, "_module"):
            self.load_module(name=name)

        logger.info(
            f"Starting pipeline {self.cfg.project.name}.{name}"
        )  # in environment {environment}")

        run_params = self.cfg.pipeline.run

        final_vars = final_vars or run_params.final_vars
        inputs = {
            **(run_params.inputs or {}),
            **(inputs or {}),
        }  # <-- inputs override and adds to run_params

        kwargs.update(
            {
                arg: eval(arg) or getattr(run_params, arg)
                for arg in ["executor", "with_tracker", "with_opentelemetry"]
            }
        )

        dr, shutdown = self._get_driver(
            name=name,
            **kwargs,
        )

        res = dr.execute(final_vars=final_vars, inputs=inputs)

        logger.success(f"Finished pipeline {self.cfg.project.name}.{name}")

        if shutdown is not None:
            shutdown()

        return res

    def run(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool = False,
        with_opentelemetry: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        """
        Run the pipeline.

        Args:
            name (str): The name of the pipeline.
            executor (str | None, optional): The executor to use. Defaults to None.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            with_tracker (bool, optional): Whether to use a tracker. Defaults to False.
            with_opentelemetry (bool, optional): Whether to use OpenTelemetry. Defaults to False.
            reload (bool, optional): Whether to reload the pipeline. Defaults to False.
            **kwargs: Additional keyword arguments.
        Returns:
            Any: The result of running the pipeline.
        """
        return self._run(
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            reload=reload,
            **kwargs,
        )

    def run_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        """
        Add a job to run the pipeline with the given parameters to the worker.
        Executes the job immediatly and returns the result of the execution.

        Args:
            name (str): The name of the job.
            executor (str | None, optional): The executor to use for the job. Defaults to None.
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the job. Defaults to None.
            reload (bool, optional): Whether to reload the job. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The result of the job execution.
        """

        with SchedulerManager(
            name=f"{self.cfg.project.name}.{name}",
            fs=self._fs,
            role="scheduler",
        ) as sm:
            # if not any([task.id == "run-pipeline" for task in sm.get_tasks()]):
            #    sm.configure_task(func_or_task_id="run-pipeline", func=self._run)
            kwargs.update(
                {
                    arg: eval(arg)
                    for arg in [
                        "name",
                        "inputs",
                        "final_vars",
                        "executor",
                        "with_tracker",
                        "with_opentelemetry",
                        "reload",
                    ]
                }
            )
            return sm.run_job(
                self._run,
                kwargs=kwargs,
                job_executor=(
                    executor
                    if executor in ["async", "threadpool", "processpool"]
                    else "threadpool"
                ),
            )

    def _add_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        reload: bool = False,
        result_expiration_time: float | dt.timedelta = 0,
        **kwargs,
    ) -> UUID:
        """
        Add a job to run the pipeline with the given parameters to the worker data store.
        Executes the job immediatly and returns the job id (UUID). The job result will be stored in the data store
        for the given `result_expiration_time` and can be fetched using the job id (UUID).

        Args:
            name (str): The name of the job.
            executor (str | None, optional): The executor for the job. Defaults to None.
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the job. Defaults to None.
            reload (bool, optional): Whether to reload the job. Defaults to False.
            result_expiration_time (float | dt.timedelta | None, optional): The result expiration time for the job.
                Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            UUID: The UUID of the added job.
        """
        with SchedulerManager(
            name=f"{self.cfg.project.name}.{name}",
            fs=self._fs,
            role="scheduler",
        ) as sm:
            kwargs.update(
                {
                    arg: eval(arg)
                    for arg in [
                        "name",
                        "inputs",
                        "final_vars",
                        "executor",
                        "with_tracker",
                        "with_opentelemetry",
                        "reload",
                    ]
                }
            )
            id_ = sm.add_job(
                self._run,
                kwargs=kwargs,
                job_executor=(
                    executor
                    if executor in ["async", "threadpool", "processpool"]
                    else "threadpool"
                ),
                result_expiration_time=result_expiration_time,
            )
            rich.print(
                f"✅ Successfully added job for "
                f"[blue]{self.cfg.project.name}.{name}[/blue] with ID [green]{id_}[/green]"
            )
            return id_

    def add_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        reload: bool = False,
        result_expiration_time: float | dt.timedelta = 0,
        **kwargs,
    ):
        """
        Add a job to run the pipeline with the given parameters to the worker data store.
        Executes the job immediatly and returns the job id (UUID). The job result will be stored in the data store
        for the given `result_expiration_time` and can be fetched using the job id (UUID).

        Args:
            name (str): The name of the job.
            executor (str | None, optional): The executor for the job. Defaults to None.
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the job. Defaults to None.
            reload (bool, optional): Whether to reload the job. Defaults to False.
            result_expiration_time (float | dt.timedelta | None, optional): The result expiration time for the job.
                Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            UUID: The UUID of the added job.
        """
        return self._add_job(
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            reload=reload,
            result_expiration_time=result_expiration_time,
            **kwargs,
        )

    def schedule(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        trigger_type: str | None = None,
        id_: str | None = None,
        paused: bool = False,
        coalesce: str = "latest",
        misfire_grace_time: float | dt.timedelta | None = None,
        max_jitter: float | dt.timedelta | None = None,
        max_running_jobs: int | None = None,
        conflict_policy: str = "do_nothing",
        # job_result_expiration_time: float | dt.timedelta = 0,
        overwrite: bool = False,
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
            with_tracker (bool | None, optional): Whether to include a tracker for the pipeline. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to include OpenTelemetry for the pipeline.
                Defaults to None.
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

        """
        if SchedulerManager is None:
            raise ValueError("APScheduler4 not installed. Please install it first.")

        # if "pipeline" in self.cfg.scheduler:
        schedule_cfg = self.cfg.pipeline.schedule  # .copy()
        run_cfg = self.cfg.pipeline.run

        kwargs.update(
            {arg: eval(arg) or getattr(run_cfg, arg) for arg in run_cfg.to_dict()}
        )
        trigger_type = trigger_type or schedule_cfg.trigger.type_

        trigger_kwargs = {
            key: kwargs.pop(key, None)
            or getattr(getattr(schedule_cfg.trigger, trigger_type), key)
            for key in getattr(schedule_cfg.trigger, trigger_type).to_dict()
        }

        trigger_kwargs.pop("type_", None)

        schedule_kwargs = {
            arg: eval(arg) or getattr(schedule_cfg.run, arg)
            for arg in schedule_cfg.run.to_dict()
        }
        executor = executor or schedule_cfg.run.executor
        # id_ = id_ or schedule_cfg.run.id_

        def _get_id() -> str:
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

        with SchedulerManager(
            name=f"{self.cfg.project.name}.{name}",
            fs=self._fs,
            role="scheduler",
        ) as sm:
            trigger = get_trigger(type_=trigger_type, **trigger_kwargs)

            id_ = sm.add_schedule(
                func_or_task_id=self._run,
                trigger=trigger,
                id=id_,
                args=(name,),  # inputs, final_vars, executor, with_tracker),
                kwargs=kwargs,
                job_executor=(
                    executor
                    if executor in ["async", "threadpool", "processpool"]
                    else "threadpool"
                ),
                **schedule_kwargs,
            )
            rich.print(
                f"✅ Successfully added schedule for "
                f"[blue]{self.cfg.project.name}.{name}[/blue] with ID [green]{id_}[/green]"
            )
            return id_

    def add(
        self,
        name: str | None = None,
        overwrite: bool = False,
        pipeline_file: str | None = None,
        pipeline_config: str | dict | PipelineConfig = {},
    ):
        """
        Adds a pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
            pipeline_file (str | None, optional): The path to the pipeline file or the pipeline file content.
                Defaults to None.
            pipeline_config (str | dict | PipelineConfig, optional): The configuration for the pipeline or the pipeline
                config content. Defaults to {}.
        """

        if not self._fs.exists(self._conf_dir):
            raise ValueError(
                f"Configuration path {self._conf_dir} does not exist. Please run flowerpower init first."
            )
        if not self._fs.exists(self._pipeline_dir):
            raise ValueError(
                f"Pipeline path {self._pipeline_dir} does not exist. Please run flowerpower init first."
            )

        if self._fs.exists(f"{self._pipeline_dir}/{name}.py") and not overwrite:
            raise ValueError(
                f"Pipeline {self.cfg.project.name}.{name} already exists. Use `overwrite=True` to overwrite."
            )
        if name is None:
            if not pipeline_file:
                raise ValueError("Please provide a name for the pipeline.")
            name = os.path.splitext(os.path.basename(pipeline_file))[0]
        try:
            if pipeline_file:
                if ".py" not in pipeline_file:
                    self._fs.put_file(pipeline_file, f"{self._pipeline_dir}/{name}.py")
                else:
                    self._fs.write_text(
                        f"{self._pipeline_dir}/{name}.py", pipeline_file
                    )
            else:
                with self._fs.open(f"{self._pipeline_dir}/{name}.py", "w") as f:
                    f.write(
                        PIPELINE_PY_TEMPLATE.format(
                            name=name,
                            date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        )
                    )
        except NotImplementedError:
            raise NotImplementedError(
                "The filesystem "
                f"{self.fs.fs.protocol[0] if isinstance(self.fs.fs.protocol, tuple) else self.fs.fs.protocol} "
                "does not support writing files."
            )

        if pipeline_config:
            if isinstance(pipeline_config, str):
                if ".yml" in pipeline_config or ".yaml" in pipeline_config:
                    self._fs.put_file(
                        pipeline_config, f"{self._conf_dir}/pipelines/{name}.yml"
                    )
                else:
                    self._fs.write_text(
                        f"{self._conf_dir}/pipelines/{name}.yml", pipeline_config
                    )
            else:
                self.cfg.pipeline = (
                    pipeline_config
                    if isinstance(pipeline_config, PipelineConfig)
                    else PipelineConfig.from_dict(name, pipeline_config)
                )
                if not self.cfg.pipeline.name:
                    self.cfg.pipeline.name = name
        else:
            self.cfg.pipeline = PipelineConfig(name=name)

        self.cfg.save()

        rich.print(
            f"🔧 Created new pipeline [bold blue]{self.cfg.project.name}.{name}[/bold blue]"
        )

    def new(
        self,
        name: str,
        overwrite: bool = False,
    ):
        """
        Adds a new pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
        """
        self.add(name, overwrite)

    def delete(self, name: str, cfg: bool = True, remove_module_file: bool = False):
        """
        Delete a pipeline.

        Args:
            name (str): The name of the pipeline to delete.
            cfg (bool, optional): Whether to delete the pipeline configuration. Defaults to True.
            remove_module_file (bool, optional): Whether to delete the pipeline module file. Defaults to False.
        """

        if cfg:
            if self._fs.exists(f"{self._conf_dir}/pipelines/{name}.yml"):
                self._fs.rm(f"{self._conf_dir}/pipelines/{name}.yml")
                rich.print(f"🗑️ Deleted pipeline config for {name}")

        if remove_module_file:
            if self._fs.exists(f"{self._pipeline_dir}/{name}.py"):
                self._fs.rm(f"{self._pipeline_dir}/{name}.py")
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
        Save the graph of functions for a given name.

        Args:
            name (str): The name of the graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            reload (bool, optional): Whether to reload the graph data. Defaults to False.

        Returns:
            str: The path to the saved graph file.
        """
        dag = self._display_all_function(name=name, reload=reload)

        self._fs.makedirs("graphs", exist_ok=True)
        dag.save(os.path.join(self._base_dir, f"graphs/{name}.{format}"))

    def show_dag(
        self,
        name: str,
        reload: bool = False,
    ):
        """
        Display the graph of functions for a given name.

        Args:
            name (str): The name of the graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            show (bool, optional): Whether to open the graph file after generating it. Defaults to False.
            reload (bool, optional): Whether to reload the graph data. Defaults to False.

        Returns:
            graph: The generated graph object.
        """
        dag = self._display_all_function(name=name, reload=reload)
        return dag.show()

    def _get_files(self) -> list[str]:
        """
        Get the pipeline files.

        Returns:
            list[str]: A list of pipeline files.
        """
        return [f for f in self._fs.ls(self._pipeline_dir) if f.endswith(".py")]

    def _get_names(self) -> list[str]:
        """
        Get the pipeline names.

        Returns:
            list[str]: A list of pipeline names.
        """
        return [os.path.splitext(os.path.basename(f))[0] for f in self._get_files()]

    def get_summary(
        self, name: str | None = None, config: bool = True, module: bool = True
    ) -> dict:
        """
        Get a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            config (bool, optional): Whether to show the configuration. Defaults to True.
            module (bool, optional): Whether to show the module. Defaults to True.
        Returns:
            dict: A dictionary containing the pipeline summary.
        """
        if name:
            pipeline_names = [name]
        else:
            pipeline_names = self._get_names()

        pipeline_summary = {}
        for name in pipeline_names:
            self.load_config(name)
            if config:
                pipeline_summary[name] = {"config": self.cfg.pipeline.to_dict()}
            if module:
                pipeline_summary[name].update(
                    {
                        "module": self._fs.cat(
                            f"{self._pipeline_dir}/{name}.py"
                        ).decode(),
                    }
                )
        return pipeline_summary

    def show_summary(
        self, name: str | None = None, config: bool = True, module: bool = True
    ) -> dict:
        """
        Show a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            config (bool, optional): Whether to show the configuration. Defaults to True.
            module (bool, optional): Whether to show the module. Defaults to True.
        """

        pipeline_summary = self.get_summary(name=name, config=config, module=module)

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
            add_dict_to_tree(config_tree, info["config"])

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

            if config:
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

    @property
    def summary(self) -> dict:
        """
        Get a summary of the pipelines.

        Returns:
            dict: A dictionary containing the pipeline summary.
        """
        return self.get_summary()

    def all_pipelines(self, show: bool = True) -> None:
        """
        Print all available pipelines in a formatted table.

        Args:
            show (bool, optional): Whether to print the table. Defaults to True.
        Returns:
            None
        """

        pipeline_files = [
            f for f in self._fs.ls(self._pipeline_dir) if f.endswith(".py")
        ]
        pipeline_names = [os.path.splitext(f)[0] for f in pipeline_files]

        if not pipeline_files:
            rich.print("[yellow]No pipelines found[/yellow]")
            return

        pipeline_info = []

        for path, name in zip(pipeline_files, pipeline_names):
            # path = os.path.join( f)
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
            rich.print(table)
        else:
            return pipeline_info


class Pipeline(PipelineManager):
    def __init__(
        self,
        name: str,
        base_dir: str | None = None,
        storage_options: dict = {},
        fs: AbstractFileSystem | None = None,
    ):
        """
        Initializes the Pipeline object.

        Args:
            name (str): The name of the pipeline.
            base_dir (str | None): The flowerpower base path. Defaults to None.
            storage_options (dict, optional): The fsspec storage options. Defaults to {}.
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.

        Returns:
            None
        """
        super().__init__(base_dir=base_dir, storage_options=storage_options, fs=fs)
        self.name = name
        self.load_module()
        self.load_config(name)

    def run(
        self,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool = False,
        with_opentelemetry: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        name = self.name
        return super().run(
            name=name,
            executor=executor,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            reload=reload,
            **kwargs,
        )

    def run_job(
        self,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        name = self.name
        return super().run_job(
            name=name,
            executor=executor,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            reload=reload,
            **kwargs,
        )

    def add_job(
        self,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        reload: bool = False,
        result_expiration_time: float | dt.timedelta = 0,
        **kwargs,
    ) -> UUID:
        name = self.name
        return super().add_job(
            name=name,
            executor=executor,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            reload=reload,
            result_expiration_time=result_expiration_time,
            **kwargs,
        )

    def schedule(
        self,
        trigger_type: str | None = None,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool = False,
        with_opentelemetry: bool = False,
        paused: bool = False,
        coalesce: str = "latest",
        misfire_grace_time: float | dt.timedelta | None = None,
        max_jitter: float | dt.timedelta | None = None,
        max_running_jobs: int | None = None,
        conflict_policy: str = "do_nothing",
        # job_result_expiration_time: float | dt.timedelta = 0,
        **kwargs,
    ):
        name = self.name
        return super().schedule(
            name=name,
            executor=executor,
            trigger_type=trigger_type,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            paused=paused,
            coalesce=coalesce,
            misfire_grace_time=misfire_grace_time,
            max_jitter=max_jitter,
            max_running_jobs=max_running_jobs,
            # job_result_expiration_time=job_result_expiration_time,
            conflict_policy=conflict_policy,
            **kwargs,
        )

    def save_dag(self, name, format="png"):
        return super().save_dag(name, format)

    def show_dag(
        self,
    ):
        return super().show_dag(
            self.name,
        )

    def delete(self, cfg: bool = True, remove_module_file: bool = False):
        return super().delete(self.name, cfg, remove_module_file)

    def load_module(self):
        super().load_module(self.name)

    # def start_mqtt_listener(
    #     self,
    #     topic: str | None = None,
    #     host: str = "localhost",
    #     port: int = 1883,
    #     user: str | None = None,
    #     pw: str | None = None,
    #     inputs: dict | None = None,
    #     final_vars: list | None = None,
    #     executor: str | None = None,
    #     with_tracker: bool | None = None,
    #     with_opentelemetry: bool | None = None,
    #     reload: bool = False,
    #     result_expiration_time: float | dt.timedelta = 0,
    #     background: bool = False,
    #     **kwargs,
    # ):
    #     name = self.name
    #     return super().start_mqtt_listener(
    #         name=name,
    #         topic=topic,
    #         host=host,
    #         port=port,
    #         user=user,
    #         pw=pw,
    #         inputs=inputs,
    #         final_vars=final_vars,
    #         executor=executor,
    #         with_tracker=with_tracker,
    #         with_opentelemetry=with_opentelemetry,
    #         reload=reload,
    #         result_expiration_time=result_expiration_time,
    #         background=background,
    #         **kwargs,
    #     )

    # def stop_mqtt_listener(self):
    #     return super().stop_mqtt_listener(self.name)

    def get_summary(self, config: bool = True, module: bool = True):
        return super().get_summary(self.name, config=config, module=module)[self.name]

    def show_summary(self, config: bool = True, module: bool = True):
        return super().show_summary(self.name, config=config, module=module)

    @property
    def summary(self):
        return self.get_summary()


def add(
    name: str,
    overwrite: bool = False,
    pipeline_file: str | None = None,
    pipeline_config: str | dict | PipelineConfig = {},
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
):
    """
    Add a new pipeline.

    Args:
        name (str): The name of the pipeline.
        overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
        pipeline_file (str | None, optional): The path to the pipeline file. Defaults to None.
        pipeline_config (str | dict | PipelineConfig, optional): The pipeline configuration. Defaults to {}.
        base_dir (str | None, optional): The base directory of the pipeline. Defaults to None.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
    """
    pm = PipelineManager(base_dir=base_dir, storage_options=storage_options, fs=fs)
    pm.add(
        name=name,
        overwrite=overwrite,
        pipeline_file=pipeline_file,
        pipeline_config=pipeline_config,
    )


def add_job(
    name: str,
    inputs: dict | None = None,
    final_vars: list | None = None,
    executor: str | None = None,
    with_tracker: bool | None = None,
    with_opentelemetry: bool | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    reload: bool = False,
    result_expiration_time: float | dt.timedelta = 0,
    **kwargs,
) -> UUID:
    """
    Add a job to run the pipeline with the given parameters to the worker data store.
    Executes the job immediatly and returns the job id (UUID). The job result will be stored in the data store for the
    given `result_expiration_time` and can be fetched using the job id (UUID).

    Args:
        name (str): The name of the job.
        executor (str | None, optional): The executor to use for the job. Defaults to None.
        inputs (dict | None, optional): The inputs for the job. Defaults to None.
        final_vars (list | None, optional): The final variables for the job. Defaults to None.
        with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
        with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the job. Defaults to None.
        base_dir (str | None, optional): The base path for the job. Defaults to None.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
        reload (bool, optional): Whether to reload the job. Defaults to False.
        result_expiration_time (float | dt.timedelta | None, optional): The expiration time for the job result.
            Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        UUID: The UUID of the added job.
    """
    p = Pipeline(name=name, base_dir=base_dir, storage_options=storage_options, fs=fs)
    return p.add_job(
        executor=executor,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        with_opentelemetry=with_opentelemetry,
        reload=reload,
        result_expiration_time=result_expiration_time,
        **kwargs,
    )


def all_pipelines(
    base_dir: str | None = None,
    show: bool = True,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
):
    """
    Print all available pipelines in a formatted table.

    Args:
        base_dir (str | None, optional): The base path of the pipelines. Defaults to None.
        show (bool, optional): Whether to print the table. Defaults to True.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
    """
    with PipelineManager(
        base_dir=base_dir, storage_options=storage_options, fs=fs
    ) as pm:
        return pm.all_pipelines(show=show)


def delete(
    name: str,
    base_dir: str | None = None,
    remove_module_file: bool = False,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
):
    """
    Delete a pipeline.

    Args:
        name (str): The name of the pipeline to delete.
        base_dir (str | None, optional): The base path of the pipeline. Defaults to None.
        remove_module_file (bool, optional): Whether to delete the pipeline module. Defaults to False.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
    """
    with Pipeline(
        name=name, base_dir=base_dir, storage_options=storage_options, fs=fs
    ) as p:
        p.delete(remove_module_file=remove_module_file)


def get_summary(
    name: str | None = None,
    base_dir: str | None = None,
    config: bool = True,
    module: bool = True,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
):
    """
    Get a summary of the pipelines.

    Args:
        name (str): The name of the pipeline.
        base_dir (str | None, optional): The base path of the pipeline. Defaults to None.
        config (bool, optional): Whether to show the configuration. Defaults to True.
        module (bool, optional): Whether to show the module. Defaults to True.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
    Returns:
        dict: A dictionary containing the pipeline summary.
    """
    with PipelineManager(
        base_dir=base_dir, storage_options=storage_options, fs=fs
    ) as p:
        return p.get_summary(name=name, config=config, module=module)


def new(
    name: str,
    overwrite: bool = False,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
):
    """
    Add a new pipeline.

    Args:
        name (str): The name of the pipeline.
        overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
        base_dir (str | None, optional): The base directory of the pipeline. Defaults to None.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
    """

    with PipelineManager(
        base_dir=base_dir, storage_options=storage_options, fs=fs
    ) as pm:
        pm.new(name=name, overwrite=overwrite)


def run(
    name: str,
    inputs: dict | None = None,
    final_vars: list | None = None,
    executor: str | None = None,
    with_tracker: bool = False,
    with_opentelemetry: bool = False,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    reload: bool = False,
    **kwargs,
) -> Any:
    """
    Run the pipeline with the given parameters.

    Args:
        name (str): The name of the pipeline.
        executor (str | None, optional): The executor to use. Defaults to None.
        inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
        final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
        with_tracker (bool, optional): Whether to use the tracker. Defaults to False.
        with_opentelemetry (bool, optional): Whether to use OpenTelemetry. Defaults to False.
        base_dir (str | None, optional): The base path for the pipeline. Defaults to None.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
        reload (bool, optional): Whether to reload the pipeline. Defaults to False.
        **kwargs: Additional keyword arguments.
    Returns:
        Any: The result of running the pipeline.
    """
    with Pipeline(
        name=name, base_dir=base_dir, storage_options=storage_options, fs=fs
    ) as p:
        return p.run(
            executor=executor,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            reload=reload,
            **kwargs,
        )


def run_job(
    name: str,
    inputs: dict | None = None,
    final_vars: list | None = None,
    executor: str | None = None,
    with_tracker: bool | None = None,
    with_opentelemetry: bool | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    reload: bool = False,
    **kwargs,
) -> Any:
    """
    Add a job to run the pipeline with the given parameters to the worker.
    Executes the job immediatly and returns the job result.

    Args:
        name (str): The name of the job.
        executor (str | None, optional): The executor to use for the job. Defaults to None.
        inputs (dict | None, optional): The inputs for the job. Defaults to None.
        final_vars (list | None, optional): The final variables for the job. Defaults to None.
        with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
        with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the job. Defaults to None.
        base_dir (str | None, optional): The base path for the job. Defaults to None.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
        reload (bool, optional): Whether to reload the job. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        Any: The result of running the job.
    """

    with Pipeline(
        name=name, base_dir=base_dir, storage_options=storage_options, fs=fs
    ) as p:
        return p.run_job(
            executor=executor,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            reload=reload,
            **kwargs,
        )


# def start_mqtt_listener(
#     name: str,
#     topic: str | None = None,
#     host: str = "localhost",
#     port: int = 1883,
#     user: str | None = None,
#     pw: str | None = None,
#     inputs: dict | None = None,
#     final_vars: list | None = None,
#     executor: str | None = None,
#     with_tracker: bool | None = None,
#     with_opentelemetry: bool | None = None,
#     base_dir: str | None = None,
#     storage_options: dict = {},
#     fs: AbstractFileSystem | None = None,
#     reload: bool = False,
#     result_expiration_time: float | dt.timedelta = 0,
#     as_job: bool = False,
#     background: bool = False,
#     **kwargs,
# ) -> "MQTTClient":
#     """
#     Run a pipeline when a message is received on a given topic.

#     Args:
#         name (str): The name of the pipeline.
#         topic (str | None, optional): The topic to subscribe to. Defaults to None.
#         host (str, optional): The host of the MQTT broker. Defaults to "localhost".
#         port (int, optional): The port of the MQTT broker. Defaults to 1883.
#         user (str | None, optional): The username for the MQTT broker. Defaults to None.
#         pw (str | None, optional): The password for the MQTT broker. Defaults to None.
#         inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
#         final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
#         executor (str | None, optional): The executor to use for the pipeline. Defaults to None.
#         with_tracker (bool | None, optional): Whether to use a tracker for the pipeline. Defaults to None.
#         with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the pipeline. Defaults to None.
#         base_dir (str | None, optional): The base path of the pipeline. Defaults to None.
#         storage_options (dict, optional): The fsspec storage options. Defaults to {}.
#         fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
#         reload (bool, optional): Whether to reload the pipeline. Defaults to False.
#         result_expiration_time (float | dt.timedelta, optional): The result expiration time for the job.
#               Defaults to 0.
#         as_job (bool, optional): Whether to run the pipeline as a job. Defaults to False.
#         background (bool, optional): Whether to run the pipeline in the background. Defaults to False.
#         **kwargs: Additional keyword arguments.
#     """
#     with Pipeline(
#         name=name, base_dir=base_dir, storage_options=storage_options, fs=fs
#     ) as p:
#         p.start_mqtt_listener(
#             topic=topic,
#             host=host,
#             port=port,
#             user=user,
#             pw=pw,
#             inputs=inputs,
#             final_vars=final_vars,
#             executor=executor,
#             with_tracker=with_tracker,
#             with_opentelemetry=with_opentelemetry,
#             reload=reload,
#             result_expiration_time=result_expiration_time,
#             as_job=as_job,
#             background=background,
#             **kwargs,
#         )
#         return p.mqtt_client[name]


def schedule(
    name: str,
    trigger_type: str | None = None,
    inputs: dict | None = None,
    final_vars: list | None = None,
    executor: str | None = None,
    with_tracker: bool = False,
    with_opentelemetry: bool = False,
    paused: bool = False,
    coalesce: str = "latest",
    misfire_grace_time: float | dt.timedelta | None = None,
    max_jitter: float | dt.timedelta | None = None,
    max_running_jobs: int | None = None,
    conflict_policy: str = "do_nothing",
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
) -> str:
    """
    Schedule a pipeline for execution.

    Args:
        name (str): The name of the pipeline.
        executor (str | None, optional): The executor to use for running the pipeline. Defaults to None.
        trigger_type (str, optional): The type of schedule. Defaults to "cron".
        auto_start (bool, optional): Whether to automatically start the pipeline. Defaults to True.
        background (bool, optional): Whether to run the pipeline in the background. Defaults to False.
        inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
        final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
        with_tracker (bool, optional): Whether to use a tracker for the pipeline. Defaults to False.
        with_opentelemetry (bool, optional): Whether to use OpenTelemetry for the pipeline. Defaults to False.
        paused (bool, optional): Whether to start the pipeline in a paused state. Defaults to False.
        coalesce (str, optional): The coalesce strategy for the pipeline. Defaults to "latest".
        misfire_grace_time (float | dt.timedelta | None, optional): The grace time for misfired jobs. Defaults to None.
        max_jitter (float | dt.timedelta | None, optional): The maximum number of seconds to randomly add to the
            scheduled. Defaults to None.
        max_running_jobs (int | None, optional): The maximum number of running jobs. Defaults to None.
        conflict_policy (str, optional): The conflict policy for the pipeline. Defaults to "do_nothing".
        job_result_expiration_time (float | dt.timedelta | None, optional): The result expiration time for the job.
                Defaults to None.
        base_dir (str | None, optional): The base path for the pipeline. Defaults to None.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        str: The ID of the scheduled pipeline.
    """
    with Pipeline(
        name=name, base_dir=base_dir, storage_options=storage_options, fs=fs
    ) as p:
        return p.schedule(
            executor=executor,
            tigger_type=trigger_type,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            paused=paused,
            coalesce=coalesce,
            misfire_grace_time=misfire_grace_time,
            max_jitter=max_jitter,
            max_running_jobs=max_running_jobs,
            conflict_policy=conflict_policy,
            **kwargs,
        )


def save_dag(
    name: str,
    format="png",
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
):
    with Pipeline(
        name=name, base_dir=base_dir, storage_options=storage_options, fs=fs
    ) as p:
        p.save_dag(name, format)


def show_dag(
    name: str,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    reload: bool = False,
):
    """
    Display the pipeline with the given name.

    Parameters:
        name (str): The name of the pipeline.
        format (str, optional): The format of the displayed pipeline. Defaults to "png".
        view (bool, optional): Whether to display the pipeline. Defaults to False.
        base_dir (str | None, optional): The base path of the pipeline. Defaults to None.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
        reload (bool, optional): Whether to reload the pipeline. Defaults to False.
    """
    with Pipeline(
        name=name, base_dir=base_dir, storage_options=storage_options, fs=fs
    ) as p:
        p.show_dag()


def show_summary(
    name: str | None = None,
    base_dir: str | None = None,
    config: bool = True,
    module: bool = True,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
):
    """
    Show a summary of the pipelines.

    Args:
        name (str): The name of the pipeline.
        base_dir (str | None, optional): The base path of the pipeline. Defaults to None.
        config (bool, optional): Whether to show the configuration. Defaults to True.
        module (bool, optional): Whether to show the module. Defaults to True.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
    """
    with PipelineManager(
        base_dir=base_dir, storage_options=storage_options, fs=fs
    ) as pm:
        pm.show_summary(name=name, config=config, module=module)
