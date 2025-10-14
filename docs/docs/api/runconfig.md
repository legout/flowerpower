# RunConfig

**Module:** [`flowerpower.cfg.pipeline.run`](../../../../src/flowerpower/cfg/pipeline/run.py)

The `RunConfig` class encapsulates all configuration parameters for pipeline execution in FlowerPower. It provides a structured way to pass execution settings to both `Pipeline.run()` and `PipelineManager.run()` methods.

## Initialization

### __init__
```python
__init__(
  self,
  inputs: dict[str, Any] | None = None,
  final_vars: list[str] | None = None,
  config: dict[str, Any] | None = None,
  cache: dict[str, Any] | bool | None = None,
  with_adapter: WithAdapterConfig | dict = WithAdapterConfig(),
  executor: ExecutorConfig | dict = ExecutorConfig(),
  log_level: str | None = "INFO",
  max_retries: int = 3,
  retry_delay: int | float = 1,
  jitter_factor: float | None = 0.1,
  retry_exceptions: list[str] = ["Exception"],
  pipeline_adapter_cfg: dict | None = None,
  project_adapter_cfg: dict | None = None,
  adapter: dict[str, Any] | None = None,
  reload: bool = False,
  on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
  on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
)
```

Initializes a `RunConfig` instance with execution parameters.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `inputs` | `dict[str, Any] \| None` | Override pipeline input values. Example: `{"data_date": "2025-04-28"}` | `None` |
| `final_vars` | `list[str] \| None` | Specify which output variables to return. Example: `["model", "metrics"]` | `None` |
| `config` | `dict[str, Any] \| None` | Configuration for Hamilton pipeline executor. Example: `{"model": "LogisticRegression"}` | `None` |
| `cache` | `dict[str, Any] \| bool \| None` | Cache configuration for results or `False` to disable. | `False` |
| `executor` | `ExecutorConfig \| dict` | Execution configuration; dict will be coerced to `ExecutorConfig`. | `ExecutorConfig()` |
| `with_adapter` | `WithAdapterConfig \| dict` | Adapter settings for pipeline execution; dict will be coerced to `WithAdapterConfig`. | `WithAdapterConfig()` |
| `pipeline_adapter_cfg` | `dict \| PipelineAdapterConfig \| None` | Pipeline-specific adapter settings. Example: `{"tracker": {"project_id": "123", "tags": {"env": "prod"}}}` | `None` |
| `project_adapter_cfg` | `dict \| ProjectAdapterConfig \| None` | Project-level adapter settings. Example: `{"opentelemetry": {"host": "http://localhost:4317"}}` | `None` |
| `adapter` | `dict[str, Any] \| None` | Custom adapter instance for pipeline Example: `{"ray_graph_adapter": RayGraphAdapter()}` | `None` |
| `reload` | `bool` | Force reload of pipeline configuration. | `False` |
| `log_level` | `str \| None` | Logging level: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" | `"INFO"` |
| `max_retries` | `int` | Maximum number of retries for execution. | `3` |
| `retry_delay` | `int \| float` | Delay between retries in seconds. | `1` |
| `jitter_factor` | `float \| None` | Random jitter factor to add to retry delay | `0.1` |
| `retry_exceptions` | `list[str]` | Exception class names to trigger a retry (converted to classes). | `["Exception"]` |
| `on_success` | `Callable \| tuple[Callable, tuple \| None, dict \| None] \| None` | Callback to run on successful pipeline execution. | `None` |
| `on_failure` | `Callable \| tuple[Callable, tuple \| None, dict \| None] \| None` | Callback to run on pipeline execution failure. | `None` |

## Attributes

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `inputs` | `dict[str, Any] \| None` | Override pipeline input values. |
| `final_vars` | `list[str] \| None` | Specify which output variables to return. |
| `config` | `dict[str, Any] \| None` | Configuration for Hamilton pipeline executor. |
| `cache` | `dict[str, Any] \| None` | Cache configuration for results. |
| `executor` | `ExecutorConfig` | Execution configuration. |
| `with_adapter` | `WithAdapterConfig` | Adapter settings for pipeline execution. |
| `pipeline_adapter_cfg` | `dict \| PipelineAdapterConfig \| None` | Pipeline-specific adapter settings. |
| `project_adapter_cfg` | `dict \| ProjectAdapterConfig \| None` | Project-level adapter settings. |
| `adapter` | `dict[str, Any] \| None` | Custom adapter instance for pipeline. |
| `reload` | `bool` | Force reload of pipeline configuration. |
| `log_level` | `str \| None` | Logging level for the execution. |
| `max_retries` | `int \| None` | Maximum number of retries for execution. |
| `retry_delay` | `float \| None` | Delay between retries in seconds. |
| `jitter_factor` | `float \| None` | Random jitter factor to add to retry delay. |
| `retry_exceptions` | `tuple \| list \| None` | Exceptions that trigger a retry. |
| `on_success` | `Callable \| tuple[Callable, tuple \| None, dict \| None] \| None` | Callback to run on successful pipeline execution. |
| `on_failure` | `Callable \| tuple[Callable, tuple \| None, dict \| None] \| None` | Callback to run on pipeline execution failure. |

## Methods

### copy
```python
copy(self) -> 'RunConfig'
```

Create a shallow copy of the RunConfig instance.

**Returns:** `RunConfig` - A new RunConfig instance with the same configuration.

#### Example

```python
from flowerpower.cfg.pipeline.run import RunConfig

# Create a base configuration
base_config = RunConfig(
    inputs={"data_date": "2025-01-01"},
    log_level="INFO"
)

# Create a copy and modify it
custom_config = base_config.copy()
custom_config.final_vars = ["model", "metrics"]
```

### update
```python
update(self, **kwargs) -> 'RunConfig'
```

Update the RunConfig with new values and return self for method chaining.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `**kwargs` | `Any` | Key-value pairs of attributes to update. |

**Returns:** `RunConfig` - The updated RunConfig instance (self).

#### Example

```python
from flowerpower.cfg.pipeline.run import RunConfig

# Create a base configuration
config = RunConfig()

# Update multiple attributes
config.update(
    inputs={"data_date": "2025-01-01"},
    final_vars=["model", "metrics"],
    log_level="DEBUG"
)
```

# RunConfigBuilder

**Module:** [`flowerpower.cfg.pipeline.builder`](../../../../src/flowerpower/cfg/pipeline/builder.py)

The `RunConfigBuilder` class provides a fluent interface for constructing `RunConfig` instances. It allows for method chaining and provides a more readable way to build complex configurations.

## Initialization

### __init__
```python
__init__(self)
```

Initializes a new `RunConfigBuilder` instance with default values.

## Methods

### with_inputs
```python
with_inputs(self, inputs: dict[str, Any]) -> 'RunConfigBuilder'
```

Set the input values for the pipeline execution.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `inputs` | `dict[str, Any]` | Input values for the pipeline. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

builder = RunConfigBuilder()
builder.with_inputs({"data_date": "2025-01-01", "batch_size": 32})
```

### with_final_vars
```python
with_final_vars(self, final_vars: list[str]) -> 'RunConfigBuilder'
```

Set the output variables to return from the pipeline execution.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `final_vars` | `list[str]` | List of output variable names. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

builder = RunConfigBuilder()
builder.with_final_vars(["model", "metrics", "predictions"])
```

### with_config
```python
with_config(self, config: dict[str, Any]) -> 'RunConfigBuilder'
```

Set the configuration for the Hamilton pipeline executor.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `config` | `dict[str, Any]` | Configuration for the executor. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

builder = RunConfigBuilder()
builder.with_config({"model": "LogisticRegression", "params": {"C": 1.0}})
```

### with_cache
```python
with_cache(self, cache: dict[str, Any]) -> 'RunConfigBuilder'
```

Set the cache configuration for the pipeline execution.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `cache` | `dict[str, Any]` | Cache configuration. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

builder = RunConfigBuilder()
builder.with_cache({"recompute": ["node1", "final_node"]})
```

### with_executor_config
```python
with_executor_config(self, executor_cfg: str | dict | ExecutorConfig) -> 'RunConfigBuilder'
```

Set the execution configuration for the pipeline.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `executor_cfg` | `str \| dict \| ExecutorConfig` | Execution configuration. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

# Using a string
builder = RunConfigBuilder()
builder.with_executor_config("threadpool")

# Using a dictionary
builder = RunConfigBuilder()
builder.with_executor_config({"type": "threadpool", "max_workers": 4})
```

### with_adapter_config
```python
with_adapter_config(self, with_adapter_cfg: dict | WithAdapterConfig) -> 'RunConfigBuilder'
```

Set the adapter settings for pipeline execution.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `with_adapter_cfg` | `dict \| WithAdapterConfig` | Adapter settings. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

builder = RunConfigBuilder()
builder.with_adapter_config({"opentelemetry": True, "tracker": False})
```

### with_pipeline_adapter_config
```python
with_pipeline_adapter_config(self, pipeline_adapter_cfg: dict | PipelineAdapterConfig) -> 'RunConfigBuilder'
```

Set the pipeline-specific adapter settings.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `pipeline_adapter_cfg` | `dict \| PipelineAdapterConfig` | Pipeline-specific adapter settings. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

builder = RunConfigBuilder()
builder.with_pipeline_adapter_config({
    "tracker": {"project_id": "123", "tags": {"env": "prod"}}
})
```

### with_project_adapter_config
```python
with_project_adapter_config(self, project_adapter_cfg: dict | ProjectAdapterConfig) -> 'RunConfigBuilder'
```

Set the project-level adapter settings.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `project_adapter_cfg` | `dict \| ProjectAdapterConfig` | Project-level adapter settings. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

builder = RunConfigBuilder()
builder.with_project_adapter_config({
    "opentelemetry": {"host": "http://localhost:4317"}
})
```

### with_adapter
```python
with_adapter(self, adapter: dict[str, Any]) -> 'RunConfigBuilder'
```

Set custom adapter instances for the pipeline.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `adapter` | `dict[str, Any]` | Custom adapter instances. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder
from some_module import RayGraphAdapter

builder = RunConfigBuilder()
builder.with_adapter({"ray_graph_adapter": RayGraphAdapter()})
```

### with_reload
```python
with_reload(self, reload: bool = True) -> 'RunConfigBuilder'
```

Set whether to force reload of pipeline configuration.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `reload` | `bool` | Whether to force reload. | `True` |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

builder = RunConfigBuilder()
builder.with_reload(True)
```

### with_log_level
```python
with_log_level(self, log_level: str) -> 'RunConfigBuilder'
```

Set the logging level for the execution.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `log_level` | `str` | Logging level. Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

builder = RunConfigBuilder()
builder.with_log_level("DEBUG")
```

### with_retry_config
```python
with_retry_config(self, max_retries: int | None = None, retry_delay: float | None = None, jitter_factor: float | None = None, retry_exceptions: tuple | list | None = None) -> 'RunConfigBuilder'
```

Set the retry configuration for the execution.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `max_retries` | `int \| None` | Maximum number of retries. | `None` |
| `retry_delay` | `float \| None` | Delay between retries in seconds. | `None` |
| `jitter_factor` | `float \| None` | Random jitter factor to add to retry delay. | `None` |
| `retry_exceptions` | `tuple \| list \| None` | Exceptions that trigger a retry. | `None` |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

builder = RunConfigBuilder()
builder.with_retry_config(
    max_retries=3,
    retry_delay=1.0,
    retry_exceptions=(ValueError, KeyError)
)
```

### with_success_callback
```python
with_success_callback(self, on_success: Callable | tuple[Callable, tuple | None, dict | None]) -> 'RunConfigBuilder'
```

Set the callback to run on successful pipeline execution.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `on_success` | `Callable \| tuple[Callable, tuple \| None, dict \| None]` | Callback function or tuple with function, args, and kwargs. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

def success_handler(result):
    print(f"Pipeline succeeded with result: {result}")

builder = RunConfigBuilder()
builder.with_success_callback(success_handler)
```

### with_failure_callback
```python
with_failure_callback(self, on_failure: Callable | tuple[Callable, tuple | None, dict | None]) -> 'RunConfigBuilder'
```

Set the callback to run on pipeline execution failure.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `on_failure` | `Callable \| tuple[Callable, tuple \| None, dict \| None]` | Callback function or tuple with function, args, and kwargs. |

**Returns:** `RunConfigBuilder` - The builder instance for method chaining.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

def failure_handler(error):
    print(f"Pipeline failed with error: {error}")

builder = RunConfigBuilder()
builder.with_failure_callback(failure_handler)
```

### build
```python
build(self) -> RunConfig
```

Build and return a `RunConfig` instance with the configured parameters.

**Returns:** `RunConfig` - A new RunConfig instance with the configured parameters.

#### Example

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

# Build a configuration
config = (
    RunConfigBuilder()
    .with_inputs({"data_date": "2025-01-01"})
    .with_final_vars(["model", "metrics"])
    .with_log_level("DEBUG")
    .with_retry_config(max_retries=3, retry_delay=1.0)
    .build()
)
```

## Usage Examples

### Basic Usage

```python
from flowerpower.cfg.pipeline.run import RunConfig
from flowerpower.cfg.pipeline.builder import RunConfigBuilder
from flowerpower.pipeline import PipelineManager

# Using RunConfig directly
config = RunConfig(
    inputs={"data_date": "2025-01-01"},
    final_vars=["model", "metrics"],
    log_level="DEBUG"
)

manager = PipelineManager()
result = manager.run("my_pipeline", run_config=config)

# Using RunConfigBuilder
config = (
    RunConfigBuilder()
    .with_inputs({"data_date": "2025-01-01"})
    .with_final_vars(["model", "metrics"])
    .with_log_level("DEBUG")
    .build()
)

result = manager.run("my_pipeline", run_config=config)
```

### Complex Configuration

```python
from flowerpower.cfg.pipeline.builder import RunConfigBuilder
from flowerpower.pipeline import PipelineManager

def success_handler(result):
    print(f"Pipeline succeeded: {result}")

def failure_handler(error):
    print(f"Pipeline failed: {error}")

# Build a complex configuration
config = (
    RunConfigBuilder()
    .with_inputs({"data_date": "2025-01-01", "batch_size": 32})
    .with_final_vars(["model", "metrics", "predictions"])
    .with_config({"model": "LogisticRegression", "params": {"C": 1.0}})
    .with_cache({"recompute": ["preprocessing"]})
    .with_executor_config({"type": "threadpool", "max_workers": 4})
    .with_adapter_config({"opentelemetry": True})
    .with_pipeline_adapter_config({"tracker": {"project_id": "123"}})
    .with_project_adapter_config({"opentelemetry": {"host": "localhost:4317"}})
    .with_log_level("DEBUG")
    .with_retry_config(max_retries=3, retry_delay=1.0)
    .with_success_callback(success_handler)
    .with_failure_callback(failure_handler)
    .build()
)

manager = PipelineManager()
result = manager.run("ml_pipeline", run_config=config)
```

### Reusing Configurations

```python
from flowerpower.cfg.pipeline.run import RunConfig
from flowerpower.cfg.pipeline.builder import RunConfigBuilder
from flowerpower.pipeline import PipelineManager

# Create a base configuration
base_config = (
    RunConfigBuilder()
    .with_log_level("INFO")
    .with_retry_config(max_retries=2, retry_delay=0.5)
    .build()
)

# Create specialized configurations by copying and modifying
training_config = base_config.copy()
training_config.update(
    inputs={"mode": "training", "data_split": 0.8},
    final_vars=["model", "training_metrics"]
)

inference_config = base_config.copy()
inference_config.update(
    inputs={"mode": "inference", "model_path": "/path/to/model"},
    final_vars=["predictions", "inference_metrics"]
)

manager = PipelineManager()

# Run with different configurations
training_result = manager.run("ml_pipeline", run_config=training_config)
inference_result = manager.run("ml_pipeline", run_config=inference_config)
