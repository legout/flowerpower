import datetime as dt

from munch import Munch, munchify
import msgspec

from ..base import BaseConfig


class ProjectWorkerConfig(BaseConfig):
    data_store: dict | Munch = msgspec.field(default_factory=dict)
    event_broker: dict | Munch = msgspec.field(default_factory=dict)
    cleanup_interval: int | float | dt.timedelta = msgspec.field(default=300)  # int in secods
    max_concurrent_jobs: int = msgspec.field(default=10)

    def __post_init__(self):
        if isinstance(self.data_store, dict):
            self.data_store = munchify(self.data_store)
        if isinstance(self.event_broker, dict):
            self.event_broker = munchify(self.event_broker)
