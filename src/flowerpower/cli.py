import os

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
    name: str,
    environment: str = "prod",
    executor: str = "local",
    base_path: str = "",
    inputs: str = "",
    final_vars: str = "",
    with_tracker: bool = None,
):
    # run_params = (
    #     dict([kw.split("=") for kw in run_params.split(",")]) if run_params else {}
    # )
    # tracker_params = (
    #     dict([kw.split("=") for kw in tracker_params.split(",")])
    #     if tracker_params
    #     else {}
    # )
    # kwargs = {**run_params, **tracker_params}
    inputs = eval(inputs) if len(inputs) else None
    final_vars = eval(final_vars) if len(final_vars) else None
    with_tracker = with_tracker if with_tracker is not None else None

    _ = run(
        name=name,
        environment=environment,
        executor=executor,
        base_path=base_path,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
    )


@app.command()
def schedule_pipeline(
    name: str,
    environment: str = "prod",
    executor: str = "local",
    base_path: str = "",
    type: str = "cron",
    auto_start: bool = False,
    background: bool = False,
    inputs: str = "",
    final_vars: str = "",
    with_tracker: bool = None,
    crontab: str = "",
    cron_params: str = "",
    interval_params: str = "",
    calendarinterval_params: str = "",
    date_params: str = "",
):
    if get_scheduler is None:
        raise ValueError("APScheduler not installed. Please install it first.")

    inputs = eval(inputs) if len(inputs) else None
    final_vars = eval(final_vars) if len(final_vars) else None
    with_tracker = with_tracker if with_tracker is not None else None

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
        name=name,
        environment=environment,
        executor=executor,
        base_path=base_path,
        type=type,
        auto_start=auto_start,
        background=background,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        **kwargs,
    )


@app.command()
def start_scheduler(
    base_path: str = "",
    background: bool = True,
):
    conf_path = os.path.join(base_path, "conf")
    pipelines_path = os.path.join(base_path, "pipelines")
    start_scheduler_(
        conf_path=conf_path, pipelines_path=pipelines_path, background=background
    )

    # @app.command()
    # def show(
    #     schedules: bool = False,
    #     jobs: bool = False,
    #     pipelines: bool = False,
    #     conf_path: str = "",
    #     pipelines_path: str = "pipelines",
    # ):
    #     if get_scheduler is None:
    #         raise ValueError("APScheduler not installed. Please install it first.")
    #     from rich.console import Console

    #     console = Console()

    #     if conf_path == "":
    #         conf_path = None
    #     if schedules:
    #         console.rule("Schedules")
    #         scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipelines_path)
    #         console.print(scheduler.get_schedules())

    #     if jobs:
    #         console.rule("Jobs")
    #         scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipelines_path)
    #         console.print(scheduler.get_jobs())

    # list schedules
    # list jobs
    # list pipelines
    ...


@app.command()
def add_pipeline(
    name: str,
    base_path: str = "",
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
        base_path=base_path,
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
def init(name: str, pipelines_path: str = "pipelines", conf_path: str = "conf"):
    init_(name, pipelines_path=pipelines_path, conf_path=conf_path)


if __name__ == "__main__":
    app()
