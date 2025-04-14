import datetime as dt

import msgspec
from enum import Enum
from ..base import BaseConfig

# class Worker(Enum):
#    RQ = "rq"
#    APSCHEDULER = "apscheduler"


class WorkerBackend(BaseConfig):
    """
    Worker backend configuration for FlowerPower.
    Inherits from BaseConfig and adapts Redis logic.
    """

    type: str | None = msgspec.field(default=None)
    uri: str | None = msgspec.field(default=None)
    username: str | None = msgspec.field(default=None)
    password: str | None = msgspec.field(default=None)
    host: str | None = msgspec.field(default=None)
    port: int | None = msgspec.field(default=None)
    database: int | None = msgspec.field(default=None)
    ssl: bool = msgspec.field(default=False)


class APSBackend(BaseConfig):
    data_store: WorkerBackend = msgspec.field(default_factory=WorkerBackend)
    event_broker: WorkerBackend = msgspec.field(default_factory=WorkerBackend)
    cleanup_interval: int | float | dt.timedelta = msgspec.field(
        default=300
    )  # int in secods
    max_concurrent_jobs: int = msgspec.field(default=10)
    schema: str | None = msgspec.field(default="flowerpower")


class RQBackend(BaseConfig):
    backend: WorkerBackend = msgspec.field(default_factory=WorkerBackend)
    queues: str | list[str] = msgspec.field(default_factory=lambda: ["default"])


class ProjectWorkerConfig(BaseConfig):
    aps_backend: APSBackend | None = msgspec.field(default_factory=APSBackend)
    rq_backend: RQBackend | None = msgspec.field(default_factory=RQBackend)
    type: str | None = msgspec.field(default=None)

    def __post_init__(self):
        if self.type is not None:
            self.type = self.type.lower()
            if self.type == "rq":
                self.aps_backend = None
            elif self.type == "apscheduler":
                self.rq_backend = None
            else:
                raise ValueError(
                    f"Invalid worker type: {self.type}. Valid types: {['rq', 'apscheduler']}"
                )
