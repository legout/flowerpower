# FlowerPowerProject

**Module:** [`flowerpower.flowerpower.FlowerPowerProject`](../../../src/flowerpower/flowerpower.py)

The `FlowerPowerProject` class represents an initialized FlowerPower project, providing an interface to manage pipelines and project-level settings.

## Initialization

### __init__

```python
__init__(self, pipeline_manager: PipelineManager)
...
```

Initializes a `FlowerPowerProject` instance. This constructor is typically called internally by `FlowerPowerProject.load()` or `FlowerPowerProject.new()`.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `pipeline_manager` | `PipelineManager` | An instance of `PipelineManager` to manage pipelines within this project. |

## Attributes

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `pipeline_manager` | `PipelineManager` | Manages pipelines within the project. |
| `name` | `str` | The name of the current project. |

## Methods

### run

```python
run(self, name: str, run_config: RunConfig | None = None, inputs: dict | None = None, final_vars: list[str] | None = None, config: dict | None = None, cache: dict | None = None, executor_cfg: str | dict | ExecutorConfig | None = None, with_adapter_cfg: dict | WithAdapterConfig | None = None, pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None, project_adapter_cfg: dict | ProjectAdapterConfig | None = None, adapter: dict[str, Any] | None = None, reload: bool = False, log_level: str | None = None, max_retries: int | None = None, retry_delay: float | None = None, jitter_factor: float | None = None, retry_exceptions: tuple | list | None = None, on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = None, on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = None) -> dict[str, Any]
...
```

Execute a pipeline synchronously and return its results.

This is a convenience method that delegates to the pipeline manager. It provides the same functionality as `self.pipeline_manager.run()`.

This method supports two primary ways of providing execution configuration:
1. Using a `RunConfig` object (recommended): Provides a structured way to pass all execution parameters.
2. Using individual parameters (`**kwargs`): Allows specifying parameters directly, which will override corresponding values in the `RunConfig` if both are provided.

When both `run_config` and individual parameters (`**kwargs`) are provided, the individual parameters take precedence over the corresponding values in `run_config`.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str` | Name of the pipeline to run. Must be a valid identifier. | |
| `run_config` | `RunConfig \| None` | Configuration object containing all execution parameters. See [RunConfig](./runconfig.md) for details. | `None` |
| `inputs` | `dict \| None` | Override pipeline input values. Example: `{"data_date": "2025-04-28"}` | `None` |
| `final_vars` | `list[str] \| None` | Specify which output variables to return. Example: `["model", "metrics"]` | `None` |
| `config` | `dict \| None` | Configuration for Hamilton pipeline executor. Example: `{"model": "LogisticRegression"}` | `None` |
| `cache` | `dict \| None` | Cache configuration for results. Example: `{"recompute": ["node1", "final_node"]}` | `None` |
| `executor_cfg` | `str \| dict \| ExecutorConfig \| None` | Execution configuration, can be: <br>- `str`: Executor name, e.g. "threadpool", "local" <br>- `dict`: Raw config, e.g. `{"type": "threadpool", "max_workers": 4}` <br>- `ExecutorConfig`: Structured config object | `None` |
| `with_adapter_cfg` | `dict \| WithAdapterConfig \| None` | Adapter settings for pipeline execution. Example: `{"opentelemetry": True, "tracker": False}` | `None` |
| `pipeline_adapter_cfg` | `dict \| PipelineAdapterConfig \| None` | Pipeline-specific adapter settings. Example: `{"tracker": {"project_id": "123", "tags": {"env": "prod"}}}` | `None` |
| `project_adapter_cfg` | `dict \| ProjectAdapterConfig \| None` | Project-level adapter settings. Example: `{"opentelemetry": {"host": "http://localhost:4317"}}` | `None` |
| `adapter` | `dict[str, Any] \| None` | Custom adapter instance for pipeline Example: `{"ray_graph_adapter": RayGraphAdapter()}` | `None` |
| `reload` | `bool` | Force reload of pipeline configuration. | `False` |
| `log_level` | `str \| None` | Logging level for the execution. Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" | `None` |
| `max_retries` | `int \| None` | Maximum number of retries for execution. | `None` |
| `retry_delay` | `float \| None` | Delay between retries in seconds. | `None` |
| `jitter_factor` | `float \| None` | Random jitter factor to add to retry delay | `None` |
| `retry_exceptions` | `tuple \| list \| None` | Exceptions that trigger a retry. | `None` |
| `on_success` | `Callable \| tuple[Callable, tuple | None, dict | None] \| None` | Callback to run on successful pipeline execution. | `None` |
| `on_failure` | `Callable \| tuple[Callable, tuple | None, dict | None] \| None` | Callback to run on pipeline execution failure. | `None` |

**Returns:** `dict[str, Any]` - Pipeline execution results, mapping output variable names to their computed values.

**Raises:**

- `ValueError`: If pipeline name doesn't exist or configuration is invalid.
- `ImportError`: If pipeline module cannot be imported.
- `RuntimeError`: If execution fails due to pipeline or adapter errors.

#### Example

```python
from flowerpower import FlowerPowerProject
from flowerpower.cfg.pipeline.run import RunConfig
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

project = FlowerPowerProject.load(".")

# Simple execution
result = project.run("my_pipeline")

# Using individual parameters (kwargs)
result = project.run(
    "ml_pipeline",
    inputs={"data_date": "2025-01-01"},
    final_vars=["model", "metrics"]
)

# Using RunConfig directly
config = RunConfig(
    inputs={"data_date": "2025-01-01"},
    final_vars=["model", "metrics"],
    log_level="DEBUG"
)
result = project.run("ml_pipeline", run_config=config)

# Using RunConfigBuilder from flowerpower.cfg.pipeline.builder (recommended)
config = (
    RunConfigBuilder()
    .with_inputs({"data_date": "2025-01-01"})
    .with_final_vars(["model", "metrics"])
    .with_log_level("DEBUG")
    .with_retry_config(max_retries=3, retry_delay=1.0)
    .build()
)
result = project.run("ml_pipeline", run_config=config)

# Mixing RunConfig with individual parameters (kwargs)
# Individual parameters take precedence over RunConfig values
base_config = RunConfigBuilder().with_log_level("INFO").build()
result = project.run(
    "ml_pipeline",
    run_config=base_config,
    inputs={"data_date": "2025-01-01"},  # Overrides inputs in base_config
    final_vars=["model"]  # Overrides final_vars in base_config
)
```

### load

```python
load(cls, base_dir: str | None = None, storage_options: dict | BaseStorageOptions | None = {}, fs: AbstractFileSystem | None = None, log_level: str | None = None) -> "FlowerPowerProject | None"
...
```

Load an existing FlowerPower project.

If the project does not exist, it returns `None` and logs an error message.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `base_dir` | `str \| None` | The base directory of the project. If `None`, it defaults to the current working directory. | `None` |
| `storage_options` | `dict \| BaseStorageOptions \| None` | Storage options for the filesystem. | `{}` |
| `fs` | `AbstractFileSystem \| None` | An instance of `AbstractFileSystem` to use for file operations. | `None` |
| `log_level` | `str \| None` | The logging level to set for the project. If `None`, it uses the default log level. | `None` |

**Returns:** `FlowerPowerProject | None` - An instance if the project exists, otherwise `None`.

#### Example

```python
from flowerpower import FlowerPowerProject

# Load a project from the current directory
project = FlowerPowerProject.load(".")

# Load a project from a specific path
project = FlowerPowerProject.load("/path/to/my/project")
```

### new

```python
new(cls, name: str | None = None, base_dir: str | None = None, storage_options: dict | BaseStorageOptions | None = {}, fs: AbstractFileSystem | None = None, hooks_dir: str = settings.HOOKS_DIR, log_level: str | None = None, overwrite: bool = False) -> "FlowerPowerProject"
...
```

Initialize a new FlowerPower project.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str \| None` | The name of the project. If `None`, it defaults to the current directory name. | `None` |
| `base_dir` | `str \| None` | The base directory where the project will be created. If `None`, it defaults to the current working directory. | `None` |
| `storage_options` | `dict \| BaseStorageOptions \| None` | Storage options for the filesystem. | `{}` |
| `fs` | `AbstractFileSystem \| None` | An instance of `AbstractFileSystem` to use for file operations. If None, uses the `get_filesystem` helper. | `None` |
| `hooks_dir` | `str` | The directory where the project hooks will be stored. | `settings.HOOKS_DIR` |
| `log_level` | `str \| None` | The logging level to set for the project. If `None`, it uses the default log level. | `None` |
| `overwrite` | `bool` | Whether to overwrite an existing project at the specified base directory. | `False` |

**Returns:** `FlowerPowerProject` - An instance of `FlowerPowerProject` initialized with the new project.

**Raises:** `FileExistsError`: If the project already exists at the specified base directory.

#### Example

```python
from flowerpower import FlowerPowerProject

# Initialize a new project in the current directory
project = FlowerPowerProject.new()

# Initialize a new project with a specific name
project = FlowerPowerProject.new(name="my-new-project")
```
