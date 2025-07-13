import datetime
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union

from flowerpower.cfg.project.adapter import ProjectConfigAdapter
from flowerpower.fs.storage_options import resolve_filesystem

class JobStatus(Enum):
    """Enumeration of possible job states in the queue."""

    PENDING = auto()
    QUEUED = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()
    RETRY = auto()
    SCHEDULED = auto()
    PAUSED = auto()


@dataclass
class JobInfo:
    """Backend-agnostic representation of a job in the queue."""

    id: str
    status: JobStatus
    name: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: Optional[int] = None
    queue: Optional[str] = None
    worker_id: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkerInfo:
    """Information about a worker process/instance."""

    id: str
    name: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[datetime.datetime] = None
    last_heartbeat: Optional[datetime.datetime] = None
    queues: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueueInfo:
    """Information about a job queue."""

    name: str
    job_count: int
    jobs: Optional[List[str]] = None


class Factor:
    """
    Factor for job queue configuration resolution.

    Initialize Factor instance through either:
    - Direct type/backend specification
    - Base directory + storage options/filesystem

    Args:
        type: Job queue type (e.g., 'rq')
        backend: Configuration dictionary for the backend
        base_dir: Base directory path for project
        storage_options: Storage options dictionary
        fs: Filesystem instance (alternative to storage_options)
    """

    def __init__(
        self,
        type: str = None,
        backend: dict = None,
        base_dir: str = None,
        storage_options: dict = None,
        fs=None,
    ):
        # Conflicting parameter check
        if (type or backend) and base_dir:
            raise ValueError("Conflicting initialization: provide either (type and backend) or base_dir, not both.")

        if (type is not None) ^ (backend is not None):
            raise ValueError("Both 'type' and 'backend' must be provided together.")

        if type and backend:
            self.type = type
            self.backend = backend
            return

        if base_dir:
            import os

            conf_path = os.path.join(base_dir, "conf", "project.yml")
            if not os.path.exists(conf_path):
                raise FileNotFoundError(f"Project configuration file not found: {conf_path}")

            # Use ProjectConfigAdapter to load config
            adapter = ProjectConfigAdapter(conf_path, fs=fs or (resolve_filesystem(storage_options) if storage_options else None))
            config = adapter.load()
            job_queue_config = config.get("job_queue")
            if not job_queue_config or "type" not in job_queue_config or "backend" not in job_queue_config:
                raise ValueError("Invalid or missing job_queue configuration in project.yml")

            self.type = job_queue_config["type"]
            self.backend = job_queue_config["backend"]
            return

        raise ValueError("Insufficient initialization parameters: provide either (type and backend) or base_dir.")

    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkerStats:
    """Statistics about a worker's activity."""

    worker_id: str
    jobs_processed: int = 0
    jobs_failed: int = 0
    last_job_id: Optional[str] = None
    last_active: Optional[datetime.datetime] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BackendCapabilities:
    """Describes the features supported by a job queue backend."""

    supports_scheduling: bool = False
    supports_priorities: bool = False
    supports_worker_control: bool = False
    supports_job_cancellation: bool = False
    supports_queue_inspection: bool = False
    supports_job_result_fetching: bool = True
    supports_worker_stats: bool = False
    custom_capabilities: Dict[str, Any] = field(default_factory=dict)
