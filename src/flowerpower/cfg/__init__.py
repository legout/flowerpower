from pathlib import Path

import msgspec
from fsspeckit import AbstractFileSystem, BaseStorageOptions, filesystem
from munch import Munch

from ..settings import CONFIG_DIR, PIPELINES_DIR
from .base import BaseConfig
from .exceptions import ConfigLoadError, ConfigSaveError, ConfigPathError
from .pipeline import PipelineConfig, init_pipeline_config
from .project import ProjectConfig, init_project_config
from ..utils.env import (
    parse_env_overrides,
    build_specific_overlays,
    apply_global_shims,
    merge_overlays_into_config,
)


class Config(BaseConfig):
    """Main configuration class for FlowerPower, combining project and pipeline settings.

    This class serves as the central configuration manager, handling both project-wide
    and pipeline-specific settings. It provides functionality for loading and saving
    configurations using various filesystem abstractions.

    Attributes:
        pipeline (PipelineConfig): Configuration for the pipeline.
        project (ProjectConfig): Configuration for the project.
        fs (AbstractFileSystem | None): Filesystem abstraction for I/O operations.
        base_dir (str | None): Base directory for the configuration.
        base_dir_path (pathlib.Path | None): Base directory as a Path object (property).
        storage_options (Munch): Options for filesystem operations.

    Example:
        ```python
        # Load configuration
        config = Config.load(
            base_dir="my_project",
            name="project1",
            pipeline_name="data-pipeline"
        )

        # Save configuration
        config.save(project=True, pipeline=True)
        ```
    """

    pipeline: PipelineConfig = msgspec.field(default_factory=PipelineConfig)
    project: ProjectConfig = msgspec.field(default_factory=ProjectConfig)
    fs: AbstractFileSystem | None = None
    base_dir: str | None = None
    storage_options: Munch = msgspec.field(default_factory=Munch)

    def __post_init__(self):
        """Handle conversion of storage_options from dict to Munch if needed."""
        if isinstance(self.storage_options, dict):
            self.storage_options = Munch(self.storage_options)
        
        # Validate storage_options
        self._validate_storage_options()
        
        # Validate base_dir if provided
        if self.base_dir is not None:
            self._validate_base_dir()

    def _validate_storage_options(self) -> None:
        """Validate storage_options parameter.
        
        Raises:
            ValueError: If storage_options contains invalid values.
        """
        if self.storage_options is None:
            self.storage_options = Munch()
        
        if not isinstance(self.storage_options, (dict, Munch)):
            raise ValueError(f"storage_options must be a dict or Munch, got {type(self.storage_options)}")

    def _validate_base_dir(self) -> None:
        """Validate base_dir parameter.
        
        Raises:
            ValueError: If base_dir contains invalid characters or is empty.
        """
        # Convert Path to string if needed
        base_dir_str = str(self.base_dir) if hasattr(self.base_dir, '__str__') else self.base_dir
        
        if not isinstance(base_dir_str, str):
            raise ValueError(f"base_dir must be a string or Path, got {type(self.base_dir)}")
        
        # Check for directory traversal attempts (but allow absolute paths)
        if '..' in base_dir_str:
            raise ValueError(f"Invalid base_dir: {base_dir_str}. Contains path traversal characters.")
        
        # Check for empty string
        if not base_dir_str.strip():
            raise ValueError("base_dir cannot be empty or whitespace only.")

    @property
    def base_dir_path(self) -> Path | None:
        """Get base_dir as a pathlib.Path object.
        
        Returns:
            pathlib.Path | None: The base directory as a Path object, or None if base_dir is None.
        """
        return Path(self.base_dir) if self.base_dir is not None else None

    @classmethod
    def load(
        cls,
        base_dir: str = ".",
        name: str | None = None,
        pipeline_name: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
    ):
        """Load both project and pipeline configurations.

        Args:
            base_dir (str, optional): Base directory for configurations. Defaults to ".".
            name (str | None, optional): Project name. Defaults to None.
            pipeline_name (str | None, optional): Pipeline name. Defaults to None.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Returns:
            Config: Combined configuration instance.

        Example:
            ```python
            config = Config.load(
                base_dir="my_project",
                name="test_project",
                pipeline_name="etl",
            )
            ```
        """
        if fs is None:
            # Use cached filesystem for better performance
            storage_options_hash = cls._hash_storage_options(storage_options)
            fs = cls._get_cached_filesystem(base_dir, storage_options_hash)
        
        try:
            project = ProjectConfig.load(
                base_dir=base_dir,
                name=name,
                fs=fs,
                storage_options=storage_options,
            )
        except ConfigLoadError as e:
            raise ConfigLoadError(f"Failed to load project configuration: {e}", path=base_dir, original_error=e)
            
        try:
            pipeline = PipelineConfig.load(
                base_dir=base_dir,
                name=pipeline_name,
                fs=fs,
                storage_options=storage_options,
            )
        except ConfigLoadError as e:
            raise ConfigLoadError(f"Failed to load pipeline configuration: {e}", path=base_dir, original_error=e)

        config = cls(
            base_dir=base_dir,
            pipeline=pipeline,
            project=project,
            fs=fs,
            storage_options=storage_options,
        )

        # Apply environment overlays with specificity and shims
        try:
            overrides = parse_env_overrides()
            proj_overlay, pipe_overlay = build_specific_overlays(overrides)
            apply_global_shims(overrides, proj_overlay, pipe_overlay)
            merge_overlays_into_config(config, proj_overlay, pipe_overlay)
        except Exception:
            # Fail-open: ignore overlay errors to avoid breaking existing flows
            pass

        return config

    def save(
        self,
        project: bool = False,
        pipeline: bool = True,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
    ):
        """Save project and/or pipeline configurations.

        Args:
            project (bool, optional): Whether to save project config. Defaults to False.
            pipeline (bool, optional): Whether to save pipeline config. Defaults to True.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Example:
            ```python
            config.save(project=True, pipeline=True)
            ```
        """
        if fs is None and self.fs is None:
            # Use cached filesystem for better performance
            storage_options_hash = self._hash_storage_options(storage_options)
            self.fs = self._get_cached_filesystem(self.base_dir, storage_options_hash)

        if not self.fs.exists(CONFIG_DIR):
            self.fs.makedirs(CONFIG_DIR)

        if pipeline:
            self.fs.makedirs(PIPELINES_DIR, exist_ok=True)
            h_params = self.pipeline.pop("h_params") if self.pipeline.h_params else None
            # Validate pipeline name to prevent directory traversal
            if self.pipeline.name and ('..' in self.pipeline.name or '/' in self.pipeline.name or '\\' in self.pipeline.name):
                raise ConfigPathError(f"Invalid pipeline name: {self.pipeline.name}. Contains path traversal characters.", path=self.pipeline.name)
            try:
                self.pipeline.to_yaml(
                    path=f"conf/pipelines/{self.pipeline.name}.yml", fs=self.fs
                )
            except ConfigSaveError as e:
                raise ConfigSaveError(f"Failed to save pipeline configuration: {e}", path=f"conf/pipelines/{self.pipeline.name}.yml", original_error=e)
            if h_params:
                self.pipeline.h_params = h_params
        if project:
            try:
                self.project.to_yaml("conf/project.yml", self.fs)
            except ConfigSaveError as e:
                raise ConfigSaveError(f"Failed to save project configuration: {e}", path="conf/project.yml", original_error=e)


def load(
    base_dir: str,
    name: str | None = None,
    pipeline_name: str | None = None,
    storage_options: dict | BaseStorageOptions | None = {},
    fs: AbstractFileSystem | None = None,
):
    """Helper function to load configuration.

    This is a convenience wrapper around Config.load().

    Args:
        base_dir (str): Base directory for configurations.
        name (str | None, optional): Project name. Defaults to None.
        pipeline_name (str | None, optional): Pipeline name. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.

    Returns:
        Config: Combined configuration instance.

    Example:
        ```python
        config = load(base_dir="my_project", name="test", pipeline_name="etl")
        ```
    """
    return Config.load(
        name=name,
        pipeline_name=pipeline_name,
        base_dir=base_dir,
        storage_options=storage_options,
        fs=fs,
    )


def save(
    config: Config,
    project: bool = False,
    pipeline: bool = True,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | BaseStorageOptions | None = {},
):
    """Helper function to save configuration.

    This is a convenience wrapper around Config.save().

    Args:
        config (Config): Configuration instance to save.
        project (bool, optional): Whether to save project config. Defaults to False.
        pipeline (bool, optional): Whether to save pipeline config. Defaults to True.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

    Example:
        ```python
        config = load(base_dir="my_project")
        save(config, project=True, pipeline=True)
        ```
    """
    config.save(
        project=project, pipeline=pipeline, fs=fs, storage_options=storage_options
    )


def init_config(
    base_dir: str = ".",
    name: str | None = None,
    pipeline_name: str | None = None,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | BaseStorageOptions | None = {},
):
    """Initialize a new configuration with both project and pipeline settings.

    This function creates and initializes both project and pipeline configurations,
    combining them into a single Config instance.

    Args:
        base_dir (str, optional): Base directory for configurations. Defaults to ".".
        name (str | None, optional): Project name. Defaults to None.
        pipeline_name (str | None, optional): Pipeline name. Defaults to None.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

    Returns:
        Config: The initialized configuration instance.

    Example:
        ```python
        config = init_config(
            base_dir="my_project",
            name="test_project",
            pipeline_name="data-pipeline",
        )
        ```
    """
    pipeline_cfg = init_pipeline_config(
        base_dir=base_dir,
        name=pipeline_name,
        fs=fs,
        storage_options=storage_options,
    )
    project_cfg = init_project_config(
        base_dir=base_dir,
        name=name,
        fs=fs,
        storage_options=storage_options,
    )
    return Config(pipeline=pipeline_cfg, project=project_cfg, fs=fs, base_dir=base_dir)


# Helper methods for centralized load/save logic
@classmethod
def _load_config(
    cls,
    config_class: type[BaseConfig],
    base_dir: str,
    name: str | None,
    fs: AbstractFileSystem,
    storage_options: dict | BaseStorageOptions | None,
) -> BaseConfig:
    """Centralized configuration loading logic.
    
    Args:
        config_class: The configuration class to load.
        base_dir: Base directory for configurations.
        name: Configuration name.
        fs: Filesystem instance.
        storage_options: Options for filesystem.
        
    Returns:
        Loaded configuration instance.
    """
    return config_class.load(
        base_dir=base_dir,
        name=name,
        fs=fs,
        storage_options=storage_options,
    )


def _save_pipeline_config(self) -> None:
    """Save pipeline configuration with proper handling of h_params."""
    self.fs.makedirs(PIPELINES_DIR, exist_ok=True)
    h_params = self.pipeline.pop("h_params") if self.pipeline.h_params else None
    self.pipeline.to_yaml(
        path=f"conf/pipelines/{self.pipeline.name}.yml", fs=self.fs
    )
    if h_params:
        self.pipeline.h_params = h_params


def _save_project_config(self) -> None:
    """Save project configuration."""
    self.project.to_yaml("conf/project.yml", self.fs)
