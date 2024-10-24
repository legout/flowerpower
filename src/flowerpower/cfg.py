import datetime as dt
import os
from dataclasses import asdict, dataclass, field

import yaml
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

    def __post_init__(self):
        if isinstance(self.inputs, dict):
            self.inputs = munchify(self.inputs)


@dataclass
class PipelineScheduleConfig(BaseConfig):
    type_: str | None = None
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
        if isinstance(self.func, dict):
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


@dataclass
class ProjectSchedulerConfig(BaseConfig):
    data_store: dict | Munch = field(default_factory=dict)
    event_broker: dict | Munch = field(default_factory=dict)

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
                print(pipeline_name)
                pipeline = PipelineConfig.from_yaml(
                    name=pipeline_name,
                    path=os.path.join(
                        base_dir, "conf", f"pipelines/{pipeline_name}.yml"
                    ),
                )
                print(pipeline)
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


# import os
# from pathlib import Path

# import yaml
# from hamilton.function_modifiers import source, value
# from munch import Munch, munchify, unmunchify

# from .helpers.templates import (
#     PIPELINE_TEMPLATE,  # noqa: F401
#     SCHEDULER_TEMPLATE,  # noqa: F401
#     TRACKER_TEMPLATE,  # noqa: F401
# )


# class BaseConfig:
#     def __init__(self, name: str, base_dir: str | None = None) -> None:
#         self._base_dir = base_dir or ""
#         self._base_dir = str(self._base_dir).rstrip("/")
#         if self._base_dir.endswith("conf"):
#             self._base_dir = self._base_dir.rstrip("conf").rstrip("/")
#         self.name = name
#         self._path = os.path.join(self._base_dir, "conf", self.name + ".yml")

#     def load(self):
#         """
#         Load the configuration parameters from a YAML file.

#         Args:
#             path (str): The path to the YAML file.

#         Returns:
#             dict: The loaded configuration parameters.
#         """
#         if Path(self._path).exists():
#             with open(self._path) as f:
#                 self._cfg = munchify(yaml.full_load(f))
#         else:
#             self._cfg = None

#     def write(self) -> None:
#         """
#         Write the configuration to a YAML file.

#         Args:
#             cfg (dict | Munch): The configuration to be written.
#             name (str): The name of the file.

#         Returns:
#             None
#         """

#         with open(self._path, "w") as f:
#             f.write(
#                 eval(f"{self.name.upper()}_TEMPLATE")
#                 + yaml.dump(unmunchify(self._cfg), sort_keys=False)
#                 .replace("null", "")
#                 .replace("{}", "")
#             )

#     def update(self, cfg: dict | Munch) -> None:
#         """
#         Update the configuration with the given parameters.

#         Args:
#             cfg (dict | Munch): The parameters to update the configuration with.
#             name (str): The name of the configuration.

#         Returns:
#             None
#         """
#         if self._cfg is None:
#             self._cfg = munchify(cfg)
#         else:
#             self._cfg.update(cfg)
#         # self._write()


# class TrackerConfig(BaseConfig):
#     name = "tracker"
#     init_cfg = {
#         "username": None,
#         "api_url": "http://localhost:8241",
#         "ui_url": "http://localhost:8242",
#         "api_key": None,
#         "pipeline": {},
#     }

#     def __init__(self, base_dir: str | None = None) -> None:
#         super().__init__(self.name, base_dir)

#         self.load()
#         self._cfg = self._cfg or munchify(self.init_cfg)


# class SchedulerConfig(BaseConfig):
#     name = "scheduler"
#     init_cfg = {
#         "data_store": {"type": "memory"},
#         "event_broker": {"type": "local"},
#         "cleanup_interval": {"unit": "minutes", "value": 15},
#         "pipeline": {},
#     }

#     def __init__(self, base_dir: str | None = None) -> None:
#         super().__init__(self.name, base_dir)

#         self.load()
#         self._cfg = self._cfg or munchify(self.init_cfg)


# class PipelineConfig(BaseConfig):
#     name = "pipeline"
#     init_cfg = {
#         "run": {},
#         # {
#         #    "dev": {"inputs": None, "final_vars": None, "with_tracker": False},
#         #    "prod": {"inputs": None, "final_vars": None, "with_tracker": True},
#         # },
#         "params": {},
#     }

#     def __init__(self, base_dir: str | None = None) -> None:
#         super().__init__(self.name, base_dir)

#         self.load()
#         self._cfg = self._cfg or munchify(self.init_cfg)

#     def _to_ht_params(self, d: dict, parent_dict: dict | None = None):
#         """
#         Recursively converts the values in a dictionary to `source` or `value` objects.

#         Args:
#             d (dict): The dictionary to convert.
#             parent_dict (dict | None): The parent dictionary. Defaults to None.

#         Returns:
#             dict: The converted dictionary.
#         """

#         if parent_dict is None:
#             parent_dict = d

#         for k, v in d.items():
#             if isinstance(v, str):
#                 if v in parent_dict:
#                     d[k] = source(v)
#                 else:
#                     d[k] = value(v)
#             else:
#                 d[k] = value(v)
#         return d

#     def _to_ht_parameterization(self, d: dict) -> dict:
#         """
#         Convert a dictionary into a parameterization dictionary.

#         Args:
#             d (dict): The input dictionary.

#         Returns:
#             dict: The parameterization dictionary.

#         """
#         return {k: {k: d[k]} for k in d}

#     def load(self):
#         """
#         Load the configuration parameters.

#         This method loads the configuration parameters from the specified file path.
#         It updates the parameters dictionary with the loaded values and converts
#         certain values to a specific format using the `_to_ht_params` and
#         `_to_ht_parameterization` methods.

#         Returns:
#             None
#         """
#         ...
#         super().load()
#         if self._cfg is None:
#             return

#         self._params = self._cfg.params.copy() if self._cfg.params is not None else {}

#         for node in self._params:
#             if self._params[node] is None:
#                 continue
#             self._params[node].update(
#                 {
#                     k: self._to_ht_params(v)
#                     for k, v in self._params[node].items()
#                     if v is not None
#                 }
#             )
#         self._params.update(
#             {
#                 k: self._to_ht_parameterization(v)
#                 for k, v in self._params.items()
#                 if v is not None
#             }
#         )
#         self._params = munchify(self._params)


# class Config:
#     def __init__(self, base_dir: str | None = None) -> None:
#         self._tracker = TrackerConfig(base_dir)
#         self._scheduler = SchedulerConfig(base_dir)
#         self._pipeline = PipelineConfig(base_dir)

#     def update(
#         self,
#         cfg: dict | Munch,
#         name: str,
#     ) -> None:
#         """
#         Update the configuration with the given parameters.

#         Args:
#             cfg (dict | Munch): The parameters to update the configuration with.
#             name (str): The name of the configuration.

#         Returns:
#             None
#         """
#         if name == "pipeline":
#             self._pipeline.update(cfg)
#         if name == "tracker":
#             self._tracker.update(cfg)
#         if name == "scheduler":
#             self._scheduler.update(cfg)

#     def write(
#         self, pipeline: bool = False, tracker: bool = False, scheduler: bool = False
#     ) -> None:
#         """
#         Write the configuration to file.

#         Args:
#             pipeline (bool): If True, write the pipeline configuration to file.
#             tracker (bool): If True, write the tracker configuration to file.
#             scheduler (bool): If True, write the scheduler configuration to file.

#         Returns:
#             None
#         """
#         if pipeline:
#             self._pipeline.write()
#         if tracker:
#             self._tracker.write()
#         if scheduler:
#             self._scheduler.write()

#     @property
#     def pipeline(self):
#         return self._pipeline._cfg

#     @property
#     def scheduler(self):
#         return self._scheduler._cfg

#     @property
#     def tracker(self):
#         return self._tracker._cfg

#     @property
#     def pipeline_params(self):
#         return self._pipeline._params
