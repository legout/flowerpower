from pathlib import Path

import yaml
from hamilton.function_modifiers import value, source

from loguru import logger
from munch import Munch, munchify, unmunchify
from .constants import PIPELINE_TEMPLATE, SCHEDULER_TEMPLATE, TRACKER_TEMPLATE  # noqa: F401


class Config:
    def __init__(self, path: str = "conf") -> None:
        self._path = path
        self._check_conf_path()
        self._set_cfg_filenames()

        self._pipeline = None
        self._pipeline_params = None
        self._tracker = None
        self._scheduler = None

    def _check_conf_path(self) -> bool:
        """
        Check if the configuration path exists.

        Args:
            None

        Returns:
            bool: True if the path exists, False otherwise.
        """
        if not Path(self._path).exists():
            logger.warning(f"conif path {self._path} does not exist.")

    def _set_cfg_filenames(self):
        """
        Sets the filenames for the configuration files.

        This method sets the filenames for the pipeline, tracker, and scheduler configuration files.
        It uses the rglob method to find the files with the specified patterns in the given path.
        The filenames are stored in the respective instance variables.

        Note: This method assumes that there is at least one file matching each pattern in the given path.

        Returns:
            None
        """
        self._pipeline_path = list((Path(self._path)).rglob("pipeline*.y*ml"))
        self._pipeline_path = self._pipeline_path[0] if self._pipeline_path else None

        self._tracker_path = list((Path(self._path)).rglob("tracker*.y*ml"))
        self._tracker_path = self._tracker_path[0] if self._tracker_path else None

        self._scheduler_path = list((Path(self._path)).rglob("scheduler*.y*ml"))
        self._scheduler_path = self._scheduler_path[0] if self._scheduler_path else None

    @staticmethod
    def _load(path: str) -> dict:
        """
        Load the configuration parameters from a YAML file.

        Args:
            path (str): The path to the YAML file.

        Returns:
            dict: The loaded configuration parameters.
        """
        with open(path) as f:
            params = yaml.full_load(f)

        return params

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
            if self._pipeline is None:
                self._pipeline = munchify(cfg)
            else:
                self._pipeline.update(cfg)
        if name == "tracker":
            if self._tracker is None:
                self._tracker = munchify(cfg)
            else:
                self._tracker.update(cfg)
        if name == "scheduler":
            if self._scheduler is None:
                self._scheduler = munchify(cfg)
            else:
                self._scheduler.update(cfg)

    def _write(self, name: str) -> None:
        """
        Write the configuration to a YAML file.

        Args:
            cfg (dict | Munch): The configuration to be written.
            name (str): The name of the file.

        Returns:
            None
        """
        cfg = eval(f"self._{name}")
        with open(f"{self._path}/{name}.yml", "w") as f:
            f.write(
                eval(f"{name.upper()}_TEMPLATE")
                + yaml.dump(unmunchify(cfg), sort_keys=False)
                .replace("null", "")
                .replace("{}", "")
            )

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
            name = "pipeline"
            self._write(name)
        if tracker:
            name = "tracker"
            self._write(name)
        if scheduler:
            name = "scheduler"
            self._write(name)

    @staticmethod
    def _to_ht_params(d: dict, parent_dict: dict | None = None):
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

    @staticmethod
    def _to_ht_parameterization(d: dict) -> dict:
        """
        Convert a dictionary into a parameterization dictionary.

        Args:
            d (dict): The input dictionary.

        Returns:
            dict: The parameterization dictionary.

        """
        return {k: {k: d[k]} for k in d}

    def load_pipeline(self) -> Munch:
        """
        Loads the pipeline configuration from a YAML file and returns it as a Munch object.

        Returns:
            Munch: The loaded pipeline configuration.

        Raises:
            FileNotFoundError: If no YAML file with the name 'pipeline.yml' is found.
        """

        if not self._pipeline_path:
            logger.error("No YAML file found with name 'pipeline.yml'")
            return

        self._pipeline = munchify(self._load(self._pipeline_path))

        self._pipeline_params = self._pipeline.params.copy()

        for node in self._pipeline_params:
            self._pipeline_params[node].update(
                {
                    k: self._to_ht_params(v)
                    for k, v in self._pipeline_params[node].items()
                    if v is not None
                }
            )
        self._pipeline_params.update(
            {
                k: self._to_ht_parameterization(v)
                for k, v in self._pipeline_params.items()
                if v is not None
            }
        )
        self._pipeline_params = munchify(self._pipeline_params)

    def load_scheduler(self) -> Munch:
        """
        Loads the scheduler configuration from a YAML file.

        Returns:
            A Munch object representing the loaded scheduler configuration.

        Raises:
            FileNotFoundError: If no YAML file with the name 'scheduler.yml' is found.
        """

        if not self._pipeline_path:
            logger.error("No YAML file found with name 'scheduler'")
            return

        self._scheduler = munchify(self._load(self._scheduler_path))

    def load_tracker(self) -> Munch:
        """
        Loads the tracker from a YAML file.

        Returns:
            Munch: The loaded tracker object.
        """
        if not self._tracker_path:
            logger.error("No YAML file found with name 'tracker'")
            return

        self._tracker = munchify(self._load(self._tracker_path))

    @property
    def pipeline(self):
        if self._pipeline is None:
            self.load_pipeline()
        return self._pipeline

    @property
    def scheduler(self):
        if self._scheduler is None:
            self.load_scheduler()
        return self._scheduler

    @property
    def tracker(self):
        if self._tracker is None:
            self.load_tracker()
        return self._tracker

    @property
    def pipeline_params(self):
        if self._pipeline is None:
            self.load_pipeline()
        return self._pipeline_params
