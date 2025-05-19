<div align="center">
  <h1>FlowerPower 🌸 - Build & Orchestrate Data Pipelines</h1>
  <h3>Simple Workflow Framework - Hamilton + APScheduler or RQ = FlowerPower</h3>
  <img src="./image.png" alt="FlowerPower Logo" width="400" height="300">
</div>



[![PyPI version](https://img.shields.io/pypi/v/flowerpower.svg?style=flat-square)](https://pypi.org/project/flowerpower/) <!-- Placeholder -->
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/legout/flowerpower/blob/main/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/legout/flowerpower)


**FlowerPower** is a Python framework designed for building, configuring, scheduling, and executing data processing pipelines with ease and flexibility. It promotes a modular, configuration-driven approach, allowing you to focus on your pipeline logic while FlowerPower handles the orchestration.

It is leveraging the [Hamilton](https://github.com/DAGWorks-Inc/hamilton) library for defining dataflows in a clean, functional way within your Python pipeline scripts. Pipelines are defined in Python modules and configured using YAML files, making it easy to manage and understand your data workflows.
FlowerPower integrates with job queue systems like [APScheduler](https://github.com/scheduler/apscheduler) and [RQ](https://github.com/rq/rq), enabling you to schedule and manage your pipeline runs efficiently. It also provides a web UI (Hamilton UI) for monitoring and managing your pipelines.
FlowerPower is designed to be extensible, allowing you to easily swap components like job queue backends or add custom I/O plugins. This flexibility makes it suitable for a wide range of data processing tasks, from simple ETL jobs to complex data workflows.


## ✨ Key Features

*   **Modular Pipeline Design:** Thanks to [Hamilton](https://github.com/DAGWorks-Inc/hamilton), you can define your data processing logic in Python modules, using functions as nodes in a directed acyclic graph (DAG).
*   **Configuration-Driven:** Define pipeline parameters, execution logic, and scheduling declaratively using simple YAML files.
*   **Job Queue Integration:** Built-in support for different asynchronous execution models:
    *   **APScheduler:** For time-based scheduling (cron, interval, date).
    *   **RQ (Redis Queue):** For distributed task queues.
*   **Extensible I/O Plugins:** Connect to various data sources and destinations (CSV, JSON, Parquet, DeltaTable, DuckDB, PostgreSQL, MySQL, MSSQL, Oracle, MQTT, SQLite, and more).
*   **Multiple Interfaces:** Interact with your pipelines via:
    *   **Command Line Interface (CLI):** For running, managing, and inspecting pipelines.
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
uv pip install flowerpower[apscheduler,rq] # Example for APScheduler and RQ
uv pip install flowerpower[io] # Example for I/O plugins (CSV, JSON, Parquet, DeltaTable, DuckDB, PostgreSQL, MySQL, MSSQL, Oracle, SQLite)
uv pip install flowerpower[ui] # Example for Hamilton UI
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
from flowerpower import init_project

# Creates the structure in the current directory
init_project(name='hello-flowerpower-project', job_queue_type='rq') # Or 'apscheduler'
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

Open `conf/project.yml` and define your project name and choose your job queue backend. Here's an example using RQ:

```yaml
name: hello-flowerpower
job_queue:
  type: rq
  backend:
    type: redis
    host: localhost
    port: 6379
    # ... other redis options
    queues:
      - default
      - high
      - low
# adapter: ... # Optional adapter configurations (e.g., Hamilton Tracker, MLflow), see `conf/project.yml` for details
```

### 2. Create Your Pipeline

You can create a new pipeline using the CLI or programmatically.

**Using the CLI:**

```bash
flowerpower pipeline new hello_world
```

**Using Python:**

There is a `PipelineManager` class to manage pipelines programmatically:

```python
from flowerpower.pipeline import PipelineManager
pm = PipelineManager(base_dir='.')
pm.new(name='hello_world') # Creates a new pipeline
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
  target:
    name: "World"

run: # How to execute the pipeline
  final_vars: # Specify the desired output(s) from your Hamilton DAG
    - full_greeting
  # inputs: # Optional: Specify input variables to the pipeline
    # message: "Hello"
  # config: ... # Runtime configuration overrides for Hamilton
  # executor: ... # Execution backend (e.g., threadpool, multiprocessing)

schedule: # Optional: How often to run the pipeline
  cron: "0 * * * *" # Run hourly
  # interval: # e.g., { "minutes": 15 }
  # date: # e.g., "2025-12-31 23:59:59"
```
### 3. Run Your Pipeline 🏃‍♀️

FlowerPower offers flexibility in how you execute your pipelines:
 - **Synchronous Execution:** Run the pipeline directly.
 - **Asynchronous Execution:** Use job queues for scheduling, background execution, or distributed processing.

#### 1. Synchronous Execution:

For quick testing or local runs, you can execute your pipeline synchronously. This is useful for debugging or running pipelines in a local environment.

*   **Via CLI:**
    ```bash
    # Run the pipeline synchronously
    flowerpower pipeline run hello_world --base_dir .
    ```
*   **Via Python:**
    ```python
    from flowerpower.pipeline import PipelineManager
    pm = PipelineManager(base_dir='.')
    pm.run('hello_world') # Execute the pipeline named 'hello_world'  

#### 2. Asynchronous Execution (Job Queues):

For scheduling, background execution, or distributed processing, leverage FlowerPower's job queue integration. Ideal for distributed task queues where workers can pick up jobs. 

You have to install the job queue backend you want to use. FlowerPower supports two job queue backends: RQ (Redis Queue) and APScheduler.
```bash
# Install RQ (Redis Queue) or APScheduler
uv pip install flowerpower[rq] # For RQ (Redis Queue)
uv pip install flowerpower[apscheduler] # For APScheduler
```
*   **Note:** Ensure you have the required dependencies installed for your chosen job queue backend. For RQ, you need Redis running. For APScheduler, you need a data store (PostgreSQL, MySQL, SQLite, MongoDB) and an event broker (Redis, MQTT, PostgreSQL).

**a) Configuring Job Queue Backends:** 

Configuration of the job queue backend is done in your `conf/project.yml`. Currently, FlowerPower supports two job queue backends:

*   **RQ (Redis Queue):**
    *   **Requires:** Access to a running Redis server.
    *   Configure in `conf/project.yml`: 
          ```yaml
          job_queue:
            type: rq
            backend:
              type: redis
              host: localhost
              port: 6379
              ... # other redis options

*   **APScheduler:**
    *   **Requires:**
        *   A **Data Store:** To persist job information (Options: PostgreSQL, MySQL, SQLite, MongoDB).
        *   An **Event Broker:** To notify workers of scheduled jobs (Options: Redis, MQTT, PostgreSQL).
    *   Configure in `cong/project.yml`:
          ```yaml
          job_queue:
            type: apscheduler
            backend:
              type: postgresql # or mysql, sqlite, mongodb
              host: localhost
              port: 5432
              user: your_user
              password: your_password
              database: your_database
              ... # other database options
            event_broker:
              type: redis # or mqtt, postgresql
              host: localhost
              port: 6379
              ... # other redis options
          ```
    
It is possible to override the job queue backend configuration using environment variables, the `settings` module or by monkey patching the backend configuration of the `PipelineManager` or `JobQueueManager` classes. This might be useful for testing or when you want to avoid hardcoding values in your configuration files.
*   **Using the `settings` module:**
    e.g to override the RQ backend username and password:
    ```python
    from flowerpower import settings
    
    # Override some configuration values. e.g. when using rq 
    settings.RQ_BACKEND_USERNAME = 'your_username'
    settings.RQ_BACKEND_PASSWORD = 'your_password'   
    ```
    See the `flowerpower/settings/job_queue.py` file for all available settings.

*   **Monkey Patching:**
    e.g to override the APScheduler data store username and password:
    ```python
    from flowerpower.pipeline import PipelineManager

    pm = PipelineManager(base_dir='.')
    pm.project_cfg.job_queue.backend.username = 'your_username'
    pm.project_cfg.job_queue.backend.password = 'your_password'
    ```
*  **Using Environment Variables:**
    e.g. use a `.env` file or set them in your environment. Here is a list of the available environment variables for the job queue backend configuration:
    ```
    FP_JOB_QUEUE_TYPE

    # RQ (Redis Queue) backend
    FP_RQ_BACKEND
    FP_RQ_BACKEND_USERNAME
    FP_RQ_BACKEND_PASSWORD
    FP_RQ_BACKEND_HOST
    FP_RQ_BACKEND_PORT

    # APScheduler data store
    FP_APS_BACKEND_DS
    FP_APS_BACKEND_DS_USERNAME
    FP_APS_BACKEND_DS_PASSWORD
    FP_APS_BACKEND_DS_HOST
    FP_APS_BACKEND_DS_PORT

    # APScheduler event broker
    FP_APS_BACKEND_EB
    FP_APS_BACKEND_EB_USERNAME
    FP_APS_BACKEND_EB_PASSWORD
    FP_APS_BACKEND_EB_HOST
    FP_APS_BACKEND_EB_PORT
    ```


**b) Add Job to Queue:** 
Run your pipeline using the job queue system. This allows you to schedule jobs, run them in the background, or distribute them across multiple workers.

*   **Via CLI:**
    ```bash
    # This will run the pipeline immediately and return the job result (blocking, until the job is done)
    flowerpower pipeline run-job hello_world --base_dir . 

    # Submit the pipeline to the job queue and return the job ID (non-blocking)
    flowerpower pipeline add-job hello_world --base_dir . 
    ```
*   **Via Python:**
    
    ```python
    from flowerpower.pipeline import PipelineManager
    pm = PipelineManager(base_dir='.')

    # submit the pipeline to the job queue and return the job ID (non-blocking)
    job_id = pm.add_job('hello_world') 

    # submit the pipeline to the job queue, runs it immediately and returns the job ID (non-blocking)
    result = pm.run_job('hello_world')
    ```

These commands will add the pipeline to the job queue, allowing it to be executed in the background or at scheduled intervals. The jobs will be processed by one or more workers, depending on your job queue configuration. You have to start the job queue workers separately.


**c) Start Job Queue Workers:** 
To process jobs in the queue, you need to start one or more workers.

*  **Via CLI:**
    ```bash
    flowerpower job-queue start-worker --base_dir . # Start the job queue worker
    ```

*   **Via Python:**
    ```python
    from flowerpower.job_queue import JobQueueManager
    with JobQueueManager(base_dir='.'):
        # Start the job queue worker
        jqm.start_worker()
    ```


## Local Development Setup (Docker):

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
flowerpower pipeline run hello_world --base_dir .

# Add a job to the queue
flowerpower pipeline add-job hello_world --base_dir .

# Schedule a pipeline
flowerpower pipeline schedule hello_world --base_dir . # Schedules like cron, interval, or date are configured in the pipeline config

# And many more commands...
flowerpower --help # List all available commands

```

## 🖥️ UI

The FlowerPower web UI (Hamilton UI) provides a graphical interface for monitoring and managing your pipelines. It allows you to visualize pipeline runs, schedules, and potentially manage configurations.

```bash
# Start the web UI
flowerpower ui
```

## 📖 Documentation

There is not much documentation yet, but you can find some examples in the `examples/` directory. The examples cover various use cases, including:
*   Basic pipeline creation and execution.
*   Using different job queue backends (RQ and APScheduler).
*   Configuring and scheduling pipelines.


There is a first version of documentation in `docs/`. This documentation is generated using [Pocket Flow Tutorial Project](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge). Although it is not complete and might be wrong in some parts, it can be a good starting point for understanding how to use FlowerPower.


## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details. (Placeholder - update with actual license)