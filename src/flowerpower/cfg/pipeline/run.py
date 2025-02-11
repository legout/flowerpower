from munch import Munch, munchify
from pydantic import Field

from ..base import BaseConfig


class PipelineRunConfig(BaseConfig):
    final_vars: list[str] = Field(default_factory=list)
    inputs: dict | Munch = Field(default_factory=dict)
    executor: str | None = None
    config: dict | Munch = Field(default_factory=dict)
    with_tracker: bool = False
    with_opentelemetry: bool = False
    with_progressbar: bool = False

    def model_post_init(self, __context):
        if isinstance(self.inputs, dict):
            self.inputs = munchify(self.inputs)
