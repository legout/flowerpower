# import typer
import datetime as dt
import importlib.util

# from .pipelines import *
import importlib
import os
import sys

from dateutil import tz
from hamilton import driver
from hamilton.execution import executors
from hamilton_sdk import adapters
from loguru import logger
from munch import munchify, unmunchify

from .cfg import (
    PIPELINE_PY_TEMPLATE,
    load_pipeline_cfg,
    load_scheduler_cfg,
    load_tracker_cfg,
    write,
)


if importlib.util.find_spec("apscheduler"):
    # from hamilton.execution import executors
    from .scheduler import get_scheduler

else:
    get_scheduler = None

# PIPELINE = load_pipeline_cfg()
# TRACKER = load_tracker_cfg()
# SCHEDULER = load_scheduler_cfg()


def get_driver(
    pipeline: str,
    executor: str | None = None,
    base_path: str = "",
    with_tracker: bool = False,
    **kwargs,
) -> driver.Driver:
    conf_path = os.path.join(base_path, "conf")
    pipeline_path = os.path.join(base_path, "pipelines")

    tracker_cfg = load_tracker_cfg(path=conf_path)
    tracker_params = tracker_cfg.pipeline[pipeline]

    sys.path.append(pipeline_path)
    module = importlib.import_module(pipeline)

    if executor is None or executor == "local":
        executor_ = executors.SynchronousLocalTaskExecutor()
    elif executor == "MultiProcessingExecutor" or executor == "multiprocessing":
        executor_ = executors.MultiProcessingExecutor(max_tasks=20)
    elif executor == "MultiThreadingExecutor" or executor == "multithreading":
        executor_ = executors.MultiThreadingExecutor(max_tasks=20)

    if with_tracker:
        project_id = kwargs.pop("project_id", None) or tracker_params.get(
            "project_id", None
        )
        username = kwargs.pop("username", None) or tracker_cfg.get("username", None)
        dag_name = kwargs.pop("dag_name", None) or tracker_params.get("dag_name", None)
        tags = kwargs.pop("tags", None) or tracker_params.get("tags", None)
        api_url = kwargs.pop("api_url", None) or tracker_cfg.get("api_url", None)
        ui_url = kwargs.pop("ui_url", None) or tracker_cfg.get("ui_url", None)

        if project_id is None:
            raise ValueError(
                "Please provide a project_id if you want to use the tracker"
            )

        tracker = adapters.HamiltonTracker(
            project_id=project_id,
            username=username,
            dag_name=dag_name,
            tags=tags,
            hamilton_api_url=api_url,
            hamilton_ui_url=ui_url,
        )

        dr = (
            driver.Builder()
            .with_modules(module)
            .enable_dynamic_execution(allow_experimental_mode=True)
            .with_adapters(tracker)
            .with_remote_executor(executor_)
            .build()
        )
    else:
        dr = (
            driver.Builder()
            .with_modules(module)
            .enable_dynamic_execution(allow_experimental_mode=True)
            .with_remote_executor(executor_)
            .build()
        )

    return dr


def run(
    pipeline: str,
    environment: str = "prod",
    executor: str | None = None,
    base_path: str = "",
    inputs: dict | None = None,
    final_vars: list | None = None,
    with_tracker: bool | None = None,
    **kwargs,
) -> None:
    conf_path = os.path.join(base_path, "conf")
    # pipeline_path = os.path.join(base_path, "pipelines")

    pipeline_cfg = load_pipeline_cfg(path=conf_path)

    logger.info(f"Starting pipeline {pipeline} in environment {environment}")

    run_params = getattr(pipeline_cfg.run, pipeline)[environment]

    final_vars = final_vars or run_params.get("final_vars", [])
    inputs = {**(run_params.get("inputs", {}) or {}), **(inputs or {})}
    with_tracker = with_tracker or run_params.get("with_tracker", False)

    dr = get_driver(
        pipeline=pipeline,
        executor=executor,
        base_path=base_path,
        with_tracker=with_tracker,
        **kwargs,
    )

    res = dr.execute(final_vars=final_vars, inputs=unmunchify(inputs))

    logger.success(f"Finished pipeline {pipeline}")

    return res


def schedule(
    pipeline: str,
    environment: str = "prod",
    executor: str | None = None,
    base_path: str = "",
    type: str = "cron",
    auto_start: bool = True,
    background: bool = False,
    inputs: dict | None = None,
    final_vars: list | None = None,
    with_tracker: bool | None = None,
    **kwargs,
):
    if get_scheduler is None:
        raise ValueError("APScheduler not installed. Please install it first.")

    conf_path = os.path.join(base_path, "conf")
    pipeline_path = os.path.join(base_path, "pipelines")

    scheduler_cfg = load_scheduler_cfg(path=conf_path)

    scheduler_params = scheduler_cfg.pipeline[pipeline]

    start_time = kwargs.pop("start_time", dt.datetime.now()) or scheduler_params.get(
        "start_time", dt.datetime.now()
    )
    end_time = kwargs.pop("end_time", None) or scheduler_params.get("end_time", None)

    scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipeline_path)
    if type == "cron":
        crontab = kwargs.pop("crontab", None) or scheduler_params.get("crontab", None)
        if crontab is not None:
            from apscheduler.triggers.cron import CronTrigger

            trigger = CronTrigger.from_crontab(crontab)
        else:
            from apscheduler.triggers.cron import CronTrigger

            year = kwargs.pop("year", None) or scheduler_params.get("year", None)
            month = kwargs.pop("month", None) or scheduler_params.get("month", None)
            week = kwargs.pop("week", None) or scheduler_params.get("week", None)
            day = kwargs.pop("day", None) or scheduler_params.get("day", None)
            days_of_week = kwargs.pop("days_of_week", None) or scheduler_params.get(
                "days_of_week", None
            )
            hour = kwargs.pop("hour", None) or scheduler_params.get("hour", None)
            minute = kwargs.pop("minute", None) or scheduler_params.get("minute", None)
            second = kwargs.pop("second", None) or scheduler_params.get("second", None)
            timezone = kwargs.pop(
                "timezone", tz.gettz("Europe/Berlin")
            ) or scheduler_params.get("timezone", tz.gettz("Europe/Berlin"))

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

        weeks = kwargs.pop("weeks", 0) or scheduler_params.get("weeks", 0)
        days = kwargs.pop("days", 0) or scheduler_params.get("days", 0)
        hours = kwargs.pop("hours", 0) or scheduler_params.get("hours", 0)
        minutes = kwargs.pop("minutes", 0) or scheduler_params.get("minutes", 0)
        seconds = kwargs.pop("seconds", 0) or scheduler_params.get("seconds", 0)
        microseconds = kwargs.pop("microseconds", 0) or scheduler_params.get(
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
        from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger

        weeks = kwargs.pop("weeks", 0) or scheduler_params.get("weeks", 0)
        days = kwargs.pop("days", 0) or scheduler_params.get("days", 0)
        hours = kwargs.pop("hours", 0) or scheduler_params.get("hours", 0)
        minutes = kwargs.pop("minutes", 0) or scheduler_params.get("minutes", 0)
        seconds = kwargs.pop("seconds", 0) or scheduler_params.get("seconds", 0)
        microseconds = kwargs.pop("microseconds", 0) or scheduler_params.get(
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
        args=(
            pipeline,
            environment,
            executor,
            base_path,
            inputs,
            final_vars,
            with_tracker,
        ),
        kwargs=kwargs,
    )
    logger.success(
        f"Added scheduler for {pipeline} in environment {environment} with id {id_}"
    )
    if auto_start:
        if background:
            scheduler.start_in_background()
            return scheduler, id_

        else:
            scheduler.run_until_stopped()


def add(
    name: str,
    base_path: str = "",
    overwrite: bool = False,
    params: dict | None = None,
    run: dict | None = None,
    schedule: dict | None = None,
    tracker: dict | None = None,
):
    logger.info(f"Creating new pipeline {name}")

    conf_path = os.path.join(base_path, "conf")
    pipelines_path = os.path.join(base_path, "pipelines")

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
            PIPELINE_PY_TEMPLATE.format(
                name=name, date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
    logger.info(f"Created pipeline module {name}.py")
    # pipeline configuration

    pipeline_cfg = load_pipeline_cfg(path=conf_path) or munchify(
        {"run": {}, "params": {}}
    )
    if pipeline_cfg.params is None:
        pipeline_cfg.params = {}
    if pipeline_cfg.run is None:
        pipeline_cfg.run = {}

    # pipeline_run = kwargs.get("run", None)
    # pipeline_params = kwargs.get("params", None)

    pipeline_cfg.params[name] = params or None
    pipeline_cfg.run[name] = run or munchify(
        {
            "dev": {"inputs": None, "final_vars": None, "with_tracker": False},
            "prod": {"inputs": None, "final_vars": None, "with_tracker": True},
        }
    )

    write(pipeline_cfg, "pipeline", conf_path)
    logger.info(f"Updated pipeline configuration {conf_path}/pipeline.yml")

    # scheduler configuration

    scheduler_cfg = load_scheduler_cfg(path=conf_path) or munchify(
        {
            "data_store": {"type": "memory"},
            "event_broker": {"type": "local"},
            "pipeline": {},
        }
    )
    if scheduler_cfg.pipeline is None:
        scheduler_cfg.pipeline = {}
    # schedule_params = kwargs.get("schedule", None)
    scheduler_cfg.pipeline[name] = schedule or {"type": None}

    write(scheduler_cfg, "scheduler", conf_path)
    logger.info(f"Updated scheduler configuration {conf_path}/scheduler.yml")

    # tracker configuration
    tracker_cfg = load_tracker_cfg(path=conf_path) or munchify(
        {
            "username": None,
            "api_url": "http://localhost:8241",
            "ui_url": "http://localhost:8242",
            "api_key": None,
            "pipeline": {},
        }
    )
    if tracker_cfg.pipeline is None:
        tracker_cfg.pipeline = {}

    # tracker_params = kwargs.get("tracker", None)
    tracker_cfg.pipeline[name] = tracker or {
        "project_id": None,
        "dag_name": None,
        "tags": None,
    }

    write(tracker_cfg, "tracker", conf_path)
    logger.info(f"Updated tracker configuration {conf_path}/tracker.yml")

    logger.success(f"Created pipeline {name}")

    # return pipeline_cfg, scheduler_cfg, tracker_cfg


def delete():
    pass


def show(pipeline: str, format: str = "png", view: bool = False):
    os.makedirs("graphs", exist_ok=True)
    dr = get_driver(
        pipeline=pipeline, environment="dev", executor=None, with_tracker=False
    )
    if view:
        dr.display_all_functions(f"graphs/{pipeline}.{format}").view()
    else:
        dr.display_all_functions(f"graphs/{pipeline}.{format}")
