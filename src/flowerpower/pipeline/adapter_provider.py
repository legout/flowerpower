"""Adapter resolution and construction for pipeline execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..cfg.pipeline.run import RunConfig, WithAdapterConfig
from ..utils.adapter import AdapterManager


@dataclass(frozen=True)
class ResolvedAdapterSet:
    """Resolved adapter configs and runtime adapter instances for a run."""

    with_adapter_cfg: WithAdapterConfig
    pipeline_adapter_cfg: Any
    project_adapter_cfg: Any
    runtime_adapters: list[Any]


class AdapterProvider:
    """Resolve adapter config precedence and construct runtime adapters."""

    def __init__(self, adapter_manager: AdapterManager | None = None) -> None:
        self._adapter_manager = adapter_manager or AdapterManager()

    def resolve(
        self,
        run_config: RunConfig,
        pipeline_config: Any,
        project_adapter_base: Any = None,
        *,
        construct_runtime: bool = True,
    ) -> ResolvedAdapterSet:
        """Resolve adapter configs into ``run_config`` and optionally create adapters."""
        explicit_overrides = set(run_config.explicit_overrides or [])

        pipeline_adapter_cfg = self._resolve_pipeline_adapter_config(
            run_config,
            pipeline_config,
            explicit_overrides,
        )
        project_adapter_cfg = self._resolve_project_adapter_config(
            run_config,
            project_adapter_base,
            explicit_overrides,
        )
        with_adapter_cfg = run_config.with_adapter or WithAdapterConfig()
        run_config.with_adapter = with_adapter_cfg

        runtime_adapters = (
            self._create_runtime_adapters(
                run_config,
                with_adapter_cfg,
                pipeline_adapter_cfg,
                project_adapter_cfg,
            )
            if construct_runtime
            else []
        )

        return ResolvedAdapterSet(
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            runtime_adapters=runtime_adapters,
        )

    def construct_runtime_adapters(
        self,
        run_config: RunConfig,
        adapter_set: ResolvedAdapterSet,
    ) -> ResolvedAdapterSet:
        """Construct runtime adapters for an already-resolved adapter set."""
        return ResolvedAdapterSet(
            with_adapter_cfg=adapter_set.with_adapter_cfg,
            pipeline_adapter_cfg=adapter_set.pipeline_adapter_cfg,
            project_adapter_cfg=adapter_set.project_adapter_cfg,
            runtime_adapters=self._create_runtime_adapters(
                run_config,
                adapter_set.with_adapter_cfg,
                adapter_set.pipeline_adapter_cfg,
                adapter_set.project_adapter_cfg,
            ),
        )

    def _create_runtime_adapters(
        self,
        run_config: RunConfig,
        with_adapter_cfg: WithAdapterConfig,
        pipeline_adapter_cfg: Any,
        project_adapter_cfg: Any,
    ) -> list[Any]:
        adapters = self._adapter_manager.create_adapters(
            with_adapter_cfg,
            pipeline_adapter_cfg,
            project_adapter_cfg,
        )
        if run_config.adapter:
            adapters.extend(run_config.adapter.values())
        return adapters

    def _resolve_pipeline_adapter_config(
        self,
        run_config: RunConfig,
        pipeline_config: Any,
        explicit_overrides: set[str],
    ) -> Any:
        from ..cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig

        pipeline_adapter_base = getattr(pipeline_config, "adapter", None)
        if pipeline_adapter_base is not None and not (
            "pipeline_adapter_cfg" in explicit_overrides
            and run_config.pipeline_adapter_cfg is None
        ):
            run_config.pipeline_adapter_cfg = (
                self._adapter_manager.resolve_pipeline_adapter_config(
                    run_config.pipeline_adapter_cfg,
                    pipeline_adapter_base,
                )
            )

        if run_config.pipeline_adapter_cfg is None:
            run_config.pipeline_adapter_cfg = PipelineAdapterConfig()
        return run_config.pipeline_adapter_cfg

    def _resolve_project_adapter_config(
        self,
        run_config: RunConfig,
        project_adapter_base: Any,
        explicit_overrides: set[str],
    ) -> Any:
        from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig

        if not (
            "project_adapter_cfg" in explicit_overrides
            and run_config.project_adapter_cfg is None
        ):
            run_config.project_adapter_cfg = (
                self._adapter_manager.resolve_project_adapter_config(
                    run_config.project_adapter_cfg,
                    project_adapter_base,
                )
            )

        if run_config.project_adapter_cfg is None:
            run_config.project_adapter_cfg = ProjectAdapterConfig()
        return run_config.project_adapter_cfg


def resolve_run_config_adapter_configs(
    run_config: RunConfig,
    pipeline_config: Any,
    project_adapter_base: Any = None,
) -> RunConfig:
    """Compatibility helper that resolves adapter configs without exposing adapters."""
    AdapterProvider().resolve(
        run_config,
        pipeline_config,
        project_adapter_base,
        construct_runtime=False,
    )
    return run_config
