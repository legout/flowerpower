# import typer
from hamilton import driver
from hamilton_sdk import adapters
from loguru import logger

# from hamilton.execution import executors
from .config import load_pipeline_params
from .scheduler import configure_scheduler
from typing import Any

# from .pipelines import *
import importlib
import datetime as dt
from dateutil import tz


def run_pipeline(
    pipeline: str,
    environment: str = "prod",
    with_tracker: bool = False,
    project_id: int | None = None,
    **kwargs,
) -> None:

    PIPELINE_PARAMS = load_pipeline_params().run[environment][pipeline.split(".")[-1]]
    module = importlib.import_module(pipeline)
    if with_tracker:
        if project_id is None:
            raise ValueError(
                "Please provide a project_id if you want to use the tracker"
            )
        tracker = adapters.HamiltonTracker(
            project_id=project_id,
            **kwargs,
            # username="volker.lorrmann@siemens.com",
            # dag_name="my_version_of_the_dag",
            # tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
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

    logger.info(f"Starting pipeline {pipeline}")

    _ = dr.execute(final_vars=PIPELINE_PARAMS.final_vars, inputs=PIPELINE_PARAMS.inputs)

    logger.success(f"Finished pipeline {pipeline}")


def schedule_pipeline(
    pipeline: str,
    environment: str = "prod",
    type: str = "cron",
    year: int | str | None = None,
    month: int | str | None = None,
    week: int | str | None = None,
    day: float | int | str | None = None,
    days_of_week: float | int | str | None = None,
    hour: int | str | None = None,
    minute: int | str | None = None,
    second: int | str | None = None,
    weeks: float | int = 0,
    days: float | int = 0,
    hours: float | int = 0,
    minutes: float | int = 0,
    seconds: float | int = 0,
    microseconds: float | int = 0,
    start_time: Any = dt.datetime.now(),
    end_time: Any = None,
    timezone: Any = tz.tzlocal(),
    crontab: str | None = None,
    with_tracker: bool = False,
    project_id: int | None = None,
    **kwargs,
):
    scheduler = configure_scheduler()
    if type == "cron":
        if crontab is not None:
            from apscheduler.triggers.cron import CronTrigger

            trigger = CronTrigger.from_crontab(crontab)
        else:
            from apscheduler.triggers.cron import CronTrigger

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

    scheduler.add_schedule(
        run_pipeline,
        trigger=trigger,
        args=(environment, pipeline, with_tracker, project_id),
        kwargs=kwargs,
    )


if __name__ == "__main__":
    pass
    # app()
    # run("raw_to_stage1", filesystem="local")
