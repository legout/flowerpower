"""
APScheduler implementation for FlowerPower scheduler.

This module implements the scheduler interfaces using APScheduler as the backend.
"""

import collections.abc
import datetime as dt
import importlib.util
import uuid
from typing import Any

from fsspec.spec import AbstractFileSystem
from loguru import logger

# Check if APScheduler is available
if not importlib.util.find_spec("apscheduler"):
    raise ImportError(
        "APScheduler is not installed. Please install it using `pip install "
        "'apscheduler>4.0.0a1'`, 'conda install apscheduler4' or `pip install flowerpower[apscheduler]`"
    )

from apscheduler import Scheduler
from apscheduler.executors.async_ import AsyncJobExecutor
from apscheduler.executors.subprocess import ProcessPoolJobExecutor
from apscheduler.executors.thread import ThreadPoolJobExecutor

from ...cfg import Config
from ..base import BaseTrigger, BaseWorker
from .setup import APSBackend, APSDataStore, APSEventBroker
from .trigger import APSTrigger
from .utils import display_jobs, display_schedules

# Patch pickle if needed
try:
    from ...utils.monkey import patch_pickle

    patch_pickle()
except Exception as e:
    logger.warning(f"Failed to patch pickle: {e}")


class APSWorker(BaseWorker):
    """Implementation of BaseScheduler using APScheduler."""

    def __init__(
        self,
        name: str | None = None,
        base_dir: str | None = None,
        backend: APSBackend | None = None,
        storage_options: dict[str, Any] = None,
        fs: AbstractFileSystem | None = None,
        **kwargs,
    ):
        """
        Initialize the APScheduler backend.

        Args:
            name: Name of the scheduler
            base_dir: Base directory for the FlowerPower project
            backend: APSBackend instance with data store and event broker
            storage_options: Storage options for filesystem access
            fs: Filesystem to use
            **kwargs: Additional parameters
        """
        logger_ = kwargs.pop("logger", logger)
        default_job_executor = kwargs.pop("default_job_executor", "threadpool")

        super().__init__(
            name=name,
            base_dir=base_dir,
            fs=fs,
            backend=backend,
            storage_options=storage_options,
            **kwargs,
        )

        # Set up job executors
        self._setup_job_executors()

        self._client = Scheduler(
            job_executors=self._job_executors,
            event_broker=self._backend.event_broker.client,
            data_store=self._backend.data_store.client,
            identity=self.name,
            logger=logger_,
            cleanup_interval=self.cfg.project.worker.cleanup_interval,
            max_concurrent_jobs=self.cfg.project.worker.max_concurrent_jobs,
            default_job_executor=default_job_executor,
        )

    def _load_config(self) -> None:
        """Load the configuration."""
        self.cfg = Config.load(base_dir=self._base_dir, fs=self._fs)

    def _setup_backend(self) -> None:
        """
        Set up the data store and SQLAlchemy engine for the scheduler.

        This method initializes the data store and SQLAlchemy engine using configuration
        values. It validates configuration, handles errors, and logs the setup process.

        Raises:
            RuntimeError: If the data store setup fails due to misconfiguration or connection errors.
        """
        # Validate configuration
        backend_cfg = getattr(self.cfg.project.worker, "backend", None)
        if not backend_cfg:
            logger.error("Backend configuration is missing in project.worker.backend.")
            raise RuntimeError("Backend configuration is missing.")

        data_store_cfg = backend_cfg.get("data_store", None)
        if not data_store_cfg:
            logger.error(
                "Data store configuration is missing in project.worker.backend.data_store."
            )
            raise RuntimeError("Data store configuration is missing.")

        event_broker_cfg = backend_cfg.get("event_broker", None)
        if not event_broker_cfg:
            logger.error(
                "Event broker configuration is missing in project.worker.backend.event_broker."
            )
            raise RuntimeError("Event broker configuration is missing.")

        try:
            asp_datastore = APSDataStore(
                type=data_store_cfg.get("type", "memory"),
                engine_or_uri=data_store_cfg.get("uri", None),
                schema=data_store_cfg.get("schema", "flowerpower"),
                username=data_store_cfg.get("username", None),
                password=data_store_cfg.get("password", None),
                ssl=data_store_cfg.get("ssl", False),
                **data_store_cfg.get("kwargs", {}),
            )
            logger.info(
                "Data store setup successful (type=%r, uri=%r)",
                data_store_cfg.get("type", "memory"),
                data_store_cfg.get("uri", None),
            )
        except Exception as exc:
            logger.exception(
                "Failed to set up data store (type=%r, uri=%r): %s",
                data_store_cfg.get("type", "memory"),
                data_store_cfg.get("uri", None),
                exc,
            )
        try:
            aps_eventbroker = APSEventBroker(
                type=event_broker_cfg.get("type", "memory"),
                uri=event_broker_cfg.get("uri", None),
                sqla_engine=asp_datastore.sqla_engine,
                host=event_broker_cfg.get("host", None),
                port=event_broker_cfg.get("port", 0),
                username=event_broker_cfg.get("username", None),
                password=event_broker_cfg.get("password", None),
            )
        except Exception as exc:
            logger.exception(
                "Failed to set up event broker (type=%r, uri=%r): %s",
                event_broker_cfg.get("type", "memory"),
                event_broker_cfg.get("uri", None),
                exc,
            )
        self._backend = APSBackend(
            data_store=asp_datastore, event_broker=aps_eventbroker
        )

    def _setup_job_executors(self) -> None:
        """Set up job executors."""
        self._job_executors = {
            "async": AsyncJobExecutor(),
            "threadpool": ThreadPoolJobExecutor(),
            "processpool": ProcessPoolJobExecutor(),
        }

    def start_worker(self, background: bool = False) -> None:
        """
        Start a worker.

        Args:
            background: Whether to run in the background
        """
        if background:
            self._scheduler.start_in_background()
        else:
            self._scheduler.run_until_stopped()

    def stop_worker(self) -> None:
        """Stop the worker."""
        self._scheduler.stop()

    def add_job(
        self,
        func: collections.abc.Callable,
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        id: str | None = None,
        result_ttl: float | dt.timedelta = 0,
        **job_kwargs,
    ) -> str:
        """
        Add a job for immediate execution.

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            id: Optional job ID
            result_expiration_time: How long to keep the result
            **job_kwargs: Additional job parameters

        Returns:
            str: Job ID
        """
        job_executor = job_kwargs.pop("job_executor", "threadpool")

        # Convert result_expiration_time to datetime.timedelta if it's not already
        if isinstance(result_ttl, (int, float)):
            result_ttl = dt.timedelta(seconds=result_ttl)

        id = id or str(uuid.uuid4())

        job = self._scheduler.add_job(
            func,
            args=args or (),
            kwargs=kwargs or {},
            # id=job_id,
            job_executor=job_executor,
            result_expiration_time=result_ttl,
            **job_kwargs,
        )

        return job

    def add_schedule(
        self,
        func: collections.abc.Callable,
        trigger: BaseTrigger,
        id: str | None = None,
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        **schedule_kwargs,
    ) -> str:
        """
        Schedule a job for repeated execution.

        Args:
            func: Function to execute
            trigger: Trigger defining when to execute the function
            id: Optional schedule ID
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            **schedule_kwargs: Additional schedule parameters

        Returns:
            str: Schedule ID
        """
        job_executor = schedule_kwargs.pop("job_executor", "threadpool")

        # Get the actual trigger instance
        if isinstance(trigger, APSTrigger):
            trigger_instance = trigger.get_trigger_instance()
        else:
            # If it's not an APSchedulerTrigger, we assume it's already a trigger instance
            trigger_instance = trigger

        schedule = self._scheduler.add_schedule(
            func,
            trigger=trigger_instance,
            id=id,
            args=args or (),
            kwargs=kwargs or {},
            job_executor=job_executor,
            **schedule_kwargs,
        )

        return schedule

    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a schedule.

        Args:
            schedule_id: ID of the schedule to remove

        Returns:
            bool: True if the schedule was removed, False otherwise
        """
        try:
            self._scheduler.remove_schedule(schedule_id)
            return True
        except Exception as e:
            logger.error(f"Failed to remove schedule {schedule_id}: {e}")
            return False

    def remove_all_schedules(self) -> None:
        """Remove all schedules."""
        for sched in self._scheduler.get_schedules():
            self._scheduler.remove_schedule(sched.id)

    def get_job_result(self, job_id: str) -> Any:
        """
        Get the result of a job.

        Args:
            job_id: ID of the job

        Returns:
            Any: Result of the job
        """
        return self._scheduler.get_job_result(job_id)

    def get_schedules(self, as_dict: bool = False) -> list[Any]:
        """
        Get all schedules.

        Args:
            as_dict: Whether to return schedules as dictionaries

        Returns:
            List[Any]: List of schedules
        """
        schedules = self._scheduler.get_schedules()
        if as_dict:
            return [sched.to_dict() for sched in schedules]
        return schedules

    def get_jobs(self, as_dict: bool = False) -> list[Any]:
        """
        Get all jobs.

        Args:
            as_dict: Whether to return jobs as dictionaries

        Returns:
            List[Any]: List of jobs
        """
        jobs = self._scheduler.get_jobs()
        if as_dict:
            return [job.to_dict() for job in jobs]
        return jobs

    def show_schedules(self) -> None:
        """Display the schedules in a user-friendly format."""
        display_schedules(self._scheduler.get_schedules())

    def show_jobs(self) -> None:
        """Display the jobs in a user-friendly format."""
        display_jobs(self._scheduler.get_jobs())
