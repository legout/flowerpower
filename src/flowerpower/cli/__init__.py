import importlib
import os

import typer
from loguru import logger

from ..flowerpower import init as init_
from .pipeline import app as pipeline_app
from .utils import parse_dict_or_list_param

app = typer.Typer(
    help="FlowerPower: A framework for building, executing, and managing data processing pipelines",
    rich_markup_mode="rich",
)


app.add_typer(
    pipeline_app, name="pipeline", help="Manage and execute FlowerPower pipelines"
)

if importlib.util.find_spec("apscheduler") or importlib.util.find_spec("rq"):
    from .job_queue import app as job_queue_app

    app.add_typer(
        job_queue_app,
        name="job-queue",
        help="Manage job queue workers and scheduled tasks",
    )

if importlib.util.find_spec("paho"):
    from .mqtt import app as mqtt_app

    app.add_typer(
        mqtt_app, name="mqtt", help="Connect pipelines to MQTT message brokers"
    )


@app.command()
def init(
    project_name: str = typer.Option(
        None, "--name", "-n", help="Name of the FlowerPower project to create"
    ),
    base_dir: str = typer.Option(
        None,
        "--base-dir",
        "-d",
        help="Base directory where the project will be created",
    ),
    storage_options: str = typer.Option(
        None, "--storage-options", "-s", help="Storage options as a JSON or dict string"
    ),
    job_queue_type: str = typer.Option(
        "rq",
        "--job-queue-type",
        "-q",
        help="Job queue backend type to use (rq, apscheduler)",
    ),
):
    """
    Initialize a new FlowerPower project.

    This command creates a new FlowerPower project with the necessary directory structure
    and configuration files. If no project name is provided, the current directory name
    will be used as the project name.

    Args:
        project_name: Name of the FlowerPower project to create. If not provided,
                      the current directory name will be used
        base_dir: Base directory where the project will be created. If not provided,
                  the current directory's parent will be used
        storage_options: Storage options for filesystem access, as a JSON or dict string
        job_queue_type: Type of job queue backend to use (rq, apscheduler)

    Examples:
        # Create a project in the current directory using its name
        $ flowerpower init

        # Create a project with a specific name
        $ flowerpower init --name my-awesome-project

        # Create a project in a specific location
        $ flowerpower init --name my-project --base-dir /path/to/projects

        # Create a project with APScheduler as the job queue backend
        $ flowerpower init --job-queue-type apscheduler
    """
    parsed_storage_options = {}
    if storage_options:
        try:
            parsed_storage_options = (
                parse_dict_or_list_param(storage_options, "dict") or {}
            )
        except Exception as e:
            logger.error(f"Error parsing storage options: {e}")
            raise typer.Exit(code=1)

    try:
        init_(
            name=project_name,
            base_dir=base_dir,
            storage_options=parsed_storage_options,
            job_queue_type=job_queue_type,
        )
    except Exception as e:
        logger.error(f"Error initializing project: {e}")
        raise typer.Exit(code=1)


@app.command()
def ui(
    port: int = typer.Option(8241, "--port", "-p", help="Port to run the UI server on"),
    base_dir: str = typer.Option(
        "~/.hamilton/db", "--base-dir", "-d", help="Base directory for Hamilton UI data"
    ),
    no_migration: bool = typer.Option(
        False, "--no-migration", help="Skip running database migrations"
    ),
    no_open: bool = typer.Option(
        False, "--no-open", help="Don't automatically open the UI in a browser"
    ),
    settings_file: str = typer.Option(
        "mini", "--settings", "-s", help="Settings file to use for the UI"
    ),
    config_file: str = typer.Option(
        None, "--config", "-c", help="Configuration file to use for the UI"
    ),
):
    """
    Start the Hamilton UI web application.

    This command launches the Hamilton UI, which provides a web interface for
    visualizing and interacting with your FlowerPower pipelines. The UI allows you
    to explore pipeline execution graphs, view results, and manage jobs.

    Args:
        port: Port to run the UI server on
        base_dir: Base directory where the UI will store its data
        no_migration: Skip running database migrations on startup
        no_open: Prevent automatically opening the browser
        settings_file: Settings profile to use (mini, dev, prod)
        config_file: Optional custom configuration file path

    Examples:
        # Start the UI with default settings
        $ flowerpower ui

        # Run the UI on a specific port
        $ flowerpower ui --port 9000

        # Use a custom data directory
        $ flowerpower ui --base-dir ~/my-project/.hamilton-data

        # Start without opening a browser
        $ flowerpower ui --no-open

        # Use production settings
        $ flowerpower ui --settings prod
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
        base_dir=os.path.expanduser(base_dir),
        no_migration=no_migration,
        no_open=no_open,
        settings_file=settings_file,
        config_file=config_file,
    )


if __name__ == "__main__":
    app()
