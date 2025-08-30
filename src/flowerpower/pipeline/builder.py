from __future__ import annotations

from typing import Any, Callable

from ..cfg import PipelineConfig
from ..cfg.pipeline.run import RunConfig


class RunConfigBuilder:
    """A builder for creating RunConfig objects.

    This class provides a fluent interface for constructing a RunConfig object,
    allowing for a more readable and self-documenting way to configure a
    pipeline run.
    """

    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name
        self._config = RunConfig()
        self._load_defaults()

    def _load_defaults(self):
        """Loads the default configuration from the pipeline's YAML file."""
        pipeline_cfg = PipelineConfig.load(name=self.pipeline_name)
        if pipeline_cfg and pipeline_cfg.run:
            self._config = pipeline_cfg.run

    def with_inputs(self, inputs: dict) -> "RunConfigBuilder":
        self._config.inputs.update(inputs)
        return self

    def with_final_vars(self, final_vars: list[str]) -> "RunConfigBuilder":
        self._config.final_vars.extend(final_vars)
        return self

    def build(self) -> "RunConfig":
        return self._config