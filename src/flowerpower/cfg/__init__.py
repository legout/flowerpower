from pathlib import Path

import msgspec
from munch import Munch

from ..fs import AbstractFileSystem, BaseStorageOptions, get_filesystem
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
        base_dir (str | Path | None): Base directory for the configuration.
        storage_options (dict | Munch): Options for filesystem operations.

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
    base_dir: str | Path | None = None
    storage_options: dict | Munch = msgspec.field(default_factory=Munch)

    @classmethod
    def load(
        cls,
        base_dir: str = ".",
        name: str | None = None,
        pipeline_name: str | None = None,
        job_queue_type: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
    ):
        """Load both project and pipeline configurations.

        Args:
            base_dir (str, optional): Base directory for configurations. Defaults to ".".
            name (str | None, optional): Project name. Defaults to None.
            pipeline_name (str | None, optional): Pipeline name. Defaults to None.
            job_queue_type (str | None, optional): Type of job queue to use. Defaults to None.
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
                job_queue_type="rq"
            )
            ```
        """
        if fs is None:
            fs = get_filesystem(
                base_dir, cached=True, dirfs=True, storage_options=storage_options
            )
        project = ProjectConfig.load(
            base_dir=base_dir,
            name=name,
            job_queue_type=job_queue_type,
            fs=fs,
            storage_options=storage_options,
        )
        pipeline = PipelineConfig.load(
            base_dir=base_dir,
            name=pipeline_name,
            fs=fs,
            storage_options=storage_options,
        )

        return cls(
            base_dir=base_dir,
            pipeline=pipeline,
            project=project,
            fs=fs,
            storage_options=storage_options,
        )

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
            self.fs = get_filesystem(
                self.base_dir, cached=True, dirfs=True, **storage_options
            )

        if not self.fs.exists("conf"):
            self.fs.makedirs("conf")

        if pipeline:
            self.fs.makedirs("conf/pipelines", exist_ok=True)
            h_params = self.pipeline.pop("h_params") if self.pipeline.h_params else None
            self.pipeline.to_yaml(
                path=f"conf/pipelines/{self.pipeline.name}.yml", fs=self.fs
            )
            if h_params:
                self.pipeline.h_params = h_params
        if project:
            self.project.to_yaml("conf/project.yml", self.fs)


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
    job_queue_type: str | None = None,
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
        job_queue_type (str | None, optional): Type of job queue to use. Defaults to None.
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
            job_queue_type="rq"
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
        job_queue_type=job_queue_type,
        fs=fs,
        storage_options=storage_options,
    )
    return Config(pipeline=pipeline_cfg, project=project_cfg, fs=fs, base_dir=base_dir)
