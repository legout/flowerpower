import importlib
import os
import sys
import uvicorn
import typer
from pathlib import Path

web_app = typer.Typer(help="Web UI commands")


@web_app.command()
def start(
    host: str = "127.0.0.1",
    port: int = 8080,
    reload: bool = True,
    base_dir: str = None,
):
    """
    Start the FlowerPower Web UI.

    Args:
        host: Host address to run the server on
        port: Port to run the server on
        reload: Enable auto-reload on code changes
        base_dir: Base directory for the FlowerPower project
    """
    # Set the base directory in environment variable so web app can access it
    if base_dir:
        os.environ["FLOWERPOWER_BASE_DIR"] = base_dir

    # Import after setting environment vars
    from .._web import app as fastapi_app

    # Start the server
    uvicorn.run(
        "flowerpower.web:app", 
        host=host, 
        port=port, 
        reload=reload
    )


if __name__ == "__main__":
    web_app()
