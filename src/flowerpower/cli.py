from typer import Typer

from .pipeline import run, schedule, add, delete
from .scheduler import get_scheduler
from .scheduler import start_scheduler as start_scheduler_
from .main import init as init_

app = Typer()


@app.command()
def run_pipeline(
    pipeline: str,
    environment: str = "prod",
    run_params: str = "",
    tracker_params: str = "",
):
    run_params = dict([kw.split("=") for kw in run_params.split(",")])
    tracker_params = dict([kw.split("=") for kw in tracker_params.split(",")])
    kwargs = {**run_params, **tracker_params}
    run(pipeline=pipeline, environment=environment, **kwargs)


@app.command()
def schedule_pipeline(
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

    schedule(pipeline=pipeline, environment=environment, type=type, **kwargs)


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
def add_pipeline(
    name: str,
    pipelines_path: str,
    conf_path: str = "conf",
    overwrite: bool = False,
    params: str = "",
    run: str = "",
    schedule: str = "",
    tracker: str = "",
):
    params = dict([kw.split("=") for kw in params.split(",")])
    run = dict([kw.split("=") for kw in run.split(",")])
    schedule = dict([kw.split("=") for kw in schedule.split(",")])
    tracker = dict([kw.split("=") for kw in tracker.split(",")])

    add(
        name=name,
        pipelines_path=pipelines_path,
        conf_path=conf_path,
        overwrite=overwrite,
        params=params,
        run=run,
        schedule=schedule,
        tracker=tracker,
    )


@app.command()
def delete_pipeline():
    delete()


@app.command()
def init(pipelines_path: str = "pipelines", conf_path: str = "conf"):
    init_(pipelines_path=pipelines_path, conf_path=conf_path)


if __name__ == "__main__":
    app()
