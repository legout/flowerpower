import datetime as dt
import pathlib
from typing import Any

import yaml
from fsspec.spec import AbstractFileSystem
from hamilton.function_modifiers import source, value
from munch import Munch, munchify, unmunchify

# from dataclasses import asdict, dataclass, field
from pydantic import BaseModel, ConfigDict, Field

from .utils.filesystem import get_filesystem


class BaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self) -> dict[str, Any]:
        return unmunchify(self.model_dump())

    def to_yaml(self, path: str, fs: AbstractFileSystem | None = None) -> None:
        try:
            with fs.open(path, "w") as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
        except NotImplementedError:
            raise NotImplementedError(
                "The filesystem "
                f"{self.fs.fs.protocol[0] if isinstance(self.fs.fs.protocol, tuple) else self.fs.fs.protocol} "
                "does not support writing files."
            )

    @classmethod
    def from_dict(cls, d: dict[str, Any] | Munch) -> "BaseConfig":
        return cls(**d)

    @classmethod
    def from_yaml(cls, path: str, fs: AbstractFileSystem):
        # if fs is None:
        #    fs = get_filesystem(".", cached=True)
        with fs.open(path) as f:
            return cls.from_dict(yaml.full_load(f))

    def update(self, d: dict[str, Any] | Munch) -> None:
        for k, v in d.items():
            setattr(self, k, v)


class PipelineRunConfig(BaseConfig):
    final_vars: list[str] = Field(default_factory=list)
    inputs: dict | Munch = Field(default_factory=dict)
    executor: str | None = Field(default=None)
    with_tracker: bool = Field(default=False)
    with_opentelemetry: bool = Field(default=False)

    def model_post_init(self, __context):
        if isinstance(self.inputs, dict):
            self.inputs = munchify(self.inputs)


class PipelineScheduleTriggerConfig(BaseConfig):
    type_: str | None = Field(default=None)
    crontab: str | None = Field(default=None)
    year: str | int | None = Field(default=None)
    month: str | int | None = Field(default=None)
    weeks: int | float = Field(default=0)
    week: str | int | None = Field(default=None)
    days: int | float = Field(default=0)
    day: str | int | None = Field(default=None)
    day_of_week: str | int | None = Field(default=None)
    hours: int | float = Field(default=0)
    hour: str | int | None = Field(default=None)
    minutes: int | float = Field(default=0)
    minute: str | int | None = Field(default=None)
    seconds: int | float = Field(default=0)
    second: str | int | None = Field(default=None)
    start_time: dt.datetime | None = Field(default=None)
    end_time: dt.datetime | None = Field(default=None)
    timezone: str | None = Field(default=None)


class PipelineScheduleRunConfig(BaseConfig):
    id_: str | None = Field(default=None)
    executor: str | None = Field(default=None)
    paused: bool = Field(default=False)
    coalesce: str = Field(default="latest")  # other options are "all" and "earliest"
    misfire_grace_time: int | float | dt.timedelta | None = Field(default=None)
    max_jitter: int | float | dt.timedelta | None = Field(default=None)
    max_running_jobs: int | None = Field(default=None)
    conflict_policy: str | None = Field(
        default="do_nothing"
    )  # other options are "replace" and "exception"


class PipelineScheduleConfig(BaseConfig):
    run: PipelineScheduleRunConfig = Field(default_factory=PipelineScheduleRunConfig)
    trigger: PipelineScheduleTriggerConfig = Field(
        default_factory=PipelineScheduleTriggerConfig
    )


class PipelineTrackerConfig(BaseConfig):
    project_id: int | None = Field(default=None)
    version: str | None = Field(default=None)
    dag_name: str | None = Field(default=None)
    tags: dict | Munch = Field(default_factory=dict)

    def model_post_init(self, __context):
        self.tags = munchify(self.tags)


class PipelineConfig(BaseConfig):
    name: str | None = Field(default=None)
    run: PipelineRunConfig = Field(default_factory=PipelineRunConfig)
    schedule: PipelineScheduleConfig = Field(default_factory=PipelineScheduleConfig)
    params: dict | Munch = Field(default_factory=dict)
    tracker: PipelineTrackerConfig = Field(default_factory=PipelineTrackerConfig)
    h_params: dict | Munch = Field(default_factory=dict)

    def model_post_init(self, __context):
        if isinstance(self.params, dict):
            self.h_params = munchify(self.to_h_params(self.params))
            self.params = munchify(self.params)

    def to_yaml(self, path: str, fs: AbstractFileSystem):
        try:
            with fs.open(path, "w") as f:
                d = self.to_dict()
                d.pop("name")
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
    def to_h_params(d: dict) -> dict:
        """Coverts a dictionary of function arguments to Hamilton function parameters"""

        def transform_recursive(val, original_dict):
            # If it's a dictionary, recursively transform its values
            if isinstance(val, dict):
                return {
                    k: transform_recursive(v, original_dict) for k, v in val.items()
                }
            # If it's a string and matches a key in the original dictionary
            elif isinstance(val, str) and val in original_dict:
                return source(val)
            # For all other values
            else:
                return value(val)

        # Step 1: Replace each value with a dictionary containing key and value
        result = {k: {k: d[k]} for k in d}

        # Step 2 & 3: Transform all values recursively
        return {k: transform_recursive(v, d) for k, v in result.items()}


class ProjectWorkerConfig(BaseConfig):
    data_store: dict | Munch = Field(default_factory=dict)
    event_broker: dict | Munch = Field(default_factory=dict)
    cleanup_interval: int | float | dt.timedelta = Field(default=900)  # int in secods
    max_concurrent_jobs: int = Field(default=100)

    def model_post_init(self, __context):
        if isinstance(self.data_store, dict):
            self.data_store = munchify(self.data_store)
        if isinstance(self.event_broker, dict):
            self.event_broker = munchify(self.event_broker)


class ProjectTrackerConfig(BaseConfig):
    username: str | None = Field(default=None)
    api_url: str = "http://localhost:8241"
    ui_url: str = "http://localhost:8242"
    api_key: str | None = Field(default=None)


class ProjectOpenTelemetryConfig(BaseConfig):
    host: str = Field(default="localhost")
    port: int = Field(default=6831)


class ProjectConfig(BaseConfig):
    name: str | None = Field(default=None)
    worker: ProjectWorkerConfig = Field(default_factory=ProjectWorkerConfig)
    tracker: ProjectTrackerConfig = Field(default_factory=ProjectTrackerConfig)
    open_telemetry: ProjectOpenTelemetryConfig = Field(
        default_factory=ProjectOpenTelemetryConfig
    )


class Config(BaseConfig):
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    fs: AbstractFileSystem | None = Field(default=None)
    base_dir: str | pathlib.Path | None = Field(default=None)
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
            self.pipeline.to_yaml(f"conf/pipelines/{self.pipeline.name}.yml", self.fs)
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
