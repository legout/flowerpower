from pathlib import Path

import msgspec
from munch import Munch

from ..fs import get_filesystem, AbstractFileSystem
#from .base import BaseConfig
from .pipeline import PipelineConfig
from .project import ProjectConfig

import copy

from typing import Any, Self

from fsspec import filesystem


class BaseConfig(msgspec.Struct, kw_only=True):
    def to_dict(self) -> dict[str, Any]:
        return msgspec.to_builtins(self)

    def to_yaml(self, path: str, fs: AbstractFileSystem | None = None) -> None:
        """
        Converts the instance to a YAML file.
        
        Args:
            path: The path to the YAML file.
            fs: An optional filesystem instance to use for file operations.
            
        Raises:
            NotImplementedError: If the filesystem does not support writing files.  
        """
        if fs is None:
            fs = filesystem("file")
        try:
            with fs.open(path, "wb") as f:
                f.write(msgspec.yaml.encode(self, order="deterministic"))
                # yaml.dump(self.to_dict(), f, default_flow_style=False)
        except NotImplementedError:
            raise NotImplementedError("The filesystem does not support writing files.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseConfig":
        """
        Converts a dictionary to an instance of the class.
        Args:
            data: The dictionary to convert.
        
        Returns:
            An instance of the class with the values from the dictionary.
        """
        return msgspec.convert(data, cls)

    @classmethod
    def from_yaml(cls, path: str, fs: AbstractFileSystem | None = None) -> "BaseConfig":
        """
        Loads a YAML file and converts it to an instance of the class.
        
        Args:
            path: The path to the YAML file.
            fs: An optional filesystem instance to use for file operations.

        Returns:
            An instance of the class with the values from the YAML file.
        
        """
        if fs is None:
            fs = filesystem("file")
        with fs.open(path) as f:
            # data = yaml.full_load(f)
            # return cls.from_dict(data)
            return msgspec.yaml.decode(f.read(), type=cls, strict=False)

    def update(self, d: dict[str, Any]) -> None:
        for k, v in d.items():
            if hasattr(self, k):
                current_value = getattr(self, k)
                if isinstance(current_value, dict) and isinstance(v, dict):
                    current_value.update(v)
                else:
                    setattr(self, k, v)
            else:
                setattr(self, k, v)

    def merge_dict(self, d: dict[str, Any]) -> Self:
        """
        Creates a copy of this instance and updates the copy with values
        from the provided dictionary, only if the dictionary field's value is not
        its default value. The original instance (self) is not modified.
        
        Args:
            d: The dictionary to get values from.

        Returns:
            A new instance of the struct with updated values.
        """
        self_copy = copy.copy(self)
        for k, v in d.items():
            if hasattr(self_copy, k):
                current_value = getattr(self_copy, k)
                if isinstance(current_value, dict) and isinstance(v, dict):
                    current_value.update(v)
                else:
                    setattr(self_copy, k, v)
            else:
                setattr(self_copy, k, v)
        return self_copy
    
    def merge(self, source: Self) -> Self:
        """
        Creates a copy of this instance and updates the copy with values
        from the source struct, only if the source field's value is not
        its default value. The original instance (self) is not modified.

        Args:
            source: The msgspec.Struct instance of the same type to get values from.

        Returns:
            A new instance of the struct with updated values.

        Raises:
            TypeError: If source is not of the same type as self.
        """
        if type(self) is not type(source):
            raise TypeError(f"Source must be an instance of {type(self).__name__}, not {type(source).__name__}")

        updated_instance = copy.copy(self)

        # Get default values if they exist
        defaults = getattr(source, '__struct_defaults__', {})

        for field in source.__struct_fields__:
            source_value = getattr(source, field)
            has_explicit_default = field in defaults
            is_default_value = False

            if has_explicit_default:
                is_default_value = (source_value == defaults[field])
            else:
                is_default_value = (source_value is None)

            if not is_default_value:
               setattr(updated_instance, field, source_value)

        return updated_instance

class Config(BaseConfig):
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
        worker_type: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | Munch = Munch(),
    ):
        if fs is None:
            fs = get_filesystem(base_dir, cached=True, dirfs=True, **storage_options)
        project = ProjectConfig.load(
            base_dir=base_dir,
            name=name,
            worker_type=worker_type,
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
        storage_options: dict | Munch = Munch(),
    ):
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
    storage_options: dict | Munch = Munch(),
    fs: AbstractFileSystem | None = None,
):
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
    storage_options: dict | Munch = Munch(),
):
    config.save(
        project=project, pipeline=pipeline, fs=fs, storage_options=storage_options
    )
