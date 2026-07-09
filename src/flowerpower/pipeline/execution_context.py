"""Execution context utilities for pipeline runs."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from hamilton.execution import executors as h_executors
from loguru import logger

from ..cfg.pipeline.run import ExecutorConfig, RunConfig
from ..utils.adapter import AdapterManager


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

    def build(
        self, run_config: RunConfig
    ) -> tuple[h_executors.BaseExecutor, Callable | None, list]:
        """Create executor, shutdown function, and adapters for a pipeline run."""
        executor_cfg = run_config.executor or ExecutorConfig()
        executor, cleanup_fn = self._create_executor(
            executor_cfg,
            run_config.project_adapter_cfg,
        )
        adapters = self._create_adapters(run_config)
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

    def _create_adapters(self, run_config: RunConfig) -> list:
        with_adapter_cfg = run_config.with_adapter

        pipeline_adapter_cfg = run_config.pipeline_adapter_cfg
        if pipeline_adapter_cfg is None:
            from ..cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
            pipeline_adapter_cfg = PipelineAdapterConfig()

        project_adapter_cfg = run_config.project_adapter_cfg
        if project_adapter_cfg is None:
            from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
            project_adapter_cfg = ProjectAdapterConfig()

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


def resolve_run_config_adapter_configs(
    run_config: RunConfig,
    pipeline_config: Any,
    project_adapter_base: Any = None,
) -> RunConfig:
    """Merge pipeline and project adapter defaults into a resolved RunConfig.

    This resolution must happen before runtime object construction so that the
    execution-context builder can consume the resolved RunConfig values without
    re-deciding precedence against pipeline defaults.
    """
    explicit_overrides = set(run_config.explicit_overrides or [])
    manager = AdapterManager()
    if pipeline_config is not None:
        pipeline_adapter = getattr(pipeline_config, "adapter", None)
        if pipeline_adapter is not None and not (
            "pipeline_adapter_cfg" in explicit_overrides
            and run_config.pipeline_adapter_cfg is None
        ):
            run_config.pipeline_adapter_cfg = manager.resolve_pipeline_adapter_config(
                run_config.pipeline_adapter_cfg, pipeline_adapter
            )

    if not (
        "project_adapter_cfg" in explicit_overrides
        and run_config.project_adapter_cfg is None
    ):
        run_config.project_adapter_cfg = manager.resolve_project_adapter_config(
            run_config.project_adapter_cfg, project_adapter_base
        )
    return run_config
