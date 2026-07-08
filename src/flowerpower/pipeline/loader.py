"""Pipeline loader for configuration, module, and instance caching."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import msgspec
from fsspeckit import AbstractFileSystem
from loguru import logger

from ..cfg import PipelineConfig, ProjectConfig
from ..settings import HOOKS_DIR
from ..utils.security import validate_pipeline_name
from .config_manager import PipelineConfigManager
from .module_resolver import PipelineModuleResolver

if TYPE_CHECKING:
    from ..flowerpower import FlowerPowerProject
    from .pipeline import Pipeline

__all__ = ["CachedPipelineData", "PipelineLoader"]


class CachedPipelineData(msgspec.Struct):
    """Container for cached pipeline data."""

    pipeline: "Pipeline | None" = None
    config: PipelineConfig | None = None
    module: Any = None


class PipelineLoader:
    """Loads pipeline configurations, modules, and Pipeline instances."""

    def __init__(
        self,
        config_manager: PipelineConfigManager,
        module_resolver: PipelineModuleResolver,
        fs: AbstractFileSystem,
        project_cfg: ProjectConfig,
    ) -> None:
        self._config_manager = config_manager
        self._module_resolver = module_resolver
        self._fs = fs
        self.project_cfg = project_cfg
        self._hooks_dir = getattr(project_cfg, "hooks_dir", HOOKS_DIR) or HOOKS_DIR
        self._pipeline_data_cache: dict[str, CachedPipelineData] = {}

    def sync_project_state(self) -> None:
        try:
            self.project_cfg = self._config_manager.project_config
        except ValueError:
            return
        self._hooks_dir = getattr(self.project_cfg, "hooks_dir", HOOKS_DIR) or HOOKS_DIR

    def get_pipeline(
        self, name: str, project_context: "FlowerPowerProject", reload: bool = False
    ) -> "Pipeline":
        """Get a Pipeline instance for the given name.

        This method creates a fully-formed Pipeline object by loading its configuration
        and Python module, then injecting the project context.

        Args:
            name: Name of the pipeline to get
            project_context: Reference to the FlowerPowerProject
            reload: Whether to reload configuration and module from disk

        Returns:
            Pipeline instance ready for execution
        """
        name = validate_pipeline_name(name)

        # Use cache if available and not reloading
        cached_data = self._pipeline_data_cache.get(name)
        if not reload and cached_data is not None and cached_data.pipeline is not None:
            self.sync_project_state()
            logger.debug(f"Returning cached pipeline '{name}'")
            return cached_data.pipeline

        logger.debug(f"Creating pipeline instance for '{name}'")

        # Load pipeline configuration
        config = self.load_config(name, reload=reload)

        # Load pipeline module
        module = self.load_module(name, reload=reload)

        # Import Pipeline class here to avoid circular import
        from .pipeline import Pipeline

        # Create Pipeline instance
        pipeline = Pipeline(
            name=name,
            config=config,
            module=module,
            project_context=project_context,
        )

        # Cache the pipeline data
        self._pipeline_data_cache[name] = CachedPipelineData(
            pipeline=pipeline,
            config=config,
            module=module,
        )

        logger.debug(f"Successfully created pipeline instance for '{name}'")
        return pipeline

    def load_config(self, name: str, reload: bool = False) -> PipelineConfig:
        """Load pipeline configuration from disk.

        Args:
            name: Name of the pipeline
            reload: Whether to reload from disk even if cached

        Returns:
            PipelineConfig instance
        """
        name = validate_pipeline_name(name)

        # Use cache if available and not reloading
        cached_data = self._pipeline_data_cache.get(name)
        if not reload and cached_data is not None and cached_data.config is not None:
            self.sync_project_state()
            logger.debug(f"Returning cached config for pipeline '{name}'")
            return cached_data.config

        logger.debug(f"Loading configuration for pipeline '{name}'")

        config = self._config_manager.load_pipeline_config(name, reload=reload)
        self.sync_project_state()

        if cached_data is None:
            self._pipeline_data_cache[name] = CachedPipelineData(config=config)
        else:
            cached_data.config = config
            if reload:
                cached_data.pipeline = None
                cached_data.module = None

        return config

    def load_module(self, name: str, reload: bool = False) -> Any:
        """Load pipeline module from disk.

        Args:
            name: Name of the pipeline
            reload: Whether to reload from disk even if cached

        Returns:
            Loaded Python module
        """
        name = validate_pipeline_name(name)

        # Use cache if available and not reloading
        cached_data = self._pipeline_data_cache.get(name)
        if not reload and cached_data is not None and cached_data.module is not None:
            logger.debug(f"Returning cached module for pipeline '{name}'")
            return cached_data.module

        logger.debug(f"Loading module for pipeline '{name}'")

        # Load the module through the shared resolver (handles package-root
        # normalization, hyphens, and fallback candidates)
        module = self._module_resolver.load(name, reload=reload)

        if cached_data is None:
            self._pipeline_data_cache[name] = CachedPipelineData(module=module)
        else:
            cached_data.module = module
            if reload:
                cached_data.pipeline = None

        return module

    def clear_cache(self, name: str | None = None):
        """Clear cached pipelines, configurations, and modules.

        Args:
            name: If provided, clear cache only for this pipeline.
                 If None, clear entire cache.
        """
        if name:
            logger.debug(f"Clearing cache for pipeline '{name}'")
            self._pipeline_data_cache.pop(name, None)
        else:
            logger.debug("Clearing entire pipeline cache")
            self._pipeline_data_cache.clear()
