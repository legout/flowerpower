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
    ssl_cert: str | None = msgspec.field(default=None)
    ssl_key: str | None = msgspec.field(default=None)
    ssl_ca: str | None = msgspec.field(default=None)
    verify_ssl: bool = msgspec.field(default=False)


class APSDataStore(WorkerBackend):
    pass


class APSEventBroker(WorkerBackend):
    pass


class APSBackend(BaseConfig):
    data_store: APSDataStore = msgspec.field(default_factory=APSDataStore)
    event_broker: APSEventBroker = msgspec.field(default_factory=APSEventBroker)
    cleanup_interval: int | float | dt.timedelta = msgspec.field(
        default=300
    )  # int in secods
    max_concurrent_jobs: int = msgspec.field(default=10)
    schema: str | None = msgspec.field(default="flowerpower")
    default_job_executor:str | None = msgspec.field(default="threadpool")
    num_workers: int | None = msgspec.field(default=None)

class RQBackend(WorkerBackend):
    queues: str | list[str] = msgspec.field(default_factory=lambda: ["default"])


class HueyBackend(WorkerBackend):
    pass


class ProjectWorkerConfig(BaseConfig):
    type: str | None = msgspec.field(default="rq")
    backend: dict | None = msgspec.field(default=None)

    def __post_init__(self):
        if self.type is not None:
            self.type = self.type.lower()
            if self.type == "rq":
                if self.backend is None:
                    self.backend = RQBackend()
                else:
                    self.backend = RQBackend(**self.backend)
                    if self.backend.type is None:
                        self.backend.type = "redis"
            elif self.type == "apscheduler":
                if self.backend is None:
                    self.backend = APSBackend(
                        data_store=APSDataStore(), event_broker=APSEventBroker()
                    )
                else:
                    self.backend = APSBackend(
                        data_store=APSDataStore(**self.backend.get("data_store", {})),
                        event_broker=APSEventBroker(
                            **self.backend.get("event_broker", {})
                        ),
                    )
            elif self.type == "huey":
                if self.backend is None:
                    self.backend = HueyBackend()
                else:
                    self.backend = HueyBackend(**self.backend)
            else:
                raise ValueError(
                    f"Invalid worker type: {self.type}. Valid types: {['rq', 'apscheduler', 'huey']}"
                )
