import yaml
from munch import Munch, munchify, unmunchify
from pathlib import Path
from hamilton.function_modifiers import value
from loguru import logger

def _load(name:str, path:str|None=None) -> dict:
    """
    Load configuration parameters from a YAML file.

    Args:
        name (str): The name of the YAML file to load.
        path (str|None, optional): The path to the YAML file. If not provided, the function will 
            search for the file in the current working directory and its subdirectories.

    Returns:
        dict: A dictionary containing the loaded configuration parameters.

    Raises:
        FileNotFoundError: If the specified YAML file is not found.

    """
    if path is None:
        path = list(Path.cwd().rglob(f"{name}*.y*ml"))
        
        if not len(path):
            logger.error(f"No YAML file found with name '{name}'")
            return

        path = path[0]

    with open(path) as f:
        params = yaml.full_load(f)

    return params

def write(cfg:dict|Munch, name:str, path:str|None=None) -> None:
     
     with open(f"{path}/{name}.yml", "w") as f:
        f.write(
            eval(f"{name.upper()}_TEMPLATE")
             + yaml.dump(unmunchify(cfg), sort_keys=False).replace("null", "")
        )


def _to_ht_value(value_dict: dict) -> dict:
    """
    Recursively converts a dictionary to a dictionary of value objects.

    Args:
        value_dict (dict): The dictionary to be converted.

    Returns:
        dict: The converted dictionary with value objects.

    """
    if isinstance(value_dict, dict):
        return {k: _to_ht_value(v) for k, v in value_dict.items()}
    else:
        return value(value_dict)

def load_pipeline_cfg(path: str | None = None, ht_values: bool = False) -> Munch:
    """
    Load pipeline parameters from a YAML file.

    Args:
        path (str | None): The path to the YAML file. If None, it will search for a file named "pipeline*.y*ml" 
            in the current working directory.
        ht_values (bool): Whether to convert the loaded parameters to "ht_value" format.

    Returns:
        Munch: A Munch object containing the loaded pipeline parameters.
    """

    params = _load("pipeline",path)

    if ht_values:
        params = _to_ht_value(params)

    return munchify(params)

def load_scheduler_cfg(path: str | None = None) -> Munch:
    """
    Load scheduler parameters from a YAML file.

    Args:
        path (str | None): The path to the YAML file. If None, it will search for a file named "scheduler*.y*ml" 
            in the current working directory.
      
    Returns:
        Munch: A Munch object containing the loaded scheduler parameters.
    """

    params = _load("scheduler",path)

    return munchify(params)

def load_tracker_cfg(path: str | None = None) -> Munch:
    """
    Load tracker config from a YAML file.

    Args:
        path (str | None): The path to the YAML file. If None, it will search for a file named "tracker*.y*ml" 
            in the current working directory.
      
    Returns:
        Munch: A Munch object containing the loaded tracker parameters.
    """

    params = _load("tracker",path)

    return munchify(params)



PIPELINE_TEMPLATE = """
# ---------------- Pipelines Configuration ----------------- #

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

SCHEDULER_TEMPLATE = """
# ---------------- Scheduler Configuration ----------------- #

# ------------------------ Example ------------------------- #
#
# ##  data store configuration
#
# ### postgres
# data_store:
#   type: sqlalchemy
#   url: "postgresql+asyncpg://edge:edge@db/flowerpower"
# 
# ### sqlite 
# data_store:
#   type: sqlalchemy
#   url: "sqlite+aiosqlite:///flowerpower.db"
#
# ### memory
# data_store:
#   type: memory
#
# ### mongodb
# data_store:
#   type: mongodb
#   url: "mongodb://localhost:27017/scheduler"
#
# ## event broker configuration
#
# ### postgres
# event_broker:
#   type: asyncpg
#   url: "postgresql+asyncpg://edge:edge@db/flowerpower"
#
# ### mqtt
# event_broker:
#   type: mqtt
#   host: localhost
#   port: 1883
#   username: "edge"
#   password: "edge"

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

TRACKER_TEMPLATE = """
# ----------------- Tracker Configuration ------------------ #

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
PIPELINE = load_pipeline_cfg()
SCHEDULER = load_scheduler_cfg()
TRACKER = load_tracker_cfg()
