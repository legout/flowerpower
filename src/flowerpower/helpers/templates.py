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
# ## cleanup interval configuration
#
# cleanup_interval:
#   unit: minutes
#   value: 15
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
from flowerpower.cfg import Config
from pathlib import Path

PARAMS = Config(Path(__file__).parents[1]).pipeline_params.{name}
"""
