
import msgspec

from ..base import BaseConfig

from .open_telemetry import ProjectOpenTelemetryConfig
from .tracker import ProjectTrackerConfig
from .worker import ProjectWorkerConfig


class ProjectConfig(BaseConfig):
    name: str | None = None
    worker: ProjectWorkerConfig = msgspec.field(default_factory=ProjectWorkerConfig)
    tracker: ProjectTrackerConfig = msgspec.field(default_factory=ProjectTrackerConfig)
    open_telemetry: ProjectOpenTelemetryConfig = msgspec.field(
        default_factory=ProjectOpenTelemetryConfig
    )
