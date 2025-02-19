import importlib.util

import typer
from loguru import logger

# Import your existing pipeline functions
# from ..pipeline import (
#     add as add_pipeline_,
#     add_job as add_pipeline_job_,
#     all_pipelines as all_pipelines_,
#     delete as delete_pipeline_,
#     get_summary as get_pipeline_summary_,
#     new as new_pipeline_,
#     run as run_pipeline_,
#     run_job as run_pipeline_job_,
#     schedule as schedule_pipeline_,
#     save_dag as save_pipeline_dag_,
#     show_dag as show_pipeline_dag_,
#     show_summary as show_pipeline_summary_,
#     # start_mqtt_listener as start_mqtt_listener_,
# )
from ..pipeline import Pipeline, PipelineManager
from .utils import parse_dict_or_list_param, parse_param_dict

# Optional imports
if importlib.util.find_spec("apscheduler"):
    from ..scheduler import get_schedule_manager
    from ..scheduler import start_worker as start_worker_
else:
    get_schedule_manager = None
    start_worker_ = None


app = typer.Typer(help="Pipeline management commands")


@app.command()
def run(
    name: str,
    executor: str | None = None,
    base_dir: str | None = None,
    inputs: str | None = None,
    final_vars: str | None = None,
    config: str | None = None,
    with_tracker: bool = False,
    with_opentelemetry: bool = False,
    with_progressbar: bool = False,
    storage_options: str | None = None,
):
    """
    Run the specified pipeline.

    Args:
        name: Name of the pipeline to run
        executor: Executor to use
        base_dir: Base directory for the pipeline
        inputs: Input parameters as JSON, dict string, or key=value pairs
        final_vars: Final variables as JSON or list
        config: Config for the hamilton pipeline executor
        with_tracker: Enable tracking with hamilton ui
        with_opentelemetry: Enable OpenTelemetry tracing
        with_progressbar: Enable progress bar
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    # JSON inputs
    pipeline run my_pipeline --inputs '{"key": "value"}'

    # Dict string inputs
    pipeline run my_pipeline --inputs "{'key': 'value'}"

    # Key-value pair inputs
    pipeline run my_pipeline --inputs 'key1=value1,key2=value2'

    # List final vars
    pipeline run my_pipeline --final-vars '["var1", "var2"]'

    # Storage options
    pipeline run my_pipeline --storage-options 'endpoint=http://localhost,use_ssl=true'
    """
    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_config = parse_dict_or_list_param(config, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with Pipeline(
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as pipeline:
        pipeline.run(
            executor=executor,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            config=parsed_config,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
        )


@app.command()
def run_job(
    name: str,
    executor: str | None = None,
    base_dir: str | None = None,
    inputs: str | None = None,
    final_vars: str | None = None,
    config: str | None = None,
    with_tracker: bool = False,
    with_opentelemetry: bool = False,
    with_progressbar: bool = False,
    storage_options: str | None = None,
):
    """
    Run the specified pipeline job.

    Args:
        name: Name of the pipeline job to run
        executor: Executor to use
        base_dir: Base directory for the pipeline
        inputs: Input parameters as JSON, dict string, or key=value pairs
        final_vars: Final variables as JSON or list
        config: Config for the hamilton pipeline executor
        with_tracker: Enable tracking with hamilton ui
        with_opentelemetry: Enable OpenTelemetry tracing
        with_progressbar: Enable progress bar
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    # JSON inputs
    pipeline run-job 123 --inputs '{"key": "value"}'

    # Dict string inputs
    pipeline run-job 123 --inputs "{'key': 'value'}"

    # Key-value pair inputs
    pipeline run-job 123 --inputs 'key1=value1,key2=value2'

    # List final vars
    pipeline run-job 123 --final-vars '["var1", "var2"]'

    # Storage options
    pipeline run-job 123 --storage-options 'endpoint=http://localhost,use_ssl=true'
    """
    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_config = parse_dict_or_list_param(config, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with Pipeline(
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as pipeline:
        pipeline.run_job(
            executor=executor,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            config=parsed_config,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
        )


@app.command()
def add_job(
    name: str,
    executor: str | None = None,
    base_dir: str | None = None,
    inputs: str | None = None,
    final_vars: str | None = None,
    config: str | None = None,
    with_tracker: bool = False,
    with_opentelemetry: bool = False,
    with_progressbar: bool = False,
    storage_options: str | None = None,
):
    """
    Add a job to the specified pipeline.

    Args:
        name: Name of the pipeline to add as job
        executor: Executor to use
        base_dir: Base directory for the pipeline
        inputs: Input parameters as JSON, dict string, or key=value pairs
        final_vars: Final variables as JSON or list
        config: Config for the hamilton pipeline executor
        with_tracker: Enable tracking with hamilton ui
        with_opentelemetry: Enable OpenTelemetry tracing
        with_progressbar: Enable progress bar
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    # JSON inputs
    pipeline add-job my_pipeline --inputs '{"key": "value"}'

    # Dict string inputs
    pipeline add-job my_pipeline --inputs "{'key': 'value'}"

    # Key-value pair inputs
    pipeline add-job my_pipeline --inputs 'key1=value1,key2=value2'

    # List final vars
    pipeline add-job my_pipeline --final-vars '["var1", "var2"]'

    # Storage options
    pipeline add-job my_pipeline --storage-options 'endpoint=http://localhost,use_ssl=true'
    """
    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_config = parse_dict_or_list_param(config, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    storage_options = (parsed_storage_options or {},)

    with Pipeline(
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as pipeline:
        pipeline.add_job(
            executor=executor,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            config=parsed_config,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
        )


@app.command()
def schedule(
    name: str,
    executor: str | None = None,
    base_dir: str | None = None,
    trigger_type: str = "cron",
    inputs: str | None = None,
    final_vars: str | None = None,
    config: str | None = None,
    with_tracker: bool = False,
    with_opentelemetry: bool = False,
    with_progressbar: bool = False,
    paused: bool = False,
    coalesce: str = "latest",
    misfire_grace_time: float | None = None,
    max_jitter: float | None = None,
    max_running_jobs: int | None = None,
    conflict_policy: str = "do_nothing",
    crontab: str | None = None,
    cron_params: str | None = None,
    interval_params: str | None = None,
    calendarinterval_params: str | None = None,
    date_params: str | None = None,
    storage_options: str | None = None,
    overwrite: bool = False,
):
    """
    Schedule a pipeline with various configuration options.

    Args:
        name: Name of the pipeline to schedule
        executor: Executor to use
        base_dir: Base directory for the pipeline
        trigger_type: Type of schedule
        inputs: Input parameters as JSON, dict string, or key=value pairs
        final_vars: Final variables as JSON or list
        config: Config for the hamilton pipeline executor
        with_tracker: Enable tracking with hamilton ui
        with_opentelemetry: Enable OpenTelemetry tracing
        with_progressbar: Enable progress bar
        paused: Start the job in paused state
        coalesce: Coalesce policy
        misfire_grace_time: Misfire grace time
        max_jitter: Maximum jitter
        max_running_jobs: Maximum running jobs
        conflict_policy: Conflict policy
        crontab: Crontab expression
        cron_params: Cron parameters as JSON or key=value pairs
        interval_params: Interval parameters as JSON or key=value pairs
        calendarinterval_params: Calendar interval parameters as JSON or key=value pairs
        date_params: Date parameters as JSON or key=value pairs
        storage_options: Storage options as JSON, dict string, or key=value pairs
        overwrite: Overwrite existing schedule

    Examples:
    # JSON inputs
    pipeline schedule my_pipeline --inputs '{"key": "value"}'

    # Dict string inputs
    pipeline schedule my_pipeline --inputs "{'key': 'value'}"

    # Key-value pair inputs
    pipeline schedule my_pipeline --inputs 'key1=value1,key2=value2'

    # List final vars
    pipeline schedule my_pipeline --final-vars '["var1", "var2"]'

    # Storage options
    pipeline schedule my_pipeline --storage-options 'endpoint=http://localhost,use_ssl=true'

    # Cron schedule
    pipeline schedule my_pipeline --trigger-type cron --crontab '0 0 * * *'

    # Interval schedule
    pipeline schedule my_pipeline --trigger-type interval --interval_params minutes=1

    # Calendar interval schedule
    pipeline schedule my_pipeline --trigger-type calendarinterval --calendarinterval_params month=5

    # Date schedule
    pipeline schedule my_pipeline --trigger-type date --date_params run_date='2021-01-01 12:00:01'

    """
    if get_schedule_manager is None:
        raise ValueError("APScheduler not installed. Please install it first.")

    # Parse inputs
    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_config = parse_dict_or_list_param(config, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    # Parse various parameter dictionaries
    cron_params_dict = parse_param_dict(cron_params)
    interval_params_dict = parse_param_dict(interval_params)
    calendarinterval_params_dict = parse_param_dict(calendarinterval_params)
    date_params_dict = parse_param_dict(date_params)

    # Combine all parameter dictionaries
    kwargs = {
        **cron_params_dict,
        **interval_params_dict,
        **calendarinterval_params_dict,
        **date_params_dict,
    }

    # Add crontab if provided
    if crontab is not None:
        kwargs["crontab"] = crontab

    # Convert numeric parameters
    for key in ["weeks", "days", "hours", "minutes", "seconds"]:
        if key in kwargs:
            try:
                kwargs[key] = float(kwargs[key])
            except ValueError:
                logger.warning(f"Could not convert {key} to float: {kwargs[key]}")

    with Pipeline(
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as pipeline:
        id_ = pipeline.schedule(
            executor=executor,
            trigger_type=trigger_type,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            config=parsed_config,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
            paused=paused,
            coalesce=coalesce,
            misfire_grace_time=misfire_grace_time,
            max_jitter=max_jitter,
            max_running_jobs=max_running_jobs,
            conflict_policy=conflict_policy,
            overwrite=overwrite,
            **kwargs,
        )

    logger.info(f"Job {id_} scheduled.")


@app.command()
def schedule_all(
    executor: str | None = None,
    base_dir: str | None = None,
    inputs: str | None = None,
    final_vars: str | None = None,
    config: str | None = None,
    with_tracker: bool = False,
    with_opentelemetry: bool = False,
    with_progressbar: bool = False,
    paused: bool = False,
    coalesce: str = "latest",
    misfire_grace_time: float | None = None,
    max_jitter: float | None = None,
    max_running_jobs: int | None = None,
    conflict_policy: str = "do_nothing",
    storage_options: str | None = None,
    overwrite: bool = False,
):
    """
    Schedule all pipelines using the pipeline specific configurations (`conf/pipelines/<name>.yml`).

    Args:
        executor: Executor to use
        base_dir: Base directory for the pipeline
        inputs: Input parameters as JSON, dict string, or key=value pairs
        final_vars: Final variables as JSON or list
        config: Config for the hamilton pipeline executor
        with_tracker: Enable tracking with hamilton ui
        with_opentelemetry: Enable OpenTelemetry tracing
        with_progressbar: Enable progress bar
        paused: Start the job in paused state
        coalesce: Coalesce policy
        misfire_grace_time: Misfire grace time
        max_jitter: Maximum jitter
        max_running_jobs: Maximum running jobs
        conflict_policy: Conflict policy
        storage_options: Storage options as JSON, dict string, or key=value pairs
        overwrite: Overwrite existing schedule

    Examples:
    pipeline schedule-all
    """
    if get_schedule_manager is None:
        raise ValueError("APScheduler not installed. Please install it first.")

    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.schedule_all(
            executor=executor,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
            paused=paused,
            coalesce=coalesce,
            misfire_grace_time=misfire_grace_time,
            max_jitter=max_jitter,
            max_running_jobs=max_running_jobs,
            conflict_policy=conflict_policy,
            overwrite=overwrite,
        )


@app.command()
def new(
    name: str,
    base_dir: str | None = None,
    storage_options: str | None = None,
    overwrite: bool = False,
):
    """
    Create a new pipeline.

    Args:
        name: Name of the new pipeline
        base_dir: Base directory for the new pipeline
        overwrite: Overwrite existing pipeline
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    pipeline new my_pipeline
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.new(name=name, overwrite=overwrite)


@app.command()
def delete(
    name: str,
    base_dir: str | None = None,
    cfg: bool = False,
    module: bool = False,
    storage_options: str | None = None,
):
    """
    Delete the specified pipeline.

    Args:
        name: Name of the pipeline to delete
        base_dir: Base directory for the pipeline
        cfg: Remove associated configuration
        module: Remove associated module
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    pipeline delete my_pipeline
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with Pipeline(
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as pipeline:
        pipeline.delete(cfg=cfg, module=module)


@app.command()
def show_dag(
    name: str, base_dir: str | None = None, storage_options: str | None = None
):
    """
    Show the DAG of the specified pipeline.

    Args:
        name: Name of the pipeline to show
        base_dir: Base directory for the pipeline
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    pipeline show-dag my_pipeline
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with Pipeline(
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as pipeline:
        pipeline.show_dag()


@app.command()
def save_dag(
    name: str, base_dir: str | None = None, storage_options: str | None = None
):
    """
    Save the DAG of the specified pipeline.

    Args:
        name: Name of the pipeline to save
        base_dir: Base directory for the pipeline
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    pipeline save-dag my_pipeline
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with Pipeline(
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as pipeline:
        pipeline.save_dag()


@app.command()
def show_pipelines(base_dir: str | None = None, storage_options: str | None = None):
    """
    List all available pipelines.

    Args:
        base_dir: Base directory for the pipelines
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    pipeline list-pipelines
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.show_pipelines()


@app.command()
def show_summary(
    name: str | None = None,
    cfg: bool = True,
    module: bool = True,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Show the summary of the specified pipeline.

    Args:
        name: Name of the pipeline to show
        base_dir: Base directory for the pipeline
        cfg: Show configuration
        module: Show module information
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    pipeline show-summary my_pipeline
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.show_summary(name=name, cfg=cfg, module=module)
