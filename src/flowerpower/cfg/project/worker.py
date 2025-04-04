import datetime as dt

from munch import Munch, munchify
from pydantic import Field

from ..base import BaseConfig


class ProjectWorkerConfig(BaseConfig):
    # Removed APScheduler specific fields: data_store, event_broker
    # cleanup_interval: int | float | dt.timedelta = Field(default=300) # Note: RQ doesn't have a direct equivalent cleanup interval concept
    # max_concurrent_jobs: int = Field(default=10) # Note: Concurrency is managed by the number of RQ workers run

    # --- RQ Configuration ---
    redis_url: str = Field(default="redis://localhost:6379/0")
    default_queue: str = Field(default="default")

    # Removed model_post_init related to data_store/event_broker
