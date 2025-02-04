from munch import Munch, munchify
from pydantic import Field

from ..base import BaseConfig


class PipelineTrackerConfig(BaseConfig):
    project_id: int | None = None
    # version: str | None = None
    dag_name: str | None = None
    tags: dict | Munch = Field(default_factory=dict)

    def model_post_init(self, __context):
        self.tags = munchify(self.tags)
