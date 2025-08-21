# Quickstart

Welcome to the FlowerPower quickstart guide! This guide will walk you through the process of creating a "Hello World" project to demonstrate the core functionalities of the library.

## Installation

First, ensure you have FlowerPower installed. We recommend using `uv` for a fast and reliable installation.

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install FlowerPower with RQ for job queue support
uv pip install flowerpower[rq]
```

## 1. Initialize Your Project

You can create a new project using either the CLI or the Python API.

### Using the CLI

```bash
flowerpower init --name hello-flowerpower --job_queue_type rq
cd hello-flowerpower
```

### Using the Python API

```python
from flowerpower import FlowerPowerProject

# Initialize a new project with RQ job queue support
project = FlowerPowerProject.init(
    name='hello-flowerpower',
    job_queue_type='rq'
)
```

This creates a standard project structure with `conf/` and `pipelines/` directories.

## 2. Configure Your Project

The `conf/project.yml` file contains global settings for your project, including the job queue configuration.

```yaml
# conf/project.yml
name: hello-flowerpower
job_queue:
  type: rq
  backend:
    type: redis
    host: localhost
    port: 6379
    queues:
      - default
      - high
      - low
```

## 3. Create a Pipeline

Next, create a pipeline to define your data processing logic.

### Using the CLI

```bash
flowerpower pipeline new hello_world
```

### Using the Python API

```python
from flowerpower import FlowerPowerProject

project = FlowerPowerProject.load('.')
project.pipeline_manager.new(name='hello_world')
```

This generates `pipelines/hello_world.py` for your pipeline logic and `conf/pipelines/hello_world.yml` for its configuration.

## 4. Implement the Pipeline

Open `pipelines/hello_world.py` and add your Hamilton functions.

```python
# pipelines/hello_world.py
from pathlib import Path
from hamilton.function_modifiers import parameterize
from flowerpower.cfg import Config

# Load pipeline parameters
PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="hello_world"
).pipeline.h_params

@parameterize(**PARAMS.greeting_message)
def greeting_message(message: str) -> str:
    return f"{message},"

@parameterize(**PARAMS.target_name)
def target_name(name: str) -> str:
    return f"{name}!"

def full_greeting(greeting_message: str, target_name: str) -> str:
    """Combines the greeting and target."""
    print(f"Executing pipeline: {greeting_message} {target_name}")
    return f"{greeting_message} {target_name}"
```

## 5. Configure the Pipeline

In `conf/pipelines/hello_world.yml`, define the parameters and execution details for your pipeline.

```yaml
# conf/pipelines/hello_world.yml
params:
  greeting_message:
    message: "Hello"
  target_name:
    name: "World"

run:
  final_vars:
    - full_greeting

schedule:
  cron: "0 * * * *" # Run hourly
```

## 6. Run the Pipeline

You can run your pipeline synchronously for quick tests or asynchronously for scheduled and background jobs.

### Synchronous Execution

This is useful for debugging and local development.

#### Using the CLI

```bash
flowerpower pipeline run hello_world
```

#### Using the Python API

```python
from flowerpower import FlowerPowerProject

project = FlowerPowerProject.load('.')
result = project.run('hello_world')
print(result)
```

### Asynchronous Execution

For asynchronous execution, you need a running Redis server.

!!! note
    Ensure Redis is running before proceeding with asynchronous execution. You can use the provided Docker setup for a quick start:
    ```bash
    cd docker
    docker-compose up -d redis
    ```

#### Enqueue a Job

Add your pipeline to the job queue for background processing.

##### Using the CLI

```bash
flowerpower pipeline add-job hello_world
```

##### Using the Python API

```python
from flowerpower import FlowerPowerProject

project = FlowerPowerProject.load('.')
job_id = project.enqueue('hello_world')
print(f"Job enqueued with ID: {job_id}")
```

#### Start a Worker

Workers are required to process jobs from the queue.

##### Using the CLI

```bash
flowerpower job-queue start-worker
```

##### Using the Python API

```python
from flowerpower import FlowerPowerProject

project = FlowerPowerProject.load('.')
# Start a worker in the background
project.start_worker(background=True)
```

For more details on managing your project, refer to the API documentation for `FlowerPowerProject`, `PipelineManager`, and `JobQueueManager`.