from pathlib import Path

import yaml
from hamilton.function_modifiers import value, source

from loguru import logger
from munch import Munch, munchify, unmunchify


def _load(path: str) -> dict:
    """
    Load configuration parameters from a YAML file.

    Args:
        path (str): The path to the YAML file. If not provided, the function will
            search for the file in the current working directory and its subdirectories.

    Returns:
        dict: A dictionary containing the loaded configuration parameters.

    Raises:
        FileNotFoundError: If the specified YAML file is not found.

    """
    # if path is None:
    #     path = list((Path.cwd() / "conf").rglob(f"{name}*.y*ml"))

    #     if not len(path):
    #         # logger.error(f"No YAML file found with name '{name}'")
    #         return

    #     path = path[0]

    with open(path) as f:
        params = yaml.full_load(f)

    return params


def write(cfg: dict | Munch, name: str, path: str | None = None) -> None:
    """
    Writes the given configuration to a YAML file.

    Args:
        cfg (dict|Munch): The configuration to be written. It can be a dictionary or a Munch object.
        name (str): The name of the YAML file to be created.
        path (str|None, optional): The path to the directory where the YAML file will be created. If None,
        the current working directory will be used.

    Returns:
        None

    Raises:
        None

    This function opens a file with the specified name and path in write mode. It then writes the
    configuration to the file in YAML format. The configuration is first converted to a
    dictionary using the `unmunchify` function, and then converted to a string using the `yaml.dump`
    function. The resulting string is then concatenated with the value of the variable `name.upper() + "_TEMPLATE"`.
    The resulting string is then written to the file.

    Example:
        >>> cfg = {"key": "value"}
        >>> write(cfg, "config", "/path/to/directory")
        This will create a YAML file named "config.yml" in the specified directory with the following content:
        CONFIG_TEMPLATE
        key: value
    """
    with open(f"{path}/{name}.yml", "w") as f:
        f.write(
            eval(f"{name.upper()}_TEMPLATE")
            + yaml.dump(unmunchify(cfg), sort_keys=False)
            .replace("null", "")
            .replace("{}", "")
        )


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
        if isinstance(v, dict):
            _to_ht_params(v, parent_dict)
        else:
            if isinstance(v, str):
                if v in parent_dict:
                    d[k] = source(v)
                else:
                    d[k] = value(v)
            else:
                d[k] = value(v)
    return d


# def _to_ht_value(value_dict: dict) -> dict:
#     """
#     Recursively converts a dictionary to a dictionary of value objects.

#     Args:
#         value_dict (dict): The dictionary to be converted.

#     Returns:
#         dict: The converted dictionary with value objects.

#     """
#     if isinstance(value_dict, dict):
#         return {k: _to_ht_value(v) for k, v in value_dict.items()}
#     else:
#         return value(value_dict)


def _to_ht_parameterization(d: dict) -> dict:
    """
    Convert a dictionary into a parameterization dictionary.

    Args:
        d (dict): The input dictionary.

    Returns:
        dict: The parameterization dictionary.

    """
    return {k: {k: d[k]} for k in d}


def load_pipeline_cfg(path: str = "conf", to_ht: bool = False) -> Munch:
    """
    Load pipeline parameters from a YAML file.

    Args:
        path (str): The path to the YAML file. If None, it will search for a file named "pipeline*.y*ml"
            in the current working directory.
        ht_values (bool): Whether to convert the loaded parameters to "ht_value" format.

    Returns:
        Munch: A Munch object containing the loaded pipeline parameters.
    """
    if (
        "pipeline.yml" not in path
        or "pipeline.yaml" not in path
        or "pipelines.yml" not in path
        or "pipelines.yaml" not in path
    ):
        path = list((Path(path)).rglob("pipeline*.y*ml"))
        if not len(path):
            logger.error("No YAML file found with name 'pipeline'")
            return
        path = path[0]

    cfg = _load(path)

    if to_ht:
        # cfg = _to_ht_value(cfg)
        cfg["params"].update(
            {
                k: _to_ht_parameterization(_to_ht_params(v))
                for k, v in cfg["params"].items()
                if v is not None
            }
        )

    return munchify(cfg)


def load_scheduler_cfg(path: str = "conf") -> Munch:
    """
    Load scheduler parameters from a YAML file.

    Args:
        path (str): The path to the YAML file. If None, it will search for a file named "scheduler*.y*ml"
            in the current working directory.

    Returns:
        Munch: A Munch object containing the loaded scheduler parameters.
    """
    if (
        "scheduler.yml" not in path
        or "scheduler.yaml" not in path
        or "schedulers.yml" not in path
        or "schedulers.yaml" not in path
    ):
        path = list((Path(path)).rglob("scheduler*.y*ml"))
        if not len(path):
            logger.error("No YAML file found with name 'scheduler'")
            return
        path = path[0]

    cfg = _load(path)

    return munchify(cfg)


def load_tracker_cfg(path: str = "conf") -> Munch:
    """
    Load tracker config from a YAML file.

    Args:
        path (str): The path to the YAML file. If None, it will search for a file named "tracker*.y*ml"
            in the current working directory.

    Returns:
        Munch: A Munch object containing the loaded tracker parameters.
    """
    if (
        "tracker.yml" not in path
        or "tracker.yaml" not in path
        or "trackers.yml" not in path
        or "trackers.yaml" not in path
    ):
        path = list((Path(path)).rglob("tracker*.y*ml"))
        if not len(path):
            logger.error("No YAML file found with name 'tracker'")
            return
        path = path[0]

    cfg = _load(path)

    return munchify(cfg)


PIPELINE_TEMPLATE = """# ---------------- Pipelines Configuration ----------------- #

# ------------------------ Example ------------------------- #
#
# path: pipelines
#
# ## pipeline parameter
#
# params:
#   flow1:                      ## pipeline name
#       step1:                  ## step name
#         param1_1: 123         ## step parameters
#         param1_2: abc
#       step2:
#         param2_1: true
#
# ## run configuration
#
# run:
#   prod: # environment name
#     flow1:
#       inputs:                 ## input parameters
#       final_vars: [step2]     ## final output vars
#       with_tracker: true      ## whether to track the run
#
#   dev:
#     flow1:
#       inputs:
#       final_vars: [step2]
#       with_tracker: false
#
# ---------------------------------------------------------- #

"""

SCHEDULER_TEMPLATE = """# ---------------- Scheduler Configuration ----------------- #

# ------------------------ Example ------------------------- #
#
# ##  data store configuration
#
# ### postgres
# data_store:
#   type: sqlalchemy
#   url: postgresql+asyncpg://edge:edge@postgres/flowerpower
#
# ### sqlite
# data_store:
#   type: sqlalchemy
#   url: sqlite+aiosqlite:///flowerpower.db
#
# ### memory
# data_store:
#   type: memory
#
# ### mongodb
# data_store:
#   type: mongodb
#   url: mongodb://localhost:27017/scheduler
#
# ## event broker configuration
#
# ### postgres
# event_broker:
#   type: asyncpg
#   url: postgresql+asyncpg://edge:edge@postgres/flowerpower
#
# ### mqtt
# event_broker:
#   type: mqtt
#   host: localhost
#   port: 1883
#   username: edge
#   password: edge

# ### redis
# event_broker:
#   type: redis
#   host: localhost
#   port: 6379

# ### local
# event_broker:
#   type: local # or memory
#
# ## pipeline schedule configuration
#
# pipeline:
#   my_flow:
#     type: cron                ## options: interval, calendarinterval, date
#     start_time:
#     end_time:
#     ## optional cron arguments
#     crontab: * * * * *
#     year:
#     month:
#     week:
#     day:
#     days_of_week:
#     hour:
#     minute:
#     second:
#     timezone:
#     ## optional interval arguments
#     weeks:
#     days:
#     hours:
#     minutes:
#     seconds:
#     microseconds:
#
# ---------------------------------------------------------- #

"""

TRACKER_TEMPLATE = """# ----------------- Tracker Configuration ------------------ #

# ------------------------ Example ------------------------- #
#
# username: your.email@example.com
# api_url: http://localhost:8241
# ui_url: http://localhost:8242
# api_key:

# pipeline:
#   my_flow:
#     project_id: 1
#     tags:
#       environment: dev
#       version: 1.0
#       TODO: add_more_tags_to_find_your_run_later
#     dag_name: my_flow_123
#
# ---------------------------------------------------------- #

"""

PIPELINE_PY_TEMPLATE = """# FlowerPower pipeline {name}.py
# Created on {date}


from hamilton.function_modifiers import parameterize
from flowerpower.cfg import load_pipeline_cfg
from pathlib import Path

PARAMS = load_pipeline_cfg(
    path=str(Path(__file__).parent / "conf"), to_ht=True
).params.{name}
"""
# PIPELINE = load_pipeline_cfg()
# SCHEDULER = load_scheduler_cfg()
# TRACKER = load_tracker_cfg()
