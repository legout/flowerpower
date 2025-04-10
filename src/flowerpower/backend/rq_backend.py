"""
RQ (Redis Queue) implementation for FlowerPower scheduler.

This module implements the scheduler interfaces using RQ and RQ-Scheduler as the backend.
"""

import datetime as dt
import importlib.util
import json
import uuid
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from fsspec.spec import AbstractFileSystem
from loguru import logger

# Check if RQ and RQ-Scheduler are available
if not (importlib.util.find_spec("rq") and importlib.util.find_spec("rq_scheduler")):
    raise ImportError(
        "RQ and RQ-Scheduler are not installed. Please install them using "
        "`pip install rq rq-scheduler`, or `pip install flowerpower[rq]`"
    )

import redis
from rq import Queue, Worker
from rq.command import send_shutdown_command
from rq.job import Job as RQJob
from rq_scheduler import Scheduler as RQScheduler

import posixpath

from ..cfg import Config
from ..fs import get_filesystem
from .base import BaseDataStore, BaseEventBroker, BaseScheduler, BaseTrigger


class RQTrigger(BaseTrigger):
    """Implementation of BaseTrigger for RQ Scheduler."""
    
    def get_trigger_instance(self, **kwargs) -> Dict[str, Any]:
        """
        Get trigger parameters for RQ Scheduler.
        
        Args:
            **kwargs: Keyword arguments for the trigger
            
        Returns:
            Dict[str, Any]: A dictionary with trigger configuration
        """
        # RQ doesn't have specific trigger classes like APScheduler.
        # Instead, we'll return a dictionary with parameters that can
        # be used by RQSchedulerBackend to schedule jobs appropriately.
        
        result = {
            "type": self.trigger_type,
            **kwargs
        }
        
        # For cron triggers, handle crontab string specifically
        if self.trigger_type == "cron" and "crontab" in kwargs:
            result["crontab"] = kwargs["crontab"]
        
        return result


class RQDataStore(BaseDataStore):
    """Implementation of BaseDataStore for RQ using Redis."""
    
    def __init__(self, redis_conn=None, **kwargs):
        """
        Initialize the RQ data store.
        
        Args:
            redis_conn: Redis connection to use
            **kwargs: Additional parameters for Redis connection
        """
        if redis_conn:
            self.redis = redis_conn
        else:
            host = kwargs.get("host", "localhost")
            port = kwargs.get("port", 6379)
            db = kwargs.get("db", 0)
            password = kwargs.get("password", None)
            self.redis = redis.Redis(host=host, port=port, db=db, password=password)
        
        # Create a namespace for job results
        self.result_namespace = kwargs.get("result_namespace", "flowerpower:results")
    
    def store_job_result(self, job_id: str, result: Any, expiration_time: Optional[dt.timedelta] = None) -> None:
        """
        Store a job result in Redis.
        
        Args:
            job_id: ID of the job
            result: Result of the job execution
            expiration_time: How long to keep the result
        """
        key = f"{self.result_namespace}:{job_id}"
        
        # Serialize the result for storage
        serialized_result = json.dumps(result) if result is not None else None
        
        # Store in Redis with optional expiration
        self.redis.set(key, serialized_result)
        
        if expiration_time:
            seconds = int(expiration_time.total_seconds())
            if seconds > 0:
                self.redis.expire(key, seconds)
    
    def get_job_result(self, job_id: str) -> Any:
        """
        Get a job result from Redis.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Any: Result of the job execution
        """
        key = f"{self.result_namespace}:{job_id}"
        result = self.redis.get(key)
        
        if result:
            return json.loads(result)
        return None
    
    def close(self) -> None:
        """Close the Redis connection."""
        self.redis.close()


class RQEventBroker(BaseEventBroker):
    """Implementation of BaseEventBroker for RQ using Redis pub/sub."""
    
    def __init__(self, redis_conn=None, **kwargs):
        """
        Initialize the RQ event broker.
        
        Args:
            redis_conn: Redis connection to use
            **kwargs: Additional parameters for Redis connection
        """
        if redis_conn:
            self.redis = redis_conn
        else:
            host = kwargs.get("host", "localhost")
            port = kwargs.get("port", 6379)
            db = kwargs.get("db", 0)
            password = kwargs.get("password", None)
            self.redis = redis.Redis(host=host, port=port, db=db, password=password)
        
        # Event prefix for pub/sub channels
        self.event_prefix = kwargs.get("event_prefix", "flowerpower:events")
        
        # Store subscription callbacks
        self.subscriptions = {}
    
    def publish(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Publish an event using Redis pub/sub.
        
        Args:
            event_type: Type of the event
            event_data: Data associated with the event
        """
        channel = f"{self.event_prefix}:{event_type}"
        message = json.dumps(event_data)
        self.redis.publish(channel, message)
    
    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to an event using Redis pub/sub.
        
        This is a simplified implementation that won't work without a separate thread
        to listen for messages. For a real implementation, you would need to run a
        pubsub listener in a separate thread or use a proper Redis message queue pattern.
        
        Args:
            event_type: Type of the event
            callback: Callback to invoke when the event occurs
        """
        logger.warning(
            "RQEventBroker.subscribe is a simplified implementation. "
            "To properly listen for events, you need to implement a pubsub listener."
        )
        
        channel = f"{self.event_prefix}:{event_type}"
        self.subscriptions[channel] = callback
    
    def close(self) -> None:
        """Close the Redis connection."""
        self.redis.close()


class RQSchedulerBackend(BaseScheduler):
    """Implementation of BaseScheduler using RQ and RQ-Scheduler."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        base_dir: Optional[str] = None,
        data_store: Optional[BaseDataStore] = None,
        event_broker: Optional[BaseEventBroker] = None,
        storage_options: Dict[str, Any] = None,
        fs: Optional[AbstractFileSystem] = None,
        **kwargs
    ):
        """
        Initialize the RQ scheduler backend.
        
        Args:
            name: Name of the scheduler
            base_dir: Base directory for the FlowerPower project
            data_store: Data store to use
            event_broker: Event broker to use
            storage_options: Storage options for filesystem access
            fs: Filesystem to use
            **kwargs: Additional parameters
        """
        self.name = name or ""
        self._base_dir = base_dir or str(Path.cwd())
        self._storage_options = storage_options or {}
        
        if fs is None:
            fs = get_filesystem(self._base_dir, **(self._storage_options or {}))
        self._fs = fs
        
        self._conf_path = "conf"
        self._pipelines_path = "pipelines"
        
        self._sync_fs()
        self.load_config()
        
        # Set up Redis connection
        redis_config = self.cfg.project.worker.event_broker
        host = redis_config.get("host", "localhost")
        port = redis_config.get("port", 6379)
        db = redis_config.get("db", 0)
        password = redis_config.get("password", None)
        
        # If redis_url is provided, use it instead of host/port
        redis_url = redis_config.get("uri", None)
        if redis_url:
            self.redis_conn = redis.from_url(redis_url)
        else:
            self.redis_conn = redis.Redis(host=host, port=port, db=db, password=password)
        
        # Set up data store
        if not data_store:
            self.data_store = RQDataStore(redis_conn=self.redis_conn)
        else:
            self.data_store = data_store
        
        # Set up event broker
        if not event_broker:
            self.event_broker = RQEventBroker(redis_conn=self.redis_conn)
        else:
            self.event_broker = event_broker
        
        # Set up RQ queue and scheduler
        queue_name = self.cfg.project.worker.get("queue_name", "flowerpower")
        self.queue = Queue(queue_name, connection=self.redis_conn)
        self.scheduler = RQScheduler(connection=self.redis_conn, queue=self.queue)
        
        # Workers tracking
        self.workers = []
        
        # Add pipelines path to sys.path
        import sys
        sys.path.append(self._pipelines_path)
    
    def _sync_fs(self) -> None:
        """Sync the filesystem."""
        if self._fs.is_cache_fs:
            self._fs.sync()
        
        modules_path = posixpath.join(self._fs.path, self._pipelines_path)
        if modules_path not in sys.path:
            sys.path.append(modules_path)
    
    def load_config(self) -> None:
        """Load the configuration."""
        self.cfg = Config.load(base_dir=self._base_dir, fs=self._fs)
    
    def start_worker(self, background: bool = False) -> None:
        """
        Start a worker to process jobs.
        
        Args:
            background: Whether to run in the background
        """
        import subprocess
        
        if background:
            # Start worker in a subprocess
            cmd = ["rq", "worker", "--with-scheduler", self.queue.name]
            proc = subprocess.Popen(cmd)
            logger.info(f"Started RQ worker in background (PID: {proc.pid})")
        else:
            # Start worker in the current process (blocking)
            logger.info(f"Starting RQ worker for queue '{self.queue.name}', press Ctrl+C to stop...")
            worker = Worker([self.queue], connection=self.redis_conn)
            self.workers.append(worker)
            worker.work()
    
    def stop_worker(self) -> None:
        """Stop all workers."""
        for worker in self.workers:
            send_shutdown_command(self.redis_conn, worker.name)
        
        self.workers = []
    
    def add_job(
        self, 
        func: Callable, 
        args: Optional[Tuple] = None, 
        kwargs: Optional[Dict[str, Any]] = None,
        job_id: Optional[str] = None,
        result_expiration_time: Union[float, dt.timedelta] = 0,
        **job_kwargs
    ) -> str:
        """
        Add a job for immediate execution.
        
        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            job_id: Optional job ID
            result_expiration_time: How long to keep the result
            **job_kwargs: Additional job parameters
            
        Returns:
            str: Job ID
        """
        job_id = job_id or str(uuid.uuid4())
        
        # Convert result_expiration_time to int (seconds) if it's not already
        if isinstance(result_expiration_time, dt.timedelta):
            result_ttl = int(result_expiration_time.total_seconds())
        else:
            result_ttl = int(result_expiration_time)
        
        # Enqueue the job
        job = self.queue.enqueue(
            func,
            args=args or (),
            kwargs=kwargs or {},
            job_id=job_id,
            result_ttl=result_ttl,
            **job_kwargs
        )
        
        return job.id
    
    def add_schedule(
        self,
        func: Callable,
        trigger: BaseTrigger,
        schedule_id: Optional[str] = None,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        **schedule_kwargs
    ) -> str:
        """
        Schedule a job for repeated execution.
        
        Args:
            func: Function to execute
            trigger: Trigger defining when to execute the function
            schedule_id: Optional schedule ID
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            **schedule_kwargs: Additional schedule parameters
            
        Returns:
            str: Schedule ID
        """
        schedule_id = schedule_id or str(uuid.uuid4())
        args = args or ()
        kwargs = kwargs or {}
        
        # Get trigger configuration
        if isinstance(trigger, RQTrigger):
            trigger_config = trigger.get_trigger_instance()
        else:
            # Assume it's a dictionary with trigger configuration
            trigger_config = trigger
        
        trigger_type = trigger_config.get("type")
        
        # Handle different trigger types
        if trigger_type == "cron":
            crontab = trigger_config.get("crontab")
            if crontab:
                job = self.scheduler.cron(
                    crontab,
                    func,
                    args=args,
                    kwargs=kwargs,
                    id=schedule_id,
                    **schedule_kwargs
                )
            else:
                # Construct crontab from individual components
                minute = trigger_config.get("minute", "*")
                hour = trigger_config.get("hour", "*")
                day = trigger_config.get("day", "*")
                month = trigger_config.get("month", "*")
                day_of_week = trigger_config.get("day_of_week", "*")
                
                crontab = f"{minute} {hour} {day} {month} {day_of_week}"
                
                job = self.scheduler.cron(
                    crontab,
                    func,
                    args=args,
                    kwargs=kwargs,
                    id=schedule_id,
                    **schedule_kwargs
                )
        
        elif trigger_type == "interval":
            # Calculate interval in seconds
            seconds = 0
            if "seconds" in trigger_config:
                seconds += trigger_config["seconds"]
            if "minutes" in trigger_config:
                seconds += trigger_config["minutes"] * 60
            if "hours" in trigger_config:
                seconds += trigger_config["hours"] * 3600
            if "days" in trigger_config:
                seconds += trigger_config["days"] * 86400
            if "weeks" in trigger_config:
                seconds += trigger_config["weeks"] * 604800
            
            job = self.scheduler.schedule(
                scheduled_time=dt.datetime.utcnow(),  # Start from now
                func=func,
                args=args,
                kwargs=kwargs,
                interval=seconds,
                id=schedule_id,
                **schedule_kwargs
            )
        
        elif trigger_type == "date":
            # One-time execution at a specific date
            run_time = trigger_config.get("run_time", dt.datetime.utcnow())
            
            job = self.scheduler.schedule(
                scheduled_time=run_time,
                func=func,
                args=args,
                kwargs=kwargs,
                id=schedule_id,
                **schedule_kwargs
            )
        
        else:
            raise ValueError(f"Unsupported trigger type: {trigger_type}")
        
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
            self.scheduler.cancel(schedule_id)
            return True
        except Exception as e:
            logger.error(f"Failed to remove schedule {schedule_id}: {e}")
            return False
    
    def remove_all_schedules(self) -> None:
        """Remove all schedules."""
        for job in self.scheduler.get_jobs():
            self.scheduler.cancel(job.id)
    
    def get_job_result(self, job_id: str) -> Any:
        """
        Get the result of a job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Any: Result of the job
        """
        try:
            job = RQJob.fetch(job_id, connection=self.redis_conn)
            return job.result
        except Exception as e:
            logger.error(f"Error retrieving job result for {job_id}: {e}")
            return None
    
    def _job_to_dict(self, job):
        """Convert RQ job to dictionary format."""
        return {
            'id': job.id,
            'func_name': job.func_name,
            'args': job.args,
            'kwargs': job.kwargs,
            'scheduled_at': job.scheduled_at.isoformat() if hasattr(job, 'scheduled_at') and job.scheduled_at else None,
            'enqueued_at': job.enqueued_at.isoformat() if job.enqueued_at else None,
            'ended_at': job.ended_at.isoformat() if job.ended_at else None,
            'result': job.result,
            'status': job.get_status(),
            'interval': job.meta.get('interval') if hasattr(job, 'meta') else None,
            'cron': job.meta.get('cron') if hasattr(job, 'meta') else None
        }
    
    def get_schedules(self, as_dict: bool = False) -> List[Any]:
        """
        Get all schedules.
        
        Args:
            as_dict: Whether to return schedules as dictionaries
            
        Returns:
            List[Any]: List of schedules
        """
        schedules = self.scheduler.get_jobs()
        if as_dict:
            return [self._job_to_dict(job) for job in schedules]
        return schedules
    
    def get_jobs(self, as_dict: bool = False) -> List[Any]:
        """
        Get all jobs.
        
        Args:
            as_dict: Whether to return jobs as dictionaries
            
        Returns:
            List[Any]: List of jobs
        """
        jobs = self.queue.get_jobs()
        if as_dict:
            return [self._job_to_dict(job) for job in jobs]
        return jobs
    
    def show_schedules(self) -> None:
        """Display the schedules in a user-friendly format."""
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        table = Table(title="Scheduled Jobs")
        
        table.add_column("ID", style="cyan")
        table.add_column("Function", style="green")
        table.add_column("Schedule", style="yellow")
        table.add_column("Next Run", style="magenta")
        
        for job in self.scheduler.get_jobs():
            # Determine schedule type and format
            schedule_type = "Unknown"
            if hasattr(job, 'meta'):
                if job.meta.get('cron'):
                    schedule_type = f"Cron: {job.meta['cron']}"
                elif job.meta.get('interval'):
                    schedule_type = f"Interval: {job.meta['interval']}s"
            
            next_run = job.scheduled_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(job, 'scheduled_at') and job.scheduled_at else "Unknown"
            
            table.add_row(
                job.id,
                job.func_name,
                schedule_type,
                next_run
            )
        
        console.print(table)
    
    def show_jobs(self) -> None:
        """Display the jobs in a user-friendly format."""
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        table = Table(title="Jobs")
        
        table.add_column("ID", style="cyan")
        table.add_column("Function", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Enqueued At", style="magenta")
        table.add_column("Result", style="blue")
        
        for job in self.queue.get_jobs():
            table.add_row(
                job.id,
                job.func_name,
                job.get_status(),
                job.enqueued_at.strftime("%Y-%m-%d %H:%M:%S") if job.enqueued_at else "Unknown",
                str(job.result) if job.result else "None"
            )
        
        console.print(table)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context."""
        try:
            self.redis_conn.close()
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")
