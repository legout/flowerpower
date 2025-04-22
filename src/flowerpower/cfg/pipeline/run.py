import msgspec
from munch import munchify
import os
from .. import BaseConfig


class AdapterConfig(BaseConfig):
    tracker: bool = msgspec.field(default=False)
    mlflow: bool = msgspec.field(default=False)
    openlineage: bool = msgspec.field(default=False)
    ray: bool = msgspec.field(default=False)
    opentelemetry: bool = msgspec.field(default=False)
    progressbar: bool = msgspec.field(default=False)


class ExecutorConfig(BaseConfig):
    type: str | None = msgspec.field(default=None)
    max_workers: int | None = msgspec.field(default=10)
    num_cpus: int | None = msgspec.field(default_factory=os.cpu_count)


class RunConfig(BaseConfig):
    inputs: dict | None = msgspec.field(default_factory=dict)
    final_vars: list[str] | None = msgspec.field(default_factory=list)
    config: dict | None = msgspec.field(default_factory=dict)
    cache: dict | None = msgspec.field(default_factory=dict)
    adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)
    executor: ExecutorConfig = msgspec.field(default_factory=ExecutorConfig)

    def __post_init__(self):
        if isinstance(self.inputs, dict):
            self.inputs = munchify(self.inputs)
        if isinstance(self.config, dict):
            self.config = munchify(self.config)
        if isinstance(self.cache, dict):
            self.cache = munchify(self.cache)
