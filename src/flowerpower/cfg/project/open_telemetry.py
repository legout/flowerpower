from pydantic import Field

from ..base import BaseConfig


class ProjectOpenTelemetryConfig(BaseConfig):
    host: str = Field(default="localhost")
    port: int = Field(default=6831)
