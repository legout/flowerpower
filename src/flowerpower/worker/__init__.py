from typing import Any, Optional

from ..fs import AbstractFileSystem
from ..utils.logging import setup_logging
from .apscheduler import APSBackend, APSWorker
from .base import BaseBackend, BaseWorker
from ._huey import HueyWorker
from .rq import RQBackend, RQWorker

setup_logging()


class Worker:
    """A factory class for creating worker instances for job scheduling and execution.

    This class provides a unified interface for creating different types of worker instances
    (RQ, APScheduler, Huey) based on the specified backend type. Each worker type provides
    different capabilities for job scheduling and execution.

    The worker instances handle:
    - Job scheduling and execution
    - Background task processing
    - Job queue management
    - Result storage and retrieval

    Example:
        ```python
        # Create an RQ worker
        rq_worker = Worker(
            type="rq",
            name="my_worker",
            log_level="DEBUG"
        )

        # Create an APScheduler worker with custom backend
        from flowerpower.worker.apscheduler import APSBackend
        backend_config = APSBackend(
            data_store={"type": "postgresql", "uri": "postgresql+asyncpg://user:pass@localhost/db"},
            event_broker={"type": "redis", "uri": "redis://localhost:6379/0"}
        )
        aps_worker = Worker(
            type="apscheduler",
            name="scheduler",
            backend=backend_config
        )

        # Create a Huey worker with filesystem access
        from fsspec.implementations.local import LocalFileSystem
        huey_worker = Worker(
            type="huey",
            name="file_processor",
            fs=LocalFileSystem()
        )
        ```
    """

    def __new__(
        cls,
        type: str = "rq",
        name: str | None = None,
        base_dir: str | None = None,
        backend: BaseBackend | None = None,
        storage_options: Optional[dict[str, Any]] = None,
        fs: AbstractFileSystem | None = None,
        log_level: str | None = None,
        **kwargs,
    ) -> BaseWorker:
        """Create a new worker instance based on the specified backend type.

        Args:
            type: The type of worker to create. Valid values are:
                - "rq": Redis Queue worker for Redis-based job queuing
                - "apscheduler": APScheduler worker for advanced job scheduling
                - "huey": Huey worker for lightweight task queueing. Note: This
            name: Name of the worker instance. Used for identification in logs
                and monitoring.
            base_dir: Base directory for worker files and configuration. Defaults
                to current working directory if not specified.
            backend: Pre-configured backend instance. If not provided, one will
                be created based on configuration settings.
            storage_options: Options for configuring filesystem storage access.
                Example: {"mode": "async", "root": "/tmp", "protocol": "s3"}
            fs: Custom filesystem implementation for storage operations.
                Example: S3FileSystem, LocalFileSystem, etc.
            log_level: Logging level for the worker. Valid values are:
                "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            **kwargs: Additional configuration options passed to the specific
                worker implementation.

        Returns:
            BaseWorker: An instance of the specified worker type (RQWorker,
                APSWorker, or HueyWorker).

        Raises:
            ValueError: If an invalid worker type is specified.
            ImportError: If required dependencies for the chosen worker type
                are not installed.
            RuntimeError: If worker initialization fails due to configuration
                or connection issues.

        Example:
            ```python
            # Basic RQ worker
            worker = Worker(type="rq", name="basic_worker")

            # APScheduler with custom logging and storage
            worker = Worker(
                type="apscheduler",
                name="scheduler",
                base_dir="/app/data",
                storage_options={"mode": "async"},
                log_level="DEBUG"
            )

            # Huey worker with custom backend
            # !! The Huey worker is still a work in progress. Do not use yet. !!
            from flowerpower.worker import Backend
            backend = Backend("huey", redis_url="redis://localhost:6379/0")
            worker = Worker(
                type="huey",
                name="task_processor",
                backend=backend
            )
            ```
        """
        if type == "rq":
            return RQWorker(
                name=name,
                base_dir=base_dir,
                backend=backend,
                storage_options=storage_options,
                fs=fs,
                log_level=log_level,
                **kwargs,
            )
        elif type == "apscheduler":
            return APSWorker(
                name=name,
                base_dir=base_dir,
                backend=backend,
                storage_options=storage_options,
                fs=fs,
                log_level=log_level,
                **kwargs,
            )
        elif type == "huey":
            return HueyWorker(name, base_dir, backend, storage_options, fs, **kwargs)
        else:
            raise ValueError(
                f"Invalid backend type: {type}. Valid types: ['rq', 'apscheduler', 'huey']"
            )


class Backend:
    """A factory class for creating backend instances for different worker types.

    This class provides a unified interface for creating backend instances that handle
    the storage, queuing, and event management for different worker types. Each backend
    type provides specific implementations for:
    - Job storage and persistence
    - Queue management
    - Event handling and communication
    - Result storage

    Example:
        ```python
        # Create RQ backend with Redis
        rq_backend = Backend(
            worker_type="rq",
            uri="redis://localhost:6379/0",
            queues=["high", "default", "low"]
        )

        # Create APScheduler backend with PostgreSQL and Redis
        aps_backend = Backend(
            worker_type="apscheduler",
            data_store={
                "type": "postgresql",
                "uri": "postgresql+asyncpg://user:pass@localhost/db"
            },
            event_broker={
                "type": "redis",
                "uri": "redis://localhost:6379/0"
            }
        )
        ```
    """

    def __new__(
        cls,
        worker_type: str,
        **kwargs,
    ) -> BaseBackend:
        """Create a new backend instance based on the specified worker type.

        Args:
            worker_type: The type of backend to create. Valid values are:
                - "rq": Redis Queue backend using Redis
                - "apscheduler": APScheduler backend supporting various databases
                    and event brokers
            **kwargs: Backend-specific configuration options:
                For RQ:
                    - uri (str): Redis connection URI
                    - queues (list[str]): List of queue names
                    - result_ttl (int): Time to live for results in seconds
                For APScheduler:
                    - data_store (dict): Data store configuration
                    - event_broker (dict): Event broker configuration
                    - cleanup_interval (int): Cleanup interval in seconds
                    - max_concurrent_jobs (int): Maximum concurrent jobs

        Returns:
            BaseBackend: An instance of RQBackend or APSBackend depending on
                the specified worker type.

        Raises:
            ValueError: If an invalid worker type is specified.
            RuntimeError: If backend initialization fails due to configuration
                or connection issues.

        Example:
            ```python
            # Create RQ backend
            rq_backend = Backend(
                worker_type="rq",
                uri="redis://localhost:6379/0",
                queues=["high", "default", "low"],
                result_ttl=3600
            )

            # Create APScheduler backend with PostgreSQL and Redis
            aps_backend = Backend(
                worker_type="apscheduler",
                data_store={
                    "type": "postgresql",
                    "uri": "postgresql+asyncpg://user:pass@localhost/db",
                    "schema": "scheduler"
                },
                event_broker={
                    "type": "redis",
                    "uri": "redis://localhost:6379/0"
                },
                cleanup_interval=300,
                max_concurrent_jobs=10
            )
            ```
        """
        if worker_type == "rq":
            return RQBackend(**kwargs)
        elif worker_type == "apscheduler":
            return APSBackend(**kwargs)
        else:
            raise ValueError(
                f"Invalid backend type: {worker_type}. Valid types: ['rq', 'apscheduler']"
            )


__all__ = [
    "Worker",
    "RQWorker",
    "APSWorker",
    "HueyWorker",
    "Backend",
    "RQBackend",
    "APSBackend",
]
