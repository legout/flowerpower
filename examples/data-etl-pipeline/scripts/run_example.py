#!/usr/bin/env python3
# /// script
# dependencies = [
#     "flowerpower",
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




@app.command()
def sync():
    """Run the ETL pipeline synchronously."""
    run_synchronous()




def main():
    """Main entry point for the Typer CLI application."""
    app()


if __name__ == "__main__":
    main()
