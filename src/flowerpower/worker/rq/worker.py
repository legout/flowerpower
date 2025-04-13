"""
RQSchedulerBackend implementation for FlowerPower using RQ and rq-scheduler.

This module implements the scheduler backend using RQ (Redis Queue) and rq-scheduler.
"""

import datetime as dt
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union

from loguru import logger
from rq import Queue
from rq_scheduler import Scheduler

from ...cfg import Config
from ...fs import AbstractFileSystem, get_filesystem
from ..base import BaseTrigger, BaseWorker
from .setup import RQBackend
from .trigger import RQTrigger
from .utils import show_jobs, show_schedules


class RQWorker(BaseWorker):
    """
    Implementation of BaseScheduler using RQ and rq-scheduler.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        base_dir: Optional[str] = None,
        backend: Optional[RQBackend] = None,
        storage_options: Optional[Dict[str, Any]] = None,
        fs: AbstractFileSystem | None = None,
        **kwargs,
    ):
        """
        Initialize the RQScheduler backend.

        Args:
            name: Name of the scheduler
            base_dir: Base directory for the FlowerPower project
            data_store: RQDataStore instance (for job results)
            event_broker: RQEventBroker instance (for pub/sub)
            storage_options: Storage options for filesystem access
            fs: Filesystem to use
            queue_name: Name of the RQ queue
            **kwargs: Additional parameters
        """
        self.name = name or "rq_scheduler"
        self._base_dir = base_dir or str(Path.cwd())
        self._storage_options = storage_options or {}
        self._backend = backend

        if fs is None:
            fs = get_filesystem(self._base_dir, **(self._storage_options or {}))
        self._fs = fs

        self._conf_path = "conf"
        self._pipelines_path = "pipelines"

        self._load_config()

        # Set up data store
        if not backend:
            self._setup_backend()

        # Setup Redis connection for RQ
        redis_conn = self._backend.client

        # Setup RQ Queue and Scheduler
        self._queue = Queue(name=self._backend.queue, connection=redis_conn)
        self._scheduler = Scheduler(queue=self._queue, connection=redis_conn)

        # Add pipelines path to sys.path
        sys.path.append(self._pipelines_path)

    def _load_config(self) -> None:
        """Load the configuration."""
        self.cfg = Config.load(base_dir=self._base_dir, fs=self._fs)

    def _setup_backend(self) -> None:
        """
        Set up the data store for the scheduler using config.
        """
        backend_cfg = getattr(self.cfg.project.worker, "backend", None)
        if not backend_cfg:
            logger.error("Backend configuration is missing in project.worker.backend.")
            raise RuntimeError("Backend configuration is missing.")

        try:
            self._backend = RQBackend(
                type=backend_cfg.get("type", "redis"),
                host=backend_cfg.get("host"),
                port=backend_cfg.get("port"),
                database=backend_cfg.get("database"),
                password=backend_cfg.get("password"),
                ssl=backend_cfg.get("ssl", False),
                **backend_cfg.get("kwargs", {}),
            )
            logger.info(
                "RQ Data store setup successful (type=%r, host=%r, port=%r, db=%r)",
                backend_cfg.get("type", "redis"),
                backend_cfg.get("host"),
                backend_cfg.get("port"),
                backend_cfg.get("database"),
            )
        except Exception as exc:
            logger.exception(
                "Failed to set up RQ backend (type=%r, host=%r, port=%r, db=%r): %s",
                backend_cfg.get("type", "redis"),
                backend_cfg.get("host"),
                backend_cfg.get("port"),
                backend_cfg.get("database"),
                exc,
            )
            raise RuntimeError(f"Failed to set up RQ backend: {exc}") from exc

    def add_job(
        self,
        func: Callable,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        result_ttl: Union[float, dt.timedelta] = 0,
        **job_kwargs,
    ) -> str:
        """
        Add a job for immediate execution.

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            id: Optional job ID
            result_ttl: How long to keep the result (seconds or timedelta)
            **job_kwargs: Additional job parameters

        Returns:
            str: Job ID
        """
        job_id = id or str(uuid.uuid4())
        if isinstance(result_ttl, (int, float)):
            result_ttl = dt.timedelta(seconds=result_ttl)
        args = args or ()
        kwargs = kwargs or {}

        job = self._queue.enqueue(
            func,
            args=args,
            kwargs=kwargs,
            job_id=job_id,
            result_ttl=int(result_ttl.total_seconds()) if result_ttl else None,
            **job_kwargs,
        )
        logger.info(f"Enqueued job {job_id} ({func.__name__})")
        return job.id

    def add_schedule(
        self,
        func: Callable,
        trigger: BaseTrigger,
        id: Optional[str] = None,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        **schedule_kwargs,
    ) -> str:
        """
        Schedule a job for repeated execution.

        Args:
            func: Function to execute
            trigger: RQTrigger instance
            id: Optional schedule ID
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            **schedule_kwargs: Additional schedule parameters

        Returns:
            str: Schedule ID
        """
        schedule_id = id or str(uuid.uuid4())
        args = args or ()
        kwargs = kwargs or {}

        # Get trigger parameters
        if isinstance(trigger, RQTrigger):
            trigger_params = trigger.get_trigger_instance(**schedule_kwargs)
        else:
            trigger_params = schedule_kwargs

        # Support cron and interval triggers
        if trigger_params.get("type") == "cron":
            cron = trigger_params.get("crontab")
            job = self._scheduler.cron(
                cron_string=cron,
                func=func,
                args=args,
                kwargs=kwargs,
                id=schedule_id,
                repeat=None,  # Infinite by default
                meta={"cron": cron},
            )
        elif trigger_params.get("type") == "interval":
            interval = trigger_params.get("interval")
            job = self._scheduler.schedule(
                scheduled_time=dt.datetime.utcnow() + dt.timedelta(seconds=interval),
                func=func,
                args=args,
                kwargs=kwargs,
                interval=interval,
                id=schedule_id,
                repeat=None,  # Infinite by default
                meta={"interval": interval},
            )
        else:
            raise ValueError(f"Unsupported trigger type: {trigger_params.get('type')}")

        logger.info(
            f"Scheduled job {schedule_id} ({func.__name__}) with trigger {trigger_params}"
        )
        return job.id

    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a schedule.

        Args:
            schedule_id: ID of the schedule to remove

        Returns:
            bool: True if the schedule was removed, False otherwise
        """
        try:
            self._scheduler.cancel(schedule_id)
            logger.info(f"Removed schedule {schedule_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove schedule {schedule_id}: {e}")
            return False

    def remove_all_schedules(self) -> None:
        """Remove all schedules."""
        for job in self._scheduler.get_jobs():
            self._scheduler.cancel(job.id)
        logger.info("Removed all schedules.")

    def get_job_result(self, job_id: str) -> Any:
        """
        Get the result of a job.

        Args:
            job_id: ID of the job

        Returns:
            Any: Result of the job
        """
        return self._backend.get_job_result(job_id)

    def get_schedules(self, as_dict: bool = False) -> list:
        """
        Get all schedules.

        Args:
            as_dict: Whether to return schedules as dictionaries

        Returns:
            List: List of scheduled jobs
        """
        jobs = self._scheduler.get_jobs()
        if as_dict:
            return [
                job.to_dict() if hasattr(job, "to_dict") else job.__dict__
                for job in jobs
            ]
        return jobs

    def get_jobs(self, as_dict: bool = False) -> list:
        """
        Get all jobs in the queue.

        Args:
            as_dict: Whether to return jobs as dictionaries

        Returns:
            List: List of jobs
        """
        jobs = self._queue.get_jobs()
        if as_dict:
            return [
                job.to_dict() if hasattr(job, "to_dict") else job.__dict__
                for job in jobs
            ]
        return jobs

    def show_schedules(self) -> None:
        """Display the schedules in a user-friendly format."""
        show_schedules(self._scheduler)

    def show_jobs(self) -> None:
        """Display the jobs in a user-friendly format."""
        show_jobs(self._queue)
