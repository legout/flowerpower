# RunConfig

**Module:** [`flowerpower.cfg.pipeline.run`](https://github.com/legout/flowerpower/blob/main/src/flowerpower/cfg/pipeline/run.py)

The `RunConfig` class encapsulates all configuration parameters for pipeline execution. It is passed to [`FlowerPowerProject.run()`](./flowerpowerproject.md) and [`PipelineManager.run()`](./pipelinemanager.md). Runtime `kwargs` override matching fields in a `RunConfig`.

## Initialization

```python
RunConfig(
    inputs: dict | None = None,
    final_vars: list[str] | None = None,
    config: dict | None = None,
    cache: dict | bool | None = None,
    with_adapter: WithAdapterConfig | dict = WithAdapterConfig(),
    executor: ExecutorConfig | dict = ExecutorConfig(),
    retry: RetryConfig | dict | None = None,
    log_level: str | None = "INFO",
    max_retries: int = 3,
    retry_delay: int | float = 1,
    jitter_factor: float | None = 0.1,
    retry_exceptions: list[str] = ["Exception"],
    pipeline_adapter_cfg: dict | None = None,
    project_adapter_cfg: dict | None = None,
    adapter: dict[str, Any] | None = None,
    reload: bool = False,
    on_success: Callable | tuple | None = None,
    on_failure: Callable | tuple | None = None,
    additional_modules: list[str | Any] | None = None,
    async_driver: bool | None = None,
)
```

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `inputs` | `dict \| None` | Override pipeline inputs. | `{}` |
| `final_vars` | `list[str] \| None` | Output variables to return. | `[]` |
| `config` | `dict \| None` | Hamilton executor configuration. | `{}` |
| `cache` | `dict \| bool \| None` | Cache configuration or `False` to disable. | `False` |
| `with_adapter` | `WithAdapterConfig \| dict` | Adapter toggles for this run. | `WithAdapterConfig()` |
| `executor` | `ExecutorConfig \| dict` | Executor configuration. | `ExecutorConfig()` |
| `retry` | `RetryConfig \| dict \| None` | Canonical retry settings. | `None` |
| `log_level` | `str \| None` | Logging level. | `"INFO"` |
| `max_retries` | `int` | **Deprecated.** Use `retry`. | `3` |
| `retry_delay` | `int \| float` | **Deprecated.** Use `retry`. | `1` |
| `jitter_factor` | `float \| None` | **Deprecated.** Use `retry`. | `0.1` |
| `retry_exceptions` | `list[str]` | **Deprecated.** Use `retry`. | `["Exception"]` |
| `pipeline_adapter_cfg` | `dict \| None` | Pipeline-specific adapter settings. | `None` |
| `project_adapter_cfg` | `dict \| None` | Project-level adapter settings. | `None` |
| `adapter` | `dict[str, Any] \| None` | Custom adapter instances. | `None` |
| `reload` | `bool` | Force reload of pipeline configuration. | `False` |
| `on_success` | `Callable \| tuple \| None` | Callback on success. | `None` |
| `on_failure` | `Callable \| tuple \| None` | Callback on failure. | `None` |
| `additional_modules` | `list[str \| Any] \| None` | Additional Hamilton modules. | `None` |
| `async_driver` | `bool \| None` | Enable Hamilton's async driver. | `None` |

!!! warning "Deprecated top-level retry fields"
    The top-level `max_retries`, `retry_delay`, `jitter_factor`, and `retry_exceptions` fields are deprecated and emit a `DeprecationWarning`. Use the nested `retry` block (`RetryConfig`) or the builder helpers instead.

## Attributes

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `inputs` | `dict \| None` | Override pipeline inputs. |
| `final_vars` | `list[str] \| None` | Output variables to return. |
| `config` | `dict \| None` | Hamilton executor configuration. |
| `cache` | `dict \| bool \| None` | Cache configuration. |
| `executor` | `ExecutorConfig` | Executor configuration. |
| `with_adapter` | `WithAdapterConfig` | Adapter toggles. |
| `retry` | `RetryConfig` | Canonical retry configuration. |
| `pipeline_adapter_cfg` | `dict \| None` | Pipeline-specific adapter settings. |
| `project_adapter_cfg` | `dict \| None` | Project-level adapter settings. |
| `adapter` | `dict[str, Any] \| None` | Custom adapter instances. |
| `reload` | `bool` | Force reload configuration. |
| `log_level` | `str \| None` | Logging level. |
| `on_success` | `Callable \| tuple \| None` | Success callback. |
| `on_failure` | `Callable \| tuple \| None` | Failure callback. |
| `additional_modules` | `list[str \| Any] \| None` | Additional Hamilton modules for driver composition. |
| `async_driver` | `bool \| None` | Enable Hamilton's async driver. |

### WithAdapterConfig

**Module:** `flowerpower.cfg.pipeline.run.WithAdapterConfig`

Adapter toggles for a single run. Each field is a boolean.

| Field | Description |
|:------|:------------|
| `hamilton_tracker` | Enable Hamilton Tracker integration. |
| `mlflow` | Enable MLflow integration. |
| `ray` | Enable Ray distributed execution. |
| `progressbar` | Enable a progress bar. |
| `future` | Enable future adapters. |

```python
from flowerpower.cfg.pipeline.run import WithAdapterConfig

WithAdapterConfig(hamilton_tracker=True, mlflow=False, ray=False)
```

!!! note
    Use `hamilton_tracker` for tracking and lineage integration.

### RetryConfig

**Module:** `flowerpower.cfg.pipeline.run.RetryConfig`

| Field | Type | Description | Default |
|:------|:-----|:------------|:--------|
| `max_retries` | `int` | Maximum retry attempts. | `3` |
| `retry_delay` | `float` | Delay between retries in seconds. | `1.0` |
| `jitter_factor` | `float` | Random jitter factor. | `0.1` |
| `retry_exceptions` | `list[str]` | Exception names that trigger a retry. | `["Exception"]` |

### ExecutorConfig

**Module:** `flowerpower.cfg.pipeline.run.ExecutorConfig`

| Field | Type | Description | Default |
|:------|:-----|:------------|:--------|
| `type` | `str \| None` | Executor type. | `settings.EXECUTOR` |
| `max_workers` | `int \| None` | Max parallel tasks. | `settings.EXECUTOR_MAX_WORKERS` |
| `num_cpus` | `int \| None` | CPU allocation for distributed executors. | `settings.EXECUTOR_NUM_CPUS` |

## Methods

### copy

```python
copy(self) -> RunConfig
```

Create a shallow copy of the `RunConfig`.

```python
base = RunConfig(log_level="INFO")
custom = base.copy()
custom.final_vars = ["model"]
```

### update

```python
update(self, **kwargs) -> RunConfig
```

Update fields in place and return `self` for chaining.

```python
config = RunConfig()
config.update(
    inputs={"data_date": "2025-01-01"},
    final_vars=["model", "metrics"],
    log_level="DEBUG",
)
```

# RunConfigBuilder

**Module:** [`flowerpower.utils.config`](https://github.com/legout/flowerpower/blob/main/src/flowerpower/utils/config.py)

A fluent builder for constructing `RunConfig` instances. The builder is the recommended way to create complex run configurations.

```python
from flowerpower.utils.config import RunConfigBuilder

cfg = (
    RunConfigBuilder()
    .with_inputs({"data_date": "2025-01-01"})
    .with_final_vars(["model", "metrics"])
    .with_log_level("DEBUG")
    .with_retries(max_attempts=3, delay=1.0)
    .build()
)
```

!!! warning
    `RunConfigBuilder` must be imported from `flowerpower.utils.config`.

## Builder methods

All methods return `self` for method chaining.

| Method | Description |
|:-------|:------------|
| `with_inputs(inputs)` | Set pipeline input overrides. |
| `with_final_vars(final_vars)` | Set output variables to return. |
| `with_config(config)` | Set Hamilton executor configuration. |
| `with_cache(cache)` | Set cache configuration. |
| `with_executor(executor_cfg)` | Set executor configuration. |
| `with_executor_cfg(executor_cfg)` | Alias for `with_executor`. |
| `with_with_adapter_cfg(with_adapter_cfg)` | Set adapter toggles. |
| `with_pipeline_adapter_cfg(pipeline_adapter_cfg)` | Set pipeline-specific adapter settings. |
| `with_project_adapter_cfg(project_adapter_cfg)` | Set project-level adapter settings. |
| `with_adapter(adapter)` | Set custom adapter instances. |
| `with_async_driver(enabled)` | Enable or disable the async driver. |
| `with_additional_modules(modules)` | Set additional Hamilton modules. |
| `with_retry_config(max_retries, retry_delay, jitter_factor, retry_exceptions)` | Set retry values. |
| `with_retries(max_attempts, delay, jitter, exceptions)` | Alias for `with_retry_config`. |
| `with_logging(log_level)` | Set logging level. |
| `with_log_level(log_level)` | Alias for `with_logging`. |
| `with_callbacks(on_success, on_failure)` | Set both callbacks. |
| `with_on_success(on_success)` | Set success callback. |
| `with_on_failure(on_failure)` | Set failure callback. |
| `with_max_retries(max_retries)` | Deprecated convenience method. |
| `with_retry_delay(retry_delay)` | Deprecated convenience method. |
| `with_jitter_factor(jitter_factor)` | Deprecated convenience method. |
| `with_retry_exceptions(retry_exceptions)` | Deprecated convenience method. |
| `with_reload(reload)` | Set the reload flag. |
| `reset()` | Reset the builder to defaults. |
| `from_config(config)` | Class method: create a builder from an existing `RunConfig`. |
| `build()` | Build and return the `RunConfig`. |

## Examples

### Basic usage

```python
from flowerpower.utils.config import RunConfigBuilder
from flowerpower.pipeline import PipelineManager

manager = PipelineManager()

cfg = (
    RunConfigBuilder()
    .with_inputs({"data_date": "2025-01-01"})
    .with_final_vars(["model", "metrics"])
    .with_log_level("DEBUG")
    .build()
)

result = manager.run("ml_pipeline", run_config=cfg)
```

### Complex configuration

```python
from flowerpower.utils.config import RunConfigBuilder
from flowerpower.pipeline import PipelineManager

def success_handler(result):
    print(f"Pipeline succeeded: {result}")

def failure_handler(error):
    print(f"Pipeline failed: {error}")

cfg = (
    RunConfigBuilder()
    .with_inputs({"data_date": "2025-01-01", "batch_size": 32})
    .with_final_vars(["model", "metrics", "predictions"])
    .with_config({"model": "LogisticRegression", "params": {"C": 1.0}})
    .with_cache(False)
    .with_executor({"type": "threadpool", "max_workers": 4})
    .with_with_adapter_cfg({"hamilton_tracker": True})
    .with_project_adapter_cfg({"hamilton_tracker": {"api_url": "http://localhost:8241"}})
    .with_log_level("DEBUG")
    .with_retries(max_attempts=3, delay=1.0)
    .with_on_success(success_handler)
    .with_on_failure(failure_handler)
    .build()
)

manager = PipelineManager()
result = manager.run("ml_pipeline", run_config=cfg)
```

### Reusing configurations

```python
from flowerpower.utils.config import RunConfigBuilder
from flowerpower.pipeline import PipelineManager

base_config = (
    RunConfigBuilder()
    .with_log_level("INFO")
    .with_retries(max_attempts=2, delay=0.5)
    .build()
)

training_config = base_config.copy()
training_config.update(
    inputs={"mode": "training", "data_split": 0.8},
    final_vars=["model", "training_metrics"],
)

inference_config = base_config.copy()
inference_config.update(
    inputs={"mode": "inference", "model_path": "/path/to/model"},
    final_vars=["predictions", "inference_metrics"],
)

manager = PipelineManager()
manager.run("ml_pipeline", run_config=training_config)
manager.run("ml_pipeline", run_config=inference_config)
```
