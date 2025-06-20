from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union
import datetime


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