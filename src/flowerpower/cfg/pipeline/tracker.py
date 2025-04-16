import msgspec
from munch import munchify

from ..base import BaseConfig


class PipelineTrackerConfig(BaseConfig):
    project_id: int | None = None
    # version: str | None = None
    dag_name: str | None = None
    tags: dict  = msgspec.field(default_factory=dict)

    def __post_init__(self):
        self.tags = munchify(self.tags)
