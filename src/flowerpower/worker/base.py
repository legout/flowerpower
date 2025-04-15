"""
Base scheduler interface for FlowerPower.

This module defines the abstract base classes for scheduling operations
that can be implemented by different backend providers (APScheduler, RQ, etc.).
"""
import urllib.parse
import abc
import datetime as dt
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
from sqlalchemy.ext.asyncio import AsyncEngine

from ..fs import AbstractFileSystem, get_filesystem
from ..cfg import Config
from ..utils.misc import update_config_from_dict


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
    def default_port(self):
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
        ca_file: str | None = None,
        cert_file: str | None = None,
        key_file: str | None = None,
        verify_ssl: bool = False,
    ) -> str:
        import urllib.parse
 
        #components: List[str] = []

        # Get the appropriate URI prefix based on backend type and SSL setting
        if self.is_redis_type:
            uri_prefix = "rediss://" if ssl else "redis://"
        elif self.is_nats_kv_type:
            uri_prefix = "nats+tls://" if ssl else "nats://"
        elif self.is_mqtt_type:
            uri_prefix = "mqtts://" if ssl else "mqtt://"
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
        port = port or self.default_port
        database = database or self.default_database

        port_part = f":{port}" #if port is not None else self.default_port

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

        # Prepare query parameters for SSL files
        query_params: list[str] = []

        if ssl:
            # Always add ssl query parameter if ssl=True
            if self.value == "postgresql":
                query_params.append("ssl=verify-full" if verify_ssl else "ssl=allow")
                if ca_file:
                    query_params.append(f"sslrootcert={urllib.parse.quote(ca_file)}")
                if cert_file:
                    query_params.append(f"sslcert={urllib.parse.quote(cert_file)}")
                if key_file:
                    query_params.append(f"sslkey={urllib.parse.quote(key_file)}")
            elif self.value == "mysql":
                query_params.append("ssl=true")
                if ca_file:
                    query_params.append(f"ssl_ca={urllib.parse.quote(ca_file)}")
                if cert_file:
                    query_params.append(f"ssl_cert={urllib.parse.quote(cert_file)}")
                if key_file:
                    query_params.append(f"ssl_key={urllib.parse.quote(key_file)}")
            elif self.is_mongodb_type:
                query_params.append("tls=true")
                if ca_file:
                    query_params.append(f"tlsCAFile={urllib.parse.quote(ca_file)}")
                if cert_file and key_file:
                    query_params.append(f"tlsCertificateKeyFile={urllib.parse.quote(cert_file)}")
            elif self.is_redis_type:
                query_params.append("ssl=true")
                if ca_file:
                    query_params.append(f"ssl_ca_certs={urllib.parse.quote(ca_file)}")
                if cert_file:
                    query_params.append(f"ssl_certfile={urllib.parse.quote(cert_file)}")
                if key_file:
                    query_params.append(f"ssl_keyfile={urllib.parse.quote(key_file)}")
            elif self.is_nats_kv_type:
                query_params.append("tls=true")
                if ca_file:
                    query_params.append(f"tls_ca_file={urllib.parse.quote(ca_file)}")
                if cert_file:
                    query_params.append(f"tls_cert_file={urllib.parse.quote(cert_file)}")
                if key_file:
                    query_params.append(f"tls_key_file={urllib.parse.quote(key_file)}")
            elif self.is_mqtt_type:
                query_params.append("tls=true")
                if ca_file:
                    query_params.append(f"tls_ca_file={urllib.parse.quote(ca_file)}")
                if cert_file:
                    query_params.append(f"tls_cert_file={urllib.parse.quote(cert_file)}")
                if key_file:
                    query_params.append(f"tls_key_file={urllib.parse.quote(key_file)}")

        # Compose query string if Any params exist
        query_string = ""
        if query_params:
            query_string = "?" + "&".join(query_params)

        return f"{base_uri}{query_string}"



def build_url(
    type: str,
    host: str | None = None,
    port: int | None = None,
    username: str| None  = None,
    password: str| None  = None,
    database: str| None  = None,
    ssl: bool = False,
    ca_file: str| None  = None,
    cert_file: str| None  = None,
    key_file: str| None  = None,
    verify_ssl: bool = True,  # Controls certificate validation
) -> str:
    """
    Generate a connection URL for various database types.
    
    Args:
        type: Database type (postgresql, mysql, sqlite, mongodb, redis, nats, mqtt, memory)
        host: Database host
        port: Database port
        username: Authentication username
        password: Authentication password
        database: Database name
        ssl: Whether to use SSL
        ca_file: CA certificate file path
        cert_file: Client certificate file path
        key_file: Client key file path
        verify_ssl: Whether to verify SSL certificates (default: True)
        
    Returns:
        Connection URL string
    """
    # Set default values based on database type
    default_ports = {
        "postgresql": 5432,
        "mysql": 3306,
        "mongodb": 27017,
        "redis": 6379,
        "nats": 4222,
        "mqtt": 1883 if not ssl else 8883,
    }

    if host is None and type.lower() not in ["memory", "sqlite"]:
        host = "localhost"
    if port is None and type.lower() in default_ports:
        port = default_ports[type.lower()]


    type = type.lower()
    
    # Handle memory database type (SQLite in-memory)
    if type == "memory":
        return "sqlite+aiosqlite:///:memory:"
    
    # Build authentication part of URL if credentials are provided
    auth = ""
    if username:
        auth = urllib.parse.quote(username)
        if password:
            auth += f":{urllib.parse.quote(password)}"
        auth += "@"
    
    # Build the base URL with host and port
    base_url = ""
    if host:
        base_url = host
        if port:
            base_url += f":{port}"
    
    # Build query parameters for SSL options
    query_params: list[str] = []
    
    # Protocol prefix for NATS with SSL
    nats_prefix = "nats+tls" if ssl and type == "nats" else "nats"
    
    if ssl:
        if type == "postgresql":
            # For PostgreSQL, use the appropriate SSL mode
            if verify_ssl:
                if ca_file:
                    query_params.append("ssl=verify-ca")
                else:
                    query_params.append("ssl=verify-full")
            else:
                query_params.append("ssl=allow")
            
            if ca_file:
                query_params.append(f"sslrootcert={ca_file}")
            if cert_file:
                query_params.append(f"sslcert={cert_file}")
            if key_file:
                query_params.append(f"sslkey={key_file}")
                
        elif type == "mysql":
            query_params.append("ssl=true")
            
            if ca_file:
                query_params.append(f"ssl_ca={ca_file}")
            if cert_file:
                query_params.append(f"ssl_cert={cert_file}")
            if key_file:
                query_params.append(f"ssl_key={key_file}")
            if not verify_ssl:
                query_params.append("ssl_verify_cert=false")
                
        elif type == "mongodb":
            query_params.append("tls=true")
            
            if ca_file:
                query_params.append(f"tlsCAFile={ca_file}")
            if cert_file and key_file:
                query_params.append(f"tlsCertificateKeyFile={cert_file}")
            if not verify_ssl:
                query_params.append("tlsAllowInvalidCertificates=true")
                
        elif type == "redis":
            # For Redis, we use rediss:// instead of redis:// for SSL
            type = "rediss"
            
            if not verify_ssl:
                query_params.append("ssl_cert_reqs=none")
            if ca_file:
                query_params.append(f"ssl_ca_certs={ca_file}")
            if cert_file:
                query_params.append(f"ssl_certfile={cert_file}")
            if key_file:
                query_params.append(f"ssl_keyfile={key_file}")
                
        elif type == "nats":
            # NATS with SSL uses nats+tls:// protocol (handled in prefix)
            if not verify_ssl:
                query_params.append("tls_verify=false")
            if ca_file:
                query_params.append(f"tls_ca_file={ca_file}")
            if cert_file:
                query_params.append(f"tls_cert_file={cert_file}")
            if key_file:
                query_params.append(f"tls_key_file={key_file}")
                
        elif type == "mqtt":
            query_params.append("tls=true")
            
            if not verify_ssl:
                query_params.append("tls_insecure=true")
            if ca_file:
                query_params.append(f"tls_ca_file={ca_file}")
            if cert_file:
                query_params.append(f"tls_cert_file={cert_file}")
            if key_file:
                query_params.append(f"tls_key_file={key_file}")
    
    # Construct query string
    query_string = ""
    if query_params:
        query_string = "?" + "&".join(query_params)
    
    # Generate URL based on database type
    if type == "postgresql":
        db_path = f"{database}" if database else ""
        return f"postgresql+asyncpg://{auth}{base_url}/{db_path}{query_string}"
    
    elif type == "mysql":
        db_path = f"{database}" if database else ""
        return f"mysql+aiomysql://{auth}{base_url}/{db_path}{query_string}"
    
    elif type == "sqlite":
        db_path = f"{database}" if database else ""
        return f"sqlite+aiosqlite:///{db_path}{query_string}"
    
    elif type == "mongodb":
        db_path = f"{database}" if database else ""
        return f"mongodb://{auth}{base_url}/{db_path}{query_string}"
    
    elif type in ["redis", "rediss"]:
        db_number = f"/{database}" if database and database.isdigit() else ""
        return f"{type}://{auth}{base_url}{db_number}{query_string}"
    
    elif type == "nats":
        return f"{nats_prefix}://{auth}{base_url}{query_string}"
    
    elif type == "mqtt":
        return f"mqtt://{auth}{base_url}{query_string}"
    
    else:
        raise ValueError(f"Unsupported database type: {type}")

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
    _kwargs: dict = field(default_factory=dict)
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
    def from_dict(cls, d: dict) -> "BaseBackend":
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
        storage_options: dict = None,
        fs: AbstractFileSystem | None = None,
        **cfg_updates: dict[str, Any],

    ):
        """
        Initialize the APScheduler backend.

        Args:
            name: Name of the scheduler
            base_dir: Base directory for the FlowerPower project
            backend: APSBackend instance with data store and event broker
            storage_options: Storage options for filesystem access
            fs: Filesystem to use
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

        self._load_config(**cfg_updates)

        # Add pipelines path to sys.path
        sys.path.append(self._pipelines_path)


    def _load_config(self, **cfg_updates) -> None:
        """Load the configuration.
        
        Args:
            cfg_updates: Configuration updates to apply
        """
        cfg = Config.load(base_dir=self._base_dir, fs=self._fs)
        self.cfg = update_config_from_dict(cfg.project.worker, cfg_updates)


    @abc.abstractmethod
    def add_job(
        self,
        func: callable,
        args: tuple | None = None,
        kwargs: dict | None = None,
        id: str | None = None,
        result_ttl: float | dt.timedelta = 0,
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
        func: callable,
        trigger: "BaseTrigger",
        id: str | None = None,
        args: tuple | None = None,
        kwargs: dict | None = None,
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
