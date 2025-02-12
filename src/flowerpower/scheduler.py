import importlib.util
import sys

if importlib.util.find_spec("apscheduler"):
    from apscheduler import Scheduler, current_scheduler
    from apscheduler.executors.async_ import AsyncJobExecutor
    from apscheduler.executors.subprocess import ProcessPoolJobExecutor
    from apscheduler.executors.thread import ThreadPoolJobExecutor

    from .utils.monkey import patch_pickle

    patch_pickle()

else:
    raise ImportError(
        "APScheduler is not installed. Please install it using `pip install"
        "'apscheduler>4.0.0a1'`, 'conda install apscheduler4' or `pip install flowerpower[scheduler]`"
    )

import posixpath
import uuid
from pathlib import Path
from typing import Any

from fsspec.spec import AbstractFileSystem
from loguru import logger

from .cfg import Config
from .fs import get_filesystem
from .utils.datastore import setup_data_store
from .utils.eventbroker import setup_event_broker
from .utils.scheduler import display_jobs, display_schedules, display_tasks


class SchedulerManager(Scheduler):
    def __init__(
        self,
        name: str | None = None,
        base_dir: str | None = None,
        storage_options: dict = {},
        fs: AbstractFileSystem | None = None,
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
        self._base_dir = base_dir or str(Path.cwd())
        self._storage_options = storage_options
        if fs is None:
            fs = get_filesystem(self._base_dir, **self._storage_options)
        self._fs = fs

        self._conf_path = "conf"
        self._pipelines_path = "pipelines"  # or pipelines_path

        self._sync_fs()
        self.load_config()

        self._setup_data_store()
        self._setup_event_broker()
        self._setup_job_executors()

        super().__init__(
            data_store=self._data_store,
            event_broker=self._event_broker,
            job_executors=self._job_executors,
            identity=self.name,
            logger=logger,
            cleanup_interval=self.cfg.project.worker.cleanup_interval,
            max_concurrent_jobs=self.cfg.project.worker.max_concurrent_jobs,
            **kwargs,
        )

        sys.path.append(self._pipelines_path)

    def _sync_fs(self):
        """
        Sync the filesystem.

        Returns:
            None
        """
        if self._fs.is_cache_fs:
            self._fs.sync()

        modules_path = posixpath.join(self._fs.path, self._pipelines_path)
        if modules_path not in sys.path:
            sys.path.append(modules_path)

    def load_config(self):
        """
        Load the configuration file.

        This method loads the configuration file specified by the `_conf_dir` attribute and
        assigns it to the `cfg` attribute.

        """
        self.cfg = Config.load(base_dir=self._base_dir, fs=self._fs)

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

        self._data_store, self._sqla_engine = setup_data_store(
            type=self.cfg.project.worker.data_store.get("type", "memory"),
            engine_or_uri=self.cfg.project.worker.data_store.get("uri", None),
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
        self._event_broker = setup_event_broker(
            type=self.cfg.project.worker.event_broker.get("type", "memory"),
            uri=self.cfg.project.worker.event_broker.get("uri", None),
            sqla_engine=self._sqla_engine,
            host=self.cfg.project.worker.event_broker.get("host", None),
            port=self.cfg.project.worker.event_broker.get("port", 0),
            username=self.cfg.project.worker.event_broker.get("username", None),
            password=self.cfg.project.worker.event_broker.get("password", None),
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

    def get_tasks(self, as_dict: bool = False):
        """
        Get all tasks from the scheduler.

        Args:
            as_dict (bool, optional): Whether to return the tasks as a list of dictionaries. Defaults to False.

        Returns:
            list: A list of tasks.
        """
        tasks = super().get_tasks()
        if as_dict:
            return [task.to_dict() for task in tasks]
        return super().get_tasks()

    def get_schedules(self, as_dict: bool = False):
        """
        Get all schedules from the scheduler.

        Args:
            as_dict (bool, optional): Whether to return the schedules as a list of dictionaries. Defaults to False.

        Returns:
            list: A list of schedules.
        """
        schedules = super().get_schedules()
        if as_dict:
            return [schedule.to_dict() for schedule in schedules]
        return schedules

    def get_schedule(self, id: str, as_dict: bool = False):
        """
        Get a schedule by ID.

        Args:
            id (str): The ID of the schedule.
            as_dict (bool, optional): Whether to return the schedule as a dictionary. Defaults to False.

        Returns:
            Schedule: The schedule object.
        """
        schedule = super().get_schedule(id)
        if as_dict:
            return schedule.to_dict()
        return schedule

    def get_jobs(self, as_dict: bool = False):
        """
        Get all jobs from the scheduler.

        Args:
            as_dict (bool, optional): Whether to return the jobs as a list of dictionaries. Defaults to False.

        Returns:
            list: A list of jobs.
        """
        jobs = super().get_jobs()
        if as_dict:
            return [job.to_dict() for job in jobs]
        return jobs

    def show_schedules(self):
        """
        Shows all schedules in the scheduler.

        This method iterates over all schedules in the scheduler and prints their details.

        Parameters:
            None
        """
        display_schedules(self.get_schedules())

    def show_tasks(self):
        """
        Shows all tasks in the scheduler.

        This method iterates over all tasks in the scheduler and prints their details.

        Parameters:
            None
        """
        display_tasks(self.get_tasks())

    def show_jobs(self):
        """
        Shows all jobs in the scheduler.

        This method iterates over all jobs in the scheduler and prints their details.

        Parameters:
            None
        """
        display_jobs(self.get_jobs())


# Wrapper functions for backward compatibility
def get_schedule_manager(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
) -> SchedulerManager:
    """
    Returns a SchedulerManager instance with the specified name and base path.

    Args:
        name (str | None, optional): The name of the scheduler manager. Defaults to None.
        base_dir (str | None, optional): The base path for the scheduler manager. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults to None.
        **kwargs: Additional keyword arguments to be passed to the SchedulerManager constructor.

    Returns:
        SchedulerManager: The initialized SchedulerManager instance.
    """
    manager = SchedulerManager(
        name, base_dir, storage_options=storage_options, fs=fs, **kwargs
    )
    return manager


def get_current_scheduler_manager() -> SchedulerManager | None:
    """
    Returns the current scheduler manager.

    Returns:
        The current scheduler manager if available, otherwise None.
    """
    return current_scheduler.get()


def start_worker(
    name: str | None = None,
    base_dir: str | None = None,
    background: bool = False,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
) -> SchedulerManager:
    """
    Start the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path for the scheduler. Defaults to None.
        background (bool, optional): Whether to start the scheduler in the background. Defaults to False.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        SchedulerManager: The scheduler instance.
    """
    # manager = get_schedule_manager(name, base_dir, role="worker", storage_options=storage_options, fs=fs, **kwargs)
    with SchedulerManager(
        name, base_dir, storage_options=storage_options, fs=fs, **kwargs
    ) as manager:
        manager.start_worker(background=background)


def remove_all_schedules(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
):
    """
    Remove all schedules.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults to None.
        **kwargs: Additional keyword arguments.
    """
    with SchedulerManager(
        name,
        base_dir,
        role="scheduler",
        storage_options=storage_options,
        fs=fs,
        **kwargs,
    ) as manager:
        manager.remove_all_schedules()


def add_schedule(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
) -> str:
    """
    Add a schedule to the scheduler.

    Args:
        name (str, optional): The name of the schedule. Defaults to None.
        base_dir (str, optional): The base path for the schedule. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults to None.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        str: The ID of the added schedule.
    """
    with SchedulerManager(name, base_dir, role="scheduler") as manager:
        id_ = manager.add_schedule(storage_options=storage_options, fs=fs, **kwargs)
    return id_


def add_job(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
) -> uuid.UUID:
    """
    Add a job to the scheduler. Executes the job immediatly and returns the job id (UUID).
    The job result will be stored in the data store for the given `result_expiration_time` and
    can be fetched using the job id (UUID).

    Args:
        name (str | None): The name of the job. Defaults to None.
        base_dir (str | None): The base path for the job. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults to None.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        uuid.UUID: The ID of the added job.
    """
    with SchedulerManager(name, base_dir, role="scheduler") as manager:
        id_ = manager.add_job(storage_options=storage_options, fs=fs, **kwargs)
    return id_


def run_job(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
) -> Any:
    """
    Run a job using the SchedulerManager. Executes the job immediatly and returns the result of the job.

    Args:
        name (str, optional): The name of the job. Defaults to None.
        base_dir (str, optional): The base path of the job. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults to None.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Any: The SchedulerManager instance.

    """
    with SchedulerManager(name, base_dir, role="scheduler") as manager:
        result = manager.run_job(storage_options=storage_options, fs=fs, **kwargs)

    return result


def get_schedules(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
):
    """
    Get all schedules from the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        list: A list of schedules.
    """
    with SchedulerManager(
        name,
        base_dir,
        role="scheduler",
        storage_options=storage_options,
        fs=fs,
        **kwargs,
    ) as manager:
        schedules = manager.get_schedules()
    return schedules


def get_tasks(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
):
    """
    Get all tasks from the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        list: A list of tasks.
    """
    with SchedulerManager(
        name,
        base_dir,
        role="scheduler",
        storage_options=storage_options,
        fs=fs,
        **kwargs,
    ) as manager:
        tasks = manager.get_tasks()
    return tasks


def get_jobs(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
):
    """
    Get all jobs from the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        list: A list of jobs.
    """
    with SchedulerManager(
        name,
        base_dir,
        role="scheduler",
        storage_options=storage_options,
        fs=fs,
        **kwargs,
    ) as manager:
        jobs = manager.get_jobs()
    return jobs


def get_job_result(
    job_id: str,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
) -> Any:
    """
    Get the result of a job using the job id.

    Args:
        job_id (str): The ID of the job.
        name (str | None, optional): The name of the job. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        Any: The result of the job.
    """
    with SchedulerManager(
        name,
        base_dir,
        role="scheduler",
        storage_options=storage_options,
        fs=fs,
        **kwargs,
    ) as manager:
        result = manager.get_job_result(job_id)
    return result


def show_schedules(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
):
    """
    Show all schedules in the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults
        **kwargs: Additional keyword arguments.
    """
    with SchedulerManager(
        name,
        base_dir,
        role="scheduler",
        storage_options=storage_options,
        fs=fs,
        **kwargs,
    ) as manager:
        manager.show_schedules()


def show_tasks(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
):
    """
    Show all tasks in the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults
        **kwargs: Additional keyword arguments.
    """
    with SchedulerManager(
        name,
        base_dir,
        role="scheduler",
        storage_options=storage_options,
        fs=fs,
        **kwargs,
    ) as manager:
        manager.show_tasks()


def show_jobs(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    **kwargs,
):
    """
    Show all jobs in the scheduler.

    Args:
        name (str | None, optional): The name of the scheduler. Defaults to None.
        base_dir (str | None, optional): The base path. Defaults to None.
        storage_options (dict, optional): The storage options. Defaults to {}.
        fs (AbstractFileSystem, optional): The filesystem. Defaults
        **kwargs: Additional keyword arguments.
    """
    with SchedulerManager(
        name,
        base_dir,
        role="scheduler",
        storage_options=storage_options,
        fs=fs,
        **kwargs,
    ) as manager:
        manager.show_jobs()
