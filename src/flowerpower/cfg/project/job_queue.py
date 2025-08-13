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

            else:
                raise ValueError(
                    f"Invalid job queue type: {self.type}. Valid types: ['rq']"
                )

    def update_type(self, type: str):
        if type != self.type:
            self.type = type
            self.backend = None
            self.__post_init__()
