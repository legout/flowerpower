from typing import Callable, Any, Dict
from datetime import datetime, timedelta # Added import
from flowerpower.worker.base import TaskQueueInterface
from flowerpower.worker.config import TaskQueueConfig, RQConfig, HueyConfig, APSchedulerConfig
from flowerpower.worker.adapters import RQAdapter, HueyAdapter, APSchedulerAdapter

class WorkerManager:
    def __init__(self, config: TaskQueueConfig):
        self.config = config
        if config.type == "rq":
            self.adapter = RQAdapter(RQConfig(**config.__dict__))
        elif config.type == "huey":
            self.adapter = HueyAdapter(HueyConfig(**config.__dict__))
        elif config.type == "apscheduler":
            self.adapter = APSchedulerAdapter(APSchedulerConfig(**config.__dict__))
        else:
            raise ValueError(f"Unknown task queue type: {type(config)}")

    def define_task(self, func: Callable[..., Any]) -> Callable[..., Any]:
        return self.adapter.define_task(func)

    def enqueue_task(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self.adapter.enqueue_task(func, *args, **kwargs)

    def schedule_task_at(self, func: Callable[..., Any], run_time: datetime, *args: Any, **kwargs: Any) -> None:
        """Schedules a task for execution at a specific datetime."""
        self.adapter.schedule_task_at(func, run_time, *args, **kwargs)

    def schedule_task_in(self, func: Callable[..., Any], delay: timedelta, *args: Any, **kwargs: Any) -> None:
        """Schedules a task for execution after a specified delay."""
        self.adapter.schedule_task_in(func, delay, *args, **kwargs)

    def schedule_task_cron(self, func: Callable[..., Any], cron_string: str, *args: Any, **kwargs: Any) -> None:
        """Schedules a task for execution based on a cron expression."""
        self.adapter.schedule_task_cron(func, cron_string, *args, **kwargs)

    def schedule_task_interval(self, func: Callable[..., Any], interval: timedelta, *args: Any, **kwargs: Any) -> None:
        """Schedules a task for execution at a recurring interval."""
        self.adapter.schedule_task_interval(func, interval, *args, **kwargs)

    def get_task(self, task_id: str) -> Any:
        return self.adapter.get_task(task_id)

    def worker_start(self, num_workers: int = 1) -> None:
        self.adapter.worker_start(num_workers)

    def worker_stop(self) -> None:
        self.adapter.worker_stop()

    def worker_monitor(self) -> Any:
        return self.adapter.worker_monitor()