#!/usr/bin/env python3
# /// script
# dependencies = [
#     "flowerpower[rq]",
#     "pandas>=2.0.0",
#     "plotly>=5.15.0",
#     "typer>=0.9.0",
#     "numpy>=1.21.0"
# ]
# ///

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parents[1]
sys.path.insert(0, str(project_root))

from typing import Annotated

import typer

from flowerpower import FlowerPowerProject

app = typer.Typer()


def run_synchronous():
    """Run the ETL pipeline synchronously."""
    project = FlowerPowerProject.load(str(project_root))
    return project.run("sales_etl")


def run_with_job_queue():
    """Run the ETL pipeline using the job queue."""
    project = FlowerPowerProject.load(str(project_root))
    return project.enqueue("sales_etl")


def schedule_pipeline():
    """Schedule the ETL pipeline for recurring execution."""
    project = FlowerPowerProject.load(str(project_root))
    return project.schedule("sales_etl")


@app.command()
def sync():
    """Run the ETL pipeline synchronously."""
    run_synchronous()


@app.command()
def queue():
    """Run the ETL pipeline using the job queue."""
    run_with_job_queue()


@app.command()
def schedule():
    """Schedule the ETL pipeline for recurring execution."""
    schedule_pipeline()


def main():
    """Main entry point for the Typer CLI application."""
    app()


if __name__ == "__main__":
    main()
