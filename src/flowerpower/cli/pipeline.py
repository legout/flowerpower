# Import necessary libraries
import datetime as dt

import duration_parser
import typer
from loguru import logger
from typing_extensions import Annotated

from ..pipeline.manager import HookType, PipelineManager
from ..utils.logging import setup_logging
from .utils import parse_dict_or_list_param  # , parse_param_dict

setup_logging()

app = typer.Typer(help="Pipeline management commands")


@app.command()
def run(
    name: str = typer.Argument(..., help="Name of the pipeline to run"),
    executor: str | None = typer.Option(
        None, help="Executor to use for running the pipeline"
    ),
    base_dir: str | None = typer.Option(None, help="Base directory for the pipeline"),
    inputs: str | None = typer.Option(
        None, help="Input parameters as JSON, dict string, or key=value pairs"
    ),
    final_vars: str | None = typer.Option(None, help="Final variables as JSON or list"),
    config: str | None = typer.Option(
        None, help="Config for the hamilton pipeline executor"
    ),
    cache: str | None = typer.Option(
        None, help="Cache configuration as JSON or dict string"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    with_adapter: str | None = typer.Option(
        None, help="Adapter configuration as JSON or dict string"
    ),
    max_retries: int = typer.Option(
        0, help="Maximum number of retry attempts on failure"
    ),
    retry_delay: float = typer.Option(
        1.0, help="Base delay between retries in seconds"
    ),
    jitter_factor: float = typer.Option(
        0.1, help="Random factor applied to delay for jitter (0-1)"
    ),
):
    """
    Run a pipeline immediately.

    This command executes a pipeline with the specified configuration and inputs.
    The pipeline will run synchronously, and the command will wait for completion.

    Args:
        name: Name of the pipeline to run
        executor: Type of executor to use
        base_dir: Base directory containing pipelines and configurations
        inputs: Input parameters for the pipeline
        final_vars: Final variables to request from the pipeline
        config: Configuration for the Hamilton executor
        cache: Cache configuration for improved performance
        storage_options: Options for storage backends
        log_level: Set the logging level
        with_adapter: Configuration for adapters like trackers or monitors
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Base delay between retries in seconds
        jitter_factor: Random factor applied to delay for jitter (0-1)

    Examples:
        # Run a pipeline with default settings
        $ pipeline run my_pipeline

        # Run with custom inputs
        $ pipeline run my_pipeline --inputs '{"data_path": "data/myfile.csv", "limit": 100}'

        # Specify which final variables to calculate
        $ pipeline run my_pipeline --final-vars '["output_table", "summary_metrics"]'

        # Configure caching
        $ pipeline run my_pipeline --cache '{"type": "memory", "ttl": 3600}'

        # Use a different executor
        $ pipeline run my_pipeline --executor distributed

        # Enable adapters for monitoring/tracking
        $ pipeline run my_pipeline --with-adapter '{"tracker": true, "opentelemetry": true}'

        # Set a specific logging level
        $ pipeline run my_pipeline --log-level debug

        # Configure automatic retries on failure
        $ pipeline run my_pipeline --max-retries 3 --retry-delay 2.0 --jitter-factor 0.2
    """
    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_config = parse_dict_or_list_param(config, "dict")
    parsed_cache = parse_dict_or_list_param(cache, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    parsed_with_adapter = parse_dict_or_list_param(with_adapter, "dict")

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        _ = manager.run(
            name=name,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            config=parsed_config,
            cache=parsed_cache,
            executor_cfg=executor,
            with_adapter_cfg=parsed_with_adapter,
            max_retries=max_retries,
            retry_delay=retry_delay,
            jitter_factor=jitter_factor,
        )
        logger.info(f"Pipeline '{name}' finished running.")


@app.command()
def run_job(
    name: str = typer.Argument(..., help="Name or ID of the pipeline job to run"),
    executor: str | None = typer.Option(
        None, help="Executor to use for running the job"
    ),
    base_dir: str | None = typer.Option(None, help="Base directory for the pipeline"),
    inputs: str | None = typer.Option(
        None, help="Input parameters as JSON, dict string, or key=value pairs"
    ),
    final_vars: str | None = typer.Option(None, help="Final variables as JSON or list"),
    config: str | None = typer.Option(
        None, help="Config for the hamilton pipeline executor"
    ),
    cache: str | None = typer.Option(
        None, help="Cache configuration as JSON or dict string"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    with_adapter: str | None = typer.Option(
        None, help="Adapter configuration as JSON or dict string"
    ),
    max_retries: int = typer.Option(
        0, help="Maximum number of retry attempts on failure"
    ),
    retry_delay: float = typer.Option(
        1.0, help="Base delay between retries in seconds"
    ),
    jitter_factor: float = typer.Option(
        0.1, help="Random factor applied to delay for jitter (0-1)"
    ),
):
    """
    Run a specific pipeline job.

    This command runs an existing job by its ID. The job should have been previously
    added to the system via the add-job command or through scheduling.

    Args:
        name: Job ID to run
        executor: Type of executor to use (maps to executor_cfg in manager)
        base_dir: Base directory containing pipelines and configurations
        inputs: Input parameters for the pipeline
        final_vars: Final variables to request from the pipeline
        config: Configuration for the Hamilton executor
        cache: Cache configuration
        storage_options: Options for storage backends
        log_level: Set the logging level
        with_adapter: Configuration for adapters like trackers or monitors
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Base delay between retries in seconds
        jitter_factor: Random factor applied to delay for jitter (0-1)

    Examples:
        # Run a job with a specific ID
        $ pipeline run-job job-123456

        # Run a job with custom inputs
        $ pipeline run-job job-123456 --inputs '{"data_path": "data/myfile.csv"}'

        # Specify a different executor
        $ pipeline run-job job-123456 --executor local

        # Use caching for better performance
        $ pipeline run-job job-123456 --cache '{"type": "memory"}'

        # Configure adapters for monitoring
        $ pipeline run-job job-123456 --with-adapter '{"tracker": true, "opentelemetry": false}'

        # Set up automatic retries for resilience
        $ pipeline run-job job-123456 --max-retries 3 --retry-delay 2.0
    """
    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_config = parse_dict_or_list_param(config, "dict")
    parsed_cache = parse_dict_or_list_param(cache, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    parsed_with_adapter = parse_dict_or_list_param(with_adapter, "dict")

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        _ = manager.run_job(
            name=name,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            config=parsed_config,
            cache=parsed_cache,
            executor_cfg=executor,
            with_adapter_cfg=parsed_with_adapter,
            max_retries=max_retries,
            retry_delay=retry_delay,
            jitter_factor=jitter_factor,
        )
        logger.info(f"Job '{name}' finished running.")


@app.command()
def add_job(
    name: str = typer.Argument(..., help="Name of the pipeline to add as a job"),
    executor: str | None = typer.Option(
        None, help="Executor to use for running the job"
    ),
    base_dir: str | None = typer.Option(None, help="Base directory for the pipeline"),
    inputs: str | None = typer.Option(
        None, help="Input parameters as JSON, dict string, or key=value pairs"
    ),
    final_vars: str | None = typer.Option(None, help="Final variables as JSON or list"),
    config: str | None = typer.Option(
        None, help="Config for the hamilton pipeline executor"
    ),
    cache: str | None = typer.Option(
        None, help="Cache configuration as JSON or dict string"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    with_adapter: str | None = typer.Option(
        None, help="Adapter configuration as JSON or dict string"
    ),
    run_at: str | None = typer.Option(None, help="Run at a specific time (ISO format)"),
    run_in: str | None = typer.Option(
        None, help="Run in a specific interval (e.g., '5m', '1h', '12m34s')"
    ),
    max_retries: int = typer.Option(
        3, help="Maximum number of retry attempts on failure"
    ),
    retry_delay: float = typer.Option(
        1.0, help="Base delay between retries in seconds"
    ),
    jitter_factor: float = typer.Option(
        0.1, help="Random factor applied to delay for jitter (0-1)"
    ),
):
    """
    Add a pipeline job to the queue.

    This command adds a job to the queue for later execution. The job is based on
    an existing pipeline with customized inputs and configuration.

    Args:
        name: Pipeline name to add as a job
        executor: Type of executor to use
        base_dir: Base directory containing pipelines and configurations
        inputs: Input parameters for the pipeline
        final_vars: Final variables to request from the pipeline
        config: Configuration for the Hamilton executor
        cache: Cache configuration
        storage_options: Options for storage backends
        log_level: Set the logging level
        with_adapter: Configuration for adapters like trackers or monitors
        run_at: Run the job at a specific time (ISO format)
        run_in: Run the job in a specific interval (e.g., '5m', '1h')
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Base delay between retries in seconds
        jitter_factor: Random factor applied to delay for jitter (0-1)

    Examples:
        # Add a basic job
        $ pipeline add-job my_pipeline

        # Add a job with custom inputs
        $ pipeline add-job my_pipeline --inputs '{"data_path": "data/myfile.csv"}'

        # Specify final variables to calculate
        $ pipeline add-job my_pipeline --final-vars '["output_table", "metrics"]'

        # Configure caching
        $ pipeline add-job my_pipeline --cache '{"type": "memory", "ttl": 3600}'

        # Use a specific log level
        $ pipeline add-job my_pipeline --log-level debug

        # Configure automatic retries for resilience
        $ pipeline add-job my_pipeline --max-retries 5 --retry-delay 2.0 --jitter-factor 0.2
    """
    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_config = parse_dict_or_list_param(config, "dict")
    parsed_cache = parse_dict_or_list_param(cache, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    parsed_with_adapter = parse_dict_or_list_param(with_adapter, "dict")
    run_at = dt.datetime.fromisoformat(run_at) if run_at else None
    run_in = duration_parser.parse(run_in) if run_in else None

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        job_id = manager.add_job(
            name=name,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            config=parsed_config,
            cache=parsed_cache,
            executor_cfg=executor,
            with_adapter_cfg=parsed_with_adapter,
            run_at=run_at,
            run_in=run_in,
            max_retries=max_retries,
            retry_delay=retry_delay,
            jitter_factor=jitter_factor,
        )
        logger.info(f"Job {job_id} added for pipeline '{name}'.")


@app.command()
def schedule(
    name: str = typer.Argument(..., help="Name of the pipeline to schedule"),
    executor: str | None = typer.Option(
        None, help="Executor to use for running the job"
    ),
    base_dir: str | None = typer.Option(None, help="Base directory for the pipeline"),
    inputs: str | None = typer.Option(
        None, help="Input parameters as JSON, dict string, or key=value pairs"
    ),
    final_vars: str | None = typer.Option(None, help="Final variables as JSON or list"),
    config: str | None = typer.Option(
        None, help="Config for the hamilton pipeline executor"
    ),
    cache: str | None = typer.Option(
        None, help="Cache configuration as JSON or dict string"
    ),
    cron: str | None = typer.Option(None, help="Cron expression for scheduling"),
    interval: str | None = typer.Option(
        None, help="Interval for scheduling (e.g., '5m', '1h')"
    ),
    date: str | None = typer.Option(
        None, help="Specific date and time for scheduling (ISO format)"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    with_adapter: str | None = typer.Option(
        None, help="Adapter configuration as JSON or dict string"
    ),
    overwrite: bool = typer.Option(
        False, help="Overwrite existing schedule if it exists"
    ),
    schedule_id: str | None = typer.Option(
        None, help="Custom ID for the schedule (autogenerated if not provided)"
    ),
    max_retries: int = typer.Option(
        3, help="Maximum number of retry attempts on failure"
    ),
    retry_delay: float = typer.Option(
        1.0, help="Base delay between retries in seconds"
    ),
    jitter_factor: float = typer.Option(
        0.1, help="Random factor applied to delay for jitter (0-1)"
    ),
):
    """
    Schedule a pipeline to run at specified times.

    This command schedules a pipeline to run automatically based on various
    scheduling triggers like cron expressions, time intervals, or specific dates.

    Args:
        name: Pipeline name to schedule
        executor: Type of executor to use
        base_dir: Base directory containing pipelines and configurations
        inputs: Input parameters for the pipeline
        final_vars: Final variables to request from the pipeline
        config: Configuration for the Hamilton executor
        cache: Cache configuration
        cron: Cron expression for scheduling (e.g., "0 * * * *")
        interval: Interval for scheduling (e.g., "5m", "1h")
        date: Specific date and time for scheduling (ISO format)
        storage_options: Options for storage backends
        log_level: Set the logging level
        with_adapter: Configuration for adapters like trackers or monitors
        overwrite: Overwrite existing schedule with same ID
        schedule_id: Custom identifier for the schedule
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Base delay between retries in seconds
        jitter_factor: Random factor applied to delay for jitter (0-1)

    Examples:
        # Schedule with cron expression (every hour)
        $ pipeline schedule my_pipeline --trigger-type cron --crontab "0 * * * *"

        # Schedule to run every 15 minutes
        $ pipeline schedule my_pipeline --trigger-type interval --interval_params minutes=15

        # Schedule to run at a specific date and time
        $ pipeline schedule my_pipeline --trigger-type date --date_params run_date="2025-12-31 23:59:59"

        # Schedule with custom inputs and cache settings
        $ pipeline schedule my_pipeline --inputs '{"source": "database"}' --cache '{"type": "redis"}'

        # Create a schedule in paused state
        $ pipeline schedule my_pipeline --crontab "0 9 * * 1-5" --paused

        # Set a custom schedule ID
        $ pipeline schedule my_pipeline --crontab "0 12 * * *" --schedule_id "daily-noon-run"

        # Configure automatic retries for resilience
        $ pipeline schedule my_pipeline --max-retries 5 --retry-delay 2.0 --jitter-factor 0.2
    """
    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_config = parse_dict_or_list_param(config, "dict")
    parsed_cache = parse_dict_or_list_param(cache, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    parsed_with_adapter = parse_dict_or_list_param(with_adapter, "dict")
    interval = duration_parser.parse(interval) if interval else None
    cron = cron if cron else None
    date = dt.datetime.fromisoformat(date) if date else None

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        # Combine common schedule kwargs

        id_ = manager.schedule(
            name=name,
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            config=parsed_config,
            cache=parsed_cache,
            executor_cfg=executor,
            with_adapter_cfg=parsed_with_adapter,
            cron=cron,
            interval=interval,
            date=date,
            overwrite=overwrite,
            schedule_id=schedule_id,
            max_retries=max_retries,
            retry_delay=retry_delay,
            jitter_factor=jitter_factor,
        )

    logger.info(f"Pipeline '{name}' scheduled with ID {id_}.")


@app.command()
def schedule_all(
    executor: str | None = typer.Option(
        None, help="Override executor specified in pipeline configs"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory containing pipelines and configurations"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    overwrite: bool = typer.Option(
        False, help="Overwrite existing schedules if they exist"
    ),
):
    """
    Schedule all pipelines based on their individual configurations.

    This command reads the configuration files for all pipelines in the project
    and schedules them based on their individual scheduling settings. This is useful
    for setting up all scheduled pipelines at once after deployment or system restart.

    Args:
        executor: Override executor specified in pipeline configs
        base_dir: Base directory containing pipelines and configurations
        storage_options: Options for storage backends
        log_level: Set the logging level
        overwrite: Whether to overwrite existing schedules

    Examples:
        # Schedule all pipelines using their configurations
        $ pipeline schedule-all

        # Force overwrite of existing schedules
        $ pipeline schedule-all --overwrite

        # Override executor for all pipelines
        $ pipeline schedule-all --executor distributed

        # Set custom base directory
        $ pipeline schedule-all --base-dir /path/to/project
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        manager.schedule_all(overwrite=overwrite, executor_cfg=executor)
    logger.info("Scheduled all pipelines based on their configurations.")


@app.command()
def new(
    name: str = typer.Argument(..., help="Name of the pipeline to create"),
    base_dir: str | None = typer.Option(None, help="Base directory for the pipeline"),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    overwrite: bool = typer.Option(
        False, help="Overwrite existing pipeline if it exists"
    ),
):
    """
    Create a new pipeline structure.

    This command creates a new pipeline with the necessary directory structure,
    configuration file, and skeleton module file. It prepares all the required
    components for you to start implementing your pipeline logic.

    Args:
        name: Name for the new pipeline
        base_dir: Base directory to create the pipeline in
        storage_options: Options for storage backends
        log_level: Set the logging level
        overwrite: Whether to overwrite existing pipeline with the same name

    Examples:
        # Create a new pipeline with default settings
        $ pipeline new my_new_pipeline

        # Create a pipeline, overwriting if it exists
        $ pipeline new my_new_pipeline --overwrite

        # Create a pipeline in a specific directory
        $ pipeline new my_new_pipeline --base-dir /path/to/project
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        manager.new(name=name, overwrite=overwrite)
    logger.info(f"New pipeline structure created for '{name}'.")


@app.command()
def delete(
    name: str = typer.Argument(..., help="Name of the pipeline to delete"),
    base_dir: str | None = typer.Option(
        None, help="Base directory containing the pipeline"
    ),
    cfg: bool = typer.Option(
        False, "--cfg", "-c", help="Delete only the configuration file"
    ),
    module: bool = typer.Option(
        False, "--module", "-m", help="Delete only the pipeline module"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
):
    """
    Delete a pipeline's configuration and/or module files.

    This command removes a pipeline's configuration file and/or module file from the project.
    If neither --cfg nor --module is specified, both will be deleted.

    Args:
        name: Name of the pipeline to delete
        base_dir: Base directory containing the pipeline
        cfg: Delete only the configuration file
        module: Delete only the pipeline module
        storage_options: Options for storage backends
        log_level: Set the logging level

    Examples:
        # Delete a pipeline (both config and module)
        $ pipeline delete my_pipeline

        # Delete only the configuration file
        $ pipeline delete my_pipeline --cfg

        # Delete only the module file
        $ pipeline delete my_pipeline --module
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    # If neither flag is set, default to deleting both
    delete_cfg = cfg or not (cfg or module)
    delete_module = module or not (cfg or module)

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        manager.delete(name=name, cfg=delete_cfg, module=delete_module)

    deleted_parts = []
    if delete_cfg:
        deleted_parts.append("config")
    if delete_module:
        deleted_parts.append("module")
    logger.info(
        f"Pipeline '{name}' deleted ({', '.join(deleted_parts)})."
        if deleted_parts
        else f"Pipeline '{name}' - nothing specified to delete."
    )


@app.command()
def show_dag(
    name: str = typer.Argument(..., help="Name of the pipeline to visualize"),
    base_dir: str | None = typer.Option(
        None, help="Base directory containing the pipeline"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    format: str = typer.Option(
        "png", help="Output format (e.g., png, svg, pdf). If 'raw', returns object."
    ),
):
    """
    Show the DAG (Directed Acyclic Graph) of a pipeline.

    This command generates and displays a visual representation of the pipeline's
    execution graph, showing how nodes are connected and dependencies between them.

    Args:
        name: Name of the pipeline to visualize
        base_dir: Base directory containing the pipeline
        storage_options: Options for storage backends
        log_level: Set the logging level
        format: Output format for the visualization

    Examples:
        # Show pipeline DAG in PNG format (default)
        $ pipeline show-dag my_pipeline

        # Generate SVG format visualization
        $ pipeline show-dag my_pipeline --format svg

        # Get raw graphviz object
        $ pipeline show-dag my_pipeline --format raw
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    is_raw = format.lower() == "raw"

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        # Manager's show_dag likely handles rendering or returning raw object
        try:
            graph_or_none = manager.show_dag(
                name=name, format=format if not is_raw else "png", raw=is_raw
            )
            if is_raw and graph_or_none:
                print("Graphviz object returned (not rendered):")
                # print(graph_or_none) # Or handle as needed
            elif not is_raw:
                logger.info(
                    f"DAG for pipeline '{name}' displayed/saved (format: {format})."
                )
        except ImportError:
            logger.error(
                "Graphviz is not installed. Cannot show/save DAG. Install with: pip install graphviz"
            )
        except Exception as e:
            logger.error(f"Failed to generate DAG for pipeline '{name}': {e}")


@app.command()
def save_dag(
    name: str = typer.Argument(..., help="Name of the pipeline to visualize"),
    base_dir: str | None = typer.Option(
        None, help="Base directory containing the pipeline"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    format: str = typer.Option("png", help="Output format (e.g., png, svg, pdf)"),
    output_path: str | None = typer.Option(
        None, help="Custom path to save the file (default: <name>.<format>)"
    ),
):
    """
    Save the DAG (Directed Acyclic Graph) of a pipeline to a file.

    This command generates a visual representation of the pipeline's execution graph
    and saves it to a file in the specified format.

    Args:
        name: Name of the pipeline to visualize
        base_dir: Base directory containing the pipeline
        storage_options: Options for storage backends
        log_level: Set the logging level
        format: Output format for the visualization
        output_path: Custom file path to save the output (defaults to pipeline name)

    Examples:
        # Save pipeline DAG in PNG format (default)
        $ pipeline save-dag my_pipeline

        # Save in SVG format
        $ pipeline save-dag my_pipeline --format svg

        # Save to a custom location
        $ pipeline save-dag my_pipeline --output-path ./visualizations/my_graph.png
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        try:
            file_path = manager.save_dag(
                name=name, format=format, output_path=output_path
            )
            logger.info(f"DAG for pipeline '{name}' saved to {file_path}.")
        except ImportError:
            logger.error(
                "Graphviz is not installed. Cannot save DAG. Install with: pip install graphviz"
            )
        except Exception as e:
            logger.error(f"Failed to save DAG for pipeline '{name}': {e}")


@app.command()
def show_pipelines(
    base_dir: str | None = typer.Option(
        None, help="Base directory containing pipelines"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
):
    """
    List all available pipelines in the project.

    This command displays a list of all pipelines defined in the project,
    providing an overview of what pipelines are available to run or schedule.

    Args:
        base_dir: Base directory containing pipelines
        storage_options: Options for storage backends
        log_level: Set the logging level
        format: Output format for the list (table, json, yaml)

    Examples:
        # List all pipelines in table format (default)
        $ pipeline show-pipelines

        # Output in JSON format
        $ pipeline show-pipelines --format json

        # List pipelines from a specific directory
        $ pipeline show-pipelines --base-dir /path/to/project
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        manager.show_pipelines(format=format)


@app.command()
def show_summary(
    name: str | None = typer.Option(
        None, help="Name of specific pipeline to show (all pipelines if not specified)"
    ),
    cfg: bool = typer.Option(True, help="Include configuration details"),
    code: bool = typer.Option(True, help="Include code/module details"),
    project: bool = typer.Option(True, help="Include project context"),
    base_dir: str | None = typer.Option(
        None, help="Base directory containing pipelines"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    to_html: bool = typer.Option(False, help="Output summary as HTML"),
    to_svg: bool = typer.Option(False, help="Output summary as SVG (if applicable)"),
    output_file: str | None = typer.Option(
        None, help="Save output to specified file instead of printing"
    ),
):
    """
    Show summary information for one or all pipelines.

    This command displays detailed information about pipelines including their
    configuration, code structure, and project context. You can view information
    for a specific pipeline or get an overview of all pipelines.

    Args:
        name: Name of specific pipeline to summarize (all if not specified)
        cfg: Include configuration details
        code: Include code/module details
        project: Include project context information
        base_dir: Base directory containing pipelines
        storage_options: Options for storage backends
        log_level: Set the logging level
        to_html: Generate HTML output instead of text
        to_svg: Generate SVG output (where applicable)
        output_file: File path to save the output instead of printing to console

    Examples:
        # Show summary for all pipelines
        $ pipeline show-summary

        # Show summary for a specific pipeline
        $ pipeline show-summary --name my_pipeline

        # Show only configuration information
        $ pipeline show-summary --name my_pipeline --cfg --no-code --no-project

        # Generate HTML report
        $ pipeline show-summary --to-html --output-file pipeline_report.html
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        # Assumes manager.show_summary handles printing/returning formatted output
        summary_output = manager.show_summary(
            name=name,
            cfg=cfg,
            code=code,
            project=project,
            to_html=to_html,
            to_svg=to_svg,
        )

        if summary_output:
            if output_file:
                with open(output_file, "w") as f:
                    f.write(summary_output)
                logger.info(f"Summary saved to {output_file}")
            else:
                print(summary_output)
        # Otherwise, assume manager printed the summary


@app.command()
def add_hook(
    name: str = typer.Argument(..., help="Name of the pipeline to add the hook to"),
    function_name: str = typer.Option(
        ...,
        "--function",
        "-f",
        help="Name of the hook function defined in the pipeline module",
    ),
    type: Annotated[
        HookType, typer.Option(help="Type of hook to add")
    ] = HookType.MQTT_BUILD_CONFIG,
    to: str | None = typer.Option(
        None, help="Target node name or tag (required for node hooks)"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory containing the pipeline"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
):
    """
    Add a hook to a pipeline configuration.

    This command adds a hook function to a pipeline's configuration. Hooks are functions
    that are called at specific points during pipeline execution to perform additional
    tasks like logging, monitoring, or data validation.

    Args:
        name: Name of the pipeline to add the hook to
        function_name: Name of the hook function (must be defined in the pipeline module)
        type: Type of hook (determines when the hook is called during execution)
        to: Target node or tag (required for node-specific hooks)
        base_dir: Base directory containing the pipeline
        storage_options: Options for storage backends
        log_level: Set the logging level

    Examples:
        # Add a post-run hook
        $ pipeline add-hook my_pipeline --function log_results

        # Add a pre-run hook
        $ pipeline add-hook my_pipeline --function validate_inputs --type PRE_RUN

        # Add a node-specific hook (executed before a specific node runs)
        $ pipeline add-hook my_pipeline --function validate_data --type NODE_PRE_EXECUTE --to data_processor

        # Add a hook for all nodes with a specific tag
        $ pipeline add-hook my_pipeline --function log_metrics --type NODE_POST_EXECUTE --to @metrics
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    # Validate 'to' argument for node hooks
    if type in (HookType.NODE_PRE_EXECUTE, HookType.NODE_POST_EXECUTE) and not to:
        raise typer.BadParameter(
            "The '--to' option (target node/tag) is required for node hooks."
        )

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    ) as manager:
        try:
            manager.add_hook(
                name=name,
                type=type,
                to=to,
                function_name=function_name,
            )
            logger.info(
                f"Hook '{function_name}' added to pipeline '{name}' (type: {type.value})."
            )
        except Exception as e:
            logger.error(f"Failed to add hook to pipeline '{name}': {e}")
