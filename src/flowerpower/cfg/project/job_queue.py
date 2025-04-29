import datetime as dt

import msgspec

from ... import settings
from ..base import BaseConfig


class JobQueueBackendConfig(BaseConfig):
    """
    Job Queue backend configuration for FlowerPower.
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


class APSDataStoreConfig(JobQueueBackendConfig):
    type: str = msgspec.field(default=settings.APS_BACKEND_DS)
    host: str = msgspec.field(
        default=settings.BACKEND_PROPERTIES[settings.APS_BACKEND_DS]["default_host"]
    )
    port: int = msgspec.field(
        default=settings.BACKEND_PROPERTIES[settings.APS_BACKEND_DS]["default_port"]
    )
    schema: str | None = msgspec.field(default=settings.APS_SCHEMA_DS)
    username: str = msgspec.field(
        default=settings.BACKEND_PROPERTIES[settings.APS_BACKEND_DS]["default_username"]
    )


class APSEventBrokerConfig(JobQueueBackendConfig):
    type: str = msgspec.field(default=settings.APS_BACKEND_EB)
    host: str = msgspec.field(
        default=settings.BACKEND_PROPERTIES[settings.APS_BACKEND_EB]["default_host"]
    )
    port: int = msgspec.field(
        default=settings.BACKEND_PROPERTIES[settings.APS_BACKEND_EB]["default_port"]
    )
    username: str = msgspec.field(
        default=settings.BACKEND_PROPERTIES[settings.APS_BACKEND_EB]["default_username"]
    )
    from_ds_sqla: bool = msgspec.field(
        default_factory=lambda: settings.APS_BACKEND_EB == "postgresql"
        and settings.APS_BACKEND_DS == "postgresql"
    )


class APSBackendConfig(BaseConfig):
    data_store: APSDataStoreConfig = msgspec.field(default_factory=APSDataStoreConfig)
    event_broker: APSEventBrokerConfig = msgspec.field(
        default_factory=APSEventBrokerConfig
    )
    cleanup_interval: int | float | dt.timedelta = msgspec.field(
        default=settings.APS_CLEANUP_INTERVAL
    )  # int in secods
    max_concurrent_jobs: int = msgspec.field(default=settings.APS_MAX_CONCURRENT_JOBS)
    default_job_executor: str | None = msgspec.field(default=settings.EXECUTOR)
    num_workers: int | None = msgspec.field(default=settings.APS_NUM_WORKERS)


class RQBackendConfig(JobQueueBackendConfig):
    type: str = msgspec.field(default="redis")
    host: str = msgspec.field(
        default=settings.BACKEND_PROPERTIES["redis"]["default_host"]
    )
    port: int = msgspec.field(
        default=settings.BACKEND_PROPERTIES["redis"]["default_port"]
    )
    database: int = msgspec.field(
        default=settings.BACKEND_PROPERTIES["redis"]["default_database"]
    )
    queues: str | list[str] = msgspec.field(default_factory=lambda: settings.RQ_QUEUES)
    num_workers: int = msgspec.field(default=settings.RQ_NUM_WORKERS)  # int in secods


class HueyBackendConfig(JobQueueBackendConfig):
    pass


class JobQueueConfig(BaseConfig):
    type: str | None = msgspec.field(default="rq")
    backend: dict | None = msgspec.field(default=None)

    def __post_init__(self):
        if self.type is not None:
            self.type = self.type.lower()
            if self.type == "rq":
                if self.backend is None:
                    self.backend = RQBackendConfig()
                else:
                    if isinstance(self.backend, dict):
                        self.backend = RQBackendConfig.from_dict(self.backend)
                    elif isinstance(self.backend, RQBackendConfig):
                        pass
                    else:
                        raise ValueError(
                            f"Invalid backend type for RQ: {type(self.backend)}"
                        )
            elif self.type == "apscheduler":
                if self.backend is None:
                    self.backend = APSBackendConfig()
                else:
                    if isinstance(self.backend, dict):
                        self.backend = APSBackendConfig.from_dict(self.backend)
                    elif isinstance(self.backend, APSBackendConfig):
                        pass
                    else:
                        raise ValueError(
                            f"Invalid backend type for APScheduler: {type(self.backend)}"
                        )

            elif self.type == "huey":
                if self.backend is None:
                    self.backend = HueyBackendConfig()
                else:
                    if isinstance(self.backend, dict):
                        self.backend = HueyBackendConfig.from_dict(self.backend)
                    elif isinstance(self.backend, HueyBackendConfig):
                        pass
                    else:
                        raise ValueError(
                            f"Invalid backend type for Huey: {type(self.backend)}"
                        )
                    self.backend = HueyBackendConfig(**self.backend)
            else:
                raise ValueError(
                    f"Invalid job queue type: {self.type}. Valid types: {['rq', 'apscheduler', 'huey']}"
                )

    def update_type(self, type: str):
        if type != self.type:
            self.type = type
            self.backend = None
            self.__post_init__()
