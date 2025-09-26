# PipelineExecutor

**Module:** `flowerpower.pipeline.executor.PipelineExecutor`

The `PipelineExecutor` handles pipeline execution with comprehensive parameter handling. It is responsible for executing pipelines with various configurations, merging runtime parameters with pipeline defaults, and delegating to Pipeline objects for execution.

## Initialization

### __init__

```python
__init__(self, config_manager: PipelineConfigManager, registry: PipelineRegistry, project_context: Optional[Any] = None)
```

Initialize the pipeline executor.

**Parameters:**
- `config_manager`: Configuration manager for accessing pipeline configs
- `registry`: Pipeline registry for accessing pipeline objects
- `project_context`: Optional project context for execution

**Example:**
```python
from flowerpower.pipeline.config_manager import PipelineConfigManager
from flowerpower.pipeline.registry import PipelineRegistry

config_manager = PipelineConfigManager(...)
registry = PipelineRegistry(...)
executor = PipelineExecutor(config_manager, registry)
```

## Methods

### run

```python
run(self, name: str, run_config: RunConfig | None = None, **kwargs) -> dict[str, Any]
```

Execute a pipeline synchronously and return its results.

This is the main method for running pipelines directly. It handles configuration loading, adapter setup, and execution via Pipeline objects.

**Parameters:**
- `name`: Name of the pipeline to run. Must be a valid identifier.
- `run_config`: Run configuration object containing all execution parameters. If None, the default configuration from the pipeline will be used.
- `**kwargs`: Additional parameters to override the run_config. Supported parameters include inputs, final_vars, config, cache, executor_cfg, with_adapter_cfg, pipeline_adapter_cfg, project_adapter_cfg, adapter, reload, log_level, max_retries, retry_delay, jitter_factor, retry_exceptions, on_success, on_failure.

**Returns:**
- `dict[str, Any]`: Pipeline execution results, mapping output variable names to their computed values.

**Raises:**
- `ValueError`: If pipeline configuration cannot be loaded
- `ImportError`: If pipeline module cannot be imported
- `RuntimeError`: If execution fails due to pipeline or adapter errors

**Example:**
```python
from flowerpower.pipeline import PipelineManager
from flowerpower.cfg.pipeline.run import RunConfig

manager = PipelineManager()
executor = manager._executor  # Internal access, use manager.run() in practice

# Load pipeline configuration
pipeline_config = manager._config_manager.load_pipeline_config("my_pipeline")

# Initialize run_config with pipeline defaults if not provided
run_config = pipeline_config.run

# Merge kwargs into run_config if needed
if kwargs:
    run_config = merge_run_config_with_kwargs(run_config, kwargs)

# Set up logging for this specific run if log_level is provided
if run_config.log_level is not None:
    setup_logging(level=run_config.log_level)

# Get the pipeline object from registry
pipeline = manager._registry.get_pipeline(name="my_pipeline", project_context=manager._project_context)

# Execute the pipeline
return pipeline.run(run_config=run_config)
```

### run_async

```python
async run_async(self, name: str, run_config: RunConfig | None = None, **kwargs) -> dict[str, Any]
```

Execute a pipeline asynchronously and return its results.

**Parameters:**
- `name`: Name of the pipeline to run
- `run_config`: Run configuration object
- `**kwargs`: Additional parameters to override the run_config

**Returns:**
- `dict[str, Any]`: Results of pipeline execution

**Example:**
```python
from flowerpower.pipeline import PipelineManager
from flowerpower.cfg.pipeline.run import RunConfig

manager = PipelineManager()
executor = manager._executor

# Load pipeline configuration
pipeline_config = manager._config_manager.load_pipeline_config("my_pipeline")

# Initialize run_config with pipeline defaults if not provided
run_config = pipeline_config.run

# Merge kwargs into run_config if needed
if kwargs:
    run_config = merge_run_config_with_kwargs(run_config, kwargs)

# Set up logging for this specific run if log_level is provided
if run_config.log_level is not None:
    setup_logging(level=run_config.log_level)

# Get the pipeline object from registry
pipeline = manager._registry.get_pipeline(name="my_pipeline", project_context=manager._project_context)

# Execute the pipeline asynchronously
return await pipeline.run_async(run_config=run_config)