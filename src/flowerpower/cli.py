import os

from typer import Typer

from .cfg import (PIPELINES_TEMPLATE, SCHEDULER_TEMPLATE, TRACKER_TEMPLATE,
                  write)
from .pipeline import run as run_pipeline
from .pipeline import schedule as schedule_pipeline
from .scheduler import get_scheduler
from .scheduler import start_scheduler as start_scheduler_

app = Typer()


@app.command()
def run(
    pipeline: str,
    environment: str = "prod",
    run_params: str = "",
    tracker_params: str = "",
):
    run_params = dict([kw.split("=") for kw in run_params.split(",")])
    tracker_params = dict([kw.split("=") for kw in tracker_params.split(",")])
    kwargs = {**run_params, **tracker_params}
    run_pipeline(pipeline=pipeline, environment=environment, **kwargs)


@app.command()
def schedule(
    pipeline: str,
    type: str,
    environment: str = "prod",
    crontab: str = "",
    cron_params: str = "",
    interval_params: str = "",
    calendarinterval_params: str = "",
    date_params: str = "",
):
    crontab = crontab or None
    cron_params = dict([kw.split("=") for kw in cron_params.split(",")])
    interval_params = dict([kw.split("=") for kw in interval_params.split(",")])
    calendarinterval_params = dict(
        [kw.split("=") for kw in calendarinterval_params.split(",")]
    )
    date_params = dict([kw.split("=") for kw in date_params.split(",")])
    kwargs = {
        **cron_params,
        **interval_params,
        **calendarinterval_params,
        **date_params,
    }
    if crontab is not None:
        kwargs["crontab"] = crontab

    schedule_pipeline(pipeline=pipeline, environment=environment, type=type, **kwargs)


@app.command()
def start_scheduler(
    conf_path: str | None = None,
    pipelines_path: str = "pipelines",
    background: bool = True,
):
    start_scheduler_(
        conf_path=conf_path, pipelines_path=pipelines_path, background=background
    )


@app.command()
def show(
    schedules: bool = False,
    jobs: bool = False,
    pipelines: bool = False,
    conf_path: str = "",
    pipelines_path: str = "pipelines",
):
    from rich.console import Console

    console = Console()

    if conf_path == "":
        conf_path = None
    if schedules:
        console.rule("Schedules")
        scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipelines_path)
        console.print(scheduler.get_schedules())

    if jobs:
        console.rule("Jobs")
        scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipelines_path)
        console.print(scheduler.get_jobs())

    # list schedules
    # list jobs
    # list pipelines
    ...


@app.command()
def add(): ...


@app.command()
def remove():
    # remove schedule
    # remove job
    # remove pipeline
    ...


@app.command()
def init(pipelines_path: str = "pipelines", conf_path: str = "conf"):
    os.makedirs(pipelines_path, exist_ok=True)
    os.makedirs(conf_path, exist_ok=True)

    write(PIPELINES_TEMPLATE, "pipelines", conf_path)


if __name__ == "__main__":
    app()
