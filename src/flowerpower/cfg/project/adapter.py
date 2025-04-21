import msgspec

from ..base import BaseConfig
from munch import munchify

class TrackerConfig(BaseConfig):
    username: str | None = msgspec.field(default=None)
    api_url: str = msgspec.field(default="http://localhost:8241")
    ui_url: str = msgspec.field(default="http://localhost:8242")
    api_key: str | None = msgspec.field(default=None)
    verify: bool = msgspec.field(default=False)

class MLFlowConfig(BaseConfig):
    tracking_uri: str | None = msgspec.field(default=None)
    registry_uri: str | None = msgspec.field(default=None)
    artifact_location: str | None = msgspec.field(default=None)

class OpenTelemetryConfig(BaseConfig):
    host: str = msgspec.field(default="localhost")
    port: int = msgspec.field(default=6831)

class RayConfig(BaseConfig):
    ray_init_config = msgspec.field(default_factory=dict)
    shutdown_ray_on_completion: bool = msgspec.field(default=False)

    def __post_init__(self):
        if isinstance(self.ray_init_config, dict):
            self.ray_init_config = munchify(self.ray_init_config)

class AdapterConfig(BaseConfig):
    tracker: TrackerConfig = msgspec.field(default_factory=TrackerConfig)
    mlflow: MLFlowConfig = msgspec.field(default_factory=MLFlowConfig)
    ray: RayConfig = msgspec.field(default_factory=RayConfig)
    opentelemetry: OpenTelemetryConfig = msgspec.field(
        default_factory=OpenTelemetryConfig
    )
