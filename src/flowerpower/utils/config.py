"""
Configuration utilities for FlowerPower.

This module provides shared configuration handling utilities to avoid code duplication.
"""

from typing import Any, Dict, Iterable
from dataclasses import fields

from ..cfg.pipeline.run import (
    RunConfig,
    ExecutorConfig,
    WithAdapterConfig,
    RetryConfig,
)
from .security import validate_config_dict, validate_callback_function


def prefer_executor_override(base: ExecutorConfig, override: str | dict | ExecutorConfig | None) -> ExecutorConfig:
    """Merge executor configs preferring explicit runtime overrides.

    Rules:
    - If override is None -> return base
    - String -> treated as type override
    - Dict -> fields present (including explicit None) override base
    - ExecutorConfig -> fields that are not None override base
    """
    if override is None:
        return base

    # Normalize override to ExecutorConfig
    if isinstance(override, str):
        return ExecutorConfig(
            type=override,
            max_workers=base.max_workers,
            num_cpus=base.num_cpus,
        )
    elif isinstance(override, dict):
        # Preserve explicit None vs missing by checking keys
        ov = ExecutorConfig.from_dict(override)
        type_set = 'type' in override
        max_workers_set = 'max_workers' in override
        num_cpus_set = 'num_cpus' in override
        merged = ExecutorConfig(
            type=ov.type if type_set else base.type,
            max_workers=ov.max_workers if max_workers_set else base.max_workers,
            num_cpus=ov.num_cpus if num_cpus_set else base.num_cpus,
        )
        return merged
    elif isinstance(override, ExecutorConfig):
        ov = override
    else:
        return base

    # Build merged with explicit precedence: if ov.field is not None, use it
    # Note: for dict-based overrides, explicit None is kept as None (clears base)
    merged = ExecutorConfig(
        type=ov.type if (ov.type is not None) else base.type,
        max_workers=ov.max_workers if (ov.max_workers is not None) else base.max_workers,
        num_cpus=ov.num_cpus if (ov.num_cpus is not None) else base.num_cpus,
    )
    return merged


def resolve_executor_config(
    *,
    base: ExecutorConfig | None,
    override: str | dict | ExecutorConfig | None,
) -> ExecutorConfig:
    """Resolve executor config from base defaults and runtime overrides."""
    effective_base = base or ExecutorConfig()
    if override is None:
        return effective_base
    return prefer_executor_override(effective_base, override)

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
    run_config.executor_override_raw = value


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


def _set_retry_cfg(run_config: RunConfig, value):
    """Set retry config (nested)."""
    if isinstance(value, dict):
        run_config.retry = RetryConfig.from_dict(value)
    elif isinstance(value, RetryConfig):
        run_config.retry = value


def _merge_additional_modules(run_config: RunConfig, value):
    """Merge additional modules while preserving order and removing duplicates."""

    def _normalise_modules(mods: Any) -> list:
        if mods is None:
            return []
        if isinstance(mods, (str, bytes)):
            return [mods]
        if isinstance(mods, Iterable) and not isinstance(mods, (dict,)):  # type: ignore[arg-type]
            return list(mods)
        return [mods]

    existing = _normalise_modules(run_config.additional_modules)
    incoming = _normalise_modules(value)
    combined: list[Any] = []

    def _append_unique(module_obj: Any) -> None:
        for existing_module in combined:
            if existing_module is module_obj:
                return
            if (
                isinstance(existing_module, str)
                and isinstance(module_obj, str)
                and existing_module == module_obj
            ):
                return
        combined.append(module_obj)

    for module_obj in existing + incoming:
        _append_unique(module_obj)

    run_config.additional_modules = combined if combined else None


_attr_handlers = {
    'inputs': _merge_inputs,
    'config': _merge_config,
    'cache': _set_cache,
    'adapter': _merge_adapter,
    'executor_cfg': _set_executor_cfg,
    'with_adapter_cfg': _set_with_adapter_cfg,
    'pipeline_adapter_cfg': _set_pipeline_adapter_cfg,
    'project_adapter_cfg': _set_project_adapter_cfg,
    'retry': _set_retry_cfg,
    'additional_modules': _merge_additional_modules,
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
            elif attr in ['max_retries', 'retry_delay', 'jitter_factor', 'retry_exceptions']:
                # Map deprecated flat fields into nested retry configuration
                if run_config.retry is None:
                    run_config.retry = RetryConfig()
                if attr == 'max_retries' and value is not None:
                    run_config.retry.max_retries = int(value)
                elif attr == 'retry_delay' and value is not None:
                    run_config.retry.retry_delay = float(value)
                elif attr == 'jitter_factor':
                    run_config.retry.jitter_factor = value
                elif attr == 'retry_exceptions' and value is not None:
                    run_config.retry.retry_exceptions = list(value) if isinstance(value, (list, tuple)) else [value]
            else:
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

    def with_additional_modules(self, modules: Any | None) -> 'RunConfigBuilder':
        """Set additional modules for Hamilton driver composition."""
        if modules is None:
            return self

        merged = self.config.additional_modules or []
        to_add = modules
        if isinstance(to_add, (str, bytes)):
            to_add = [to_add]
        elif not isinstance(to_add, list):
            to_add = list(to_add)  # type: ignore[arg-type]

        for module_obj in to_add:
            if merged is None:
                merged = []
            if merged and any(
                (existing is module_obj)
                or (
                    isinstance(existing, str)
                    and isinstance(module_obj, str)
                    and existing == module_obj
                )
                for existing in merged
            ):
                continue
            merged.append(module_obj)

        self.config.additional_modules = merged
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
            self.config.executor_override_raw = executor_cfg
        return self
    
    def with_retry_config(self, max_retries: int | None = None, retry_delay: float | None = None,
                         jitter_factor: float | None = None, retry_exceptions: tuple | list | None = None) -> 'RunConfigBuilder':
        """Set retry configuration."""
        if self.config.retry is None:
            self.config.retry = RetryConfig()
        if max_retries is not None:
            self.config.retry.max_retries = max_retries
        if retry_delay is not None:
            self.config.retry.retry_delay = retry_delay
        if jitter_factor is not None:
            self.config.retry.jitter_factor = jitter_factor
        if retry_exceptions is not None:
            self.config.retry.retry_exceptions = list(retry_exceptions) if isinstance(retry_exceptions, (list, tuple)) else [retry_exceptions]
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
            if self.config.retry is None:
                self.config.retry = RetryConfig()
            self.config.retry.max_retries = max_retries
        return self
    
    def with_retry_delay(self, retry_delay: float | None) -> 'RunConfigBuilder':
        """Set retry delay."""
        if retry_delay is not None:
            if self.config.retry is None:
                self.config.retry = RetryConfig()
            self.config.retry.retry_delay = retry_delay
        return self
    
    def with_jitter_factor(self, jitter_factor: float | None) -> 'RunConfigBuilder':
        """Set jitter factor."""
        if jitter_factor is not None:
            if self.config.retry is None:
                self.config.retry = RetryConfig()
            self.config.retry.jitter_factor = jitter_factor
        return self
    
    def with_retry_exceptions(self, retry_exceptions: list | None) -> 'RunConfigBuilder':
        """Set retry exceptions."""
        if retry_exceptions is not None:
            if self.config.retry is None:
                self.config.retry = RetryConfig()
            self.config.retry.retry_exceptions = retry_exceptions
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
            executor_override_raw=self.config.executor_override_raw,
            with_adapter=self.config.with_adapter,
            pipeline_adapter_cfg=self.config.pipeline_adapter_cfg,
            project_adapter_cfg=self.config.project_adapter_cfg,
            adapter=self.config.adapter,
            reload=self.config.reload,
            log_level=self.config.log_level,
            retry=self.config.retry,
            on_success=self.config.on_success,
            on_failure=self.config.on_failure,
            additional_modules=self.config.additional_modules,
        )
