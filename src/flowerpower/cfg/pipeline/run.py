import msgspec
from munch import munchify

from ..base import BaseConfig

class AdapterConfig(BaseConfig):
    tracker: bool = msgspec.field(default=False)
    mlflow: bool = msgspec.field(default=False)
    openlineage: bool = msgspec.field(default=False)
    ray: bool = msgspec.field(default=False)
    opentelemetry: bool = msgspec.field(default=False)
    progressbar: bool = msgspec.field(default=False)


class RunConfig(BaseConfig):
    final_vars: list[str] | None = msgspec.field(default_factory=list)
    inputs: dict | None = msgspec.field(default_factory=dict)
    executor: str | None = msgspec.field(default=None)
    config: dict | None = msgspec.field(default_factory=dict)
    cache: dict | None = msgspec.field(default_factory=dict)
    adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)

    def __post_init__(self):
        if isinstance(self.inputs, dict):
            self.inputs = munchify(self.inputs)
        if isinstance(self.config, dict):
            self.config = munchify(self.config)
        if isinstance(self.cache, dict):
            self.cache = munchify(self.cache)
