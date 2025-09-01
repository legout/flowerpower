# Quickstart

Welcome to the FlowerPower quickstart guide! This guide will walk you through the process of creating a "Hello World" project to demonstrate the core functionalities of the library.

## Installation

First, ensure you have FlowerPower installed. We recommend using `uv` for a fast and reliable installation.

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install FlowerPower
uv pip install flowerpower
```

## 1. Initialize Your Project

You can create a new project using either the CLI or the Python API.

### Using the CLI

```bash
flowerpower init --name hello-flowerpower
cd hello-flowerpower
```

### Using the Python API

```python
from flowerpower import FlowerPowerProject

# Initialize a new project
project = FlowerPowerProject.init(
    name='hello-flowerpower'
)
```

This creates a standard project structure with `conf/` and `pipelines/` directories.

## 2. Configure Your Project

The `conf/project.yml` file contains global settings for your project.

```yaml
# conf/project.yml
name: hello-flowerpower
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

You can run your pipeline synchronously for quick tests.

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

### Advanced Pipeline Execution with RunConfig

For more control over pipeline execution, you can use the `RunConfig` class to configure execution parameters.

#### Using RunConfig Directly

```python
from flowerpower import FlowerPowerProject
from flowerpower.run_config import RunConfig

project = FlowerPowerProject.load('.')

# Create a configuration with custom parameters
config = RunConfig(
    inputs={"greeting_message": "Hi", "target_name": "FlowerPower"},
    final_vars=["full_greeting"],
    log_level="DEBUG"
)

result = project.run('hello_world', run_config=config)
print(result)
```

#### Using RunConfigBuilder (Recommended)

The `RunConfigBuilder` provides a fluent interface for building complex configurations:

```python
from flowerpower import FlowerPowerProject
from flowerpower.run_config import RunConfigBuilder

project = FlowerPowerProject.load('.')

# Build a configuration using the builder pattern
config = (
    RunConfigBuilder()
    .with_inputs({"greeting_message": "Hello", "target_name": "World"})
    .with_final_vars(["full_greeting"])
    .with_log_level("DEBUG")
    .with_retry_config(max_retries=3, retry_delay=1.0)
    .build()
)

result = project.run('hello_world', run_config=config)
print(result)
```

#### Mixing RunConfig with Individual Parameters

You can also combine `RunConfig` with individual parameters, where individual parameters take precedence:

```python
from flowerpower import FlowerPowerProject
from flowerpower.run_config import RunConfigBuilder

project = FlowerPowerProject.load('.')

# Create a base configuration
base_config = RunConfigBuilder().with_log_level("INFO").build()

# Run with base config but override specific parameters
result = project.run(
    'hello_world',
    run_config=base_config,
    inputs={"greeting_message": "Greetings", "target_name": "Universe"}
)
print(result)
```

For more details on managing your project, refer to the API documentation for `FlowerPowerProject`, `PipelineManager`, and `RunConfig`.