"""
Base scheduler interface for FlowerPower.

This module defines the abstract base classes for scheduling operations
that can be implemented by different backend providers (APScheduler, RQ, etc.).
"""

import abc
import datetime as dt
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union

from sqlalchemy.ext.asyncio import AsyncEngine

from ..fs import AbstractFileSystem, get_filesystem

# Define backend properties in a dictionary for easier maintenance
BACKEND_PROPERTIES = {
    "postgresql": {
        "uri_prefix": "postgresql+asyncpg://",
        "default_port": 5432,
        "default_host": "localhost",
        "default_database": "postgres",
        "is_sqla_type": True,
    },
    "mysql": {
        "uri_prefix": "mysql+aiomysql://",
        "default_port": 3306,
        "default_host": "localhost",
        "default_database": "msql",
        "is_sqla_type": True,
    },
    "sqlite": {
        "uri_prefix": "sqlite+aiosqlite://",
        "default_port": None,
        "default_host": "",
        "default_database": "",
        "is_sqla_type": True,
        "is_sqlite_type": True,
    },
    "mongodb": {
        "uri_prefix": "mongodb://",
        "default_port": 27017,
        "default_host": "localhost",
        "default_database": "admin",
    },
    "mqtt": {
        "uri_prefix": "mqtt://",
        "default_port": 1883,
        "default_host": "localhost",
        "default_database": "mqtt",
    },
    "redis": {
        "uri_prefix": "redis://",
        "default_port": 6379,
        "default_host": "localhost",
        "default_database": "0",
    },
    "nats_kv": {
        "uri_prefix": "nats://",
        "default_port": 4222,
        "default_host": "localhost",
        "default_database": "default",
    },
    "memory": {
        "uri_prefix": "memory://",
        "default_port": None,
        "default_host": "",
        "default_database": "",
    },
}


class BackendType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    MQTT = "mqtt"
    REDIS = "redis"
    NATS_KV = "nats_kv"
    MEMORY = "memory"

    @property
    def properties(self):
        return BACKEND_PROPERTIES[self.value]

    @property
    def uri_prefix(self) -> str:
        return self.properties.get("uri_prefix", "")

    @property
    def default_port(self) -> int | None:
        return self.properties.get("default_port")

    @property
    def default_host(self) -> str:
        return self.properties.get("default_host", "")

    @property
    def default_database(self) -> str:
        return self.properties.get("default_database", "")

    @property
    def is_sqla_type(self) -> bool:
        return self.properties.get("is_sqla_type", False)

    @property
    def is_mongodb_type(self) -> bool:
        return self.value == "mongodb"

    @property
    def is_mqtt_type(self) -> bool:
        return self.value == "mqtt"

    @property
    def is_redis_type(self) -> bool:
        return self.value == "redis"

    @property
    def is_nats_kv_type(self) -> bool:
        return self.value == "nats_kv"

    @property
    def is_memory_type(self) -> bool:
        return self.value == "memory"

    @property
    def is_sqlite_type(self) -> bool:
        return self.value == "sqlite"

    def gen_uri(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str | None = None,
        ssl: bool = False,
    ) -> str:
        import urllib.parse
        from typing import List

        # Build components conditionally
        components: List[str] = []
        
        # Get the appropriate URI prefix based on backend type and SSL setting
        if self.is_redis_type:
            uri_prefix = "rediss://" if ssl else "redis://"
        elif self.is_nats_kv_type:
            uri_prefix = "nats+tls://" if ssl else "nats://"
        elif self.is_mqtt_type:
            uri_prefix = "mqtts://" if ssl else "mqtt://"
            # For MQTT, use standard SSL port if not specified
            if ssl and port == 1883:
                port = 8883
        else:
            uri_prefix = self.uri_prefix

        # Handle authentication
        if username and password:
            auth = f"{urllib.parse.quote(username)}:{urllib.parse.quote(password)}@"
        elif username:
            auth = f"{urllib.parse.quote(username)}@"
        elif password:
            auth = f":{urllib.parse.quote(password)}@"
        else:
            auth = ""

        # Handle host and port
        host = host or self.default_host
        port_part = f":{port}" if port is not None else ""

        # Special handling for SQLite and memory types
        if self.is_sqlite_type or self.is_memory_type:
            if self.is_sqlite_type and database:
                return f"{uri_prefix}{database}"
            return "memory://"

        # Build path component
        database = database or self.default_database
        path = f"/{database}" if database else ""

        # Construct base URI
        base_uri = f"{uri_prefix}{auth}{host}{port_part}{path}"

        # Add SSL parameters if needed
        if ssl and not (self.is_sqlite_type or self.is_memory_type or
                       self.is_nats_kv_type or self.is_redis_type or self.is_mqtt_type):
            sep = "&" if "?" in base_uri else "?"
            if self.value == "postgresql":
                return f"{base_uri}{sep}ssl=verify-full"  # More secure default
            elif self.value == "mysql":
                return f"{base_uri}{sep}ssl=true"
            elif self.is_mongodb_type:
                return f"{base_uri}{sep}ssl=true"  # Removed tlsAllowInvalidCertificates

        return base_uri


@dataclass(slots=True)
class BaseBackend:
    type: BackendType | str | None = None
    uri: str | None = None
    username: str | None = None
    password: str | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None
    ssl: bool = False
    _kwargs: dict = field(default=dict)
    _sqla_engine: AsyncEngine | None = None  # SQLAlchemy async engine instance for SQL backends
    _client: Any | None = None  # Native client instance for non-SQL backends

    def __post_init__(self):
        if self.type is None:
            self.type = "memory"

        elif isinstance(self.type, str):
            try:
                self.type = BackendType[self.type.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid backend type: {self.type}. Valid types: {[bt.value for bt in BackendType]}"
                )

        if not self.uri:
            self.uri = self.type.gen_uri(
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
                ssl=self.ssl,
            )

        # Setup is handled by backend-specific implementations

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BaseBackend":
        return cls(**d)


class BaseTrigger(abc.ABC):
    """
    Abstract base class for schedule triggers.

    A trigger determines when a scheduled job should be executed.
    """

    def __init__(self, trigger_type: str):
        self.trigger_type = trigger_type

    @abc.abstractmethod
    def get_trigger_instance(self, **kwargs) -> Any:
        """
        Get the backend-specific trigger instance.

        Args:
            **kwargs: Keyword arguments specific to the trigger type

        Returns:
            Any: A backend-specific trigger instance
        """
        pass


class BaseWorker(abc.ABC):
    """
    Abstract base class for scheduler workers (APScheduler, RQ, etc.).
    Defines the required interface for all scheduler backends.

    Can be used as a context manager:

    ```python
    with RQWorker(name="test") as worker:
        worker.add_job(job1)
    ```
    """

    def __enter__(self):
        """Context manager entry - returns self for use in with statement."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures workers are stopped."""
        if hasattr(self, "_worker_process") and self._worker_process is not None:
            self.stop_worker()
        if hasattr(self, "_worker_pool") and self._worker_pool is not None:
            self.stop_worker_pool()
        return False  # Don't suppress exceptions

    def __init__(
        self,
        name: str | None = None,
        base_dir: str | None = None,
        backend: BaseBackend | None = None,
        storage_options: dict[str, Any] = None,
        fs: AbstractFileSystem | None = None,
        **kwargs,
    ):
        """
        Initialize the APScheduler backend.

        Args:
            name: Name of the scheduler
            base_dir: Base directory for the FlowerPower project
            backend: APSBackend instance with data store and event broker
            storage_options: Storage options for filesystem access
            fs: Filesystem to use
            **kwargs: Additional parameters
        """
        self.name = name or ""
        self._base_dir = base_dir or str(Path.cwd())
        self._storage_options = storage_options or {}
        self._backend = backend

        if fs is None:
            fs = get_filesystem(self._base_dir, **(self._storage_options or {}))
        self._fs = fs

        self._conf_path = "conf"
        self._pipelines_path = "pipelines"

        # Add pipelines path to sys.path
        sys.path.append(self._pipelines_path)

    @abc.abstractmethod
    def add_job(
        self,
        func: Callable,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        result_ttl: Union[float, dt.timedelta] = 0,
        **job_kwargs,
    ) -> str:
        """
        Add a one-off job to the scheduler.
        Returns the job ID.
        """
        pass

    @abc.abstractmethod
    def add_schedule(
        self,
        func: Callable,
        trigger: "BaseTrigger",
        id: Optional[str] = None,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        **schedule_kwargs,
    ) -> str:
        """
        Add a scheduled (recurring) job to the scheduler.
        Returns the schedule ID.
        """
        pass

    @abc.abstractmethod
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a scheduled job by its schedule ID.
        Returns True if removed, False if not found.
        """
        pass

    @abc.abstractmethod
    def remove_all_schedules(self) -> None:
        """
        Remove all scheduled jobs.
        """
        pass

    @abc.abstractmethod
    def get_job_result(self, job_id: str) -> Any:
        """
        Retrieve the result of a completed job by its job ID.
        """
        pass

    @abc.abstractmethod
    def get_schedules(self, as_dict: bool = False) -> list:
        """
        Get a list of all scheduled jobs.
        """
        pass

    @abc.abstractmethod
    def get_jobs(self, as_dict: bool = False) -> list:
        """
        Get a list of all jobs (scheduled and one-off).
        """
        pass

    @abc.abstractmethod
    def show_schedules(self) -> None:
        """
        Print or log all current schedules.
        """
        pass

    @abc.abstractmethod
    def show_jobs(self) -> None:
        """
        Print or log all current jobs.
        """
        pass

    @abc.abstractmethod
    def start_worker(self, background: bool = False) -> None:
        """
        Start the worker process/thread.

        Args:
            background: Whether to run the worker in the background or in the current process
        """
        pass

    @abc.abstractmethod
    def stop_worker(self) -> None:
        """
        Stop the worker process/thread.
        """
        pass

    @abc.abstractmethod
    def start_worker_pool(
        self, num_workers: int = None, background: bool = True
    ) -> None:
        """
        Start a pool of worker processes to handle jobs in parallel.

        Args:
            num_workers: Number of worker processes to start (defaults to CPU count)
            background: Whether to run the workers in the background
        """
        pass

    @abc.abstractmethod
    def stop_worker_pool(self) -> None:
        """
        Stop all worker processes in the pool.
        """
        pass
