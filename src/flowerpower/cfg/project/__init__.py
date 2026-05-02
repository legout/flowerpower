import posixpath

import msgspec
from fsspeckit import AbstractFileSystem, BaseStorageOptions

from ...settings import CONFIG_DIR, HOOKS_DIR
from ...utils.filesystem import find_first_existing_path, get_project_config_paths
from ...utils.security import (
    SecurityError,
    validate_directory_fragment,
    validate_file_path,
)
from ...utils.yaml_env import interpolate_env_in_data
from ..base import BaseConfig
from ..exceptions import ConfigLoadError
from .adapter import AdapterConfig


class ProjectConfig(BaseConfig):
    """A configuration class for managing project-level settings in FlowerPower.

    This class handles project-wide configuration including adapter settings.
    It supports loading from and saving to YAML files, with filesystem abstraction.

    Attributes:
        name (str | None): The name of the project.
        adapter (AdapterConfig): Configuration for the adapter component.

    Example:
        ```python
        # Create a new project config
        project = ProjectConfig(name="my-project")

        # Load existing project config
        project = ProjectConfig.load(base_dir="path/to/project")

        # Save project config
        project.save(base_dir="path/to/project")
        ```
    """

    name: str | None = msgspec.field(default=None)
    hooks_dir: str = msgspec.field(default=HOOKS_DIR)
    adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)

    def __post_init__(self):
        if isinstance(self.adapter, dict):
            self.adapter = AdapterConfig.from_dict(self.adapter)

        validate_file_path(
            self.hooks_dir,
            allow_absolute=False,
            allow_relative=True,
        )

        # Validate project name if provided
        if self.name is not None:
            self._validate_project_name()

    def _validate_project_name(self) -> None:
        """Validate project name parameter.

        Raises:
            ValueError: If project name contains invalid characters.
        """
        if not isinstance(self.name, str):
            raise ValueError(f"Project name must be a string, got {type(self.name)}")

        # Check for directory traversal attempts
        if ".." in self.name or "/" in self.name or "\\" in self.name:
            raise ValueError(
                f"Invalid project name: {self.name}. Contains path traversal characters."
            )

        # Check for empty string
        if not self.name.strip():
            raise ValueError("Project name cannot be empty or whitespace only.")

    @classmethod
    def load(
        cls,
        base_dir: str = ".",
        name: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = None,
        cfg_dir: str | None = None,
    ):
        """Load project configuration from a YAML file.

        Args:
            base_dir (str, optional): Base directory for the project. Defaults to ".".
            name (str | None, optional): Project name. Defaults to None.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict, optional): Options for filesystem. Defaults to empty dict.
            cfg_dir (str, optional): Configuration directory. Defaults to CONFIG_DIR.

        Returns:
            ProjectConfig: Loaded project configuration.

        Example:
            ```python
            project = ProjectConfig.load(
                base_dir="my_project",
                name="pipeline1"
                )
            ```
        """
        if cfg_dir is None:
            cfg_dir = CONFIG_DIR
        cfg_dir = validate_directory_fragment(cfg_dir)
        if fs is None:
            fs = cls._get_cached_filesystem(base_dir, storage_options)

        cfg_path = find_first_existing_path(
            fs,
            get_project_config_paths(cfg_dir),
            purpose="project config",
        )
        if cfg_path is not None:
            return cls.from_yaml(path=cfg_path, fs=fs)
        return cls(name=name)

    @classmethod
    def from_yaml(cls, path: str, fs: AbstractFileSystem):
        if fs is not None and "://" in str(path):
            validated_path = path
        else:
            try:
                # Validate the path to prevent directory traversal
                validated_path = validate_file_path(
                    path, allow_absolute=False, allow_relative=True
                )
            except SecurityError as e:
                raise ConfigLoadError(
                    f"Path validation failed: {e}", path=path, original_error=e
                ) from e

        try:
            with fs.open(str(validated_path)) as f:
                raw = f.read()
        except Exception as e:
            raise ConfigLoadError(
                f"Failed to load configuration from {validated_path}",
                path=str(validated_path),
                original_error=e,
            ) from e
        try:
            import yaml as _yaml

            data = _yaml.safe_load(raw) or {}
            data = interpolate_env_in_data(data)
        except Exception as e:
            raise ConfigLoadError(
                f"Failed to parse YAML for {path}", path=path, original_error=e
            ) from e
        try:
            return msgspec.convert(data, cls)
        except Exception as e:
            raise ConfigLoadError(
                f"Failed to validate configuration from {validated_path}",
                path=str(validated_path),
                original_error=e,
            ) from e

    def save(
        self,
        base_dir: str = ".",
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = None,
        cfg_dir: str | None = None,
    ):
        """Save project configuration to a YAML file.

        Args:
            base_dir (str, optional): Base directory for the project. Defaults to ".".
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict, optional): Options for filesystem. Defaults to empty dict.
            cfg_dir (str, optional): Configuration directory. Defaults to CONFIG_DIR.

        Example:
            ```python
            project_config.save(base_dir="my_project")
            ```
        """
        if cfg_dir is None:
            cfg_dir = CONFIG_DIR
        cfg_dir = validate_directory_fragment(cfg_dir)
        if fs is None:
            fs = self._get_cached_filesystem(base_dir, storage_options)

        cfg_path = get_project_config_paths(cfg_dir)[0]
        save_dir = posixpath.dirname(cfg_path) or "."
        fs.makedirs(save_dir, exist_ok=True)
        self.to_yaml(path=cfg_path, fs=fs)


def init_project_config(
    base_dir: str = ".",
    name: str | None = None,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    cfg_dir: str | None = None,
):
    """Initialize a new project configuration.

    This function creates a new project configuration and saves it to disk.

    Args:
        base_dir (str, optional): Base directory for the project. Defaults to ".".
        name (str | None, optional): Project name. Defaults to None.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict, optional): Options for filesystem. Defaults to empty dict.

    Returns:
        ProjectConfig: The initialized project configuration.

    Example:
        ```python
        project = init_project_config(
            base_dir="my_project",
            name="test_project"
        )
        ```
    """
    project = ProjectConfig.load(
        base_dir=base_dir,
        name=name,
        fs=fs,
        storage_options=storage_options,
        cfg_dir=cfg_dir,
    )
    project.save(
        base_dir=base_dir,
        fs=fs,
        storage_options=storage_options,
        cfg_dir=cfg_dir,
    )
    return project
