"""
Environment overlay utilities for FlowerPower.

Features:
- Parse namespaced env vars into nested dicts using double-underscore separators.
- Support global FP_* shims (e.g., FP_LOG_LEVEL) and namespaced forms
  (FP_PROJECT__..., FP_PIPELINE__...).
- Coerce scalar types (int, float, bool) and JSON objects/arrays for rich values.
- Merge overrides into msgspec-based config structs with clear precedence.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Mapping
import warnings


def _coerce_value(raw: str) -> Any:
    s = raw.strip()
    # JSON object/array/bool/null/number
    try:
        if (s and s[0] in "[{") or s in ("true", "false", "null") or re.fullmatch(r"-?\d+(\.\d+)?", s):
            return json.loads(s)
    except Exception:
        pass
    # Strict bools
    low = s.lower()
    if low in ("true", "false"):
        return low == "true"
    # Int
    if re.fullmatch(r"-?\d+", s):
        try:
            return int(s)
        except Exception:
            return raw
    # Float
    if re.fullmatch(r"-?\d+\.\d+", s):
        try:
            return float(s)
        except Exception:
            return raw
    # Comma-list fallback (strings)
    if "," in s:
        return [part.strip() for part in s.split(",")]
    return raw


def _set_nested(dct: dict, path: list[str], value: Any) -> None:
    cur = dct
    for key in path[:-1]:
        if key not in cur or not isinstance(cur[key], dict):
            cur[key] = {}
        cur = cur[key]
    cur[path[-1]] = value


def parse_env_overrides(env: Mapping[str, str] | None = None, prefix: str = "FP_") -> dict:
    """Parse env vars into nested overrides dict.

    Supports keys like:
    - FP_PROJECT__ADAPTER__HAMILTON_TRACKER__API_KEY
    - FP_PIPELINE__RUN__EXECUTOR__TYPE
    - FP_LOG_LEVEL (global shim)
    """
    env = dict(env or os.environ)
    overrides: dict[str, Any] = {}

    for key, raw in env.items():
        if not key.startswith(prefix):
            continue
        rest = key[len(prefix):]
        if not rest:
            continue
        value = _coerce_value(raw)
        # Namespaced?
        if "__" in rest:
            path = [p.lower() for p in rest.split("__")]
            _set_nested(overrides, path, value)
        else:
            # Global shim, keep upper for later mapping
            overrides.setdefault("_global", {})[rest] = value
    return overrides


def _merge_dict(target: dict, source: dict) -> dict:
    for k, v in source.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            _merge_dict(target[k], v)
        else:
            target[k] = v
    return target


def build_specific_overlays(overrides: dict) -> tuple[dict, dict]:
    """Return (project_overlay, pipeline_overlay) from parsed overrides.

    Example output paths (lowercased):
    - project: {"project": {"adapter": {"hamilton_tracker": {"api_key": "..."}}}}
    - pipeline: {"pipeline": {"run": {"log_level": "DEBUG"}}}
    """
    project: dict[str, Any] = {}
    pipeline: dict[str, Any] = {}

    # Project overlay
    if "project" in overrides:
        project = {"project": overrides["project"]}

    # Pipeline overlay
    if "pipeline" in overrides:
        pipeline = {"pipeline": overrides["pipeline"]}

    return project, pipeline


def apply_global_shims(overrides: dict, project_overlay: dict, pipeline_overlay: dict) -> None:
    """Map legacy global FP_* envs into reasonable defaults if specific keys are absent.

    Example mappings:
    - FP_LOG_LEVEL -> pipeline.run.log_level (only if not already set)
    - FP_EXECUTOR  -> pipeline.run.executor.type
    - FP_EXECUTOR_MAX_WORKERS -> pipeline.run.executor.max_workers
    - FP_EXECUTOR_NUM_CPUS    -> pipeline.run.executor.num_cpus
    - FP_MAX_RETRIES -> pipeline.run.retry.max_retries
    - FP_RETRY_DELAY -> pipeline.run.retry.retry_delay
    - FP_JITTER_FACTOR -> pipeline.run.retry.jitter_factor
    """
    g = overrides.get("_global", {})

    def ensure_path(base: dict, path: list[str]) -> dict:
        cur = base
        for p in path:
            if p not in cur or not isinstance(cur[p], dict):
                cur[p] = {}
            cur = cur[p]
        return cur

    if "LOG_LEVEL" in g:
        tgt = ensure_path(pipeline_overlay.setdefault("pipeline", {}), ["run"])
        tgt.setdefault("log_level", g["LOG_LEVEL"])

    if "EXECUTOR" in g:
        tgt = ensure_path(pipeline_overlay.setdefault("pipeline", {}), ["run", "executor"])
        tgt.setdefault("type", g["EXECUTOR"])
    if "EXECUTOR_MAX_WORKERS" in g:
        tgt = ensure_path(pipeline_overlay.setdefault("pipeline", {}), ["run", "executor"])
        tgt.setdefault("max_workers", g["EXECUTOR_MAX_WORKERS"])
    if "EXECUTOR_NUM_CPUS" in g:
        tgt = ensure_path(pipeline_overlay.setdefault("pipeline", {}), ["run", "executor"])
        tgt.setdefault("num_cpus", g["EXECUTOR_NUM_CPUS"])

    if "MAX_RETRIES" in g:
        warnings.warn(
            "Environment variable FP_MAX_RETRIES is deprecated; use FP_PIPELINE__RUN__RETRY__MAX_RETRIES instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        tgt = ensure_path(pipeline_overlay.setdefault("pipeline", {}), ["run", "retry"])
        tgt.setdefault("max_retries", g["MAX_RETRIES"])
    if "RETRY_DELAY" in g:
        warnings.warn(
            "Environment variable FP_RETRY_DELAY is deprecated; use FP_PIPELINE__RUN__RETRY__RETRY_DELAY instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        tgt = ensure_path(pipeline_overlay.setdefault("pipeline", {}), ["run", "retry"])
        tgt.setdefault("retry_delay", g["RETRY_DELAY"])
    if "JITTER_FACTOR" in g:
        warnings.warn(
            "Environment variable FP_JITTER_FACTOR is deprecated; use FP_PIPELINE__RUN__RETRY__JITTER_FACTOR instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        tgt = ensure_path(pipeline_overlay.setdefault("pipeline", {}), ["run", "retry"])
        tgt.setdefault("jitter_factor", g["JITTER_FACTOR"])


def merge_overlays_into_config(config_struct, project_overlay: dict, pipeline_overlay: dict):
    """Merge parsed overlays into a Config-like struct (has .project and .pipeline)."""
    # Use BaseConfig.merge_dict semantics via .update/merge_dict if present
    if hasattr(config_struct, "project") and project_overlay:
        cfg = getattr(config_struct, "project")
        if hasattr(cfg, "update"):
            cfg.update(project_overlay.get("project", {}))
    if hasattr(config_struct, "pipeline") and pipeline_overlay:
        cfg = getattr(config_struct, "pipeline")
        if hasattr(cfg, "update"):
            cfg.update(pipeline_overlay.get("pipeline", {}))
