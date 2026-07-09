"""Orchestrates pipeline execution."""

from __future__ import annotations

from types import ModuleType
from typing import TYPE_CHECKING, Any

from hamilton import driver
from hamilton.execution import executors
from loguru import logger

from ..cfg.pipeline.run import RunConfig
from ..settings import PIPELINES_DIR
from ..utils.config import (
    clone_run_config,
    merge_run_config_with_kwargs,
    validate_resolved_run_config,
)
from ..utils.logging import ensure_logging_initialized, setup_logging
from .execution_context import ExecutionContextBuilder
from .module_resolver import PipelineModuleResolver
from .retry import RetryManager

if TYPE_CHECKING:
    from .pipeline import Pipeline

try:  # Optional import; handled gracefully in async path
    from hamilton import async_driver as hamilton_async_driver
except ImportError:  # pragma: no cover - handled at runtime
    hamilton_async_driver = None


class PipelineRunner:
    """Facade responsible for executing a single pipeline instance."""

    def __init__(self, pipeline: Pipeline) -> None:
        self._pipeline = pipeline
        ensure_logging_initialized()

    def run(self, run_config: RunConfig | None = None, **kwargs) -> dict[str, Any]:
        configured_run = self._prepare_run_config(run_config, kwargs)
        context_builder = self._build_context_builder()

        modules = self._resolve_modules(configured_run)

        if configured_run.log_level:
            setup_logging(level=configured_run.log_level)

        retry_manager = self._create_retry_manager(configured_run)

        def operation() -> dict[str, Any]:
            return self._execute_sync(context_builder, configured_run, modules)

        return retry_manager.execute(
            operation=operation,
            on_success=configured_run.on_success,
            on_failure=configured_run.on_failure,
            context_name=self._pipeline.name,
        )

    async def run_async(
        self, run_config: RunConfig | None = None, **kwargs
    ) -> dict[str, Any]:
        configured_run = self._prepare_run_config(run_config, kwargs)
        context_builder = self._build_context_builder()

        modules = self._resolve_modules(configured_run)

        if configured_run.log_level:
            setup_logging(level=configured_run.log_level)
        retry_manager = self._create_retry_manager(configured_run)

        use_async_driver = configured_run.async_driver
        if use_async_driver is None:
            use_async_driver = True
        if not use_async_driver:
            raise ValueError(
                "Asynchronous execution requires RunConfig.async_driver=True. "
                "Set async_driver to True or invoke PipelineManager.run for synchronous execution."
            )

        async_driver_module = self._get_async_driver_module()

        async def operation_async() -> dict[str, Any]:
            return await self._execute_async(
                context_builder,
                configured_run,
                modules,
                async_driver_module,
            )

        return await retry_manager.execute_async(
            operation=operation_async,
            on_success=configured_run.on_success,
            on_failure=configured_run.on_failure,
            context_name=self._pipeline.name,
        )

    def _prepare_run_config(
        self, run_config: RunConfig | None, overrides: dict[str, Any]
    ) -> RunConfig:
        configured = clone_run_config(run_config or self._pipeline.config.run)
        if overrides:
            configured = merge_run_config_with_kwargs(configured, overrides)
        validate_resolved_run_config(configured)
        return configured

    def _build_context_builder(self) -> ExecutionContextBuilder:
        return ExecutionContextBuilder(
            executor_factory=self._pipeline.executor_factory,
            adapter_manager=self._pipeline.adapter_manager,
            pipeline_config=self._pipeline.config,
            project_context=self._pipeline.project_context,
        )

    def _create_retry_manager(self, run_config: RunConfig) -> RetryManager:
        retry_cfg = run_config.retry or self._pipeline.config.run.retry
        retry_config = retry_cfg
        return RetryManager(
            max_retries=retry_config.max_retries,
            retry_delay=retry_config.retry_delay,
            jitter_factor=retry_config.jitter_factor,
            retry_exceptions=tuple(retry_config.retry_exceptions),
        )

    def _execute_sync(
        self,
        context_builder: ExecutionContextBuilder,
        run_config: RunConfig,
        modules: list[ModuleType],
    ) -> dict[str, Any]:
        executor, shutdown, adapters = context_builder.build(run_config)
        synchronous_executor = run_config.executor.type in (
            "synchronous",
            "local",
            None,
        )

        allow_experimental_mode = True
        try:
            dr_builder = (
                driver.Builder()
                .with_modules(*modules)
                .with_config(run_config.config)
                .with_adapters(*adapters)
                .enable_dynamic_execution(
                    allow_experimental_mode=allow_experimental_mode
                )
                .with_local_executor(executors.SynchronousLocalTaskExecutor())
            )
            if not synchronous_executor:
                dr_builder = dr_builder.with_remote_executor(executor)

            dr = dr_builder.build()
            return dr.execute(
                final_vars=run_config.final_vars,
                inputs=run_config.inputs,
            )
        finally:
            if shutdown:
                try:
                    shutdown()
                except Exception as error:  # pragma: no cover - defensive
                    logger.warning(
                        "Failed to shutdown executor for pipeline '{name}': {error}",
                        name=self._pipeline.name,
                        error=error,
                    )

    async def _execute_async(
        self,
        context_builder: ExecutionContextBuilder,
        run_config: RunConfig,
        modules: list[ModuleType],
        async_driver_module,
    ) -> dict[str, Any]:
        executor, shutdown, adapters = context_builder.build(run_config)
        synchronous_executor = run_config.executor.type in (
            "synchronous",
            "local",
            None,
        )
        allow_experimental_mode = True

        try:
            dr_builder = (
                async_driver_module.Builder()
                .with_modules(*modules)
                .with_config(run_config.config)
                .with_adapters(*adapters)
                .enable_dynamic_execution(
                    allow_experimental_mode=allow_experimental_mode
                )
                .with_local_executor(executors.SynchronousLocalTaskExecutor())
            )
            if not synchronous_executor:
                dr_builder = dr_builder.with_remote_executor(executor)

            dr = await dr_builder.build()
            return await dr.execute(
                final_vars=run_config.final_vars,
                inputs=run_config.inputs,
            )
        finally:
            if shutdown:
                try:
                    shutdown()
                except Exception as error:  # pragma: no cover - defensive
                    logger.warning(
                        "Failed to shutdown executor for pipeline '{name}': {error}",
                        name=self._pipeline.name,
                        error=error,
                    )

    def _resolve_modules(self, run_config: RunConfig) -> list[ModuleType]:
        resolver = PipelineModuleResolver(self._resolve_pipelines_dir())
        additional = run_config.additional_modules or []
        if isinstance(additional, (str, bytes)):
            additional = [additional]
        return resolver.resolve(
            self._pipeline.module,
            additional=additional,
            reload=run_config.reload,
        )

    def _resolve_pipelines_dir(self) -> str | None:
        """Determine the configured pipelines directory for module resolution.

        Delegates package-root normalization to the resolver; this method only
        figures out *which* directory fragment to use.
        """
        context = self._pipeline.project_context
        pipelines_dir = getattr(context, "pipelines_dir", None)
        if isinstance(pipelines_dir, str):
            return pipelines_dir
        manager = getattr(context, "pipeline_manager", None)
        pipelines_dir = getattr(manager, "_pipelines_dir", None)
        if isinstance(pipelines_dir, str):
            return pipelines_dir
        module_name = getattr(self._pipeline.module, "__name__", "")
        if isinstance(module_name, str) and "." in module_name:
            return module_name.split(".", 1)[0]
        return PIPELINES_DIR

    def _get_async_driver_module(self):
        if hamilton_async_driver is None:
            raise ImportError(
                "Hamilton's async driver is unavailable. Upgrade the 'hamilton' package "
                "to a version that provides hamilton.async_driver (e.g., pip install -U hamilton)."
            )
        return hamilton_async_driver
