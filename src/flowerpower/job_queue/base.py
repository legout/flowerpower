"""
Base scheduler interface for FlowerPower.

This module defines the abstract base classes for scheduling operations
that can be implemented by different backend providers (RQ, etc.).
"""

import importlib
import os
import posixpath
import sys
import urllib.parse
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar, Optional, List, Dict, Union

if importlib.util.find_spec("sqlalchemy"):
    from sqlalchemy.ext.asyncio import AsyncEngine
else:
    AsyncEngine = TypeVar("AsyncEngine")

from ..cfg import ProjectConfig
from ..cfg.pipeline.run import RetryConfig
from ..fs import AbstractFileSystem, get_filesystem, get_storage_options_and_fs, get_protocol
from ..settings import BACKEND_PROPERTIES, CACHE_DIR, CONFIG_DIR, PIPELINES_DIR

# Import unified job queue models
from src.flowerpower.job_queue.models import (
    JobStatus,
    JobInfo,
    WorkerInfo,
    QueueInfo,
    WorkerStats,
    BackendCapabilities,
)


class BackendType(str, Enum):
    POSTGRESQL = "postgresql"
    # MYSQL = "mysql"
    SQLITE = "sqlite"
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


class BaseJobQueueManager(ABC):
    """
    Abstract base class for pluggable job queue managers.
    Defines the required interface for all job queue backends.

    Can be used as a context manager.

    All methods must be implemented by concrete backends.
    """

    def __init__(
        self,
        type: str | None = None,
        name: str | None = None,
        base_dir: str | None = None,
        backend: BaseBackend | None = None,
        storage_options: dict = None,
        fs: AbstractFileSystem | None = None,
    ):
        """
        Initialize the BaseBackend.

        Args:
            type (str | None): The type of backend to use (e.g., "redis", "sqlite").
            name (str | None): The name of the job queue.
            base_dir (str | None): The base directory for the project.
            backend (BaseBackend | None): An instance of BaseBackend to use.
            storage_options (dict): Additional storage options for the filesystem.
            fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use.

        """
        self.name = name or ""
        self._base_dir = base_dir or str(Path.cwd())
        self._backend = backend
        self._type = type
        cached = True if storage_options is not None or get_protocol(self._base_dir)!= "file" else False
        self._storage_options, self._fs = get_storage_options_and_fs(
            base_dir=self._base_dir,
            storage_options=storage_options,
            fs=fs,
            cached=cached
        )

        self._load_config()

    def _load_config(self) -> None:
        """Load the configuration.

        Args:
            cfg_updates: Configuration updates to apply
        """
        self._cfg = ProjectConfig.load(
            base_dir=self._base_dir, job_queue_type=self._type, fs=self._fs
        ).job_queue



    @property
    def cfg(self) -> ProjectConfig:
        """Get the current project configuration."""
        if not hasattr(self, "_cfg"):
            self._load_config()
        return self._cfg


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

    @property
    @abstractmethod
    def capabilities(self) -> BackendCapabilities:
        """
        Returns the capabilities of this backend.
        """
        pass

    # --- Job Management ---

    @abstractmethod
    def enqueue_job(self, job: JobInfo) -> str:
        """
        Enqueue a job for execution.

        Args:
            job (JobInfo): The job to enqueue.

        Returns:
            str: The job ID assigned by the backend.
        """
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[JobInfo]:
        """
        Retrieve information about a job by its ID.

        Args:
            job_id (str): The job ID.

        Returns:
            Optional[JobInfo]: The job information, or None if not found.
        """
        pass

    @abstractmethod
    def list_jobs(
        self, status: Optional[JobStatus] = None, queue: Optional[str] = None
    ) -> List[JobInfo]:
        """
        List jobs, optionally filtered by status or queue.

        Args:
            status (Optional[JobStatus]): Filter by job status.
            queue (Optional[str]): Filter by queue name.

        Returns:
            List[JobInfo]: List of jobs.
        """
        pass

    @abstractmethod
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job if it is running or queued.

        Args:
            job_id (str): The job ID.

        Returns:
            bool: True if the job was cancelled, False otherwise.
        """
        pass

    # @abstractmethod
    # def retry_job(self, job_id: str) -> bool:
    #     """
    #     Retry a failed job.

    #     Args:
    #         job_id (str): The job ID.

    #     Returns:
    #         bool: True if the retry was scheduled, False otherwise.
    #     """
    #     pass

    # --- Worker Management ---

    @abstractmethod
    def list_workers(self) -> List[WorkerInfo]:
        """
        List all workers known to the backend.

        Returns:
            List[WorkerInfo]: List of worker information.
        """
        pass

    @abstractmethod
    def get_worker(self, worker_id: str) -> Optional[WorkerInfo]:
        """
        Retrieve information about a worker.

        Args:
            worker_id (str): The worker ID.

        Returns:
            Optional[WorkerInfo]: The worker information, or None if not found.
        """
        pass

    # @abstractmethod
    # def get_worker_stats(self, worker_id: str) -> Optional[WorkerStats]:
    #     """
    #     Retrieve statistics for a worker.

    #     Args:
    #         worker_id (str): The worker ID.

    #     Returns:
    #         Optional[WorkerStats]: The worker statistics, or None if not available.
    #     """
    #     pass

    @abstractmethod
    def stop_worker(self, worker_id: Optional[str] = None) -> None:
        """
        Stop a worker or all workers.

        Args:
            worker_id (Optional[str]): The worker ID to stop, or None to stop all.
        """
        pass

    # --- Queue Management ---

    @abstractmethod
    def list_queues(self) -> List[QueueInfo]:
        """
        List all queues managed by the backend.

        Returns:
            List[QueueInfo]: List of queue information.
        """
        pass

    @abstractmethod
    def get_queue(self, queue_name: str) -> Optional[QueueInfo]:
        """
        Retrieve information about a queue.

        Args:
            queue_name (str): The queue name.

        Returns:
            Optional[QueueInfo]: The queue information, or None if not found.
        """
        pass

    # --- Pipeline/Legacy Methods (for compatibility) ---

    @abstractmethod
    def enqueue_pipeline(
        self,
        pipeline_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        result_ttl: Optional[int] = 120,
        run_at: Any = None,
        run_in: Any = None,
        final_vars: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        cache: Union[bool, Dict] = False,
        executor: Union[str, Dict, Any, None] = None,
        with_adapter: Union[Dict, Any, None] = None,
        adapter_cfg: Union[Dict, Any, None] = None,
        hamilton_adapters: Optional[Dict[str, Any]] = None,
        reload: bool = False,
        log_level: Optional[str] = None,
        retry: Union[Dict, RetryConfig, None] = None,
        **kwargs,
    ) -> str:
        """
        Enqueue a pipeline for execution via the job queue.
        Returns the job ID.
        """
        pass

    @abstractmethod
    def run_pipeline_sync(
        self,
        pipeline_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        final_vars: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        cache: Union[bool, Dict] = False,
        executor: Union[str, Dict, Any, None] = None,
        with_adapter: Union[Dict, Any, None] = None,
        adapter_cfg: Union[Dict, Any, None] = None,
        hamilton_adapters: Optional[Dict[str, Any]] = None,
        reload: bool = False,
        log_level: Optional[str] = None,
        retry: Union[Dict, RetryConfig, None] = None,
        **kwargs,
    ) -> Any:
        """
        Run a pipeline synchronously and return its result.
        """
        pass

    @abstractmethod
    def schedule_pipeline(
        self,
        pipeline_name: str,
        cron: Optional[str] = None,
        interval: int | None = None,
        date: str | None = None,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        cache: bool | dict = False,
        executor: Union[str, Dict, Any, None] = None,
        with_adapter: Union[Dict, Any, None] = None,
        adapter_cfg: Union[Dict, Any, None] = None,
        hamilton_adapters: Optional[Dict[str, Any]] = None,
        reload: bool = False,
        log_level: str | None = None,
        retry: dict | RetryConfig | None = None,
        schedule_id: str | None = None,
        overwrite: bool = False,
        **kwargs,
    ):
        """Schedule a pipeline for execution using the configured job queue."""
        pass
