from pydantic import Field
from munch import Munch, munchify
from ..base import BaseConfig


class PipelineTrackerConfig(BaseConfig):
    project_id: int | None = Field(default=None)
    version: str | None = Field(default=None)
    dag_name: str | None = Field(default=None)
    tags: dict | Munch = Field(default_factory=dict)

    def model_post_init(self, __context):
        self.tags = munchify(self.tags)
