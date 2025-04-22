import datetime as dt

import msgspec

from .. import BaseConfig

# class Worker(Enum):
#    RQ = "rq"
#    APSCHEDULER = "apscheduler"


class WorkerBackendConfig(BaseConfig):
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
    cert_file: str | None = msgspec.field(default=None)
    key_file: str | None = msgspec.field(default=None)
    ca_file: str | None = msgspec.field(default=None)
    verify_ssl: bool = msgspec.field(default=False)


class APSDataStoreConfig(WorkerBackendConfig):
    type: str = msgspec.field(default_factory=lambda: "postgresql")
    host: str = msgspec.field(default_factory=lambda: "localhost")
    port: int = msgspec.field(default_factory=lambda: 5432)
    schema: str | None = msgspec.field(default="flowerpower")
    username: str = msgspec.field(default_factory=lambda: "postgres")


class APSEventBrokerConfig(WorkerBackendConfig):
    from_ds_sqla: bool = msgspec.field(default=True)


class APSBackendConfig(BaseConfig):
    data_store: APSDataStoreConfig = msgspec.field(default_factory=APSDataStoreConfig)
    event_broker: APSEventBrokerConfig = msgspec.field(
        default_factory=APSEventBrokerConfig
    )
    cleanup_interval: int | float | dt.timedelta = msgspec.field(
        default=300
    )  # int in secods
    max_concurrent_jobs: int = msgspec.field(default=10)
    default_job_executor: str | None = msgspec.field(default="threadpool")
    num_workers: int | None = msgspec.field(default=None)


class RQBackendConfig(WorkerBackendConfig):
    type: str = msgspec.field(default_factory=lambda: "redis")
    host: str = msgspec.field(default_factory=lambda: "localhost")
    port: int = msgspec.field(default_factory=lambda: 6379)
    queues: str | list[str] = msgspec.field(default_factory=lambda: ["default"])


class HueyBackendConfig(WorkerBackendConfig):
    pass


class WorkerConfig(BaseConfig):
    type: str | None = msgspec.field(default="rq")
    backend: dict | None = msgspec.field(default=None)

    def __post_init__(self):
        if self.type is not None:
            self.type = self.type.lower()
            if self.type == "rq":
                if self.backend is None:
                    self.backend = RQBackendConfig()
                else:
                    self.backend = RQBackendConfig(**self.backend)
            elif self.type == "apscheduler":
                if self.backend is None:
                    self.backend = APSBackendConfig(
                        data_store=APSDataStoreConfig(),
                        event_broker=APSEventBrokerConfig(),
                    )
                else:
                    self.backend = APSBackendConfig(
                        data_store=APSDataStoreConfig(
                            self.backend.get("data_store", {})
                        ),
                        event_broker=APSEventBrokerConfig(
                            self.backend.get("event_broker", {})
                        ),
                    )
            elif self.type == "huey":
                if self.backend is None:
                    self.backend = HueyBackendConfig()
                else:
                    self.backend = HueyBackendConfig(**self.backend)
            else:
                raise ValueError(
                    f"Invalid worker type: {self.type}. Valid types: {['rq', 'apscheduler', 'huey']}"
                )

    def update_type(self, type: str):
        if type != self.type:
            self.type = type
            self.backend = None
            self.__post_init__()
