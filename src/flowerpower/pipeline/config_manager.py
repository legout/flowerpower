"""Configuration management for pipelines."""

from typing import Any

from fsspeckit import AbstractFileSystem

from ..cfg import PipelineConfig, ProjectConfig
from ..settings import CONFIG_DIR, PIPELINES_DIR
from ..utils.env import apply_env_overlays
from ..utils.filesystem import find_first_existing_path, get_project_config_paths
from ..utils.security import validate_directory_fragment, validate_pipeline_name


class PipelineConfigManager:
    """Handles loading, validation, and access to pipeline configurations.

    This class is responsible for:
    - Loading project and pipeline configurations
    - Validating configuration files
    - Providing convenient access to configuration objects
    - Managing configuration reload logic
    """

    def __init__(
        self,
        base_dir: str,
        fs: AbstractFileSystem,
        storage_options: dict[str, Any] | Any,
        cfg_dir: str | None = CONFIG_DIR,
        pipelines_dir: str | None = PIPELINES_DIR,
    ):
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
        self._project_cfg: ProjectConfig | None = None
        self._pipeline_cfg: PipelineConfig | None = None
        self._current_project_name: str | None = None
        self._current_pipeline_name: str | None = None
        self._env_overlays: tuple[dict, dict] | None = None

    def _project_config_paths(self) -> list[str]:
        return get_project_config_paths(self._cfg_dir)

    def load_project_config(
        self,
        reload: bool = False,
        name: str | None = None,
    ) -> ProjectConfig:
        """Load project configuration.

        Args:
            reload: Whether to reload the configuration even if already loaded

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
        requested_name = None if project_config_exists else (name if name is not None else self._current_project_name)

        if (
            self._project_cfg is None
            or self._current_project_name != requested_name
            or reload
        ):
            load_kwargs = {
                "base_dir": self._base_dir,
                "fs": self._fs,
                "storage_options": self._storage_options,
                "cfg_dir": self._cfg_dir,
            }
            if requested_name is not None:
                load_kwargs["name"] = requested_name

            self._project_cfg = ProjectConfig.load(**load_kwargs)
            self._current_project_name = requested_name

            self._env_overlays = apply_env_overlays(
                project_cfg=self._project_cfg,
                overlays=None if reload else self._env_overlays,
            )

        return self._project_cfg

    def load_pipeline_config(
        self,
        name: str | None,
        reload: bool = False,
    ) -> PipelineConfig:
        """Load pipeline configuration.

        Args:
            name: Name of the pipeline to load
            reload: Whether to reload the configuration even if already loaded

        Returns:
            PipelineConfig: The loaded pipeline configuration
        """
        if name is not None:
            name = validate_pipeline_name(name)

        if self._pipeline_cfg is None or self._current_pipeline_name != name or reload:
            # Ensure project config is loaded first
            self.load_project_config(reload=reload)

            # Load configuration through the canonical loader
            self._pipeline_cfg = PipelineConfig.load(
                base_dir=self._base_dir,
                name=name,
                fs=self._fs,
                storage_options=self._storage_options,
                cfg_dir=self._cfg_dir,
                pipelines_dir=self._pipelines_dir,
            )

            self._env_overlays = apply_env_overlays(
                pipeline_cfg=self._pipeline_cfg,
                overlays=self._env_overlays,
            )

            # Update current pipeline name
            self._current_pipeline_name = name

        return self._pipeline_cfg

    @property
    def project_config(self) -> ProjectConfig:
        """Get the current project configuration.

        Returns:
            ProjectConfig: The current project configuration

        Raises:
            ValueError: If project configuration has not been loaded
        """
        if self._project_cfg is None:
            raise ValueError(
                "Project configuration not loaded. Call load_project_config() first."
            )
        return self._project_cfg

    @property
    def pipeline_config(self) -> PipelineConfig:
        """Get the current pipeline configuration.

        Returns:
            PipelineConfig: The current pipeline configuration

        Raises:
            ValueError: If pipeline configuration has not been loaded
        """
        if self._pipeline_cfg is None:
            raise ValueError(
                "Pipeline configuration not loaded. Call load_pipeline_config() first."
            )
        return self._pipeline_cfg

    @property
    def current_pipeline_name(self) -> str | None:
        """Get the name of the currently loaded pipeline.

        Returns:
            str | None: Name of the current pipeline, or None if none loaded
        """
        return self._current_pipeline_name
