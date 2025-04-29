import msgspec
import yaml
from hamilton.function_modifiers import source, value
from munch import Munch, munchify

from ...fs import AbstractFileSystem, BaseStorageOptions, get_filesystem
from ..base import BaseConfig
from .adapter import AdapterConfig
from .run import RunConfig
from .schedule import ScheduleConfig


class PipelineConfig(BaseConfig):
    """Configuration class for managing pipeline settings in FlowerPower.

    This class handles pipeline-specific configuration including run settings, scheduling,
    parameters, and adapter settings. It supports Hamilton-style parameter configuration
    and YAML serialization.

    Attributes:
        name (str | None): The name of the pipeline.
        run (RunConfig): Configuration for pipeline execution.
        schedule (ScheduleConfig): Configuration for pipeline scheduling.
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
    schedule: ScheduleConfig = msgspec.field(default_factory=ScheduleConfig)
    params: dict = msgspec.field(default_factory=dict)
    adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)
    h_params: dict = msgspec.field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.params, dict):
            self.h_params = munchify(self.to_h_params(self.params))
            self.params = munchify(self.params)

    def to_yaml(self, path: str, fs: AbstractFileSystem):
        try:
            fs.makedirs(fs._parent(path), exist_ok=True)
            with fs.open(path, "w") as f:
                d = self.to_dict()
                d.pop("name")
                d.pop("h_params")
                yaml.dump(d, f, default_flow_style=False)
        except NotImplementedError:
            raise NotImplementedError(
                "The filesystem "
                f"{self.fs.fs.protocol[0] if isinstance(self.fs.fs.protocol, tuple) else self.fs.fs.protocol} "
                "does not support writing files."
            )

    @classmethod
    def from_dict(cls, name: str, data: dict | Munch):
        data.update({"name": name})
        return msgspec.convert(data, cls)

    @classmethod
    def from_yaml(cls, name: str, path: str, fs: AbstractFileSystem):
        with fs.open(path) as f:
            data = yaml.full_load(f)
            return cls.from_dict(name=name, data=data)

    def update(self, d: dict | Munch):
        for k, v in d.items():
            eval(f"self.{k}.update({v})")
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

        # Step 1: Replace each value with a dictionary containing key and value
        result = {k: {k: d[k]} for k in d}

        # Step 2: Transform all values recursively
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
            fs = get_filesystem(
                base_dir, cached=False, dirfs=True, storage_options=storage_options
            )
        if fs.exists("conf/pipelines"):
            if name is not None:
                pipeline = PipelineConfig.from_yaml(
                    name=name,
                    path=f"conf/pipelines/{name}.yml",
                    fs=fs,
                )
            else:
                pipeline = PipelineConfig(name=name)
        else:
            pipeline = PipelineConfig(name=name)

        return pipeline

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
            fs = get_filesystem(
                base_dir, cached=True, dirfs=True, storage_options=storage_options
            )

        fs.makedirs("conf/pipelines", exist_ok=True)
        if name is not None:
            self.name = name
        if self.name is None:
            raise ValueError("Pipeline name is not set. Please provide a name.")

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
