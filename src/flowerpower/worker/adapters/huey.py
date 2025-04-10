from typing import Callable, Any, Dict
from datetime import datetime, timedelta
from flowerpower.worker.base import TaskQueueInterface
from flowerpower.worker.config import HueyConfig
from huey import Huey, SqliteHuey, RedisHuey
from urllib.parse import urlparse

class HueyAdapter(TaskQueueInterface):
    """
    Adapter for Huey implementing the TaskQueueInterface.
    """
    def __init__(self, config: HueyConfig):
        self.config = config
        self.huey = self._initialize_huey()
        # Store mapping from original function to Huey task instance
        self._task_registry: Dict[Callable[..., Any], Any] = {}

    def _initialize_huey(self) -> Huey:
        """Initializes the Huey instance based on the URL scheme."""
        parsed_url = urlparse(self.config.url)
        if parsed_url.scheme in ('redis', 'rediss'):
            # Extract host, port, db from URL if needed, Huey handles URL directly
            return RedisHuey(name=self.config.huey_name, url=self.config.url, immediate=self.config.immediate)
        elif parsed_url.scheme == 'sqlite':
            # Huey expects just the path for SqliteHuey
            db_path = parsed_url.path
            # Handle absolute paths like sqlite:////path/to/db by removing leading slashes if more than one
            while db_path.startswith('/') and len(db_path) > 1 and db_path[1] == '/':
                 db_path = db_path[1:]
            # Remove single leading slash for absolute paths like sqlite:///path/to/db
            if db_path.startswith('/') and len(db_path) > 1:
                 db_path = db_path[1:]

            return SqliteHuey(name=self.config.huey_name, filename=db_path, immediate=self.config.immediate)
        # Add other Huey backends here if needed (e.g., FileHuey)
        else:
            raise ValueError(f"Unsupported Huey URL scheme: {parsed_url.scheme}")

    def define_task(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Defines a task using the Huey instance's task decorator.
        Stores the mapping from the original function to the Huey task.
        """
        if func in self._task_registry:
            return self._task_registry[func] # Return existing Huey task if already defined

        # Decorate the function using the initialized Huey instance
        huey_task = self.huey.task()(func)
        self._task_registry[func] = huey_task
        return huey_task # Return the Huey task instance

    def _get_huey_task(self, task_func: Callable[..., Any]) -> Any:
        """Retrieves the Huey task instance for a given original function."""
        huey_task = self._task_registry.get(task_func)
        if not huey_task:
            # If not found, try defining it dynamically.
            # This handles cases where the adapter might be re-initialized
            # without redefining tasks explicitly through the manager.
            # Consider if raising an error for undefined tasks is preferable.
            huey_task = self.define_task(task_func)
            # Alternative: raise ValueError(f"Task {task_func.__name__} was not defined using define_task.")
        return huey_task

    def enqueue_task(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Enqueues a task for immediate execution by calling the Huey task function.
        """
        huey_task = self._get_huey_task(task)
        huey_task(*args, **kwargs)

    def schedule_task_at(self, task: Callable[..., Any], run_time: datetime, *args: Any, **kwargs: Any) -> None:
        """
        Schedules a task for execution at a specific datetime using Huey's schedule method with eta.
        """
        huey_task = self._get_huey_task(task)
        if not hasattr(huey_task, 'schedule'):
             raise AttributeError(f"The Huey task '{task.__name__}' does not have a schedule method. Is it defined correctly?")
        huey_task.schedule(args=args, kwargs=kwargs, eta=run_time)

    def schedule_task_in(self, task: Callable[..., Any], delay: timedelta, *args: Any, **kwargs: Any) -> None:
        """
        Schedules a task for execution after a specified delay using Huey's schedule method with delay.
        """
        huey_task = self._get_huey_task(task)
        if not hasattr(huey_task, 'schedule'):
             raise AttributeError(f"The Huey task '{task.__name__}' does not have a schedule method. Is it defined correctly?")
        # Huey's delay is in seconds
        huey_task.schedule(args=args, kwargs=kwargs, delay=int(delay.total_seconds()))

    def schedule_task_cron(self, task: Callable[..., Any], cron_string: str, *args: Any, **kwargs: Any) -> None:
        """
        Schedules a task for execution based on a cron expression.
        Not directly supported dynamically by Huey after initial definition.
        """
        raise NotImplementedError(
            "Huey defines periodic tasks (cron/interval) via decorators (@huey.periodic_task) "
            "at definition time, not dynamically via a method call."
        )

    def schedule_task_interval(self, task: Callable[..., Any], interval: timedelta, *args: Any, **kwargs: Any) -> None:
        """
        Schedules a task for execution at a recurring interval.
        Not directly supported dynamically by Huey after initial definition.
        """
        raise NotImplementedError(
            "Huey defines periodic tasks (cron/interval) via decorators (@huey.periodic_task) "
            "at definition time, not dynamically via a method call."
        )

    def get_task(self, task_id: str) -> Any:
        """
        Retrieves a task by its ID.
        Huey primarily returns Result objects on enqueue/schedule. Retrieving arbitrary
        tasks by ID later is not a standard API feature and would require backend-specific querying.
        """
        # Huey's API focuses on the Result handle returned by enqueue/schedule.
        # There isn't a direct equivalent to RQ's Job.fetch(id).
        raise NotImplementedError(
            "Retrieving Huey tasks by ID after scheduling is not directly supported via a standard API."
        )

    def worker_start(self, num_workers: int = 1) -> None:
        """
        Starts worker processes.
        Not implemented: Huey workers are typically started via the 'huey_consumer' CLI.
        """
        raise NotImplementedError(
            "Starting Huey workers must be done via the 'huey_consumer' CLI."
        )

    def worker_stop(self) -> None:
        """
        Stops worker processes.
        Not implemented: Huey workers are typically stopped externally (e.g., SIGINT/SIGTERM).
        """
        raise NotImplementedError(
            "Stopping Huey workers must be done externally (e.g., by terminating the process)."
        )

    def worker_monitor(self) -> Any:
        """
        Monitors worker processes.
        Not implemented: Monitoring Huey workers typically involves external tools or checking logs.
        """
        raise NotImplementedError(
            "Worker monitoring is not directly implemented in this adapter. Check logs or use external tools."
        )