import msgspec

from ..base import BaseConfig

from .adapter import AdapterConfig
from .worker import WorkerConfig


class ProjectConfig(BaseConfig):
    name: str | None = msgspec.field(default=None)
    worker: WorkerConfig = msgspec.field(default_factory=WorkerConfig)
    adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)
