import datetime as dt
import os
from dataclasses import asdict, dataclass, field

import yaml
from hamilton.function_modifiers import source, value
from munch import Munch, munchify, unmunchify


@dataclass
class BaseConfig:
    def to_dict(self):
        return unmunchify(asdict(self))  # .__dict__)

    def to_yaml(self, path: str):
        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    @classmethod
    def from_dict(cls, d: dict | Munch):
        return cls(**d)

    @classmethod
    def from_yaml(cls, path: str):
        with open(path) as f:
            return cls.from_dict(yaml.full_load(f))


@dataclass
class PipelineRunConfig(BaseConfig):
    final_vars: list[str] = field(default_factory=list)
    inputs: dict | Munch = field(default_factory=dict)
    executor: str | None = None
    with_tracker: bool = False

    def __post_init__(self):
        if isinstance(self.inputs, dict):
            self.inputs = munchify(self.inputs)


@dataclass
class PipelineScheduleTriggerConfig(BaseConfig):
    type: str | None = None
    crontab: str | None = None
    year: str | int | None = None
    month: str | int | None = None
    weeks: int | float = 0
    week: str | int | None = None
    days: int | float = 0
    day: str | int | None = None
    minutes: int | float = 0
    minute: str | int | None = None
    seconds: int | float = 0
    second: str | int | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None
    timezone: str | None = None


@dataclass
class PipelineScheduleRunConfig(BaseConfig):
    id: str | None = None
    executor: str | None = None
    paused: bool = False
    coalesce: str = "latest"  # other options are "all" and "earliest"
    misfire_grace_time: int | float | dt.timedelta | None = None
    max_jitter: int | float | dt.timedelta | None = None
    max_running_jobs: int | None = None
    conflict_poilcy: str | None = (
        "do_nothing"  # other options are "replace" and "exception"
    )


@dataclass
class PipelineScheduleConfig(BaseConfig):
    run: PipelineScheduleRunConfig = field(default_factory=PipelineScheduleRunConfig)
    trigger: PipelineScheduleTriggerConfig = field(
        default_factory=PipelineScheduleTriggerConfig
    )


@dataclass
class PipelineTrackerConfig(BaseConfig):
    project_id: int | None = None
    version: str | None = None
    dag_name: str | None = None
    tags: dict | Munch = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.tags, dict):
            self.tags = munchify(self.tags)


@dataclass
class PipelineConfig(BaseConfig):
    name: str | None = None
    run: PipelineRunConfig = field(default_factory=PipelineRunConfig)
    schedule: PipelineScheduleConfig = field(default_factory=PipelineScheduleConfig)
    func: dict | Munch = field(default_factory=dict)
    tracker: PipelineTrackerConfig = field(default_factory=PipelineTrackerConfig)

    def __post_init__(self):
        self.run = PipelineRunConfig(
            **self.run if isinstance(self.run, dict | Munch) else self.run.to_dict()
        )
        self.schedule = PipelineScheduleConfig(
            **self.schedule
            if isinstance(self.schedule, dict | Munch)
            else self.schedule.to_dict()
        )
        self.tracker = PipelineTrackerConfig(
            **self.tracker
            if isinstance(self.tracker, dict | Munch)
            else self.tracker.to_dict()
        )
        if isinstance(self.func, dict):
            self.hamilton_func_params = munchify(self.f_args_to_ht_params(self.func))
            self.func = munchify(self.func)

    def to_dict(self):
        d = asdict(self)
        # d.pop("name")
        return unmunchify(d)

    def to_yaml(self, path: str):
        with open(path, "w") as f:
            d = self.to_dict()
            d.pop("name")
            yaml.dump(d, f, default_flow_style=False)

    @classmethod
    def from_dict(cls, name: str, d: dict | Munch):
        d.update({"name": name})
        return cls(**d)

    @classmethod
    def from_yaml(cls, name: str, path: str):
        with open(path) as f:
            return cls.from_dict(name, yaml.full_load(f))

    @staticmethod
    def f_args_to_ht_params(d: dict) -> dict:
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

        # result = {}
        # for key, val in d.items():
        #     result[key] = {
        #         key: val
        #     }

        # Step 1: Replace each value with a dictionary containing key and value
        result = {k: {k: d[k]} for k in d}

        # Step 2 & 3: Transform all values recursively
        return {k: transform_recursive(v, d) for k, v in result.items()}


@dataclass
class ProjectSchedulerConfig(BaseConfig):
    data_store: dict | Munch = field(default_factory=dict)
    event_broker: dict | Munch = field(default_factory=dict)
    cleanup_interval: int | float | dt.timedelta = 900  # int in secods
    max_concurrent_jobs: int = 100

    def __post_init__(self):
        if isinstance(self.data_store, dict):
            self.data_store = munchify(self.data_store)
        if isinstance(self.event_broker, dict):
            self.event_broker = munchify(self.event_broker)


@dataclass
class ProjectTrackerConfig(BaseConfig):
    username: str | None = None
    api_url: str = "http://localhost:8241"
    ui_url: str = "http://localhost:8242"
    api_key: str | None = None


@dataclass
class ProjectConfig(BaseConfig):
    scheduler: ProjectSchedulerConfig = field(default_factory=ProjectSchedulerConfig)
    tracker: ProjectTrackerConfig = field(default_factory=ProjectTrackerConfig)

    def __post_init__(self):
        self.scheduler = ProjectSchedulerConfig(
            **self.scheduler
            if isinstance(self.scheduler, dict | Munch)
            else self.scheduler.to_dict()
        )
        self.tracker = ProjectTrackerConfig(
            **self.tracker
            if isinstance(self.tracker, dict | Munch)
            else self.tracker.to_dict()
        )


@dataclass
class Config(BaseConfig):
    base_dir: str | None = None
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    project: ProjectConfig = field(default_factory=ProjectConfig)

    def __post_init__(self):
        self.pipeline = PipelineConfig(
            **self.pipeline
            if isinstance(self.pipeline, dict | Munch)
            else self.pipeline.to_dict()
        )
        self.project = ProjectConfig(
            **self.project
            if isinstance(self.project, dict | Munch)
            else self.project.to_dict()
        )

    @classmethod
    def load(cls, base_dir: str, pipeline_name: str | None = None):
        if os.path.exists(os.path.join(base_dir, "conf/project.yml")):
            project = ProjectConfig.from_yaml(
                path=os.path.join(base_dir, "conf/project.yml")
            )
        else:
            project = ProjectConfig()

        if pipeline_name is not None:
            if os.path.exists(
                os.path.join(base_dir, "conf", f"pipelines/{pipeline_name}.yml")
            ):
                pipeline = PipelineConfig.from_yaml(
                    name=pipeline_name,
                    path=os.path.join(
                        base_dir, "conf", f"pipelines/{pipeline_name}.yml"
                    ),
                )
            else:
                pipeline = PipelineConfig(name=pipeline_name)
        else:
            pipeline = PipelineConfig(name=pipeline_name)

        return cls(base_dir=base_dir, pipeline=pipeline, project=project)

    def save(self):
        if not os.path.exists(os.path.join(self.base_dir, "conf")):
            os.makedirs(os.path.join(self.base_dir, "conf"))

        if self.pipeline.name is not None:
            self.pipeline.to_yaml(
                os.path.join(self.base_dir, f"conf/pipelines/{self.pipeline.name}.yml")
            )
        self.project.to_yaml(os.path.join(self.base_dir, "conf/project.yml"))


def load(base_dir: str, pipeline_name: str | None = None):
    return Config.load(base_dir, pipeline_name)


def save(config: Config):
    config.save()
