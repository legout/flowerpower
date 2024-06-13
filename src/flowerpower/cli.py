from typer import Typer
import importlib.util

from .pipeline import run, schedule, add, delete

if importlib.util.find_spec("apscheduler"):
    from .scheduler import get_scheduler
    from .scheduler import start_scheduler as start_scheduler_
else:
    get_scheduler = None
    start_scheduler_ = None

from .main import init as init_

app = Typer()


@app.command()
def run_pipeline(
    pipeline: str,
    environment: str = "prod",
    executor: str = "local",
    run_params: str = "",
    tracker_params: str = "",
):
    run_params = (
        dict([kw.split("=") for kw in run_params.split(",")]) if run_params else {}
    )
    tracker_params = (
        dict([kw.split("=") for kw in tracker_params.split(",")])
        if tracker_params
        else {}
    )
    kwargs = {**run_params, **tracker_params}
    _ = run(pipeline=pipeline, environment=environment, executor=executor, **kwargs)


@app.command()
def schedule_pipeline(
    pipeline: str,
    type: str,
    environment: str = "prod",
    executor: str = "local",
    auto_start: bool = False,
    background: bool = False,
    crontab: str = "",
    cron_params: str = "",
    interval_params: str = "",
    calendarinterval_params: str = "",
    date_params: str = "",
):
    if get_scheduler is None:
        raise ValueError("APScheduler not installed. Please install it first.")

    crontab = crontab or None
    cron_params = (
        dict([kw.split("=") for kw in cron_params.split(",")]) if cron_params else {}
    )
    interval_params = (
        dict([kw.split("=") for kw in interval_params.split(",")])
        if interval_params
        else {}
    )

    calendarinterval_params = (
        dict([kw.split("=") for kw in calendarinterval_params.split(",")])
        if calendarinterval_params
        else {}
    )
    date_params = (
        dict([kw.split("=") for kw in date_params.split(",")]) if date_params else {}
    )
    try:
        for key in ["weeks", "days", "hours", "minutes", "seconds"]:
            if key in interval_params:
                interval_params[key] = float(interval_params[key])
            if key in calendarinterval_params:
                calendarinterval_params[key] = float(calendarinterval_params[key])
    except ValueError:
        pass
    kwargs = {
        **cron_params,
        **interval_params,
        **calendarinterval_params,
        **date_params,
    }
    if crontab is not None:
        kwargs["crontab"] = crontab

    schedule(
        pipeline=pipeline,
        environment=environment,
        executor=executor,
        type=type,
        auto_start=auto_start,
        background=background,
        **kwargs,
    )


@app.command()
def start_scheduler(
    conf_path: str = "conf",
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
    if get_scheduler is None:
        raise ValueError("APScheduler not installed. Please install it first.")
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
    pipelines_path: str = "pipelines",
    conf_path: str = "conf",
    overwrite: bool = False,
    pipeline_params: str = "",
    run_params: str = "",
    schedule_params: str = "",
    tracker_params: str = "",
):
    pipeline_params = (
        dict([kw.split("=") for kw in pipeline_params.split(",")])
        if pipeline_params
        else {}
    )
    run_params = (
        dict([kw.split("=") for kw in run_params.split(",")]) if run_params else {}
    )
    schedule_params = (
        dict([kw.split("=") for kw in schedule_params.split(",")])
        if schedule_params
        else {}
    )
    tracker_params = (
        dict([kw.split("=") for kw in tracker_params.split(",")])
        if tracker_params
        else {}
    )

    add(
        name=name,
        pipelines_path=pipelines_path,
        conf_path=conf_path,
        overwrite=overwrite,
        params=pipeline_params,
        run=run_params,
        schedule=schedule_params,
        tracker=tracker_params,
    )


@app.command()
def delete_pipeline():
    delete()


@app.command()
def init(pipelines_path: str = "pipelines", conf_path: str = "conf"):
    init_(pipelines_path=pipelines_path, conf_path=conf_path)


if __name__ == "__main__":
    app()
