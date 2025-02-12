from pathlib import Path

import yaml
from fsspec import AbstractFileSystem
from hamilton.function_modifiers import source, value
from munch import Munch, munchify
from pydantic import Field

from ..fs import get_filesystem
from .base import BaseConfig
from .pipeline.run import PipelineRunConfig
from .pipeline.schedule import PipelineScheduleConfig
from .pipeline.tracker import PipelineTrackerConfig
from .project.open_telemetry import ProjectOpenTelemetryConfig
from .project.tracker import ProjectTrackerConfig
from .project.worker import ProjectWorkerConfig


class PipelineConfig(BaseConfig):
    name: str | None = None
    run: PipelineRunConfig = Field(default_factory=PipelineRunConfig)
    schedule: PipelineScheduleConfig = Field(default_factory=PipelineScheduleConfig)
    params: dict | Munch = {}
    tracker: PipelineTrackerConfig = Field(default_factory=PipelineTrackerConfig)
    h_params: dict | Munch = {}

    def model_post_init(self, __context):
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
    def from_dict(cls, name: str, d: dict | Munch):
        d.update({"name": name})
        return cls(**d)

    @classmethod
    def from_yaml(cls, name: str, path: str, fs: AbstractFileSystem):
        with fs.open(path) as f:
            return cls.from_dict(name, yaml.full_load(f))

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
    # def to_h_params(d: dict) -> dict:
    #     """Coverts a dictionary of function arguments to Hamilton function parameters"""
    #
    #     def transform_recursive(val, original_dict):
    #         # If it's a dictionary, recursively transform its values
    #         if isinstance(val, dict):
    #             return {
    #                 k: transform_recursive(v, original_dict) for k, v in val.items()
    #             }
    #         # If it's a string and matches a key in the original dictionary
    #         elif isinstance(val, str) and val in original_dict:
    #             return source(val)
    #         # For all other values
    #         else:
    #             return value(val)
    #
    #     # Step 1: Replace each value with a dictionary containing key and value
    #     result = {k: {k: d[k]} for k in d}
    #
    #     # Step 2 & 3: Transform all values recursively
    #     return {k: transform_recursive(v, d) for k, v in result.items()}
    def to_h_params(d: dict) -> dict:
        """Converts a dictionary of function arguments to Hamilton function parameters"""

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


class ProjectConfig(BaseConfig):
    name: str | None = None
    worker: ProjectWorkerConfig = Field(default_factory=ProjectWorkerConfig)
    tracker: ProjectTrackerConfig = Field(default_factory=ProjectTrackerConfig)
    open_telemetry: ProjectOpenTelemetryConfig = Field(
        default_factory=ProjectOpenTelemetryConfig
    )


class Config(BaseConfig):
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    fs: AbstractFileSystem | None = None
    base_dir: str | Path | None = None
    storage_options: dict | Munch = Field(default_factory=Munch)

    @classmethod
    def load(
        cls,
        base_dir: str = "",
        name: str | None = None,
        pipeline_name: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | Munch = Munch(),
    ):
        if fs is None:
            fs = get_filesystem(base_dir, cached=True, dirfs=True, **storage_options)
        if fs.exists("conf/project.yml"):
            project = ProjectConfig.from_yaml(path="conf/project.yml", fs=fs)
        else:
            project = ProjectConfig(name=name)

        if pipeline_name is not None:
            if fs.exists(f"conf/pipelines/{pipeline_name}.yml"):
                pipeline = PipelineConfig.from_yaml(
                    name=pipeline_name,
                    path=f"conf/pipelines/{pipeline_name}.yml",
                    fs=fs,
                )
            else:
                pipeline = PipelineConfig(name=pipeline_name)
        else:
            pipeline = PipelineConfig(name=pipeline_name)

        return cls(
            base_dir=base_dir,
            pipeline=pipeline,
            project=project,
            fs=fs,
            storage_options=storage_options,
        )

    def save(self):
        if not self.fs.exists("conf"):
            self.fs.makedirs("conf")

        if self.pipeline.name is not None:
            # h_params = self.pipeline.params.pop("h_params") if "h_params" in self.pipeline.params else None
            self.pipeline.to_yaml(
                f"conf/pipelines/{self.pipeline.name.replace('.', '/')}.yml", self.fs
            )
            # if h_params is not None:
            #    self.pipeline.params["h_params"] = h_params
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


def save(config: Config):
    config.save()
