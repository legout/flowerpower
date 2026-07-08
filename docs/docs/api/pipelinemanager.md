# PipelineManager

**Module:** `flowerpower.pipeline.PipelineManager`

The `PipelineManager` is the central class for managing pipeline operations in a FlowerPower project. It provides a unified interface for running pipelines, discovering pipeline definitions, and accessing sub-managers for creation, execution, IO, and visualization.

## Initialization

```python
PipelineManager(
    base_dir: str | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    fs: AbstractFileSystem | None = None,
    cfg_dir: str = "conf",
    pipelines_dir: str = "pipelines",
    log_level: str | None = None,
)
```

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `base_dir` | `str \| None` | Base directory of the project. | Current working directory |
| `storage_options` | `dict \| BaseStorageOptions \| None` | Filesystem storage options (e.g., for S3 or GCS). | `{}` |
| `fs` | `AbstractFileSystem \| None` | fsspec-compatible filesystem instance. | `None` |
| `cfg_dir` | `str` | Name of the configuration directory. | `"conf"` |
| `pipelines_dir` | `str` | Name of the pipelines directory. | `"pipelines"` |
| `log_level` | `str \| None` | Logging level. | `None` |

### Example

```python
from flowerpower.pipeline import PipelineManager

manager = PipelineManager()
```

## Properties

| Property | Type | Description |
|:---------|:-----|:------------|
| `creator` | `PipelineCreator` | Creates and deletes pipelines. |
| `executor` | `PipelineExecutor` | Executes pipelines synchronously or asynchronously. |
| `registry` | `PipelineRegistry` | Pipeline discovery, summaries, and hooks. |
| `io` | `PipelineIOManager` | Pipeline import/export operations. |
| `visualizer` | `PipelineVisualizer` | DAG rendering and saving. |
| `pipelines` | `list[str]` | Names of all discovered pipelines. |
| `summary` | `dict` | Full summary of all pipelines. |
| `project_cfg` | `ProjectConfig` | Current project configuration. |
| `pipeline_cfg` | `PipelineConfig` | Configuration of the currently loaded pipeline. |
| `current_pipeline_name` | `str \| None` | Name of the currently loaded pipeline. |

!!! tip
    Discover pipelines via the `pipelines` and `summary` properties, or through `manager.registry.*` methods.

## Methods

### run

```python
run(
    self,
    name: str,
    run_config: RunConfig | None = None,
    **kwargs,
) -> dict[str, Any]
```

Execute a pipeline synchronously and return its results. Runtime `kwargs` override matching fields in `run_config`.

**Parameters:**

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str` | Name of the pipeline to run. | — |
| `run_config` | `RunConfig \| None` | Structured execution configuration. | `None` |
| `inputs` | `dict \| None` | Override pipeline inputs. | `None` |
| `final_vars` | `list[str] \| None` | Output variables to return. | `None` |
| `config` | `dict \| None` | Hamilton executor configuration. | `None` |
| `cache` | `dict \| None` | Cache configuration. | `None` |
| `executor_cfg` | `str \| dict \| ExecutorConfig \| None` | Executor configuration. | `None` |
| `with_adapter_cfg` | `dict \| WithAdapterConfig \| None` | Adapter toggles (e.g., `{"hamilton_tracker": True}`). | `None` |
| `pipeline_adapter_cfg` | `dict \| None` | Pipeline-specific adapter settings. | `None` |
| `project_adapter_cfg` | `dict \| None` | Project-level adapter settings. | `None` |
| `adapter` | `dict[str, Any] \| None` | Custom adapter instances. | `None` |
| `reload` | `bool` | Force reload of the pipeline configuration. | `False` |
| `log_level` | `str \| None` | Logging level for this run. | `None` |
| `on_success` | `Callable \| tuple \| None` | Callback on success. | `None` |
| `on_failure` | `Callable \| tuple \| None` | Callback on failure. | `None` |

!!! warning "Deprecated retry kwargs"
    The standalone `max_retries`, `retry_delay`, `jitter_factor`, and `retry_exceptions` kwargs are deprecated and emit a `DeprecationWarning`. Prefer `run_config.retry` or `RunConfigBuilder.with_retries()`.

### run_async

```python
run_async(
    self,
    name: str,
    run_config: RunConfig | None = None,
    **kwargs,
) -> dict[str, Any]
```

Execute a pipeline asynchronously using Hamilton's async driver. Returns an awaitable coroutine.

```python
result = await manager.run_async("my_pipeline", run_config=config)
```

### load_pipeline

```python
load_pipeline(self, name: str, reload: bool = False) -> PipelineConfig
```

Load or reload the configuration for a specific pipeline.

## Sub-manager usage

### Registry

```python
manager.registry.create_pipeline("data_transformation")
manager.registry.delete_pipeline("old_pipeline")
manager.registry.list_pipelines()
manager.registry.show_pipelines()
manager.registry.get_summary("my_pipeline")
manager.registry.show_summary("my_pipeline")
```

### IO

```python
manager.io.import_pipeline("new_pipeline", "/path/to/other/project")
manager.io.export_pipeline("my_pipeline", "/path/to/backup")
```

### Visualization

```python
manager.visualizer.show_dag("my_pipeline")
manager.visualizer.save_dag("my_pipeline", format="png")
```

## Context manager

```python
from flowerpower.pipeline import PipelineManager

with PipelineManager() as manager:
    result = manager.run("my_pipeline")
```
