import msgspec

from ..base import BaseConfig
from .open_telemetry import OpenTelemetryConfig
from .tracker import TrackerConfig
from .worker import WorkerConfig


class ProjectConfig(BaseConfig):
    name: str | None = None
    worker: WorkerConfig = msgspec.field(default_factory=WorkerConfig)
    tracker: TrackerConfig = msgspec.field(default_factory=TrackerConfig)
    open_telemetry: OpenTelemetryConfig = msgspec.field(
        default_factory=OpenTelemetryConfig
    )
