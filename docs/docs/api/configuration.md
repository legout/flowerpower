# Configuration

FlowerPower uses a layered configuration system. Configuration is read from YAML files, environment overlays, and runtime parameters, with higher layers overriding lower layers.

## Precedence

1. Runtime `kwargs` and `RunConfig` fields
2. Environment overlays: `FP_PIPELINE__*` and `FP_PROJECT__*`
3. YAML files after `${VAR}` interpolation
4. Global env shims: `FP_LOG_LEVEL`, `FP_EXECUTOR`, `FP_EXECUTOR_MAX_WORKERS`, `FP_EXECUTOR_NUM_CPUS`, `FP_MAX_RETRIES`, `FP_RETRY_DELAY`, `FP_JITTER_FACTOR`
5. Code defaults

Nested keys in environment variables use double underscores. Values are strictly coerced and JSON strings are converted to objects or lists when possible.

```bash
export FP_PIPELINE__RUN__LOG_LEVEL=DEBUG
export FP_PROJECT__ADAPTER__HAMILTON_TRACKER__API_KEY=abc123
```

YAML interpolation supports Docker Compose–style expansion:

```yaml
run:
  log_level: ${FP_LOG_LEVEL:-INFO}
adapter:
  hamilton_tracker:
    api_key: ${HAMILTON_API_KEY:?Missing Hamilton Tracker key}
```

## Config

**Module:** `flowerpower.cfg.Config`

The composite configuration class that combines `ProjectConfig` and `PipelineConfig`.

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `pipeline` | `PipelineConfig` | Pipeline-specific configuration. |
| `project` | `ProjectConfig` | Project-level configuration. |
| `fs` | `AbstractFileSystem \| None` | Filesystem abstraction. |
| `base_dir` | `str \| Path \| None` | Base directory for the configuration. |
| `storage_options` | `dict` | Storage options for filesystem access. |

```python
from flowerpower.cfg import Config

config = Config.load(base_dir="my_project", pipeline_name="data-pipeline")
config.project.name
config.pipeline.params
```

## ProjectConfig

**Module:** `flowerpower.cfg.ProjectConfig`

Project-level configuration.

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `name` | `str \| None` | Project name. |
| `hooks_dir` | `str \| None` | Directory for hooks. |
| `adapter` | `AdapterConfig` | Project-level adapter settings. |

## PipelineConfig

**Module:** `flowerpower.cfg.PipelineConfig`

Pipeline-specific configuration. The `params` field is a plain dictionary. When the config is loaded, `h_params` is generated automatically from `params` using `to_h_params()` and is used inside pipeline modules via `PARAMS['function_name']`.

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `name` | `str \| None` | Pipeline name. |
| `params` | `dict` | Pipeline parameters. |
| `run` | `RunConfig` | Execution configuration. |
| `adapter` | `AdapterConfig` | Pipeline-specific adapter settings. |
| `h_params` | `dict` | Hamilton-formatted parameters, derived from `params`. |

```python
from flowerpower.cfg import PipelineConfig

pipeline_config = PipelineConfig()
print(pipeline_config.name)
print(pipeline_config.run.executor)
```

## RunConfig

**Module:** `flowerpower.cfg.pipeline.run.RunConfig`

Encapsulates all execution parameters. See the dedicated [RunConfig reference](./runconfig.md) for details.

## ExecutorConfig

**Module:** `flowerpower.cfg.pipeline.run.ExecutorConfig`

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `type` | `str \| None` | Executor type, e.g., `"synchronous"`, `"threadpool"`, `"processpool"`, `"ray"`. |
| `max_workers` | `int \| None` | Max parallel tasks for thread/process executors. |
| `num_cpus` | `int \| None` | CPU allocation for distributed executors. |

## WithAdapterConfig

**Module:** `flowerpower.cfg.pipeline.run.WithAdapterConfig`

Adapter toggles for a single run. Enable an adapter by setting the corresponding field to `True`.

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `hamilton_tracker` | `bool` | Enable Hamilton Tracker integration. |
| `mlflow` | `bool` | Enable MLflow integration. |
| `ray` | `bool` | Enable Ray distributed execution. |
| `progressbar` | `bool` | Enable a progress bar. |
| `future` | `bool` | Enable future adapters. |

!!! note
    Use `hamilton_tracker` for tracking and lineage integration.

```python
from flowerpower.cfg.pipeline.run import WithAdapterConfig

WithAdapterConfig(hamilton_tracker=True, mlflow=False)
```
