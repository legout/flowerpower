"""Pipeline Registry — compatibility facade over catalog, loader, and resolver.

This module preserves the historical :class:`PipelineRegistry` public surface
while delegating discovery, listing, and presentation-free summary assembly to
:class:`PipelineCatalog`, and config/module loading, ``Pipeline`` construction,
and cache/reload invalidation to :class:`PipelineLoader`.  Import-name
normalization is handled by the shared :class:`PipelineModuleResolver`.
"""

import posixpath
from enum import Enum
from typing import TYPE_CHECKING, Any
import rich

from fsspeckit import AbstractFileSystem, filesystem

from ..cfg import ProjectConfig
from ..settings import CONFIG_DIR, LOG_LEVEL, PIPELINES_DIR
from ..utils.filesystem import (
    add_modules_path,
)
from ..utils.logging import setup_logging
from ..utils.security import (
    validate_directory_fragment,
    validate_file_path,
    validate_pipeline_name,
)
from ..utils.templates import HOOK_TEMPLATE__MQTT_BUILD_CONFIG

# Import base utilities
from .catalog import PipelineCatalog
from .config_manager import PipelineConfigManager
from .loader import CachedPipelineData, PipelineLoader
from .module_resolver import PipelineModuleResolver
from .presenter import PipelinePresenter

if TYPE_CHECKING:
    from ..flowerpower import FlowerPowerProject
    from .pipeline import Pipeline

__all__ = ["CachedPipelineData", "HookType", "PipelineRegistry"]


setup_logging(level=LOG_LEVEL)


class HookType(str, Enum):
    MQTT_BUILD_CONFIG = "mqtt-build-config"

    def default_function_name(self) -> str:
        return self.value.replace("-", "_")

    def __str__(self) -> str:
        return self.value


class PipelineRegistry:
    """Compatibility facade over catalog, loader, and resolver responsibilities.

    Discovery, listing, and presentation-free summary payloads are owned by the
    :class:`PipelineCatalog`.  Config/module loading, ``Pipeline`` construction,
    and cache/reload invalidation are owned by the :class:`PipelineLoader`.
    Import-name normalization is owned by :class:`PipelineModuleResolver`.

    Historical public methods (``list_pipelines``, ``get_summary``,
    ``load_config``, ``load_module``, ``get_pipeline``, ``clear_cache``,
    ``new``, ``delete``, ``create_pipeline``, ``delete_pipeline``) remain
    source-compatible and delegate to the appropriate module.
    """

    def __init__(
        self,
        project_cfg: ProjectConfig,
        fs: AbstractFileSystem,
        base_dir: str | None = None,
        storage_options: dict | None = None,
        config_manager: "PipelineConfigManager | None" = None,
        cfg_dir: str = CONFIG_DIR,
        pipelines_dir: str = PIPELINES_DIR,
    ):
        """
        Initializes the PipelineRegistry.

        Args:
            project_cfg: The project configuration object.
            fs: The filesystem instance.
            base_dir: The base directory path.
            storage_options: Storage options for filesystem operations.
            config_manager: Optional PipelineConfigManager to delegate config loading to.
                If not provided, one is automatically instantiated.
            cfg_dir: Configuration directory name.
            pipelines_dir: Pipelines directory name.
        """
        self._fs = fs
        if config_manager is not None:
            self._base_dir = getattr(config_manager, "_base_dir", base_dir)
            self._cfg_dir = getattr(config_manager, "_cfg_dir", CONFIG_DIR)
            self._pipelines_dir = getattr(
                config_manager, "_pipelines_dir", PIPELINES_DIR
            )
        else:
            self._base_dir = base_dir
            self._cfg_dir = validate_directory_fragment(
                cfg_dir if cfg_dir is not None else CONFIG_DIR
            )
            self._pipelines_dir = validate_directory_fragment(
                pipelines_dir if pipelines_dir is not None else PIPELINES_DIR
            )

        if config_manager is None:
            config_manager = PipelineConfigManager(
                base_dir=base_dir or ".",
                fs=fs,
                storage_options=storage_options or {},
                cfg_dir=cfg_dir,
                pipelines_dir=pipelines_dir,
            )

        # Shared resolver for pipeline module imports
        module_resolver = PipelineModuleResolver(self._pipelines_dir)

        # Loader owns config/module/pipeline cache and invalidation
        self._loader = PipelineLoader(
            config_manager=config_manager,
            module_resolver=module_resolver,
            fs=fs,
            project_cfg=project_cfg,
        )

        # Catalog owns discovery, listing, and presentation-free summaries
        self._catalog = PipelineCatalog(
            fs=fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
            project_cfg=project_cfg,
            config_provider=self._loader.load_config,
            project_cfg_provider=lambda: self._loader.project_cfg,
        )

        # Presenter for all Rich rendering
        self._presenter = PipelinePresenter()

        # Sync project state through the loader
        self._sync_project_state()

        # Ensure module paths are added (delegated to shared utility)
        add_modules_path(self._fs, self._pipelines_dir, self._base_dir)

    @classmethod
    def from_context(
        cls,
        context,
        *,
        project_cfg: ProjectConfig,
        config_manager: "PipelineConfigManager | None" = None,
    ) -> "PipelineRegistry":
        """Create a registry from project runtime context facts."""
        return cls(
            project_cfg=project_cfg,
            fs=context.fs,
            base_dir=context.base_dir,
            storage_options=context.storage_options,
            config_manager=config_manager,
            cfg_dir=context.cfg_dir,
            pipelines_dir=context.pipelines_dir,
        )

    # --- Delegating properties (compatibility with historical internals) ---

    @property
    def project_cfg(self) -> ProjectConfig:
        """Current project configuration (synced by the loader)."""
        return self._loader.project_cfg

    @property
    def _hooks_dir(self) -> str:
        return self._loader._hooks_dir

    @property
    def _pipeline_data_cache(self) -> dict[str, CachedPipelineData]:
        return self._loader._pipeline_data_cache

    @property
    def _config_manager(self) -> PipelineConfigManager:
        return self._loader._config_manager

    @classmethod
    def from_filesystem(
        cls,
        base_dir: str,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | None = None,
        cfg_dir: str = CONFIG_DIR,
        pipelines_dir: str = PIPELINES_DIR,
    ) -> "PipelineRegistry":
        """
        Create a PipelineRegistry from filesystem parameters.

        This factory method creates a complete PipelineRegistry instance by:
        1. Creating the filesystem if not provided
        2. Loading the ProjectConfig from the base directory
        3. Initializing the registry with the loaded configuration

        Args:
            base_dir: The base directory path for the FlowerPower project
            fs: Optional filesystem instance. If None, will be created from base_dir
            storage_options: Optional storage options for filesystem access
            cfg_dir: Configuration directory name.
            pipelines_dir: Pipelines directory name.

        Returns:
            PipelineRegistry: A fully configured registry instance

        Raises:
            ValueError: If base_dir is invalid or ProjectConfig cannot be loaded
            RuntimeError: If filesystem creation fails

        Example:
            ```python
            # Create registry from local directory
            registry = PipelineRegistry.from_filesystem("/path/to/project")

            # Create registry with S3 storage
            registry = PipelineRegistry.from_filesystem(
                "s3://my-bucket/project",
                storage_options={"key": "secret"}
            )
            ```
        """
        # Create filesystem if not provided
        if fs is None:
            fs = filesystem(
                base_dir,
                storage_options=storage_options,
                cached=storage_options is not None,
            )

        # Set up a config manager so env overlays are applied consistently
        config_manager = PipelineConfigManager(
            base_dir=base_dir,
            fs=fs,
            storage_options=storage_options or {},
            cfg_dir=cfg_dir,
            pipelines_dir=pipelines_dir,
        )

        # Load project configuration through the manager (applies env overlays)
        project_cfg = config_manager.load_project_config()

        # Ensure we have a ProjectConfig instance
        if not isinstance(project_cfg, ProjectConfig):
            raise TypeError(f"Expected ProjectConfig, got {type(project_cfg)}")

        # Create and return registry instance
        return cls(
            project_cfg=project_cfg,
            fs=fs,
            base_dir=base_dir,
            storage_options=storage_options,
            config_manager=config_manager,
            cfg_dir=cfg_dir,
            pipelines_dir=pipelines_dir,
        )

    # --- Loader delegation (config/module/pipeline cache) ---

    def _sync_project_state(self) -> None:
        """Sync project configuration and hooks dir through the loader."""
        self._loader.sync_project_state()

    def get_pipeline(
        self, name: str, project_context: "FlowerPowerProject", reload: bool = False
    ) -> "Pipeline":
        """Get a Pipeline instance for the given name.

        Delegates to :class:`PipelineLoader`.

        Args:
            name: Name of the pipeline to get
            project_context: Reference to the FlowerPowerProject
            reload: Whether to reload configuration and module from disk

        Returns:
            Pipeline instance ready for execution

        Raises:
            FileNotFoundError: If pipeline configuration or module doesn't exist
            ImportError: If pipeline module cannot be imported
            ValueError: If pipeline configuration is invalid
        """
        return self._loader.get_pipeline(name, project_context, reload=reload)

    def load_config(self, name: str, reload: bool = False) -> Any:
        """Load pipeline configuration from disk.

        Delegates to :class:`PipelineLoader`.

        Args:
            name: Name of the pipeline
            reload: Whether to reload from disk even if cached

        Returns:
            PipelineConfig instance
        """
        return self._loader.load_config(name, reload=reload)

    def load_module(self, name: str, reload: bool = False) -> Any:
        """Load pipeline module from disk.

        Delegates to :class:`PipelineLoader`.

        Args:
            name: Name of the pipeline
            reload: Whether to reload from disk even if cached

        Returns:
            Loaded Python module
        """
        return self._loader.load_module(name, reload=reload)

    def clear_cache(self, name: str | None = None):
        """Clear cached pipelines, configurations, and modules.

        Delegates to :class:`PipelineLoader`.

        Args:
            name: If provided, clear cache only for this pipeline.
                 If None, clear entire cache.
        """
        self._loader.clear_cache(name)

    # --- Catalog delegation (discovery, listing, summaries) ---

    def _get_files(self) -> list[str]:
        """Get the list of pipeline files. Delegates to :class:`PipelineCatalog`."""
        return self._catalog.get_files()

    def _get_names(self) -> list[str]:
        """Get the list of pipeline names. Delegates to :class:`PipelineCatalog`."""
        return self._catalog.get_names()

    def _path_to_pipeline_name(self, path: str) -> str:
        """Convert a pipeline file path into a discovered pipeline name."""
        return self._catalog.path_to_pipeline_name(path)

    def _read_stored_pipeline_name(self, module_path: str) -> str | None:
        """Return the canonical pipeline name from YAML when available."""
        return self._catalog.read_stored_pipeline_name(module_path)

    def _collect_pipeline_info(self) -> list[dict[str, Any]]:
        """Collect metadata for all pipelines. Delegates to :class:`PipelineCatalog`."""
        return self._catalog.collect_pipeline_info()

    def get_summary(
        self,
        name: str | None = None,
        cfg: bool = True,
        code: bool = True,
        project: bool = True,
    ) -> dict[str, Any]:
        """
        Get a summary of the pipelines.

        Delegates to :class:`PipelineCatalog` for presentation-free payload
        assembly.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            cfg (bool, optional): Whether to show the configuration. Defaults to True.
            code (bool, optional): Whether to show the module. Defaults to True.
            project (bool, optional): Whether to show the project configuration. Defaults to True.
        Returns:
            dict[str, dict | str]: A dictionary containing the pipeline summary.

        Examples:
            ```python
            pm = PipelineManager()
            summary=pm.get_summary()
            ```
        """
        return self._catalog.get_summary(
            name=name, cfg=cfg, code=code, project=project
        )

    def list_pipeline_info(self) -> list[dict[str, Any]]:
        """Get metadata for all available pipelines.

        Returns:
            list[dict[str, Any]]: Pipeline metadata dictionaries.
        """
        return self._catalog.list_pipeline_info()

    def list_pipelines(self) -> list[str]:
        """Get the discovered pipeline names.

        Returns:
            list[str]: Canonical pipeline names.
        """
        return self._catalog.list_pipelines()

    @property
    def summary(self) -> dict[str, dict | str]:
        """Get a summary of the pipelines."""
        return self.get_summary()

    @property
    def pipelines(self) -> list[str]:
        """Get a list of discovered pipeline names."""
        return self._catalog.pipelines

    # --- Presentation (delegated to PipelinePresenter) ---

    def show_summary(
        self,
        name: str | None = None,
        cfg: bool = True,
        code: bool = True,
        project: bool = True,
        to_html: bool = False,
        to_svg: bool = False,
    ) -> None | str:
        """Show a Rich-rendered summary of pipelines.

        Delegates to :class:`PipelinePresenter` for all rendering.

        Returns:
            None | str: HTML/SVG string when export is requested, otherwise None.
        """
        summary = self.get_summary(name=name, cfg=cfg, code=code, project=project)
        return self._presenter.show_summary(
            summary, cfg=cfg, code=code, project=project,
            to_html=to_html, to_svg=to_svg,
        )

    def show_pipelines(self) -> None:
        """Print all available pipelines in a formatted table.

        Delegates to :class:`PipelinePresenter`.
        """
        info = self._collect_pipeline_info()
        if not info:
            self._presenter.print_no_pipelines_found()
            return
        self._presenter.show_pipelines_table(info)

    # --- Backward-compatible lifecycle delegation ---

    def _creator(self):
        """Build a creator using the registry's current project/config state."""
        self._sync_project_state()

        from .creator import PipelineCreator

        return PipelineCreator(
            project_cfg=self.project_cfg,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )

    def new(self, name: str, overwrite: bool = False) -> None:
        """Create a pipeline.

        Backward-compatible shim for older callers that still use the registry
        as the lifecycle entry point.
        """
        self._creator().new(name=name, overwrite=overwrite)

    def delete(self, name: str, cfg: bool = True, module: bool = False) -> None:
        """Delete a pipeline.

        Backward-compatible shim for older callers that still use the registry
        as the lifecycle entry point.
        """
        self._creator().delete(name=name, cfg=cfg, module=module)

    def create_pipeline(self, name: str, overwrite: bool = False) -> None:
        """Backward-compatible alias for :meth:`new`."""
        self.new(name=name, overwrite=overwrite)

    def delete_pipeline(
        self, name: str, cfg: bool = True, module: bool = False
    ) -> None:
        """Backward-compatible alias for :meth:`delete`."""
        self.delete(name=name, cfg=cfg, module=module)

    # --- Hook management ---

    def add_hook(
        self,
        name: str,
        type: HookType,
        to: str | None = None,
        function_name: str | None = None,
    ):
        """Add a hook to the pipeline module.

        Hook management remains on the facade for source compatibility.

        Args:
            name (str): The name of the pipeline
            type (HookType): The type of the hook.
            to (str | None, optional): The name of the file to add the hook to. Defaults to the hook.py file in the pipelines hooks folder.
            function_name (str | None, optional): The name of the function. If not provided uses default name of hook type.

        Returns:
            None

        Examples:
            >>> pm = PipelineManager()
            >>> pm.add_hook(HookType.PRE_EXECUTE)
        """

        name = validate_pipeline_name(name)
        self._sync_project_state()

        if to is None:
            to = f"{self._hooks_dir}/{name}/hook.py"
        else:
            to = f"{self._hooks_dir}/{name}/{to}"

        to = str(validate_file_path(to))

        match type:
            case HookType.MQTT_BUILD_CONFIG:
                template = HOOK_TEMPLATE__MQTT_BUILD_CONFIG

        if function_name is None:
            function_name = type.default_function_name()

        if not self._fs.exists(to):
            self._fs.makedirs(posixpath.dirname(to), exist_ok=True)

        with self._fs.open(to, "a") as f:
            f.write(template.format(function_name=function_name))

        rich.print(
            f"🔧 Added hook [bold blue]{type.value}[/bold blue] to {to} as {function_name} for {name}"
        )
