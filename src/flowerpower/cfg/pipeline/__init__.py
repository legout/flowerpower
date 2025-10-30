import msgspec
import yaml
from fsspeckit import AbstractFileSystem, BaseStorageOptions, filesystem
from hamilton.function_modifiers import source, value
from munch import Munch, munchify
from typing import Optional

from ..base import BaseConfig, validate_file_path
from ..exceptions import ConfigLoadError, ConfigSaveError, ConfigPathError
from .adapter import AdapterConfig
from .run import ExecutorConfig as ExecutorConfig
from .run import RunConfig
from .run import WithAdapterConfig as WithAdapterConfig
from .run import migrate_legacy_retry_fields
from ...utils.yaml_env import interpolate_env_in_data


class PipelineConfig(BaseConfig):
    """Configuration class for managing pipeline settings in FlowerPower.

    This class handles pipeline-specific configuration including run settings, scheduling,
    parameters, and adapter settings. It supports Hamilton-style parameter configuration
    and YAML serialization.

    Attributes:
        name (str | None): The name of the pipeline.
        run (RunConfig): Configuration for pipeline execution.
        params (dict): Pipeline parameters.
        adapter (AdapterConfig): Configuration for the pipeline adapter.
        h_params (dict): Hamilton-formatted parameters.

    Example:
        ```python
        # Create a new pipeline config
        pipeline = PipelineConfig(name="data-transform")

        # Set parameters
        pipeline.params = {
            "input_path": "data/input",
            "batch_size": 100
        }

        # Save configuration
        pipeline.save(name="data-transform")
        ```
    """

    name: str | None = msgspec.field(default=None)
    run: RunConfig = msgspec.field(default_factory=RunConfig)
    params: dict = msgspec.field(default_factory=dict)
    adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)
    h_params: dict = msgspec.field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.params, dict):
            self.h_params = munchify(self.to_h_params(self.params))
            self.params = munchify(self.params)
        
        # Validate pipeline name if provided
        if self.name is not None:
            self._validate_pipeline_name()

    def to_yaml(self, path: str, fs: AbstractFileSystem):
        """Save pipeline configuration to YAML file.
        
        Args:
            path: Path to the YAML file.
            fs: Filesystem instance.
            
        Raises:
            ConfigSaveError: If saving the configuration fails.
            ConfigPathError: If the path contains directory traversal attempts.
        """
        try:
            # Validate the path to prevent directory traversal
            validated_path = validate_file_path(path)
        except ConfigPathError as e:
            raise ConfigSaveError(f"Path validation failed: {e}", path=path, original_error=e)
            
        try:
            fs.makedirs(fs._parent(validated_path), exist_ok=True)
            with fs.open(validated_path, "w") as f:
                d = self.to_dict()
                d.pop("name")
                d.pop("h_params")
                yaml.dump(d, f, default_flow_style=False)
        except NotImplementedError as e:
            raise ConfigSaveError(
                f"The filesystem does not support writing files.",
                path=validated_path,
                original_error=e
            )
        except Exception as e:
            raise ConfigSaveError(
                f"Failed to write configuration to {validated_path}",
                path=validated_path,
                original_error=e
            )

    @classmethod
    def from_dict(cls, name: str, data: dict | Munch):
        data.update({"name": name})
        
        # Handle null params field by converting to empty dict
        # This fixes the issue where YAML parses empty sections with comments as null
        if data.get('params') is None:
            data['params'] = {}
        
        instance = msgspec.convert(data, cls)
        # Manually call __post_init__ since msgspec.convert doesn't call it
        instance.__post_init__()
        return instance

    @classmethod
    def from_yaml(cls, name: str, path: str, fs: AbstractFileSystem):
        """Load pipeline configuration from YAML file.
        
        Args:
            name: Pipeline name.
            path: Path to the YAML file.
            fs: Filesystem instance.
            
        Returns:
            Loaded pipeline configuration.
            
        Raises:
            ConfigLoadError: If loading the configuration fails.
            ConfigPathError: If the path contains directory traversal attempts.
        """
        try:
            # Validate the path to prevent directory traversal
            validated_path = validate_file_path(path)
        except ConfigPathError as e:
            raise ConfigLoadError(f"Path validation failed: {e}", path=path, original_error=e)
            
        try:
            with fs.open(validated_path) as f:
                raw = yaml.safe_load(f) or {}
                data = interpolate_env_in_data(raw)

            migrated = False
            if isinstance(data, dict) and isinstance(data.get('run'), dict):
                migrated = migrate_legacy_retry_fields(data['run'])

            pipeline = cls.from_dict(name=name, data=data)

            if migrated:
                pipeline.to_yaml(path=validated_path, fs=fs)

            return pipeline
        except Exception as e:
            raise ConfigLoadError(
                f"Failed to load configuration from {validated_path}",
                path=validated_path,
                original_error=e
            )

    def update(self, d: dict | Munch):
        for k, v in d.items():
            # Safe attribute access instead of eval()
            if hasattr(self, k) and hasattr(getattr(self, k), 'update'):
                getattr(self, k).update(v)
            if k == "params":
                self.params.update(munchify(v))
                self.h_params = munchify(self.to_h_params(self.params))
                # self.params = munchify(self.params)
        if "params" in d:
            self.h_params = munchify(self.to_h_params(self.params))
            self.params = munchify(self.params)

    @staticmethod
    def to_h_params(d: dict) -> dict:
        """Convert a dictionary of parameters to Hamilton-compatible format.

        This method transforms regular parameter dictionaries into Hamilton's function parameter
        format, supporting nested parameters and source/value decorators.

        Args:
            d (dict): The input parameter dictionary.

        Returns:
            dict: Hamilton-formatted parameter dictionary.

        Example:
            ```python
            params = {
                "batch_size": 100,
                "paths": {"input": "data/in", "output": "data/out"}
            }
            h_params = PipelineConfig.to_h_params(params)
            ```
        """

        def transform_recursive(val, original_dict, depth=1):
            if isinstance(val, dict):
                # If we're at depth 3, wrap the entire dictionary in value()
                if depth == 3:
                    return value(val)
                # Otherwise, continue recursing
                return {
                    k: transform_recursive(v, original_dict, depth + 1)
                    for k, v in val.items()
                }
            # If it's a string and matches a key in the original dictionary
            elif isinstance(val, str) and val in original_dict:
                return source(val)
            # For non-dictionary values at depth 3
            elif depth == 3:
                return value(val)
            # For all other values
            return val
        
        result = {k: {k: d[k]} for k in d}  # Step 1: Wrap each parameter in its own dict
        
        # Step 2: Transform each parameter value recursively
        return {k: transform_recursive(v, d) for k, v in result.items()}

    @classmethod
    def load(
        cls,
        base_dir: str = ".",
        name: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
    ):
        """Load pipeline configuration from a YAML file.

        Args:
            base_dir (str, optional): Base directory for the pipeline. Defaults to ".".
            name (str | None, optional): Pipeline name. Defaults to None.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Returns:
            PipelineConfig: Loaded pipeline configuration.

        Example:
            ```python
            pipeline = PipelineConfig.load(
                base_dir="my_project",
                name="data-pipeline"
            )
            ```
        """
        if fs is None:
            # Use cached filesystem for better performance
            storage_options_hash = cls._hash_storage_options(storage_options)
            fs = cls._get_cached_filesystem(base_dir, storage_options_hash)
        if fs.exists("conf/pipelines") and name is not None:
            
            pipeline = PipelineConfig.from_yaml(
                name=name,
                path=f"conf/pipelines/{name}.yml",
                fs=fs,
            )
        else:
            pipeline = PipelineConfig(name=name)

        return pipeline
    
    
    # Helper methods for centralized load/save logic
    @classmethod
    def _load_pipeline_config(cls, base_dir: str, name: str | None, fs: AbstractFileSystem) -> "PipelineConfig":
        """Centralized pipeline configuration loading logic.
        
        Args:
            base_dir: Base directory for the pipeline.
            name: Pipeline name.
            fs: Filesystem instance.
            
        Returns:
            Loaded pipeline configuration.
        """
        if fs.exists("conf/pipelines") and name is not None:
            pipeline = cls.from_yaml(
                name=name,
                path=f"conf/pipelines/{name}.yml",
                fs=fs,
            )
        else:
            pipeline = cls(name=name)
        return pipeline
    
    
    def _save_pipeline_config(self, fs: AbstractFileSystem) -> None:
        """Centralized pipeline configuration saving logic.
        
        Args:
            fs: Filesystem instance.
        """
        h_params = getattr(self, "h_params")
        self.to_yaml(path=f"conf/pipelines/{self.name}.yml", fs=fs)
        setattr(self, "h_params", h_params)
    
    def _validate_pipeline_name(self) -> None:
        """Validate pipeline name parameter.
        
        Raises:
            ValueError: If pipeline name contains invalid characters.
        """
        if not isinstance(self.name, str):
            raise ValueError(f"Pipeline name must be a string, got {type(self.name)}")
        
        # Check for directory traversal attempts
        if '..' in self.name or '/' in self.name or '\\' in self.name:
            raise ValueError(f"Invalid pipeline name: {self.name}. Contains path traversal characters.")
        
        # Check for empty string
        if not self.name.strip():
            raise ValueError("Pipeline name cannot be empty or whitespace only.")

    def save(
        self,
        name: str | None = None,
        base_dir: str = ".",
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
    ):
        """Save pipeline configuration to a YAML file.

        Args:
            name (str | None, optional): Pipeline name. Defaults to None.
            base_dir (str, optional): Base directory for the pipeline. Defaults to ".".
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Raises:
            ValueError: If pipeline name is not set.

        Example:
            ```python
            pipeline_config.save(name="data-pipeline", base_dir="my_project")
            ```
        """
        if fs is None:
            # Use cached filesystem for better performance
            storage_options_hash = self._hash_storage_options(storage_options)
            fs = self._get_cached_filesystem(base_dir, storage_options_hash)

        fs.makedirs("conf/pipelines", exist_ok=True)
        if name is not None:
            self.name = name
        if self.name is None:
            raise ValueError("Pipeline name is not set. Please provide a name.")

        # Validate pipeline name to prevent directory traversal
        if self.name and ('..' in self.name or '/' in self.name or '\\' in self.name):
            raise ValueError(f"Invalid pipeline name: {self.name}. Contains path traversal characters.")

        h_params = getattr(self, "h_params")

        self.to_yaml(path=f"conf/pipelines/{self.name}.yml", fs=fs)

        setattr(self, "h_params", h_params)


def init_pipeline_config(
    base_dir: str = ".",
    name: str | None = None,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | BaseStorageOptions | None = {},
):
    """Initialize a new pipeline configuration.

    This function creates a new pipeline configuration and saves it to disk.

    Args:
        base_dir (str, optional): Base directory for the pipeline. Defaults to ".".
        name (str | None, optional): Pipeline name. Defaults to None.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

    Returns:
        PipelineConfig: The initialized pipeline configuration.

    Example:
        ```python
        pipeline = init_pipeline_config(
            base_dir="my_project",
            name="etl-pipeline"
        )
        ```
    """
    pipeline = PipelineConfig.load(
        base_dir=base_dir, name=name, fs=fs, storage_options=storage_options
    )
    pipeline.save(name=name, base_dir=base_dir, fs=fs, storage_options=storage_options)
    return pipeline
