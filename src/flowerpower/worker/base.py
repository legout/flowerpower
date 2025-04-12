"""
Base scheduler interface for FlowerPower.

This module defines the abstract base classes for scheduling operations
that can be implemented by different backend providers (APScheduler, RQ, etc.).
"""

import abc
import datetime as dt

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from fsspec.spec import AbstractFileSystem

from enum import Enum
from sqlalchemy.ext.asyncio import AsyncEngine
from dataclasses import dataclass, field


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

class BaseBackendType(str, Enum):
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
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        database: str = None,
        ssl: bool = False,
    ) -> str:
        import urllib.parse

        host = host or self.default_host
        port = port or self.default_port
        database = database or self.default_database

        # Get the appropriate URI prefix based on backend type and SSL setting
        if self.is_redis_type:
            uri_prefix = "rediss://" if ssl else "redis://"
        elif self.is_nats_kv_type:
            uri_prefix = "nats+tls://" if ssl else "nats://"
        elif self.is_mqtt_type:
            uri_prefix = "mqtts://" if ssl else "mqtt://"  # Use mqtts:// for SSL
        else:
            uri_prefix = self.uri_prefix

        # Handle authentication with proper URL escaping
        auth_part = ""
        if username and password:
            quoted_username = urllib.parse.quote(username)
            quoted_password = urllib.parse.quote(password)
            auth_part = f"{quoted_username}:{quoted_password}@"
        elif username:
            quoted_username = urllib.parse.quote(username)
            auth_part = f"{quoted_username}@"
        elif password:
            quoted_password = urllib.parse.quote(password)
            auth_part = f":{quoted_password}@"

        # Generate base URI without SSL params
        if self.is_sqla_type:
            if self.is_sqlite_type:
                base_uri = f"{uri_prefix}{database}".replace("None", "")
            else:
                base_uri = (
                    f"{uri_prefix}{auth_part}{host}:{port}/{database}".replace(
                        "None", ""
                    )
                    .rstrip("/")
                    .rstrip(":")
                )
        elif self.is_mongodb_type:
            base_uri = (
                f"{uri_prefix}{auth_part}{host}:{port}/{database}".replace("None", "")
                .rstrip("/")
                .rstrip(":")
            )
        elif self.is_redis_type:
            base_uri = f"{uri_prefix}{auth_part}{host}:{port}/{database}"
        elif self.is_nats_kv_type:
            base_uri = f"{uri_prefix}{auth_part}{host}:{port}"
        elif self.is_mqtt_type:
            # For MQTT, port might change for SSL (8883 is standard for MQTT+SSL)
            mqtt_port = 8883 if ssl and port == 1883 else port
            base_uri = f"{uri_prefix}{auth_part}{host}:{mqtt_port}"
        elif self.is_memory_type:
            return "memory://"  # Memory doesn't need SSL
        else:
            raise ValueError(f"Unsupported data store type: {self}")

        # Add SSL parameters for different database types
        if ssl:
            if (
                self.is_sqlite_type
                or self.is_memory_type
                or self.is_nats_kv_type
                or self.is_redis_type
                or self.is_mqtt_type
            ):
                # SQLite doesn't use SSL
                return base_uri
            else:
                if "?" in base_uri:
                    base_uri += "&"
                else:
                    base_uri += "?"

                if self.value == "postgresql":
                    # PostgreSQL SSL parameters
                    return f"{base_uri}ssl=allow"
                elif self.value == "mysql":
                    return f"{base_uri}ssl=true"
                elif self.is_mongodb_type:
                    return f"{base_uri}ssl=true&tlsAllowInvalidCertificates=true"
                else:
                    # Default SSL parameter
                    return base_uri
        else:
            return base_uri


@dataclass(slots=True)
class BaseBackend:
    type: BaseBackendType | str | None = None
    uri: str | None = None
    schema_or_queue: str | None = "flowerpower"
    username: str | None = None
    password: str | None = None
    host: str = None
    port: int | None = None
    database: str | None = None
    ssl: bool = False
    _kwargs: dict = field(default=dict)
    _sqla_engine: AsyncEngine | None = None
    _client: any = None

    def __post_init__(self, backend_type: BaseBackendType):
        if self.type is None:
            self.type = "memory"

        elif isinstance(self.type, str):
            self.type = backend_type[self.type.upper()]

        if not self.uri:
            self.uri = self.type.gen_uri(
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
                ssl=self.ssl,
            )

        #self._validate_inputs()
        self.setup()

    @classmethod
    def from_dict(cls, d: dict[str, any]) -> "BaseBackend":
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




class BaseScheduler(abc.ABC):
    """
    Abstract base class for schedulers.

    A scheduler manages jobs and their execution schedule.
    """

    @abc.abstractmethod
    def __init__(
        self,
        name: Optional[str] = None,
        base_dir: Optional[str] = None,
        data_store: Optional[BaseDataStore] = None,
        event_broker: Optional[BaseEventBroker] = None,
        storage_options: Dict[str, Any] = None,
        fs: Optional[AbstractFileSystem] = None,
        **kwargs,
    ):
        """
        Initialize the scheduler.

        Args:
            name: The name of the scheduler
            base_dir: Base directory for the FlowerPower project
            data_store: The data store to use
            event_broker: The event broker to use
            storage_options: Storage options for filesystem access
            fs: Filesystem to use
            **kwargs: Additional backend-specific arguments
        """
        pass

    @abc.abstractmethod
    def _load_config(self) -> None:
        """Load the scheduler configuration."""
        pass

    @abc.abstractmethod
    def start_worker(self, background: bool = False) -> None:
        """
        Start a worker to process jobs.

        Args:
            background: Whether to run the worker in the background
        """
        pass

    @abc.abstractmethod
    def stop_worker(self) -> None:
        """Stop the worker."""
        pass

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
        Add a job for immediate execution.

        Args:
            func: The function to execute
            args: Positional arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            id: Optional job ID
            result_ttl: How long to keep the result
            **job_kwargs: Additional backend-specific job parameters

        Returns:
            str: The ID of the added job
        """
        pass

    @abc.abstractmethod
    def add_schedule(
        self,
        func: Callable,
        trigger: BaseTrigger,
        id: Optional[str] = None,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        **schedule_kwargs,
    ) -> str:
        """
        Add a schedule.

        Args:
            func: The function to execute
            trigger: The trigger for the schedule
            id: Optional schedule ID
            args: Positional arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            **schedule_kwargs: Additional backend-specific schedule parameters

        Returns:
            str: The ID of the added schedule
        """
        pass

    @abc.abstractmethod
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a schedule.

        Args:
            schedule_id: The ID of the schedule to remove

        Returns:
            bool: Whether the schedule was removed
        """
        pass

    @abc.abstractmethod
    def get_job_result(self, job_id: str) -> Any:
        """
        Get a job result.

        Args:
            job_id: The ID of the job

        Returns:
            Any: The result of the job execution
        """
        pass

    @abc.abstractmethod
    def get_schedules(self, as_dict: bool = False) -> List[Any]:
        """
        Get all schedules.

        Args:
            as_dict: Whether to return schedules as dictionaries

        Returns:
            List[Any]: A list of schedules
        """
        pass

    @abc.abstractmethod
    def get_jobs(self, as_dict: bool = False) -> List[Any]:
        """
        Get all jobs.

        Args:
            as_dict: Whether to return jobs as dictionaries

        Returns:
            List[Any]: A list of jobs
        """
        pass
