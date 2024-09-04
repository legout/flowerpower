import datetime as dt
import importlib.util
import importlib
import os
import sys
from typing import Any, Callable
from uuid import UUID

from hamilton import driver
from hamilton_sdk import adapters
from loguru import logger
from munch import unmunchify
from .helpers.templates import PIPELINE_PY_TEMPLATE
from .cfg import Config


if importlib.util.find_spec("apscheduler"):
    from .scheduler import SchedulerManager
else:
    SchedulerManager = None


from .helpers.executor import get_executor
from .helpers.trigger import get_trigger, ALL_TRIGGER_KWARGS


class PipelineManager:
    def __init__(self, base_dir: str | None = None):
        """
        Initializes the Pipeline object.

        Args:
            base_dir (str | None): The flowerpower base path. Defaults to None.

        Returns:
            None
        """
        self._base_dir = base_dir or ""
        self._conf_dir = os.path.join(self._base_dir, "conf")
        self._pipeline_dir = os.path.join(self._base_dir, "pipelines")

        sys.path.append(self._pipeline_dir)

        self.load_config()

    def load_module(self, name: str):
        """
        Load a module dynamically.

        Args:
            name (str): The name of the module to load.

        Returns:
            None
        """
        if not hasattr(self, "_module"):
            self._module = importlib.import_module(name)
        else:
            self._module = importlib.reload(self._module)

    def load_config(self):
        """
        Load the configuration file.

        This method loads the configuration file specified by the `_conf_dir` attribute and
        assigns it to the `cfg` attribute.

        Parameters:
        - None

        Returns:
        - None
        """
        self.cfg = Config(base_dir=self._base_dir)

    def _get_driver(
        self,
        name: str,
        executor: str | None = None,
        with_tracker: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> tuple[driver.Driver, Callable | None]:
        """
        Get the driver and shutdown function for a given pipeline.

        Args:
            name (str): The name of the pipeline.
            executor (str | None, optional): The executor to use. Defaults to None.
            with_tracker (bool, optional): Whether to use the tracker. Defaults to False.
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
        max_tasks = kwargs.pop("max_tasks", 20)
        num_cpus = kwargs.pop("num_cpus", 4)
        executor_, shutdown = get_executor(
            executor or "local", max_tasks=max_tasks, num_cpus=num_cpus
        )
        if reload or not hasattr(self, "_module"):
            self.load_module(name)

        if with_tracker:
            tracker_cfg = self.cfg.tracker.pipeline.get(name, {})
            tracker_kwargs = {
                key: kwargs.pop(key, None) or tracker_cfg.get(key, None)
                for key in [
                    "project_id",
                    "username",
                    "dag_name",
                    "tags",
                    "api_url",
                    "ui_url",
                ]
            }
            tracker_kwargs["hamilton_api_url"] = tracker_kwargs.pop("api_url", None)
            tracker_kwargs["hamilton_ui_url"] = tracker_kwargs.pop("ui_url", None)

            project_id = tracker_kwargs.get("project_id", None)

            if project_id is None:
                raise ValueError(
                    "Please provide a project_id if you want to use the tracker"
                )

            tracker = adapters.HamiltonTracker(project_id=project_id, **tracker_kwargs)

            dr = (
                driver.Builder()
                .with_modules(self._module)
                .enable_dynamic_execution(allow_experimental_mode=True)
                .with_adapters(tracker)
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
        environment: str = "dev",
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        """
        Run the pipeline with the given parameters.

        Args:
            name (str): The name of the pipeline.
            environment (str, optional): The environment to run the pipeline in. Defaults to "dev".
            executor (str | None, optional): The executor to use. Defaults to None.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker. Defaults to None.
            reload (bool, optional): Whether to reload the pipeline. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The result of executing the pipeline.
        """
        logger.info(f"Starting pipeline {name} in environment {environment}")

        run_params = self.cfg.pipeline.run.get(name)[environment]

        final_vars = final_vars or run_params.get("final_vars", [])
        inputs = {
            **(run_params.get("inputs", {}) or {}),
            **(inputs or {}),
        }  # <-- inputs override and adds to run_params

        kwargs.update(
            {
                arg: eval(arg) or run_params.get(arg, None)
                for arg in ["executor", "with_tracker", "reload"]
            }
        )

        dr, shutdown = self._get_driver(
            name=name,
            **kwargs,
        )

        res = dr.execute(final_vars=final_vars, inputs=unmunchify(inputs))

        logger.success(f"Finished pipeline {name}")

        if shutdown is not None:
            shutdown()

        return res

    def run(
        self,
        name: str,
        environment: str = "dev",
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        """
        Run the pipeline.

        Args:
            name (str): The name of the pipeline.
            environment (str, optional): The environment to run the pipeline in. Defaults to "dev".
            executor (str | None, optional): The executor to use. Defaults to None.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            with_tracker (bool, optional): Whether to use a tracker. Defaults to False.
            reload (bool, optional): Whether to reload the pipeline. Defaults to False.
            **kwargs: Additional keyword arguments.
        Returns:
            Any: The result of running the pipeline.
        """
        return self._run(
            name=name,
            environment=environment,
            inputs=inputs,
            final_vars=final_vars,
            executor=executor,
            with_tracker=with_tracker,
            reload=reload,
            **kwargs,
        )

    def run_job(
        self,
        name: str,
        environment: str = "dev",
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        """
        Add a job to run the pipeline with the given parameters to the scheduler.
        Executes the job immediatly and returns the result of the execution.

        Args:
            name (str): The name of the job.
            environment (str, optional): The environment to run the job in. Defaults to "dev".
            executor (str | None, optional): The executor to use for the job. Defaults to None.
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
            reload (bool, optional): Whether to reload the job. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The result of the job execution.
        """

        with SchedulerManager(
            name=name, base_dir=self._base_dir, role="scheduler"
        ) as sm:
            # if not any([task.id == "run-pipeline" for task in sm.get_tasks()]):
            #    sm.configure_task(func_or_task_id="run-pipeline", func=self._run)
            return sm.run_job(
                self._run,
                args=(
                    name,
                    environment,
                    inputs,
                    final_vars,
                    executor,
                    with_tracker,
                    reload,
                ),
                kwargs=kwargs,
                job_executor=(
                    executor
                    if executor in ["async", "threadpool", "processpool"]
                    else "threadpool"
                ),
            )

    def add_job(
        self,
        name: str,
        environment: str = "dev",
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        reload: bool = False,
        result_expiration_time: float | dt.timedelta = 0,
        **kwargs,
    ) -> UUID:
        """
        Add a job to run the pipeline with the given parameters to the scheduler data store.
        Executes the job immediatly and returns the job id (UUID). The job result will be stored in the data store
        for the given `result_expiration_time` and can be fetched using the job id (UUID).

        Args:
            name (str): The name of the job.
            environment (str, optional): The environment for the job. Defaults to "dev".
            executor (str | None, optional): The executor for the job. Defaults to None.
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
            reload (bool, optional): Whether to reload the job. Defaults to False.
            result_expiration_time (float | dt.timedelta | None, optional): The result expiration time for the job.
                Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            UUID: The UUID of the added job.
        """
        with SchedulerManager(
            name=name, base_dir=self._base_dir, role="scheduler"
        ) as sm:
            return sm.add_job(
                self._run,
                args=(
                    name,
                    environment,
                    inputs,
                    final_vars,
                    executor,
                    with_tracker,
                    reload,
                ),
                kwargs=kwargs,
                job_executor=(
                    executor
                    if executor in ["async", "threadpool", "processpool"]
                    else "threadpool"
                ),
                result_expiration_time=result_expiration_time,
            )

    def schedule(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        environment: str = "dev",
        executor: str | None = None,
        with_tracker: bool | None = None,
        trigger_type: str | None = None,
        paused: bool = False,
        coalesce: str = "latest",
        misfire_grace_time: float | dt.timedelta | None = None,
        max_jitter: float | dt.timedelta | None = None,
        max_running_jobs: int | None = None,
        conflict_policy: str = "do_nothing",
        # job_result_expiration_time: float | dt.timedelta = 0,
        **kwargs,
    ) -> str:
        """
        Schedule a pipeline for execution.

        Args:
            name (str): The name of the pipeline.
            environment (str, optional): The environment in which the pipeline will run. Defaults to "dev".
            executor (str | None, optional): The executor to use for running the pipeline. Defaults to None.
            trigger_type (str | None, optional): The type of trigger for the pipeline. Defaults to None.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            with_tracker (bool | None, optional): Whether to include a tracker for the pipeline. Defaults to None.
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
            **kwargs: Additional keyword arguments for the trigger.

        Returns:
            str: The ID of the scheduled pipeline.

        Raises:
            ValueError: If APScheduler4 is not installed.

        """
        if SchedulerManager is None:
            raise ValueError("APScheduler4 not installed. Please install it first.")

        if "pipeline" in self.cfg.scheduler:
            scheduler_cfg = self.cfg.scheduler.pipeline.get(name, None)  # .copy()
        else:
            scheduler_cfg = {}

        trigger_type = trigger_type or scheduler_cfg.get("trigger_type", None)

        trigger_kwargs = {
            key: kwargs.pop(key, None) or scheduler_cfg.get(key, None)
            for key in ALL_TRIGGER_KWARGS.get(trigger_type, [])
            if key in kwargs or key in scheduler_cfg
        }

        schedule_kwargs = {
            arg: eval(arg) or scheduler_cfg.get(arg, None)
            for arg in [
                # "executor",
                "paused",
                "coalesce",
                "misfire_grace_time",
                "max_jitter",
                "max_running_jobs",
                "conflict_policy",
                # "job_result_expiration_time",
            ]
        }
        schedule_kwargs["paused"] = schedule_kwargs.get("paused", False) or False

        with SchedulerManager(
            name=name + "_scheduler", base_dir=self._base_dir, role="scheduler"
        ) as sm:
            trigger = get_trigger(trigger_type, **trigger_kwargs)
            # print("datastore", sm.data_store)
            # print("event_broker", sm.event_broker)
            print("trigger", trigger)
            print("kwargs", kwargs)
            print("scheduler_kwargs", schedule_kwargs)
            id_ = sm.add_schedule(
                func_or_task_id=self._run,
                trigger=trigger,
                args=(name, environment, inputs, final_vars, executor, with_tracker),
                kwargs=kwargs,
                job_executor=(
                    executor
                    if executor in ["async", "threadpool", "processpool"]
                    else "threadpool"
                ),
                **schedule_kwargs,
            )
            logger.success(
                f"Added scheduler for {name} in environment {environment} with id {id_}"
            )
            return id_

    def new(
        self,
        name: str,
        overwrite: bool = False,
        params: dict | None = None,
        run: dict | None = None,
        schedule: dict | None = None,
        tracker: dict | None = None,
    ):
        """
        Add a new item to the pipeline.

        Args:
            name (str): The name of the item.
            overwrite (bool, optional): Whether to overwrite an existing item with the same name. Defaults to False.
            params (dict | None, optional): The parameters for the item. Defaults to None.
            run (dict | None, optional): The run configuration for the item. Defaults to None.
            schedule (dict | None, optional): The schedule configuration for the item. Defaults to None.
            tracker (dict | None, optional): The tracker configuration for the item. Defaults to None.
        """
        self.add(name, overwrite, params, run, schedule, tracker)

    def add(
        self,
        name: str,
        overwrite: bool = False,
        params: dict | None = None,
        run: dict | None = None,
        schedule: dict | None = None,
        tracker: dict | None = None,
    ):
        """
        Adds a new pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
            params (dict | None, optional): The parameters for the pipeline. Defaults to None.
            run (dict | None, optional): The run configuration for the pipeline. Defaults to None.
            schedule (dict | None, optional): The schedule configuration for the pipeline. Defaults to None.
            tracker (dict | None, optional): The tracker configuration for the pipeline. Defaults to None.
        """
        logger.info(f"Creating new pipeline {name}")

        if not os.path.exists(self._conf_dir):
            raise ValueError(
                f"Configuration path {self._conf_dir} does not exist. Please run flowerpower init first."
            )
        if not os.path.exists(self._pipeline_dir):
            raise ValueError(
                f"Pipeline path {self._pipeline_dir} does not exist. Please run flowerpower init first."
            )

        if os.path.exists(f"{self._pipeline_dir}/{name}.py") and not overwrite:
            raise ValueError(
                f"Pipeline {name} already exists. Use `overwrite=True` to overwrite."
            )

        os.makedirs(self._pipeline_dir, exist_ok=True)
        with open(f"{self._pipeline_dir}/{name}.py", "w") as f:
            f.write(
                PIPELINE_PY_TEMPLATE.format(
                    name=name, date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
        logger.info(f"Created pipeline module {name}.py")

        run = run or {
            "dev": {"final_vars": [], "inputs": {}},
            "prod": {"final_vars": [], "inputs": {}},
        }

        self.cfg.update({"run": {name: run}, "params": {name: params}}, name="pipeline")
        logger.info(f"Updated pipeline configuration {self._conf_dir}/pipeline.yml")
        self.cfg.update({"pipeline": {name: schedule}}, name="scheduler")
        logger.info(f"Updated scheduler configuration {self._conf_dir}/scheduler.yml")
        self.cfg.update({"pipeline": {name: tracker}}, name="tracker")
        logger.info(f"Updated tracker configuration {self._conf_dir}/tracker.yml")
        self.cfg.write(pipeline=True, scheduler=True, tracker=True)

        logger.success(f"Created pipeline {name}")

    def delete(self, name: str, cfg: bool = True, module: bool = False):
        """
        Delete a pipeline.

        Args:
            name (str): The name of the pipeline to delete.
            cfg (bool, optional): Whether to delete the pipeline configuration. Defaults to True.
            module (bool, optional): Whether to delete the pipeline module file. Defaults to False.
        """

        if cfg:
            self.cfg.pipeline.run.pop(name)
            self.cfg.pipeline.params.pop(name)
            self.cfg.scheduler.pipeline.pop(name)
            self.cfg.tracker.pipeline.pop(name)
            self.cfg.write(pipeline=True, scheduler=True, tracker=True)
            logger.info(f"Deleted pipeline config for {name}")

        if module:
            if os.path.exists(f"{self._pipeline_dir}/{name}.py"):
                os.remove(f"{self._pipeline_dir}/{name}.py")
                logger.info(f"Deleted pipeline module {name}.py")

    def show(
        self, name: str, format: str = "png", view: bool = False, reload: bool = False
    ):
        """
        Display the graph of functions for a given name.

        Args:
            name (str): The name of the graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            view (bool, optional): Whether to open the graph file after generating it. Defaults to False.
            reload (bool, optional): Whether to reload the graph data. Defaults to False.

        Returns:
            graph: The generated graph object.
        """
        os.makedirs(os.path.join(self._base_dir, "graphs"), exist_ok=True)
        dr, _ = self._get_driver(
            name=name, executor=None, with_tracker=False, reload=reload
        )
        graph = dr.display_all_functions(
            os.path.join(self._base_dir, "graphs", f"{name}.{format}")
        )
        if view:
            graph.view()
        return graph


class Pipeline(PipelineManager):
    def __init__(self, name: str, base_dir: str | None = None):
        super().__init__(base_dir)
        self.name = name
        self.load_module()

    def run(
        self,
        environment: str = "dev",
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        name = self.name
        return super().run(
            name=name,
            environment=environment,
            executor=executor,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            reload=reload,
            **kwargs,
        )

    def run_job(
        self,
        environment: str = "dev",
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        name = self.name
        return super().run_job(
            name=name,
            environment=environment,
            executor=executor,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            reload=reload,
            **kwargs,
        )

    def add_job(
        self,
        environment: str = "dev",
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        reload: bool = False,
        result_expiration_time: float | dt.timedelta = 0,
        **kwargs,
    ) -> UUID:
        name = self.name
        return super().add_job(
            name=name,
            environment=environment,
            executor=executor,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            reload=reload,
            result_expiration_time=result_expiration_time,
            **kwargs,
        )

    def schedule(
        self,
        environment: str = "dev",
        trigger_type: str = "cron",
        inputs: dict | None = None,
        final_vars: list | None = None,
        executor: str | None = None,
        with_tracker: bool = False,
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
            environment=environment,
            executor=executor,
            trigger_type=trigger_type,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            paused=paused,
            coalesce=coalesce,
            misfire_grace_time=misfire_grace_time,
            max_jitter=max_jitter,
            max_running_jobs=max_running_jobs,
            # job_result_expiration_time=job_result_expiration_time,
            conflict_policy=conflict_policy,
            **kwargs,
        )

    def show(self, format: str = "png", view: bool = False, reload: bool = False):
        return super().show(self.name, format=format, view=view, reload=reload)

    def delete(self, cfg: bool = True, module: bool = False):
        return super().delete(self.name, cfg, module)

    def load_module(self):
        super().load_module(self.name)


def add(
    name: str,
    overwrite: bool = False,
    params: dict | None = None,
    run: dict | None = None,
    schedule: dict | None = None,
    tracker: dict | None = None,
    base_dir: str | None = None,
):
    """
    Add a pipeline to the PipelineManager.

    Args:
        name (str): The name of the pipeline.
        overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
        params (dict | None, optional): The parameters for the pipeline. Defaults to None.
        run (dict | None, optional): The run configuration for the pipeline. Defaults to None.
        schedule (dict | None, optional): The schedule configuration for the pipeline. Defaults to None.
        tracker (dict | None, optional): The tracker configuration for the pipeline. Defaults to None.
        base_dir (str | None, optional): The base path for the pipeline. Defaults to None.
    """
    pm = PipelineManager(base_dir=base_dir)
    pm.add(name, overwrite, params, run, schedule, tracker)


def new(
    name: str,
    overwrite: bool = False,
    params: dict | None = None,
    run: dict | None = None,
    schedule: dict | None = None,
    tracker: dict | None = None,
    base_dir: str | None = None,
):
    """
    Create a new pipeline.

    Args:
        name (str): The name of the pipeline.
        overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
        params (dict | None, optional): The parameters for the pipeline. Defaults to None.
        run (dict | None, optional): The run configuration for the pipeline. Defaults to None.
        schedule (dict | None, optional): The schedule configuration for the pipeline. Defaults to None.
        tracker (dict | None, optional): The tracker configuration for the pipeline. Defaults to None.
        base_dir (str | None, optional): The base path for the pipeline. Defaults to None.
    """
    pm = PipelineManager(base_dir=base_dir)
    pm.new(name, overwrite, params, run, schedule, tracker)


def run(
    name: str,
    environment: str = "dev",
    inputs: dict | None = None,
    final_vars: list | None = None,
    executor: str | None = None,
    with_tracker: bool = False,
    base_dir: str | None = None,
    reload: bool = False,
    **kwargs,
) -> Any:
    """
    Run the pipeline with the given parameters.

    Args:
        name (str): The name of the pipeline.
        environment (str, optional): The environment to run the pipeline in. Defaults to "dev".
        executor (str | None, optional): The executor to use. Defaults to None.
        inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
        final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
        with_tracker (bool, optional): Whether to use the tracker. Defaults to False.
        base_dir (str | None, optional): The base path for the pipeline. Defaults to None.
        reload (bool, optional): Whether to reload the pipeline. Defaults to False.
        **kwargs: Additional keyword arguments.
    Returns:
        Any: The result of running the pipeline.
    """
    p = Pipeline(name=name, base_dir=base_dir)
    return p.run(
        environment=environment,
        executor=executor,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        reload=reload,
        **kwargs,
    )


def run_job(
    name: str,
    environment: str = "dev",
    inputs: dict | None = None,
    final_vars: list | None = None,
    executor: str | None = None,
    with_tracker: bool | None = None,
    base_dir: str | None = None,
    reload: bool = False,
    **kwargs,
) -> Any:
    """
    Add a job to run the pipeline with the given parameters to the scheduler.
    Executes the job immediatly and returns the job result.

    Args:
        name (str): The name of the job.
        environment (str, optional): The environment to run the job in. Defaults to "dev".
        executor (str | None, optional): The executor to use for the job. Defaults to None.
        inputs (dict | None, optional): The inputs for the job. Defaults to None.
        final_vars (list | None, optional): The final variables for the job. Defaults to None.
        with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
        base_dir (str | None, optional): The base path for the job. Defaults to None.
        reload (bool, optional): Whether to reload the job. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        Any: The result of running the job.
    """

    p = Pipeline(name=name, base_dir=base_dir)
    return p.run_job(
        environment=environment,
        executor=executor,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        reload=reload,
        **kwargs,
    )


def add_job(
    name: str,
    environment: str = "dev",
    inputs: dict | None = None,
    final_vars: list | None = None,
    executor: str | None = None,
    with_tracker: bool | None = None,
    base_dir: str | None = None,
    reload: bool = False,
    result_expiration_time: float | dt.timedelta = 0,
    **kwargs,
) -> UUID:
    """
    Add a job to run the pipeline with the given parameters to the scheduler data store.
    Executes the job immediatly and returns the job id (UUID). The job result will be stored in the data store for the
    given `result_expiration_time` and can be fetched using the job id (UUID).

    Args:
        name (str): The name of the job.
        environment (str, optional): The environment to run the job in. Defaults to "dev".
        executor (str | None, optional): The executor to use for the job. Defaults to None.
        inputs (dict | None, optional): The inputs for the job. Defaults to None.
        final_vars (list | None, optional): The final variables for the job. Defaults to None.
        with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
        base_dir (str | None, optional): The base path for the job. Defaults to None.
        reload (bool, optional): Whether to reload the job. Defaults to False.
        result_expiration_time (float | dt.timedelta | None, optional): The expiration time for the job result.
            Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        UUID: The UUID of the added job.
    """
    p = Pipeline(name=name, base_dir=base_dir)
    return p.add_job(
        environment=environment,
        executor=executor,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        reload=reload,
        result_expiration_time=result_expiration_time,
        **kwargs,
    )


def schedule(
    name: str,
    environment: str = "dev",
    trigger_type: str = "cron",
    inputs: dict | None = None,
    final_vars: list | None = None,
    executor: str | None = None,
    with_tracker: bool = False,
    paused: bool = False,
    coalesce: str = "latest",
    misfire_grace_time: float | dt.timedelta | None = None,
    max_jitter: float | dt.timedelta | None = None,
    max_running_jobs: int | None = None,
    conflict_policy: str = "do_nothing",
    # job_result_expiration_time: float | dt.timedelta = 0,
    base_dir: str | None = None,
    **kwargs,
) -> str:
    """
    Schedule a pipeline for execution.

    Args:
        name (str): The name of the pipeline.
        environment (str, optional): The environment in which the pipeline will run. Defaults to "dev".
        executor (str | None, optional): The executor to use for running the pipeline. Defaults to None.
        trigger_type (str, optional): The type of schedule. Defaults to "cron".
        auto_start (bool, optional): Whether to automatically start the pipeline. Defaults to True.
        background (bool, optional): Whether to run the pipeline in the background. Defaults to False.
        inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
        final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
        with_tracker (bool, optional): Whether to use a tracker for the pipeline. Defaults to False.
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
        **kwargs: Additional keyword arguments.

    Returns:
        str: The ID of the scheduled pipeline.
    """
    p = Pipeline(name=name, base_dir=base_dir)
    return p.schedule(
        environment=environment,
        executor=executor,
        tigger_type=trigger_type,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        paused=paused,
        coalesce=coalesce,
        misfire_grace_time=misfire_grace_time,
        max_jitter=max_jitter,
        max_running_jobs=max_running_jobs,
        # job_result_expiration_time=job_result_expiration_time,
        conflict_policy=conflict_policy,
        **kwargs,
    )


def show(
    name: str,
    format: str = "png",
    view: bool = False,
    base_dir: str | None = None,
    reload: bool = False,
):
    """
    Display the pipeline with the given name.

    Parameters:
        name (str): The name of the pipeline.
        format (str, optional): The format of the displayed pipeline. Defaults to "png".
        view (bool, optional): Whether to display the pipeline. Defaults to False.
        base_dir (str | None, optional): The base path of the pipeline. Defaults to None.
        reload (bool, optional): Whether to reload the pipeline. Defaults to False.
    """
    p = Pipeline(name=name, base_dir=base_dir)
    p.show(format=format, view=view, reload=reload)


def delete(name: str, base_dir: str | None = None, module: bool = False):
    """
    Delete a pipeline.

    Args:
        name (str): The name of the pipeline to delete.
        base_dir (str | None, optional): The base path of the pipeline. Defaults to None.
        module (bool, optional): Whether to delete the pipeline module. Defaults to False.
    """
    p = Pipeline(name=name, base_dir=base_dir)
    p.delete(module=module)
