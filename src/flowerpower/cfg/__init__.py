from pathlib import Path

import msgspec
from fsspeckit import AbstractFileSystem, BaseStorageOptions
from ..settings import CONFIG_DIR, PIPELINES_DIR
from ..utils.filesystem import (
    format_pipeline_file_path,
    get_pipeline_config_paths,
    get_project_config_paths,
)
from ..utils.security import (
    validate_directory_fragment,
    validate_file_path,
    validate_pipeline_name,
)
from .base import BaseConfig
from .pipeline import PipelineConfig, init_pipeline_config
from .project import ProjectConfig, init_project_config


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
        storage_options (dict): Options for filesystem operations.

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
    storage_options: dict = msgspec.field(default_factory=dict)
    cfg_dir: str | None = None
    pipelines_dir: str | None = None

    def __post_init__(self):
        """Handle conversion of storage_options from dict if needed."""
        if isinstance(self.storage_options, BaseStorageOptions):
            self.storage_options = dict(
                self.storage_options.to_dict(with_protocol=True)
            )
        elif isinstance(self.storage_options, dict):
            self.storage_options = dict(self.storage_options)

        # Validate storage_options
        self._validate_storage_options()

        # Validate base_dir if provided
        if self.base_dir is not None:
            self._validate_base_dir()

    def to_dict(self) -> dict[str, object]:
        data = super().to_dict()
        data.pop("cfg_dir", None)
        data.pop("pipelines_dir", None)
        return data

    def _validate_storage_options(self) -> None:
        """Validate storage_options parameter.

        Raises:
            ValueError: If storage_options contains invalid values.
        """
        if self.storage_options is None:
            self.storage_options = {}

        if not isinstance(self.storage_options, dict):
            raise ValueError(
                f"storage_options must be a dict, got {type(self.storage_options)}"
            )

    def _validate_base_dir(self) -> None:
        """Validate base_dir parameter.

        Raises:
            ValueError: If base_dir contains invalid characters or is empty.
        """
        base_dir_str = str(self.base_dir)

        # Use shared path validation (allows both absolute and relative paths)
        validate_file_path(base_dir_str, allow_absolute=True, allow_relative=True)

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
        storage_options: dict | BaseStorageOptions | None = None,
        cfg_dir: str | None = None,
        pipelines_dir: str | None = None,
    ):
        """Load both project and pipeline configurations.

        Args:
            base_dir (str, optional): Base directory for configurations. Defaults to ".".
            name (str | None, optional): Project name. Defaults to None.
            pipeline_name (str | None, optional): Pipeline name. Defaults to None.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict, optional): Options for filesystem. Defaults to empty dict.
            cfg_dir (str | None, optional): Configuration directory override. Defaults to CONFIG_DIR.
            pipelines_dir (str | None, optional): Pipeline directory override. Defaults to PIPELINES_DIR.

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
            fs = cls._get_cached_filesystem(base_dir, storage_options)

        from ..pipeline.config_manager import PipelineConfigManager

        config_manager = PipelineConfigManager(
            base_dir=base_dir,
            fs=fs,
            storage_options=storage_options or {},
            cfg_dir=cfg_dir,
            pipelines_dir=pipelines_dir,
        )

        project = config_manager.load_project_config(name=name)
        pipeline = config_manager.load_pipeline_config(pipeline_name)

        return cls(
            base_dir=base_dir,
            pipeline=pipeline,
            project=project,
            fs=fs,
            storage_options=storage_options,
            cfg_dir=cfg_dir,
            pipelines_dir=pipelines_dir,
        )

    def save(
        self,
        project: bool = False,
        pipeline: bool = True,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = None,
        cfg_dir: str | None = None,
        pipelines_dir: str | None = None,
    ):
        """Save project and/or pipeline configurations.

        Args:
            project (bool, optional): Whether to save project config. Defaults to False.
            pipeline (bool, optional): Whether to save pipeline config. Defaults to True.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict, optional): Options for filesystem. Defaults to empty dict.
            cfg_dir (str | None, optional): Configuration directory override. Defaults to CONFIG_DIR.
            pipelines_dir (str | None, optional): Pipeline directory override. Defaults to PIPELINES_DIR.

        Example:
            ```python
            config.save(project=True, pipeline=True)
            ```
        """
        active_fs = fs or self.fs
        if active_fs is None:
            # Use cached filesystem for better performance
            effective_storage_options = (
                storage_options if storage_options is not None else self.storage_options
            )
            active_fs = self._get_cached_filesystem(
                self.base_dir, effective_storage_options
            )
            self.fs = active_fs

        if cfg_dir is None:
            cfg_dir = self.cfg_dir if self.cfg_dir is not None else CONFIG_DIR
        if pipelines_dir is None:
            pipelines_dir = (
                self.pipelines_dir if self.pipelines_dir is not None else PIPELINES_DIR
            )

        cfg_dir = validate_directory_fragment(cfg_dir)
        pipelines_dir = validate_directory_fragment(pipelines_dir)

        self.cfg_dir = cfg_dir
        self.pipelines_dir = pipelines_dir

        if pipeline:
            if self.pipeline.name is None:
                raise ValueError("Pipeline name is not set. Please provide a name.")

            # Validate pipeline name
            self.pipeline.name = validate_pipeline_name(self.pipeline.name)

            formatted_name = format_pipeline_file_path(self.pipeline.name)
            pipeline_path = get_pipeline_config_paths(
                formatted_name,
                cfg_dir,
                pipelines_dir,
            )[0]

            self.pipeline.to_yaml(path=pipeline_path, fs=active_fs)
        if project:
            project_path = get_project_config_paths(cfg_dir)[0]
            active_fs.makedirs(cfg_dir or ".", exist_ok=True)
            self.project.to_yaml(path=project_path, fs=active_fs)


def load(
    base_dir: str,
    name: str | None = None,
    pipeline_name: str | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    fs: AbstractFileSystem | None = None,
    cfg_dir: str | None = None,
    pipelines_dir: str | None = None,
):
    """Helper function to load configuration.

    This is a convenience wrapper around Config.load().

    Args:
        base_dir (str): Base directory for configurations.
        name (str | None, optional): Project name. Defaults to None.
        pipeline_name (str | None, optional): Pipeline name. Defaults to None.
        storage_options (dict, optional): Options for filesystem. Defaults to empty dict.
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
        cfg_dir=cfg_dir,
        pipelines_dir=pipelines_dir,
    )


def save(
    config: Config,
    project: bool = False,
    pipeline: bool = True,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    cfg_dir: str | None = None,
    pipelines_dir: str | None = None,
):
    """Helper function to save configuration.

    This is a convenience wrapper around Config.save().

    Args:
        config (Config): Configuration instance to save.
        project (bool, optional): Whether to save project config. Defaults to False.
        pipeline (bool, optional): Whether to save pipeline config. Defaults to True.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict, optional): Options for filesystem. Defaults to empty dict.

    Example:
        ```python
        config = load(base_dir="my_project")
        save(config, project=True, pipeline=True)
        ```
    """
    config.save(
        project=project,
        pipeline=pipeline,
        fs=fs,
        storage_options=storage_options,
        cfg_dir=cfg_dir,
        pipelines_dir=pipelines_dir,
    )


def init_config(
    base_dir: str = ".",
    name: str | None = None,
    pipeline_name: str | None = None,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    cfg_dir: str | None = None,
    pipelines_dir: str | None = None,
):
    """Initialize a new configuration with both project and pipeline settings.

    This function creates and initializes both project and pipeline configurations,
    combining them into a single Config instance.

    Args:
        base_dir (str, optional): Base directory for configurations. Defaults to ".".
        name (str | None, optional): Project name. Defaults to None.
        pipeline_name (str | None, optional): Pipeline name. Defaults to None.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict, optional): Options for filesystem. Defaults to empty dict.

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
        cfg_dir=cfg_dir,
        pipelines_dir=pipelines_dir,
    )
    project_cfg = init_project_config(
        base_dir=base_dir,
        name=name,
        fs=fs,
        storage_options=storage_options,
        cfg_dir=cfg_dir,
    )
    return Config(
        pipeline=pipeline_cfg,
        project=project_cfg,
        fs=fs,
        base_dir=base_dir,
        cfg_dir=cfg_dir,
        pipelines_dir=pipelines_dir,
    )
