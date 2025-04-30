<div align="center">
  <h1>FlowerPower 🌸 - Build & Orchestrate Data Pipelines</h1>
  <h3>Simple Workflow Framework - Hamilton + APScheduler or RQ = FlowerPower</h3>
  <img src="./image.png" alt="FlowerPower Logo" width="400" height="300">
</div>


# FlowerPower 🌸 - Build & Orchestrate Data Pipelines

[![PyPI version](https://img.shields.io/pypi/v/flowerpower.svg?style=flat-square)](https://pypi.org/project/flowerpower/) <!-- Placeholder -->
[![License](https://img.shields.io/pypi/l/flowerpower.svg?style=flat-square)](https://github.com/your-org/flowerpower/blob/main/LICENSE) <!-- Placeholder -->
[![Build Status](https://img.shields.io/github/actions/workflow/status/your-org/flowerpower/ci.yml?branch=main&style=flat-square)](https://github.com/your-org/flowerpower/actions) <!-- Placeholder -->
[![Python Version](https://img.shields.io/pypi/pyversions/flowerpower.svg?style=flat-square)](https://pypi.org/project/flowerpower/) <!-- Placeholder -->

**FlowerPower** is a Python framework designed for building, configuring, scheduling, and executing data processing pipelines with ease and flexibility. It promotes a modular, configuration-driven approach, allowing you to focus on your pipeline logic while FlowerPower handles the orchestration.

## ✨ Key Features

*   **Modular Design:** Easily swap components like job queue backends (APScheduler, RQ) or add custom I/O plugins.
*   **Configuration-Driven:** Define pipeline parameters, execution logic, and scheduling declaratively using simple YAML files.
*   **Job Queue Integration:** Built-in support for different asynchronous execution models:
    *   **APScheduler:** For time-based scheduling (cron, interval, date).
    *   **RQ (Redis Queue):** For distributed task queues.
*   **Extensible I/O Plugins:** Connect to various data sources and destinations (CSV, JSON, Parquet, DeltaTable, DuckDB, PostgreSQL, MySQL, MSSQL, Oracle, MQTT, SQLite, and more).
*   **Hamilton Integration:** Leverages the [Hamilton](https://github.com/DAGWorks-Inc/hamilton) library for defining dataflows in a clean, functional way within your Python pipeline scripts.
*   **Multiple Interfaces:** Interact with your pipelines via:
    *   **Command Line Interface (CLI):** For running, managing, and inspecting pipelines.
    *   **Web UI:** A graphical interface for monitoring and managing pipelines and schedules.
*   **Filesystem Abstraction:** Simplifies interactions with different storage backends.

## 🚀 Installation

We recommend using [uv](https://github.com/astral-sh/uv) for installing FlowerPower and managing your project environments. `uv` is an extremely fast Python package installer and resolver.

```bash
# Create and activate a virtual environment (recommended)
uv venv
source .venv/bin/activate # Or .\.venv\Scripts\activate on Windows

# Install FlowerPower
uv pip install flowerpower
```

*(Note: Specify required Python versions if known, e.g., Python 3.8+)*

## 🌱 Getting Started

Let's build a simple "Hello World" pipeline.

**1. Initialize Your Project:**

You can quickly set up the standard FlowerPower project structure using the CLI or Python.

**Using the CLI:**

Navigate to your desired parent directory and run:
```bash
flowerpower init --name hello-flowerpower-project
```
This will create a `hello-flowerpower-project` directory with the necessary `conf/` and `pipelines/` subdirectories and default configuration files.

**Using Python:**

Alternatively, you can initialize programmatically:
```python
from flowerpower import init_project

# Creates the structure in the current directory
init_project(name='hello-flowerpower-project', job_queue_type='rq') # Or 'apscheduler'
```

This sets up the basic layout:
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

**2. Configure Project (`conf/project.yml`):**

Define your project name and choose your job queue backend. Here's an example using RQ:

```yaml
name: my_awesome_project
job_queue:
  type: rq
  backend:
    type: redis
    # host: localhost # Default or specify connection details
    # port: 6379
    # ... other redis options
    queues:
      - default
      - high
      - low
# adapter: ... # Optional adapter configurations (e.g., Hamilton Tracker, MLflow)
```

**3. Define Pipeline (`conf/pipelines/hello_world.yml`):**

Specify parameters, run configurations, and scheduling for your pipeline.

```yaml
# adapter: ... # Pipeline-specific adapter overrides

params: # Parameters accessible in your Python code
  greeting:
    message: "Hello"
  target:
    name: "World"

run: # How to execute the pipeline
  final_vars: # Specify the desired output(s) from your Hamilton DAG
    - full_greeting
  # config: ... # Runtime configuration overrides for Hamilton
  # executor: ... # Execution backend (e.g., threadpool, multiprocessing)

schedule: # Optional: How often to run the pipeline
  cron: "0 * * * *" # Run hourly
  # interval: # e.g., { "minutes": 15 }
  # date: # e.g., "2025-12-31 23:59:59"
```

**4. Implement Pipeline (`pipelines/hello_world.py`):**

Write your pipeline logic using Python and Hamilton. FlowerPower makes configuration easily accessible.

```python
import pandas as pd
from pathlib import Path
from hamilton.function_modifiers import parameterize
from flowerpower.cfg import Config

# Load configuration specific to this pipeline
# Assumes this file is in pipelines/hello_world.py relative to conf/
PARAMS = Config.load(Path(__file__).parents[1], pipeline_name="hello_world").pipeline.h_params
@parameterize(**PARAMS.greeting) # Inject 'message' from params
def greeting_message(message: str) -> str:
  """Provides the greeting part."""
  return f"{message},"

@parameterize(**PARAMS.target) # Inject 'name' from params
def target_name(name: str) -> str:
  """Provides the target name."""
  return f"{name}!"

def full_greeting(greeting_message: str, target_name: str) -> str:
  """Combines the greeting and target."""
  print(f"Generating greeting: {greeting_message} {target_name}")
  return f"{greeting_message} {target_name}"

# You can add more complex Hamilton functions here...
```


## 🏃‍♀️ Running Pipelines: Sync vs. Async

FlowerPower offers flexibility in how you execute your pipelines:

**1. Synchronous Execution:**

For simple pipelines or testing, you can run them directly in the current session without involving a job queue.

*   **Via CLI:**
    ```bash
    # Assumes your project structure is standard and you are in the project root
    flowerpower pipeline run hello_world --base_dir .
    ```
*   **Via Python:**
    ```python
    from flowerpower.pipeline import PipelineManager

    # Specify the base directory containing your 'conf/' folder
    pm = PipelineManager(base_dir='.')
    results = pm.run('hello_world') # Execute the pipeline named 'hello_world'
    print(results)
    ```

**2. Asynchronous Execution (Job Queues):**

For scheduling, background execution, or distributed processing, leverage FlowerPower's job queue integration. This is configured in your `conf/project.yml`.

*   **RQ (Redis Queue):**
    *   **Requires:** Access to a running Redis server.
    *   Ideal for distributed task queues where workers can pick up jobs.
    *   Configure in `project.yml`: `job_queue: { type: rq, backend: { type: redis, ... } }`
    *   **Learn More:** [RQ Documentation](https://python-rq.org/)

*   **APScheduler:**
    *   **Requires:**
        *   A **Data Store:** To persist job information (Options: PostgreSQL, MySQL, SQLite, MongoDB).
        *   An **Event Broker:** To notify workers of scheduled jobs (Options: Redis, MQTT, PostgreSQL).
    *   Ideal for time-based scheduling (cron, intervals, specific dates).
    *   Configure in `project.yml`: `job_queue: { type: apscheduler, datastore: { ... }, eventbroker: { ... } }`
    *   **Learn More:** [APScheduler Documentation](https://apscheduler.readthedocs.io/)

**Local Development Setup (Docker):**

To easily set up required services like Redis, PostgreSQL, or MQTT locally for testing job queues, a basic `docker-compose.yml` file is provided in the `docker/` directory. This file includes configurations for various services useful during development.

```bash
# Navigate to the docker directory and start services
cd docker
docker-compose up -d redis postgres # Example: Start Redis and PostgreSQL
```
*(Note: Review and adapt `docker/docker-compose.yml` for your specific needs. It's intended for development, not production.)*



## ⚙️ Configuration Overview

FlowerPower uses a layered configuration system:

*   **`conf/project.yml`:** Defines global settings for your project, primarily the `job_queue` backend (RQ or APScheduler) and configurations for integrated `adapter`s (like Hamilton Tracker, MLflow, etc.).
*   **`conf/pipelines/*.yml`:** Each file defines a specific pipeline. It contains:
    *   `params`: Input parameters for your Hamilton functions.
    *   `run`: Execution details like target outputs (`final_vars`), Hamilton runtime `config`, and `executor` settings.
    *   `schedule`: Defines when the pipeline should run automatically (using `cron`, `interval`, or `date`).
    *   `adapter`: Pipeline-specific overrides for adapter settings.

## 🛠️ Basic Usage

The primary way to interact with pipelines is often through the CLI:

```bash
# Run a pipeline manually
flowerpower run <pipeline_name>

# List available pipelines (example command)
# flowerpower list pipelines

# Check job status (example command)
# flowerpower status
```

*(Note: Replace placeholder commands with actual CLI commands once known)*

## 🖥️ Interfaces

FlowerPower provides two main ways to interact:

*   **CLI:** A command-line interface for developers and automation.
*   **Web UI:** A browser-based interface for monitoring pipeline runs, schedules, and potentially managing configurations.

## 🤝 Contributing

Contributions are welcome! Please refer to the `CONTRIBUTING.md` file (placeholder) for guidelines.

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details. (Placeholder - update with actual license)