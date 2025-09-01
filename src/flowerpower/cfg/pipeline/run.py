import msgspec
from munch import munchify
from typing import Any, Callable

from ... import settings
from ..base import BaseConfig


class WithAdapterConfig(BaseConfig):
    hamilton_tracker: bool = msgspec.field(default=False)
    mlflow: bool = msgspec.field(default=False)
    # openlineage: bool = msgspec.field(default=False)
    ray: bool = msgspec.field(default=False)
    opentelemetry: bool = msgspec.field(default=False)
    progressbar: bool = msgspec.field(default=False)
    future: bool = msgspec.field(default=False)


class ExecutorConfig(BaseConfig):
    type: str | None = msgspec.field(default=settings.EXECUTOR)
    max_workers: int | None = msgspec.field(default=settings.EXECUTOR_MAX_WORKERS)
    num_cpus: int | None = msgspec.field(default=settings.EXECUTOR_NUM_CPUS)


class RunConfig(BaseConfig):
    inputs: dict | None = msgspec.field(default_factory=dict)
    final_vars: list[str] | None = msgspec.field(default_factory=list)
    config: dict | None = msgspec.field(default_factory=dict)
    cache: dict | bool | None = msgspec.field(default=False)
    with_adapter: WithAdapterConfig = msgspec.field(default_factory=WithAdapterConfig)
    executor: ExecutorConfig = msgspec.field(default_factory=ExecutorConfig)
    log_level: str | None = msgspec.field(default="INFO")
    max_retries: int = msgspec.field(default=3)
    retry_delay: int | float = msgspec.field(default=1)
    jitter_factor: float | None = msgspec.field(default=0.1)
    retry_exceptions: list[str] = msgspec.field(default_factory=lambda: ["Exception"])
    # New fields for comprehensive configuration
    pipeline_adapter_cfg: dict | None = msgspec.field(default=None)
    project_adapter_cfg: dict | None = msgspec.field(default=None)
    adapter: dict[str, Any] | None = msgspec.field(default=None)
    reload: bool = msgspec.field(default=False)
    on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = msgspec.field(default=None)
    on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = msgspec.field(default=None)

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
        if isinstance(self.pipeline_adapter_cfg, dict):
            from ..pipeline.adapter import AdapterConfig as PipelineAdapterConfig
            self.pipeline_adapter_cfg = PipelineAdapterConfig.from_dict(self.pipeline_adapter_cfg)
        if isinstance(self.project_adapter_cfg, dict):
            from ..project.adapter import AdapterConfig as ProjectAdapterConfig
            self.project_adapter_cfg = ProjectAdapterConfig.from_dict(self.project_adapter_cfg)
        if isinstance(self.adapter, dict):
            # Convert adapter instances if needed
            pass
        if isinstance(self.retry_exceptions, list):
            # Convert string exceptions to actual exception classes
            converted_exceptions = []
            for exc in self.retry_exceptions:
                if isinstance(exc, str):
                    try:
                        exc_class = eval(exc)
                        # Ensure it's actually an exception class
                        if isinstance(exc_class, type) and issubclass(exc_class, BaseException):
                            converted_exceptions.append(exc_class)
                        else:
                            converted_exceptions.append(Exception)
                    except (NameError, AttributeError):
                        converted_exceptions.append(Exception)
                elif isinstance(exc, type) and issubclass(exc, BaseException):
                    converted_exceptions.append(exc)
                else:
                    converted_exceptions.append(Exception)
            self.retry_exceptions = converted_exceptions
