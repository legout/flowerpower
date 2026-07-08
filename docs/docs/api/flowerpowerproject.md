# FlowerPowerProject

**Module:** [`flowerpower.flowerpower.FlowerPowerProject`](https://github.com/legout/flowerpower/blob/main/src/flowerpower/flowerpower.py)

`FlowerPowerProject` represents a FlowerPower project. It provides methods to create a new project, load an existing one, and run pipelines.

## Lifecycle methods

!!! tip "Creating projects"
    To create a project, always use `FlowerPowerProject.new(...)`.

### new

```python
new(
    cls,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    fs: AbstractFileSystem | None = None,
    hooks_dir: str = settings.HOOKS_DIR,
    log_level: str | None = None,
    overwrite: bool = False,
) -> FlowerPowerProject
```

Create a new FlowerPower project.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str \| None` | Project name. | Current directory name |
| `base_dir` | `str \| None` | Directory to create the project in. | Current working directory |
| `storage_options` | `dict \| BaseStorageOptions \| None` | Filesystem storage options. | `None` |
| `fs` | `AbstractFileSystem \| None` | fsspec-compatible filesystem instance. | `None` |
| `hooks_dir` | `str` | Directory for hooks. | `settings.HOOKS_DIR` |
| `log_level` | `str \| None` | Logging level. | `None` |
| `overwrite` | `bool` | Overwrite an existing project. | `False` |

**Returns:** `FlowerPowerProject`

**Raises:** `FileExistsError` if the project already exists and `overwrite` is `False`.

### load

```python
load(
    cls,
    base_dir: str | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    fs: AbstractFileSystem | None = None,
    log_level: str | None = None,
) -> FlowerPowerProject | None
```

Load an existing project. Returns `None` if the project does not exist.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `base_dir` | `str \| None` | Directory to load from. | Current working directory |
| `storage_options` | `dict \| BaseStorageOptions \| None` | Filesystem storage options. | `None` |
| `fs` | `AbstractFileSystem \| None` | fsspec-compatible filesystem instance. | `None` |
| `log_level` | `str \| None` | Logging level. | `None` |

**Returns:** `FlowerPowerProject` if the project exists, otherwise `None`.

## Attributes

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `pipeline_manager` | `PipelineManager` | Manages pipelines within the project. |
| `name` | `str` | The project name. |

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

Execute a pipeline synchronously. This delegates to `self.pipeline_manager.run()` and accepts the same parameters.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str` | Name of the pipeline to run. | — |
| `run_config` | `RunConfig \| None` | Structured execution configuration. | `None` |
| `inputs` | `dict \| None` | Override pipeline inputs. | `None` |
| `final_vars` | `list[str] \| None` | Output variables to return. | `None` |
| `config` | `dict \| None` | Hamilton executor configuration. | `None` |
| `cache` | `dict \| None` | Cache configuration. | `None` |
| `executor_cfg` | `str \| dict \| ExecutorConfig \| None` | Executor configuration. | `None` |
| `with_adapter_cfg` | `dict \| WithAdapterConfig \| None` | Adapter toggles. | `None` |
| `pipeline_adapter_cfg` | `dict \| None` | Pipeline-specific adapter settings. | `None` |
| `project_adapter_cfg` | `dict \| None` | Project-level adapter settings. | `None` |
| `adapter` | `dict[str, Any] \| None` | Custom adapter instances. | `None` |
| `reload` | `bool` | Force reload of pipeline configuration. | `False` |
| `log_level` | `str \| None` | Logging level. | `None` |
| `on_success` | `Callable \| tuple \| None` | Callback on success. | `None` |
| `on_failure` | `Callable \| tuple \| None` | Callback on failure. | `None` |

!!! warning "Deprecated retry kwargs"
    The standalone `max_retries`, `retry_delay`, `jitter_factor`, and `retry_exceptions` kwargs are deprecated. Prefer `run_config.retry` or `RunConfigBuilder.with_retries()`.

**Returns:** `dict[str, Any]` — mapping output variable names to computed values.

!!! note
    `FlowerPowerProject` does not have `run_async`. Use the manager directly: `project.pipeline_manager.run_async(...)`.

### Example

```python
from flowerpower import FlowerPowerProject
from flowerpower.utils.config import RunConfigBuilder

project = FlowerPowerProject.new(name="my_project")
project = FlowerPowerProject.load(".")

# Run a pipeline
result = project.run("hello")

# With a RunConfig
config = (
    RunConfigBuilder()
    .with_inputs({"data_date": "2025-01-01"})
    .with_final_vars(["model", "metrics"])
    .with_log_level("DEBUG")
    .build()
)
result = project.run("ml_pipeline", run_config=config)

# Async execution via the manager
result = await project.pipeline_manager.run_async("ml_pipeline", run_config=config)
```
