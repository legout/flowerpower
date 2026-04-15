"""Pipeline Registry for discovery, listing, caching, and module loading."""

import posixpath
from typing import TYPE_CHECKING, Any

import msgspec
import rich
import yaml
from fsspeckit import AbstractFileSystem, filesystem
from loguru import logger

# Import necessary config types and utility functions
from ..cfg import PipelineConfig, ProjectConfig
from ..settings import CONFIG_DIR, HOOKS_DIR, LOG_LEVEL, PIPELINES_DIR
from ..utils.filesystem import (
    add_modules_path,
    format_pipeline_file_path,
    format_pipeline_module_path,
    format_pipeline_package_root,
    get_pipeline_config_paths,
)
from ..utils.logging import setup_logging
from ..utils.security import (
    SecurityError,
    validate_directory_fragment,
    validate_file_path,
    validate_pipeline_name,
)
from ..utils.templates import HOOK_TEMPLATE__MQTT_BUILD_CONFIG

# Import base utilities
from .base import load_module
from .config_manager import PipelineConfigManager
from .presenter import PipelinePresenter

if TYPE_CHECKING:
    from ..flowerpower import FlowerPowerProject
    from .pipeline import Pipeline

from enum import Enum


class HookType(str, Enum):
    MQTT_BUILD_CONFIG = "mqtt-build-config"

    def default_function_name(self) -> str:
        return self.value.replace("-", "_")

    def __str__(self) -> str:
        return self.value


class CachedPipelineData(msgspec.Struct):
    """Container for cached pipeline data."""

    pipeline: "Pipeline | None" = None
    config: PipelineConfig | None = None
    module: Any = None


setup_logging(level=LOG_LEVEL)


class PipelineRegistry:
    """Manages discovery, listing, caching, and module loading of pipelines.

    Rendering / presentation is delegated to :class:`PipelinePresenter`.
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
        self.project_cfg = project_cfg
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
        self._hooks_dir = getattr(project_cfg, "hooks_dir", HOOKS_DIR) or HOOKS_DIR
        if config_manager is None:
            config_manager = PipelineConfigManager(
                base_dir=base_dir or ".",
                fs=fs,
                storage_options=storage_options or {},
                cfg_dir=cfg_dir,
                pipelines_dir=pipelines_dir,
            )
        self._config_manager = config_manager

        # Consolidated cache for pipeline data
        self._pipeline_data_cache: dict[str, CachedPipelineData] = {}

        # Presenter for all Rich rendering
        self._presenter = PipelinePresenter()

        self._sync_project_state()

        # Ensure module paths are added (delegated to shared utility)
        add_modules_path(self._fs, self._pipelines_dir, self._base_dir)

    def _sync_project_state(self) -> None:
        try:
            self.project_cfg = self._config_manager.project_config
        except ValueError:
            return
        self._hooks_dir = getattr(self.project_cfg, "hooks_dir", HOOKS_DIR) or HOOKS_DIR

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

    # --- Pipeline Factory Methods ---

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

        Raises:
            FileNotFoundError: If pipeline configuration or module doesn't exist
            ImportError: If pipeline module cannot be imported
            ValueError: If pipeline configuration is invalid
        """
        name = validate_pipeline_name(name)

        # Use cache if available and not reloading
        cached_data = self._pipeline_data_cache.get(name)
        if not reload and cached_data is not None and cached_data.pipeline is not None:
            self._sync_project_state()
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
            self._sync_project_state()
            logger.debug(f"Returning cached config for pipeline '{name}'")
            return cached_data.config

        logger.debug(f"Loading configuration for pipeline '{name}'")

        config = self._config_manager.load_pipeline_config(name, reload=reload)
        self._sync_project_state()

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

        # Convert pipeline name to module name using the shared helper
        formatted_name = format_pipeline_module_path(name)
        package_root = format_pipeline_package_root(self._pipelines_dir)
        module_name = (
            f"{package_root}.{formatted_name}" if package_root else formatted_name
        )

        # Load the module
        module = load_module(module_name, reload=reload)

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

    # --- Pipeline Discovery & Listing ---

    def _get_files(self) -> list[str]:
        """
        Get the list of pipeline files.

        Returns:
            list[str]: The list of pipeline files.
        """
        try:
            files: list[str] = []
            seen: set[str] = set()
            discovery_error_logged = False
            patterns = (
                posixpath.join(self._pipelines_dir, "*.py"),
                posixpath.join(self._pipelines_dir, "**", "*.py"),
            )
            for pattern in patterns:
                try:
                    paths = self._fs.glob(pattern)
                except NotImplementedError as e:
                    logger.debug(
                        f"Skipping unsupported pipeline glob pattern {pattern}: {e}"
                    )
                    continue
                except Exception as e:
                    if not discovery_error_logged:
                        logger.error(
                            f"Error accessing pipeline glob pattern {pattern}: {e}"
                        )
                        discovery_error_logged = True
                    continue

                for path in paths:
                    if posixpath.basename(path) == "__init__.py" or path in seen:
                        continue
                    seen.add(path)
                    files.append(path)
            return sorted(files)
        except (OSError, PermissionError) as e:
            logger.error(
                f"Error accessing pipeline directory {self._pipelines_dir}: {e}"
            )
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error accessing pipeline directory {self._pipelines_dir}: {e}"
            )
            return []

    def _get_names(self) -> list[str]:
        """
        Get the list of pipeline names.

        Returns:
            list[str]: The list of pipeline names.
        """
        return [self._path_to_pipeline_name(path) for path in self._get_files()]

    def _path_to_pipeline_name(self, path: str) -> str:
        """Convert a pipeline file path into a discovered pipeline name."""
        relative_path = posixpath.relpath(path, self._pipelines_dir)
        module_path = posixpath.splitext(relative_path)[0]
        derived_name = module_path.replace("/", ".")
        stored_name = self._read_stored_pipeline_name(module_path)
        return stored_name or derived_name

    def _read_stored_pipeline_name(self, module_path: str) -> str | None:
        """Return the canonical pipeline name from YAML when available."""
        candidate_paths = get_pipeline_config_paths(
            module_path,
            self._cfg_dir,
            self._pipelines_dir,
        )

        for cfg_path in candidate_paths:
            try:
                exists = self._fs.exists(cfg_path)
            except Exception as error:
                logger.debug(
                    f"Skipping unreadable pipeline config candidate {cfg_path}: {error}"
                )
                continue

            if not exists:
                continue
            try:
                with self._fs.open(cfg_path) as f:
                    data = yaml.safe_load(f) or {}
            except Exception as e:
                logger.debug(
                    f"Skipping unreadable pipeline config candidate {cfg_path}: {e}"
                )
                continue

            stored_name = data.get("name") if isinstance(data, dict) else None
            if isinstance(stored_name, str) and stored_name:
                try:
                    return validate_pipeline_name(stored_name)
                except (SecurityError, ValueError):
                    continue

        return None

    # --- Data Gathering (presentation-free) ---

    def get_summary(
        self,
        name: str | None = None,
        cfg: bool = True,
        code: bool = True,
        project: bool = True,
    ) -> dict[str, Any]:
        """
        Get a summary of the pipelines.

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
        if name is not None:
            name = validate_pipeline_name(name)
            pipeline_names = [name]
        else:
            pipeline_names = self._get_names()

        summary: dict[str, Any] = {}
        summary["pipelines"] = {}

        if project:
            self._sync_project_state()
            summary["project"] = self.project_cfg.to_dict()

        for name in pipeline_names:
            # Load pipeline config directly

            pipeline_summary = {}
            if cfg:
                pipeline_cfg = self.load_config(name=name, reload=False)
                pipeline_summary["cfg"] = pipeline_cfg.to_dict()
            if code:
                try:
                    module_path = posixpath.join(
                        self._pipelines_dir,
                        f"{format_pipeline_file_path(name)}.py",
                    )
                    module_content = self._fs.cat(module_path).decode()
                    pipeline_summary["module"] = module_content
                except FileNotFoundError:
                    logger.warning(f"Module file not found for pipeline '{name}'")
                    pipeline_summary["module"] = "# Module file not found"
                except (OSError, PermissionError, UnicodeDecodeError) as e:
                    logger.error(
                        f"Error reading module file for pipeline '{name}': {e}"
                    )
                    pipeline_summary["module"] = f"# Error reading module file: {e}"
                except Exception as e:
                    logger.error(
                        f"Unexpected error reading module file for pipeline '{name}': {e}"
                    )
                    pipeline_summary["module"] = (
                        f"# Unexpected error reading module file: {e}"
                    )

            if pipeline_summary:  # Only add if cfg or code was requested and found
                summary["pipelines"][name] = pipeline_summary
        return summary

    def _collect_pipeline_info(self) -> list[dict[str, Any]]:
        """Collect metadata (name, path, mod_time, size) for all pipelines.

        Returns:
            A list of dicts, each with keys ``name``, ``path``, ``mod_time``,
            and ``size``.  Returns an empty list when no pipelines exist.
        """
        pipeline_files = self._get_files()
        pipeline_names = [self._path_to_pipeline_name(path) for path in pipeline_files]

        if not pipeline_files:
            return []

        pipeline_info: list[dict[str, Any]] = []

        for path, name in zip(pipeline_files, pipeline_names, strict=True):
            try:
                mod_time = self._fs.modified(path).strftime("%Y-%m-%d %H:%M:%S")
            except NotImplementedError:
                mod_time = "N/A"
            try:
                size_bytes = self._fs.size(path)
                size = f"{size_bytes / 1024:.1f} KB" if size_bytes else "0.0 KB"
            except NotImplementedError:
                size = "N/A"
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not get size for {path}: {e}")
                size = "Error"
            except Exception as e:
                logger.warning(f"Unexpected error getting size for {path}: {e}")
                size = "Error"

            pipeline_info.append(
                {
                    "name": name,
                    "path": path,
                    "mod_time": mod_time,
                    "size": size,
                }
            )

        return pipeline_info

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

    def _all_pipelines(
        self, show: bool = True, to_html: bool = False, to_svg: bool = False
    ) -> list[dict[str, Any]] | str | None:
        """Return or display all pipelines.

        When *show* is ``True`` (the default), renders via the presenter.
        When ``False``, returns the raw data list.

        Returns:
            ``list[dict[str, Any]]`` when *show* is ``False``, otherwise ``None``
            (or an HTML/SVG export string).
        """
        info = self._collect_pipeline_info()

        if not info:
            if show:
                self._presenter.print_no_pipelines_found()
            return [] if not show else None

        if show:
            return self._presenter.show_pipelines_table(
                info, to_html=to_html, to_svg=to_svg,
            )

        return info

    def list_pipeline_info(self) -> list[dict[str, Any]]:
        """Get metadata for all available pipelines.

        Returns:
            list[dict[str, Any]]: Pipeline metadata dictionaries.
        """
        return self._collect_pipeline_info()

    def list_pipelines(self) -> list[str]:
        """Get the discovered pipeline names.

        Returns:
            list[str]: Canonical pipeline names.
        """
        return self._get_names()

    @property
    def summary(self) -> dict[str, dict | str]:
        """Get a summary of the pipelines."""
        return self.get_summary()

    @property
    def pipelines(self) -> list[str]:
        """Get a list of discovered pipeline names."""
        return self._get_names()

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
        """
        Add a hook to the pipeline module.

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
