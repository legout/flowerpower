import msgspec

from ..base import BaseConfig


class TrackerConfig(BaseConfig):
    username: str | None = msgspec.field(default=None)
    api_url: str = "http://localhost:8241"
    ui_url: str = "http://localhost:8242"
    api_key: str | None = msgspec.field(default=None)
    verify: bool = False
