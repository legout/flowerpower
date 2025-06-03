import importlib
from typing import Any, Optional

from loguru import logger

from ..cfg.project import ProjectConfig
from ..fs import AbstractFileSystem
from ..utils.logging import setup_logging

if importlib.util.find_spec("apscheduler"):
    from .apscheduler import APSBackend, APSManager
else:
    APSBackend = None
    APSManager = None
if importlib.util.find_spec("rq"):
    from .rq import RQBackend, RQManager
else:
    RQBackend = None
    RQManager = None
from .base import BaseBackend, BaseJobQueueManager

setup_logging()


class JobQueueBackend:
    """A factory class for creating backend instances for different job queue types.

    This class provides a unified interface for creating backend instances that handle
    the storage, queuing, and event management for different job queue types. Each backend
    type provides specific implementations for:
    - Job storage and persistence
    - Queue management
    - Event handling and communication
    - Result storage

    Example:
        ```python
        # Create RQ backend with Redis
        rq_backend = JobQueueBackend(
            job_queue_type="rq",
            uri="redis://localhost:6379/0",
            queues=["high", "default", "low"]
        )

        # Create APScheduler backend with PostgreSQL and Redis
        aps_backend = JobQueueBackend(
            job_queue_type="apscheduler",
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
        job_queue_type: str,
        **kwargs,
    ) -> BaseBackend:
        """Create a new backend instance based on the specified job queue type.

        Args:
            job_queue_type: The type of backend to create. Valid values are:
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
                the specified job queue type.

        Raises:
            ValueError: If an invalid job queue type is specified.
            RuntimeError: If backend initialization fails due to configuration
                or connection issues.

        Example:
            ```python
            # Create RQ backend
            rq_backend = Backend(
                job_queue_type="rq",
                uri="redis://localhost:6379/0",
                queues=["high", "default", "low"],
                result_ttl=3600
            )

            # Create APScheduler backend with PostgreSQL and Redis
            aps_backend = Backend(
                job_queue_type="apscheduler",
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
        if job_queue_type == "rq" and RQBackend is not None:
            return RQBackend(**kwargs)
        elif job_queue_type == "apscheduler" and APSBackend is not None:
            return APSBackend(**kwargs)
        else:
            if job_queue_type == "rq" and RQBackend is None:
                logger.warning(
                    "RQ is not installed. `JobQueueBackend` is not initialized and using the job queue is disabled. "
                    "Install rq to use RQ. `uv pip install flowerpower[rq]` or `uv add flowerpower[rq]`"
                )
                return None
            elif job_queue_type == "apscheduler" and APSBackend is None:
                logger.warning(
                    "APScheduler is not installed. `JobQueueBackend` is not initialized and using the job queue is disabled. "
                    "Install apscheduler to use APScheduler. `uv pip install flowerpower[apscheduler]` or `uv add flowerpower[apscheduler]`"
                )
                return None
            else:
                raise ValueError(
                    f"Invalid job queue type: {job_queue_type}. Valid types: ['rq', 'apscheduler']"
                )


class JobQueueManager:
    """A factory class for creating job queue instances for job scheduling and execution.

    This class provides a unified interface for creating different types of job queue instances
    (RQ, APScheduler, Huey) based on the specified backend type. Each job queue type provides
    different capabilities for job scheduling and execution.

    The job queue instances handle:
    - Job scheduling and execution
    - Background task processing
    - Job queue management
    - Result storage and retrieval

    Example:
        ```python
        # Create an RQ job queue
        rq_worker = JobQueueManager(
            type="rq",
            name="my_worker",
            log_level="DEBUG"
        )

        # Create an APScheduler job queue with custom backend
        from flowerpower.job_queue.apscheduler import APSBackend
        backend_config = APSBackend(
            data_store={"type": "postgresql", "uri": "postgresql+asyncpg://user:pass@localhost/db"},
            event_broker={"type": "redis", "uri": "redis://localhost:6379/0"}
        )
        aps_worker = JobQueueManager(
            type="apscheduler",
            name="scheduler",
            backend=backend_config
        )

        ```
    """

    def __new__(
        cls,
        type: str | None = None,
        name: str | None = None,
        base_dir: str | None = ".",
        backend: JobQueueBackend | None = None,
        storage_options: Optional[dict[str, Any]] = None,
        fs: AbstractFileSystem | None = None,
        log_level: str | None = None,
        **kwargs,
    ) -> BaseJobQueueManager:
        """Create a new job queue instance based on the specified backend type.

        Args:
            type: The type of job queue to create. Valid values are:
                - "rq": Redis Queue job queue for Redis-based job queuing
                - "apscheduler": APScheduler job queue for advanced job scheduling
            name: Name of the job queue instance. Used for identification in logs
                and monitoring.
            base_dir: Base directory for job queue files and configuration. Defaults
                to current working directory if not specified.
            backend: Pre-configured backend instance. If not provided, one will
                be created based on configuration settings.
            storage_options: Options for configuring filesystem storage access.
                Example: {"mode": "async", "root": "/tmp", "protocol": "s3"}
            fs: Custom filesystem implementation for storage operations.
                Example: S3FileSystem, LocalFileSystem, etc.
            log_level: Logging level for the job queue. Valid values are:
                "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            **kwargs: Additional configuration options passed to the specific
                job queue implementation.

        Returns:
            BaseJobQueueManager: An instance of the specified job queue type (RQManager,
                APSManager).

        Raises:
            ValueError: If an invalid job queue type is specified.
            ImportError: If required dependencies for the chosen job queue type
                are not installed.
            RuntimeError: If job queue initialization fails due to configuration
                or connection issues.

        Example:
            ```python
            # Basic RQ job queue
            worker = JobQueueManager(type="rq", name="basic_worker")

            # APScheduler with custom logging and storage
            worker = JobQueueManager(
                type="apscheduler",
                name="scheduler",
                base_dir="/app/data",
                storage_options={"mode": "async"},
                log_level="DEBUG"
            )

            ```
        """
        if type is None:
            type = ProjectConfig.load(
                base_dir=base_dir,
                name=name,
                fs=fs,
                storage_options=storage_options or {},
            ).job_queue.type

        if type == "rq":
            if RQManager is not None:
                return RQManager(
                    name=name,
                    base_dir=base_dir,
                    backend=backend,
                    storage_options=storage_options,
                    fs=fs,
                    log_level=log_level,
                    **kwargs,
                )
            else:
                logger.warning(
                    "`JobQueueManager` can not be initialized. This might be due to missing dependencies (RQ), invalid configuration or backend not being available."
                )
                return None

        elif type == "apscheduler":
            if APSManager is not None:
                return APSManager(
                    name=name,
                    base_dir=base_dir,
                    backend=backend,
                    storage_options=storage_options,
                    fs=fs,
                    log_level=log_level,
                    **kwargs,
                )
            else:
                logger.warning(
                    "`JobQueueManager` can not be initialized. This might be due to missing dependencies (APScheduler), invalid configuration or backend not being available."
                )
                return None

        else:
            raise ImportError(
                f"Invalid job queue type: {type}. Valid types: ['rq', 'apscheduler']"
            )


__all__ = [
    "JobQueueManager",
    "RQManager",
    "APSManager",
    # "HueyWorker",
    "JobQueueBackend",
    "RQBackend",
    "APSBackend",
]
