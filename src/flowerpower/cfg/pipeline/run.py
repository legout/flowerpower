import msgspec
from munch import munchify

from ..base import BaseConfig


class RunConfig(BaseConfig):
    final_vars: list[str] | None = msgspec.field(default_factory=list)
    inputs: dict | None = msgspec.field(default_factory=dict)
    executor: str | None = None
    config: dict | None = msgspec.field(default_factory=dict)
    with_tracker: bool = False
    with_opentelemetry: bool = False
    with_progressbar: bool = False

    def __post_init__(self):
        if isinstance(self.inputs, dict):
            self.inputs = munchify(self.inputs)
        if isinstance(self.config, dict):
            self.config = munchify(self.config)
