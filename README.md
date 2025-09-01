<div align="center">
  <h1>FlowerPower 🌸 - Build & Orchestrate Data Pipelines</h1>
  <h3>Simple Workflow Framework - Hamilton = FlowerPower</h3>
  <img src="./image.png" alt="FlowerPower Logo" width="400" height="300">
</div>



[![PyPI version](https://img.shields.io/pypi/v/flowerpower.svg?style=flat-square)](https://pypi.org/project/flowerpower/) <!-- Placeholder -->
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/legout/flowerpower/blob/main/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/legout/flowerpower)
[![Documentation Status](https://readthedocs.org/projects/flowerpower/badge/?version=latest)](https://legout.github.io/flowerpower/)


**FlowerPower** is a Python framework designed for building, configuring, and executing data processing pipelines with ease and flexibility. It promotes a modular, configuration-driven approach, allowing you to focus on your pipeline logic while FlowerPower handles the orchestration.

It leverages the [Hamilton](https://github.com/apache/hamilton) library for defining dataflows in a clean, functional way within your Python pipeline scripts. Pipelines are defined in Python modules and configured using YAML files, making it easy to manage and understand your data workflows.
FlowerPower provides a unified project interface that makes it easy to work with pipeline execution. It also provides a web UI (Hamilton UI) for monitoring and managing your pipelines.
FlowerPower is designed to be extensible, allowing you to easily add custom I/O plugins and adapt to different deployment scenarios. This flexibility makes it suitable for a wide range of data processing tasks, from simple ETL jobs to complex data workflows.


## ✨ Key Features

*   **Modular Pipeline Design:** Thanks to [Hamilton](https://github.com/apache/hamilton), you can define your data processing logic in Python modules, using functions as nodes in a directed acyclic graph (DAG).
*   **Configuration-Driven:** Define pipeline parameters, execution logic, and scheduling declaratively using simple YAML files.
*   **Extensible I/O Plugins:** Connect to various data sources and destinations (CSV, JSON, Parquet, DeltaTable, DuckDB, PostgreSQL, MySQL, MSSQL, Oracle, MQTT, SQLite, and more).
*   **Unified Project Interface:** Interact with your pipelines via:
    *   **FlowerPowerProject API:** A unified interface for pipeline execution, supporting both `RunConfig` objects and flexible `**kwargs` overrides.
    *   **Command Line Interface (CLI):** For running, managing, and inspecting pipelines, with enhanced `run` command capabilities.
    *   **Web UI:** A graphical interface for monitoring and managing pipelines and schedules. ([Hamilton UI](https://hamilton.dagworks.io/en/latest/hamilton-ui/ui/))
*   **Filesystem Abstraction:** Simplified file handling with support for local and remote filesystems (e.g., S3, GCS).

## 📦 Installation

We recommend using [uv](https://github.com/astral-sh/uv) for installing FlowerPower and managing your project environments. `uv` is an extremely fast Python package installer and resolver.

```bash
# Create and activate a virtual environment (recommended)
uv venv
source .venv/bin/activate # Or .\.venv\Scripts\activate on Windows

# Install FlowerPower
uv pip install flowerpower

# Optional: Install additional dependencies for specific features
uv pip install flowerpower[io] # For I/O plugins (CSV, JSON, Parquet, DeltaTable, DuckDB, PostgreSQL, MySQL, MSSQL, Oracle, SQLite)
uv pip install flowerpower[ui] # For Hamilton UI
uv pip install flowerpower[all] # Install all optional dependencies
```

*(Note: Specify required Python versions if known, e.g., Python 3.8+)*

## 🚀 Getting Started

Let's build a simple "Hello World" pipeline.

### 1. Initialize Your Project:

You can quickly set up the standard FlowerPower project structure using the CLI or Python.

**Using the CLI:**

Navigate to your desired parent directory and run:
```bash
flowerpower init --name hello-flowerpower-project
```


**Using Python:**

Alternatively, you can initialize programmatically:
```python
from flowerpower import FlowerPowerProject

# Initialize a new project
project = FlowerPowerProject.init(
    name='hello-flowerpower-project',
)
```

This will create a `hello-flowerpower-project` directory with the necessary `conf/` and `pipelines/` subdirectories and default configuration files.

```
hello-flowerpower-project/
├── conf/
│   ├── project.yml
│   └── pipelines/
└── pipelines/
```

Now, navigate into your new project directory:

```bash
cd hello-flowerpower-project
```

**Configure Project (`conf/project.yml`):**

Open `conf/project.yml` and define your project name:

```yaml
name: hello-flowerpower
# adapter: ... # Optional adapter configurations (e.g., Hamilton Tracker, MLflow), see `conf/project.yml` for details
```

### 2. Create Your Pipeline

You can create a new pipeline using the CLI or programmatically.

**Using the CLI:**

```bash
flowerpower pipeline new hello_world
```

**Using Python:**

You can create pipelines programmatically using the FlowerPowerProject interface:

```python
from flowerpower import FlowerPowerProject

# Load the project
project = FlowerPowerProject.load('.')

# Create a new pipeline
project.pipeline_manager.new(name='hello_world')
```

This will create a new file `hello_world.py` in the `pipelines/` directory and a corresponding configuration file `hello_world.yml` in `conf/pipelines/`.

**Implement Pipeline (`pipelines/hello_world.py`):**

Open `pipelines/hello_world.py` and write your pipeline logic using Python and Hamilton. FlowerPower makes configuration easily accessible.

```python
# FlowerPower pipeline hello_world.py
# Created on 2025-05-03 22:34:09

####################################################################################################
# Import necessary libraries
# NOTE: Remove or comment out imports that are not used in the pipeline

from hamilton.function_modifiers import parameterize

from pathlib import Path

from flowerpower.cfg import Config

####################################################################################################
# Load pipeline parameters. Do not modify this section.

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="hello_world"
).pipeline.h_params


####################################################################################################
# Helper functions.
# This functions have to start with an underscore (_).


####################################################################################################
# Pipeline functions

@parameterize(**PARAMS.greeting_message) # Inject 'message' from params
def greeting_message(message: str) -> str:
  """Provides the greeting part."""
  return f"{message},"

@parameterize(**PARAMS.target_name) # Inject 'name' from params
def target_name(name: str) -> str:
  """Provides the target name."""
  return f"{name}!"

def full_greeting(greeting_message: str, target_name: str) -> str:
  """Combines the greeting and target."""
  print(f"Generating greeting: {greeting_message} {target_name}")
  return f"{greeting_message} {target_name}"

# You can add more complex Hamilton functions here...
```

**Configure Pipeline (`conf/pipelines/hello_world.yml`):**

Open `conf/pipelines/hello_world.yml` and specify parameters, run configurations, and scheduling for your pipeline.

```yaml
# adapter: ... # Pipeline-specific adapter overrides

params: # Parameters accessible in your Python code
  greeting_message:
    message: "Hello"
  target_name:
    name: "World"

run: # How to execute the pipeline
  final_vars: # Specify the desired output(s) from your Hamilton DAG
    - full_greeting
  # inputs: # Optional: Specify input variables to the pipeline
    # message: "Hello"
  # config: ... # Runtime configuration overrides for Hamilton
  # executor: ... # Execution backend (e.g., threadpool, multiprocessing)

```
### 3. Run Your Pipeline 🏃‍♀️

FlowerPower allows you to execute your pipelines synchronously, with flexible configuration options.

#### Synchronous Execution:

For quick testing or local runs, you can execute your pipeline synchronously. This is useful for debugging or running pipelines in a local environment.

*   **Via CLI:**

    The `flowerpower pipeline run` command now supports `RunConfig` objects (via file path or JSON string) and direct `**kwargs` for overriding.

    ```bash
    # Basic pipeline execution
    flowerpower pipeline run hello_world

    # Run with individual parameters (kwargs)
    flowerpower pipeline run hello_world --inputs '{"greeting_message": "Hi", "target_name": "FlowerPower"}' --final-vars '["full_greeting"]' --log-level DEBUG

    # Run using a RunConfig from a YAML file
    # Assuming you have a run_config.yaml like:
    # inputs:
    #   greeting_message: "Hola"
    #   target_name: "Amigo"
    # log_level: "INFO"
    flowerpower pipeline run hello_world --run-config ./run_config.yaml

    # Run using a RunConfig provided as a JSON string
    flowerpower pipeline run hello_world --run-config '{"inputs": {"greeting_message": "Bonjour", "target_name": "Monde"}, "log_level": "INFO"}'

    # Mixing RunConfig with individual parameters (kwargs overrides RunConfig)
    # This will run with log_level="DEBUG" and inputs={"greeting_message": "Howdy", "target_name": "Partner"}
    flowerpower pipeline run hello_world --run-config '{"inputs": {"greeting_message": "Original", "target_name": "Value"}, "log_level": "INFO"}' --inputs '{"greeting_message": "Howdy", "target_name": "Partner"}' --log-level DEBUG
    ```

*   **Via Python:**

    The `run` methods (`FlowerPowerProject.run`, `PipelineManager.run`) now primarily accept a `RunConfig` object, but also allow individual parameters to be passed via `**kwargs` which override `RunConfig` attributes.

    ```python
    from flowerpower import FlowerPowerProject
    from flowerpower.cfg.pipeline.run import RunConfig
    from flowerpower.cfg.pipeline.builder import RunConfigBuilder

    # Load the project
    project = FlowerPowerProject.load('.')

    # Basic execution
    result = project.run('hello_world')
    print(result)

    # Using individual parameters (kwargs)
    result = project.run(
        'hello_world',
        inputs={"greeting_message": "Hi", "target_name": "FlowerPower"},
        final_vars=["full_greeting"],
        log_level="DEBUG"
    )
    print(result)

    # Using RunConfig directly
    config = RunConfig(
        inputs={"greeting_message": "Aloha", "target_name": "World"},
        final_vars=["full_greeting"],
        log_level="INFO"
    )
    result = project.run('hello_world', run_config=config)
    print(result)

    # Using RunConfigBuilder (recommended)
    config = (
        RunConfigBuilder(pipeline_name='hello_world')
        .with_inputs({"greeting_message": "Greetings", "target_name": "Earth"})
        .with_final_vars(["full_greeting"])
        .with_log_level("DEBUG")
        .with_retries(max_attempts=3, delay=1.0)
        .build()
    )
    result = project.run('hello_world', run_config=config)
    print(result)

    # Mixing RunConfig with individual parameters (kwargs overrides RunConfig)
    base_config = RunConfigBuilder().with_log_level("INFO").build()
    result = project.run(
        'hello_world',
        run_config=base_config,
        inputs={"greeting_message": "Howdy", "target_name": "Partner"}, # Overrides inputs in base_config
        log_level="DEBUG" # Overrides log_level in base_config
    )
    print(result)
    ```


## ⚙️ Configuration Overview

FlowerPower uses a layered configuration system:

*   **`conf/project.yml`:** Defines global settings for your project, including integrated `adapter`s (like Hamilton Tracker, MLflow, etc.).
*   **`conf/pipelines/*.yml`:** Each file defines a specific pipeline. It contains:
    *   `params`: Input parameters for your Hamilton functions.
    *   `run`: Execution details like target outputs (`final_vars`), Hamilton runtime `config`, and `executor` settings.
    *   `adapter`: Pipeline-specific overrides for adapter settings.

## 🛠️ Basic Usage

You can interact with FlowerPower pipelines through multiple interfaces:

**Python API (Recommended):**
```python
from flowerpower import FlowerPowerProject
from flowerpower.cfg.pipeline.run import RunConfig
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

# Load the project
project = FlowerPowerProject.load('.')

# Run a pipeline using RunConfig
config = RunConfig(inputs={"greeting_message": "Hello", "target_name": "API"})
result = project.run('hello_world', run_config=config)
print(result)

# Run a pipeline using kwargs
result = project.run('hello_world', inputs={"greeting_message": "Hi", "target_name": "Kwargs"})
print(result)
```

**CLI:**
```bash
# Run a pipeline using RunConfig from a file
# flowerpower pipeline run hello_world --run-config ./path/to/run_config.yaml

# Run a pipeline using kwargs
flowerpower pipeline run hello_world --inputs '{"greeting_message": "CLI", "target_name": "Kwargs"}'

# List all available commands
flowerpower --help
```

## 🔧 Direct Module Usage

While the unified `FlowerPowerProject` interface is recommended for most use cases, you can also use the pipeline module directly for more granular control or when you only need specific functionality.

### Pipeline-Only Usage

If you only need pipeline execution, you can use the `PipelineManager` directly:

```python
from flowerpower.pipeline import PipelineManager
from flowerpower.cfg.pipeline.run import RunConfig
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

# Initialize pipeline manager
pm = PipelineManager(base_dir='.')

# Create a new pipeline
pm.new(name='my_pipeline')

# Run a pipeline synchronously using RunConfig
config = RunConfig(inputs={'param': 'value'}, final_vars=['output_var'])
result = pm.run(name='my_pipeline', run_config=config)
print(result)

# Run a pipeline synchronously using kwargs
result = pm.run(name='my_pipeline', inputs={'param': 'new_value'}, final_vars=['output_var'])
print(result)

# List available pipelines
pipelines = pm.list()
print(f"Available pipelines: {pipelines}")

# Get pipeline information
info = pm.get('my_pipeline')
print(f"Pipeline config: {info}")

# Delete a pipeline
pm.delete('old_pipeline')
```

**When to use Pipeline-only approach:**
- Simple synchronous workflows
- Testing and development
- Lightweight applications with minimal dependencies

**Benefits of FlowerPowerProject vs Direct Usage:**

| Approach | Benefits | Use Cases |
|----------|----------|-----------|
| **FlowerPowerProject** | - Unified interface<br>- Automatic dependency injection<br>- Simplified configuration<br>- Best practices built-in | - Most applications<br>- Rapid development<br>- Full feature integration |
| **Pipeline-only** | - Lightweight<br>- Simple synchronous execution | - Testing<br>- Simple workflows |

## 🖥️ UI

The FlowerPower web UI (Hamilton UI) provides a graphical interface for monitoring and managing your pipelines. It allows you to visualize pipeline runs, schedules, and potentially manage configurations.

```bash
# Start the web UI
flowerpower ui
```

## 📖 Documentation

You can find the full documentation for FlowerPower, including installation instructions, usage examples, and API references, at [https://legout.github.io/flowerpower/](https://legout.github.io/flowerpower/).


## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details. (Placeholder - update with actual license)