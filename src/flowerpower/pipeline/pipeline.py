"""Active Pipeline class for FlowerPower."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import msgspec

from ..cfg import PipelineConfig
from ..utils.adapter import create_adapter_manager
from ..utils.executor import create_executor_factory
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
    _runner: Optional[PipelineRunner] = None

    def __post_init__(self) -> None:
        initialize_telemetry()
        self._adapter_manager = create_adapter_manager()
        self._executor_factory = create_executor_factory()

    def run(self, run_config=None, **kwargs):
        return self._get_runner().run(run_config=run_config, **kwargs)

    async def run_async(self, run_config=None, **kwargs):
        return await self._get_runner().run_async(run_config=run_config, **kwargs)

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
