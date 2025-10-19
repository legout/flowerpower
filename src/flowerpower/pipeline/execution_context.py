"""Execution context utilities for pipeline runs."""

from __future__ import annotations

from typing import Any, Callable

from hamilton.execution import executors as h_executors
from loguru import logger

from ..cfg.pipeline.run import ExecutorConfig, RunConfig
from ..utils.config import resolve_executor_config


class ExecutionContextBuilder:
    """Builds the executor + adapter context required for a pipeline run."""

    def __init__(
        self,
        *,
        executor_factory: Any,
        adapter_manager: Any,
        pipeline_config: Any,
        project_context: Any,
    ) -> None:
        self._executor_factory = executor_factory
        self._adapter_manager = adapter_manager
        self._pipeline_config = pipeline_config
        self._project_context = project_context

    def build(self, run_config: RunConfig) -> tuple[h_executors.BaseExecutor, Callable | None, list]:
        """Create executor, shutdown function, and adapters for a pipeline run."""
        executor_cfg = resolve_executor_config(
            base=self._pipeline_config.run.executor,
            override=run_config.executor_override_raw or run_config.executor,
        )
        executor, cleanup_fn = self._create_executor(executor_cfg)
        adapters = self._create_adapters(run_config)
        logger.debug(
            "Execution context created. executor={executor} adapters={adapters}",
            executor=executor_cfg.type,
            adapters=[type(adapter).__name__ for adapter in adapters],
        )
        return executor, cleanup_fn, adapters

    def _create_executor(
        self, executor_cfg: ExecutorConfig
    ) -> tuple[h_executors.BaseExecutor, Callable | None]:
        executor = self._executor_factory.create_executor(executor_cfg)
        cleanup_fn = None

        # Only ray currently needs special shutdown handling
        ray_module = self._get_optional_ray()
        if executor_cfg.type == "ray" and ray_module is not None:
            project_cfg = getattr(self._project_context, "project_cfg", None) or getattr(
                self._project_context, "_project_cfg", None
            )
            if project_cfg and getattr(project_cfg.adapter, "ray", None):
                should_shutdown = getattr(
                    project_cfg.adapter.ray, "shutdown_ray_on_completion", False
                )
                cleanup_fn = ray_module.shutdown if should_shutdown else None

        return executor, cleanup_fn

    def _create_adapters(self, run_config: RunConfig) -> list:
        with_adapter_cfg = self._adapter_manager.resolve_with_adapter_config(
            run_config.with_adapter, self._pipeline_config.run.with_adapter
        )

        pipeline_adapter_cfg = self._adapter_manager.resolve_pipeline_adapter_config(
            run_config.pipeline_adapter_cfg, self._pipeline_config.adapter
        )

        project_adapter_cfg = self._adapter_manager.resolve_project_adapter_config(
            run_config.project_adapter_cfg, self._project_context
        )

        adapters = self._adapter_manager.create_adapters(
            with_adapter_cfg, pipeline_adapter_cfg, project_adapter_cfg
        )

        if run_config.adapter:
            adapters.extend(run_config.adapter.values())

        return adapters

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
