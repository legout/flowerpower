"""Configuration management for pipelines."""

from typing import Any

from fsspeckit import AbstractFileSystem

from ..cfg import PipelineConfig, ProjectConfig
from ..settings import CONFIG_DIR, PIPELINES_DIR
from ..utils.env import apply_env_overlays
from ..utils.filesystem import find_first_existing_path, get_project_config_paths
from ..utils.security import validate_directory_fragment, validate_pipeline_name


class PipelineConfigManager:
    """Loads project and pipeline configurations from disk.

    Stateless loader: every call reads fresh and applies environment overlays.
    Caching is owned by PipelineLoader, not this module.
    """

    def __init__(
        self,
        base_dir: str,
        fs: AbstractFileSystem,
        storage_options: dict[str, Any] | Any,
        cfg_dir: str | None = CONFIG_DIR,
        pipelines_dir: str | None = PIPELINES_DIR,
    ) -> None:
        """Initialize the configuration manager.

        Args:
            base_dir: Base directory for the project
            fs: Filesystem instance for file operations
            storage_options: Storage options for filesystem
            cfg_dir: Configuration directory name
            pipelines_dir: Pipelines directory name
        """
        self._base_dir = base_dir
        self._fs = fs
        self._storage_options = storage_options
        self._cfg_dir = validate_directory_fragment(
            cfg_dir if cfg_dir is not None else CONFIG_DIR
        )
        self._pipelines_dir = validate_directory_fragment(
            pipelines_dir if pipelines_dir is not None else PIPELINES_DIR
        )

    def _project_config_paths(self) -> list[str]:
        return get_project_config_paths(self._cfg_dir)

    def load_project_config(self, name: str | None = None) -> ProjectConfig:
        """Load project configuration.

        Args:
            name: Fallback project name when no project config file exists.

        Returns:
            ProjectConfig: The loaded project configuration
        """
        project_config_exists = (
            find_first_existing_path(
                self._fs,
                self._project_config_paths(),
                purpose="project config",
            )
            is not None
        )
        requested_name = None if project_config_exists else name

        load_kwargs = {
            "base_dir": self._base_dir,
            "fs": self._fs,
            "storage_options": self._storage_options,
            "cfg_dir": self._cfg_dir,
        }
        if requested_name is not None:
            load_kwargs["name"] = requested_name

        project_cfg = ProjectConfig.load(**load_kwargs)
        apply_env_overlays(project_cfg=project_cfg)
        return project_cfg

    def load_pipeline_config(self, name: str | None) -> PipelineConfig:
        """Load pipeline configuration.

        Args:
            name: Name of the pipeline to load

        Returns:
            PipelineConfig: The loaded pipeline configuration
        """
        if name is not None:
            name = validate_pipeline_name(name)

        # Load configuration through the canonical loader
        pipeline_cfg = PipelineConfig.load(
            base_dir=self._base_dir,
            name=name,
            fs=self._fs,
            storage_options=self._storage_options,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )

        # Apply env overlays to pipeline config only — project overlays are
        # applied by load_project_config() when it is called.
        apply_env_overlays(pipeline_cfg=pipeline_cfg)
        return pipeline_cfg
