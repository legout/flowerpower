# Configuration

FlowerPower uses a hierarchical configuration system to manage project and pipeline settings. The main configuration classes are:

-   [`Config`](#config)
-   [`ProjectConfig`](#projectconfig)
-   [`PipelineConfig`](#pipelineconfig)
-   [`BaseConfig`](#baseconfig)

The `Config` class serves as a composite that combines `ProjectConfig` and `PipelineConfig`, providing a unified interface to access both project-level and pipeline-specific settings. All configuration classes inherit from `BaseConfig`, which provides common functionality for configuration management.

## Classes

### BaseConfig
**Module:** `flowerpower.cfg.base.BaseConfig`

The `BaseConfig` class is the foundation for all configuration classes in FlowerPower. It provides common functionality including YAML serialization/deserialization, dictionary conversion, and configuration manipulation methods.

**Methods:**

| Method | Description |
|:-------|:------------|
| `to_dict()` | Converts the configuration instance to a dictionary. |
| `to_yaml(path, fs)` | Saves the configuration to a YAML file using the specified filesystem. |
| `from_dict(data)` | Creates a configuration instance from a dictionary. |
| `from_yaml(path, fs)` | Loads a configuration instance from a YAML file. |
| `update(d)` | Updates this instance with values from the provided dictionary. |
| `merge_dict(d)` | Creates a copy of this instance and updates the copy with values from the provided dictionary. |
| `merge(source)` | Creates a copy of this instance and updates the copy with non-default values from the source struct. |

#### Example

```python
from flowerpower.cfg.base import BaseConfig

# Update configuration with dictionary values
config.update({"param1": "value1", "nested": {"key": "value"}})

# Create a new configuration with merged values
new_config = config.merge_dict({"param2": "value2"})

# Merge with another configuration instance
merged_config = config.merge(other_config)
```

### Config
**Module:** `flowerpower.cfg.Config`

The `Config` class is the main configuration class that combines project and pipeline settings. It serves as the central configuration manager and provides a unified interface to access both `ProjectConfig` and `PipelineConfig`.

**Attributes:**

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `pipeline` | `PipelineConfig` | A `PipelineConfig` object containing pipeline-specific settings. |
| `project` | `ProjectConfig` | A `ProjectConfig` object containing project-level settings. |
| `fs` | `AbstractFileSystem \| None` | Filesystem abstraction for I/O operations. |
| `base_dir` | `str \| Path \| None` | Base directory for the configuration. |
| `storage_options` | `dict \| Munch` | Options for filesystem operations. |

#### Example

```python
from flowerpower.cfg import Config

# Load default configuration
config = Config()

# Access project and pipeline settings
print(config.project.name)
print(config.pipeline.name)

# Load configuration from directory
config = Config.load(base_dir="my_project", name="project1", pipeline_name="data-pipeline")

# Save configuration
config.save(project=True, pipeline=True)
```

## Environment Overlays and YAML Interpolation

FlowerPower applies configuration from multiple sources with a predictable precedence:

1. Programmatic overrides at execution time (kwargs, `RunConfig`)
2. Environment overlays via namespaced variables `FP_PIPELINE__...` / `FP_PROJECT__...`
3. YAML files after environment interpolation (see below)
4. Global env shims like `FP_LOG_LEVEL`, `FP_EXECUTOR`, `FP_MAX_RETRIES` (used only if specific keys are not provided)
5. Code defaults

### Environment Overlays

- Nested keys are expressed with double-underscores and mapped to config trees.
- Examples:
  - `FP_PIPELINE__RUN__LOG_LEVEL=DEBUG`
  - `FP_PIPELINE__RUN__EXECUTOR__TYPE=threadpool`
  - `FP_PROJECT__ADAPTER__HAMILTON_TRACKER__API_KEY=...`
- Global shims:
  - `FP_LOG_LEVEL`, `FP_EXECUTOR`, `FP_EXECUTOR_MAX_WORKERS`, `FP_EXECUTOR_NUM_CPUS`
  - `FP_MAX_RETRIES`, `FP_RETRY_DELAY`, `FP_JITTER_FACTOR`
- Values are strictly coerced (bool/int/float); JSON values (objects/arrays) are supported.

### YAML Environment Interpolation

String values in YAML support Docker Compose–style variable expansion:

```yaml
run:
  log_level: ${FP_LOG_LEVEL:-INFO}
  executor: ${FP_PIPELINE__RUN__EXECUTOR:-{"type":"synchronous"}}
adapter:
  hamilton_tracker:
    api_key: ${HAMILTON_API_KEY:?Missing tracker key}
```

Supported syntax: `${VAR}`, `${VAR:-default}`, `${VAR-default}`, `${VAR:?err}`, `${VAR?err}`, `$${...}` to escape. If the final string parses as JSON, it is converted to the corresponding typed value.

### Retry Normalization

`RunConfig.retry` is the canonical place for retry settings. Legacy top-level fields (`max_retries`, `retry_delay`, `jitter_factor`, `retry_exceptions`) are still accepted but are normalized into the nested `retry` block on load and now emit `DeprecationWarning` when set explicitly. Update configuration files to prefer the nested structure (e.g. `retry: {max_retries: 3, retry_delay: 2.0}`). Environment shims (`FP_MAX_RETRIES`, etc.) continue to work but likewise trigger deprecation notices.

### ProjectConfig
**Module:** `flowerpower.cfg.ProjectConfig`

The `ProjectConfig` class manages project-level settings, including adapter configurations.

**Attributes:**

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `name` | `str` | The name of the project. |
| `adapter` | `AdapterConfig` | An `AdapterConfig` object for the project-level adapter settings. |

#### Example

```python
from flowerpower.cfg import ProjectConfig

# Load project configuration
project_config = ProjectConfig()

# Access project settings
print(project_config.name)
```

### PipelineConfig
**Module:** `flowerpower.cfg.PipelineConfig`

The `PipelineConfig` class manages pipeline-specific settings, including run settings, scheduling, parameters, and adapter configurations.

**Attributes:**

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `name` | `str` | The name of the pipeline. |
| `run` | `RunConfig` | A `RunConfig` object for pipeline execution settings. |
| `schedule` | `ScheduleConfig` | A `ScheduleConfig` object for pipeline scheduling. |
| `params` | `dict` | A dictionary of pipeline parameters. |
| `adapter` | `AdapterConfig` | An `AdapterConfig` object for pipeline-specific adapter settings. |

#### Example

```python
from flowerpower.cfg import PipelineConfig

# Load pipeline configuration
pipeline_config = PipelineConfig()

# Access pipeline settings
print(pipeline_config.name)
print(pipeline_config.run.executor)
```

### ExecutorConfig
**Module:** `flowerpower.cfg.ExecutorConfig`

Defines the configuration for the pipeline executor (synchronous or distributed backends).

Supported types: `"synchronous"`, `"threadpool"`, `"processpool"`, `"ray"`, `"dask"`.

**Attributes:**

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `type` | `str` | Executor type (see supported types). |
| `max_workers` | `int | None` | Max parallel tasks for thread/process executors. |
| `num_cpus` | `int | None` | CPU allocation for distributed executors (ray/dask). |

#### Examples

```python
from flowerpower.cfg import ExecutorConfig

# Synchronous (sequential) execution
ExecutorConfig(type="synchronous")

# Thread pool with 4 workers
ExecutorConfig(type="threadpool", max_workers=4)

# Ray with CPU allocation
ExecutorConfig(type="ray", num_cpus=4)
```

### WithAdapterConfig
**Module:** `flowerpower.cfg.WithAdapterConfig`

Defines settings for using adapters during pipeline execution.

**Attributes:**

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `adapter_name` | `str` | The name of the adapter. |
| `enabled` | `bool` | Whether the adapter is enabled. |
| `config` | `dict` | Adapter-specific configurations. |

#### Example

```python
from flowerpower.cfg import WithAdapterConfig

# Create a WithAdapterConfig
adapter_config = WithAdapterConfig(adapter_name="opentelemetry", enabled=True)
print(adapter_config.enabled)
```

### AdapterConfig
**Module:** `flowerpower.cfg.AdapterConfig`

A base class for adapter configurations, used for both project and pipeline-level settings.

**Attributes:**

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `type` | `str` | The type of adapter. |
| `config` | `dict` | A dictionary of adapter-specific configurations. |

#### Example

```python
from flowerpower.cfg import AdapterConfig

# Create an AdapterConfig
adapter_config = AdapterConfig(type="tracker", config={"project_id": "abc"})
print(adapter_config.type)
```
