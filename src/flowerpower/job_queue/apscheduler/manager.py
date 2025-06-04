"""
APScheduler implementation for FlowerPower scheduler.

This module implements the scheduler interfaces using APScheduler as the backend.
"""

import datetime as dt
import importlib.util
from typing import Any, Callable
from uuid import UUID

import duration_parser
from apscheduler import Job, Scheduler
from apscheduler.executors.async_ import AsyncJobExecutor
from apscheduler.executors.subprocess import ProcessPoolJobExecutor
from apscheduler.executors.thread import ThreadPoolJobExecutor
from fsspec.spec import AbstractFileSystem
from loguru import logger

from ...utils.logging import setup_logging
from ..base import BaseJobQueueManager
from .setup import APSBackend, APSDataStore, APSEventBroker
from .trigger import APSTrigger
from .utils import display_jobs, display_schedules

# Check if APScheduler is available
# if not importlib.util.find_spec("apscheduler"):
#    raise ImportError(
#        "APScheduler is not installed. Please install it using `pip install "
#        "'apscheduler>4.0.0a1'`, 'conda install apscheduler4' or `pip install flowerpower[apscheduler]`"
#    )


setup_logging()

# Patch pickle if needed
try:
    from ...utils.monkey import patch_pickle

    patch_pickle()
except Exception as e:
    logger.warning(f"Failed to patch pickle: {e}")


class APSManager(BaseJobQueueManager):
    """Implementation of BaseScheduler using APScheduler.

    This worker class uses APScheduler 4.0+ as the backend to schedule and manage jobs.
    It supports different job executors including async, thread pool, and process pool.

    Typical usage:
        ```python
        worker = APSManager(name="my_scheduler")
        worker.start_worker(background=True)

        # Add a job
        def my_job(x: int) -> int:
            return x * 2

        job_id = worker.add_job(my_job, func_args=(10,))
        ```
    """

    def __init__(
        self,
        name: str | None = "flowerpower_apscheduler",
        base_dir: str | None = None,
        backend: APSBackend | dict | None = None,
        storage_options: dict[str, Any] = None,
        fs: AbstractFileSystem | None = None,
        log_level: str | None = None,
    ):
        """Initialize the APScheduler backend.

        Args:
            name: Name of the scheduler instance. Used for identification in logs and data stores.
            base_dir: Base directory for the FlowerPower project. Used for finding configuration files.
            backend: APSBackend instance with data store and event broker configurations,
                or a dictionary with configuration parameters.
            storage_options: Options for configuring file system storage access.
                Example: {"mode": "async", "root": "/tmp"}
            fs: Custom filesystem implementation for storage operations.
            log_level: Logging level to use for this worker instance.
                Example: "DEBUG", "INFO", "WARNING", etc.

        Raises:
            RuntimeError: If backend setup fails due to missing or invalid configurations.
            ImportError: If required dependencies are not installed.

        Example:
            ```python
            # Basic initialization
            worker = APSManager(name="my_scheduler")

            # With custom backend and logging

            # Create a custom backend configuration using dictionaries for data store and event broker
            backend_config = {
                "data_store": {"type": "postgresql", "uri": "postgresql+asyncpg://user:pass@localhost/db"},
                "event_broker": {"type": "redis", "uri": "redis://localhost:6379/0"}
            }

            # Create a custom backend configuration using APSBackend, APSDataStore, and APSEventBroker classes
            from flowerpower.worker.aps import APSBackend, APSDataStore, APSEventBroker
            data_store = APSDataStore(
                type="postgresql",
                uri="postgresql+asyncpg://user:pass@localhost/db"
            )
            event_broker = APSEventBroker(
                from_ds_sqla=True
            )
            backend_config = APSBackend(
                data_store=data_store,
                event_broker=event_broker
            )

            worker = APSManager(
                name="custom_scheduler",
                backend=backend_config,
                log_level="DEBUG"
            )
            ```
        """
        if log_level:
            setup_logging(level=log_level)

        super().__init__(
            type="apscheduler",
            name=name,
            base_dir=base_dir,
            fs=fs,
            backend=backend,
            storage_options=storage_options,
        )

        if not isinstance(backend, APSBackend):
            self._setup_backend(backend)
        else:
            self._backend = backend

        # Set up job executors
        self._job_executors = {
            "async": AsyncJobExecutor(),
            "threadpool": ThreadPoolJobExecutor(),
            "processpool": ProcessPoolJobExecutor(),
        }
        self._worker = Scheduler(
            job_executors=self._job_executors,
            event_broker=self._backend.event_broker._client,
            data_store=self._backend.data_store._client,
            identity=self.name,
            logger=logger,
            cleanup_interval=self._backend.cleanup_interval,
            max_concurrent_jobs=self._backend.max_concurrent_jobs,
            default_job_executor=self._backend.default_job_executor,
        )

    def _setup_backend(self, backend: dict | None) -> None:
        """
        Set up the data store and SQLAlchemy engine for the scheduler.

        This method initializes the data store and SQLAlchemy engine using configuration
        values. It validates configuration, handles errors, and logs the setup process.

        Raises:
            RuntimeError: If the data store setup fails due to misconfiguration or connection errors.
        """
        if backend is None:
            self._backend = APSBackend(**self.cfg.backend.to_dict())
        elif isinstance(backend, dict):
            backend_cfg = self.cfg.backend.to_dict()
            backend_cfg.update(backend)
            self._backend = APSBackend(**backend_cfg)

        if (
            self._backend.data_store._client is not None
            and self._backend.event_broker._client is not None
        ):
            logger.info(
                f"Data store and event broker set up successfully: data store type"
                f" '{self._backend.data_store.type}', event broker type '{self._backend.event_broker.type}'"
            )

    def start_worker(
        self, background: bool = False, num_workers: int | None = None
    ) -> None:
        """Start the APScheduler worker process.

        This method initializes and starts the worker process that executes scheduled jobs.
        The worker can be started in foreground (blocking) or background mode.

        Args:
            background: If True, runs the worker in a non-blocking background mode.
                If False, runs in the current process and blocks until stopped.
            num_workers: Number of worker processes for the executor pools.
                If None, uses the value from config or defaults to CPU count.

        Raises:
            RuntimeError: If worker fails to start or if multiprocessing setup fails.

        Example:
            ```python
            # Start worker in background with 4 processes
            worker.start_worker(background=True, num_workers=4)

            # Start worker in foreground (blocking)
            worker.start_worker(background=False)

            # Use as a context manager
            with worker.start_worker(background=False):
                # Do some work
                pass
            ```
        """
        import multiprocessing

        # Allow configuration override for pool sizes
        if num_workers is None:
            num_workers = self.cfg.num_workers or multiprocessing.cpu_count()

        # Adjust thread and process pool executor sizes
        if "processpool" in self._job_executors:
            self._job_executors["processpool"].max_workers = num_workers
        if "threadpool" in self._job_executors:
            threadpool_size = getattr(
                self.cfg.backend, "threadpool_size", num_workers * 5
            )
            self._job_executors["threadpool"].max_workers = threadpool_size

        logger.info(f"Configured worker pool with {num_workers} workers.")

        if background:
            logger.info("Starting APScheduler worker in background mode.")
            self._worker.start_in_background()
        else:
            logger.info("Starting APScheduler worker in foreground mode.")
            self._worker.run_until_stopped()

    def stop_worker(self) -> None:
        """Stop the APScheduler worker process.

        This method stops the worker process and cleans up resources.
        It should be called before program exit to ensure proper cleanup.

        Raises:
            RuntimeError: If worker fails to stop cleanly.

        Example:
            ```python
            try:
                worker.start_worker(background=True)
                # ... do work ...
            finally:
                worker.stop_worker()
            ```
        """
        logger.info("Stopping APScheduler worker.")
        self._worker.stop()
        self._worker._exit_stack.close()

    def start_worker_pool(
        self,
        background: bool = False,
        num_workers: int | None = None,
    ) -> None:
        """
        Start a pool of worker processes to handle jobs in parallel.

        APScheduler 4.0 already handles concurrency internally through its executors,
        so this method simply starts a single worker with the appropriate configuration.

        Args:
            num_workers: Number of worker processes (affects executor pool sizes)
            background: Whether to run in background
        """

        # Start a single worker which will use the configured executors
        self.start_worker(background=background, num_workers=num_workers)

    def stop_worker_pool(self) -> None:
        """
        Stop the worker pool.

        Since APScheduler manages concurrency internally, this just stops the worker.
        """

        logger.info("Stopping APScheduler worker pool.")
        self.stop_worker()

    ## Jobs

    def add_job(
        self,
        func: Callable,
        func_args: tuple | None = None,
        func_kwargs: dict[str, Any] | None = None,
        result_ttl: float | dt.timedelta = 0,
        run_at: dt.datetime | None = None,
        run_in: int | float | None = None,
        job_executor: str | None = None,
    ) -> str:
        """Add a job for immediate or scheduled execution.

        This method adds a job to the scheduler. The job can be executed immediately
        or scheduled for later execution using run_at or run_in parameters.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            result_ttl: Time to live for the job result, as seconds or timedelta.
                After this time, the result may be removed from storage.
            run_at: Schedule the job to run at a specific datetime.
                Takes precedence over run_in if both are specified.
            run_in: Schedule the job to run after a delay (in seconds).
                Only used if run_at is not specified.
            job_executor: Name of the executor to run the job ("async", "threadpool",
                or "processpool"). If None, uses the default from config.

        Returns:
            str: Unique identifier for the job.

        Raises:
            ValueError: If the function is not serializable or arguments are invalid.
            RuntimeError: If the job cannot be added to the scheduler.

        Note:
            When using run_at or run_in, the job results will not be stored in the data store.

        Example:
            ```python
            # Add immediate job
            def my_task(x: int, y: int) -> int:
                return x + y

            job_id = worker.add_job(
                my_task,
                func_args=(1, 2),
                result_ttl=3600  # Keep result for 1 hour
            )

            # Schedule job for later
            tomorrow = dt.datetime.now() + dt.timedelta(days=1)
            job_id = worker.add_job(
                my_task,
                func_kwargs={"x": 1, "y": 2},
                run_at=tomorrow
            )

            # Run after delay
            job_id = worker.add_job(
                my_task,
                func_args=(1, 2),
                run_in=3600  # Run in 1 hour
            )
            ```
        """
        job_executor = job_executor or self.cfg.backend.default_job_executor

        # Convert result_expiration_time to datetime.timedelta if it's not already
        if isinstance(result_ttl, (int, float)):
            result_ttl = dt.timedelta(seconds=result_ttl)

        run_at = (
            dt.datetime.fromisoformat(run_at) if isinstance(run_at, str) else run_at
        )
        run_in = duration_parser.parse(run_in) if isinstance(run_in, str) else run_in

        if run_in:
            run_at = dt.datetime.now() + dt.timedelta(seconds=run_in)

        if run_at:
            job_id = self.add_schedule(
                func,
                func_args=func_args,
                func_kwargs=func_kwargs,
                date=run_at,
                job_executor=job_executor,
            )
        else:
            job_id = self._worker.add_job(
                func,
                args=func_args or (),
                kwargs=func_kwargs or {},
                job_executor=job_executor,
                result_expiration_time=result_ttl,
            )

        return str(job_id)

    def run_job(
        self,
        func: Callable,
        func_args: tuple | None = None,
        func_kwargs: dict[str, Any] | None = None,
        job_executor: str | None = None,
    ) -> Any:
        """Run a job immediately and wait for its result.

        This method executes the job synchronously and returns its result.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            job_executor: Name of the executor to run the job ("async", "threadpool",
                or "processpool"). If None, uses the default from config.

        Returns:
            Any: The result returned by the executed function.

        Raises:
            Exception: Any exception raised by the executed function.

        Example:
            ```python
            def add(x: int, y: int) -> int:
                return x + y

            result = worker.run_job(add, func_args=(1, 2))
            assert result == 3
            ```
        """
        job_executor = job_executor or self.cfg.backend.default_job_executor

        return self._worker.run_job(
            func,
            args=func_args or (),
            kwargs=func_kwargs or {},
        )

    def get_jobs(self) -> list[Job]:
        """Get all jobs from the scheduler.

        Returns:
            list[Job]: List of all jobs in the scheduler, including pending,
                running, and completed jobs.

        Example:
            ```python
            jobs = worker.get_jobs()
            for job in jobs:
                print(f"Job {job.id}: {job.status}")
            ```
        """
        return self._worker.get_jobs()

    def get_job(self, job_id: str | UUID) -> Job | None:
        """Get a specific job by its ID.

        Args:
            job_id: Unique identifier of the job, as string or UUID.

        Returns:
            Job | None: The job object if found, None otherwise.

        Example:
            ```python
            # Get job using string ID
            job = worker.get_job("550e8400-e29b-41d4-a716-446655440000")

            # Get job using UUID
            from uuid import UUID
            job = worker.get_job(UUID("550e8400-e29b-41d4-a716-446655440000"))
            ```
        """
        jobs = self._worker.get_jobs()
        if isinstance(job_id, str):
            job_id = UUID(job_id)

        for job in jobs:
            if job.id == job_id:
                return job
        return None

    def get_job_result(self, job_id: str | UUID, wait: bool = True) -> Any:
        """Get the result of a specific job.

        Args:
            job_id: Unique identifier of the job, as string or UUID.
            wait: If True, waits for the job to complete before returning.
                If False, returns None if the job is not finished.

        Returns:
            Any: The result of the job if available, None if the job is not
                finished and wait=False.

        Raises:
            ValueError: If the job ID is invalid.
            TimeoutError: If the job takes too long to complete (when waiting).

        Example:
            ```python
            # Wait for result
            result = worker.get_job_result("550e8400-e29b-41d4-a716-446655440000")

            # Check result without waiting
            result = worker.get_job_result(
                "550e8400-e29b-41d4-a716-446655440000",
                wait=False
            )
            if result is None:
                print("Job still running")
            ```
        """
        if isinstance(job_id, str):
            job_id = UUID(job_id)
        return self._worker.get_job_result(job_id, wait=wait)

    def cancel_job(self, job_id: str | UUID) -> bool:
        """Cancel a running or pending job.

        Note:
            Not currently implemented for APScheduler backend. Jobs must be removed
            manually from the data store.

        Args:
            job_id: Unique identifier of the job to cancel, as string or UUID.

        Returns:
            bool: Always returns False as this operation is not implemented.

        Example:
            ```python
            # This operation is not supported
            success = worker.cancel_job("job-123")
            assert not success
            ```
        """
        logger.info(
            "Not implemented for apscheduler yet. You have to remove the job manually from the data_store."
        )
        return False

    def delete_job(self, job_id: str | UUID) -> bool:
        """
        Delete a job and its results from storage.

        Note:
            Not currently implemented for APScheduler backend. Jobs must be removed
            manually from the data store.

        Args:
            job_id: Unique identifier of the job to delete, as string or UUID.

        Returns:
            bool: Always returns False as this operation is not implemented.

        Example:
            ```python
            # This operation is not supported
            success = worker.delete_job("job-123")
            assert not success
            ```
        """
        logger.info(
            "Not implemented for apscheduler yet. You have to remove the job manually from the data_store."
        )
        return False

    def cancel_all_jobs(self) -> None:
        """Cancel all running and pending jobs.

        Note:
            Not currently implemented for APScheduler backend. Jobs must be removed
            manually from the data store.

        Example:
            ```python
            # This operation is not supported
            worker.cancel_all_jobs()  # No effect
            ```
        """
        logger.info(
            "Not implemented for apscheduler yet. You have to remove the jobs manually from the data_store."
        )
        return None

    def delete_all_jobs(self) -> None:
        """
        Delete all jobs and their results from storage.

        Note:
            Not currently implemented for APScheduler backend. Jobs must be removed
            manually from the data store.

        Example:
            ```python
            # This operation is not supported
            worker.delete_all_jobs()  # No effect
            ```
        """
        logger.info(
            "Not implemented for apscheduler yet. You have to remove the jobs manually from the data_store."
        )
        return None

    @property
    def jobs(self) -> list[Job]:
        """Get all jobs from the scheduler.

        Returns:
            list[Job]: List of all job objects in the scheduler.

        Example:
            ```python
            all_jobs = worker.jobs
            print(f"Total jobs: {len(all_jobs)}")
            for job in all_jobs:
                print(f"Job {job.id}: {job.status}")
            ```
        """
        return self._worker.get_jobs()

    @property
    def job_ids(self) -> list[str]:
        """Get all job IDs from the scheduler.

        Returns:
            list[str]: List of unique identifiers for all jobs.

        Example:
            ```python
            ids = worker.job_ids
            print(f"Job IDs: {', '.join(ids)}")
            ```
        """
        return [str(job.id) for job in self._worker.get_jobs()]

    ## Schedules
    def add_schedule(
        self,
        func: Callable,
        func_args: tuple | None = None,
        func_kwargs: dict[str, Any] | None = None,
        cron: str | dict[str, str | int] | None = None,
        interval: int | str | dict[str, str | int] | None = None,
        date: dt.datetime | None = None,
        schedule_id: str | None = None,
        job_executor: str | None = None,
        **schedule_kwargs,
    ) -> str:
        """Schedule a job for repeated or one-time execution.

        This method adds a scheduled job to the scheduler. The schedule can be defined
        using cron expressions, intervals, or specific dates.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            cron: Cron expression for scheduling. Can be a string (e.g. "* * * * *")
                or a dict with cron parameters. Only one of cron, interval, or date
                should be specified.
            interval: Interval for recurring execution in seconds, or a dict with
                interval parameters. Only one of cron, interval, or date should
                be specified.
            date: Specific datetime for one-time execution. Only one of cron,
                interval, or date should be specified.
            schedule_id: Optional unique identifier for the schedule.
                If None, a UUID will be generated.
            job_executor: Name of the executor to run the job ("async", "threadpool",
                or "processpool"). If None, uses the default from config.
            **schedule_kwargs: Additional scheduling parameters:
                - coalesce: CoalescePolicy = CoalescePolicy.latest
                - misfire_grace_time: float | timedelta | None = None
                - max_jitter: float | timedelta | None = None
                - max_running_jobs: int | None = None
                - conflict_policy: ConflictPolicy = ConflictPolicy.do_nothing
                - paused: bool = False

        Returns:
            str: Unique identifier for the schedule.

        Raises:
            ValueError: If no trigger type is specified or if multiple triggers
                are specified.
            RuntimeError: If the schedule cannot be added to the scheduler.

        Example:
            ```python
            def my_task(msg: str) -> None:
                print(f"Running task: {msg}")

            # Using cron expression (run every minute)
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Cron job"},
                cron="* * * * *"
            )

            # Using cron dict
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Cron job"},
                cron={
                    "minute": "*/15",  # Every 15 minutes
                    "hour": "9-17"     # During business hours
                }
            )

            # Using interval (every 5 minutes)
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Interval job"},
                interval=300  # 5 minutes in seconds
            )

            # Using interval dict
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Interval job"},
                interval={
                    "hours": 1,
                    "minutes": 30
                }
            )

            # One-time future execution
            import datetime as dt
            future_date = dt.datetime.now() + dt.timedelta(days=1)
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "One-time job"},
                date=future_date
            )

            # With additional options
            from apscheduler import CoalescePolicy
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Advanced job"},
                interval=300,
                coalesce=CoalescePolicy.latest,
                max_jitter=dt.timedelta(seconds=30)
            )
            ```
        """
        job_executor = job_executor or self.cfg.backend.default_job_executor

        if cron:
            trigger_instance = APSTrigger("cron")
            if isinstance(cron, str):
                cron = {"crontab": cron}
            trigger = trigger_instance.get_trigger_instance(**cron)
        elif interval:
            trigger_instance = APSTrigger("interval")
            if isinstance(interval, str | int):
                interval = {"seconds": int(interval)}
            trigger = trigger_instance.get_trigger_instance(**interval)

        if date:
            trigger_instance = APSTrigger("date")
            trigger = trigger_instance.get_trigger_instance(run_time=date)

        schedule_id = self._worker.add_schedule(
            func,
            trigger=trigger,
            id=schedule_id,
            args=func_args or (),
            kwargs=func_kwargs or {},
            job_executor=job_executor,
            **schedule_kwargs,
        )

        return schedule_id

    def get_schedules(self, as_dict: bool = False) -> list[Any]:
        """Get all schedules from the scheduler.

        Args:
            as_dict: If True, returns schedules as dictionaries instead of
                Schedule objects.

        Returns:
            list[Any]: List of all schedules, either as Schedule objects or
                dictionaries depending on as_dict parameter.

        Example:
            ```python
            # Get schedule objects
            schedules = worker.get_schedules()
            for schedule in schedules:
                print(f"Schedule {schedule.id}: Next run at {schedule.next_run_time}")

            # Get as dictionaries
            schedules = worker.get_schedules(as_dict=True)
            for schedule in schedules:
                print(f"Schedule {schedule['id']}: {schedule['trigger']}")
            ```
        """
        return self._worker.get_schedules()

    def get_schedule(self, schedule_id: str) -> Any:
        """Get a specific schedule by its ID.

        Args:
            schedule_id: Unique identifier of the schedule.

        Returns:
            Any: The schedule object if found, None otherwise.

        Example:
            ```python
            schedule = worker.get_schedule("my-daily-job")
            if schedule:
                print(f"Next run at: {schedule.next_run_time}")
            else:
                print("Schedule not found")
            ```
        """
        if schedule_id in self.schedule_ids:
            return self._worker.get_schedule(schedule_id)

        logger.error(f"Schedule {schedule_id} not found.")
        return None

    def cancel_schedule(self, schedule_id: str) -> bool:
        """Cancel a schedule.

        This method removes the schedule from the scheduler. This is equivalent
        to delete_schedule and stops any future executions of the schedule.

        Args:
            schedule_id: Unique identifier of the schedule to cancel.

        Returns:
            bool: True if the schedule was successfully canceled,
                False if the schedule was not found.

        Example:
            ```python
            if worker.cancel_schedule("my-daily-job"):
                print("Schedule canceled successfully")
            else:
                print("Schedule not found")
            ```
        """
        if schedule_id not in self.schedule_ids:
            logger.error(f"Schedule {schedule_id} not found.")
            return False
        self._worker.remove_schedule(schedule_id)
        logger.info(f"Schedule {schedule_id} canceled.")

    def delete_schedule(self, schedule_id: str) -> bool:
        """Remove a schedule.

        This method removes the schedule from the scheduler. This is equivalent
        to cancel_schedule and stops any future executions of the schedule.

        Args:
            schedule_id: Unique identifier of the schedule to remove.

        Returns:
            bool: True if the schedule was successfully removed,
                False if the schedule was not found.

        Raises:
            RuntimeError: If removal fails due to data store errors.

        Example:
            ```python
            try:
                if worker.delete_schedule("my-daily-job"):
                    print("Schedule deleted successfully")
                else:
                    print("Schedule not found")
            except RuntimeError as e:
                print(f"Failed to delete schedule: {e}")
            ```
        """
        self.cancel_schedule(schedule_id)

    def cancel_all_schedules(self) -> None:
        """Cancel all schedules in the scheduler.

        This method removes all schedules from the scheduler, stopping all future
        executions. This operation cannot be undone.

        Example:
            ```python
            # Cancel all schedules
            worker.cancel_all_schedules()
            assert len(worker.schedules) == 0
            ```
        """
        for sched in self.schedule_ids:
            self.cancel_schedule(sched)
        logger.info("All schedules canceled.")
        return None

    def delete_all_schedules(self) -> None:
        """
        Delete all schedules from the scheduler.

        This method removes all schedules from the scheduler, stopping all future
        executions. This operation cannot be undone.

        Example:
            ```python
            # Delete all schedules
            worker.delete_all_schedules()
            assert len(worker.schedules) == 0
            ```
        """
        for sched in self.schedule_ids:
            self.delete_schedule(sched)
        logger.info("All schedules deleted.")
        return None

    @property
    def schedules(self) -> list[Any]:
        """Get all schedules from the scheduler.

        Returns:
            list[Any]: List of all schedule objects in the scheduler.

        Example:
            ```python
            schedules = worker.schedules
            print(f"Total schedules: {len(schedules)}")
            ```
        """
        return self._worker.get_schedules()

    @property
    def schedule_ids(self) -> list[str]:
        """Get all schedule IDs from the scheduler.

        Returns:
            list[str]: List of unique identifiers for all schedules.

        Example:
            ```python
            ids = worker.schedule_ids
            print(f"Schedule IDs: {', '.join(ids)}")
            ```
        """
        return [str(sched.id) for sched in self._worker.get_schedules()]

    def pause_schedule(self, schedule_id: str) -> bool:
        """Pause a schedule temporarily.

        This method pauses the schedule without removing it. The schedule can be
        resumed later using resume_schedule.

        Args:
            schedule_id: Unique identifier of the schedule to pause.

        Returns:
            bool: True if the schedule was successfully paused,
                False if the schedule was not found.

        Example:
            ```python
            # Pause a schedule temporarily
            if worker.pause_schedule("daily-backup"):
                print("Schedule paused")
            ```
        """
        if schedule_id not in self.schedule_ids:
            logger.error(f"Schedule {schedule_id} not found.")
            return False
        self._worker.pause_schedule(schedule_id)
        logger.info(f"Schedule {schedule_id} paused.")
        return True

    def resume_schedule(self, schedule_id: str) -> bool:
        """Resume a paused schedule.

        Args:
            schedule_id: Unique identifier of the schedule to resume.

        Returns:
            bool: True if the schedule was successfully resumed,
                False if the schedule was not found.

        Example:
            ```python
            # Resume a paused schedule
            if worker.resume_schedule("daily-backup"):
                print("Schedule resumed")
            ```
        """
        if schedule_id not in self.schedule_ids:
            logger.error(f"Schedule {schedule_id} not found.")
            return False
        self._worker.unpause_schedule(schedule_id)
        logger.info(f"Schedule {schedule_id} resumed.")
        return True

    def pause_all_schedules(self) -> None:
        """Pause all schedules in the scheduler.

        This method pauses all schedules without removing them. They can be
        resumed using resume_all_schedules.

        Example:
            ```python
            # Pause all schedules temporarily
            worker.pause_all_schedules()
            ```
        """
        for sched in self.schedule_ids:
            self.pause_schedule(sched)
        logger.info("All schedules paused.")
        return None

    def resume_all_schedules(self) -> None:
        """Resume all paused schedules.

        This method resumes all paused schedules in the scheduler.

        Example:
            ```python
            # Resume all paused schedules
            worker.resume_all_schedules()
            ```
        """
        for sched in self.schedule_ids:
            self.resume_schedule(sched)
        logger.info("All schedules resumed.")
        return None

    def show_schedules(self) -> None:
        """Display all schedules in a user-friendly format.

        This method prints a formatted view of all schedules including their
        status, next run time, and other relevant information.

        Example:
            ```python
            # Show all schedules in a readable format
            worker.show_schedules()
            ```
        """
        display_schedules(self._worker.get_schedules())

    def show_jobs(self) -> None:
        """Display all jobs in a user-friendly format.

        This method prints a formatted view of all jobs including their
        status, result, and other relevant information.

        Example:
            ```python
            # Show all jobs in a readable format
            worker.show_jobs()
            ```
        """
        display_jobs(self._worker.get_jobs())
