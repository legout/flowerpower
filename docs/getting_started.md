# Getting Started with FlowerPower

## Introduction

FlowerPower is a Python workflow framework designed to simplify the creation, configuration, and execution of data processing pipelines. It leverages the Hamilton SDK and integrates with job queue systems like RQ, allowing for scheduled and managed pipeline runs. Pipelines are defined in Python modules and configured using YAML files.

## Installation

Install the core FlowerPower library using pip:

```bash
pip install flowerpower
```

FlowerPower uses optional dependencies for specific features like job queue backends (RQ), I/O connectors (databases, MQTT), etc. Install these as needed. For example, to use the RQ backend and MQTT:

```bash
pip install flowerpower[rq,mqtt]
```

Refer to the `pyproject.toml` file for a full list of available optional dependencies.

## Basic Usage: Hello World Example

This example demonstrates a simple pipeline defined in `examples/hello-world/`.

**1. Pipeline Configuration (`examples/hello-world/conf/pipelines/hello_world.yml`):**

This YAML file defines the pipeline's name, the Python module containing the logic, default parameters, and output handling.

```yaml
# FlowerPower pipeline config hello_world.yml
name: hello_world
description: A simple hello world pipeline
module: pipelines.hello_world

# --- Default Parameters ---
params:
  name: World

# --- Output Configuration ---
outputs:
  print_message: # Corresponds to a function/node name
    action: print # Special action, implies no saving needed
```

**2. Pipeline Code (`examples/hello-world/pipelines/hello_world.py`):**

This Python module defines the functions (nodes) that make up the pipeline's logic. FlowerPower uses type hints to define dependencies between functions.

```python
# FlowerPower pipeline hello_world.py
import time
import pandas as pd
from flowerpower.config import Config

PARAMS = Config.load()

def name() -> str:
    """Returns the name parameter."""
    return PARAMS.name

def wait() -> None:
    """Waits for 2 seconds."""
    time.sleep(2)

def message(name: str, wait: None) -> str:
    """Returns a greeting message."""
    return f"Hello, {name}!"

def print_message(message: str) -> None:
    """Prints the message."""
    print(message)
```

**3. Running the Pipeline:**

FlowerPower provides a command-line interface (CLI) defined via the `[project.scripts]` section in `pyproject.toml`. Based on the CLI structure found in `src/flowerpower/cli/pipeline.py`, you can likely run the pipeline using the following command from the project root directory:

```bash
flowerpower pipeline run hello_world
```

This command tells FlowerPower to execute the pipeline named `hello_world`, using its configuration file (`hello_world.yml`) to find the corresponding Python module (`pipelines/hello_world.py`) and execute the defined flow, ultimately calling the `print_message` function.

## Configuration

As seen in the example, FlowerPower relies heavily on YAML configuration files:

*   **Project Configuration (`project.yml`):** Defines project-level settings, such as the job queue backend (RQ), filesystem configurations, and default settings.
*   **Pipeline Configuration (`pipelines/*.yml`):** Defines individual pipeline specifics, including the source module, default parameters, input sources, and output targets/actions.

Understanding and modifying these configuration files is key to using FlowerPower effectively.