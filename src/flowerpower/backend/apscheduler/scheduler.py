"""
APScheduler implementation for FlowerPower scheduler.

This module implements the scheduler interfaces using APScheduler as the backend.
"""

import datetime as dt
import importlib.util
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from fsspec.spec import AbstractFileSystem
from loguru import logger

# Check if APScheduler is available
if not importlib.util.find_spec("apscheduler"):
    raise ImportError(
        "APScheduler is not installed. Please install it using `pip install "
        "'apscheduler>4.0.0a1'`, 'conda install apscheduler4' or `pip install flowerpower[apscheduler]`"
    )

from apscheduler import Scheduler
from apscheduler.executors.async_ import AsyncJobExecutor
from apscheduler.executors.subprocess import ProcessPoolJobExecutor
from apscheduler.executors.thread import ThreadPoolJobExecutor


from ...cfg import Config
from ...fs import get_filesystem
from .setup.datastore import setup_data_store, APSDataStore
from .setup.eventbroker import setup_event_broker, APSEventBroker
from .utils import display_jobs, display_schedules

from ..base import BaseDataStore, BaseEventBroker, BaseScheduler, BaseTrigger
from .trigger import APSchedulerTrigger

# Patch pickle if needed
try:
    from ...utils.monkey import patch_pickle
    patch_pickle()
except Exception as e:
    logger.warning(f"Failed to patch pickle: {e}")


class APSchedulerBackend(BaseScheduler):
    """Implementation of BaseScheduler using APScheduler."""
    
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
        Initialize the APScheduler backend.
        
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
        
        #self._sync_fs()
        self._load_config()
        
        # Set up data store
        if not data_store:
            self._setup_data_store()
        else:
            self._data_store = data_store._data_store if isinstance(data_store, APSDataStore) else data_store
        
        # Set up event broker
        if not event_broker:
            self._setup_event_broker()
        else:
            self._event_broker = event_broker._event_broker if isinstance(event_broker, APSEventBroker) else event_broker
        
        # Set up job executors
        self._setup_job_executors()
        
        # Initialize APScheduler
        super_kwargs = {
            "data_store": self._data_store,
            "event_broker": self._event_broker,
            "job_executors": self._job_executors,
            "identity": self.name,
            "logger": logger,
            "cleanup_interval": self.cfg.project.worker.cleanup_interval,
            "max_concurrent_jobs": self.cfg.project.worker.max_concurrent_jobs,
        }
        super_kwargs.update(kwargs)
        
        self._scheduler = Scheduler(**super_kwargs)
        
        # Add pipelines path to sys.path
        sys.path.append(self._pipelines_path)
    
    # def _sync_fs(self) -> None:
    #     """Sync the filesystem."""
    #     if self._fs.is_cache_fs:
    #         self._fs.sync()
        
    #     modules_path = posixpath.join(self._fs.path, self._pipelines_path)
    #     if modules_path not in sys.path:
    #         sys.path.append(modules_path)
    
    def _load_config(self) -> None:
        """Load the configuration."""
        self.cfg = Config.load(base_dir=self._base_dir, fs=self._fs)
    
    def _setup_data_store(self) -> None:
        """Set up the data store."""
        self._data_store, self._sqla_engine = setup_data_store(
            type=self.cfg.project.worker.data_store.get("type", "memory"),
            engine_or_uri=self.cfg.project.worker.data_store.get("uri", None),
            schema=self.cfg.project.worker.data_store.get("schema", "flowerpower"),
            username=self.cfg.project.worker.data_store.get("username", None),
            password=self.cfg.project.worker.data_store.get("password", None),
            ssl=self.cfg.project.worker.data_store.get("ssl", False),
            **self.cfg.project.worker.data_store.get("kwargs", {})
        )
    
    def _setup_event_broker(self) -> None:
        """Set up the event broker."""
        self._event_broker = setup_event_broker(
            type=self.cfg.project.worker.event_broker.get("type", "memory"),
            uri=self.cfg.project.worker.event_broker.get("uri", None),
            sqla_engine=getattr(self, "_sqla_engine", None),
            host=self.cfg.project.worker.event_broker.get("host", None),
            port=self.cfg.project.worker.event_broker.get("port", 0),
            username=self.cfg.project.worker.event_broker.get("username", None),
            password=self.cfg.project.worker.event_broker.get("password", None),
        )
    
    def _setup_job_executors(self) -> None:
        """Set up job executors."""
        self._job_executors = {
            "async": AsyncJobExecutor(),
            "threadpool": ThreadPoolJobExecutor(),
            "processpool": ProcessPoolJobExecutor(),
        }
    
    def start_worker(self, background: bool = False) -> None:
        """
        Start a worker.
        
        Args:
            background: Whether to run in the background
        """
        if background:
            self._scheduler.start_in_background()
        else:
            self._scheduler.run_until_stopped()
    
    def stop_worker(self) -> None:
        """Stop the worker."""
        self._scheduler.stop()
    
    def add_job(
        self, 
        func: Callable, 
        args: Optional[Tuple] = None, 
        kwargs: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        result_ttl: Union[float, dt.timedelta] = 0,
        **job_kwargs
    ) -> str:
        """
        Add a job for immediate execution.
        
        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            id: Optional job ID
            result_expiration_time: How long to keep the result
            **job_kwargs: Additional job parameters
            
        Returns:
            str: Job ID
        """
        job_executor = job_kwargs.pop("job_executor", "threadpool")
        
        # Convert result_expiration_time to datetime.timedelta if it's not already
        if isinstance(result_ttl, (int, float)):
            result_ttl = dt.timedelta(seconds=result_ttl)
        
        id = id or str(uuid.uuid4())
        
        job = self._scheduler.add_job(
            func,
            args=args or (),
            kwargs=kwargs or {},
            #id=job_id,
            job_executor=job_executor,
            result_expiration_time=result_ttl,
            **job_kwargs
        )
        
        return job
    
    def add_schedule(
        self,
        func: Callable,
        trigger: BaseTrigger,
        id: Optional[str] = None,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        **schedule_kwargs
    ) -> str:
        """
        Schedule a job for repeated execution.
        
        Args:
            func: Function to execute
            trigger: Trigger defining when to execute the function
            id: Optional schedule ID
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            **schedule_kwargs: Additional schedule parameters
            
        Returns:
            str: Schedule ID
        """
        job_executor = schedule_kwargs.pop("job_executor", "threadpool")
        
        # Get the actual trigger instance
        if isinstance(trigger, APSchedulerTrigger):
            trigger_instance = trigger.get_trigger_instance()
        else:
            # If it's not an APSchedulerTrigger, we assume it's already a trigger instance
            trigger_instance = trigger
        
        schedule = self._scheduler.add_schedule(
            func,
            trigger=trigger_instance,
            id=id,
            args=args or (),
            kwargs=kwargs or {},
            job_executor=job_executor,
            **schedule_kwargs
        )
        
        return schedule
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a schedule.
        
        Args:
            schedule_id: ID of the schedule to remove
            
        Returns:
            bool: True if the schedule was removed, False otherwise
        """
        try:
            self._scheduler.remove_schedule(schedule_id)
            return True
        except Exception as e:
            logger.error(f"Failed to remove schedule {schedule_id}: {e}")
            return False
    
    def remove_all_schedules(self) -> None:
        """Remove all schedules."""
        for sched in self._scheduler.get_schedules():
            self._scheduler.remove_schedule(sched.id)
    
    def get_job_result(self, job_id: str) -> Any:
        """
        Get the result of a job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Any: Result of the job
        """
        return self._scheduler.get_job_result(job_id)
    
    def get_schedules(self, as_dict: bool = False) -> List[Any]:
        """
        Get all schedules.
        
        Args:
            as_dict: Whether to return schedules as dictionaries
            
        Returns:
            List[Any]: List of schedules
        """
        schedules = self._scheduler.get_schedules()
        if as_dict:
            return [sched.to_dict() for sched in schedules]
        return schedules
    
    def get_jobs(self, as_dict: bool = False) -> List[Any]:
        """
        Get all jobs.
        
        Args:
            as_dict: Whether to return jobs as dictionaries
            
        Returns:
            List[Any]: List of jobs
        """
        jobs = self._scheduler.get_jobs()
        if as_dict:
            return [job.to_dict() for job in jobs]
        return jobs
    
    def show_schedules(self) -> None:
        """Display the schedules in a user-friendly format."""
        display_schedules(self._scheduler.get_schedules())
    
    def show_jobs(self) -> None:
        """Display the jobs in a user-friendly format."""
        display_jobs(self._scheduler.get_jobs())
