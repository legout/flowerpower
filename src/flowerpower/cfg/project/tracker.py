from pydantic import Field

from ..base import BaseConfig


class ProjectTrackerConfig(BaseConfig):
    username: str | None = Field(default=None)
    api_url: str = "http://localhost:8241"
    ui_url: str = "http://localhost:8242"
    api_key: str | None = Field(default=None)
    verify: bool = False
