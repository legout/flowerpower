"""Active Pipeline class for FlowerPower."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import msgspec

from ..cfg import PipelineConfig
from ..cfg.pipeline.run import RunConfig
from ..utils.adapter import create_adapter_manager
from ..utils.config import merge_run_config_with_kwargs, merge_run_configs
from ..utils.executor import create_executor_factory
from .execution_context import resolve_run_config_adapter_configs
from .runner import PipelineRunner
from .telemetry import initialize_telemetry

if TYPE_CHECKING:
    from ..flowerpower import FlowerPowerProject


class Pipeline(msgspec.Struct):
    """Represents a single pipeline with configuration and execution context."""

    name: str
    config: PipelineConfig
    module: Any
    project_context: FlowerPowerProject
    _adapter_manager: Any = None
    _executor_factory: Any = None
    _runner: PipelineRunner | None = None

    def __post_init__(self) -> None:
        initialize_telemetry()
        self._adapter_manager = create_adapter_manager()
        self._executor_factory = create_executor_factory()

    def run(self, run_config=None, **kwargs):
        effective_run_config = merge_run_configs(self.config.run, run_config)
        if kwargs:
            effective_run_config = merge_run_config_with_kwargs(
                effective_run_config, kwargs
            )
        effective_run_config = resolve_run_config_adapter_configs(
            effective_run_config, self.config, self.project_context
        )
        return self._run_resolved(effective_run_config)

    def _run_resolved(self, run_config: RunConfig) -> Any:
        """Execute an already-resolved run configuration synchronously."""
        return self._get_runner().run(run_config=run_config)

    async def run_async(self, run_config=None, **kwargs):
        effective_run_config = merge_run_configs(self.config.run, run_config)
        if kwargs:
            effective_run_config = merge_run_config_with_kwargs(
                effective_run_config, kwargs
            )
        effective_run_config = resolve_run_config_adapter_configs(
            effective_run_config, self.config, self.project_context
        )
        return await self._get_runner().run_async(
            run_config=effective_run_config,
        )

    @property
    def adapter_manager(self):
        return self._adapter_manager

    @property
    def executor_factory(self):
        return self._executor_factory

    def _get_runner(self) -> PipelineRunner:
        if self._runner is None:
            self._runner = PipelineRunner(self)
        return self._runner
