import posixpath

import msgspec
import yaml
from fsspeckit import AbstractFileSystem, BaseStorageOptions
from hamilton.function_modifiers import source, value
from munch import Munch, munchify

from ...settings import CONFIG_DIR, PIPELINES_DIR
from ...utils.filesystem import (
    find_first_existing_path,
    format_pipeline_file_path,
    get_pipeline_config_paths,
)
from ...utils.security import (
    SecurityError,
    validate_directory_fragment,
    validate_file_path,
    validate_pipeline_name,
)
from ...utils.yaml_env import interpolate_env_in_data
from ..base import BaseConfig
from ..exceptions import ConfigLoadError, ConfigSaveError
from .adapter import AdapterConfig
from .run import ExecutorConfig as ExecutorConfig
from .run import RunConfig, migrate_legacy_retry_fields
from .run import WithAdapterConfig as WithAdapterConfig


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
            self.name = validate_pipeline_name(self.name)

    def to_yaml(self, path: str, fs: AbstractFileSystem):
        """Save pipeline configuration to YAML file.

        Args:
            path: Path to the YAML file.
            fs: Filesystem instance.

        Raises:
            ConfigSaveError: If saving the configuration fails or path validation fails.
        """
        if fs is not None and "://" in str(path):
            validated_path = path
        else:
            try:
                # Validate the path to prevent directory traversal
                validated_path = validate_file_path(
                    path, allow_absolute=False, allow_relative=True
                )
            except SecurityError as e:
                raise ConfigSaveError(
                    f"Path validation failed: {e}", path=path, original_error=e
                ) from e

        try:
            fs.makedirs(posixpath.dirname(str(validated_path)) or ".", exist_ok=True)
            with fs.open(str(validated_path), "w") as f:
                d = self.to_dict()
                d.pop("h_params")
                yaml.dump(d, f, default_flow_style=False)
        except NotImplementedError as e:
            raise ConfigSaveError(
                "The filesystem does not support writing files.",
                path=str(validated_path),
                original_error=e,
            ) from e
        except Exception as e:
            raise ConfigSaveError(
                f"Failed to write configuration to {validated_path}",
                path=str(validated_path),
                original_error=e,
            ) from e

    @classmethod
    def from_dict(cls, name: str, data: dict | Munch):
        payload = dict(data)
        payload["name"] = name

        # Handle null params field by converting to empty dict
        # This fixes the issue where YAML parses empty sections with comments as null
        if payload.get("params") is None:
            payload["params"] = {}

        return msgspec.convert(payload, cls)

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
            ConfigLoadError: If loading the configuration fails or path validation fails.
        """
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
                raw = yaml.safe_load(f) or {}
                data = interpolate_env_in_data(raw)

            migrated = False
            if isinstance(data, dict) and isinstance(data.get("run"), dict):
                migrated = migrate_legacy_retry_fields(data["run"])

            stored_name = data.get("name") if isinstance(data, dict) else None
            pipeline_name = stored_name if isinstance(stored_name, str) else name

            pipeline = cls.from_dict(name=pipeline_name, data=data)

            if migrated:
                pipeline.to_yaml(path=validated_path, fs=fs)

            return pipeline
        except Exception as e:
            raise ConfigLoadError(
                f"Failed to load configuration from {validated_path}",
                path=str(validated_path),
                original_error=e,
            ) from e

    def update(self, d: dict | Munch):
        updates = dict(d)
        params = updates.pop("params", None)

        if updates:
            super().update(updates)

        if params is not None:
            self.params.update(munchify(params))
            self.params = munchify(self.params)
            self.h_params = munchify(self.to_h_params(self.params))

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

        result = {
            k: {k: d[k]} for k in d
        }  # Step 1: Wrap each parameter in its own dict

        # Step 2: Transform each parameter value recursively
        return {k: transform_recursive(v, d) for k, v in result.items()}

    @classmethod
    def load(
        cls,
        base_dir: str = ".",
        name: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = None,
        cfg_dir: str | None = None,
        pipelines_dir: str | None = None,
    ):
        """Load pipeline configuration from a YAML file.

        Args:
            base_dir (str, optional): Base directory for the pipeline. Defaults to ".".
            name (str | None, optional): Pipeline name. Defaults to None.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.
            cfg_dir (str, optional): Configuration directory. Defaults to CONFIG_DIR.
            pipelines_dir (str, optional): Pipelines subdirectory. Defaults to PIPELINES_DIR.

        Returns:
            PipelineConfig: Loaded pipeline configuration.
        """
        if name is not None:
            name = validate_pipeline_name(name)

        if cfg_dir is None:
            cfg_dir = CONFIG_DIR
        if pipelines_dir is None:
            pipelines_dir = PIPELINES_DIR
        cfg_dir = validate_directory_fragment(cfg_dir)
        pipelines_dir = validate_directory_fragment(pipelines_dir)
        if fs is None:
            fs = cls._get_cached_filesystem(base_dir, storage_options)

        if name is None:
            return cls(name=name)

        formatted_name = format_pipeline_file_path(name)
        possible_paths = get_pipeline_config_paths(
            formatted_name,
            cfg_dir,
            pipelines_dir,
        )

        existing_path = find_first_existing_path(
            fs,
            possible_paths,
            purpose="pipeline config",
        )
        if existing_path is not None:
            return cls.from_yaml(name=name, path=existing_path, fs=fs)

        return cls(name=name)

    def save(
        self,
        name: str | None = None,
        base_dir: str = ".",
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = None,
        cfg_dir: str | None = None,
        pipelines_dir: str | None = None,
    ):
        """Save pipeline configuration to a YAML file.

        Args:
            name (str | None, optional): Pipeline name. Defaults to None.
            base_dir (str, optional): Base directory for the pipeline. Defaults to ".".
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.
            cfg_dir (str, optional): Configuration directory. Defaults to CONFIG_DIR.
            pipelines_dir (str, optional): Pipelines subdirectory. Defaults to PIPELINES_DIR.

        Raises:
            ValueError: If pipeline name is not set.
        """
        if cfg_dir is None:
            cfg_dir = CONFIG_DIR
        if pipelines_dir is None:
            pipelines_dir = PIPELINES_DIR
        cfg_dir = validate_directory_fragment(cfg_dir)
        pipelines_dir = validate_directory_fragment(pipelines_dir)
        if fs is None:
            fs = self._get_cached_filesystem(base_dir, storage_options)

        if name is not None:
            self.name = name
        if self.name is None:
            raise ValueError("Pipeline name is not set. Please provide a name.")

        # Validate pipeline name
        self.name = validate_pipeline_name(self.name)

        formatted_name = format_pipeline_file_path(self.name)
        file_path = get_pipeline_config_paths(
            formatted_name,
            cfg_dir,
            pipelines_dir,
        )[0]

        self.to_yaml(path=file_path, fs=fs)


def init_pipeline_config(
    base_dir: str = ".",
    name: str | None = None,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    cfg_dir: str | None = None,
    pipelines_dir: str | None = None,
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
        base_dir=base_dir,
        name=name,
        fs=fs,
        storage_options=storage_options,
        cfg_dir=cfg_dir,
        pipelines_dir=pipelines_dir,
    )
    pipeline.save(
        name=name,
        base_dir=base_dir,
        fs=fs,
        storage_options=storage_options,
        cfg_dir=cfg_dir,
        pipelines_dir=pipelines_dir,
    )
    return pipeline
