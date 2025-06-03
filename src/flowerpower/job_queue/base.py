"""
Base scheduler interface for FlowerPower.

This module defines the abstract base classes for scheduling operations
that can be implemented by different backend providers (APScheduler, RQ, etc.).
"""

import abc
import importlib
import os
import posixpath
import sys
import urllib.parse
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

if importlib.util.find_spec("sqlalchemy"):
    from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
else:
    create_async_engine = None
    AsyncEngine = TypeVar("AsyncEngine")

from ..cfg import ProjectConfig
from ..fs import AbstractFileSystem, get_filesystem
# from ..utils.misc import update_config_from_dict
from ..settings import BACKEND_PROPERTIES, CACHE_DIR, CONFIG_DIR, PIPELINES_DIR


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
    def default_username(self) -> str:
        return self.properties.get("default_username", "")

    @property
    def default_password(self) -> str:
        return self.properties.get("default_password", "")

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
        # Handle host and port
        host = host or self.default_host
        port = port or self.default_port
        database = database or self.default_database
        username = username or self.default_username
        password = password or self.default_password

        # components: List[str] = []
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

        port_part = f":{port}"  # if port is not None else self.default_port

        # Special handling for SQLite and memory types
        if self.is_sqlite_type or self.is_memory_type:
            if self.is_sqlite_type:
                if database:
                    return f"{uri_prefix}{database}"
                else:
                    return f"{uri_prefix}"
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
                    query_params.append(
                        f"tlsCertificateKeyFile={urllib.parse.quote(cert_file)}"
                    )
            elif self.is_redis_type:
                if not verify_ssl:
                    query_params.append("ssl_cert_reqs=none")
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
                    query_params.append(
                        f"tls_cert_file={urllib.parse.quote(cert_file)}"
                    )
                if key_file:
                    query_params.append(f"tls_key_file={urllib.parse.quote(key_file)}")
            elif self.is_mqtt_type:
                query_params.append("tls=true")
                if ca_file:
                    query_params.append(f"tls_ca_file={urllib.parse.quote(ca_file)}")
                if cert_file:
                    query_params.append(
                        f"tls_cert_file={urllib.parse.quote(cert_file)}"
                    )
                if key_file:
                    query_params.append(f"tls_key_file={urllib.parse.quote(key_file)}")

        # Compose query string if Any params exist
        query_string = ""
        if query_params:
            query_string = "?" + "&".join(query_params)

        return f"{base_uri}{query_string}"


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
    ca_file: str | None = None
    cert_file: str | None = None
    key_file: str | None = None
    verify_ssl: bool = False
    _kwargs: dict = field(default_factory=dict)
    _sqla_engine: AsyncEngine | None = (
        None  # SQLAlchemy async engine instance for SQL backends
    )
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
                ca_file=self.ca_file,
                cert_file=self.cert_file,
                key_file=self.key_file,
                verify_ssl=self.verify_ssl,
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


class BaseJobQueueManager:
    """
    Abstract base class for scheduler workers (APScheduler, RQ, etc.).
    Defines the required interface for all scheduler backends.

    Can be used as a context manager:

    ```python
    with RQManager(name="test") as manager:
        manager.add_job(job1)
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
        if hasattr(self, "_worker") and self._worker is not None:
            self.stop_worker()
        if hasattr(self, "_scheduler") and self._scheduler is not None:
            self.stop_scheduler()
        return False  # Don't suppress exceptions

    def __init__(
        self,
        type: str | None = None,
        name: str | None = None,
        base_dir: str | None = None,
        backend: BaseBackend | None = None,
        storage_options: dict = None,
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
            cfg_override: Configuration overrides for the worker
        """
        self.name = name or ""
        self._base_dir = base_dir or str(Path.cwd())
        # self._storage_options = storage_options or {}
        self._backend = backend
        self._type = type
        self._pipelines_dir = kwargs.get("pipelines_dir", PIPELINES_DIR)
        self._cfg_dir = CONFIG_DIR

        if storage_options is not None:
            cached = True
            cache_storage = posixpath.join(
                posixpath.expanduser(CACHE_DIR), self._base_dir.split("://")[-1]
            )
            os.makedirs(cache_storage, exist_ok=True)
        else:
            cached = False
            cache_storage = None
        if not fs:
            fs = get_filesystem(
                self._base_dir,
                storage_options=storage_options,
                cached=cached,
                cache_storage=cache_storage,
            )
        self._fs = fs
        self._storage_options = storage_options or fs.storage_options

        self._add_modules_path()
        self._load_config()

    def _load_config(self) -> None:
        """Load the configuration.

        Args:
            cfg_updates: Configuration updates to apply
        """
        self.cfg = ProjectConfig.load(
            base_dir=self._base_dir, job_queue_type=self._type, fs=self._fs
        ).job_queue

    def _add_modules_path(self):
        """
        Sync the filesystem.

        Returns:
            None
        """
        if self._fs.is_cache_fs:
            self._fs.sync_cache()
            project_path = self._fs._mapper.directory
            modules_path = posixpath.join(project_path, self._pipelines_dir)

        else:
            # Use the base directory directly if not using cache
            project_path = self._fs.path
            modules_path = posixpath.join(project_path, self._pipelines_dir)

        if project_path not in sys.path:
            sys.path.insert(0, project_path)

        if modules_path not in sys.path:
            sys.path.insert(0, modules_path)
