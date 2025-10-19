"""Orchestrates pipeline execution."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from hamilton import driver
from hamilton.execution import executors
from loguru import logger

from ..cfg.pipeline.run import RunConfig
from ..utils.config import merge_run_config_with_kwargs
from ..utils.logging import ensure_logging_initialized, setup_logging
from .execution_context import ExecutionContextBuilder
from .retry import RetryManager

if TYPE_CHECKING:
    from .pipeline import Pipeline


class PipelineRunner:
    """Facade responsible for executing a single pipeline instance."""

    def __init__(self, pipeline: "Pipeline") -> None:
        self._pipeline = pipeline
        ensure_logging_initialized()

    def run(self, run_config: RunConfig | None = None, **kwargs) -> dict[str, Any]:
        configured_run = self._prepare_run_config(run_config, kwargs)
        context_builder = self._build_context_builder()

        if configured_run.log_level:
            setup_logging(level=configured_run.log_level)
        if configured_run.reload:
            self._reload_pipeline_module()

        retry_manager = self._create_retry_manager(configured_run)
        operation = lambda: self._execute_sync(context_builder, configured_run)
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

        if configured_run.reload:
            self._reload_pipeline_module()

        if configured_run.log_level:
            setup_logging(level=configured_run.log_level)
        retry_manager = self._create_retry_manager(configured_run)

        async def operation_async() -> dict[str, Any]:
            return await self._execute_async(context_builder, configured_run)

        return await retry_manager.execute_async(
            operation=operation_async,
            on_success=configured_run.on_success,
            on_failure=configured_run.on_failure,
            context_name=self._pipeline.name,
        )

    def _prepare_run_config(
        self, run_config: RunConfig | None, overrides: dict[str, Any]
    ) -> RunConfig:
        configured = run_config or self._pipeline.config.run
        if overrides:
            configured = merge_run_config_with_kwargs(configured, overrides)
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
        self, context_builder: ExecutionContextBuilder, run_config: RunConfig
    ) -> dict[str, Any]:
        executor, shutdown, adapters = context_builder.build(run_config)
        synchronous_executor = run_config.executor.type in ("synchronous", None)

        allow_experimental_mode = True
        try:
            dr_builder = (
                driver.Builder()
                .with_modules(self._pipeline.module)
                .with_config(run_config.config)
                .with_adapters(*adapters)
                .enable_dynamic_execution(
                    allow_experimental_mode=allow_experimental_mode
                )
                .with_local_executor(executors.SynchronousLocalTaskExecutor())
            )
            # if not synchronous_executor:
            dr_builder = dr_builder.with_remote_executor(executor)
            # else:
            #    dr_builder = dr_builder.with_remote_executor(
            #        executors.SynchronousLocalTaskExecutor()
            #    )

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
        self, context_builder: ExecutionContextBuilder, run_config: RunConfig
    ) -> dict[str, Any]:
        executor, shutdown, adapters = context_builder.build(run_config)
        synchronous_executor = run_config.executor.type in ("synchronous", None)
        allow_experimental_mode = True

        try:
            dr_builder = (
                driver.Builder()
                .with_modules(self._pipeline.module)
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
            return await dr.execute_async(
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

    def _reload_pipeline_module(self) -> None:
        try:
            importlib.reload(self._pipeline.module)
            logger.debug(
                "Reloaded module for pipeline '{name}'", name=self._pipeline.name
            )
        except Exception as error:
            logger.error(
                "Failed to reload module for pipeline '{name}': {error}",
                name=self._pipeline.name,
                error=error,
            )
            raise
