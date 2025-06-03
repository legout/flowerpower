import datetime as dt
import importlib
import os

import msgspec

from ... import settings
from ...settings.backend import BACKEND_PROPERTIES
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
    type: str = msgspec.field(default=settings.APS_BACKEND_DS or "memory")
    username: str | None = msgspec.field(default=None)
    password: str | None = msgspec.field(default=None)
    host: str | None = msgspec.field(default=None)
    port: int | None = msgspec.field(default=None)
    database: str | None = msgspec.field(default=None)
    schema: str | None = msgspec.field(default=None)

    def __post_init__(self):
        self.update_settings_from_env()
        self.host = (
            settings.APS_BACKEND_DS_HOST
            or BACKEND_PROPERTIES[self.type]["default_host"]
        )
        self.port = (
            settings.APS_BACKEND_DS_PORT
            or BACKEND_PROPERTIES[self.type]["default_port"]
        )
        self.database = (
            settings.APS_BACKEND_DS_DB
            or BACKEND_PROPERTIES[self.type]["default_database"]
        )
        self.username = (
            settings.APS_BACKEND_DS_USERNAME
            or BACKEND_PROPERTIES[self.type]["default_username"]
        )
        self.password = (
            settings.APS_BACKEND_DS_PASSWORD
            or BACKEND_PROPERTIES[self.type]["default_password"]
        )

    def update_settings_from_env(self):
        if os.getenv("FP_APS_BACKEND_DS") is not None:
            settings.APS_BACKEND_DS = os.getenv("FP_APS_BACKEND_DS")
        if os.getenv("FP_APS_BACKEND_DS_USERNAME") is not None:
            settings.APS_BACKEND_DS_USERNAME = os.getenv("FP_APS_BACKEND_DS_USERNAME")
        if os.getenv("FP_APS_BACKEND_DS_PASSWORD") is not None:
            settings.APS_BACKEND_DS_PASSWORD = os.getenv("FP_APS_BACKEND_DS_PASSWORD")
        if os.getenv("FP_APS_BACKEND_DS_HOST") is not None:
            settings.APS_BACKEND_DS_HOST = os.getenv("FP_APS_BACKEND_DS_HOST")
        if os.getenv("FP_APS_BACKEND_DS_PORT") is not None:
            settings.APS_BACKEND_DS_PORT = int(os.getenv("FP_APS_BACKEND_DS_PORT"))
        if os.getenv("FP_APS_BACKEND_DS_DB") is not None:
            settings.APS_BACKEND_DS_DB = os.getenv("FP_APS_BACKEND_DS_DB")


class APSEventBrokerConfig(JobQueueBackendConfig):
    type: str = msgspec.field(default=settings.APS_BACKEND_EB or "memory")
    username: str | None = msgspec.field(default=None)
    password: str | None = msgspec.field(default=None)
    host: str | None = msgspec.field(default=None)
    port: int | None = msgspec.field(default=None)
    database: str | None = msgspec.field(default=None)
    from_ds_sqla: bool = msgspec.field(
        default_factory=lambda: settings.APS_BACKEND_EB == "postgresql"
        and settings.APS_BACKEND_DS == "postgresql"
    )

    def __post_init__(self):
        self.update_settings_from_env()
        self.host = (
            settings.APS_BACKEND_EB_HOST
            or BACKEND_PROPERTIES[self.type]["default_host"]
        )
        self.port = (
            settings.APS_BACKEND_EB_PORT
            or BACKEND_PROPERTIES[self.type]["default_port"]
        )
        self.database = (
            settings.APS_BACKEND_EB_DB
            or BACKEND_PROPERTIES[self.type]["default_database"]
        )
        self.username = (
            settings.APS_BACKEND_EB_USERNAME
            or BACKEND_PROPERTIES[self.type]["default_username"]
        )
        self.password = (
            settings.APS_BACKEND_EB_PASSWORD
            or BACKEND_PROPERTIES[self.type]["default_password"]
        )

    def update_settings_from_env(self):
        if os.getenv("FP_APS_BACKEND_EB") is not None:
            settings.APS_BACKEND_EB = os.getenv("FP_APS_BACKEND_EB")
        if os.getenv("FP_APS_BACKEND_EB_USERNAME") is not None:
            settings.APS_BACKEND_EB_USERNAME = os.getenv("FP_APS_BACKEND_EB_USERNAME")
        if os.getenv("FP_APS_BACKEND_EB_PASSWORD") is not None:
            settings.APS_BACKEND_EB_PASSWORD = os.getenv("FP_APS_BACKEND_EB_PASSWORD")
        if os.getenv("FP_APS_BACKEND_EB_HOST") is not None:
            settings.APS_BACKEND_EB_HOST = os.getenv("FP_APS_BACKEND_EB_HOST")
        if os.getenv("FP_APS_BACKEND_EB_PORT") is not None:
            settings.APS_BACKEND_EB_PORT = int(os.getenv("FP_APS_BACKEND_EB_PORT"))
        if os.getenv("FP_APS_BACKEND_EB_DB") is not None:
            settings.APS_BACKEND_EB_DB = os.getenv("FP_APS_BACKEND_EB_DB")


class APSBackendConfig(BaseConfig):
    data_store: APSDataStoreConfig = msgspec.field(default_factory=APSDataStoreConfig)
    event_broker: APSEventBrokerConfig = msgspec.field(
        default_factory=APSEventBrokerConfig
    )
    cleanup_interval: int | float | dt.timedelta = msgspec.field(
        default=settings.APS_CLEANUP_INTERVAL
    )  # int in seconds
    max_concurrent_jobs: int = msgspec.field(default=settings.APS_MAX_CONCURRENT_JOBS)
    default_job_executor: str | None = msgspec.field(default=settings.EXECUTOR)
    # num_workers: int | None = msgspec.field(default=settings.APS_NUM_WORKERS)

    # def __post_init__(self):
    #     self.data_store.update_settings_from_env()
    #     self.event_broker.update_settings_from_env()


class RQBackendConfig(JobQueueBackendConfig):
    type: str = msgspec.field(default="redis")
    username: str | None = msgspec.field(default=settings.RQ_BACKEND_USERNAME)
    password: str | None = msgspec.field(default=settings.RQ_BACKEND_PASSWORD)
    host: str = msgspec.field(default=settings.RQ_BACKEND_HOST)
    port: int = msgspec.field(default=settings.RQ_BACKEND_PORT)
    database: int = msgspec.field(default=settings.RQ_BACKEND_DB)
    queues: str | list[str] = msgspec.field(default_factory=lambda: settings.RQ_QUEUES)
    # num_workers: int = msgspec.field(default=settings.RQ_NUM_WORKERS)  # int in seconds

    def update_from_settings(self):
        if self.host == BACKEND_PROPERTIES[self.type]["default_host"]:
            self.host = settings.RQ_BACKEND_HOST
        if self.port == BACKEND_PROPERTIES[self.type]["default_port"]:
            self.port = settings.RQ_BACKEND_PORT
        if self.database == BACKEND_PROPERTIES[self.type]["default_database"]:
            self.database = settings.RQ_BACKEND_DB
        if self.username == BACKEND_PROPERTIES[self.type]["default_username"]:
            self.username = settings.RQ_BACKEND_USERNAME
        if self.password == BACKEND_PROPERTIES[self.type]["default_password"]:
            self.password = settings.RQ_BACKEND_PASSWORD

    def update_from_env(self):
        if os.getenv("FP_RQ_BACKEND") is not None:
            settings.RQ_BACKEND = os.getenv("FP_RQ_BACKEND")
        if os.getenv("FP_RQ_BACKEND_USERNAME") is not None:
            settings.RQ_BACKEND_USERNAME = os.getenv("FP_RQ_BACKEND_USERNAME")
        if os.getenv("FP_RQ_BACKEND_PASSWORD") is not None:
            settings.RQ_BACKEND_PASSWORD = os.getenv("FP_RQ_BACKEND_PASSWORD")
        if os.getenv("FP_RQ_BACKEND_HOST") is not None:
            settings.RQ_BACKEND_HOST = os.getenv("FP_RQ_BACKEND_HOST")
        if os.getenv("FP_RQ_BACKEND_PORT") is not None:
            settings.RQ_BACKEND_PORT = int(os.getenv("FP_RQ_BACKEND_PORT"))
        if os.getenv("FP_RQ_BACKEND_DB") is not None:
            settings.RQ_BACKEND_DB = int(os.getenv("FP_RQ_BACKEND_DB"))
        self.update_from_settings()

    def __post_init__(self):
        if isinstance(self.queues, str):
            self.queues = self.queues.replace(" ", "").split(",")
        elif not isinstance(self.queues, list):
            raise ValueError(
                f"Invalid queues type: {type(self.queues)}. Must be a string or a list."
            )
        self.update_from_env()


class HueyBackendConfig(JobQueueBackendConfig):
    pass


class JobQueueConfig(BaseConfig):
    type: str | None = msgspec.field(default="rq")
    backend: dict | None = msgspec.field(default=None)
    num_workers: int | None = msgspec.field(default=None)

    def __post_init__(self):
        if self.type is not None:
            self.type = self.type.lower()
            if self.type == "rq":
                self.backend = self.backend or RQBackendConfig()

                if isinstance(self.backend, dict):
                    self.backend = RQBackendConfig.from_dict(self.backend)
                elif isinstance(self.backend, RQBackendConfig):
                    pass
                else:
                    raise ValueError(
                        f"Invalid backend type for RQ: {type(self.backend)}"
                    )
                self.num_workers = self.num_workers or settings.RQ_NUM_WORKERS

            elif self.type == "apscheduler":
                self.backend = self.backend or APSBackendConfig()
                if isinstance(self.backend, dict):
                    self.backend = APSBackendConfig.from_dict(self.backend)
                elif isinstance(self.backend, APSBackendConfig):
                    pass
                else:
                    raise ValueError(
                        f"Invalid backend type for APScheduler: {type(self.backend)}"
                    )
                self.num_workers = self.num_workers or settings.APS_NUM_WORKERS
            else:
                raise ValueError(
                    f"Invalid job queue type: {self.type}. Valid types: {['rq', 'apscheduler', 'huey']}"
                )

    def update_type(self, type: str):
        if type != self.type:
            self.type = type
            self.backend = None
            self.__post_init__()
