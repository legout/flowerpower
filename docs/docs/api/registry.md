# PipelineRegistry

**Module:** `flowerpower.pipeline.registry.PipelineRegistry`

The PipelineRegistry manages discovery, listing, creation, and deletion of pipelines. It handles caching of pipeline data and provides methods for pipeline lifecycle management.

## Initialization

### from_filesystem

```python
@classmethod
from_filesystem(base_dir: str, fs: AbstractFileSystem | None = None, storage_options: dict | None = None) -> PipelineRegistry
```

Create a PipelineRegistry from filesystem parameters.

This factory method creates a complete PipelineRegistry instance by:
1. Creating the filesystem if not provided
2. Loading the ProjectConfig from the base directory
3. Initializing the registry with the loaded configuration

**Parameters:**
- `base_dir`: The base directory path for the FlowerPower project
- `fs`: Optional filesystem instance. If None, will be created from base_dir
- `storage_options`: Optional storage options for filesystem access

**Returns:** PipelineRegistry - A fully configured registry instance

**Raises:**
- ValueError: If base_dir is invalid or ProjectConfig cannot be loaded
- RuntimeError: If filesystem creation fails

**Example:**
```python
# Create registry from local directory
registry = PipelineRegistry.from_filesystem("/path/to/project")

# Create registry with S3 storage
registry = PipelineRegistry.from_filesystem(
    "s3://my-bucket/project",
    storage_options={"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
)
```

## Methods

### get_pipeline

```python
get_pipeline(self, name: str, project_context: FlowerPowerProject, reload: bool = False) -> Pipeline
```

Get a Pipeline instance for the given name.

This method creates a fully-formed Pipeline object by loading its configuration and Python module, then injecting the project context.

**Parameters:**
- `name`: Name of the pipeline to get
- `project_context`: Reference to the FlowerPowerProject
- `reload`: Whether to reload configuration and module from disk

**Returns:** Pipeline instance ready for execution

**Raises:**
- FileNotFoundError: If pipeline configuration or module doesn't exist
- ImportError: If pipeline module cannot be imported
- ValueError: If pipeline configuration is invalid

**Example:**
```python
from flowerpower import FlowerPowerProject

project = FlowerPowerProject.load(".")
registry = project.pipeline_manager.registry

pipeline = registry.get_pipeline("my_pipeline", project)
```

### new

```python
new(self, name: str, overwrite: bool = False)
```

Add a pipeline with the given name.

**Parameters:**
- `name`: Name for the new pipeline. Must be a valid Python identifier.
- `overwrite`: Whether to overwrite existing pipeline with same name. Defaults to False.

**Raises:**
- ValueError: If the configuration or pipeline path does not exist, or if the pipeline already exists.

**Example:**
```python
registry.new("my_new_pipeline")
```

### delete

```python
delete(self, name: str, cfg: bool = True, module: bool = False)
```

Delete a pipeline.

**Parameters:**
- `name`: Name of the pipeline to delete
- `cfg`: Whether to delete the config file. Defaults to True.
- `module`: Whether to delete the module file. Defaults to False.

**Returns:** None

**Raises:**
- FileNotFoundError: If the specified files do not exist.

**Example:**
```python
registry.delete("old_pipeline")
```

### show_pipelines

```python
show_pipelines(self) -> None
```

Print all available pipelines in a formatted table.

**Example:**
```python
registry.show_pipelines()
```

### list_pipelines

```python
list_pipelines(self) -> list[str]
```

Get a list of all available pipeline names.

**Returns:** List of pipeline names, sorted alphabetically.

**Example:**
```python
pipelines = registry.list_pipelines()
print(pipelines)
['data_ingestion', 'model_training', 'reporting']
```

### pipelines (Property)

```python
pipelines: list[str]
```

Get list of all available pipeline names.

**Returns:** List of pipeline names.

**Example:**
```python
print(registry.pipelines)
['data_ingestion', 'model_training', 'reporting']
```

### summary (Property)

```python
summary: dict[str, dict | str]
```

Get complete summary of all pipelines.

**Returns:** Full summary including configuration, code, and project settings for all pipelines.

**Example:**
```python
summary = registry.summary
for name, details in summary.items():
    print(f"{name}: {details.get('cfg', {}).get('type')}")
data_pipeline: batch
ml_pipeline: streaming
```

### get_summary

```python
get_summary(self, name: str | None = None, cfg: bool = True, code: bool = True, project: bool = True) -> dict[str, dict | str]
```

Get a detailed summary of pipeline(s) configuration and code.

**Parameters:**
- `name`: Specific pipeline to summarize. If None, summarizes all.
- `cfg`: Include pipeline configuration details. Default True.
- `code`: Include pipeline module code. Default True.
- `project`: Include project configuration. Default True.

**Returns:** Nested dictionary containing requested summaries.

**Example:**
```python
summary = registry.get_summary("data_pipeline")
print(summary["pipelines"]["data_pipeline"]["cfg"]["schedule"]["enabled"])
True
```

### add_hook

```python
add_hook(self, name: str, type: HookType, to: str | None = None, function_name: str | None = None) -> None
```

Add a hook to the pipeline module.

**Parameters:**
- `name`: The name of the pipeline
- `type`: The type of the hook.
- `to`: The name of the file to add the hook to. Defaults to the hook.py file in the pipelines hooks folder.
- `function_name`: The name of the function. If not provided uses default name of hook type.

**Returns:** None

**Raises:**
- ValueError: If the hook type is not valid

**Example:**
```python
from flowerpower.pipeline import HookType

registry.add_hook(
    name="data_pipeline",
    type=HookType.MQTT_BUILD_CONFIG,
    to="pre_execute_hook",
    function_name="my_pre_execute_function"
)
```

### clear_cache

```python
clear_cache(self, name: str | None = None)
```

Clear cached pipelines, configurations, and modules.

**Parameters:**
- `name`: If provided, clear cache only for this pipeline. If None, clear entire cache.

**Example:**
```python
registry.clear_cache("my_pipeline")  # Clear specific
registry.clear_cache()  # Clear all