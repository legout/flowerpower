# import typer
import datetime as dt
# from .pipelines import *
import importlib
import os
import sys


import yaml
from hamilton import driver
from hamilton_sdk import adapters
from loguru import logger
from munch import munchify

from .cfg import PIPELINE, SCHEDULER, TRACKER, write
# from hamilton.execution import executors
from .scheduler import get_scheduler


def run(
    pipeline: str,
    environment: str = "prod",
    **kwargs,
) -> None:
    pipeline_path, pipeline_name = pipeline.rsplit(".", maxsplit=1)
    pipeline_path = pipeline_path.replace(".", "/")

    logger.info(f"Starting pipeline {pipeline_name} in environment {environment}")

    sys.path.append(pipeline_path)
    module = importlib.import_module(pipeline_name)

    RUN_PARAMS = getattr(PIPELINE.run, environment)[pipeline_name]
    TRACKER_PARAMS = TRACKER.pipeline[pipeline_name]

    with_tracker = kwargs.pop("with_tracker", False) or RUN_PARAMS.get(
        "with_tracker", False
    )
    if with_tracker:
        project_id = kwargs.pop("project_id", None) or TRACKER_PARAMS.get(
            "project_id", None
        )
        username = kwargs.pop("username", None) or TRACKER_PARAMS.get("username", None)
        dag_name = kwargs.pop("dag_name", None) or TRACKER_PARAMS.get("dag_name", None)
        tags = kwargs.pop("tags", None) or TRACKER_PARAMS.get("tags", None)
        hamilton_api_url = kwargs.pop("api_url", None) or TRACKER_PARAMS.get(
            "api_url", None
        )
        hamilton_ui_url = kwargs.pop("ui_url", None) or TRACKER_PARAMS.get(
            "ui_url", None
        )

        if project_id is None:
            raise ValueError(
                "Please provide a project_id if you want to use the tracker"
            )

        tracker = adapters.HamiltonTracker(
            project_id=project_id,
            **kwargs,
            username=username,
            dag_name=dag_name,
            tags=tags,
            api_url=hamilton_api_url,
            ui_url=hamilton_ui_url,
        )

        dr = (
            driver.Builder()
            .with_modules(module)
            .enable_dynamic_execution(allow_experimental_mode=True)
            .with_adapters(tracker)
            .build()
        )
    else:
        dr = (
            driver.Builder()
            .with_modules(module)
            .enable_dynamic_execution(allow_experimental_mode=True)
            .build()
        )

    final_vars = kwargs.pop("final_vars", []) or RUN_PARAMS.get("final_vars", [])
    inputs = kwargs.pop("inputs", {}) or RUN_PARAMS.get("inputs", {})

    _ = dr.execute(final_vars=final_vars, inputs=inputs)

    logger.success(f"Finished pipeline {pipeline}")


def schedule(
    pipeline: str,
    environment: str = "prod",
    type: str = "cron",
    **kwargs,
):
    SCHEDULER_PARAMS = SCHEDULER.pipeline[pipeline]

    start_time = kwargs.pop("start_time", None) or SCHEDULER_PARAMS.get(
        "start_time", None
    )
    end_time = kwargs.pop("end_time", None) or SCHEDULER_PARAMS.get("end_time", None)

    scheduler = get_scheduler()
    if type == "cron":
        crontab = kwargs.pop("crontab", None) or SCHEDULER_PARAMS.get("crontab", None)
        if crontab is not None:
            from apscheduler.triggers.cron import CronTrigger

            trigger = CronTrigger.from_crontab(crontab)
        else:
            from apscheduler.triggers.cron import CronTrigger

            year = kwargs.pop("year", None) or SCHEDULER_PARAMS.get("year", None)
            month = kwargs.pop("month", None) or SCHEDULER_PARAMS.get("month", None)
            week = kwargs.pop("week", None) or SCHEDULER_PARAMS.get("week", None)
            day = kwargs.pop("day", None) or SCHEDULER_PARAMS.get("day", None)
            days_of_week = kwargs.pop("days_of_week", None) or SCHEDULER_PARAMS.get(
                "days_of_week", None
            )
            hour = kwargs.pop("hour", None) or SCHEDULER_PARAMS.get("hour", None)
            minute = kwargs.pop("minute", None) or SCHEDULER_PARAMS.get("minute", None)
            second = kwargs.pop("second", None) or SCHEDULER_PARAMS.get("second", None)
            timezone = kwargs.pop("timezone", None) or SCHEDULER_PARAMS.get(
                "timezone", None
            )

            trigger = CronTrigger(
                year=year,
                month=month,
                week=week,
                day=day,
                day_of_week=days_of_week,
                hour=hour,
                minute=minute,
                second=second,
                start_time=start_time,
                end_time=end_time,
                timezone=timezone,
            )
    elif type == "interval":
        from apscheduler.triggers.interval import IntervalTrigger

        weeks = kwargs.pop("weeks", 0) or SCHEDULER_PARAMS.get("weeks", 0)
        days = kwargs.pop("days", 0) or SCHEDULER_PARAMS.get("days", 0)
        hours = kwargs.pop("hours", 0) or SCHEDULER_PARAMS.get("hours", 0)
        minutes = kwargs.pop("minutes", 0) or SCHEDULER_PARAMS.get("minutes", 0)
        seconds = kwargs.pop("seconds", 0) or SCHEDULER_PARAMS.get("seconds", 0)
        microseconds = kwargs.pop("microseconds", 0) or SCHEDULER_PARAMS.get(
            "microseconds", 0
        )

        trigger = IntervalTrigger(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
            start_time=start_time,
            end_time=end_time,
            # timezone=timezone,
        )
    elif type == "calendar":
        from apscheduler.triggers.calendarinterval import \
            CalendarIntervalTrigger

        weeks = kwargs.pop("weeks", 0) or SCHEDULER_PARAMS.get("weeks", 0)
        days = kwargs.pop("days", 0) or SCHEDULER_PARAMS.get("days", 0)
        hours = kwargs.pop("hours", 0) or SCHEDULER_PARAMS.get("hours", 0)
        minutes = kwargs.pop("minutes", 0) or SCHEDULER_PARAMS.get("minutes", 0)
        seconds = kwargs.pop("seconds", 0) or SCHEDULER_PARAMS.get("seconds", 0)
        microseconds = kwargs.pop("microseconds", 0) or SCHEDULER_PARAMS.get(
            "microseconds", 0
        )

        trigger = CalendarIntervalTrigger(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
        )
    elif type == "date":
        from apscheduler.triggers.date import DateTrigger

        trigger = DateTrigger(run_time=start_time)
    # logger.info(f"Add scheduler for {pipeline} in environment {environment}  with trigger {trigger}")
    id_ = scheduler.add_schedule(
        run,
        trigger=trigger,
        args=(pipeline, environment),
        kwargs=kwargs,
    )
    logger.success(
        f"Added scheduler for {pipeline} in environment {environment} with id {id_}"
    )


def new(
    name: str,
    pipelines_path: str = "pipelines",
    conf_path: str = "conf",
    overwrite: bool = False,
    **kwargs,
):
    logger.info(f"Creating new pipeline {name}")
    if not os.path.exists(conf_path):
        raise ValueError(
            f"Configuration path {conf_path} does not exist. Please run flowerpower init first."
        )
    if not os.path.exists(pipelines_path):
        raise ValueError(
            f"Pipeline path {pipelines_path} does not exist. Please run flowerpower init first."
        )

    # touch python module
    if os.path.exists(f"{pipelines_path}/{name}.py") and overwrite is False:
        raise ValueError(
            f"Pipeline {name} already exists. Use `overwrite=True` to overwrite."
        )

    os.makedirs(pipelines_path, exist_ok=True)
    with open(f"{pipelines_path}/{name}.py", "w") as f:
        f.write(
            f"""# FlowerPower pipeline {name}.py
            # Created at {dt.datetime.now()}"
            """
        )

    # pipeline configuration

    pipeline_cfg = PIPELINE or munchify(
        {"path": pipelines_path, "run": {}, "params": {}}
    )

    pipeline_run = kwargs.get("run", None)
    pipeline_params = kwargs.get("params", None)

    pipeline_cfg.params[name] = pipeline_params or None
    pipeline_cfg.run[name] = pipeline_run or munchify(
        {
            "dev": {"inputs": None, "final_vars": None, "with_tracker": False},
            "prod": {"inputs": None, "final_vars": None, "with_tracker": True},
        }
    )

    write(pipeline_cfg, "pipelines", conf_path)

    # scheduler configuration
    scheduler_cfg = SCHEDULER or munchify(
        {
            "data_path": {"type": "memory"},
            "event_broker": {"type": "local"},
            "pipeline": {},
        }
    )

    schedule_params = kwargs.get("schedule", None)
    scheduler_cfg.pipeline[name] = schedule_params or {"type": None}

    write(scheduler_cfg, "scheduler", conf_path)

    # tracker configuration
    tracker_cfg = TRACKER or munchify(
        {
            "username": None,
            "api_url": "http://localhost:8241",
            "ui_url": "http://localhost:8242",
            "api_key": None,
            "pipeline": {},
        }
    )

    tracker_params = kwargs.get("tracker", None)
    tracker_cfg.pipeline[name] = tracker_params or {
        "project_id": None,
        "dag_name": None,
        "tags": None,
    }

    write(tracker_cfg, "tracker", conf_path)

    logger.success(f"Created pipeline {name}")

    # return pipeline_cfg, scheduler_cfg, tracker_cfg
