import importlib.util

from loguru import logger
from typer import Typer

from .pipeline import add as add_pipeline_
from .pipeline import add_job as add_pipeline_job_
from .pipeline import all_pipelines as all_pipelines_
from .pipeline import delete as delete_pipeline_
from .pipeline import get_summary as get_pipeline_summary_
from .pipeline import new as new_pipeline_
from .pipeline import run as run_pipeline_
from .pipeline import run_job as run_pipeline_job_
from .pipeline import save_dag as save_pipeline_dag_
from .pipeline import schedule as schedule_pipeline_
from .pipeline import show_dag as show_pipeline_dag_
from .pipeline import show_summary as show_pipeline_summary_
from .pipeline import start_mqtt_listener as start_mqtt_listener_

if importlib.util.find_spec("apscheduler"):
    from .scheduler import get_schedule_manager
    from .scheduler import start_worker as start_worker_
else:
    get_schedule_manager = None
    start_scheduler_ = None

from . import init as init_

app = Typer()


@app.command()
def run_pipeline(
    pipeline_name: str,
    executor: str = "local",
    base_dir: str = None,
    inputs: str = None,
    final_vars: str = None,
    with_tracker: bool = False,
    reload: bool = False,
    storage_options: str = None,
):
    """
    Run the specified task.
    Args:
        pipeline_name (str): The name of the task.
        executor (str, optional): The executor to use for running the task. Defaults to "local".
        base_dir (str, optional): The base path for the task. Defaults to None.
        inputs (str, optional): The inputs for the task. Defaults to None.
        final_vars (str, optional): The final variables for the task. Defaults to None.
        with_tracker (bool, optional): Whether to use a tracker for the task. Defaults to False.
        reload (bool, optional): Whether to reload the task. Defaults to False.
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None.
    """
    inputs = eval(inputs) if inputs is not None else None
    final_vars = eval(final_vars) if final_vars is not None else None
    with_tracker = with_tracker if with_tracker is not None else None
    storage_options = eval(storage_options) if storage_options is not None else {}

    _ = run_pipeline_(
        name=pipeline_name,
        executor=executor,
        base_dir=base_dir,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        reload=reload,
        storage_options=storage_options,
    )


@app.command()
def run_pipeline_job(
    pipeline_name: str,
    executor: str = "local",
    base_dir: str = None,
    inputs: str = None,
    final_vars: str = None,
    with_tracker: bool = False,
    reload: bool = False,
    storage_options: str = None,
):
    """
    Add a job to run the pipeline with the given parameters to the scheduler.
    Executes the job immediatly.

    Args:
        name (str): The name of the job.
        executor (str, optional): The executor to use for the job. Defaults to None.
        inputs (str, optional): The inputs for the job. Defaults to None.
        final_vars (str, optional): The final variables for the job. Defaults to None.
        with_tracker (bool, optional): Whether to use a tracker for the job. Defaults to None.
        base_dir (str, optional): The base path for the job. Defaults to None.
        reload (bool): Whether to reload the job. Defaults to False.
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None.
    """

    inputs = eval(inputs) if inputs else None
    final_vars = eval(final_vars) if final_vars is not None else None
    with_tracker = with_tracker if with_tracker is not None else None
    storage_options = eval(storage_options) if storage_options is not None else {}

    _ = run_pipeline_job_(
        name=pipeline_name,
        executor=executor,
        base_dir=base_dir,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        reload=reload,
        storage_options=storage_options,
    )


@app.command()
def add_pipeline_job(
    pipeline_name: str,
    executor: str = "local",
    base_dir: str = None,
    inputs: str = None,
    final_vars: str = None,
    with_tracker: bool = False,
    reload: bool = False,
    storage_options: str = None,
):
    """
    Add a job to run the pipeline with the given parameters to the scheduler data store.
    Executes the job immediatly and returns the job id (UUID). The job result will be stored in the data store for the
    given `result_expiration_time` and can be fetched using the job id (UUID).

    Args:
        pipeline_name (str): The name of the job.
        executor (str, optional): The executor to use for the job. Defaults to None.
        inputs (str, optional): The inputs for the job. Defaults to None.
        final_vars (str, optional): The final variables for the job. Defaults to None.
        with_tracker (bool, optional): Whether to use a tracker for the job. Defaults to None.
        base_dir (str, optional): The base path for the job. Defaults to None.
        reload (bool): Whether to reload the job. Defaults to False.
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None.
    """

    inputs = eval(inputs) if inputs else None
    final_vars = eval(final_vars) if final_vars is not None else None
    with_tracker = with_tracker if with_tracker is not None else None
    storage_options = eval(storage_options) if storage_options is not None else {}

    id_ = add_pipeline_job_(
        name=pipeline_name,
        executor=executor,
        base_dir=base_dir,
        inputs=inputs,
        final_vars=final_vars,
        with_tracker=with_tracker,
        reload=reload,
        storage_options=storage_options,
    )
    logger.info(f"Job {id_} added to the scheduler.")


@app.command()
def schedule_pipeline(
    pipeline_name: str,
    executor: str = "local",
    base_dir: str = None,
    type: str = "cron",
    inputs: str = None,
    final_vars: str = None,
    with_tracker: bool = False,
    paused: bool = False,
    coalesce: str = "latest",
    misfire_grace_time: float = None,
    max_jitter: float = None,
    max_running_jobs: int = None,
    conflict_policy: str = "do_nothing",
    crontab: str = None,
    cron_params: str = None,
    interval_params: str = None,
    calendarinterval_params: str = None,
    date_params: str = None,
    storage_options: str = None,
):
    """
    Schedule a job with the given parameters.

    Args:
        pipeline_name (str): The name of the job.
        executor (str, optional): The executor to use for running the job. Defaults to "local".
        base_dir (str, optional): The base path for the job. Defaults to None.
        type (str, optional): The type of the job. Defaults to "cron".
        inputs (str, optional): The inputs for the job. Defaults to None.
        final_vars (str, optional): The final variables for the job. Defaults to None.
        with_tracker (bool, optional): Whether to use a tracker for the job. Defaults to False.
        paused (bool, optional): Whether the job should be initially paused. Defaults to False.
        coalesce (str, optional): The coalesce strategy for the job. Defaults to "latest".
        misfire_grace_time (float, optional): The misfire grace time for the job. Defaults to None.
        max_jitter (float, optional): The maximum jitter for the job. Defaults to None.
        max_running_jobs (int, optional): The maximum number of running jobs. Defaults to None.
        conflict_policy (str, optional): The conflict policy for the job. Defaults to "do_nothing".
        crontab (str, optional): The crontab expression for the job. Defaults to None.
        cron_params (str, optional): Additional parameters for the cron job. Defaults to None.
        interval_params (str, optional): Additional parameters for the interval job. Defaults to None.
        calendarinterval_params (str, optional): Additional parameters for the calendar interval job. Defaults to None.
        date_params (str, optional): Additional parameters for the date job. Defaults to None.
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None.
    """
    if get_schedule_manager is None:
        raise ValueError("APScheduler not installed. Please install it first.")

    inputs = eval(inputs) if inputs else None
    final_vars = eval(final_vars) if final_vars is not None else None
    with_tracker = with_tracker if with_tracker is not None else None
    storage_options = eval(storage_options) if storage_options is not None else {}

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

    id_ = schedule_pipeline_(
        name=pipeline_name,
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
        storage_options=storage_options,
        **kwargs,
    )
    logger.info(f"Job {id_} scheduled.")


@app.command()
def new_pipeline(
    pipeline_name: str,
    base_dir: str = None,
    overwrite: bool = False,
    storage_options: str = None,
):
    """
    Create a new pipeline with the given parameters.

    Args:
        pipeline_name (str): The name of the pipeline.
        base_dir (str, optional): The base path for the pipeline. Defaults to None.
        overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None".
    """

    storage_options = eval(storage_options) if storage_options is not None else {}

    new_pipeline_(
        name=pipeline_name,
        base_dir=base_dir,
        overwrite=overwrite,
        storage_options=storage_options,
    )


@app.command()
def add_pipeline(
    pipeline_name: str,
    base_dir: str = None,
    overwrite: bool = False,
    pipeline_file: str = "",
    pipeline_config: str = "",
    storage_options: str = None,
):
    """
    Create a new pipeline with the given parameters.

    Args:
        pipeline_name (str): The name of the pipeline.
        base_dir (str, optional): The base path for the pipeline. Defaults to None.
        overwrite (bool, optional): Whether to overwrite an existing pipeline with the same name. Defaults to False.
        pipeline_file (str, optional): The path to the pipeline file. Defaults to "".
        pipeline_config (str, optional): The path to the pipeline configuration. Defaults to "".
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None".
    """

    storage_options = eval(storage_options) if storage_options is not None else {}

    add_pipeline_(
        name=pipeline_name,
        base_dir=base_dir,
        overwrite=overwrite,
        pipeline_config=pipeline_config,
        pipeline_file=pipeline_file,
        storage_options=storage_options,
    )


@app.command()
def delete_pipeline(
    pipeline_name: str,
    base_dir: str = None,
    module: bool = False,
    storage_options: str = "{}",
):
    """
    Delete a pipeline.

    Args:
        pipeline_name (str): The name of the pipeline to delete.
        base_dir (str): The base path of the pipeline. Defaults to None.
        module (bool, optional): Whether to delete the pipeline module. Defaults to False.
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None".
    """

    storage_options = eval(storage_options) if storage_options is not None else {}

    delete_pipeline_(
        name=pipeline_name,
        base_dir=base_dir,
        remove_module=module,
        storage_options=storage_options,
    )


@app.command()
def init(
    project_name: str = None,
    base_dir: str = None,
    storage_options: str = None,
):
    """
    Initialize the FlowerPower application.

    Args:
        name (str): The name of the application.
        base_dir (str, optional): The base path of the application. Defaults to "".
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None".
    """
    storage_options = eval(storage_options) if storage_options is not None else {}

    init_(
        name=project_name,
        base_dir=base_dir,
        storage_options=storage_options,
    )


@app.command()
def start_worker(worker_name: str, base_dir: str = None, storage_options: str = "{}"):
    """
    Start a worker.

    Args:
        name (str): The name of the worker.
        base_dir (str, optional): The base path. Defaults to "".
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None".
    """
    storage_options = eval(storage_options) if storage_options is not None else {}

    start_worker_(
        name=worker_name,
        base_dir=base_dir,
        background=False,
        storage_options=storage_options,
    )


@app.command()
def save_pipeline_dag(
    pipeline_name: str,
    base_dir: str = None,
    format: str = "png",
    storage_options: str = "{}",
):
    """
    Show the pipeline.

    Args:
        pipeline_name (str): The name of the pipeline.
        base_dir (str, optional): The base path of the pipeline. Defaults to "".
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None".
    """
    storage_options = eval(storage_options) if storage_options is not None else {}
    save_pipeline_dag_(
        name=pipeline_name,
        base_dir=base_dir,
        format=format,
        storage_options=storage_options,
    )


@app.command()
def show_pipeline_dag(
    pipeline_name: str,
    base_dir: str = None,
    storage_options: str = "{}",
):
    """
    Show the pipeline.

    Args:
        pipeline_name (str): The name of the pipeline.
        base_dir (str, optional): The base path of the pipeline. Defaults to "".
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None".
    """
    storage_options = eval(storage_options) if storage_options is not None else {}
    show_pipeline_dag_(
        name=pipeline_name,
        base_dir=base_dir,
        storage_options=storage_options,
    )


@app.command()
def all_pipelines(base_dir: str = None, storage_options: str = "{}"):
    """
    List all pipelines.

    Args:
        base_dir (str, optional): The base path of the pipelines. Defaults to "".
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None".
    """
    storage_options = eval(storage_options) if storage_options is not None else {}
    all_pipelines_(base_dir=base_dir, storage_options=storage_options)


@app.command()
def get_pipeline_summary(
    pipeline_name: str = None,
    config: bool = True,
    module: bool = True,
    base_dir: str = None,
    storage_options: str = "{}",
):
    """
    Get a summary of the pipeline.

    Args:
        pipeline_name (str, optional): The name of the pipeline.
        show (bool, optional): Whether to show the summary. Defaults to True.
        base_dir (str, optional): The base path of the pipeline. Defaults to "".
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None".
    """
    storage_options = eval(storage_options) if storage_options is not None else {}
    summary = get_pipeline_summary_(
        name=pipeline_name,
        config=config,
        module=module,
        base_dir=base_dir,
        storage_options=storage_options,
    )
    return summary


@app.command()
def show_pipeline_summary(
    pipeline_name: str = None,
    config: bool = True,
    module: bool = True,
    base_dir: str = None,
    storage_options: str = "{}",
):
    """
    Get a summary of the pipeline.

    Args:
        pipeline_name (str, optional): The name of the pipeline.
        show (bool, optional): Whether to show the summary. Defaults to True.
        base_dir (str, optional): The base path of the pipeline. Defaults to "".
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None".
    """
    storage_options = eval(storage_options) if storage_options is not None else {}
    summary = show_pipeline_summary_(
        name=pipeline_name,
        config=config,
        module=module,
        base_dir=base_dir,
        storage_options=storage_options,
    )
    return summary


@app.command()
def start_mqtt_listener(
    pipeline_name: str,
    topic: str = "#",
    host: str = "localhost",
    port: int = 1883,
    user: str = None,
    pw: str = None,
    inputs: str = None,
    final_vars: str = None,
    executor: str = None,
    with_tracker: bool = False,
    with_opentelemetry: bool = False,
    base_dir: str = None,
    storage_options: str = None,
    reload: bool = False,
    result_expiration_time: float = 0.0,
    as_job: bool = False,
    background: bool = False,
):
    """
    Start the MQTT listener.

    Args:
        pipeline_name (str): The name of the pipeline to run.
        topic (str, optional): The MQTT topic to listen to. Defaults to "#".
        host (str, optional): The MQTT host. Defaults to "localhost".
        port (int, optional): The MQTT port. Defaults to 1883.
        user (str, optional): The MQTT username. Defaults to None.
        pw (str, optional): The MQTT password. Defaults to None.
        inputs (str, optional): The inputs for the pipeline. Defaults to None.
        final_vars (list, optional): The final variables for the pipeline. Defaults to None.
        executor (str, optional): The executor to use for the pipeline. Defaults to None.
        with_tracker (bool, optional): Whether to use a tracker for the pipeline. Defaults to False.
        with_opentelemetry (bool, optional): Whether to use OpenTelemetry for the pipeline. Defaults to False.
        base_dir (str, optional): The base path for the pipeline. Defaults to None.
        storage_options (str, optional): The filesystem storage options for the task. Defaults to None.
        reload (bool, optional): Whether to reload the pipeline. Defaults to False.
        result_expiration_time (float, optional): The result expiration time for the pipeline. Defaults to 0.0.
        as_job (bool, optional): Whether to run the pipeline as a job. Defaults to False.
        background (bool, optional): Whether to run the listener in the background. Defaults to e.
    """
    storage_options = eval(storage_options) if storage_options is not None else {}
    start_mqtt_listener_(
        name=pipeline_name,
        topic=topic,
        host=host,
        port=port,
        user=user,
        pw=pw,
        inputs=inputs,
        final_vars=final_vars,
        executor=executor,
        with_tracker=with_tracker,
        with_opentelemetry=with_opentelemetry,
        base_dir=base_dir,
        storage_options=storage_options,
        reload=reload,
        result_expiration_time=result_expiration_time,
        as_job=as_job,
        background=background,
    )


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
