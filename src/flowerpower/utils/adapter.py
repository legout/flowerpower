"""
Adapter utilities for FlowerPower pipeline management.

This module provides helper classes for managing adapter configurations
and creating adapter instances with proper error handling and validation.
"""

import sys
from typing import Any, Dict, Optional

import msgspec
from loguru import logger


class AdapterManager:
    """
    Helper class for adapter configuration and instance creation.

    This class centralizes adapter configuration merging, validation,
    and instance creation to reduce complexity in the Pipeline class.
    """

    def __init__(self):
        """Initialize the adapter manager."""
        self._adapter_cache: Dict[str, Any] = {}

    def _merge_configs(self, base_config: Any, override_config: Any) -> Any:
        """Merge override config into base config."""
        if not override_config:
            return base_config
        return base_config.merge(override_config) if base_config else override_config

    def resolve_with_adapter_config(
        self,
        with_adapter_cfg: dict | Any | None,
        base_config: Any
    ) -> Any:
        """
        Resolve and merge WithAdapterConfig.

        Args:
            with_adapter_cfg: Input configuration (dict or instance)
            base_config: Base configuration to merge with

        Returns:
            WithAdapterConfig: Merged configuration
        """
        from ..cfg.pipeline.run import WithAdapterConfig

        if with_adapter_cfg:
            if isinstance(with_adapter_cfg, dict):
                with_adapter_cfg = WithAdapterConfig.from_dict(with_adapter_cfg)
            elif not isinstance(with_adapter_cfg, WithAdapterConfig):
                raise TypeError(
                    "with_adapter must be a dictionary or WithAdapterConfig instance."
                )

            return self._merge_configs(base_config, with_adapter_cfg)

        return base_config

    def resolve_pipeline_adapter_config(
        self,
        pipeline_adapter_cfg: dict | Any | None,
        base_config: Any
    ) -> Any:
        """
        Resolve and merge PipelineAdapterConfig.

        Args:
            pipeline_adapter_cfg: Input configuration (dict or instance)
            base_config: Base configuration to merge with

        Returns:
            PipelineAdapterConfig: Merged configuration
        """
        from ..cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig

        if pipeline_adapter_cfg:
            if isinstance(pipeline_adapter_cfg, dict):
                pipeline_adapter_cfg = PipelineAdapterConfig.from_dict(
                    pipeline_adapter_cfg
                )
            elif not isinstance(pipeline_adapter_cfg, PipelineAdapterConfig):
                raise TypeError(
                    "pipeline_adapter_cfg must be a dictionary or PipelineAdapterConfig instance."
                )

            return self._merge_configs(base_config, pipeline_adapter_cfg)

        return base_config

    def resolve_project_adapter_config(
        self,
        project_adapter_cfg: dict | Any | None,
        project_context: Any
    ) -> Any:
        """
        Resolve and merge ProjectAdapterConfig from project context.

        Args:
            project_adapter_cfg: Input configuration (dict or instance)
            project_context: Project context to extract base config from

        Returns:
            ProjectAdapterConfig: Merged configuration
        """
        from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig

        # Get base configuration from project context
        base_cfg = self._extract_project_adapter_config(project_context)

        if project_adapter_cfg:
            if isinstance(project_adapter_cfg, dict):
                project_adapter_cfg = ProjectAdapterConfig.from_dict(
                    project_adapter_cfg
                )
            elif not isinstance(project_adapter_cfg, ProjectAdapterConfig):
                raise TypeError(
                    "project_adapter_cfg must be a dictionary or ProjectAdapterConfig instance."
                )

            return self._merge_configs(base_cfg, project_adapter_cfg)
        else:
            # Use base configuration or create default
            return base_cfg or ProjectAdapterConfig()

    def _extract_project_adapter_config(
        self,
        project_context: Any
    ) -> Optional[Any]:
        """
        Extract adapter configuration from project context.

        Args:
            project_context: Project context (PipelineManager or FlowerPowerProject)

        Returns:
            ProjectAdapterConfig or None: Extracted configuration
        """
        # Try direct access to project config
        project_cfg = getattr(project_context, "project_cfg", None) or getattr(project_context, "_project_cfg", None)
        if project_cfg and hasattr(project_cfg, "adapter"):
            return project_cfg.adapter

        # Try via pipeline_manager if available
        if hasattr(project_context, "pipeline_manager"):
            pm = project_context.pipeline_manager
            pm_cfg = getattr(pm, "project_cfg", None) or getattr(pm, "_project_cfg", None)
            if pm_cfg and hasattr(pm_cfg, "adapter"):
                return pm_cfg.adapter

        return None

    def create_adapters(
        self,
        with_adapter_cfg: Any,
        pipeline_adapter_cfg: Any,
        project_adapter_cfg: Any
    ) -> list:
        """
        Create adapter instances based on configurations.

        Args:
            with_adapter_cfg: WithAdapter configuration
            pipeline_adapter_cfg: Pipeline adapter configuration
            project_adapter_cfg: Project adapter configuration

        Returns:
            list: List of adapter instances
        """
        adapters = []

        # Hamilton Tracker adapter
        if with_adapter_cfg.hamilton_tracker:
            adapter = self._create_hamilton_tracker(
                pipeline_adapter_cfg.hamilton_tracker,
                project_adapter_cfg.hamilton_tracker
            )
            if adapter:
                adapters.append(adapter)

        # MLFlow adapter
        if with_adapter_cfg.mlflow:
            adapter = self._create_mlflow_adapter(
                pipeline_adapter_cfg.mlflow,
                project_adapter_cfg.mlflow
            )
            if adapter:
                adapters.append(adapter)

        # OpenTelemetry adapter
        if with_adapter_cfg.opentelemetry:
            adapter = self._create_opentelemetry_adapter(
                pipeline_adapter_cfg.opentelemetry,
                project_adapter_cfg.opentelemetry
            )
            if adapter:
                adapters.append(adapter)

        return adapters

    def _create_hamilton_tracker(
        self,
        pipeline_config: Any,
        project_config: Any
    ) -> Optional[Any]:
        """Create HamiltonTracker adapter instance."""
        try:
            from hamilton.adapters import HamiltonTracker
            from hamilton import constants
            from ..settings import settings
        except ImportError:
            logger.warning("Hamilton tracker dependencies not installed")
            return None

        tracker_kwargs = project_config.to_dict()
        tracker_kwargs.update(pipeline_config.to_dict())
        tracker_kwargs["hamilton_api_url"] = tracker_kwargs.pop("api_url", None)
        tracker_kwargs["hamilton_ui_url"] = tracker_kwargs.pop("ui_url", None)

        # Set capture constants
        constants.MAX_DICT_LENGTH_CAPTURE = (
            tracker_kwargs.pop("max_dict_length_capture", None)
            or settings.HAMILTON_MAX_DICT_LENGTH_CAPTURE
        )
        constants.MAX_LIST_LENGTH_CAPTURE = (
            tracker_kwargs.pop("max_list_length_capture", None)
            or settings.HAMILTON_MAX_LIST_LENGTH_CAPTURE
        )
        constants.CAPTURE_DATA_STATISTICS = (
            tracker_kwargs.pop("capture_data_statistics", None)
            or settings.HAMILTON_CAPTURE_DATA_STATISTICS
        )

        return HamiltonTracker(**tracker_kwargs)

    def _create_mlflow_adapter(
        self,
        pipeline_config: Any,
        project_config: Any
    ) -> Optional[Any]:
        """Create MLFlow adapter instance."""
        try:
            from hamilton.experimental import h_mlflow
        except ImportError:
            logger.warning("MLFlow is not installed. Skipping MLFlow adapter.")
            return None

        mlflow_kwargs = project_config.to_dict()
        mlflow_kwargs.update(pipeline_config.to_dict())
        return h_mlflow.MLFlowTracker(**mlflow_kwargs)

    def _create_opentelemetry_adapter(
        self,
        pipeline_config: Any,
        project_config: Any
    ) -> Optional[Any]:
        """Create OpenTelemetry adapter instance."""
        try:
            from hamilton.experimental import h_opentelemetry
            from ..utils.open_telemetry import init_tracer
        except ImportError:
            logger.warning(
                "OpenTelemetry is not installed. Skipping OpenTelemetry adapter."
            )
            return None

        otel_kwargs = project_config.to_dict()
        otel_kwargs.update(pipeline_config.to_dict())
        init_tracer()
        return h_opentelemetry.OpenTelemetryTracker(**otel_kwargs)

    def clear_cache(self) -> None:
        """Clear the adapter cache."""
        self._adapter_cache.clear()


def create_adapter_manager() -> AdapterManager:
    """
    Factory function to create an AdapterManager instance.

    Returns:
        AdapterManager: Configured manager instance
    """
    return AdapterManager()