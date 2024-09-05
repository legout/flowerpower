import datetime as dt
import importlib.util
import sys

if importlib.util.find_spec("apscheduler"):
    from apscheduler import Scheduler, current_scheduler
    from apscheduler.executors.async_ import AsyncJobExecutor
    from apscheduler.executors.subprocess import ProcessPoolJobExecutor
    from apscheduler.executors.thread import ThreadPoolJobExecutor

    from .helpers import monkey

    monkey.patch_pickle()

else:
    raise ImportError(
        "APScheduler is not installed. Please install it using `pip install"
        "'apscheduler>4.0.0a1'`, 'conda install apscheduler4' or `pip install flowerpower[scheduler]`"
    )

import os
import uuid
from typing import Any

from loguru import logger

from .cfg import Config
from .helpers.datastore import setup_data_store
from .helpers.eventbroker import setup_event_broker


class SchedulerManager(Scheduler):
    def __init__(
        self,
        name: str | None = None,
        base_dir: str | None = None,
        **kwargs,
    ):
        """
        Initializes the Scheduler object.

        Args:
            name (str | None, optional): The name of the scheduler. Defaults to None.
            base_dir (str | None, optional): The flowerpower base path. Defaults to None.
            **kwargs: Additional keyword arguments.

        """
        self.name = name or ""

        if base_dir is None:
            base_dir = os.getcwd()

        self._base_dir = base_dir
        self._conf_dir = os.path.join(base_dir, "conf")  # or conf_dir
        self._pipelines_path = os.path.join(base_dir, "pipelines")  # or pipelines_path

        self.cfg = Config(self._base_dir).scheduler
        # self._data_store = None
        # self._event_broker = None
        # self._sqla_engine = None

        self._setup_data_store()
        self._setup_event_broker()
        self._setup_job_executors()

        cleanup_interval = self.cfg.get("cleanup_interval", None) or {
            "unit": "minutes",
            "value": 15,
        }
        super().__init__(
            data_store=self._data_store,
            event_broker=self._event_broker,
            job_executors=self._job_executors,
            identity=self.name,
            logger=logger,
            cleanup_interval=dt.timedelta(
                **{cleanup_interval.unit: cleanup_interval.value}
            ),
            **kwargs,
        )

        sys.path.append(self._pipelines_path)

    def _setup_data_store(self):
        """
        Sets up the data store based on the configuration.

        If the configuration specifies a data store type, it retrieves the data store and SQLA engine
        using the `get_data_store` function. The data store type is obtained from the `type` key in the
        `data_store` section of the configuration. The engine or URI is obtained from the `uri` key in
        the `data_store` section of the configuration.

        Returns:
            None
        """
        if "data_store" in self.cfg:
            if "type" in self.cfg.data_store:
                self._data_store, self._sqla_engine = setup_data_store(
                    type=self.cfg.data_store.type,
                    engine_or_uri=self.cfg.data_store.get("uri", None),
                )

    def _setup_event_broker(self):
        """
        Sets up the event broker based on the configuration settings.

        If the 'event_broker' key is present in the configuration, it checks for the 'type' key.
        If the 'type' key is present, it initializes the event broker using the specified type and other optional
            parameters.
        The optional parameters include 'uri', 'sqla_engine', 'host', 'port', 'username', and 'password'.

        Parameters:
            None

        Returns:
            None
        """
        if "event_broker" in self.cfg:
            if "type" in self.cfg.event_broker:
                self._event_broker = setup_event_broker(
                    type=self.cfg.event_broker.type,
                    uri=self.cfg.event_broker.get("uri", None),
                    sqla_engine=self._sqla_engine,
                    host=self.cfg.event_broker.get("host", "localhost"),
                    port=self.cfg.event_broker.get("port", 1883),
                    username=self.cfg.event_broker.get("username", None),
                    password=self.cfg.event_broker.get("password", None),
                )

    def _setup_job_executors(self):
        self._job_executors = {
            "async": AsyncJobExecutor(),
            "threadpool": ThreadPoolJobExecutor(),
            "processpool": ProcessPoolJobExecutor(),
        }

    def start_worker(
        self,
        background: bool = False,
    ):
        """
        Starts the worker.

        Parameters:
            background (bool): If True, starts the worker in the background. If False, runs the worker until stopped.
        """
        if background:
            self.start_in_background()
        else:
            self.run_until_stopped()

    def stop_worker(self) -> None:
        """
        Stops the worker and closes the exit stack.

        Returns:
            None
        """
        self.stop()
        self._exit_stack.close()

    def remove_all_schedules(self):
        """
        Removes all schedules from the scheduler.

        This method iterates over all schedules in the scheduler and removes them one by one.

        Parameters:
            None

        Returns:
            None
        """
        for sched in self.get_schedules():
            self.remove_schedule(sched.id)


# Wrapper functions for backward compatibility
def get_schedule_manager(
    name: str | None = None,
    base_dir: str | None = None,
    *args,
    **kwargs,
) -> SchedulerManager:
    """
    Returns a SchedulerManager instance with the specified name and base path.

    Args:
        name (str | None, optional): The name of the scheduler manager. Defaults to None.
        base_dir (str | None, optional): The base path for the scheduler manager. Defaults to None.
        *args: Additional positional arguments to be passed to the SchedulerManager constructor.
        **kwargs: Additional keyword arguments to be passed to the SchedulerManager constructor.

    Returns:
        SchedulerManager: The initialized SchedulerManager instance.
    """
    manager = SchedulerManager(name, base_dir, *args, **kwargs)
    return manager


def get_current_scheduler_manager() -> SchedulerManager | None:
    """
    Returns the current scheduler manager.

    Returns:
        The current scheduler manager if available, otherwise None.
    """
    return current_scheduler.get()


# def get_scheduler(
#     name: str | None = None,
#     base_dir: str | None = None,
#     *args,
#     **kwargs,
# ) -> SchedulerManager:
#     """
#     Get the scheduler object.

#     Args:
#         name (str | None, optional): The name of the scheduler. Defaults to None.
#         base_dir (str | None, optional): The base path. Defaults to None.
#         *args: Additional positional arguments.
#         **kwargs: Additional keyword arguments.

#     Returns:
#         SchedulerManager: The initialized SchedulerManager instance.
#     """
#     manager = get_schedule_manager(name, base_dir, *args, **kwargs)
#     return manager


def start_worker(
    name: str | None = None,
    base_dir: str | None = None,
    background: bool = False,
    *args,
    **kwargs,
) -> SchedulerManager:
    """
    Start the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path for the scheduler. Defaults to None.
        background (bool, optional): Whether to start the scheduler in the background. Defaults to False.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        SchedulerManager: The scheduler instance.
    """
    # manager = get_schedule_manager(name, base_dir, role="worker", *args, **kwargs)
    with SchedulerManager(name, base_dir, *args, **kwargs) as manager:
        manager.start_worker(background)


# def get_current_scheduler() -> Scheduler | None:
#     return SchedulerManager.get_current_scheduler()


def remove_all_schedules(
    name: str | None = None,
    base_dir: str | None = None,
    *args,
    **kwargs,
):
    """
    Remove all schedules.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.
    """
    with SchedulerManager(name, base_dir, role="scheduler", *args, **kwargs) as manager:
        manager.remove_all_schedules()


def add_schedule(
    name: str | None = None,
    base_dir: str | None = None,
    *args,
    **kwargs,
) -> str:
    """
    Add a schedule to the scheduler.

    Args:
        name (str, optional): The name of the schedule. Defaults to None.
        base_dir (str, optional): The base path for the schedule. Defaults to None.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        str: The ID of the added schedule.
    """
    with SchedulerManager(name, base_dir, role="scheduler") as manager:
        id_ = manager.add_schedule(*args, **kwargs)
    return id_


def add_job(
    name: str | None = None,
    base_dir: str | None = None,
    *args,
    **kwargs,
) -> uuid.UUID:
    """
    Add a job to the scheduler. Executes the job immediatly and returns the job id (UUID).
    The job result will be stored in the data store for the given `result_expiration_time` and
    can be fetched using the job id (UUID).

    Args:
        name (str | None): The name of the job. Defaults to None.
        base_dir (str | None): The base path for the job. Defaults to None.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        uuid.UUID: The ID of the added job.
    """
    with SchedulerManager(name, base_dir, role="scheduler") as manager:
        id_ = manager.add_job(*args, **kwargs)
    return id_


def run_job(
    name: str | None = None,
    base_dir: str | None = None,
    *args,
    **kwargs,
) -> Any:
    """
    Run a job using the SchedulerManager. Executes the job immediatly and returns the result of the job.

    Args:
        name (str, optional): The name of the job. Defaults to None.
        base_dir (str, optional): The base path of the job. Defaults to None.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Any: The SchedulerManager instance.

    """
    with SchedulerManager(name, base_dir, role="scheduler") as manager:
        result = manager.run_job(*args, **kwargs)

    return result


def get_schedules(
    name: str | None = None,
    base_dir: str | None = None,
    *args,
    **kwargs,
):
    """
    Get all schedules from the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        list: A list of schedules.
    """
    with SchedulerManager(name, base_dir, role="scheduler", *args, **kwargs) as manager:
        schedules = manager.get_schedules()
    return schedules


def get_tasks(
    name: str | None = None,
    base_dir: str | None = None,
    *args,
    **kwargs,
):
    """
    Get all tasks from the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        list: A list of tasks.
    """
    with SchedulerManager(name, base_dir, role="scheduler", *args, **kwargs) as manager:
        tasks = manager.get_tasks()
    return tasks


def get_jobs(
    name: str | None = None,
    base_dir: str | None = None,
    *args,
    **kwargs,
):
    """
    Get all jobs from the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        list: A list of jobs.
    """
    with SchedulerManager(name, base_dir, role="scheduler", *args, **kwargs) as manager:
        jobs = manager.get_jobs()
    return jobs


def get_job_result(
    job_id: str,
    name: str | None = None,
    base_dir: str | None = None,
    *args,
    **kwargs,
) -> Any:
    """
    Get the result of a job using the job id.

    Args:
        job_id (str): The ID of the job.
        name (str | None, optional): The name of the job. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        Any: The result of the job.
    """
    with SchedulerManager(name, base_dir, role="scheduler", *args, **kwargs) as manager:
        result = manager.get_job_result(job_id)
    return result
