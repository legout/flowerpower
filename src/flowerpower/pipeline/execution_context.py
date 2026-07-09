"""Execution context utilities for pipeline runs."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from hamilton.execution import executors as h_executors
from loguru import logger

from ..cfg.pipeline.run import ExecutorConfig, RunConfig
from .adapter_provider import ResolvedAdapterSet, resolve_run_config_adapter_configs

__all__ = ["ExecutionContextBuilder", "resolve_run_config_adapter_configs"]


class ExecutionContextBuilder:
    """Builds the executor + adapter context required for a pipeline run."""

    def __init__(
        self,
        *,
        executor_factory: Any,
        adapter_manager: Any = None,
        pipeline_config: Any = None,
        project_context: Any = None,
    ) -> None:
        self._executor_factory = executor_factory
        self._adapter_manager = adapter_manager
        self._pipeline_config = pipeline_config
        self._project_context = project_context

    def build(
        self,
        run_config: RunConfig,
        adapter_set: ResolvedAdapterSet,
    ) -> tuple[h_executors.BaseExecutor, Callable | None, list]:
        """Create executor, shutdown function, and adapters for a pipeline run."""
        executor_cfg = run_config.executor or ExecutorConfig()
        executor, cleanup_fn = self._create_executor(
            executor_cfg,
            adapter_set.project_adapter_cfg,
        )
        adapters = list(adapter_set.runtime_adapters)
        logger.debug(
            "Execution context created. executor={executor} adapters={adapters}",
            executor=executor_cfg.type,
            adapters=[type(adapter).__name__ for adapter in adapters],
        )
        return executor, cleanup_fn, adapters

    def _create_executor(
        self,
        executor_cfg: ExecutorConfig,
        project_adapter_cfg: Any = None,
    ) -> tuple[h_executors.BaseExecutor, Callable | None]:
        executor = self._executor_factory.create_executor(executor_cfg)
        cleanup_fn = None

        # Only ray currently needs special shutdown handling. Use the resolved
        # project adapter config instead of peeking into project context shape.
        ray_module = self._get_optional_ray()
        ray_cfg = getattr(project_adapter_cfg, "ray", None)
        if executor_cfg.type == "ray" and ray_module is not None and ray_cfg is not None:
            should_shutdown = getattr(ray_cfg, "shutdown_ray_on_completion", False)
            cleanup_fn = ray_module.shutdown if should_shutdown else None
        return executor, cleanup_fn


    @staticmethod
    def _get_optional_ray():
        try:
            import importlib.util

            if importlib.util.find_spec("ray"):
                import ray  # type: ignore

                return ray
        except Exception:  # pragma: no cover - defensive import shield
            return None
        return None


