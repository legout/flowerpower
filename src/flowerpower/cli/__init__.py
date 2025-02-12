import importlib

import typer
from loguru import logger

from ..flowerpower import init as init_
from .pipeline import app as pipeline_app

app = typer.Typer()


app.add_typer(pipeline_app, name="pipeline")

if importlib.util.find_spec("apscheduler"):
    from .scheduler import app as scheduler_app

    app.add_typer(scheduler_app, name="scheduler")

if importlib.util.find_spec("paho"):
    from .mqtt import app as mqtt_app

    app.add_typer(mqtt_app, name="mqtt")


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
def ui(
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
