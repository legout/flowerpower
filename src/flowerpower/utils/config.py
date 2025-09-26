"""
Configuration utilities for FlowerPower.

This module provides shared configuration handling utilities to avoid code duplication.
"""

from typing import Any, Dict
from dataclasses import fields

from ..cfg.pipeline.run import (
    RunConfig,
    ExecutorConfig,
    WithAdapterConfig,
)
from .security import validate_config_dict, validate_callback_function
def _merge_inputs(run_config: RunConfig, value):
    """Merge inputs into run config."""
    validate_config_dict(value)
    if run_config.inputs is None:
        run_config.inputs = value
    else:
        run_config.inputs.update(value)


def _merge_config(run_config: RunConfig, value):
    """Merge config into run config."""
    validate_config_dict(value)
    if run_config.config is None:
        run_config.config = value
    else:
        run_config.config.update(value)


def _set_cache(run_config: RunConfig, value):
    """Set cache in run config."""
    run_config.cache = value


def _merge_adapter(run_config: RunConfig, value):
    """Merge adapter into run config."""
    if run_config.adapter is None:
        run_config.adapter = value
    else:
        run_config.adapter.update(value)


def _set_executor_cfg(run_config: RunConfig, value):
    """Set executor config."""
    if isinstance(value, str):
        run_config.executor = ExecutorConfig(type=value)
    elif isinstance(value, dict):
        run_config.executor = ExecutorConfig.from_dict(value)
    elif isinstance(value, ExecutorConfig):
        run_config.executor = value


def _set_with_adapter_cfg(run_config: RunConfig, value):
    """Set with adapter config."""
    if isinstance(value, dict):
        run_config.with_adapter = WithAdapterConfig.from_dict(value)
    elif isinstance(value, WithAdapterConfig):
        run_config.with_adapter = value


def _set_pipeline_adapter_cfg(run_config: RunConfig, value):
    """Set pipeline adapter config."""
    run_config.pipeline_adapter_cfg = value


def _set_project_adapter_cfg(run_config: RunConfig, value):
    """Set project adapter config."""
    run_config.project_adapter_cfg = value


_attr_handlers = {
    'inputs': _merge_inputs,
    'config': _merge_config,
    'cache': _set_cache,
    'adapter': _merge_adapter,
    'executor_cfg': _set_executor_cfg,
    'with_adapter_cfg': _set_with_adapter_cfg,
    'pipeline_adapter_cfg': _set_pipeline_adapter_cfg,
    'project_adapter_cfg': _set_project_adapter_cfg,
}


def merge_run_config_with_kwargs(run_config: RunConfig, kwargs: Dict[str, Any]) -> RunConfig:
    """Merge kwargs into a RunConfig object.
    
    This utility function updates the RunConfig object with values from kwargs,
    handling different types of attributes appropriately.
    
    Args:
        run_config: The RunConfig object to update
        kwargs: Dictionary of additional parameters to merge
        
    Returns:
        RunConfig: Updated RunConfig object
    """
    # Handle complex attributes with specific logic
    for attr, handler in _attr_handlers.items():
        if attr in kwargs and kwargs[attr] is not None:
            handler(run_config, kwargs[attr])

    # Handle simple attributes
    simple_attrs = [
        'final_vars', 'reload', 'log_level', 'max_retries', 'retry_delay',
        'jitter_factor', 'retry_exceptions', 'on_success', 'on_failure'
    ]
    
    for attr in simple_attrs:
        if attr in kwargs and kwargs[attr] is not None:
            value = kwargs[attr]
            # Validate callbacks for security
            if attr in ['on_success', 'on_failure']:
                validate_callback_function(value)
            setattr(run_config, attr, value)
    
    return run_config


class RunConfigBuilder:
    """Builder pattern for constructing RunConfig objects with fluent interface."""
    
    def __init__(self, base_config: RunConfig | None = None):
        self.config = base_config or RunConfig()
    
    def with_inputs(self, inputs: Dict[str, Any] | None) -> 'RunConfigBuilder':
        """Set inputs configuration."""
        if inputs is not None:
            validate_config_dict(inputs)
            self.config.inputs = inputs
        return self
    
    def with_config(self, config: Dict[str, Any] | None) -> 'RunConfigBuilder':
        """Set pipeline configuration."""
        if config is not None:
            validate_config_dict(config)
            self.config.config = config
        return self
    
    def with_cache(self, cache: bool | None) -> 'RunConfigBuilder':
        """Set caching configuration."""
        if cache is not None:
            self.config.cache = cache
        return self
    
    def with_adapter(self, adapter: Dict[str, Any] | None) -> 'RunConfigBuilder':
        """Set adapter configuration."""
        if adapter is not None:
            if self.config.adapter is None:
                self.config.adapter = adapter
            else:
                self.config.adapter.update(adapter)
        return self
    
    def with_executor(self, executor_cfg: str | Dict[str, Any] | ExecutorConfig | None) -> 'RunConfigBuilder':
        """Set executor configuration."""
        if executor_cfg is not None:
            if isinstance(executor_cfg, str):
                self.config.executor = ExecutorConfig(type=executor_cfg)
            elif isinstance(executor_cfg, dict):
                self.config.executor = ExecutorConfig.from_dict(executor_cfg)
            elif isinstance(executor_cfg, ExecutorConfig):
                self.config.executor = executor_cfg
        return self
    
    def with_retry_config(self, max_retries: int | None = None, retry_delay: float | None = None,
                         jitter_factor: float | None = None, retry_exceptions: tuple | None = None) -> 'RunConfigBuilder':
        """Set retry configuration."""
        if max_retries is not None:
            self.config.max_retries = max_retries
        if retry_delay is not None:
            self.config.retry_delay = retry_delay
        if jitter_factor is not None:
            self.config.jitter_factor = jitter_factor
        if retry_exceptions is not None:
            self.config.retry_exceptions = retry_exceptions
        return self
    
    def with_logging(self, log_level: str | None = None) -> 'RunConfigBuilder':
        """Set logging configuration."""
        if log_level is not None:
            self.config.log_level = log_level
        return self
    
    def with_callbacks(self, on_success: str | None = None, on_failure: str | None = None) -> 'RunConfigBuilder':
        """Set callback configurations."""
        if on_success is not None:
            validate_callback_function(on_success)
            self.config.on_success = on_success
        if on_failure is not None:
            validate_callback_function(on_failure)
            self.config.on_failure = on_failure
        return self
    
    # Additional methods for backward compatibility with tests
    def with_final_vars(self, final_vars: list[str] | None) -> 'RunConfigBuilder':
        """Set final variables."""
        if final_vars is not None:
            self.config.final_vars = final_vars
        return self
    
    def with_executor_cfg(self, executor_cfg: str | Dict[str, Any] | ExecutorConfig | None) -> 'RunConfigBuilder':
        """Set executor configuration (alias for with_executor)."""
        return self.with_executor(executor_cfg)
    
    def with_with_adapter_cfg(self, with_adapter_cfg: Dict[str, Any] | WithAdapterConfig | None) -> 'RunConfigBuilder':
        """Set with_adapter configuration."""
        if with_adapter_cfg is not None:
            if isinstance(with_adapter_cfg, dict):
                self.config.with_adapter = WithAdapterConfig.from_dict(with_adapter_cfg)
            elif isinstance(with_adapter_cfg, WithAdapterConfig):
                self.config.with_adapter = with_adapter_cfg
        return self
    
    def with_pipeline_adapter_cfg(self, pipeline_adapter_cfg: Any | None) -> 'RunConfigBuilder':
        """Set pipeline adapter configuration."""
        if pipeline_adapter_cfg is not None:
            self.config.pipeline_adapter_cfg = pipeline_adapter_cfg
        return self
    
    def with_project_adapter_cfg(self, project_adapter_cfg: Any | None) -> 'RunConfigBuilder':
        """Set project adapter configuration."""
        if project_adapter_cfg is not None:
            self.config.project_adapter_cfg = project_adapter_cfg
        return self
    
    def with_reload(self, reload: bool | None) -> 'RunConfigBuilder':
        """Set reload flag."""
        if reload is not None:
            self.config.reload = reload
        return self
    
    def with_log_level(self, log_level: str | None) -> 'RunConfigBuilder':
        """Set log level (alias for with_logging)."""
        return self.with_logging(log_level)
    
    def with_max_retries(self, max_retries: int | None) -> 'RunConfigBuilder':
        """Set max retries."""
        if max_retries is not None:
            self.config.max_retries = max_retries
        return self
    
    def with_retry_delay(self, retry_delay: float | None) -> 'RunConfigBuilder':
        """Set retry delay."""
        if retry_delay is not None:
            self.config.retry_delay = retry_delay
        return self
    
    def with_jitter_factor(self, jitter_factor: float | None) -> 'RunConfigBuilder':
        """Set jitter factor."""
        if jitter_factor is not None:
            self.config.jitter_factor = jitter_factor
        return self
    
    def with_retry_exceptions(self, retry_exceptions: list | None) -> 'RunConfigBuilder':
        """Set retry exceptions."""
        if retry_exceptions is not None:
            self.config.retry_exceptions = retry_exceptions
        return self
    
    def with_on_success(self, on_success: Any | None) -> 'RunConfigBuilder':
        """Set on_success callback."""
        if on_success is not None:
            self.config.on_success = on_success
        return self
    
    def with_on_failure(self, on_failure: Any | None) -> 'RunConfigBuilder':
        """Set on_failure callback."""
        if on_failure is not None:
            self.config.on_failure = on_failure
        return self
    
    def reset(self) -> 'RunConfigBuilder':
        """Reset builder to default values."""
        self.config = RunConfig()
        return self
    
    @classmethod
    def from_config(cls, config: RunConfig) -> 'RunConfigBuilder':
        """Create builder from existing config."""
        return cls(base_config=config)
    
    def build(self) -> RunConfig:
        """Build and return the RunConfig object."""
        # Create a new copy to ensure immutability
        return RunConfig(
            inputs=self.config.inputs,
            final_vars=self.config.final_vars,
            config=self.config.config,
            cache=self.config.cache,
            executor=self.config.executor,
            with_adapter=self.config.with_adapter,
            pipeline_adapter_cfg=self.config.pipeline_adapter_cfg,
            project_adapter_cfg=self.config.project_adapter_cfg,
            adapter=self.config.adapter,
            reload=self.config.reload,
            log_level=self.config.log_level,
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay,
            jitter_factor=self.config.jitter_factor,
            retry_exceptions=self.config.retry_exceptions,
            on_success=self.config.on_success,
            on_failure=self.config.on_failure,
        )