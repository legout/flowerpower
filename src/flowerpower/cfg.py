import os
from pathlib import Path

import yaml
from hamilton.function_modifiers import source, value
from munch import Munch, munchify, unmunchify

from .helpers.templates import (
    PIPELINE_TEMPLATE,  # noqa: F401
    SCHEDULER_TEMPLATE,  # noqa: F401
    TRACKER_TEMPLATE,  # noqa: F401
)


class BaseConfig:
    def __init__(self, name: str, base_dir: str | None = None) -> None:
        self._base_dir = base_dir or ""
        self._base_dir = str(self._base_dir).rstrip("/")
        if self._base_dir.endswith("conf"):
            self._base_dir = self._base_dir.rstrip("conf").rstrip("/")
        self.name = name
        self._path = os.path.join(self._base_dir, "conf", self.name + ".yml")

    def load(self):
        """
        Load the configuration parameters from a YAML file.

        Args:
            path (str): The path to the YAML file.

        Returns:
            dict: The loaded configuration parameters.
        """
        if Path(self._path).exists():
            with open(self._path) as f:
                self._cfg = munchify(yaml.full_load(f))
        else:
            self._cfg = None

    def write(self) -> None:
        """
        Write the configuration to a YAML file.

        Args:
            cfg (dict | Munch): The configuration to be written.
            name (str): The name of the file.

        Returns:
            None
        """

        with open(self._path, "w") as f:
            f.write(
                eval(f"{self.name.upper()}_TEMPLATE")
                + yaml.dump(unmunchify(self._cfg), sort_keys=False)
                .replace("null", "")
                .replace("{}", "")
            )

    def update(self, cfg: dict | Munch) -> None:
        """
        Update the configuration with the given parameters.

        Args:
            cfg (dict | Munch): The parameters to update the configuration with.
            name (str): The name of the configuration.

        Returns:
            None
        """
        if self._cfg is None:
            self._cfg = munchify(cfg)
        else:
            self._cfg.update(cfg)
        # self._write()


class TrackerConfig(BaseConfig):
    name = "tracker"
    init_cfg = {
        "username": None,
        "api_url": "http://localhost:8241",
        "ui_url": "http://localhost:8242",
        "api_key": None,
        "pipeline": {},
    }

    def __init__(self, base_dir: str | None = None) -> None:
        super().__init__(self.name, base_dir)

        self.load()
        self._cfg = self._cfg or munchify(self.init_cfg)


class SchedulerConfig(BaseConfig):
    name = "scheduler"
    init_cfg = {
        "data_store": {"type": "memory"},
        "event_broker": {"type": "local"},
        "cleanup_interval": {"unit": "minutes", "value": 15},
        "pipeline": {},
    }

    def __init__(self, base_dir: str | None = None) -> None:
        super().__init__(self.name, base_dir)

        self.load()
        self._cfg = self._cfg or munchify(self.init_cfg)


class PipelineConfig(BaseConfig):
    name = "pipeline"
    init_cfg = {
        "run": {},
        # {
        #    "dev": {"inputs": None, "final_vars": None, "with_tracker": False},
        #    "prod": {"inputs": None, "final_vars": None, "with_tracker": True},
        # },
        "params": {},
    }

    def __init__(self, base_dir: str | None = None) -> None:
        super().__init__(self.name, base_dir)

        self.load()
        self._cfg = self._cfg or munchify(self.init_cfg)

    def _to_ht_params(self, d: dict, parent_dict: dict | None = None):
        """
        Recursively converts the values in a dictionary to `source` or `value` objects.

        Args:
            d (dict): The dictionary to convert.
            parent_dict (dict | None): The parent dictionary. Defaults to None.

        Returns:
            dict: The converted dictionary.
        """

        if parent_dict is None:
            parent_dict = d

        for k, v in d.items():
            if isinstance(v, str):
                if v in parent_dict:
                    d[k] = source(v)
                else:
                    d[k] = value(v)
            else:
                d[k] = value(v)
        return d

    def _to_ht_parameterization(self, d: dict) -> dict:
        """
        Convert a dictionary into a parameterization dictionary.

        Args:
            d (dict): The input dictionary.

        Returns:
            dict: The parameterization dictionary.

        """
        return {k: {k: d[k]} for k in d}

    def load(self):
        """
        Load the configuration parameters.

        This method loads the configuration parameters from the specified file path.
        It updates the parameters dictionary with the loaded values and converts
        certain values to a specific format using the `_to_ht_params` and
        `_to_ht_parameterization` methods.

        Returns:
            None
        """
        ...
        super().load()
        if self._cfg is None:
            return

        self._params = self._cfg.params.copy() if self._cfg.params is not None else {}

        for node in self._params:
            if self._params[node] is None:
                continue
            self._params[node].update(
                {
                    k: self._to_ht_params(v)
                    for k, v in self._params[node].items()
                    if v is not None
                }
            )
        self._params.update(
            {
                k: self._to_ht_parameterization(v)
                for k, v in self._params.items()
                if v is not None
            }
        )
        self._params = munchify(self._params)


class Config:
    def __init__(self, base_dir: str | None = None) -> None:
        self._tracker = TrackerConfig(base_dir)
        self._scheduler = SchedulerConfig(base_dir)
        self._pipeline = PipelineConfig(base_dir)

    def update(
        self,
        cfg: dict | Munch,
        name: str,
    ) -> None:
        """
        Update the configuration with the given parameters.

        Args:
            cfg (dict | Munch): The parameters to update the configuration with.
            name (str): The name of the configuration.

        Returns:
            None
        """
        if name == "pipeline":
            self._pipeline.update(cfg)
        if name == "tracker":
            self._tracker.update(cfg)
        if name == "scheduler":
            self._scheduler.update(cfg)

    def write(
        self, pipeline: bool = False, tracker: bool = False, scheduler: bool = False
    ) -> None:
        """
        Write the configuration to file.

        Args:
            pipeline (bool): If True, write the pipeline configuration to file.
            tracker (bool): If True, write the tracker configuration to file.
            scheduler (bool): If True, write the scheduler configuration to file.

        Returns:
            None
        """
        if pipeline:
            self._pipeline.write()
        if tracker:
            self._tracker.write()
        if scheduler:
            self._scheduler.write()

    @property
    def pipeline(self):
        return self._pipeline._cfg

    @property
    def scheduler(self):
        return self._scheduler._cfg

    @property
    def tracker(self):
        return self._tracker._cfg

    @property
    def pipeline_params(self):
        return self._pipeline._params
