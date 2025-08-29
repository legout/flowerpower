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

### ProjectConfig
**Module:** `flowerpower.cfg.ProjectConfig`

The `ProjectConfig` class manages project-level settings, including job queue and adapter configurations.

**Attributes:**

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `name` | `str` | The name of the project. |
| `job_queue` | `JobQueueConfig` | A `JobQueueConfig` object for the job queue settings. |
| `adapter` | `AdapterConfig` | An `AdapterConfig` object for the project-level adapter settings. |

#### Example

```python
from flowerpower.cfg import ProjectConfig

# Load project configuration
project_config = ProjectConfig()

# Access project settings
print(project_config.name)
print(project_config.job_queue.type)
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

Defines the configuration for the pipeline executor (e.g., "local", "threadpool").

**Attributes:**

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `type` | `str` | The type of executor (e.g., "local", "threadpool"). |
| `config` | `dict` | A dictionary of executor-specific configurations. |

#### Example

```python
from flowerpower.cfg import ExecutorConfig

# Create an ExecutorConfig
executor_config = ExecutorConfig(type="threadpool", config={"max_workers": 4})
print(executor_config.type)
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