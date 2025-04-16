"""
RQSchedulerBackend implementation for FlowerPower using RQ and rq-scheduler.

This module implements the scheduler backend using RQ (Redis Queue) and rq-scheduler.
"""

import datetime as dt
import multiprocessing
import platform
import sys
import uuid
from typing import Any, Callable

from loguru import logger
from rq import Queue
from rq_scheduler import Scheduler

from ...cfg import Config
from ...fs import AbstractFileSystem
from ..base import BaseTrigger, BaseWorker
from .setup import RQBackend
from .trigger import RQTrigger
from .utils import show_jobs, show_schedules

if sys.platform == "darwin" and platform.machine() == "arm64":
    try:
        # Check if the start method has already been set to avoid errors
        if multiprocessing.get_start_method(allow_none=True) is None:
            multiprocessing.set_start_method("fork")
            logger.info("Set multiprocessing start method to 'fork' for macOS ARM.")
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
        **cfg_updates: dict[str, Any],
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
            **cfg_upates: Configuration updates for the scheduler
        """
        super().__init__(
            name=name,
            base_dir=base_dir,
            backend=backend,
            fs=fs,
            storage_options=storage_options,
            **cfg_updates,
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
        backend_cfg = getattr(self.cfg, "rq_backend", None)
        if not backend_cfg or not getattr(backend_cfg, "backend", None):
            logger.error(
                "Backend configuration is missing in project.worker.rq_backend.backend."
            )
            raise RuntimeError("Backend configuration is missing.")
        backend_cfg = backend_cfg.backend
        try:
            self._backend = RQBackend(
                type=backend_cfg.type or "redis",
                uri=backend_cfg.uri,
                host=backend_cfg.host,
                port=backend_cfg.port,
                database=backend_cfg.database,
                username=backend_cfg.username,
                password=backend_cfg.password,
                ssl=backend_cfg.ssl,
            )
            logger.info(
                f"RQ backend setup successful (type: {self._backend.type}, uri: {self._backend.uri})"
            )
        except Exception as exc:
            logger.exception(
                f"Failed to set up RQ backend (type: {getattr(self._backend, 'type', None)}, uri: {getattr(self._backend, 'uri', None)}): {exc}"
            )
            raise RuntimeError(f"Failed to set up RQ backend: {exc}") from exc

    def _get_items(
        self, as_dict: bool = False, queue_name: str | None = None, getter=None
    ) -> list:
        """
        Helper to get jobs or schedules as objects or dicts, optionally for a specific queue.
        """
        all_items = []
        if queue_name is not None:
            if getter and queue_name in getter:
                all_items = getter[queue_name].get_jobs()
            else:
                logger.warning(f"Queue '{queue_name}' not found")
        else:
            if getter:
                for obj in getter.values():
                    all_items.extend(obj.get_jobs())
        if as_dict:
            return [
                item.to_dict() if hasattr(item, "to_dict") else item.__dict__
                for item in all_items
            ]
        return all_items

    def get_schedules(
        self, as_dict: bool = False, queue_name: str | None = None
    ) -> list:
        """
        Get all schedules.

        Args:
            as_dict: Whether to return schedules as dictionaries
            queue_name: Optional name of the queue to get schedules from.
                        If None, gets schedules from all queues.

        Returns:
            list: List of scheduled jobs
        """
        return self._get_items(as_dict, queue_name, getter=self._schedulers)

    def get_jobs(self, as_dict: bool = False, queue_name: str | None = None) -> list:
        """
        Get all jobs in the queue.

        Args:
            as_dict: Whether to return jobs as dictionaries
            queue_name: Optional name of the queue to get jobs from.
                        If None, gets jobs from all queues.

        Returns:
            list: List of jobs
        """
        return self._get_items(as_dict, queue_name, getter=self._queues)

    def add_job(
        self,
        func: Callable,
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        job_id: str | None = None,
        result_ttl: float | dt.timedelta = 0,
        queue_name: str | None = None,
        **job_kwargs,
    ) -> str:
        """
        Add a job for immediate execution.

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            job_id: Optional job ID
            result_ttl: How long to keep the result (seconds or timedelta)
            queue_name: Name of the queue to use (defaults to first queue)
            **job_kwargs: Additional job parameters

        Returns:
            str: Job ID
        """
        job_id = job_id or str(uuid.uuid4())
        if isinstance(result_ttl, (int, float)):
            result_ttl = dt.timedelta(seconds=result_ttl)
        args = args or ()
        kwargs = kwargs or {}
        if queue_name is None:
            queue_name = next(iter(self._queues))
        elif queue_name not in self._queues:
            logger.warning(
                f"Queue '{queue_name}' not found, using '{next(iter(self._queues))}'"
            )
            queue_name = next(iter(self._queues))

        queue = self._queues[queue_name]

        job = queue.enqueue(
            func,
            args=args,
            kwargs=kwargs,
            job_id=job_id,
            result_ttl=int(result_ttl.total_seconds()) if result_ttl else None,
            **job_kwargs,
        )
        logger.info(f"Enqueued job {job_id} ({func.__name__}) on queue '{queue_name}'")
        return job.id

    def add_schedule(
        self,
        func: Callable,
        trigger: BaseTrigger,
        schedule_id: str | None = None,
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        queue_name: str | None = None,
        **schedule_kwargs,
    ) -> str:
        """
        Schedule a job for repeated execution.

        Args:
            func: Function to execute
            trigger: RQTrigger instance
            schedule_id: Optional schedule ID
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            queue_name: Name of the queue to use (defaults to first queue)
            **schedule_kwargs: Additional schedule parameters

        Returns:
            str: Schedule ID
        """
        schedule_id = schedule_id or str(uuid.uuid4())
        args = args or ()
        kwargs = kwargs or {}

        # Use the specified scheduler or default to the first one
        if queue_name is None:
            queue_name = next(iter(self._schedulers))
        elif queue_name not in self._schedulers:
            logger.warning(
                f"Queue '{queue_name}' not found, using '{next(iter(self._schedulers))}'"
            )
            queue_name = next(iter(self._schedulers))

        scheduler = self._schedulers[queue_name]

        # Get trigger parameters
        if isinstance(trigger, RQTrigger):
            trigger_params = trigger.get_trigger_instance(**schedule_kwargs)
        else:
            trigger_params = schedule_kwargs

        # Support cron and interval triggers
        if trigger_params.get("type") == "cron":
            cron = trigger_params.get("crontab")
            job = scheduler.cron(
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
            job = scheduler.schedule(
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
            f"Scheduled job {schedule_id} ({func.__name__}) on queue '{queue_name}' with trigger {trigger_params}"
        )
        return job.id

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
        found = False
        # Try to cancel the schedule in all schedulers
        for queue_name, scheduler in self._schedulers.items():
            try:
                scheduler.cancel(schedule_id)
                logger.info(f"Removed schedule {schedule_id} from queue '{queue_name}'")
                found = True
            except Exception as e:
                # Only log as debug because it might just not be in this scheduler
                logger.debug(
                    f"Schedule {schedule_id} not found in queue '{queue_name}': {e}"
                )

        if not found:
            logger.error(
                f"Failed to remove schedule {schedule_id}: not found in any queue"
            )
            raise RuntimeError(
                f"Failed to remove schedule {schedule_id}: not found in any queue"
            )

        return True

    def remove_all_schedules(self) -> None:
        """Remove all schedules from all queues."""
        for queue_name, scheduler in self._schedulers.items():
            for job in scheduler.get_jobs():
                scheduler.cancel(job.id)
            logger.info(f"Removed all schedules from queue '{queue_name}'")
        logger.info("Removed all schedules from all queues.")

    def get_job_result(self, job_id: str) -> Any:
        """
        Get the result of a job.

        Args:
            job_id: ID of the job

        Returns:
            Any: Result of the job
        """
        # self._queues
        raise NotImplementedError("get_job_result is not implemented in RQWorker.")
        # pass

    def show_schedules(self) -> None:
        """Display the schedules in a user-friendly format."""
        for queue_name, scheduler in self._schedulers.items():
            print(f"Schedules in queue '{queue_name}':")
            show_schedules(scheduler)
            print("\n")

    def show_jobs(self) -> None:
        """Display the jobs in a user-friendly format."""
        for queue_name, queue in self._queues.items():
            print(f"Jobs in queue '{queue_name}':")
            show_jobs(queue)
            print("\n")

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
            # Start the worker pool process
            import threading

            def run_pool():
                worker_pool.start(burst=False)

            self._pool_thread = threading.Thread(target=run_pool, daemon=True)
            self._pool_thread.start()
            logger.info(
                f"Worker pool started with {num_workers} workers across queues: {queue_names_str} in background"
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

            if hasattr(self, "_pool_thread") and self._pool_thread.is_alive():
                # Wait for the pool thread to finish (with timeout)
                self._pool_thread.join(timeout=10)
                if self._pool_thread.is_alive():
                    logger.warning(
                        "Worker pool thread did not terminate within timeout"
                    )

            self._worker_pool = None

            if hasattr(self, "_pool_thread"):
                self._pool_thread = None
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
