from abc import ABC, abstractmethod
from typing import Callable, Any, Dict, Union
from datetime import datetime, timedelta

class TaskQueueInterface(ABC):
    @abstractmethod
    def define_task(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Defines a task with a common signature."""
        pass

    @abstractmethod
    def enqueue_task(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Enqueues a task for immediate execution."""
        pass

    @abstractmethod
    def schedule_task_at(self, task: Callable[..., Any], run_time: datetime, *args: Any, **kwargs: Any) -> None:
        """Schedules a task for execution at a specific datetime."""
        pass

    @abstractmethod
    def schedule_task_in(self, task: Callable[..., Any], delay: timedelta, *args: Any, **kwargs: Any) -> None:
        """Schedules a task for execution after a specified delay."""
        pass

    @abstractmethod
    def schedule_task_cron(self, task: Callable[..., Any], cron_string: str, *args: Any, **kwargs: Any) -> None:
        """Schedules a task for execution based on a cron expression."""
        pass

    @abstractmethod
    def schedule_task_interval(self, task: Callable[..., Any], interval: timedelta, *args: Any, **kwargs: Any) -> None:
        """Schedules a task for execution at a recurring interval."""
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Any:
        """Retrieves a task by its ID."""
        pass

    @abstractmethod
    def worker_start(self, num_workers: int = 1) -> None:
        """Starts worker processes."""
        pass

    @abstractmethod
    def worker_stop(self) -> None:
        """Stops worker processes."""
        pass

    @abstractmethod
    def worker_monitor(self) -> Any:
        """Monitors worker processes."""
        pass


    