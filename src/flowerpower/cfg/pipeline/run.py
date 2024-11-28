from pydantic import Field
from munch import Munch, munchify

from ..base import BaseConfig


class PipelineRunConfig(BaseConfig):
    final_vars: list[str] = Field(default_factory=list)
    inputs: dict | Munch = Field(default_factory=dict)
    executor: str | None = Field(default=None)
    with_tracker: bool = Field(default=False)
    with_opentelemetry: bool = Field(default=False)

    def model_post_init(self, __context):
        if isinstance(self.inputs, dict):
            self.inputs = munchify(self.inputs)
