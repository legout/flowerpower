# Import necessary libraries
import typer
from loguru import logger
from typing_extensions import Annotated, Callable, Any
from typing import Dict, List, Optional, Tuple

from ..flowerpower import FlowerPowerProject
from ..pipeline.manager import HookType, PipelineManager
from ..cfg.pipeline.run import RunConfig, RetryConfig
from ..utils.logging import setup_logging
from .utils import parse_dict_or_list_param

setup_logging()

app = typer.Typer(help="Pipeline management commands")


# Note: common_options decorator removed as it was causing TypeError
# Options are now defined directly in each function's parameter list


def parse_common_options(
    base_dir: Optional[str] = None,
    storage_options: Optional[str] = None,
    log_level: Optional[str] = None,
) -> Tuple[Optional[str], Dict, Optional[str]]:
    """Parse common CLI options and return processed values."""
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
    # Ensure storage_options is always a dict, not None or list
    if parsed_storage_options is None:
        parsed_storage_options = {}
    elif not isinstance(parsed_storage_options, dict):
        # This should not happen with param_type="dict", but being safe
        logger.warning(f"Expected dict for storage_options, got {type(parsed_storage_options)}")
        parsed_storage_options = {}
    return base_dir, parsed_storage_options, log_level


@app.command()
def run(
    name: str = typer.Argument(..., help="Name of the pipeline to run"),
    executor: str | None = typer.Option(
        None, help="Executor to use for running the pipeline"
    ),
    executor_cfg: str | None = typer.Option(
        None,
        help='Executor configuration as JSON/dict string (e.g. "{\"type\":\"threadpool\",\"max_workers\":4}")',
    ),
    executor_max_workers: int | None = typer.Option(
        None, help="Convenience flag: set executor max_workers"
    ),
    executor_num_cpus: int | None = typer.Option(
        None, help="Convenience flag: set executor num_cpus"
    ),
    base_dir: str | None = typer.Option(None, help="Base directory for the pipeline"),
    inputs: str | None = typer.Option(
        None, help="Input parameters as JSON, dict string, or key=value pairs"
    ),
    final_vars: str | None = typer.Option(
        None,
        "--final-vars",
        "--outputs",
        "-o",
        help="Final variables as JSON or list",
    ),
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
        0, help="Maximum number of retry attempts on failure (0 to disable retries)"
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
    # Parse parameters with proper type handling
    parsed_inputs = parse_dict_or_list_param(inputs, "dict") or {}
    parsed_config = parse_dict_or_list_param(config, "dict") or {}
    parsed_cache = parse_dict_or_list_param(cache, "dict") or {}
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list") or []
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}
    parsed_with_adapter = parse_dict_or_list_param(with_adapter, "dict") or {}
    parsed_executor_cfg = parse_dict_or_list_param(executor_cfg, "dict") or {}
    
    # Ensure proper types for RunConfig
    if parsed_inputs is not None and not isinstance(parsed_inputs, dict):
        parsed_inputs = {}
    if parsed_config is not None and not isinstance(parsed_config, dict):
        parsed_config = {}
    if parsed_cache is not None and not isinstance(parsed_cache, (dict, bool)):
        parsed_cache = False
    if parsed_final_vars is not None and not isinstance(parsed_final_vars, list):
        parsed_final_vars = []
    if parsed_with_adapter is not None and not isinstance(parsed_with_adapter, dict):
        parsed_with_adapter = {}
    
    # Ensure storage_options is a dict for FlowerPowerProject.load
    if parsed_storage_options is not None and not isinstance(parsed_storage_options, dict):
        parsed_storage_options = {}
    
    # Create WithAdapterConfig object if needed
    from ..cfg.pipeline.run import WithAdapterConfig
    if isinstance(parsed_with_adapter, dict):
        with_adapter_config = WithAdapterConfig.from_dict(parsed_with_adapter)
    else:
        with_adapter_config = WithAdapterConfig()

    # Use FlowerPowerProject for better consistency with the new architecture
    project = FlowerPowerProject.load(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    )

    if project is None:
        logger.error(f"Failed to load FlowerPower project from {base_dir or '.'}")
        raise typer.Exit(1)

    try:
        # Construct RunConfig object from parsed CLI arguments
        run_config = RunConfig(
            inputs=parsed_inputs,
            final_vars=parsed_final_vars,
            config=parsed_config,
            cache=parsed_cache,
            with_adapter=with_adapter_config,  # type: ignore
            retry=RetryConfig(
                max_retries=max_retries,
                retry_delay=retry_delay,
                jitter_factor=jitter_factor,
            ),
        )

        # Handle executor configuration (type + config + convenience flags)
        try:
            if executor is not None:
                # Validate type
                from ..utils.security import validate_executor_type
                validate_executor_type(executor)
                parsed_executor_cfg["type"] = executor
            if executor_max_workers is not None:
                parsed_executor_cfg["max_workers"] = executor_max_workers
            if executor_num_cpus is not None:
                parsed_executor_cfg["num_cpus"] = executor_num_cpus

            if parsed_executor_cfg:
                from ..cfg.pipeline.run import ExecutorConfig
                run_config.executor = ExecutorConfig.from_dict(parsed_executor_cfg)
        except Exception as e:
            logger.error(f"Invalid executor configuration: {e}")
            raise typer.Exit(1)

        _ = project.run(name=name, run_config=run_config)
        logger.info(f"Pipeline '{name}' finished running.")
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f"File system error during pipeline execution: {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Invalid configuration for pipeline execution: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise typer.Exit(1)


@app.command()
def new(
    name: str = typer.Argument(..., help="Name of the pipeline to create"),
    base_dir: str | None = typer.Option(None, "--base-dir", "-d", help="Base directory for the pipeline"),
    storage_options: str | None = typer.Option(None, "--storage-options", "-s", help="Storage options as JSON, dict string, or key=value pairs"),
    log_level: str | None = typer.Option(None, "--log-level", help="Logging level (debug, info, warning, error, critical)"),
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
    base_dir, parsed_storage_options, log_level = parse_common_options(
        base_dir, storage_options, log_level
    )
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as manager:
        manager.new(name=name, overwrite=overwrite)
    logger.info(f"New pipeline structure created for '{name}'.")


@app.command()
def delete(
    name: str = typer.Argument(..., help="Name of the pipeline to delete"),
    base_dir: str | None = typer.Option(None, "--base-dir", "-d", help="Base directory for the pipeline"),
    storage_options: str | None = typer.Option(None, "--storage-options", "-s", help="Storage options as JSON, dict string, or key=value pairs"),
    log_level: str | None = typer.Option(None, "--log-level", help="Logging level (debug, info, warning, error, critical)"),
    cfg: bool = typer.Option(
        False, "--cfg", "-c", help="Delete only the configuration file"
    ),
    module: bool = typer.Option(
        False, "--module", "-m", help="Delete only the pipeline module"
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
    base_dir, parsed_storage_options, log_level = parse_common_options(
        base_dir, storage_options, log_level
    )

    # If neither flag is set, default to deleting both
    delete_cfg = cfg or not (cfg or module)
    delete_module = module or not (cfg or module)

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options,
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
    base_dir: str | None = typer.Option(None, "--base-dir", "-d", help="Base directory for the pipeline"),
    storage_options: str | None = typer.Option(None, "--storage-options", "-s", help="Storage options as JSON, dict string, or key=value pairs"),
    log_level: str | None = typer.Option(None, "--log-level", help="Logging level (debug, info, warning, error, critical)"),
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
    base_dir, parsed_storage_options, log_level = parse_common_options(
        base_dir, storage_options, log_level
    )
    is_raw = format.lower() == "raw"

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options,
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
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"File system error generating DAG for pipeline '{name}': {e}")
        except ValueError as e:
            logger.error(f"Invalid configuration for DAG generation: {e}")
        except Exception as e:
            logger.error(f"Failed to generate DAG for pipeline '{name}': {e}")


@app.command()
def save_dag(
    name: str = typer.Argument(..., help="Name of the pipeline to visualize"),
    base_dir: str | None = typer.Option(None, "--base-dir", "-d", help="Base directory for the pipeline"),
    storage_options: str | None = typer.Option(None, "--storage-options", "-s", help="Storage options as JSON, dict string, or key=value pairs"),
    log_level: str | None = typer.Option(None, "--log-level", help="Logging level (debug, info, warning, error, critical)"),
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
    base_dir, parsed_storage_options, log_level = parse_common_options(
        base_dir, storage_options, log_level
    )
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options,
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
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"File system error saving DAG for pipeline '{name}': {e}")
        except ValueError as e:
            logger.error(f"Invalid configuration for DAG saving: {e}")
        except Exception as e:
            logger.error(f"Failed to save DAG for pipeline '{name}': {e}")


@app.command()
def show_pipelines(
    base_dir: str | None = typer.Option(None, "--base-dir", "-d", help="Base directory for the pipeline"),
    storage_options: str | None = typer.Option(None, "--storage-options", "-s", help="Storage options as JSON, dict string, or key=value pairs"),
    log_level: str | None = typer.Option(None, "--log-level", help="Logging level (debug, info, warning, error, critical)"),
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
    base_dir, parsed_storage_options, log_level = parse_common_options(
        base_dir, storage_options, log_level
    )
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options,
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
    base_dir: str | None = typer.Option(None, "--base-dir", "-d", help="Base directory for the pipeline"),
    storage_options: str | None = typer.Option(None, "--storage-options", "-s", help="Storage options as JSON, dict string, or key=value pairs"),
    log_level: str | None = typer.Option(None, "--log-level", help="Logging level (debug, info, warning, error, critical)"),
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
    base_dir, parsed_storage_options, log_level = parse_common_options(
        base_dir, storage_options, log_level
    )
    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options,
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
    base_dir: str | None = typer.Option(None, "--base-dir", "-d", help="Base directory for the pipeline"),
    storage_options: str | None = typer.Option(None, "--storage-options", "-s", help="Storage options as JSON, dict string, or key=value pairs"),
    log_level: str | None = typer.Option(None, "--log-level", help="Logging level (debug, info, warning, error, critical)"),
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
    base_dir, parsed_storage_options, log_level = parse_common_options(
        base_dir, storage_options, log_level
    )

    # Validate 'to' argument for node hooks
    if type in (HookType.NODE_PRE_EXECUTE, HookType.NODE_POST_EXECUTE) and not to:
        raise typer.BadParameter(
            "The '--to' option (target node/tag) is required for node hooks."
        )

    with PipelineManager(
        base_dir=base_dir,
        storage_options=parsed_storage_options,
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
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"File system error adding hook to pipeline '{name}': {e}")
        except ValueError as e:
            logger.error(f"Invalid configuration for hook addition: {e}")
        except Exception as e:
            logger.error(f"Failed to add hook to pipeline '{name}': {e}")
