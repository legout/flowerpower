import msgspec

from ..base import BaseConfig


class ProjectOpenTelemetryConfig(BaseConfig):
    host: str = msgspec.field(default="localhost")
    port: int = msgspec.field(default=6831)
