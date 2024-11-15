import datetime as dt
import importlib
import importlib.util
import os
import sys
from typing import Any, Callable
from uuid import UUID
from fsspec.spec import AbstractFileSystem

import rich
from hamilton import driver
from hamilton.plugins import h_opentelemetry
from hamilton_sdk.adapters import HamiltonTracker
from loguru import logger
from rich.table import Table

from .cfg import (
    Config,
    PipelineConfig,
    PipelineRunConfig,
    PipelineScheduleConfig,
    PipelineTrackerConfig,
)
from .helpers.open_telemetry import init_tracer
from .helpers.filesystem import get_filesystem

# from munch import unmunchify
from .helpers.templates import PIPELINE_PY_TEMPLATE

if importlib.util.find_spec("apscheduler"):
    from .scheduler import SchedulerManager
else:
    SchedulerManager = None
if importlib.util.find_spec("paho"):
    from .mqtt import MQTTClient
else:
    MQTTClient = None


from .helpers.executor import get_executor
from .helpers.trigger import get_trigger  # , ALL_TRIGGER_KWARGS


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
        self._base_dir = base_dir or ""
        self._storage_options = storage_options
        if fs is None:
            fs = get_filesystem(self._base_dir, **self._storage_options)
        self._fs = fs

        self._conf_dir = "conf"
        self._pipeline_dir = "pipelines"

        self._sync_fs()
        self.load_config()

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

        if with_opentelemetry:
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
                # args=(
                #     name,
                #     inputs,
                #     final_vars,
                #     executor,
                #     with_tracker,
                #     with_opentelemetry,
                #     reload,
                # ),
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
                # args=(
                #     name,
                #     inputs,
                #     final_vars,
                #     executor,
                #     with_tracker,
                #     with_opentelemetry,
                #     reload,
                # ),
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
        trigger_kwargs = {
            key: kwargs.pop(key, None) or getattr(schedule_cfg.trigger, key)
            for key in schedule_cfg.trigger.to_dict()
        }
        trigger_type = trigger_type or schedule_cfg.trigger.type_
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
                return f"{name}-{int(id_num)+1}"
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

    def new(
        self,
        name: str,
        overwrite: bool = False,
        pipeline_config: dict | PipelineConfig = {},
        params: dict = {},
        run: dict | PipelineRunConfig = {},
        schedule: dict | PipelineScheduleConfig = {},
        tracker: dict | PipelineTrackerConfig = {},
    ):
        """
        Adds a new pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
            pipeline_config (dict | PipelineConfig, optional): The configuration for the pipeline. Defaults to {}.
            params (dict, optional): The function configuration for the pipeline. Defaults to {}.
            run (dict | PipelineRunConfig, optional): The run configuration for the pipeline. Defaults to {}.
            schedule (dict | PipelineScheduleConfig, optional): The schedule configuration for the pipeline.
                Defaults to {}.
            tracker (dict | PipelineTrackerConfig, optional): The tracker configuration for the pipeline.
                Defaults to {}.
        """
        self.add(name, overwrite, pipeline_config, params, run, schedule, tracker)

    def add(
        self,
        name: str,
        overwrite: bool = False,
        pipeline_file: str | None = None,
        pipeline_config: dict | PipelineConfig = {},
        params: dict = {},
        run: dict | PipelineRunConfig = {},
        schedule: dict | PipelineScheduleConfig = {},
        tracker: dict | PipelineTrackerConfig = {},
    ):
        """
        Adds a new pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
            pipeline_file (str | None, optional): The path to the pipeline file. Defaults to None.
            pipeline_config (dict | PipelineConfig, optional): The configuration for the pipeline. Defaults to {}.
            params (dict, optional): The function configuration for the pipeline. Defaults to {}.
            run (dict | PipelineRunConfig, optional): The run configuration for the pipeline. Defaults to {}.
            schedule (dict | PipelineScheduleConfig, optional): The schedule configuration for the pipeline.
                Defaults to {}.
            tracker (dict | PipelineTrackerConfig, optional): The tracker configuration for the pipeline.
                Defaults to {}.
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
        try:
            if pipeline_file:
                self._fs.put_file(pipeline_file, f"{self._pipeline_dir}/{name}.py")
            else:
                with self._fs.open(f"{self._pipeline_dir}/{name}.py", "w") as f:
                    f.write(
                        PIPELINE_PY_TEMPLATE.format(
                            name=name,
                            date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        )
                    )
                    # rich.print(f"    Added pipeline file [italic green]pipelines/{name}.py[/italic green]")
        except NotImplementedError:
            raise NotImplementedError("The filesystem does not support writing files.")

        if pipeline_config:
            self.cfg.pipeline = (
                pipeline_config
                if isinstance(pipeline_config, PipelineConfig)
                else PipelineConfig.from_dict(name, pipeline_config)
            )
            if not self.cfg.pipeline.name:
                self.cfg.pipeline.name = name
        else:
            self.cfg.pipeline = PipelineConfig(
                name=name, run=run, schedule=schedule, tracker=tracker, params=params
            )

        self.cfg.save()
        # rich.print(f"   Added config file [italic green]conf/pipelines/{name}.yml[/italic green]")

        rich.print(
            f"🔧 Created new pipeline [bold blue]{self.cfg.project.name}.{name}[/bold blue]"
        )

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

    def show_dag(
        self,
        name: str,
        format: str = "png",
        show: bool = False,
        reload: bool = False,
        save: bool = False,
        **kwargs,
    ):
        """
        Display the graph of functions for a given name.

        Args:
            name (str): The name of the graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            show (bool, optional): Whether to open the graph file after generating it. Defaults to False.
            reload (bool, optional): Whether to reload the graph data. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            graph: The generated graph object.
        """
        self._fs.makedirs("graphs", exist_ok=True)
        dr, _ = self._get_driver(
            name=name, executor=None, with_tracker=False, reload=reload
        )
        if save:
            path = f"graphs/{name}.{format}"
        else:
            path = None
        graph = dr.display_all_functions(path, **kwargs)

        if show:
            graph.view()
        return graph

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

    def get_summary(self, name: str | None = None) -> dict:
        """
        Get a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
        Returns:
            dict: A dictionary containing the pipeline summary.
        """
        if name:
            pipeline_names = [name]
        else:
            pipeline_names = self._get_names()

        pipeline_summary = {}
        for name in pipeline_names:
            pipeline_summary[name] = {
                "config": self.cfg.pipeline.to_dict(),
                "module": self._fs.cat(f"{self._pipeline_dir}/{name}.py").decode(),
            }

        return pipeline_summary

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

    def start_mqtt_listener(
        self,
        name: str,
        topic: str | None = None,
        host: str = "localhost",
        port: int = 1883,
        user: str | None = None,
        pw: str | None = None,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        reload: bool = False,
        result_expiration_time: float | dt.timedelta = 0,
        as_job: bool = False,
        background: bool = False,
        **kwargs,
    ):
        """
        Run a pipeline when a message is received on a given topic.

        Args:
            name (str): The name of the pipeline.
            topic (str | None, optional): The topic to subscribe to. Defaults to None.
            host (str, optional): The host of the MQTT broker. Defaults to "localhost".
            port (int, optional): The port of the MQTT broker. Defaults to 1883.
            user (str | None, optional): The username for the MQTT broker. Defaults to None.
            pw (str | None, optional): The password for the MQTT broker. Defaults to None.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            executor (str | None, optional): The executor to use for the pipeline. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker for the pipeline. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the pipeline. Defaults to None.
            reload (bool, optional): Whether to reload the pipeline. Defaults to False.
            result_expiration_time (float | dt.timedelta, optional): The result expiration time for the job.
                Defaults to 0.
            as_job (bool, optional): Whether to run the pipeline as a job. Defaults to False.
            background (bool, optional): Whether to run the pipeline in the background. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        if inputs is None:
            inputs = {}

        def on_message(client, userdata, msg):
            logger.info("Message arrived")

            inputs["payload"] = msg.payload

            try:
                if as_job:
                    self._add_job(
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
                else:
                    self._run(
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
                logger.success("Message processed successfully")
                return
            except Exception as e:
                _ = e
                logger.exception(e)

            logger.warning("processing failed")

        if not hasattr(self, "mqtt_client"):
            self.mqtt_client = {}
        try:

            self.mqtt[name] = MQTTClient.from_event_broker(base_dir=self._base_dir)
        except ValueError as e:
            logger.exception(e)
        else:
            self.mqtt[name] = MQTTClient(user=user, pw=pw, host=host, port=port)
        if topic is None:
            topic = name
        self.mqtt[name].connect()
        self.mqtt[name].start_listener(on_message, topic, background=background)

    def stop_mqtt_listener(self, name: str):
        """
        Stop the MQTT listener.

        Returns:
            None
        """
        self.mqtt[name].stop_listener()
        self.mqtt[name].disconnect()


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
        trigger_type: str = "cron",
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

    def show_dag(
        self,
        format: str = "png",
        show: bool = False,
        save: bool = False,
        reload: bool = False,
    ):
        return super().show_dag(
            self.name, format=format, show=show, save=save, reload=reload
        )

    def delete(self, cfg: bool = True, remove_module_file: bool = False):
        return super().delete(self.name, cfg, remove_module_file)

    def load_module(self):
        super().load_module(self.name)

    def start_mqtt_listener(
        self,
        topic: str | None = None,
        host: str = "localhost",
        port: int = 1883,
        user: str | None = None,
        pw: str | None = None,
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        reload: bool = False,
        result_expiration_time: float | dt.timedelta = 0,
        background: bool = False,
        **kwargs,
    ):
        name = self.name
        return super().start_mqtt_listener(
            name=name,
            topic=topic,
            host=host,
            port=port,
            user=user,
            pw=pw,
            inputs=inputs,
            final_vars=final_vars,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            reload=reload,
            result_expiration_time=result_expiration_time,
            background=background,
            **kwargs,
        )

    def stop_mqtt_listener(self):
        return super().stop_mqtt_listener(self.name)

    def get_summary(self):
        return super().get_summary(self.name)[self.name]

    @property
    def summary(self):
        return self.get_summary()


## methods for the pipeline module


def add_pipeline(
    name: str,
    overwrite: bool = False,
    pipeline_config: dict | PipelineConfig = {},
    pipeline_file: str | None = None,
    params: dict = {},
    run: dict | PipelineRunConfig = {},
    schedule: dict | PipelineScheduleConfig = {},
    tracker: dict | PipelineTrackerConfig = {},
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
        pipeline_config (dict | PipelineConfig, optional): The pipeline configuration. Defaults to {}.
        params (dict, optional): The function configuration. Defaults to {}.
        run (dict | PipelineRunConfig, optional): The run configuration. Defaults to {}.
        schedule (dict | PipelineScheduleConfig, optional): The schedule configuration. Defaults to {}.
        tracker (dict | PipelineTrackerConfig, optional): The tracker configuration. Defaults to {}.
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
        params=params,
        run=run,
        schedule=schedule,
        tracker=tracker,
    )


def add_pipeline_job(
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
    pm = PipelineManager(base_dir=base_dir, storage_options=storage_options, fs=fs)
    return pm.all_pipelines(show=show)


def delete_pipeline(
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
    p = Pipeline(name=name, base_dir=base_dir, storage_options=storage_options, fs=fs)
    p.delete(remove_module_file=remove_module_file)


def get_pipeline_summary(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
):
    """
    Get a summary of the pipelines.

    Args:
        name (str): The name of the pipeline.
        base_dir (str | None, optional): The base path of the pipeline. Defaults to None.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
    Returns:
        dict: A dictionary containing the pipeline summary.
    """
    p = PipelineManager(base_dir=base_dir, storage_options=storage_options, fs=fs)
    return p.get_summary(name=name)


def new_pipeline(
    name: str,
    overwrite: bool = False,
    pipeline_config: dict | PipelineConfig = {},
    params: dict = {},
    run: dict | PipelineRunConfig = {},
    schedule: dict | PipelineScheduleConfig = {},
    tracker: dict | PipelineTrackerConfig = {},
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
):
    """
    Add a new pipeline.

    Args:
        name (str): The name of the pipeline.
        overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
        pipeline_config (dict | PipelineConfig, optional): The pipeline configuration. Defaults to {}.
        params (dict, optional): The function configuration. Defaults to {}.
        run (dict | PipelineRunConfig, optional): The run configuration. Defaults to {}.
        schedule (dict | PipelineScheduleConfig, optional): The schedule configuration. Defaults to {}.
        tracker (dict | PipelineTrackerConfig, optional): The tracker configuration. Defaults to {}.
        base_dir (str | None, optional): The base directory of the pipeline. Defaults to None.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
    """
    add_pipeline(
        name=name,
        overwrite=overwrite,
        pipeline_config=pipeline_config,
        params=params,
        run=run,
        schedule=schedule,
        tracker=tracker,
        base_dir=base_dir,
        storage_options=storage_options,
        fs=fs,
    )


def run_pipeline(
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
    p = Pipeline(name=name, base_dir=base_dir, storage_options=storage_options, fs=fs)
    return p.run(
        executor=executor,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        with_opentelemetry=with_opentelemetry,
        reload=reload,
        **kwargs,
    )


def run_pipeline_job(
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

    p = Pipeline(name=name, base_dir=base_dir, storage_options=storage_options, fs=fs)
    return p.run_job(
        executor=executor,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        with_opentelemetry=with_opentelemetry,
        reload=reload,
        **kwargs,
    )


def start_mqtt_listener(
    name: str,
    topic: str | None = None,
    host: str = "localhost",
    port: int = 1883,
    user: str | None = None,
    pw: str | None = None,
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
    as_job: bool = False,
    background: bool = False,
    **kwargs,
) -> MQTTClient:
    """
    Run a pipeline when a message is received on a given topic.

    Args:
        name (str): The name of the pipeline.
        topic (str | None, optional): The topic to subscribe to. Defaults to None.
        host (str, optional): The host of the MQTT broker. Defaults to "localhost".
        port (int, optional): The port of the MQTT broker. Defaults to 1883.
        user (str | None, optional): The username for the MQTT broker. Defaults to None.
        pw (str | None, optional): The password for the MQTT broker. Defaults to None.
        inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
        final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
        executor (str | None, optional): The executor to use for the pipeline. Defaults to None.
        with_tracker (bool | None, optional): Whether to use a tracker for the pipeline. Defaults to None.
        with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the pipeline. Defaults to None.
        base_dir (str | None, optional): The base path of the pipeline. Defaults to None.
        storage_options (dict, optional): The fsspec storage options. Defaults to {}.
        fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
        reload (bool, optional): Whether to reload the pipeline. Defaults to False.
        result_expiration_time (float | dt.timedelta, optional): The result expiration time for the job. Defaults to 0.
        as_job (bool, optional): Whether to run the pipeline as a job. Defaults to False.
        background (bool, optional): Whether to run the pipeline in the background. Defaults to False.
        **kwargs: Additional keyword arguments.
    """
    p = Pipeline(name=name, base_dir=base_dir, storage_options=storage_options, fs=fs)
    p.start_mqtt_listener(
        topic=topic,
        host=host,
        port=port,
        user=user,
        pw=pw,
        inputs=inputs,
        final_vars=final_vars,
        executor=executor,
        with_tracker=with_tracker,
        with_opentelemetry=with_opentelemetry,
        reload=reload,
        result_expiration_time=result_expiration_time,
        as_job=as_job,
        background=background,
        **kwargs,
    )
    return p.mqtt_client[name]


def schedule_pipeline(
    name: str,
    trigger_type: str = "cron",
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
    p = Pipeline(name=name, base_dir=base_dir, storage_options=storage_options, fs=fs)
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
        # job_result_expiration_time=job_result_expiration_time,
        conflict_policy=conflict_policy,
        **kwargs,
    )


def show_pipeline_dag(
    name: str,
    format: str = "png",
    show: bool = False,
    save: bool = False,
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
    p = Pipeline(name=name, base_dir=base_dir, storage_options=storage_options, fs=fs)
    p.show(format=format, show=show, reload=reload, save=save)
