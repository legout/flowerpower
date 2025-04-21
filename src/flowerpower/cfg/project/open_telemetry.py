import msgspec

from ..base import BaseConfig


class OpenTelemetryConfig(BaseConfig):
    host: str = msgspec.field(default="localhost")
    port: int = msgspec.field(default=6831)
