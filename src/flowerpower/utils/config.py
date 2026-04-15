"""
Configuration utilities for FlowerPower.

This module provides shared configuration handling utilities to avoid code duplication.
"""

import copy
from collections.abc import Iterable
from typing import Any

from ..cfg.pipeline.run import (
    CallbackSpec,
    RunConfig,
    ExecutorConfig,
    WithAdapterConfig,
    RetryConfig,
)
from .security import validate_config_dict, validate_callback_function


def prefer_executor_override(
    base: ExecutorConfig, override: str | dict | ExecutorConfig | None
) -> ExecutorConfig:
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
        type_set = "type" in override
        max_workers_set = "max_workers" in override
        num_cpus_set = "num_cpus" in override
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
        max_workers=ov.max_workers
        if (ov.max_workers is not None)
        else base.max_workers,
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


def _safe_copy(value: Any) -> Any:
    """Copy a value without failing on uncopyable objects like modules."""
    try:
        return copy.deepcopy(value)
    except Exception:
        if isinstance(value, list):
            return list(value)
        if isinstance(value, dict):
            return dict(value)
        try:
            return copy.copy(value)
        except Exception:
            return value


def _clone_callback_spec(value: Any) -> Any:
    """Clone a ``CallbackSpec`` while preserving callable identity."""
    if value is None or not isinstance(value, CallbackSpec):
        return value

    args = tuple(value.args) if value.args is not None else None
    kwargs = dict(value.kwargs) if value.kwargs is not None else None
    return CallbackSpec(func=value.func, args=args, kwargs=kwargs)


def _mark_explicit_override(run_config: RunConfig, *fields: str) -> None:
    """Record fields that were explicitly set on a ``RunConfig``."""
    if run_config.explicit_overrides is None:
        run_config.explicit_overrides = []
    for field in fields:
        if field not in run_config.explicit_overrides:
            run_config.explicit_overrides.append(field)


def clone_run_config(run_config: RunConfig) -> RunConfig:
    """Clone a ``RunConfig`` while tolerating runtime-only objects.

    ``RunConfig`` can contain module objects, callbacks, or adapters that are not
    safely deep-copyable. This helper copies the mutable containers we merge into
    during execution, while leaving opaque runtime objects intact when necessary.
    """
    cloned = copy.copy(run_config)
    cloned.inputs = _safe_copy(run_config.inputs)
    cloned.final_vars = _safe_copy(run_config.final_vars)
    cloned.config = _safe_copy(run_config.config)
    cloned.cache = _safe_copy(run_config.cache)
    cloned.with_adapter = _safe_copy(run_config.with_adapter)
    cloned.with_adapter_override_raw = _safe_copy(
        run_config.with_adapter_override_raw
    )
    cloned.executor = _safe_copy(run_config.executor)
    cloned.executor_override_raw = _safe_copy(run_config.executor_override_raw)
    cloned.retry = _safe_copy(run_config.retry)
    cloned.retry_override_raw = _safe_copy(run_config.retry_override_raw)
    cloned.pipeline_adapter_cfg = _safe_copy(run_config.pipeline_adapter_cfg)
    cloned.pipeline_adapter_cfg_override_raw = _safe_copy(
        run_config.pipeline_adapter_cfg_override_raw
    )
    cloned.project_adapter_cfg = _safe_copy(run_config.project_adapter_cfg)
    cloned.project_adapter_cfg_override_raw = _safe_copy(
        run_config.project_adapter_cfg_override_raw
    )
    cloned.adapter = dict(run_config.adapter) if run_config.adapter is not None else None
    cloned.on_success = _clone_callback_spec(run_config.on_success)
    cloned.on_failure = _clone_callback_spec(run_config.on_failure)
    cloned.additional_modules = _safe_copy(run_config.additional_modules)
    cloned.explicit_overrides = _safe_copy(run_config.explicit_overrides)
    _sync_retry_legacy_fields(cloned)
    return cloned


def _normalize_callback_spec(value: Any) -> Any:
    """Normalize callback values to ``CallbackSpec`` when needed."""
    if value is None:
        return value
    if isinstance(value, CallbackSpec):
        validate_callback_function(value.func)
        return _clone_callback_spec(value)
    if callable(value):
        validate_callback_function(value)
        return CallbackSpec(func=value)
    if isinstance(value, tuple):
        if len(value) != 3:
            raise ValueError(
                "Callback tuples must be (func, args, kwargs)."
            )
        func, args, kwargs = value
        validate_callback_function(func)
        normalized_args = tuple(args) if args is not None else None
        normalized_kwargs = dict(kwargs) if kwargs is not None else None
        return CallbackSpec(
            func=func,
            args=normalized_args,
            kwargs=normalized_kwargs,
        )
    raise TypeError(
        "Callback must be callable, CallbackSpec, or a (func, args, kwargs) tuple."
    )


def build_sparse_struct_patch(
    value: Any,
    default: Any,
) -> dict[str, Any]:
    """Return a nested patch containing only fields differing from defaults.

    This is a best-effort way to distinguish intentional overrides from fields
    merely populated by struct defaults. It cannot preserve the difference
    between "unset" and "explicitly set to the default value", but it lets us
    merge partially populated msgspec structs without clobbering existing base
    configuration.
    """
    patch: dict[str, Any] = {}

    for field in getattr(value, "__struct_fields__", ()):  # pragma: no branch
        if not hasattr(default, field):
            continue

        current_value = getattr(value, field)
        default_value = getattr(default, field)

        if hasattr(current_value, "merge_dict") and hasattr(default_value, "__struct_fields__"):
            nested_patch = build_sparse_struct_patch(current_value, default_value)
            if nested_patch:
                patch[field] = nested_patch
        elif current_value != default_value:
            patch[field] = _safe_copy(current_value)

    return patch


def _sync_retry_legacy_fields(run_config: RunConfig) -> None:
    """Keep deprecated flat retry fields aligned with nested retry config."""
    if run_config.retry is None:
        return

    run_config.max_retries = run_config.retry.max_retries
    run_config.retry_delay = run_config.retry.retry_delay
    run_config.jitter_factor = run_config.retry.jitter_factor
    run_config.retry_exceptions = list(run_config.retry.retry_exceptions)


def _merge_struct_or_mapping(existing: Any, value: Any) -> Any:
    """Merge mapping/struct overrides onto an existing config value."""
    if isinstance(value, dict):
        if existing is None:
            return dict(value)
        if hasattr(existing, "merge_dict"):
            return existing.merge_dict(value)
        if isinstance(existing, dict):
            merged = dict(existing)
            merged.update(value)
            return merged
        return dict(value)

    if hasattr(value, "__struct_fields__"):
        if existing is None:
            return _safe_copy(value)
        if hasattr(existing, "merge_dict"):
            patch = build_sparse_struct_patch(value, type(value)())
            return existing.merge_dict(patch) if patch else existing

    return value


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
    if run_config.executor is None:
        run_config.executor = ExecutorConfig()

    if isinstance(value, str):
        run_config.executor = run_config.executor.merge_dict({"type": value})
        run_config.executor_override_raw = value
    elif isinstance(value, dict):
        run_config.executor = run_config.executor.merge_dict(value)
        run_config.executor_override_raw = dict(value)
    elif isinstance(value, ExecutorConfig):
        patch = build_sparse_struct_patch(value, ExecutorConfig())
        if patch:
            run_config.executor = run_config.executor.merge_dict(patch)
            run_config.executor_override_raw = patch
    _mark_explicit_override(run_config, "executor")



def _set_with_adapter_cfg(run_config: RunConfig, value):
    """Set with adapter config."""
    current = run_config.with_adapter or WithAdapterConfig()
    run_config.with_adapter = _merge_struct_or_mapping(current, value)
    _mark_explicit_override(run_config, "with_adapter")


def _set_pipeline_adapter_cfg(run_config: RunConfig, value):
    """Set pipeline adapter config."""
    run_config.pipeline_adapter_cfg = _merge_struct_or_mapping(
        run_config.pipeline_adapter_cfg, value
    )
    _mark_explicit_override(run_config, "pipeline_adapter_cfg")


def _set_project_adapter_cfg(run_config: RunConfig, value):
    """Set project adapter config."""
    run_config.project_adapter_cfg = _merge_struct_or_mapping(
        run_config.project_adapter_cfg, value
    )
    _mark_explicit_override(run_config, "project_adapter_cfg")


def _set_retry_cfg(run_config: RunConfig, value):
    """Set retry config (nested)."""
    if run_config.retry is None:
        run_config.retry = RetryConfig()

    if isinstance(value, dict):
        run_config.retry = run_config.retry.merge_dict(value)
    elif isinstance(value, RetryConfig):
        patch = build_sparse_struct_patch(value, RetryConfig())
        if patch:
            run_config.retry = run_config.retry.merge_dict(patch)

    _sync_retry_legacy_fields(run_config)
    _mark_explicit_override(run_config, "retry")


def _set_async_driver(run_config: RunConfig, value):
    """Set async driver toggle."""
    if value is None:
        run_config.async_driver = None
    else:
        run_config.async_driver = bool(value)
    _mark_explicit_override(run_config, "async_driver")


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
    _mark_explicit_override(run_config, "additional_modules")


_attr_handlers = {
    "inputs": _merge_inputs,
    "config": _merge_config,
    "cache": _set_cache,
    "adapter": _merge_adapter,
    "executor_cfg": _set_executor_cfg,
    "with_adapter_cfg": _set_with_adapter_cfg,
    "pipeline_adapter_cfg": _set_pipeline_adapter_cfg,
    "project_adapter_cfg": _set_project_adapter_cfg,
    "retry": _set_retry_cfg,
    "additional_modules": _merge_additional_modules,
    "async_driver": _set_async_driver,
}


def merge_run_config_with_kwargs(
    run_config: RunConfig, kwargs: dict[str, Any]
) -> RunConfig:
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
        if attr in kwargs and (kwargs[attr] is not None or attr == "async_driver"):
            handler(run_config, kwargs[attr])

    # Handle simple attributes
    simple_attrs = [
        "final_vars",
        "reload",
        "log_level",
        "max_retries",
        "retry_delay",
        "jitter_factor",
        "retry_exceptions",
        "on_success",
        "on_failure",
    ]

    for attr in simple_attrs:
        if attr in kwargs and kwargs[attr] is not None:
            value = kwargs[attr]
            # Validate callbacks for security
            if attr in ["on_success", "on_failure"]:
                setattr(run_config, attr, _normalize_callback_spec(value))
                _mark_explicit_override(run_config, attr)
            elif attr in [
                "max_retries",
                "retry_delay",
                "jitter_factor",
                "retry_exceptions",
            ]:
                # Map deprecated flat fields into nested retry configuration
                if run_config.retry is None:
                    run_config.retry = RetryConfig()
                if attr == "max_retries" and value is not None:
                    run_config.retry.max_retries = int(value)
                elif attr == "retry_delay" and value is not None:
                    run_config.retry.retry_delay = float(value)
                elif attr == "jitter_factor":
                    run_config.retry.jitter_factor = value
                elif attr == "retry_exceptions" and value is not None:
                    run_config.retry.retry_exceptions = (
                        list(value) if isinstance(value, (list, tuple)) else [value]
                    )
                _sync_retry_legacy_fields(run_config)
                _mark_explicit_override(run_config, "retry")
            else:
                setattr(run_config, attr, value)
                _mark_explicit_override(run_config, attr)

    return run_config


def merge_run_configs(base: RunConfig, override: RunConfig | None) -> RunConfig:
    """Merge a user-provided ``RunConfig`` onto pipeline defaults.

    The override config may be only partially populated. This function treats
    values matching ``RunConfig()`` defaults as unspecified and merges only the
    differing fields onto a defensive copy of ``base``.
    """
    merged = clone_run_config(base)
    if override is None:
        return merged

    patch = build_sparse_struct_patch(override, RunConfig())
    if "executor" in patch:
        patch["executor_cfg"] = patch.pop("executor")
    if override.executor_override_raw is not None:
        patch["executor_cfg"] = _safe_copy(override.executor_override_raw)
    if "with_adapter" in patch:
        patch["with_adapter_cfg"] = patch.pop("with_adapter")
    if override.with_adapter_override_raw is not None:
        patch["with_adapter_cfg"] = _safe_copy(override.with_adapter_override_raw)
    if override.retry_override_raw is not None:
        patch["retry"] = _safe_copy(override.retry_override_raw)
    if override.pipeline_adapter_cfg_override_raw is not None:
        patch["pipeline_adapter_cfg"] = _safe_copy(
            override.pipeline_adapter_cfg_override_raw
        )
    if override.project_adapter_cfg_override_raw is not None:
        patch["project_adapter_cfg"] = _safe_copy(
            override.project_adapter_cfg_override_raw
        )
    if override.adapter is not None:
        patch["adapter"] = dict(override.adapter)
    if override.on_success is not None:
        patch["on_success"] = _clone_callback_spec(override.on_success)
    if override.on_failure is not None:
        patch["on_failure"] = _clone_callback_spec(override.on_failure)

    explicit_fields = set(override.explicit_overrides or [])
    for field in (
        "inputs",
        "final_vars",
        "config",
        "cache",
        "log_level",
        "reload",
        "async_driver",
        "additional_modules",
    ):
        if field in explicit_fields:
            setattr(merged, field, _safe_copy(getattr(override, field)))

    if explicit_fields:
        _mark_explicit_override(merged, *sorted(explicit_fields))

    if patch:
        merge_run_config_with_kwargs(merged, patch)

    return merged


class RunConfigBuilder:
    """Builder pattern for constructing RunConfig objects with fluent interface."""

    def __init__(
        self,
        base_config: RunConfig | None = None,
        pipeline_name: str | None = None,
    ):
        """Initialize the builder.

        Args:
            base_config: Optional starting configuration to mutate.
            pipeline_name: Backward-compatible placeholder retained for older
                call sites that still pass ``pipeline_name=...``. The simplified
                builder no longer needs it, so it is accepted but ignored.
        """
        self.config = clone_run_config(base_config) if base_config is not None else RunConfig()
        self.pipeline_name = pipeline_name

    def with_inputs(self, inputs: dict[str, Any] | None) -> "RunConfigBuilder":
        """Set inputs configuration."""
        if inputs is not None:
            validate_config_dict(inputs)
            self.config.inputs = dict(inputs)
            _mark_explicit_override(self.config, "inputs")
        return self

    def with_config(self, config: dict[str, Any] | None) -> "RunConfigBuilder":
        """Set pipeline configuration."""
        if config is not None:
            validate_config_dict(config)
            self.config.config = dict(config)
            _mark_explicit_override(self.config, "config")
        return self

    def with_cache(self, cache: bool | None) -> "RunConfigBuilder":
        """Set caching configuration."""
        if cache is not None:
            self.config.cache = dict(cache) if isinstance(cache, dict) else cache
            _mark_explicit_override(self.config, "cache")
        return self

    def with_adapter(self, adapter: dict[str, Any] | None) -> "RunConfigBuilder":
        """Set adapter configuration."""
        if adapter is not None:
            if self.config.adapter is None:
                self.config.adapter = dict(adapter)
            else:
                self.config.adapter.update(adapter)
            _mark_explicit_override(self.config, "adapter")
        return self

    def with_async_driver(self, enabled: bool | None) -> "RunConfigBuilder":
        """Enable or disable Hamilton's async driver for async runs."""
        if enabled is None:
            self.config.async_driver = None
        else:
            self.config.async_driver = bool(enabled)
        _mark_explicit_override(self.config, "async_driver")
        return self

    def with_additional_modules(self, modules: Any | None) -> "RunConfigBuilder":
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
        _mark_explicit_override(self.config, "additional_modules")
        return self

    def with_executor(
        self, executor_cfg: str | dict[str, Any] | ExecutorConfig | None
    ) -> "RunConfigBuilder":
        """Set executor configuration."""
        if executor_cfg is not None:
            if isinstance(executor_cfg, ExecutorConfig):
                self.config.executor = _safe_copy(executor_cfg)
                self.config.executor_override_raw = executor_cfg.to_dict()
                _mark_explicit_override(self.config, "executor")
            else:
                merge_run_config_with_kwargs(
                    self.config,
                    {"executor_cfg": executor_cfg},
                )
        return self

    def with_retry_config(
        self,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        jitter_factor: float | None = None,
        retry_exceptions: tuple | list | None = None,
    ) -> "RunConfigBuilder":
        """Set retry configuration."""
        if self.config.retry is None:
            self.config.retry = RetryConfig()
        if self.config.retry_override_raw is None:
            self.config.retry_override_raw = {}
        if max_retries is not None:
            self.config.retry.max_retries = max_retries
            self.config.retry_override_raw["max_retries"] = max_retries
        if retry_delay is not None:
            self.config.retry.retry_delay = retry_delay
            self.config.retry_override_raw["retry_delay"] = retry_delay
        if jitter_factor is not None:
            self.config.retry.jitter_factor = jitter_factor
            self.config.retry_override_raw["jitter_factor"] = jitter_factor
        if retry_exceptions is not None:
            exceptions = (
                list(retry_exceptions)
                if isinstance(retry_exceptions, (list, tuple))
                else [retry_exceptions]
            )
            self.config.retry.retry_exceptions = exceptions
            self.config.retry_override_raw["retry_exceptions"] = list(exceptions)
        _mark_explicit_override(self.config, "retry")
        return self

    def with_retries(
        self,
        max_attempts: int | None = None,
        delay: float | None = None,
        jitter: float | None = None,
        exceptions: tuple | list | None = None,
    ) -> "RunConfigBuilder":
        """Backward-compatible alias for configuring retry behavior."""
        return self.with_retry_config(
            max_retries=max_attempts,
            retry_delay=delay,
            jitter_factor=jitter,
            retry_exceptions=exceptions,
        )

    def with_logging(self, log_level: str | None = None) -> "RunConfigBuilder":
        """Set logging configuration."""
        if log_level is not None:
            self.config.log_level = log_level
            _mark_explicit_override(self.config, "log_level")
        return self

    def with_callbacks(
        self, on_success: Any | None = None, on_failure: Any | None = None
    ) -> "RunConfigBuilder":
        """Set callback configurations."""
        if on_success is not None:
            self.config.on_success = _normalize_callback_spec(on_success)
            _mark_explicit_override(self.config, "on_success")
        if on_failure is not None:
            self.config.on_failure = _normalize_callback_spec(on_failure)
            _mark_explicit_override(self.config, "on_failure")
        return self

    # Additional methods for backward compatibility with tests
    def with_final_vars(self, final_vars: list[str] | None) -> "RunConfigBuilder":
        """Set final variables."""
        if final_vars is not None:
            self.config.final_vars = list(final_vars)
            _mark_explicit_override(self.config, "final_vars")
        return self

    def with_executor_cfg(
        self, executor_cfg: str | dict[str, Any] | ExecutorConfig | None
    ) -> "RunConfigBuilder":
        """Set executor configuration (alias for with_executor)."""
        return self.with_executor(executor_cfg)

    def with_with_adapter_cfg(
        self, with_adapter_cfg: dict[str, Any] | WithAdapterConfig | None
    ) -> "RunConfigBuilder":
        """Set with_adapter configuration."""
        if with_adapter_cfg is not None:
            if isinstance(with_adapter_cfg, WithAdapterConfig):
                self.config.with_adapter = _safe_copy(with_adapter_cfg)
                self.config.with_adapter_override_raw = with_adapter_cfg.to_dict()
            else:
                merge_run_config_with_kwargs(
                    self.config,
                    {"with_adapter_cfg": with_adapter_cfg},
                )
                self.config.with_adapter_override_raw = dict(with_adapter_cfg)
        return self

    def with_pipeline_adapter_cfg(
        self, pipeline_adapter_cfg: Any | None
    ) -> "RunConfigBuilder":
        """Set pipeline adapter configuration."""
        if pipeline_adapter_cfg is not None:
            if hasattr(pipeline_adapter_cfg, "to_dict"):
                self.config.pipeline_adapter_cfg = _safe_copy(pipeline_adapter_cfg)
                self.config.pipeline_adapter_cfg_override_raw = (
                    pipeline_adapter_cfg.to_dict()
                )
            else:
                merge_run_config_with_kwargs(
                    self.config,
                    {"pipeline_adapter_cfg": pipeline_adapter_cfg},
                )
                self.config.pipeline_adapter_cfg_override_raw = dict(
                    pipeline_adapter_cfg
                )
        return self

    def with_project_adapter_cfg(
        self, project_adapter_cfg: Any | None
    ) -> "RunConfigBuilder":
        """Set project adapter configuration."""
        if project_adapter_cfg is not None:
            if hasattr(project_adapter_cfg, "to_dict"):
                self.config.project_adapter_cfg = _safe_copy(project_adapter_cfg)
                self.config.project_adapter_cfg_override_raw = (
                    project_adapter_cfg.to_dict()
                )
            else:
                merge_run_config_with_kwargs(
                    self.config,
                    {"project_adapter_cfg": project_adapter_cfg},
                )
                self.config.project_adapter_cfg_override_raw = dict(
                    project_adapter_cfg
                )
        return self

    def with_reload(self, reload: bool | None) -> "RunConfigBuilder":
        """Set reload flag."""
        if reload is not None:
            self.config.reload = reload
            _mark_explicit_override(self.config, "reload")
        return self

    def with_log_level(self, log_level: str | None) -> "RunConfigBuilder":
        """Set log level (alias for with_logging)."""
        return self.with_logging(log_level)

    def with_max_retries(self, max_retries: int | None) -> "RunConfigBuilder":
        """Set max retries."""
        return self.with_retry_config(max_retries=max_retries)

    def with_retry_delay(self, retry_delay: float | None) -> "RunConfigBuilder":
        """Set retry delay."""
        return self.with_retry_config(retry_delay=retry_delay)

    def with_jitter_factor(self, jitter_factor: float | None) -> "RunConfigBuilder":
        """Set jitter factor."""
        return self.with_retry_config(jitter_factor=jitter_factor)

    def with_retry_exceptions(
        self, retry_exceptions: list | None
    ) -> "RunConfigBuilder":
        """Set retry exceptions."""
        return self.with_retry_config(retry_exceptions=retry_exceptions)

    def with_on_success(self, on_success: Any | None) -> "RunConfigBuilder":
        """Set on_success callback."""
        if on_success is not None:
            self.config.on_success = _normalize_callback_spec(on_success)
            _mark_explicit_override(self.config, "on_success")
        return self

    def with_on_failure(self, on_failure: Any | None) -> "RunConfigBuilder":
        """Set on_failure callback."""
        if on_failure is not None:
            self.config.on_failure = _normalize_callback_spec(on_failure)
            _mark_explicit_override(self.config, "on_failure")
        return self

    def reset(self) -> "RunConfigBuilder":
        """Reset builder to default values."""
        self.config = RunConfig()
        return self

    @classmethod
    def from_config(cls, config: RunConfig) -> "RunConfigBuilder":
        """Create builder from existing config."""
        return cls(base_config=config)

    def build(self) -> RunConfig:
        """Build and return the RunConfig object."""
        built = clone_run_config(self.config)
        built.on_success = _normalize_callback_spec(built.on_success)
        built.on_failure = _normalize_callback_spec(built.on_failure)
        return built
