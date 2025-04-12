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
from .setup.datastore import  APSDataStore
from .setup.eventbroker import  APSEventBroker
from .utils import display_jobs, display_schedules

from ..base import BaseDataStore, BaseEventBroker, BaseTrigger
from .trigger import APSchedulerTrigger

# Patch pickle if needed
try:
    from ...utils.monkey import patch_pickle
    patch_pickle()
except Exception as e:
    logger.warning(f"Failed to patch pickle: {e}")


class APSchedulerBackend(Scheduler):
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
            self._data_store = data_store.client if isinstance(data_store, APSDataStore) else data_store
        
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
        
        self._client = super().__init__(**super_kwargs)
        
        # Add pipelines path to sys.path
        sys.path.append(self._pipelines_path)
    
    
    def _load_config(self) -> None:
        """Load the configuration."""
        self.cfg = Config.load(base_dir=self._base_dir, fs=self._fs)
    
    def _setup_data_store(self) -> None:
        """
        Set up the data store and SQLAlchemy engine for the scheduler.

        This method initializes the data store and SQLAlchemy engine using configuration
        values. It validates configuration, handles errors, and logs the setup process.

        Raises:
            RuntimeError: If the data store setup fails due to misconfiguration or connection errors.
        """
        # Validate configuration
        data_store_cfg = getattr(self.cfg.project.worker, "data_store", None)
        if not data_store_cfg:
            logger.error("Data store configuration is missing in project.worker.data_store.")
            raise RuntimeError("Data store configuration is missing.")

        try:
            asp_datastore = APSDataStore(
                type=data_store_cfg.get("type", "memory"),
                engine_or_uri=data_store_cfg.get("uri", None),
                schema=data_store_cfg.get("schema", "flowerpower"),
                username=data_store_cfg.get("username", None),
                password=data_store_cfg.get("password", None),
                ssl=data_store_cfg.get("ssl", False),
                **data_store_cfg.get("kwargs", {})
            )
            logger.info(
                "Data store setup successful (type=%r, uri=%r)",
                data_store_cfg.get("type", "memory"),
                data_store_cfg.get("uri", None)
            )
            self._client = asp_datastore.client
            self._sqla_engine = asp_datastore.sqla_engine


        except Exception as exc:
            logger.exception(
                "Failed to set up data store (type=%r, uri=%r): %s",
                data_store_cfg.get("type", "memory"),
                data_store_cfg.get("uri", None),
                exc
            )
            raise RuntimeError(f"Failed to set up data store: {exc}") from exc
    
    def _setup_event_broker(self) -> None:
        """
        Set up the event broker for the scheduler.

        This method initializes the event broker based on configuration settings.
        It ensures the broker is properly configured and ready for use.
        Raises:
            RuntimeError: If the event broker cannot be initialized or configured.
        """
        try:
           
            # Extract event broker configuration from project settings
            event_broker_config = self.cfg.project.worker.event_broker

            # Create the event broker instance using the factory function
            aps_eventbroker = APSEventBroker(
                type=event_broker_config.get("type", "memory"),
                uri=event_broker_config.get("uri"),
                sqla_engine=getattr(self, "_sqla_engine", None),
                host=event_broker_config.get("host"),
                port=event_broker_config.get("port", 0),
                username=event_broker_config.get("username"),
                password=event_broker_config.get("password"),
            )

            # Assign the event broker client to the instance attribute
            self._event_broker = aps_eventbroker.client

            # Validate the event broker is ready for use
            if not self._event_broker.is_ready():
                raise RuntimeError("Event broker failed readiness check.")

        except Exception as e:
            # Catch-all for other initialization errors with context
            raise RuntimeError(f"Failed to set up event broker: {e}") from e
    
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
