"""
RQSchedulerBackend implementation for FlowerPower using RQ and rq-scheduler.

This module implements the scheduler backend using RQ (Redis Queue) and rq-scheduler.
"""

import random
import datetime as dt
import multiprocessing
import platform
import sys
import uuid
from typing import Any, Callable
from cron_descriptor import get_description
from humanize import precisedelta
from loguru import logger
from rq import Queue, Repeat, Retry
from rq.job import Job
from rq.results import Result
from rq_scheduler import Scheduler


from ...fs import AbstractFileSystem
from ...utils.logging import setup_logging
from ..base import BaseWorker
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


class RQWorker(BaseWorker):
    """
    Implementation of BaseScheduler using RQ and rq-scheduler.
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
        """
        Initialize the RQScheduler backend.

        Args:
            name (str): Name of the scheduler
            base_dir (str | None): Base directory for the scheduler
            backend (RQBackend | None): RQ backend instance
            storage_options (dict[str, Any] | None): Storage options for the backend
            fs (AbstractFileSystem | None): File system instance
            log_level (str | None): Logging level for the scheduler
        """
        if log_level:
            setup_logging(level=log_level)

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
        self._schedulers = {}

        for queue_name in self._backend.queues:
            queue = Queue(name=queue_name, connection=redis_conn)
            self._queues[queue_name] = queue
            self._schedulers[queue_name] = Scheduler(queue=queue, connection=redis_conn)
            logger.debug(f"Created queue and scheduler for '{queue_name}'")

    def _setup_backend(self) -> None:
        """
        Set up the data store for the scheduler using config.
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
        self, background: bool = False, queue_names: list[str] | None = None
    ) -> None:
        """
        Start a worker process for processing jobs from the queues.

        Args:
            background: Whether to run the worker in the background or in the current process
            queue_names: List of queue names to process (defaults to all queues)
        """
        import multiprocessing

        from rq import Worker

        # Determine which queues to process
        if queue_names is None:
            # Use all queues by default
            queue_names = list(self._queues.keys())
            queue_names_str = ", ".join(queue_names)
        else:
            # Filter to only include valid queue names
            queue_names = [name for name in queue_names if name in self._queues]
            queue_names_str = ", ".join(queue_names)

        if not queue_names:
            logger.error("No valid queues specified, cannot start worker")
            return

        # Create a worker instance with queue names (not queue objects)
        worker = Worker(queue_names, connection=self._backend.client)

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
                worker_proc.work(with_scheduler=True)

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
            worker.work(with_scheduler=True)

    def stop_worker(self) -> None:
        """
        Stop the worker process if running in the background.
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
        background: bool = True,
        queue_names: list[str] | None = None,
    ) -> None:
        """
        Start a pool of worker processes to handle jobs in parallel using RQ's built-in WorkerPool.

        This implementation uses RQ's WorkerPool class which provides robust worker management
        with proper monitoring, restarting of crashed workers, and graceful shutdown.

        Args:
            num_workers: Number of worker processes to start (defaults to CPU count or config)
            background: Whether to run the workers in the background
            queue_names: List of queue names to process (defaults to all queues)
        """
        import multiprocessing

        from rq.worker_pool import WorkerPool

        if num_workers is None:
            num_workers = getattr(self.cfg, "rq_backend", None)
            if num_workers is not None:
                num_workers = getattr(num_workers, "num_workers", None)
            if num_workers is None:
                num_workers = multiprocessing.cpu_count()
        # Determine which queues to process
        if queue_names is None:
            # Use all queues by default
            queue_list = list(self._queues.keys())
            queue_names_str = ", ".join(queue_list)
        else:
            # Filter to only include valid queue names
            queue_list = [name for name in queue_names if name in self._queues]
            queue_names_str = ", ".join(queue_list)

        if not queue_list:
            logger.error("No valid queues specified, cannot start worker pool")
            return

        # Initialize RQ's WorkerPool
        worker_pool = WorkerPool(
            queues=queue_list, connection=self._backend.client, num_workers=num_workers
        )

        self._worker_pool = worker_pool

        if background:
            # Start the worker pool process using multiprocessing to avoid signal handler issues
            def run_pool_process():
                worker_pool.start(burst=False)

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
            worker_pool.start(burst=False)

    def stop_worker_pool(self) -> None:
        """
        Stop all worker processes in the pool using RQ's built-in WorkerPool.
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

    def _run_worker(self) -> None:
        """
        Helper method to run a worker process.
        Used by the worker pool.
        """
        from rq import Worker

        # Create a worker instance with queue names
        worker = Worker(self._backend.queues, connection=self._backend.client)
        # Start the worker (blocking call)
        worker.work(with_scheduler=True)

    ## Jobs ###




    def add_job(
        self,
        func: Callable,
        func_args: tuple | None = None,
        func_kwargs: dict[str, Any] | None = None,
        job_id: str | None = None,
        result_ttl: float | dt.timedelta | None = None,
        ttl: float | dt.timedelta | None = None,
        queue_name: str | None = None,
        run_at: dt.datetime | None = None,
        run_in: dt.timedelta | None = None,
        retry: int | dict | None = None,
        repeat: int | dict | None = None,
        **job_kwargs,
    ) -> Job:
        """
        Add a job for immediate execution.
        
        Note: passing `is_async=False` will run the job in the current process.

        Args:
            func (Callable): Function to execute
            func_args (tuple | None): Positional arguments for the function
            func_kwargs (dict[str, Any] | None): Keyword arguments for the function
            job_id (str | None): Optional job ID
            result_ttl (float | dt.timedelta | None): Time to live for the job result
            ttl (float | dt.timedelta | None): Time to live for the job
            queue_name (str | None): Name of the queue to use (defaults to first queue)
            run_at (dt.datetime | None): Schedule the job to run at a specific time
            run_in (dt.timedelta | None): Schedule the job to run after a delay
            retry (int | dict | None): Retry configuration. When it is an int, it will be
                converted to a Retry with max retries=retry. When it is a dict, it will be
                converted to a Retry with the given parameters.
            repeat (int | dict | None): Repeat configuration. When it is an int, it will be
                converted to a Repeat with max repeats=repeat. When it is a dict, it will be
                converted to a Repeat with the given parameters.
            **job_kwargs: Additional job parameters for the rq job.
        Returns:
            Job: Enqueued job object
        """
        job_id = job_id or str(uuid.uuid4())
        if isinstance(result_ttl, (int, float)):
            result_ttl = dt.timedelta(seconds=result_ttl)
        # args = args or ()
        # kwargs = kwargs or {}
        if queue_name is None:
            queue_name = random.choice(list(self._queues.keys()))
        elif queue_name not in self._queues:
            queue_name_new = random.choice(list(self._queues.keys()))
            logger.warning(f"Queue '{queue_name}' not found, using '{queue_name_new}'")
            queue_name = queue_name_new

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

        queue = self._queues[queue_name]
        if run_at:
            # Schedule the job to run at a specific time
            job = queue.enqueue_at(
                run_at,
                func,
                args=func_args,
                kwargs=func_kwargs,
                job_id=job_id,
                result_ttl=int(result_ttl.total_seconds()) if result_ttl else None,
                ttl=int(ttl.total_seconds()) if ttl else None,
                retry=retry,
                repeat=repeat,
                **job_kwargs,
            )
            logger.info(
                f"Enqueued job {job.id} ({func.__name__}) on queue '{queue_name}'. Scheduled to run at {run_at}."
            )
        elif run_in:
            # Schedule the job to run after a delay
            job = queue.enqueue_in(
                run_in,
                func,
                args=func_args,
                kwargs=func_kwargs,
                job_id=job_id,
                result_ttl=int(result_ttl.total_seconds()) if result_ttl else None,
                ttl=int(ttl.total_seconds()) if ttl else None,
                retry=retry,
                repeat=repeat,
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
                result_ttl=int(result_ttl.total_seconds()) if result_ttl else None,
                ttl=int(ttl.total_seconds()) if ttl else None,
                retry=retry,
                repeat=repeat,
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
            result_ttl: float | dt.timedelta | None = None,
            ttl: float | dt.timedelta | None = None,
            queue_name: str | None = None,
            retry: int | dict | None = None,
            repeat: int | dict | None = None,
            **job_kwargs)-> Any:
        """
        Run a job immediately  and return the result.
        
        This method is a wrapper around the add_job method, but it runs the job
        immediatly and returns the result.
        
        Args:
            func (Callable): Function to execute
            func_args (tuple | None): Positional arguments for the function
            func_kwargs (dict[str, Any] | None): Keyword arguments for the function
            job_id (str | None): Optional job ID
            result_ttl (float | dt.timedelta | None): Time to live for the job result
            ttl (float | dt.timedelta | None): Time to live for the job
            queue_name (str | None): Name of the queue to use (defaults to first queue)
            run_at (dt.datetime | None): Schedule the job to run at a specific time
            run_in (dt.timedelta | None): Schedule the job to run after a delay
            retry (int | dict | None): Retry configuration. When it is an int, it will be
                converted to a Retry with max retries=retry. When it is a dict, it will be
                converted to a Retry with the given parameters.
            repeat (int | dict | None): Repeat configuration. When it is an int, it will be
                converted to a Repeat with max repeats=repeat. When it is a dict, it will be
                converted to a Repeat with the given parameters.
            **job_kwargs: Additional job parameters for the rq job.
        
        Returns:

            Any: Result of the job
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
            **job_kwargs,
            )
        
        return job.result

    def _get_job_queue_name(self, job: str | Job) -> str | None:
        """
        Get the queue name for a job.

        Args:
            job: Job ID or Job object

        Returns:
            str | None: Queue name if found, None otherwise
        """
        job_id = job if isinstance(job, str) else job.id
        for queue_name in self.job_ids:
            if job_id in self.job_ids[queue_name]:
                return queue_name
        return None

    def get_jobs(
        self, queue_name: str | list[str] | None = None
    ) -> dict[str, list[Job]]:
        """
        Get all jobs in the queue.

        Args:
            queue_name: Optional name of the queue to get jobs from.
                        If None, gets jobs from all queues.

        Returns:
            list: List of jobs
        """
        if queue_name is None:
            queue_name = list(self._queues.keys())
        elif isinstance(queue_name, str):
            queue_name = [queue_name]
        jobs = {
            queue_name: self._queues[queue_name].get_jobs() for queue_name in queue_name
        }
        return jobs

    def get_job(self, job_id: str) -> Job | None:
        """
        Get a job by its ID.

        Args:
            job_id: ID of the job

        Returns:
            Job | None: Job object if found, None otherwise
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
        """
        Get the result of a job.

        Args:
            job: Job ID or Job object

        Returns:
            Any: Result of the job
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
                logger.error(f"Job {job} not found in any queue")
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
            queue_name = list(self._queues.keys())
        elif isinstance(queue_name, str):
            queue_name = [queue_name]

        for queue_name in queue_name:
            if queue_name not in self._queues:
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
            queue_name = list(self._queues.keys())
        elif isinstance(queue_name, str):
            queue_name = [queue_name]

        for queue_name in queue_name:
            if queue_name not in self._queues:
                logger.warning(f"Queue '{queue_name}' not found, skipping")
                continue

            for job in self.get_jobs(queue_name=queue_name):
                self.delete_job(job, ttl=ttl)

    @property
    def job_ids(self):
        """
        Get all job IDs from all queues.
        """
        job_ids = {}
        for queue_name in self._queues:
            job_ids[queue_name] = self._queues[queue_name].job_ids

        return job_ids

    @property
    def jobs(self):
        """
        Get all jobs from all queues.
        """
        jobs = {}
        for queue_name in self._queues:
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
        repeat: int | None = None,
        result_ttl: float | dt.timedelta | None = None,
        ttl: float | dt.timedelta | None = None,
        schedule_id: str | None = None,
        use_local_time_zone: bool = True,
        queue_name: str | None = None,
        **schedule_kwargs,
    ) -> Job:
        """
        Schedule a job for repeated execution.

        Args:
            func (Callable): Function to execute
            func_args (tuple | None): Positional arguments for the function
            func_kwargs (dict[str, Any] | None): Keyword arguments for the function
            cron (str | None): Cron expression for scheduling
            interval (int | None): Interval in seconds
            repeat (int | None): Repeat count
            result_ttl (float | dt.timedelta | None): Time to live for the job result
            ttl (float | dt.timedelta | None): Time to live for the job
            schedule_id (str | None): Optional schedule ID
            use_local_time_zone (bool): Whether to use local time zone for scheduling
            queue_name (str | None): Name of the queue to use (defaults to first queue)
            **schedule_kwargs: Additional schedule parameters for the rq-scheduler job.


        Returns:
            Job: Scheduled job object
        """
        schedule_id = schedule_id or str(uuid.uuid4())
        func_args = func_args or ()
        func_kwargs = func_kwargs or {}

        # Use the specified scheduler or default to the first one
        if queue_name is None:
            queue_name = random.choice(list(self._queues.keys()))
        elif queue_name not in self._queues:
            queue_name_new = random.choice(list(self._queues.keys()))
            logger.warning(f"Queue '{queue_name}' not found, using '{queue_name_new}'")
            queue_name = queue_name_new

        scheduler = self._schedulers[queue_name]

        if cron:
            schedule = scheduler.cron(
                cron_string=cron,
                func=func,
                args=func_args,
                kwargs=func_kwargs,
                id=schedule_id,
                repeat=repeat,  # Infinite by default
                result_ttl=int(result_ttl.total_seconds()) if result_ttl else None,
                ttl=int(ttl.total_seconds()) if ttl else None,
                use_local_time_zone=use_local_time_zone,
                queue_name=queue_name,
                meta={"cron": cron},
                **schedule_kwargs,
            )
            logger.info(
                f"Scheduled job {schedule.id} ({func.__name__}) on queue '{queue_name}' with cron '{get_description(cron)}'"
            )

        if interval:
            schedule = scheduler.schedule(
                scheduled_time=dt.datetime.now(dt.timezone.utc),
                func=func,
                args=func_args,
                kwargs=func_kwargs,
                interval=interval,
                id=schedule_id,
                repeat=repeat,  # Infinite by default
                result_ttl=int(result_ttl.total_seconds()) if result_ttl else None,
                ttl=int(ttl.total_seconds()) if ttl else None,
                queue_name=queue_name,
                meta={"interval": interval},
            )
            logger.info(
                f"Scheduled job {schedule.id} ({func.__name__}) on queue '{queue_name}' with interval '{precisedelta(interval)}'"
            )

        return schedule

    def _get_schedule_queue_name(self, schedule: str | Job) -> str | None:
        """
        Get the queue name for a schedule.

        Args:
            schedule: Schedule ID or Job object

        Returns:
            str | None: Queue name if found, None otherwise
        """
        schedule_id = schedule if isinstance(schedule, str) else schedule.id
        for queue_name in self.schedule_ids:
            if schedule_id in self.schedule_ids[queue_name]:
                return queue_name
        return None

    def get_schedules(
        self, queue_name: str | list[str] | None = None
    ) -> dict[str, list[Job]]:
        """
        Get all schedules.

        Args:
            queue_name: Optional name of the queue to get schedules from.
                        If None, gets schedules from all queues.

        Returns:
            list: List of scheduled jobs
        """
        if queue_name is None:
            queue_name = list(self._schedulers.keys())
        elif isinstance(queue_name, str):
            queue_name = [queue_name]
        schedules = {
            queue_name: list(self._schedulers[queue_name].get_jobs())
            for queue_name in queue_name
        }
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
        """
        Get the result of a schedule.

        Args:
            schedule: Schedule ID or Job object

        Returns:
            Any: Result of the schedule
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
        """
        Get the latest result of a schedule.

        Args:
            schedule: Schedule ID or Job object
            delete_result: Whether to delete the result after fetching

        Returns:
            Any: Result of the schedule
        """

        result = self._backend.get_schedule_result(schedule=schedule)[-1]

        if delete_result:
            self.delete_schedule(schedule)

        return result

    def get_schedule_result(
        self, schedule: str | Job, index: int | list[str] | slice | str
    ) -> list[Result]:
        """
        Get the result of a schedule at a specific index.

        Args:
            schedule: Schedule ID or Job object
            index: Index of the result to retrieve

        Returns:
            list[Result]: Result of the schedule at the specified index
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
        """
        Cancel a schedule.

        Args:
            schedule (str | Job): ID or Job object of the schedule to cancel

        Returns:
            bool: True if the schedule was canceled, False otherwise

        """
        queue_name = self._get_schedule_queue_name(schedule=schedule)
        if queue_name is None:
            logger.error(f"Schedule {schedule} not found in any queue")
            return False
       
        if schedule is None:
            logger.error(f"Schedule {schedule} not found in queue '{queue_name}'")
            return False

        self._schedulers[queue_name].cancel(schedule)
        logger.info(f"Canceled schedule {schedule.id} from queue '{queue_name}'")
        return True

    def cancel_all_schedules(self) -> None:
        """Cancel all schedules from all queues."""
        for queue_name, scheduler in self._schedulers.items():
            for job in scheduler.get_jobs():
                scheduler.cancel(job.id)
            logger.info(f"Canceled all schedules from queue '{queue_name}'")
        logger.info("Canceled all schedules from all queues.")

    @property
    def schedules(self):
        """
        Get all schedules from all schedulers.
        """
        schedules = self.get_schedules()

        return schedules

    @property
    def schedule_ids(self):
        """
        Get all schedule IDs from all schedulers.
        """
        schedule_ids = {}
        for queue_name in self.schedules:
            schedule_ids[queue_name] = [
                schedule.id
                for schedule in self.get_schedules(queue_name=queue_name)[queue_name]
            ]
        return schedule_ids
