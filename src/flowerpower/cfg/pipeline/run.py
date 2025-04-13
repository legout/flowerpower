from munch import Munch, munchify
import msgspec

from ..base import BaseConfig


class PipelineRunConfig(BaseConfig):
    final_vars: list[str] = msgspec.field(default_factory=list)
    inputs: dict | Munch = msgspec.field(default_factory=dict)
    executor: str | None = None
    config: dict | Munch = msgspec.field(default_factory=dict)
    with_tracker: bool = False
    with_opentelemetry: bool = False
    with_progressbar: bool = False

    def __post_init__(self):
        if isinstance(self.inputs, dict):
            self.inputs = munchify(self.inputs)
