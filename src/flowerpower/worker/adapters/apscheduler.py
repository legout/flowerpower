# src/flowerpower/worker/adapters/apscheduler.py

import threading
import asyncio
import uuid  # Import uuid for job IDs
import time  # Import time for sleep
from datetime import datetime, timedelta, timezone
from typing import Callable, Any, Dict, Optional

# Corrected import path:
from apscheduler._schedulers.async_ import AsyncScheduler  # Use this path
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
# Import the base interface and config
from flowerpower.worker.base import TaskQueueInterface
from src.flowerpower.worker.config import APSchedulerConfig

# Note: Ensure necessary database drivers like psycopg (for postgresql) or aiosqlite are installed.

class APSchedulerAdapter(TaskQueueInterface):
    """
    Adapter for APScheduler v4 to conform to the TaskQueueInterface.
    Runs the async scheduler in a background thread and exposes sync methods.
    """

    def __init__(self, config: APSchedulerConfig):
        self.config = config
        self._tasks: Dict[str, Callable[..., Any]] = {}  # Optional: track defined tasks if needed
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._start_loop, daemon=True)
        self._scheduler_ready = threading.Event()
        # Use correct type hint
        self._scheduler: Optional[AsyncScheduler] = None

        # Start the event loop thread first
        self._loop_thread.start()

        # Initialize scheduler in a separate thread to avoid blocking __init__
        # while waiting for the loop to be ready for scheduler start.
        init_thread = threading.Thread(target=self._init_scheduler_thread_target, daemon=True)
        init_thread.start()

        # Wait until the scheduler is initialized and started
        self._scheduler_ready.wait(timeout=10)  # Add a timeout
        if not self._scheduler_ready.is_set():
            raise TimeoutError("APScheduler failed to initialize within the timeout period.")

    def _start_loop(self):
        """Target for the event loop thread."""
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_forever()
        finally:
            self._loop.close()

    def _run_async(self, coro):
        """
        Run an async coroutine in the scheduler's event loop, synchronously.
        Ensures the loop is running and scheduler is initialized before submitting.
        """
        if not self._loop.is_running():
            raise RuntimeError("APScheduler event loop is not running.")
        # Add check before accessing self._scheduler
        if self._scheduler is None:
            raise RuntimeError("APScheduler is not initialized.")

        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            # Add a timeout to prevent indefinite blocking
            return future.result(timeout=10)
        except asyncio.TimeoutError:
            raise TimeoutError("Async operation timed out.")
        except Exception as e:
            # Log or handle other exceptions from the coroutine
            raise e  # Re-raise the exception

    def _init_scheduler_thread_target(self):
        """Target for the scheduler initialization thread."""
        try:
            # Ensure the loop is running before scheduling the async init
            while not self._loop.is_running():
                # Use time.sleep in sync context
                time.sleep(0.01)  # Short sleep to yield control

            async def _async_init():
                # Data store setup
                # Ensure the datastore URL is provided
                if not self.config.database_url:
                    raise ValueError("APScheduler requires a database_url in the configuration.")
                # FIX: Use correct parameter name for SQLAlchemyDataStore
                datastore = SQLAlchemyDataStore(engine_or_url=self.config.database_url)

                # Timezone
                tz = self.config.timezone or "UTC"

                # Jobstores (optional advanced config)
                jobstores_config = self.config.jobstores or {}

                self._scheduler = AsyncScheduler(
                    data_store=datastore,
                    # **jobstores_config # Spread jobstores config if needed, ensure compatibility
                    timezone=tz
                )
                # Start scheduler
                # Check scheduler is not None before starting
                if self._scheduler:
                    # FIX: Use start() instead of start_in_background() for v4
                    await self._scheduler.start()
                    self._scheduler_ready.set()  # Signal that scheduler is ready
                else:
                    # Should not happen if initialization logic is correct, but handle defensively
                    print("Error: Scheduler object is None after initialization.")

            # Schedule the async init function to run in the event loop
            asyncio.run_coroutine_threadsafe(_async_init(), self._loop)

        except Exception as e:
            # Log the error appropriately
            print(f"Error initializing APScheduler: {e}")
            # Optionally, signal failure or handle cleanup
            # self._scheduler_ready.set() # Or handle differently to indicate failure

    def define_task(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        APScheduler schedules callables directly. Store func if needed for lookup,
        but primarily just return it.
        """
        # Storing might be useful if you need to reference the original callable later
        self._tasks[func.__name__] = func
        return func

    def enqueue_task(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Schedule the task to run immediately using a DateTrigger.
        """
        if self._scheduler is None:
            raise RuntimeError("APScheduler is not initialized.")
        run_time = datetime.now(timezone.utc)
        # FIX: Use run_time instead of run_date
        #trigger = DateTrigger(run_time=run_time)
        job_id = kwargs.pop("job_id", None)  # Allow optional job ID override
        self._run_async(
            self._scheduler.add_job(
                func_or_task_id==task,
                #trigger=trigger,
                args=args,
                kwargs=kwargs,
                id=job_id
            )
        )

    def schedule_task_at(self, task: Callable[..., Any], run_time: datetime, *args: Any, **kwargs: Any) -> None:
        """
        Schedule the task for a specific datetime using DateTrigger.
        """
        if self._scheduler is None:
            raise RuntimeError("APScheduler is not initialized.")
        # Ensure timezone awareness, default to UTC if naive
        if run_time.tzinfo is None:
            run_time = run_time.replace(tzinfo=timezone.utc)

        # FIX: Use run_time instead of run_date
        trigger = DateTrigger(run_time=run_time)
        job_id = kwargs.pop("job_id", None)
        self._run_async(
            self._scheduler.add_schedule(
                func_or_task_id=task,
                trigger=trigger,
                args=args,
                kwargs=kwargs,
                id=job_id
            )
        )

    def schedule_task_in(self, task: Callable[..., Any], delay: timedelta, *args: Any, **kwargs: Any) -> None:
        """
        Schedule the task after a delay using DateTrigger.
        """
        if self._scheduler is None:
            raise RuntimeError("APScheduler is not initialized.")
        run_time = datetime.now(timezone.utc) + delay
        # FIX: Use run_time instead of run_date
        trigger = DateTrigger(run_time=run_time)
        job_id = kwargs.pop("job_id", None)
        self._run_async(
            self._scheduler.add_schedule(
                func_or_task_id=task,
                trigger=trigger,
                args=args,
                kwargs=kwargs,
                id=job_id
            )
        )

    def _parse_cron_string(self, cron_string: str) -> Dict[str, str]:
        """Helper to parse a standard 5 or 6 field cron string."""
        fields = cron_string.strip().split()
        if len(fields) not in [5, 6]:
            raise ValueError("Invalid cron string: must have 5 or 6 fields (minute hour day month day_of_week [year])")

        keys = ["minute", "hour", "day", "month", "day_of_week"]
        if len(fields) == 6:
            keys.append("year")

        return {keys[i]: field for i, field in enumerate(fields)}

    def schedule_task_cron(self, task: Callable[..., Any], cron_string: str, *args: Any, **kwargs: Any) -> None:
        """
        Schedule the task using a cron expression via CronTrigger.
        """
        if self._scheduler is None:
            raise RuntimeError("APScheduler is not initialized.")
        cron_kwargs = self._parse_cron_string(cron_string)
        # Pass timezone directly to CronTrigger if needed, based on APScheduler v4 API
        trigger = CronTrigger(**cron_kwargs, timezone=self.config.timezone)
        job_id = kwargs.pop("job_id", None)
        self._run_async(
            self._scheduler.add_schedule(
                func_or_task_id=task,
                trigger=trigger,
                args=args,
                kwargs=kwargs,
                id=job_id
            )
        )

    def schedule_task_interval(self, task: Callable[..., Any], interval: timedelta, *args: Any, **kwargs: Any) -> None:
        """
        Schedule the task at a recurring interval using IntervalTrigger.
        """
        if self._scheduler is None:
            raise RuntimeError("APScheduler is not initialized.")
        seconds = int(interval.total_seconds())
        if seconds <= 0:
            raise ValueError("Interval must be positive")

        # FIX: Remove timezone parameter if not supported by IntervalTrigger in v4
        trigger = IntervalTrigger(seconds=seconds)
        job_id = kwargs.pop("job_id", None)
        self._run_async(
            self._scheduler.add_schedule(
                func_or_task_id=task,
                trigger=trigger,
                args=args,
                kwargs=kwargs,
                id=job_id
            )
        )

    def get_task(self, task_id: uuid.UUID4) -> Any:
        """
        Retrieve a job's details by its ID. Returns JobInfo or None.
        """
        if self._scheduler is None:
            raise RuntimeError("APScheduler is not initialized.")
        return self._run_async(self._scheduler.get_job_result(task_id))

    def worker_start(self, num_workers: int = 1) -> None:
        """
        APScheduler runs in-process; the scheduler is started during initialization.
        This method checks if the scheduler is running.
        """
        if self._scheduler is None:
            print("Warning: APScheduler not initialized. Cannot check status.")
            return

        # FIX: Add check for _scheduler before calling is_running
        is_running = self._run_async(self._scheduler.is_running())
        if not is_running:
            print("Warning: APScheduler is initialized but not running.")
            # Optionally add logic to attempt a restart if desired, but complex.
        # Note: num_workers is not directly applicable here.

    def worker_stop(self) -> None:
        """
        Shutdown the APScheduler and stop the event loop thread.
        """
        if self._scheduler:
            print("Shutting down APScheduler...")
            try:
                # Use a timeout for shutdown
                self._run_async(self._scheduler.shutdown(wait=True))  # wait=True might be default or needed
                print("APScheduler shutdown complete.")
            except Exception as e:
                print(f"Error during APScheduler shutdown: {e}")
            finally:
                self._scheduler = None  # Mark as shut down

        # Stop the event loop thread
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        # Join the thread with a timeout
        self._loop_thread.join(timeout=5)
        if self._loop_thread.is_alive():
            print("Warning: APScheduler event loop thread did not stop gracefully.")

    def worker_monitor(self) -> Any:
        """
        Return a list of all scheduled jobs (JobInfo objects).
        """
        if self._scheduler is None:
            raise RuntimeError("APScheduler is not initialized.")
        return self._run_async(self._scheduler.get_jobs())

    def __del__(self):
        """Ensure scheduler and loop are cleaned up on object deletion."""
        # Call worker_stop which handles scheduler shutdown and loop stopping.
        self.worker_stop()