import os

import msgspec
from munch import munchify

from ..base import BaseConfig


class WithAdapterConfig(BaseConfig):
    tracker: bool = msgspec.field(default=False)
    mlflow: bool = msgspec.field(default=False)
    # openlineage: bool = msgspec.field(default=False)
    ray: bool = msgspec.field(default=False)
    opentelemetry: bool = msgspec.field(default=False)
    progressbar: bool = msgspec.field(default=False)
    future: bool = msgspec.field(default=False)


class ExecutorConfig(BaseConfig):
    type: str | None = msgspec.field(default=None)
    max_workers: int | None = msgspec.field(default=10)
    num_cpus: int | None = msgspec.field(default_factory=os.cpu_count)


class RunConfig(BaseConfig):
    inputs: dict | None = msgspec.field(default_factory=dict)
    final_vars: list[str] | None = msgspec.field(default_factory=list)
    config: dict | None = msgspec.field(default_factory=dict)
    cache: dict | bool | None = msgspec.field(default_factory=dict)
    with_adapter: WithAdapterConfig | dict = msgspec.field(
        default_factory=WithAdapterConfig
    )
    executor: ExecutorConfig | dict = msgspec.field(default_factory=ExecutorConfig)

    def __post_init__(self):
        if isinstance(self.inputs, dict):
            self.inputs = munchify(self.inputs)
        if isinstance(self.config, dict):
            self.config = munchify(self.config)
        if isinstance(self.cache, (dict)):
            self.cache = munchify(self.cache)
        if isinstance(self.with_adapter, dict):
            self.with_adapter = WithAdapterConfig.from_dict(self.with_adapter)
        if isinstance(self.executor, dict):
            self.executor = ExecutorConfig.from_dict(self.executor)
