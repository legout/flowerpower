from typing import Callable, Any
from datetime import datetime, timedelta, timezone
from flowerpower.worker.base import TaskQueueInterface
from flowerpower.worker.config import RQConfig
import redis
import rq
from rq import Queue, job
from rq.exceptions import NoSuchJobError
from rq_scheduler import Scheduler

class RQAdapter(TaskQueueInterface):
    """
    Adapter for RQ and RQ-Scheduler implementing the TaskQueueInterface.
    """
    def __init__(self, config: RQConfig):
        self.config = config
        self.redis_conn = redis.Redis.from_url(config.redis_url)
        self.queue = Queue(config.default_queue, connection=self.redis_conn)
        self.scheduler = Scheduler(
            queue=self.queue,
            connection=self.redis_conn
        )

    def define_task(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        RQ tasks are regular callables; just return the function.
        """
        return func

    def enqueue_task(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Enqueues a task for immediate execution using RQ.
        """
        self.queue.enqueue(task, *args, **kwargs)

    def schedule_task_at(self, task: Callable[..., Any], run_time: datetime, *args: Any, **kwargs: Any) -> None:
        """
        Schedules a task for execution at a specific datetime using RQ-Scheduler.
        """
        # RQ-Scheduler expects UTC datetimes
        if run_time.tzinfo is not None:
            run_time = run_time.astimezone(timezone.utc).replace(tzinfo=None)
        self.scheduler.enqueue_at(run_time, task, *args, **kwargs)

    def schedule_task_in(self, task: Callable[..., Any], delay: timedelta, *args: Any, **kwargs: Any) -> None:
        """
        Schedules a task for execution after a specified delay using RQ-Scheduler.
        """
        self.scheduler.enqueue_in(delay, task, *args, **kwargs)

    def schedule_task_cron(self, task: Callable[..., Any], cron_string: str, *args: Any, **kwargs: Any) -> None:
        """
        Schedules a task for execution based on a cron expression using RQ-Scheduler.
        """
        self.scheduler.cron(
            cron_string=cron_string,
            func=task,
            args=args,
            kwargs=kwargs,
            queue_name=self.config.default_queue,
            timeout=self.config.default_timeout
        )

    def schedule_task_interval(self, task: Callable[..., Any], interval: timedelta, *args: Any, **kwargs: Any) -> None:
        """
        Schedules a task for execution at a recurring interval using RQ-Scheduler.
        """
        self.scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=task,
            args=args,
            kwargs=kwargs,
            interval=int(interval.total_seconds()),
            repeat=None,  # Repeat forever
            queue_name=self.config.default_queue,
            timeout=self.config.default_timeout
        )

    def get_task(self, task_id: str) -> Any:
        """
        Retrieves a task by its ID using RQ.
        """
        try:
            return job.Job.fetch(task_id, connection=self.redis_conn)
        except NoSuchJobError:
            return None

    def worker_start(self, num_workers: int = 1) -> None:
        """
        Starts worker processes.
        Not implemented: RQ workers are typically started as external processes.
        """
        raise NotImplementedError(
            "Starting RQ workers must be done via the 'rq worker' CLI or as a separate process."
        )

    def worker_stop(self) -> None:
        """
        Stops worker processes.
        Not implemented: RQ workers are typically stopped externally.
        """
        raise NotImplementedError(
            "Stopping RQ workers must be done externally (e.g., by terminating the process)."
        )

    def worker_monitor(self) -> Any:
        """
        Monitors worker processes.
        Not implemented: Monitoring is typically handled externally or via RQ's CLI/web UI.
        """
        raise NotImplementedError(
            "Worker monitoring is not implemented in this adapter. Use RQ CLI or web UI."
        )