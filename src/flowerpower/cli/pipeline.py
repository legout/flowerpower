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
from ..pipeline import PipelineManager
from .utils import parse_dict_or_list_param, parse_param_dict

# Optional imports
if importlib.util.find_spec("apscheduler"):
    from .scheduler import get_schedule_manager
    from .scheduler import start_worker as start_worker_
else:
    get_schedule_manager = None
    start_worker_ = None


app = typer.Typer(help="Pipeline management commands")


@app.command()
def run(
    name: str,
    executor: str = "local",
    base_dir: str | None = None,
    inputs: str | None = None,
    final_vars: str | None = None,
    with_tracker: bool = False,
    reload: bool = False,
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
        with_tracker: Enable tracking
        reload: Reload pipeline before running
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
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    # run_pipeline_(
    #     name=name,
    #     executor=executor,
    #     base_dir=base_dir,
    #     inputs=parsed_inputs,
    #     final_vars=parsed_final_vars,
    #     with_tracker=with_tracker,
    #     reload=reload,
    #     storage_options=parsed_storage_options or {},
    # )
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.run(
            name=name,
            executor=executor,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            with_tracker=with_tracker,
            reload=reload,
        )


@app.command()
def run_job(
    name: str,
    executor: str = "local",
    base_dir: str | None = None,
    inputs: str | None = None,
    final_vars: str | None = None,
    with_tracker: bool = False,
    reload: bool = False,
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
        with_tracker: Enable tracking
        reload: Reload pipeline before running
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
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.run_job(
            name=name,
            executor=executor,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            with_tracker=with_tracker,
            reload=reload,
        )


@app.command()
def add_job(
    name: str,
    executor: str = "local",
    base_dir: str | None = None,
    inputs: str | None = None,
    final_vars: str | None = None,
    with_tracker: bool = False,
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
        with_tracker: Enable tracking
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
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    storage_options = (parsed_storage_options or {},)

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.add_job(
            name=name,
            executor=executor,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            with_tracker=with_tracker,
        )


@app.command()
def schedule(
    name: str,
    executor: str = "local",
    base_dir: str | None = None,
    type: str = "cron",
    inputs: str | None = None,
    final_vars: str | None = None,
    with_tracker: bool = False,
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
):
    """
    Schedule a pipeline with various configuration options.

    Supports flexible input parsing for inputs, final_vars, and storage_options
    """
    if get_schedule_manager is None:
        raise ValueError("APScheduler not installed. Please install it first.")

    # Parse inputs
    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
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

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        id_ = manager.schedule(
            name=name,
            executor=executor,
            type=type,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
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
def add(
    name: str,
    base_dir: str | None = None,
    pipeline_config: str | None = None,
    pipeline_file: str | None = None,
    overwrite: bool = False,
    storage_options: str | None = None,
):
    """
    Add an existing pipeline.

    Args:
        name: Name of the pipeline to add
        base_dir: Base directory for the pipeline
        pipeline_config: Pipeline configuration as JSON, dict string, key=value pairs or path
        pipeline_file: path to the Pipeline file to add
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    pipeline add my_pipeline
    """

    parsed_pipeline_config = parse_dict_or_list_param(pipeline_config, "dict")
    if pipeline_file is not None:
        parsed_pipeline_config = pipeline_config
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    # add_pipeline_(
    #     name=name,
    #     base_dir=base_dir,
    #     description=description,
    #     storage_options=parsed_storage_options or {},
    # )
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.add(
            name=name,
            pipeline_config=parsed_pipeline_config,
            pipeline_file=pipeline_file,
            overwrite=overwrite,
        )


@app.command()
def delete(
    name: str,
    base_dir: str | None = None,
    remove_modules: bool = False,
    storage_options: str | None = None,
):
    """
    Delete the specified pipeline.

    Args:
        name: Name of the pipeline to delete
        base_dir: Base directory for the pipeline
        remove_modules: Remove associated modules
        storage_options: Storage options as JSON, dict string, or key=value pairs

    Examples:
    pipeline delete my_pipeline
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.delete(name=name, remove_modules=remove_modules)


@app.command()
def show_dag(
    name: str, base_dir: str | None = None, storage_options: str | None = None
):
    """
    Show the DAG of the specified pipeline.

    Args:
        name: Name of the pipeline to show
        base_dir: Base directory for the pipeline

    Examples:
    pipeline show-dag my_pipeline
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.show_dag(name=name)


@app.command()
def save_dag(
    name: str, base_dir: str | None = None, storage_options: str | None = None
):
    """
    Save the DAG of the specified pipeline.

    Args:
        name: Name of the pipeline to save
        base_dir: Base directory for the pipeline

    Examples:
    pipeline save-dag my_pipeline
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.save_dag(name=name)


@app.command()
def show_pipelines(base_dir: str | None = None, storage_options: str | None = None):
    """
    List all available pipelines.

    Args:
        base_dir: Base directory for the pipelines

    Examples:
    pipeline list-pipelines
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    # all_pipelines_(base_dir=base_dir, storage_options=parsed_storage_options or {})
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.show_pipelines()


@app.command()
def show_summary(
    name: str,
    config: bool = True,
    module: bool = True,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Show the summary of the specified pipeline.

    Args:
        name: Name of the pipeline to show
        base_dir: Base directory for the pipeline

    Examples:
    pipeline show-summary my_pipeline
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    # show_pipeline_summary_(
    #     name=name,
    #     config=config,
    #     module=module,
    #     base_dir=base_dir,
    #     storage_options=parsed_storage_options or {},
    # )
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.show_summary(name=name, config=config, module=module)


@app.command()
def get_summary(
    name: str,
    config: bool = True,
    module: bool = True,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Get the summary of the specified pipeline.

    Args:
        name: Name of the pipeline to get
        base_dir: Base directory for the pipeline

    Examples:
    pipeline get-summary my_pipeline
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    # get_pipeline_summary_(
    #     name=name,
    #     config=config,
    #     module=module,
    #     base_dir=base_dir,
    #     storage_options=parsed_storage_options or {},
    # )
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
    ) as manager:
        manager.get_summary(name=name)
