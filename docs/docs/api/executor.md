# PipelineExecutor

**Module:** `flowerpower.pipeline.executor.PipelineExecutor`

The `PipelineExecutor` handles pipeline execution with comprehensive parameter handling. It is responsible for merging runtime parameters with pipeline defaults and delegating to Hamilton's execution engine.

## Initialization

```python
PipelineExecutor(
    self,
    config_manager: PipelineConfigManager,
    registry: PipelineRegistry,
    project_context: Any | None = None,
)
```

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `config_manager` | `PipelineConfigManager` | Configuration manager for pipeline configs. |
| `registry` | `PipelineRegistry` | Registry for accessing pipeline objects. |
| `project_context` | `Any \| None` | Optional project context for execution. | `None` |

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

Execute a pipeline synchronously and return its results. This is the main method used internally by `PipelineManager.run()` and `FlowerPowerProject.run()`.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str` | Name of the pipeline. | — |
| `run_config` | `RunConfig \| None` | Structured execution configuration. | `None` |
| `**kwargs` | `Any` | Runtime overrides. | — |

**Returns:** `dict[str, Any]` — mapping output variables to computed values.

**Raises:**

- `ValueError`: if configuration is invalid.
- `ImportError`: if the pipeline module cannot be imported.
- `RuntimeError`: if execution fails.

```python
from flowerpower.pipeline import PipelineManager
from flowerpower.cfg.pipeline.run import RunConfig

manager = PipelineManager()
config = RunConfig(retry={"max_retries": 3, "retry_delay": 2.0})
results = manager.executor.run("my_pipeline", run_config=config)
```

### run_async

```python
async run_async(
    self,
    name: str,
    run_config: RunConfig | None = None,
    **kwargs,
) -> dict[str, Any]
```

Execute a pipeline asynchronously using Hamilton's async driver.

```python
results = await manager.executor.run_async("my_pipeline", run_config=config)
```

!!! tip
    In most code you will call `manager.run()` or `manager.run_async()` rather than invoking the executor directly.
