<div align="center">
  <h1>FlowerPower 🌸 - Build & Orchestrate Data Pipelines</h1>
  <h3>Simple Workflow Framework - Hamilton + RQ = FlowerPower</h3>
  <img src="./image.png" alt="FlowerPower Logo" width="400" height="300">
</div>



[![PyPI version](https://img.shields.io/pypi/v/flowerpower.svg?style=flat-square)](https://pypi.org/project/flowerpower/) <!-- Placeholder -->
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/legout/flowerpower/blob/main/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/legout/flowerpower)


**FlowerPower** is a Python framework designed for building, configuring, scheduling, and executing data processing pipelines with ease and flexibility. It promotes a modular, configuration-driven approach, allowing you to focus on your pipeline logic while FlowerPower handles the orchestration.

It leverages the [Hamilton](https://github.com/apache/hamilton) library for defining dataflows in a clean, functional way within your Python pipeline scripts. Pipelines are defined in Python modules and configured using YAML files, making it easy to manage and understand your data workflows.
FlowerPower integrates with [RQ (Redis Queue)](https://github.com/rq/rq) for job queue management, enabling you to schedule and manage your pipeline runs efficiently. The framework features a clean separation between pipeline execution and job queue management, with a unified project interface that makes it easy to work with both synchronous and asynchronous execution modes. It also provides a web UI (Hamilton UI) for monitoring and managing your pipelines.
FlowerPower is designed to be extensible, allowing you to easily add custom I/O plugins and adapt to different deployment scenarios. This flexibility makes it suitable for a wide range of data processing tasks, from simple ETL jobs to complex data workflows.


## ✨ Key Features

*   **Modular Pipeline Design:** Thanks to [Hamilton](https://github.com/apache/hamilton), you can define your data processing logic in Python modules, using functions as nodes in a directed acyclic graph (DAG).
*   **Configuration-Driven:** Define pipeline parameters, execution logic, and scheduling declaratively using simple YAML files.
*   **Job Queue Integration:** Built-in support for asynchronous execution with **RQ (Redis Queue)** for distributed task queues, background processing, and time-based scheduling.
*   **Extensible I/O Plugins:** Connect to various data sources and destinations (CSV, JSON, Parquet, DeltaTable, DuckDB, PostgreSQL, MySQL, MSSQL, Oracle, MQTT, SQLite, and more).
*   **Unified Project Interface:** Interact with your pipelines via:
    *   **FlowerPowerProject API:** A unified interface for both synchronous and asynchronous pipeline execution, job queue management, and worker control.
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
uv pip install flowerpower[rq] # For RQ job queue support
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
    job_queue_type='rq'
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

Open `conf/project.yml` and define your project name and job queue backend. FlowerPower now uses RQ (Redis Queue) as its job queue system:

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
    from flowerpower import FlowerPowerProject
    
    # Load the project
    project = FlowerPowerProject.load('.')
    
    # Execute the pipeline synchronously
    result = project.run('hello_world')
    ```  

#### 2. Asynchronous Execution (Job Queues):

For scheduling, background execution, or distributed processing, leverage FlowerPower's job queue integration with RQ (Redis Queue). This is ideal for distributed task queues where workers can pick up jobs. 

First, install the RQ dependencies:
```bash
# Install RQ (Redis Queue) support
uv pip install flowerpower[rq]
```

*   **Note:** Ensure you have Redis running for RQ job queue functionality.

**a) Configuring the RQ Job Queue Backend:** 

Configuration of the job queue backend is done in your `conf/project.yml`. FlowerPower uses RQ (Redis Queue) as its job queue backend:

*   **RQ (Redis Queue) Requirements:**
    *   A **Redis server** running for job queuing and task coordination.
    *   Configure in `conf/project.yml`:
          ```yaml
          job_queue:
            type: rq
            backend:
              type: redis
              host: localhost
              port: 6379
              database: 0
              # Optional: username, password for Redis auth
              username: your_username  # if needed
              password: your_password  # if needed
              queues:
                - default
                - high
                - low
          ```
    
You can override the job queue backend configuration using environment variables, the `settings` module, or by modifying the configuration programmatically. This is useful for testing or when you want to avoid hardcoding values in your configuration files.

*   **Using the `settings` module:**
    Override RQ backend configuration:
    ```python
    from flowerpower import settings
    
    # Override RQ backend configuration
    settings.RQ_BACKEND_USERNAME = 'your_username'
    settings.RQ_BACKEND_PASSWORD = 'your_password'   
    ```
    See the `flowerpower/settings/job_queue.py` file for all available settings.

*   **Programmatic Configuration:**
    Modify configuration via the FlowerPowerProject:
    ```python
    from flowerpower import FlowerPowerProject

    project = FlowerPowerProject.load('.')
    project.job_queue_manager.cfg.backend.username = 'your_username'
    project.job_queue_manager.cfg.backend.password = 'your_password'
    ```

*  **Using Environment Variables:**
    Use a `.env` file or set them in your environment:
    ```
    FP_JOB_QUEUE_TYPE=rq

    # RQ (Redis Queue) backend
    FP_RQ_BACKEND_USERNAME=your_username
    FP_RQ_BACKEND_PASSWORD=your_password
    FP_RQ_BACKEND_HOST=localhost
    FP_RQ_BACKEND_PORT=6379
    ```


**b) Add Job to Queue:** 
Run your pipeline using the job queue system. This allows you to schedule jobs, run them in the background, or distribute them across multiple workers.

*   **Via CLI:**
    ```bash
    # Submit the pipeline to the job queue and return the job ID (non-blocking)
    flowerpower pipeline add-job hello_world --base_dir . 
    
    # Run the pipeline via job queue and wait for result (blocking)
    flowerpower pipeline run-job hello_world --base_dir . 
    ```
*   **Via Python:**
    
    ```python
    from flowerpower import FlowerPowerProject
    
    # Load the project
    project = FlowerPowerProject.load('.')

    # Enqueue the pipeline for execution (non-blocking)
    job_id = project.enqueue('hello_world')
    
    # Schedule the pipeline for future/recurring execution
    schedule_id = project.schedule('hello_world', cron="0 9 * * *")  # Daily at 9 AM
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
    from flowerpower import FlowerPowerProject
    
    # Load the project
    project = FlowerPowerProject.load('.')
    
    # Start a single worker (blocking)
    project.start_worker()
    
    # Start a worker pool (multiple workers)
    project.start_worker_pool(num_workers=4, background=True)
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

*   **`conf/project.yml`:** Defines global settings for your project, including the RQ job queue backend configuration and integrated `adapter`s (like Hamilton Tracker, MLflow, etc.).
*   **`conf/pipelines/*.yml`:** Each file defines a specific pipeline. It contains:
    *   `params`: Input parameters for your Hamilton functions.
    *   `run`: Execution details like target outputs (`final_vars`), Hamilton runtime `config`, and `executor` settings.
    *   `schedule`: Defines when the pipeline should run automatically (using `cron`, `interval`, or `date`).
    *   `adapter`: Pipeline-specific overrides for adapter settings.

## 🛠️ Basic Usage

You can interact with FlowerPower pipelines through multiple interfaces:

**Python API (Recommended):**
```python
from flowerpower import FlowerPowerProject

# Load the project
project = FlowerPowerProject.load('.')

# Run a pipeline synchronously
result = project.run('hello_world')

# Enqueue a pipeline for background execution
job_id = project.enqueue('hello_world')

# Schedule a pipeline
schedule_id = project.schedule('hello_world', cron="0 9 * * *")

# Start workers
project.start_worker_pool(num_workers=4, background=True)
```

**CLI:**
```bash
# Run a pipeline manually
flowerpower pipeline run hello_world --base_dir .

# Add a job to the queue
flowerpower pipeline add-job hello_world --base_dir .

# Schedule a pipeline
flowerpower pipeline schedule hello_world --base_dir .

# Start job queue worker
flowerpower job-queue start-worker --base_dir .

# List all available commands
flowerpower --help
```

## 🔧 Direct Module Usage

While the unified `FlowerPowerProject` interface is recommended for most use cases, you can also use the pipeline and job queue modules directly for more granular control or when you only need specific functionality.

### Pipeline-Only Usage

If you only need pipeline execution without job queue functionality, you can use the `PipelineManager` directly:

```python
from flowerpower.pipeline import PipelineManager

# Initialize pipeline manager
pm = PipelineManager(base_dir='.')

# Create a new pipeline
pm.new(name='my_pipeline')

# Run a pipeline synchronously
result = pm.run(
    name='my_pipeline',
    inputs={'param': 'value'},
    final_vars=['output_var']
)

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
- When you don't need background processing or scheduling
- Lightweight applications with minimal dependencies

### Job Queue-Only Usage

If you need job queue functionality for general task processing (not necessarily pipelines), you can use the job queue managers directly:

```python
import datetime as dt
from flowerpower.job_queue import JobQueueManager

# Initialize job queue manager with RQ backend
jqm = JobQueueManager(
    type='rq',
    name='my_worker',
    base_dir='.'
)

# Define a simple task function
def add_numbers(x: int, y: int) -> int:
    """Simple task that adds two numbers."""
    return x + y

def process_data(data: dict) -> dict:
    """More complex task that processes data."""
    result = {
        'processed': True,
        'count': len(data.get('items', [])),
        'timestamp': str(dt.datetime.now())
    }
    return result

# Enqueue jobs for immediate execution
job1 = jqm.enqueue(add_numbers, 5, 10)
job2 = jqm.enqueue(process_data, {'items': [1, 2, 3, 4, 5]})

# Enqueue jobs with delays
job3 = jqm.enqueue_in(300, add_numbers, 20, 30)  # Run in 5 minutes
job4 = jqm.enqueue_at(dt.datetime(2025, 1, 1, 9, 0), process_data, {'items': []})

# Schedule recurring jobs
schedule_id = jqm.add_schedule(
    func=process_data,
    func_kwargs={'data': {'items': []}},
    cron="0 */6 * * *",  # Every 6 hours
    schedule_id="data_processing_job"
)

# Start a worker to process jobs (blocking)
jqm.start_worker()

# Or start multiple workers in background
jqm.start_worker_pool(num_workers=4, background=True)

# Get job results
result1 = jqm.get_job_result(job1)
print(f"Addition result: {result1}")

# Clean up
jqm.stop_worker_pool()
```

**Alternatively, use RQManager directly for more RQ-specific features:**

```python
from flowerpower.job_queue.rq import RQManager

# Initialize RQ manager with custom configuration
rq_manager = RQManager(
    name='specialized_worker',
    base_dir='.',
    log_level='DEBUG'
)

# Use RQ-specific features
job = rq_manager.add_job(
    func=add_numbers,
    func_args=(100, 200),
    queue_name='high_priority',
    timeout=300,
    retry=3,
    result_ttl=3600
)

# Start worker for specific queues
rq_manager.start_worker(
    queue_names=['high_priority', 'default'],
    background=True
)

# Monitor jobs and queues
jobs = rq_manager.get_jobs()
schedules = rq_manager.get_schedules()

print(f"Active jobs: {len(jobs)}")
print(f"Active schedules: {len(schedules)}")
```

**When to use Job Queue-only approach:**
- General task processing and background jobs
- When you need fine-grained control over job queue behavior
- Microservices that only handle specific job types
- Integration with existing RQ-based systems
- When you don't need Hamilton-based pipeline functionality

### Combining Both Approaches

You can also combine both managers for custom workflows:

```python
from flowerpower.pipeline import PipelineManager
from flowerpower.job_queue import JobQueueManager

# Initialize both managers
pm = PipelineManager(base_dir='.')
jqm = JobQueueManager(type='rq', name='combined_worker', base_dir='.')

# Create a custom function that runs a pipeline
def run_pipeline_task(pipeline_name: str, inputs: dict = None):
    """Custom task that executes a pipeline."""
    result = pm.run(pipeline_name, inputs=inputs)
    return result

# Enqueue pipeline execution as a job
job_id = jqm.enqueue(
    run_pipeline_task,
    'my_pipeline',
    {'param': 'value'}
)

# Start worker to process the pipeline jobs
jqm.start_worker()
```

**Benefits of FlowerPowerProject vs Direct Usage:**

| Approach | Benefits | Use Cases |
|----------|----------|-----------|
| **FlowerPowerProject** | - Unified interface<br>- Automatic dependency injection<br>- Simplified configuration<br>- Best practices built-in | - Most applications<br>- Rapid development<br>- Full feature integration |
| **Pipeline-only** | - Lightweight<br>- No Redis dependency<br>- Simple synchronous execution | - Testing<br>- Simple workflows<br>- No background processing needed |
| **Job Queue-only** | - Fine-grained control<br>- Custom job types<br>- Existing RQ integration | - Microservices<br>- Custom task processing<br>- Non-pipeline jobs |

## 🖥️ UI

The FlowerPower web UI (Hamilton UI) provides a graphical interface for monitoring and managing your pipelines. It allows you to visualize pipeline runs, schedules, and potentially manage configurations.

```bash
# Start the web UI
flowerpower ui
```

## 📖 Documentation




## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details. (Placeholder - update with actual license)