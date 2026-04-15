# PipelineManager

**Module:** `flowerpower.pipeline.PipelineManager`

The `PipelineManager` is the central class for managing pipeline operations in FlowerPower. It provides a unified interface for running pipelines and accessing sub-managers for registry, IO, visualization, and execution.

## Initialization

### __init__
```python
__init__(self, base_dir: str | None = None, storage_options: dict | Munch | BaseStorageOptions | None = None, fs: AbstractFileSystem | None = None, cfg_dir: str | None = None, pipelines_dir: str | None = None, log_level: str | None = None)
```

Initializes the `PipelineManager`, setting up project paths and loading configurations.

| Parameter         | Type                               | Description                                                                    |
|-------------------|------------------------------------|--------------------------------------------------------------------------------|
| `base_dir` | `str \| None` | The base directory of the project. Defaults to the current working directory. | `None` |
| `storage_options` | `dict \| Munch \| BaseStorageOptions \| None` | Configuration options for filesystem access (e.g., S3, GCS). | `{}` |
| `fs` | `AbstractFileSystem \| None` | An fsspec-compatible filesystem instance. | `None` |
| `cfg_dir` | `str \| None` | Override the default configuration directory name. | `settings.CONFIG_DIR` |
| `pipelines_dir` | `str \| None` | Override the default pipelines directory name. | `settings.PIPELINES_DIR` |
| `log_level` | `str \| None` | The logging level for the manager. | `None` |

**Example:**

```python
from flowerpower.pipeline import PipelineManager

# Initialize a manager for the project in the current directory
manager = PipelineManager()
```

## Sub-Managers

The `PipelineManager` exposes sub-managers as properties for direct access:

| Property | Type | Description |
|:---------|:-----|:------------|
| `registry` | `PipelineRegistry` | Handles pipeline registration, discovery, creation, deletion, hooks, and summaries. |
| `visualizer` | `PipelineVisualizer` | Handles pipeline DAG visualization (save/show). |
| `io` | `PipelineIOManager` | Handles pipeline import/export operations. |
| `executor` | `PipelineExecutor` | Handles pipeline execution. |

## Properties

| Property | Type | Description |
|:---------|:-----|:------------|
| `project_cfg` | `ProjectConfig` | Current project configuration. |
| `pipeline_cfg` | `PipelineConfig` | Current pipeline configuration. |
| `pipelines` | `list[str]` | List of available pipeline names (delegates to `registry.pipelines`). |
| `current_pipeline_name` | `str` | Name of the currently loaded pipeline. |
| `summary` | `dict[str, dict \| str]` | Summary of all pipelines (delegates to `registry.summary`). |

## Methods

### run
```python
run(self, name: str, run_config: RunConfig | None = None, **kwargs) -> dict[str, Any]
```

Execute a pipeline synchronously and return its results. Parameters related to retries (`max_retries`, `retry_delay`, `jitter_factor`, `retry_exceptions`) configure the internal retry mechanism.

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
| `executor_cfg` | `str \| dict \| ExecutorConfig \| None` | Execution configuration, can be: <br>- `str`: Executor type, one of "synchronous", "threadpool", "processpool", "ray", "dask" <br>- `dict`: Raw config, e.g. `{"type": "threadpool", "max_workers": 4}` <br>- `ExecutorConfig`: Structured config object | `None` |
| `with_adapter_cfg` | `dict \| WithAdapterConfig \| None` | Adapter settings for pipeline execution. Example: `{"hamilton_tracker": True, "mlflow": False}` | `None` |
| `pipeline_adapter_cfg` | `dict \| PipelineAdapterConfig \| None` | Pipeline-specific adapter settings. Example: `{"tracker": {"project_id": "123", "tags": {"env": "prod"}}}` | `None` |
| `project_adapter_cfg` | `dict \| ProjectAdapterConfig \| None` | Project-level adapter settings. Example: `{"hamilton_tracker": {"api_url": "http://localhost:8241"}}` | `None` |
| `adapter` | `dict[str, Any] \| None` | Custom adapter instance for pipeline Example: `{"ray_graph_adapter": RayGraphAdapter()}` | `None` |
| `reload` | `bool` | Force reload of pipeline configuration. | `False` |
| `log_level` | `str \| None` | Logging level for the execution. Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" | `None` |
| `max_retries` | `int \| None` | **Deprecated.** Legacy retry override; use `run_config.retry`. | `None` |
| `retry_delay` | `float \| None` | **Deprecated.** Legacy retry override; use `run_config.retry`. | `None` |
| `jitter_factor` | `float \| None` | **Deprecated.** Legacy retry override; use `run_config.retry`. | `None` |
| `retry_exceptions` | `tuple \| list \| None` | **Deprecated.** Legacy retry override; use `run_config.retry`. | `None` |
| `on_success` | `Callable \| tuple[Callable, tuple \| None, dict \| None] \| None` | Callback to run on successful pipeline execution. | `None` |
| `on_failure` | `Callable \| tuple[Callable, tuple \| None, dict \| None] \| None` | Callback to run on pipeline execution failure. | `None` |

**Returns:** `dict[str, Any]` - Pipeline execution results, mapping output variable names to their computed values.

**Raises:**

- `ValueError`: If pipeline name doesn't exist or configuration is invalid.
- `ImportError`: If pipeline module cannot be imported.
- `RuntimeError`: If execution fails due to pipeline or adapter errors.

#### Example

```python
from flowerpower.pipeline import PipelineManager
from flowerpower.cfg.pipeline.run import RunConfig
from flowerpower.utils.config import RunConfigBuilder

manager = PipelineManager()

# Simple execution
result = manager.run("my_pipeline")

# Using individual parameters (kwargs)
result = manager.run(
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
result = manager.run("ml_pipeline", run_config=config)

# Using RunConfigBuilder (recommended)
config = (
    RunConfigBuilder()
    .with_inputs({"data_date": "2025-01-01"})
    .with_final_vars(["model", "metrics"])
    .with_log_level("DEBUG")
    .with_retry_config(max_retries=3, retry_delay=1.0)
    .build()
)
result = manager.run("ml_pipeline", run_config=config)
```

### load_pipeline
```python
load_pipeline(self, name: str, reload: bool = False) -> PipelineConfig
```

Load or reload configuration for a specific pipeline.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str` | Name of the pipeline whose configuration to load. | |
| `reload` | `bool` | Force reload configuration even if already loaded. | `False` |

**Returns:** `PipelineConfig`

## Sub-Manager Usage

### Registry Operations

Use `manager.registry` for pipeline creation, deletion, discovery, hooks, and summaries:

```python
from flowerpower.pipeline import PipelineManager

manager = PipelineManager()

# Create a new pipeline
manager.registry.create_pipeline("data_transformation")
manager.registry.create_pipeline("data_transformation", overwrite=True)

# Delete a pipeline
manager.registry.delete_pipeline("old_pipeline")
manager.registry.delete_pipeline("test_pipeline", cfg=True, module=True)

# List pipelines
names = manager.registry.list_pipelines()
manager.registry.show_pipelines()

# Get pipeline summaries
summary = manager.registry.get_summary("my_pipeline")
all_summaries = manager.registry.get_summary()
manager.registry.show_summary("my_pipeline")

# Manage hooks
from flowerpower.pipeline.registry import HookType
manager.registry.add_hook(
    name="my_pipeline",
    type=HookType.MQTT_BUILD_CONFIG,
    to="mqtt",
    function_name="build_mqtt_config"
)
```

### IO Operations

Use `manager.io` for pipeline import/export:

```python
from flowerpower.pipeline import PipelineManager

manager = PipelineManager()

# Import a pipeline
manager.io.import_pipeline("new_pipeline", "/path/to/other/project")
manager.io.import_pipeline("s3_pipeline", "s3://bucket/project")

# Import multiple pipelines
manager.io.import_many(["pipeline1", "pipeline2"], "/path/to/other/project")

# Import all pipelines from a project
manager.io.import_all("/path/to/backup")

# Export a pipeline
manager.io.export_pipeline("my_pipeline", "/path/to/backup")

# Export multiple pipelines
manager.io.export_many(["pipeline1", "pipeline2"], "/path/to/backup")

# Export all pipelines
manager.io.export_all("/path/to/backup")
```

### Visualization Operations

Use `manager.visualizer` for DAG visualization:

```python
from flowerpower.pipeline import PipelineManager

manager = PipelineManager()

# Show DAG interactively
manager.visualizer.show_dag("my_pipeline")
manager.visualizer.show_dag("ml_pipeline", format="svg", raw=True)

# Save DAG to file
path = manager.visualizer.save_dag("my_pipeline", base_dir=".", format="png")
path = manager.visualizer.save_dag("my_pipeline", base_dir=".", format="svg", output_path="./custom.svg")
```

## Context Manager

`PipelineManager` supports use as a context manager:

```python
from flowerpower.pipeline import PipelineManager

with PipelineManager() as manager:
    result = manager.run("my_pipeline")
```
