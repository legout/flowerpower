import datetime as dt

from munch import Munch, munchify
from pydantic import Field

from ..base import BaseConfig


class ProjectWorkerConfig(BaseConfig):
    data_store: dict | Munch = Field(default_factory=dict)
    event_broker: dict | Munch = Field(default_factory=dict)
    cleanup_interval: int | float | dt.timedelta = Field(default=900)  # int in secods
    max_concurrent_jobs: int = Field(default=100)

    def model_post_init(self, __context):
        if isinstance(self.data_store, dict):
            self.data_store = munchify(self.data_store)
        if isinstance(self.event_broker, dict):
            self.event_broker = munchify(self.event_broker)
