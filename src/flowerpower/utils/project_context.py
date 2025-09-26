"""
Project context resolution utilities for FlowerPower.

This module provides helper classes for resolving project configurations
from different context types (PipelineManager, FlowerPowerProject, etc.).
"""

from typing import Any, Optional


class ProjectContextResolver:
    """
    Helper class for resolving project configurations from various context types.

    This class centralizes the logic for extracting project configurations
    from different context objects to reduce code duplication.
    """

    def __init__(self):
        """Initialize the project context resolver."""
        self._config_cache: dict[int, Any] = {}

    def get_project_config(self, project_context: Any) -> Optional[Any]:
        """
        Get project configuration from project context.

        Args:
            project_context: Project context object

        Returns:
            Project configuration or None if not found
        """
        # Check cache first
        context_id = id(project_context)
        if context_id in self._config_cache:
            return self._config_cache[context_id]

        # Extract project config
        config = self._extract_project_config(project_context)
        if config is not None:
            self._config_cache[context_id] = config

        return config

    def get_project_adapter_config(self, project_context: Any) -> Optional[Any]:
        """
        Get project adapter configuration from project context.

        Args:
            project_context: Project context object

        Returns:
            ProjectAdapterConfig or None if not found
        """
        project_config = self.get_project_config(project_context)
        if project_config and hasattr(project_config, "adapter"):
            return project_config.adapter
        return None

    def has_project_manager(self, project_context: Any) -> bool:
        """
        Check if project context has a pipeline manager.

        Args:
            project_context: Project context object

        Returns:
            bool: True if pipeline manager is available
        """
        return hasattr(project_context, "pipeline_manager")

    def get_pipeline_manager_config(self, project_context: Any) -> Optional[Any]:
        """
        Get configuration from pipeline manager in project context.

        Args:
            project_context: Project context object

        Returns:
            Pipeline manager configuration or None
        """
        if not self.has_project_manager(project_context):
            return None

        return getattr(
            project_context.pipeline_manager, "project_cfg", None
        ) or getattr(
            project_context.pipeline_manager, "_project_cfg", None
        )

    def _extract_project_config(
        self,
        project_context: Any
    ) -> Optional[Any]:
        """
        Extract project configuration from context.

        Args:
            project_context: Project context object

        Returns:
            Project configuration or None
        """
        # Handle temporary case where project_context is PipelineManager
        manager_cfg = getattr(
            project_context, "project_cfg", None
        ) or getattr(project_context, "_project_cfg", None)

        if manager_cfg:
            return manager_cfg

        # Use project context directly if it's FlowerPowerProject
        if self.has_project_manager(project_context):
            return self.get_pipeline_manager_config(project_context)

        return None

    def create_default_adapter_config(self) -> Any:
        """
        Create a default adapter configuration.

        Returns:
            ProjectAdapterConfig: Default configuration
        """
        from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
        return ProjectAdapterConfig()

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._config_cache.clear()

    def resolve_adapter_config_with_context(
        self,
        adapter_cfg: Any,
        project_context: Any
    ) -> Any:
        """
        Resolve adapter configuration with project context.

        Args:
            adapter_cfg: Input adapter configuration
            project_context: Project context

        Returns:
            ProjectAdapterConfig: Resolved configuration
        """
        from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig

        # Get base configuration from context
        base_cfg = self.get_project_adapter_config(project_context)

        if adapter_cfg:
            if isinstance(adapter_cfg, dict):
                adapter_cfg = ProjectAdapterConfig.from_dict(adapter_cfg)
            elif not isinstance(adapter_cfg, ProjectAdapterConfig):
                raise TypeError(
                    "adapter_cfg must be a dictionary or ProjectAdapterConfig instance."
                )

            # Merge with base configuration if available
            if base_cfg:
                return base_cfg.merge(adapter_cfg)

            return adapter_cfg
        else:
            # Use base configuration or create default
            return base_cfg or self.create_default_adapter_config()


def create_project_context_resolver() -> ProjectContextResolver:
    """
    Factory function to create a ProjectContextResolver instance.

    Returns:
        ProjectContextResolver: Configured resolver instance
    """
    return ProjectContextResolver()