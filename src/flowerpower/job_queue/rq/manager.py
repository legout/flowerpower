"""
RQSchedulerBackend implementation for FlowerPower using RQ and rq-scheduler.

This module implements the scheduler backend using RQ (Redis Queue) and rq-scheduler.
"""

import datetime as dt
import multiprocessing
import platform
import sys
import time
import uuid
from typing import Any, Callable

import duration_parser
from cron_descriptor import get_description
from humanize import precisedelta
from loguru import logger
from rq import Queue, Repeat, Retry
from rq.job import Callback, Job
from rq.results import Result
from rq.worker import Worker
from rq.worker_pool import WorkerPool
from rq_scheduler import Scheduler

from ...fs import AbstractFileSystem
from ...utils.logging import setup_logging
from ..base import BaseJobQueueManager
from .setup import RQBackend

setup_logging()

if sys.platform == "darwin" and platform.machine() == "arm64":
    try:
        # Check if the start method has already been set to avoid errors
        if multiprocessing.get_start_method(allow_none=True) is None:
            multiprocessing.set_start_method("fork")
            logger.debug("Set multiprocessing start method to 'fork' for macOS ARM.")
        elif multiprocessing.get_start_method() != "fork":
            logger.warning(
                f"Multiprocessing start method already set to '{multiprocessing.get_start_method()}'. "
                f"Cannot set to 'fork'. This might cause issues on macOS ARM."
            )
    except RuntimeError as e:
        # Handle cases where the context might already be started
        logger.warning(f"Could not set multiprocessing start method to 'fork': {e}")


class RQManager(BaseJobQueueManager):
    """Implementation of BaseScheduler using Redis Queue (RQ) and rq-scheduler.

    This worker class uses RQ and rq-scheduler as the backend to manage jobs and schedules.
    It supports multiple queues, background workers, and job scheduling capabilities.

    Typical usage:
        ```python
        worker = RQManager(name="my_rq_worker")
        worker.start_worker(background=True)

        # Add a job
        def my_job(x: int) -> int:
            return x * 2

        job_id = worker.add_job(my_job, func_args=(10,))
        ```
    """

    def __init__(
        self,
        name: str = "rq_scheduler",
        base_dir: str | None = None,
        backend: RQBackend | None = None,
        storage_options: dict[str, Any] | None = None,
        fs: AbstractFileSystem | None = None,
        log_level: str | None = None,
    ):
        """Initialize the RQ scheduler backend.

        Args:
            name: Name of the scheduler instance. Used for identification in logs
                and queue names.
            base_dir: Base directory for the FlowerPower project. Used for finding
                configuration files.
            backend: RQBackend instance for Redis connection configuration.
                If None, configuration is loaded from project settings.
            storage_options: Options for configuring file system storage access.
                Example: {"mode": "async", "root": "/tmp"}
            fs: Custom filesystem implementation for storage operations.
            log_level: Logging level to use for this worker instance.
                Example: "DEBUG", "INFO", "WARNING", etc.

        Raises:
            RuntimeError: If backend setup fails due to Redis connection issues
                or missing configurations.
            ImportError: If required dependencies are not installed.

        Example:
            ```python
            # Basic initialization
            worker = RQManager(name="my_worker")

            # With custom backend and logging
            backend = RQBackend(
                uri="redis://localhost:6379/0",
                queues=["high", "default", "low"]
            )
            worker = RQManager(
                name="custom_worker",
                backend=backend,
                log_level="DEBUG"
            )
            ```
        """
        if log_level:
            setup_logging(level=log_level)
        self._log_level = log_level or "INFO"

        super().__init__(
            type="rq",
            name=name,
            base_dir=base_dir,
            backend=backend,
            fs=fs,
            storage_options=storage_options,
        )

        if self._backend is None:
            self._setup_backend()

        redis_conn = self._backend.client
        self._queues = {}

        self._queue_names = self._backend.queues  # [:-1]
        for queue_name in self._queue_names:
            queue = Queue(name=queue_name, connection=redis_conn)
            self._queues[queue_name] = queue
            self._queues[queue_name].log = logger
            logger.debug(f"Created queue and scheduler for '{queue_name}'")

        self._scheduler_name = self._backend.queues[-1]
        self._scheduler = Scheduler(
            connection=redis_conn, queue_name=self._backend.queues[-1], interval=60
        )
        self._scheduler.log = logger

    def _setup_backend(self) -> None:
        """Set up the Redis backend for the scheduler.

        This internal method initializes the Redis connection and queues based on
        project configuration. It validates configuration, handles errors, and logs
        the setup process.

        Raises:
            RuntimeError: If Redis connection fails or configuration is invalid.
        """
        backend_cfg = getattr(self.cfg, "backend", None)
        if not backend_cfg:
            logger.error(
                "Backend configuration is missing in project.worker.rq_backend.backend."
            )
            raise RuntimeError("Backend configuration is missing.")
        try:
            self._backend = RQBackend(**backend_cfg.to_dict())
            logger.info(
                f"RQ backend setup successful (type: {self._backend.type}, uri: {self._backend.uri})"
            )
        except Exception as exc:
            logger.exception(
                f"Failed to set up RQ backend (type: {getattr(self._backend, 'type', None)}, uri: {getattr(self._backend, 'uri', None)}): {exc}"
            )
            raise RuntimeError(f"Failed to set up RQ backend: {exc}") from exc

    def start_worker(
        self,
        background: bool = False,
        queue_names: list[str] | None = None,
        with_scheduler: bool = True,
        **kwargs: Any,
    ) -> None:
        """Start a worker process for processing jobs from the queues.

        Args:
            background: If True, runs the worker in a non-blocking background mode.
                If False, runs in the current process and blocks until stopped.
            queue_names: List of queue names to process. If None, processes all
                queues defined in the backend configuration.
            with_scheduler: Whether to include the scheduler queue for processing
                scheduled jobs.
            **kwargs: Additional arguments passed to RQ's Worker class.
                Example: {"burst": True, "logging_level": "INFO", "job_monitoring_interval": 30}

        Raises:
            RuntimeError: If worker fails to start or if Redis connection fails.

        Example:
            ```python
            # Start worker in background processing all queues
            worker.start_worker(background=True)

            # Start worker for specific queues
            worker.start_worker(
                background=True,
                queue_names=["high", "default"],
                with_scheduler=False
            )

            # Start worker with custom settings
            worker.start_worker(
                background=True,
                max_jobs=100,
                job_monitoring_interval=30
            )
            ```
        """
        import multiprocessing

        logging_level = kwargs.pop("logging_level", self._log_level)
        burst = kwargs.pop("burst", False)
        max_jobs = kwargs.pop("max_jobs", None)
        # Determine which queues to process
        if queue_names is None:
            # Use all queues by default
            queue_names = self._queue_names
            queue_names_str = ", ".join(queue_names)
        else:
            # Filter to only include valid queue names
            queue_names = [name for name in queue_names if name in self._queue_names]
            queue_names_str = ", ".join(queue_names)

        if not queue_names:
            logger.error("No valid queues specified, cannot start worker")
            return

        if with_scheduler:
            # Add the scheduler queue to the list of queues
            queue_names.append(self._scheduler_name)
            queue_names_str = ", ".join(queue_names)

        # Create a worker instance with queue names (not queue objects)
        worker = Worker(queue_names, connection=self._backend.client, **kwargs)

        if background:
            # We need to use a separate process rather than a thread because
            # RQ's signal handler registration only works in the main thread
            def run_worker_process(queue_names_arg):
                # Import RQ inside the process to avoid connection sharing issues
                from redis import Redis
                from rq import Worker

                # Create a fresh Redis connection in this process
                redis_conn = Redis.from_url(self._backend.uri)

                # Create a worker instance with queue names
                worker_proc = Worker(queue_names_arg, connection=redis_conn)

                # Disable the default signal handlers in RQ worker by patching
                # the _install_signal_handlers method to do nothing
                worker_proc._install_signal_handlers = lambda: None

                # Work until terminated
                worker_proc.work(
                    with_scheduler=True,
                    logging_level=logging_level,
                    burst=burst,
                    max_jobs=max_jobs,
                )

            # Create and start the process
            process = multiprocessing.Process(
                target=run_worker_process,
                args=(queue_names,),
                name=f"rq-worker-{self.name}",
            )
            # Don't use daemon=True to avoid the "daemonic processes are not allowed to have children" error
            process.start()
            self._worker_process = process
            logger.info(
                f"Started RQ worker in background process (PID: {process.pid}) for queues: {queue_names_str}"
            )
        else:
            # Start worker in the current process (blocking)
            logger.info(
                f"Starting RQ worker in current process (blocking) for queues: {queue_names_str}"
            )
            worker.work(
                with_scheduler=True,
                logging_level=logging_level,
                burst=burst,
                max_jobs=max_jobs,
            )

    def stop_worker(self) -> None:
        """Stop the worker process.

        This method stops the worker process if running in background mode and
        performs cleanup. It should be called before program exit.

        Example:
            ```python
            try:
                worker.start_worker(background=True)
                # ... do work ...
            finally:
                worker.stop_worker()
            ```
        """
        if hasattr(self, "_worker_process") and self._worker_process is not None:
            if self._worker_process.is_alive():
                self._worker_process.terminate()
                self._worker_process.join(timeout=5)
                logger.info("RQ worker process terminated")
            self._worker_process = None
        else:
            logger.warning("No worker process to stop")

    def start_worker_pool(
        self,
        num_workers: int | None = None,
        background: bool = False,
        queue_names: list[str] | None = None,
        with_scheduler: bool = True,
        **kwargs: Any,
    ) -> None:
        """Start a pool of worker processes to handle jobs in parallel.

        This implementation uses RQ's WorkerPool class which provides robust worker
        management with proper monitoring and graceful shutdown.

        Args:
            num_workers: Number of worker processes to start. If None, uses CPU
                count or configuration value.
            background: If True, runs the worker pool in background mode.
                If False, runs in the current process and blocks.
            queue_names: List of queue names to process. If None, processes all
                queues defined in the backend configuration.
            with_scheduler: Whether to include the scheduler queue for processing
                scheduled jobs.
            **kwargs: Additional arguments passed to RQ's WorkerPool class.
                Example: {"max_jobs": 100, "job_monitoring_interval": 30}

        Raises:
            RuntimeError: If worker pool fails to start or Redis connection fails.

        Example:
            ```python
            # Start pool with default settings
            worker.start_worker_pool(num_workers=4, background=True)

            # Start pool for specific queues
            worker.start_worker_pool(
                num_workers=4,
                background=True,
                queue_names=["high", "default"],
                with_scheduler=False
            )

            # Start pool with custom settings
            worker.start_worker_pool(
                num_workers=4,
                background=True,
                max_jobs=100,
                job_monitoring_interval=30
            )
            ```
        """
        import multiprocessing

        logging_level = kwargs.pop("logging_level", self._log_level)
        burst = kwargs.pop("burst", False)
        max_jobs = kwargs.pop("max_jobs", None)

        # if num_workers is None:
        #     backend = getattr(self.cfg, "backend", None)
        #     if backend is not None:
        #         num_workers = getattr(backend, "num_workers", None)
        if num_workers is None:
            num_workers = self.cfg.num_workers or multiprocessing.cpu_count()
        # Determine which queues to process
        if queue_names is None:
            # Use all queues by default
            queue_list = self._queue_names
            queue_names_str = ", ".join(queue_list)
        else:
            # Filter to only include valid queue names
            queue_list = [name for name in queue_names if name in self._queue_names]
            queue_names_str = ", ".join(queue_list)

        if not queue_list:
            logger.error("No valid queues specified, cannot start worker pool")
            return
        if with_scheduler:
            # Add the scheduler queue to the list of queues
            queue_list.append(self._scheduler_name)
            queue_names_str = ", ".join(queue_list)

        # Initialize RQ's WorkerPool
        worker_pool = WorkerPool(
            queues=queue_list,
            connection=self._backend.client,
            num_workers=num_workers,
            **kwargs,
        )
        # worker_pool.log = logger

        self._worker_pool = worker_pool

        if background:
            # Start the worker pool process using multiprocessing to avoid signal handler issues
            def run_pool_process():
                worker_pool.start(
                    burst=burst, logging_level=logging_level, max_jobs=max_jobs
                )

            self._pool_process = multiprocessing.Process(
                target=run_pool_process,
                name=f"rq-worker-pool-{self.name}",
            )
            self._pool_process.start()
            logger.info(
                f"Worker pool started with {num_workers} workers across queues: {queue_names_str} in background process (PID: {self._pool_process.pid})"
            )
        else:
            # Start the worker pool in the current process (blocking)
            logger.info(
                f"Starting worker pool with {num_workers} workers across queues: {queue_names_str} in foreground (blocking)"
            )
            worker_pool.start(burst=burst, logging_level=logging_level)

    def stop_worker_pool(self) -> None:
        """Stop all worker processes in the pool.

        This method stops all worker processes in the pool and performs cleanup.
        It ensures a graceful shutdown of all workers.

        Example:
            ```python
            try:
                worker.start_worker_pool(num_workers=4, background=True)
                # ... do work ...
            finally:
                worker.stop_worker_pool()
            ```
        """
        if hasattr(self, "_worker_pool"):
            logger.info("Stopping RQ worker pool")
            self._worker_pool.stop_workers()

            if hasattr(self, "_pool_process") and self._pool_process.is_alive():
                # Terminate the worker pool process
                self._pool_process.terminate()
                self._pool_process.join(timeout=10)
                if self._pool_process.is_alive():
                    logger.warning(
                        "Worker pool process did not terminate within timeout"
                    )

            self._worker_pool = None

            if hasattr(self, "_pool_process"):
                self._pool_process = None
        else:
            logger.warning("No worker pool to stop")

    def start_scheduler(self, background: bool = False, interval: int = 60) -> None:
        """Start the RQ scheduler process.

        The scheduler process manages scheduled and recurring jobs. It must be
        running for scheduled jobs to execute.

        Args:
            background: If True, runs the scheduler in a non-blocking background mode.
                If False, runs in the current process and blocks.
            interval: How often to check for scheduled jobs, in seconds.

        Raises:
            RuntimeError: If scheduler fails to start or Redis connection fails.

        Example:
            ```python
            # Start scheduler in background checking every 30 seconds
            worker.start_scheduler(background=True, interval=30)

            # Start scheduler in foreground (blocking)
            worker.start_scheduler(background=False)
            ```
        """
        # Create a scheduler instance with the queue name
        if not hasattr(self, "_scheduler"):
            self._scheduler = Scheduler(
                connection=self._backend.client,
                queue_name=self._backend.queues[-1],
                interval=interval,
            )
            self._scheduler.log = logger

        elif self._scheduler._interval != interval:
            self._scheduler = Scheduler(
                connection=self._backend.client,
                queue_name=self._backend.queues[-1],
                interval=interval,
            )
            self._scheduler.log = logger

        if background:

            def run_scheduler():
                self._scheduler.run()

            self._scheduler_process = multiprocessing.Process(
                target=run_scheduler, name=f"rq-scheduler-{self.name}"
            )
            self._scheduler_process.start()
            logger.info(
                f"Started RQ scheduler in background (PID: {self._scheduler_process.pid})"
            )
        else:
            logger.info("Starting RQ scheduler in current process (blocking)")
            self._scheduler.run()

    def stop_scheduler(self) -> None:
        """Stop the RQ scheduler process.

        This method stops the scheduler process if running in background mode
        and performs cleanup.

        Example:
            ```python
            try:
                worker.start_scheduler(background=True)
                # ... do work ...
            finally:
                worker.stop_scheduler()
            ```
        """
        if hasattr(self, "_scheduler_process") and self._scheduler_process is not None:
            if self._scheduler_process.is_alive():
                self._scheduler_process.terminate()
                self._scheduler_process.join(timeout=5)
                logger.info("RQ scheduler process terminated")
            self._scheduler_process = None
        else:
            logger.debug("No scheduler process to stop")

    ## Jobs ###

    def add_job(
        self,
        func: Callable,
        func_args: tuple | None = None,
        func_kwargs: dict[str, Any] | None = None,
        job_id: str | None = None,
        result_ttl: int | dt.timedelta | None = None,
        ttl: int | dt.timedelta | None = None,
        timeout: int | dt.timedelta | None = None,
        queue_name: str | None = None,
        run_at: dt.datetime | str | None = None,
        run_in: dt.timedelta | int | str | None = None,
        retry: int | dict | None = None,
        repeat: int | dict | None = None,
        meta: dict | None = None,
        failure_ttl: int | dt.timedelta | None = None,
        group_id: str | None = None,
        on_success: Callback | Callable | str | None = None,
        on_failure: Callback | Callable | str | None = None,
        on_stopped: Callback | Callable | str | None = None,
        **job_kwargs,
    ) -> Job:
        """Add a job for immediate or scheduled execution.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            job_id: Optional unique identifier for the job. If None, a UUID is generated.
            result_ttl: Time to live for the job result, as seconds or timedelta.
                After this time, the result may be removed from Redis.
            ttl: Maximum time the job can exist in Redis, as seconds or timedelta.
                After this time, the job will be removed even if not complete.
            timeout: Maximum time the job can run before being killed, as seconds or timedelta.
            queue_name: Name of the queue to place the job in. If None, uses the
                first queue from configuration.
            run_at: Schedule the job to run at a specific datetime.
            run_in: Schedule the job to run after a delay.
            retry: Number of retries or retry configuration dictionary.
                Example dict: {"max": 3, "interval": 60}
            repeat: Number of repetitions or repeat configuration dictionary.
                Example dict: {"max": 5, "interval": 3600}
            meta: Additional metadata to store with the job.
            failure_ttl: Time to live for the job failure result, as seconds or timedelta.
            group_id: Optional group ID to associate this job with a group.
            on_success: Callback to run on job success. Can be a function, string,
                or RQ Callback instance.
            on_failure: Callback to run on job failure. Can be a function, string,
                or RQ Callback instance.
            on_stopped: Callback to run when the job is stopped. Can be a function,
                string, or RQ Callback instance.
            **job_kwargs: Additional arguments for RQ's Job class.

        Returns:
            Job: The created job instance.

        Raises:
            ValueError: If the function is not serializable or arguments are invalid.
            RuntimeError: If Redis connection fails.

        Example:
            ```python
            def my_task(x: int, y: int = 0) -> int:
                return x + y

            # Add immediate job
            job = worker.add_job(
                my_task,
                func_args=(1,),
                func_kwargs={"y": 2},
                result_ttl=3600  # Keep result for 1 hour
            )

            # Add scheduled job
            tomorrow = dt.datetime.now() + dt.timedelta(days=1)
            job = worker.add_job(
                my_task,
                func_args=(1, 2),
                run_at=tomorrow,
                queue_name="scheduled"
            )

            # Add job with retries
            job = worker.add_job(
                my_task,
                func_args=(1, 2),
                retry={"max": 3, "interval": 60}  # 3 retries, 1 minute apart
            )

            # Add repeating job
            job = worker.add_job(
                my_task,
                func_args=(1, 2),
                repeat={"max": 5, "interval": 3600}  # 5 times, hourly
            )
            ```
        """
        job_id = job_id or str(uuid.uuid4())
        if isinstance(result_ttl, (int, float)):
            result_ttl = dt.timedelta(seconds=result_ttl)
        # args = args or ()
        # kwargs = kwargs or {}
        if queue_name is None:
            queue_name = self._queue_names[0]
        elif queue_name not in self._queue_names:
            logger.warning(
                f"Queue '{queue_name}' not found, using '{self._queue_names[0]}'"
            )
            queue_name = self._queue_names[0]

        if repeat:
            # If repeat is an int, convert it to a Repeat instance
            if isinstance(repeat, int):
                repeat = Repeat(max=repeat)
            elif isinstance(repeat, dict):
                # If repeat is a dict, convert it to a Repeat instance
                repeat = Repeat(**repeat)
            else:
                raise ValueError("Invalid repeat value. Must be int or dict.")
        if retry:
            if isinstance(retry, int):
                retry = Retry(max=retry)
            elif isinstance(retry, dict):
                # If retry is a dict, convert it to a Retry instance
                retry = Retry(**retry)
            else:
                raise ValueError("Invalid retry value. Must be int or dict.")

        if isinstance(ttl, dt.timedelta):
            ttl = ttl.total_seconds()
        if isinstance(timeout, dt.timedelta):
            timeout = timeout.total_seconds()
        if isinstance(result_ttl, dt.timedelta):
            result_ttl = result_ttl.total_seconds()
        if isinstance(failure_ttl, dt.timedelta):
            failure_ttl = failure_ttl.total_seconds()

        if isinstance(on_success, (str, Callable)):
            on_success = Callback(on_success)
        if isinstance(on_failure, (str, Callable)):
            on_failure = Callback(on_failure)
        if isinstance(on_stopped, (str, Callable)):
            on_stopped = Callback(on_stopped)

        queue = self._queues[queue_name]
        if run_at:
            # Schedule the job to run at a specific time
            run_at = (
                dt.datetime.fromisoformat(run_at) if isinstance(run_at, str) else run_at
            )
            job = queue.enqueue_at(
                run_at,
                func,
                args=func_args,
                kwargs=func_kwargs,
                job_id=job_id,
                result_ttl=int(result_ttl) if result_ttl else None,
                ttl=int(ttl) if ttl else None,
                failure_ttl=int(failure_ttl) if failure_ttl else None,
                timeout=int(timeout) if timeout else None,
                retry=retry,
                repeat=repeat,
                meta=meta,
                group_id=group_id,
                on_success=on_success,
                on_failure=on_failure,
                on_stopped=on_stopped,
                **job_kwargs,
            )
            logger.info(
                f"Enqueued job {job.id} ({func.__name__}) on queue '{queue_name}'. Scheduled to run at {run_at}."
            )
        elif run_in:
            # Schedule the job to run after a delay
            run_in = (
                duration_parser.parse(run_in) if isinstance(run_in, str) else run_in
            )
            run_in = (
                dt.timedelta(seconds=run_in)
                if isinstance(run_in, (int, float))
                else run_in
            )
            job = queue.enqueue_in(
                run_in,
                func,
                args=func_args,
                kwargs=func_kwargs,
                job_id=job_id,
                result_ttl=int(result_ttl) if result_ttl else None,
                ttl=int(ttl) if ttl else None,
                failure_ttl=int(failure_ttl) if failure_ttl else None,
                timeout=int(timeout) if timeout else None,
                retry=retry,
                repeat=repeat,
                meta=meta,
                group_id=group_id,
                on_success=on_success,
                on_failure=on_failure,
                on_stopped=on_stopped,
                **job_kwargs,
            )
            logger.info(
                f"Enqueued job {job.id} ({func.__name__}) on queue '{queue_name}'. Scheduled to run in {precisedelta(run_in)}."
            )
        else:
            # Enqueue the job for immediate execution
            job = queue.enqueue(
                func,
                args=func_args,
                kwargs=func_kwargs,
                job_id=job_id,
                result_ttl=int(result_ttl) if result_ttl else None,
                ttl=int(ttl) if ttl else None,
                failure_ttl=int(failure_ttl) if failure_ttl else None,
                timeout=int(timeout) if timeout else None,
                retry=retry,
                repeat=repeat,
                meta=meta,
                group_id=group_id,
                on_success=on_success,
                on_failure=on_failure,
                on_stopped=on_stopped,
                **job_kwargs,
            )
            logger.info(
                f"Enqueued job {job.id} ({func.__name__}) on queue '{queue_name}'"
            )
        return job

    def run_job(
        self,
        func: Callable,
        func_args: tuple | None = None,
        func_kwargs: dict[str, Any] | None = None,
        job_id: str | None = None,
        result_ttl: int | dt.timedelta | None = None,
        ttl: int | dt.timedelta | None = None,
        queue_name: str | None = None,
        retry: int | dict | None = None,
        repeat: int | dict | None = None,
        meta: dict | None = None,
        failure_ttl: int | dt.timedelta | None = None,
        group_id: str | None = None,
        on_success: Callback | Callable | str | None = None,
        on_failure: Callback | Callable | str | None = None,
        on_stopped: Callback | Callable | str | None = None,
        **job_kwargs,
    ) -> Any:
        """Run a job immediately and return its result.

        This method is a wrapper around add_job that waits for the job to complete
        and returns its result.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            job_id: Optional unique identifier for the job.
            result_ttl: Time to live for the job result.
            ttl: Maximum time the job can exist.
            queue_name: Name of the queue to use.
            retry: Number of retries or retry configuration.
            repeat: Number of repetitions or repeat configuration.
            meta: Additional metadata to store with the job.
            failure_ttl: Time to live for the job failure result.
            group_id: Optional group ID to associate this job with a group.
            on_success: Callback to run on job success.
            on_failure: Callback to run on job failure.
            on_stopped: Callback to run when the job is stopped.
            **job_kwargs: Additional arguments for RQ's Job class.

        Returns:
            Any: The result returned by the executed function.

        Raises:
            Exception: Any exception raised by the executed function.
            TimeoutError: If the job times out before completion.

        Example:
            ```python
            def add(x: int, y: int) -> int:
                return x + y

            # Run job and get result immediately
            result = worker.run_job(
                add,
                func_args=(1, 2),
                retry=3  # Retry up to 3 times on failure
            )
            assert result == 3
            ```
        """
        job = self.add_job(
            func=func,
            func_args=func_args,
            func_kwargs=func_kwargs,
            job_id=job_id,
            result_ttl=result_ttl,
            ttl=ttl,
            queue_name=queue_name,
            retry=retry,
            repeat=repeat,
            meta=meta,
            failure_ttl=failure_ttl,
            group_id=group_id,
            on_success=on_success,
            on_failure=on_failure,
            on_stopped=on_stopped,
            **job_kwargs,
        )
        while not job.is_finished:
            job.refresh()
            time.sleep(0.1)
        return job.result

    def _get_job_queue_name(self, job: str | Job) -> str | None:
        """Get the queue name for a job.

        Args:
            job: Job ID or Job object.

        Returns:
            str | None: Name of the queue containing the job, or None if not found.
        """
        job_id = job if isinstance(job, str) else job.id
        for queue_name in self.job_ids:
            if job_id in self.job_ids[queue_name]:
                return queue_name
        return None

    def get_jobs(
        self, queue_name: str | list[str] | None = None
    ) -> dict[str, list[Job]]:
        """Get all jobs from specified queues.

        Args:
            queue_name: Optional queue name or list of queue names to get jobs from.
                If None, gets jobs from all queues.

        Returns:
            dict[str, list[Job]]: Dictionary mapping queue names to lists of jobs.

        Example:
            ```python
            # Get jobs from all queues
            jobs = worker.get_jobs()
            for queue_name, queue_jobs in jobs.items():
                print(f"Queue {queue_name}: {len(queue_jobs)} jobs")

            # Get jobs from specific queues
            jobs = worker.get_jobs(["high", "default"])
            ```
        """
        if queue_name is None:
            queue_name = self._queue_names
        elif isinstance(queue_name, str):
            queue_name = [queue_name]
        jobs = {
            queue_name: self._queues[queue_name].get_jobs() for queue_name in queue_name
        }
        return jobs

    def get_job(self, job_id: str) -> Job | None:
        """Get a specific job by its ID.

        Args:
            job_id: Unique identifier of the job to retrieve.

        Returns:
            Job | None: The job object if found, None otherwise.

        Example:
            ```python
            job = worker.get_job("550e8400-e29b-41d4-a716-446655440000")
            if job:
                print(f"Job status: {job.get_status()}")
            ```
        """
        queue_name = self._get_job_queue_name(job=job_id)
        if queue_name is None:
            logger.error(f"Job {job_id} not found in any queue")
            return None
        job = self._queues[queue_name].fetch_job(job_id)
        if job is None:
            logger.error(f"Job {job_id} not found in queue '{queue_name}'")
            return None
        return job

    def get_job_result(self, job: str | Job, delete_result: bool = False) -> Any:
        """Get the result of a completed job.

        Args:
            job: Job ID or Job object.
            delete_result: If True, deletes the job and its result after retrieval.

        Returns:
            Any: The result of the job if available.

        Example:
            ```python
            # Get result and keep the job
            result = worker.get_job_result("job-123")

            # Get result and clean up
            result = worker.get_job_result("job-123", delete_result=True)
            ```
        """
        if isinstance(job, str):
            job = self.get_job(job_id=job)

        if job is None:
            logger.error(f"Job {job} not found in any queue")
            return None

        if delete_result:
            self.delete_job(job)

        return job.result

    def cancel_job(self, job: str | Job) -> bool:
        """
        Cancel a job in the queue.

        Args:
            job: Job ID or Job object

        Returns:
            bool: True if the job was canceled, False otherwise
        """
        if isinstance(job, str):
            job = self.get_job(job_id=job)
        if job is None:
            logger.error(f"Job {job} not found in any queue")
            return False

        job.cancel()
        logger.info(f"Canceled job {job.id} from queue '{job.origin}'")
        return True

    def delete_job(self, job: str | Job, ttl: int = 0, **kwargs) -> bool:
        """
        Remove a job from the queue.

        Args:
            job: Job ID or Job object
            ttl: Optional time to live for the job (in seconds). 0 means no TTL.
                Remove the job immediately.
            **kwargs: Additional parameters for the job removal

        Returns:
            bool: True if the job was removed, False otherwise
        """
        if isinstance(job, str):
            job = self.get_job(job)
            if job is None:
                return False
        if ttl:
            job.cleanup(ttl=ttl, **kwargs)
            logger.info(
                f"Removed job {job.id} from queue '{job.origin}' with TTL {ttl}"
            )
        else:
            job.delete(**kwargs)
        logger.info(f"Removed job {job.id} from queue '{job.origin}'")

        return True

    def cancel_all_jobs(self, queue_name: str | None = None) -> None:
        """
        Cancel all jobs in a queue.

        Args:
            queue_name (str | None): Optional name of the queue to cancel jobs from.
                If None, cancels jobs from all queues.
        """
        if queue_name is None:
            queue_name = self._queue_names
        elif isinstance(queue_name, str):
            queue_name = [queue_name]

        for queue_name in queue_name:
            if queue_name not in self._queue_names:
                logger.warning(f"Queue '{queue_name}' not found, skipping")
                continue

            for job in self.get_jobs(queue_name=queue_name):
                self.cancel_job(job)

    def delete_all_jobs(self, queue_name: str | None = None, ttl: int = 0) -> None:
        """
        Remove all jobs from a queue.

        Args:
            queue_name (str | None): Optional name of the queue to remove jobs from.
                If None, removes jobs from all queues.
            ttl: Optional time to live for the job (in seconds). 0 means no TTL.
                Remove the job immediately.

        """
        if queue_name is None:
            queue_name = self._queue_names
        elif isinstance(queue_name, str):
            queue_name = [queue_name]

        for queue_name in queue_name:
            if queue_name not in self._queue_names:
                logger.warning(f"Queue '{queue_name}' not found, skipping")
                continue

            for job in self.get_jobs(queue_name=queue_name):
                self.delete_job(job, ttl=ttl)

    @property
    def job_ids(self):
        """Get all job IDs from all queues.

        Returns:
            dict[str, list[str]]: Dictionary mapping queue names to lists of job IDs.

        Example:
            ```python
            all_ids = worker.job_ids
            for queue_name, ids in all_ids.items():
                print(f"Queue {queue_name}: {len(ids)} jobs")
            ```
        """
        job_ids = {}
        for queue_name in self._queue_names:
            job_ids[queue_name] = self._queues[queue_name].job_ids

        return job_ids

    @property
    def jobs(self):
        """Get all jobs from all queues.

        Returns:
            dict[str, list[Job]]: Dictionary mapping queue names to lists of jobs.

        Example:
            ```python
            all_jobs = worker.jobs
            for queue_name, queue_jobs in all_jobs.items():
                print(f"Queue {queue_name}: {len(queue_jobs)} jobs")
            ```
        """
        jobs = {}
        for queue_name in self._queue_names:
            jobs[queue_name] = self._queues[queue_name].get_jobs()

        return jobs

    ### Schedules ###

    def add_schedule(
        self,
        func: Callable,
        func_args: tuple | None = None,
        func_kwargs: dict[str, Any] | None = None,
        cron: str | None = None,  # Cron expression for scheduling
        interval: int | None = None,  # Interval in seconds
        date: dt.datetime | None = None,  # Date to run the job
        queue_name: str | None = None,
        schedule_id: str | None = None,
        ttl: int | dt.timedelta | None = None,
        result_ttl: int | dt.timedelta | None = None,
        repeat: int | None = None,
        timeout: int | dt.timedelta | None = None,
        meta: dict | None = None,
        on_success: Callback | Callable | str | None = None,
        on_failure: Callback | Callable | str | None = None,
        on_stopped: Callback | Callable | str | None = None,
        **schedule_kwargs,
    ) -> Job:
        """Schedule a job for repeated or one-time execution.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            cron: Cron expression for scheduling (e.g. "0 * * * *" for hourly).
            interval: Interval in seconds for recurring execution.
            date: Specific datetime for one-time execution.
            queue_name: Name of the queue to use for the scheduled job.
            schedule_id: Optional unique identifier for the schedule.
            ttl: Time to live for the schedule, as seconds or timedelta.
            result_ttl: Time to live for the job result, as seconds or timedelta.
            repeat: Number of repetitions
            timeout: Maximum time the job can run before being killed, as seconds or timedelta.
            meta: Additional metadata to store with the schedule.
            on_success: Callback to run on schedule success. Can be a function,
                string, or RQ Callback instance.
            on_failure: Callback to run on schedule failure. Can be a function,
                string, or RQ Callback instance.
            on_stopped: Callback to run when the schedule is stopped. Can be a function,
                string, or RQ Callback instance.
            **schedule_kwargs: Additional scheduling parameters:
                - repeat: Number of repetitions (int or dict)
                - result_ttl: Time to live for results (float or timedelta)
                - ttl: Time to live for the schedule (float or timedelta)
                - use_local_time_zone: Whether to use local time (bool)
                - queue_name: Queue to use for the scheduled jobs

        Returns:
            Job: The scheduled job instance.

        Raises:
            ValueError: If no scheduling method specified or invalid cron expression.
            RuntimeError: If Redis connection fails.

        Example:
            ```python
            def my_task(msg: str) -> None:
                print(f"Task: {msg}")

            # Schedule with cron (every hour)
            job = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Hourly check"},
                cron="0 * * * *"
            )

            # Schedule with interval (every 5 minutes)
            job = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Regular check"},
                interval=300
            )

            # Schedule for specific time
            tomorrow = dt.datetime.now() + dt.timedelta(days=1)
            job = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "One-time task"},
                date=tomorrow
            )
            ```
        """
        schedule_id = schedule_id or str(uuid.uuid4())
        func_args = func_args or ()
        func_kwargs = func_kwargs or {}

        # Use the specified scheduler or default to the first one

        scheduler = self._scheduler

        use_local_time_zone = schedule_kwargs.get("use_local_time_zone", True)
        # repeat = schedule_kwargs.get("repeat", None)
        # result_ttl = schedule_kwargs.get("result_ttl", None)
        # ttl = schedule_kwargs.get("ttl", None)
        if isinstance(result_ttl, dt.timedelta):
            result_ttl = result_ttl.total_seconds()
        if isinstance(ttl, dt.timedelta):
            ttl = ttl.total_seconds()
        if isinstance(timeout, dt.timedelta):
            timeout = timeout.total_seconds()
        if isinstance(interval, dt.timedelta):
            interval = interval.total_seconds()

        if isinstance(on_failure, (str, Callable)):
            on_failure = Callback(on_failure)
        if isinstance(on_success, (str, Callable)):
            on_success = Callback(on_success)
        if isinstance(on_stopped, (str, Callable)):
            on_stopped = Callback(on_stopped)

        if cron:
            if meta:
                meta.update({"cron": cron})
            else:
                meta = {"cron": cron}
            schedule = scheduler.cron(
                cron_string=cron,
                func=func,
                args=func_args,
                kwargs=func_kwargs,
                id=schedule_id,
                repeat=repeat,  # Infinite by default
                result_ttl=int(result_ttl) if result_ttl else None,
                ttl=int(ttl) if ttl else None,
                timeout=int(timeout) if timeout else None,
                meta=meta,
                use_local_time_zone=use_local_time_zone,
                queue_name=queue_name or self._scheduler_name,
                on_success=on_success,
                on_failure=on_failure,
                **schedule_kwargs,
            )
            logger.info(
                f"Scheduled job {schedule.id} ({func.__name__}) with cron '{get_description(cron)}'"
            )

        if interval:
            if meta:
                meta.update({"interval": int(interval)})
            else:
                meta = {"interval": int(interval)}
            schedule = scheduler.schedule(
                scheduled_time=dt.datetime.now(dt.timezone.utc),
                func=func,
                args=func_args,
                kwargs=func_kwargs,
                interval=int(interval),
                id=schedule_id,
                repeat=repeat,  # Infinite by default
                result_ttl=int(result_ttl) if result_ttl else None,
                ttl=int(ttl) if ttl else None,
                timeout=int(timeout) if timeout else None,
                meta=meta,
                queue_name=queue_name or self._scheduler_name,
                on_success=on_success,
                on_failure=on_failure,
                **schedule_kwargs,
            )
            logger.info(
                f"Scheduled job {schedule.id} ({func.__name__})  with interval '{precisedelta(interval)}'"
            )

        if date:
            if meta:
                meta.update({"date": date})
            else:
                meta = {"date": date}
            schedule = scheduler.schedule(
                scheduled_time=date,
                func=func,
                args=func_args,
                kwargs=func_kwargs,
                id=schedule_id,
                repeat=1,  # Infinite by default
                result_ttl=int(result_ttl) if result_ttl else None,
                ttl=int(ttl) if ttl else None,
                timeout=int(timeout) if timeout else None,
                meta=meta,
                queue_name=queue_name or self._scheduler_name,
                on_success=on_success,
                on_failure=on_failure,
                on_stopped=on_stopped,
            )
            logger.info(
                f"Scheduled job {schedule.id} ({func.__name__}) to run at '{date}'"
            )

        return schedule

    def _get_schedule_queue_name(self, schedule: str | Job) -> str | None:
        """Get the queue name for a schedule.

        Args:
            schedule: Schedule ID or Job object.

        Returns:
            str | None: Name of the scheduler queue.
        """
        return self._scheduler_name

    def get_schedules(
        self,
        until: Any | None = None,
        with_times: bool = False,
        offset: Any | None = None,
        length: Any | None = None,
    ) -> dict[str, list[Job]]:
        """Get all schedules from the scheduler.

        Args:
            until: Get schedules until this time.
            with_times: Include next run times in the results.
            offset: Number of schedules to skip.
            length: Maximum number of schedules to return.

        Returns:
            dict[str, list[Job]]: Dictionary mapping queue names to lists of schedules.

        Example:
            ```python
            # Get all schedules
            schedules = worker.get_schedules()

            # Get next 10 schedules with run times
            schedules = worker.get_schedules(
                with_times=True,
                length=10
            )
            ```
        """
        schedules = list(
            self._scheduler.get_jobs(
                until=until, with_times=with_times, offset=offset, length=length
            )
        )
        if not schedules:
            logger.info("No schedules found")
            return []
        return schedules

    def get_schedule(self, schedule_id: str) -> Job | None:
        """
        Get a schedule by its ID.

        Args:
            schedule_id: ID of the schedule

        Returns:
            Job | None: Schedule object if found, None otherwise
        """
        schedule = self.get_job(job_id=schedule_id)
        return schedule

    def _get_schedule_results(self, schedule: str | Job) -> list[Result]:
        """Get all results from a schedule's execution history.

        Args:
            schedule: Schedule ID or Job object.

        Returns:
            list[Result]: List of all results from the schedule's executions.

        Raises:
            ValueError: If schedule not found.
        """
        if isinstance(schedule, str):
            schedule = self.get_schedule(schedule_id=schedule)

        if schedule is None:
            logger.error(f"Schedule {schedule} not found in any queue")
            return None

        return [res.return_value for res in schedule.results()]

    def get_schedule_latest_result(
        self, schedule: str | Job, delete_result: bool = False
    ) -> Any:
        """Get the most recent result of a schedule.

        Args:
            schedule: Schedule ID or Job object.
            delete_result: If True, deletes the schedule and results after retrieval.

        Returns:
            Any: The most recent result of the schedule if available.

        Example:
            ```python
            # Get latest result
            result = worker.get_schedule_latest_result("schedule-123")

            # Get result and clean up
            result = worker.get_schedule_latest_result(
                "schedule-123",
                delete_result=True
            )
            ```
        """
        result = self._get_schedule_result(schedule=schedule)[-1]

        if delete_result:
            self.delete_schedule(schedule)

        return result

    def get_schedule_result(
        self, schedule: str | Job, index: int | list[str] | slice | str
    ) -> list[Result]:
        """Get specific results from a schedule's execution history.

        Args:
            schedule: Schedule ID or Job object.
            index: Which results to retrieve. Can be:
                - int: Specific index
                - list[str]: List of indices
                - slice: Range of indices
                - str: "all", "latest", or "earliest"

        Returns:
            list[Result]: List of requested results.

        Example:
            ```python
            # Get all results
            results = worker.get_schedule_result("schedule-123", "all")

            # Get latest result
            result = worker.get_schedule_result("schedule-123", "latest")

            # Get specific results
            results = worker.get_schedule_result("schedule-123", [0, 2, 4])

            # Get range of results
            results = worker.get_schedule_result("schedule-123", slice(0, 5))
            ```
        """
        results = self._get_schedule_results(schedule=schedule)
        if not results:
            return []

        if isinstance(index, str):
            if ":" in index:
                index = [int(i) for i in index.split(":")]
                index = slice(index[0], index[1])
                return [result for result in results[index]]

            if index == "all":
                return [result for result in results]
            if index == "latest":
                return results[-1]
            if index == "earliest":
                return results[0]

        elif isinstance(index, list):
            return [results[i].return_value for i in index if i < len(results)]
        elif isinstance(index, slice):
            return [result.return_value for result in results[index]]
        elif isinstance(index, int):
            if index >= len(results):
                logger.error(f"Index {index} out of range for schedule {schedule.id}")
                return []
            return results[index].return_value

    def cancel_schedule(self, schedule: str | Job) -> bool:
        """Cancel a schedule.

        This method stops any future executions of the schedule without removing
        past results.

        Args:
            schedule: Schedule ID or Job object to cancel.

        Returns:
            bool: True if successfully canceled, False if schedule not found.

        Example:
            ```python
            # Cancel by ID
            worker.cancel_schedule("schedule-123")

            # Cancel using job object
            schedule = worker.get_schedule("schedule-123")
            if schedule:
                worker.cancel_schedule(schedule)
            ```
        """
        if schedule is None:
            logger.error(f"Schedule {schedule} not found")
            return False

        self._scheduler.cancel(schedule)
        logger.info(
            f"Canceled schedule {schedule.id if isinstance(schedule, Job) else schedule}"
        )
        return True

    def cancel_all_schedules(self) -> None:
        """Cancel all schedules in the scheduler.

        This method stops all future executions of all schedules without removing
        past results.

        Example:
            ```python
            # Stop all scheduled jobs
            worker.cancel_all_schedules()
            ```
        """
        for job in self._scheduler.get_jobs():
            self._scheduler.cancel(job.id)
            logger.info(f"Canceled schedule {job.id} ")
        logger.info("Canceled all schedules from all queues.")

    def delete_schedule(self, schedule: str | Job) -> bool:
        """Delete a schedule and optionally its results.

        This method removes the schedule and optionally its execution history
        from Redis.

        Args:
            schedule: Schedule ID or Job object to delete.

        Returns:
            bool: True if successfully deleted, False if schedule not found.

        Example:
            ```python
            # Delete schedule and its history
            worker.delete_schedule("schedule-123")
            ```
        """
        return self.delete_job(schedule)

    def delete_all_schedules(self) -> None:
        """Delete all schedules and their results.

        This method removes all schedules and their execution histories from Redis.

        Example:
            ```python
            # Remove all schedules and their histories
            worker.delete_all_schedules()
            ```
        """
        for schedule in self.schedule_ids:
            self.delete_schedule(schedule)
            logger.info(f"Deleted schedule {schedule}")
        logger.info("Deleted all schedules from all queues.")

    @property
    def schedules(self):
        """Get all schedules from all schedulers.

        Returns:
            list[Job]: List of all scheduled jobs.

        Example:
            ```python
            all_schedules = worker.schedules
            print(f"Total schedules: {len(all_schedules)}")
            ```
        """
        schedules = self.get_schedules()

        return schedules

    @property
    def schedule_ids(self):
        """Get all schedule IDs.

        Returns:
            list[str]: List of unique identifiers for all schedules.

        Example:
            ```python
            ids = worker.schedule_ids
            print(f"Schedule IDs: {', '.join(ids)}")
            ```
        """
        schedule_ids = [schedule.id for schedule in self.schedules]
        return schedule_ids
