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
        name: str | None = "flowerpower_apscheduler",
        base_dir: str | None = None,
        backend: APSBackend | dict | None = None,
        storage_options: dict[str, Any] = None,
        fs: AbstractFileSystem | None = None,
    ):
        """
        Initialize the APScheduler backend.

        Args:
            name: Name of the scheduler
            base_dir: Base directory for the FlowerPower project
            backend: APSBackend instance with data store and event broker
            storage_options: Storage options for filesystem access
            fs: Filesystem to use
            **cfg_updates: Configuration updates for the scheduler
        """
        super().__init__(
            type="apscheduler",
            name=name,
            base_dir=base_dir,
            fs=fs,
            backend=backend,
            storage_options=storage_options,
        )

        if not isinstance(backend, APSBackend):
            self._setup_backend()

        # Set up job executors
        self._job_executors = {
            "async": AsyncJobExecutor(),
            "threadpool": ThreadPoolJobExecutor(),
            "processpool": ProcessPoolJobExecutor(),
        }
        self._worker = Scheduler(
            job_executors=self._job_executors,
            event_broker=self._backend.event_broker.client,
            data_store=self._backend.data_store.client,
            identity=self.name,
            logger=logger,
            cleanup_interval=self.cfg.backend.cleanup_interval,
            max_concurrent_jobs=self.cfg.backend.max_concurrent_jobs,
            default_job_executor=self.cfg.backend.default_job_executor,
        )

    def _setup_backend(self) -> None:
        """
        Set up the data store and SQLAlchemy engine for the scheduler.

        This method initializes the data store and SQLAlchemy engine using configuration
        values. It validates configuration, handles errors, and logs the setup process.

        Raises:
            RuntimeError: If the data store setup fails due to misconfiguration or connection errors.
        """
        if isinstance(self._backend, dict):
            if "data_store" in self._backend:
                data_store = APSDataStore(**self._backend["data_store"])
            if "event_broker" in self._backend:
                if self._backend["event_broker"].get("from_ds_sqla", False):
                    event_broker = APSEventBroker.from_ds_sqla(
                        sqla_engine=data_store.sqla_engine
                    )
                else:
                    event_broker = APSEventBroker(**self._backend["event_broker"])
            self._backend = APSBackend(data_store=data_store, event_broker=event_broker)
        else:
            data_store = APSDataStore(**self.cfg.backend.data_store.to_dict())

            if self.cfg.backend.event_broker.to_dict().get("from_ds_sqla", False):
                event_broker = APSEventBroker.from_ds_sqla(
                    sqla_engine=data_store.sqla_engine
                )
            else:
                event_broker = APSEventBroker(
                    **{
                        k: v
                        for k, v in self.cfg.backend.event_broker.to_dict().items()
                        if k != "from_ds_sqla"
                    }
                )
            self._backend = APSBackend(data_store=data_store, event_broker=event_broker)

        logger.info(
            f"Data store and event broker set up successfully: data store type"
            f" '{data_store.type}', event broker type '{event_broker.type}'"
        )

    def _get_items(self, as_dict: bool, getter) -> list[Any]:
        """
        Helper to get jobs or schedules as objects or dicts.
        """
        items = getter()
        if as_dict:
            return [item.to_dict() for item in items]
        return items

    def get_schedules(self, as_dict: bool = False) -> list[Any]:
        """
        Get all schedules.

        Args:
            as_dict: Whether to return schedules as dictionaries

        Returns:
            List[Any]: List of schedules
        """
        return self._get_items(as_dict, self._worker.get_schedules)

    def get_jobs(self, as_dict: bool = False) -> list[Any]:
        """
        Get all jobs.

        Args:
            as_dict: Whether to return jobs as dictionaries

        Returns:
            List[Any]: List of jobs
        """
        return self._get_items(as_dict, self._worker.get_jobs)

    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a schedule.

        Args:
            schedule_id: ID of the schedule to remove

        Returns:
            bool: True if the schedule was removed, False otherwise

        Raises:
            RuntimeError: If removal fails
        """
        try:
            self._worker.remove_schedule(schedule_id)
            return True
        except Exception as e:
            logger.exception(f"Failed to remove schedule {schedule_id}: {e}")

    def remove_all_schedules(self) -> None:
        """Remove all schedules."""
        for sched in self._worker.get_schedules():
            self._worker.remove_schedule(sched.id)

    def get_job_result(self, job_id: str) -> Any:
        """
        Get the result of a job.

        Args:
            job_id: ID of the job

        Returns:
            Any: Result of the job
        """
        return self._worker.get_job_result(job_id)

    def show_schedules(self) -> None:
        """Display the schedules in a user-friendly format."""
        display_schedules(self._worker.get_schedules())

    def show_jobs(self) -> None:
        """Display the jobs in a user-friendly format."""
        display_jobs(self._worker.get_jobs())

    def start_worker(self, background: bool = True) -> None:
        """
        Start the worker.

        Args:
            background: Whether to run in background
        """
        if background:
            logger.info("Starting APScheduler worker in background mode.")
            self._worker.start_in_background()
        else:
            logger.info("Starting APScheduler worker in foreground mode.")
            self._worker.run_until_stopped()

    def stop_worker(self) -> None:
        """Stop the worker."""
        logger.info("Stopping APScheduler worker.")
        self._worker.stop()
        self._worker._exit_stack.close()

    def start_worker_pool(
        self, num_workers: int | None = None, background: bool = True
    ) -> None:
        """
        Start a pool of worker processes to handle jobs in parallel.

        APScheduler 4.0 already handles concurrency internally through its executors,
        so this method simply starts a single worker with the appropriate configuration.

        Args:
            num_workers: Number of worker processes (affects executor pool sizes)
            background: Whether to run in background
        """
        import multiprocessing

        # Allow configuration override for pool sizes
        if num_workers is None:
            num_workers = getattr(self.cfg.backend, "num_workers", None)
            if num_workers is None:
                num_workers = multiprocessing.cpu_count()

        # Adjust thread and process pool executor sizes
        if "processpool" in self._job_executors:
            self._job_executors["processpool"].max_workers = num_workers
        if "threadpool" in self._job_executors:
            threadpool_size = getattr(
                self.cfg.backend, "threadpool_size", num_workers * 2
            )
            self._job_executors["threadpool"].max_workers = threadpool_size

        logger.info(
            f"Configured worker pool with {num_workers} workers (threadpool size: {self._job_executors['threadpool'].max_workers})"
        )

        # Start a single worker which will use the configured executors
        self.start_worker(background=background)

    def stop_worker_pool(self) -> None:
        """
        Stop the worker pool.

        Since APScheduler manages concurrency internally, this just stops the worker.
        """
        self.stop_worker()

    def add_job(
        self,
        func: collections.abc.Callable,
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        job_id: str | None = None,
        result_ttl: float | dt.timedelta = 0,
        **job_kwargs,
    ) -> str:
        """
        Add a job for immediate execution.

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            job_id: Optional job ID
            result_expiration_time: How long to keep the result
            **job_kwargs: Additional job parameters

        Returns:
            str: Job ID
        """
        job_executor = job_kwargs.pop("job_executor", "threadpool")

        # Convert result_expiration_time to datetime.timedelta if it's not already
        if isinstance(result_ttl, (int, float)):
            result_ttl = dt.timedelta(seconds=result_ttl)

        job_id = job_id or str(uuid.uuid4())

        job_id = self._worker.add_job(
            func,
            args=args or (),
            kwargs=kwargs or {},
            #id=job_id,
            job_executor=job_executor,
            result_expiration_time=result_ttl,
            **job_kwargs,
        )

        return job_id

    def add_schedule(
        self,
        func: collections.abc.Callable,
        trigger: BaseTrigger,
        schedule_id: str | None = None,
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        **schedule_kwargs,
    ) -> str:
        """
        Schedule a job for repeated execution.

        Args:
            func: Function to execute
            trigger: Trigger defining when to execute the function
            schedule_id: Optional schedule ID
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

        schedule_id = self._worker.add_schedule(
            func,
            trigger=trigger_instance,
            id=schedule_id,
            args=args or (),
            kwargs=kwargs or {},
            job_executor=job_executor,
            **schedule_kwargs,
        )

        return schedule_id
