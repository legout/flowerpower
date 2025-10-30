import msgspec
from fsspeckit import AbstractFileSystem, BaseStorageOptions, filesystem
import posixpath
from typing import Optional

from ...settings import CONFIG_DIR
from ..base import BaseConfig
from ..exceptions import ConfigLoadError, ConfigSaveError, ConfigPathError
from .adapter import AdapterConfig
from ...utils.yaml_env import interpolate_env_in_data


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
    adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)

    def __post_init__(self):
        if isinstance(self.adapter, dict):
            self.adapter = AdapterConfig.from_dict(self.adapter)
        
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
        if '..' in self.name or '/' in self.name or '\\' in self.name:
            raise ValueError(f"Invalid project name: {self.name}. Contains path traversal characters.")
        
        # Check for empty string
        if not self.name.strip():
            raise ValueError("Project name cannot be empty or whitespace only.")

    @classmethod
    def _load_project_config(cls, fs: AbstractFileSystem, name: str | None) -> "ProjectConfig":
        """Centralized project configuration loading logic.
        
        Args:
            fs: Filesystem instance.
            name: Project name.
            
        Returns:
            Loaded project configuration.
        """
        if fs.exists("conf/project.yml"):
            project = cls.from_yaml(path="conf/project.yml", fs=fs)
        else:
            project = cls(name=name)
        return project

    def _save_project_config(self, fs: AbstractFileSystem) -> None:
        """Centralized project configuration saving logic.
        
        Args:
            fs: Filesystem instance.
        """
        self.to_yaml(path=posixpath.join(CONFIG_DIR, "project.yml"), fs=fs)

    @classmethod
    def load(
        cls,
        base_dir: str = ".",
        name: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
    ):
        """Load project configuration from a YAML file.

        Args:
            base_dir (str, optional): Base directory for the project. Defaults to ".".
            name (str | None, optional): Project name. Defaults to None.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

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
        if fs is None:
            # Use cached filesystem for better performance
            storage_options_hash = cls._hash_storage_options(storage_options)
            fs = cls._get_cached_filesystem(base_dir, storage_options_hash)
        
        return cls._load_project_config(fs, name)

    @classmethod
    def from_yaml(cls, path: str, fs: AbstractFileSystem):
        try:
            with fs.open(path) as f:
                raw = f.read()
        except Exception as e:
            raise ConfigLoadError(f"Failed to load configuration from {path}", path=path, original_error=e)
        try:
            import yaml as _yaml
            data = _yaml.safe_load(raw) or {}
            data = interpolate_env_in_data(data)
        except Exception as e:
            raise ConfigLoadError(f"Failed to parse YAML for {path}", path=path, original_error=e)
        instance = msgspec.convert(data, cls)
        if hasattr(instance, "__post_init__"):
            instance.__post_init__()
        return instance

    def save(
        self,
        base_dir: str = ".",
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
    ):
        """Save project configuration to a YAML file.

        Args:
            base_dir (str, optional): Base directory for the project. Defaults to ".".
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Example:
            ```python
            project_config.save(base_dir="my_project")
            ```
        """
        if fs is None:
            # Use cached filesystem for better performance
            storage_options_hash = self._hash_storage_options(storage_options)
            fs = self._get_cached_filesystem(base_dir, storage_options_hash)

        fs.makedirs(CONFIG_DIR, exist_ok=True)
        self._save_project_config(fs)


def init_project_config(
    base_dir: str = ".",
    name: str | None = None,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | BaseStorageOptions | None = {},
):
    """Initialize a new project configuration.

    This function creates a new project configuration and saves it to disk.

    Args:
        base_dir (str, optional): Base directory for the project. Defaults to ".".
        name (str | None, optional): Project name. Defaults to None.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

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
    )
    project.save(base_dir=base_dir, fs=fs, storage_options=storage_options)
    return project

