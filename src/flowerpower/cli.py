import importlib.util

from loguru import logger
from typer import Typer

from .pipeline import add as add_
from .pipeline import add_job as add_job_
from .pipeline import delete as delete_
from .pipeline import run as run_
from .pipeline import run_job as run_job_
from .pipeline import schedule as schedule_
from .pipeline import show as show_

if importlib.util.find_spec("apscheduler"):
    from .scheduler import get_schedule_manager
    from .scheduler import start_worker as start_worker_
else:
    get_schedule_manager = None
    start_scheduler_ = None

from . import init as init_

app = Typer()


@app.command()
def run(
    name: str,
    environment: str = "dev",
    executor: str = "local",
    base_dir: str = "",
    inputs: str = "",
    final_vars: str = "",
    with_tracker: bool = False,
    reload: bool = False,
):
    """
    Run the specified task.
    Args:
        name (str): The name of the task.
        environment (str, optional): The environment to run the task in. Defaults to "dev".
        executor (str, optional): The executor to use for running the task. Defaults to "local".
        base_dir (str, optional): The base path for the task. Defaults to "".
        inputs (str, optional): The inputs for the task. Defaults to "".
        final_vars (str, optional): The final variables for the task. Defaults to "".
        with_tracker (bool, optional): Whether to use a tracker for the task. Defaults to False.
        reload (bool, optional): Whether to reload the task. Defaults to False.
    """
    inputs = eval(inputs) if len(inputs) else None
    final_vars = eval(final_vars) if len(final_vars) else None
    with_tracker = with_tracker if with_tracker is not None else None

    _ = run_(
        name=name,
        environment=environment,
        executor=executor,
        base_dir=base_dir,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        reload=reload,
    )


@app.command()
def run_job(
    name: str,
    environment: str = "dev",
    executor: str = "local",
    base_dir: str = "",
    inputs: str = "",
    final_vars: str = "",
    with_tracker: bool = False,
    reload: bool = False,
):
    """
    Add a job to run the pipeline with the given parameters to the scheduler.
    Executes the job immediatly.

    Args:
        name (str): The name of the job.
        environment (str, optional): The environment to run the job in. Defaults to "dev".
        executor (str, optional): The executor to use for the job. Defaults to None.
        inputs (str, optional): The inputs for the job. Defaults to None.
        final_vars (str, optional): The final variables for the job. Defaults to None.
        with_tracker (bool, optional): Whether to use a tracker for the job. Defaults to None.
        base_dir (str, optional): The base path for the job. Defaults to None.
        reload (bool): Whether to reload the job. Defaults to False.
    """

    inputs = eval(inputs) if len(inputs) else None
    final_vars = eval(final_vars) if len(final_vars) else None
    with_tracker = with_tracker if with_tracker is not None else None

    _ = run_job_(
        name=name,
        environment=environment,
        executor=executor,
        base_dir=base_dir,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        reload=reload,
    )


@app.command()
def add_job(
    name: str,
    environment: str = "dev",
    executor: str = "local",
    base_dir: str = "",
    inputs: str = "",
    final_vars: str = "",
    with_tracker: bool = False,
    reload: bool = False,
):
    """
    Add a job to run the pipeline with the given parameters to the scheduler data store.
    Executes the job immediatly and returns the job id (UUID). The job result will be stored in the data store for the
    given `result_expiration_time` and can be fetched using the job id (UUID).

    Args:
        name (str): The name of the job.
        environment (str, optional): The environment to run the job in. Defaults to "dev".
        executor (str, optional): The executor to use for the job. Defaults to None.
        inputs (str, optional): The inputs for the job. Defaults to None.
        final_vars (str, optional): The final variables for the job. Defaults to None.
        with_tracker (bool, optional): Whether to use a tracker for the job. Defaults to None.
        base_dir (str, optional): The base path for the job. Defaults to None.
        reload (bool): Whether to reload the job. Defaults to False.
    """

    inputs = eval(inputs) if len(inputs) else None
    final_vars = eval(final_vars) if len(final_vars) else None
    with_tracker = with_tracker if with_tracker is not None else None

    id_ = add_job_(
        name=name,
        environment=environment,
        executor=executor,
        base_dir=base_dir,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        reload=reload,
    )
    logger.info(f"Job {id_} added to the scheduler.")


@app.command()
def schedule(
    name: str,
    environment: str = "dev",
    executor: str = "local",
    base_dir: str = "",
    type: str = "cron",
    inputs: str = "",
    final_vars: str = "",
    with_tracker: bool = False,
    paused: bool = False,
    coalesce: str = "latest",
    misfire_grace_time: float = None,
    max_jitter: float = None,
    max_running_jobs: int = None,
    conflict_policy: str = "do_nothing",
    crontab: str = "",
    cron_params: str = "",
    interval_params: str = "",
    calendarinterval_params: str = "",
    date_params: str = "",
):
    """
    Schedule a job with the given parameters.

    Args:
        name (str): The name of the job.
        environment (str, optional): The environment to run the job in. Defaults to "dev".
        executor (str, optional): The executor to use for running the job. Defaults to "local".
        base_dir (str, optional): The base path for the job. Defaults to "".
        type (str, optional): The type of the job. Defaults to "cron".
        inputs (str, optional): The inputs for the job. Defaults to "".
        final_vars (str, optional): The final variables for the job. Defaults to "".
        with_tracker (bool, optional): Whether to use a tracker for the job. Defaults to False.
        paused (bool, optional): Whether the job should be initially paused. Defaults to False.
        coalesce (str, optional): The coalesce strategy for the job. Defaults to "latest".
        misfire_grace_time (float, optional): The misfire grace time for the job. Defaults to None.
        max_jitter (float, optional): The maximum jitter for the job. Defaults to None.
        max_running_jobs (int, optional): The maximum number of running jobs. Defaults to None.
        conflict_policy (str, optional): The conflict policy for the job. Defaults to "do_nothing".
        crontab (str, optional): The crontab expression for the job. Defaults to "".
        cron_params (str, optional): Additional parameters for the cron job. Defaults to "".
        interval_params (str, optional): Additional parameters for the interval job. Defaults to "".
        calendarinterval_params (str, optional): Additional parameters for the calendar interval job. Defaults to "".
        date_params (str, optional): Additional parameters for the date job. Defaults to "".
    """
    if get_schedule_manager is None:
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

    id_ = schedule_(
        name=name,
        environment=environment,
        executor=executor,
        base_dir=base_dir,
        type=type,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        paused=paused,
        coalesce=coalesce,
        misfire_grace_time=misfire_grace_time,
        max_jitter=max_jitter,
        max_running_jobs=max_running_jobs,
        conflict_policy=conflict_policy,
        **kwargs,
    )
    logger.info(f"Job {id_} scheduled.")


@app.command()
def new(
    name: str,
    base_dir: str = "",
    overwrite: bool = False,
    pipeline_params: str = "",
    run_params: str = "",
    schedule_params: str = "",
    tracker_params: str = "",
):
    """
    Create a new pipeline with the given parameters.

    Args:
        name (str): The name of the pipeline.
        base_dir (str, optional): The base path for the pipeline. Defaults to "".
        overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
        pipeline_params (str, optional): Additional parameters for the pipeline. Defaults to "".
        run_params (str, optional): Additional parameters for the run. Defaults to "".
        schedule_params (str, optional): Additional parameters for the schedule. Defaults to "".
        tracker_params (str, optional): Additional parameters for the tracker. Defaults to "".
    """
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

    add_(
        name=name,
        base_dir=base_dir,
        overwrite=overwrite,
        params=pipeline_params,
        run=run_params,
        schedule=schedule_params,
        tracker=tracker_params,
    )


@app.command()
def delete(name: str, base_dir: str = "", module: bool = False):
    """
    Delete a pipeline.

    Args:
        name (str): The name of the pipeline to delete.
        base_dir (str): The base path of the pipeline. Defaults to None.
        module (bool, optional): Whether to delete the pipeline module. Defaults to False.
    """
    delete_(name=name, base_dir=base_dir, module=module)


@app.command()
def init(name: str):
    """
    Initialize the FlowerPower application.

    Args:
        name (str): The name of the application.
    """
    init_(name)


@app.command()
def start_worker(name: str, base_dir: str = ""):
    """
    Start a worker.

    Args:
        name (str): The name of the worker.
        base_dir (str, optional): The base path. Defaults to "".
    """

    start_worker_(name=name, base_dir=base_dir, background=False)


@app.command()
def show(name: str, base_dir: str = ""):
    """
    Show the pipeline.

    Args:
        name (str): The name of the pipeline.
        base_dir (str, optional): The base path of the pipeline. Defaults to "".
    """
    show_(name=name, base_dir=base_dir, view=True)


@app.command()
def hamilton_ui(
    port: int = 8241,
    base_dir: str = "~/.hamilton/db",
    no_migration: bool = False,
    no_open: bool = False,
    settings_file: str = "mini",
    config_file: str = None,
):
    """
    Start the Hamilton UI.

    Args:
        port (int, optional): The port to run the UI on. Defaults to 8241.
        base_dir (str, optional): The base path for the UI. Defaults to "~/.hamilton/db".
        no_migration (bool, optional): Whether to run the migration. Defaults to False.
        no_open (bool, optional): Whether to open the UI in the browser. Defaults to False.
        settings_file (str, optional): The settings file to use. Defaults to "mini".
        config_file (str, optional): The config file to use. Defaults to None.
    """
    try:
        from hamilton_ui import commands
    except ImportError:
        logger.error(
            "hamilton[ui] not installed -- you have to install this to run the UI. "
            'Run `pip install "sf-hamilton[ui]"` to install and get started with the UI!'
        )
        raise app.Exit(code=1)

    commands.run(
        port=port,
        base_dir=base_dir,
        no_migration=no_migration,
        no_open=no_open,
        settings_file=settings_file,
        config_file=config_file,
    )


if __name__ == "__main__":
    app()
