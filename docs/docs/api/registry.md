# PipelineRegistry

**Module:** `flowerpower.pipeline.registry.PipelineRegistry`

The registry manages pipeline discovery, creation, deletion, summaries, and hooks.

## Initialization

### from_filesystem

```python
from_filesystem(
    cls,
    base_dir: str,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | None = None,
) -> PipelineRegistry
```

Create a registry instance from a filesystem path.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `base_dir` | `str` | Project base directory. |
| `fs` | `AbstractFileSystem \| None` | fsspec-compatible filesystem. | `None` |
| `storage_options` | `dict \| None` | Storage options. | `None` |

```python
registry = PipelineRegistry.from_filesystem("/path/to/project")
```

## Methods

### new / create_pipeline

```python
new(self, name: str, overwrite: bool = False) -> None
create_pipeline(self, name: str, overwrite: bool = False) -> None
```

Create a new pipeline. `create_pipeline` is an alias for `new` and is the form used by the manager's `creator`.

```python
from flowerpower.pipeline import PipelineManager

manager = PipelineManager()
manager.creator.create_pipeline("data_transformation")
```

### delete / delete_pipeline

```python
delete(self, name: str, cfg: bool = True, module: bool = False) -> None
delete_pipeline(self, name: str, cfg: bool = True, module: bool = False) -> None
```

Delete a pipeline's configuration file, module, or both. `delete_pipeline` is an alias for `delete`.

```python
manager.registry.delete("old_pipeline", cfg=True, module=True)
```

### get_pipeline

```python
get_pipeline(
    self,
    name: str,
    project_context: FlowerPowerProject,
    reload: bool = False,
) -> Pipeline
```

Load a `Pipeline` instance, injecting the project context.

```python
pipeline = manager.registry.get_pipeline("my_pipeline", project)
```

### list_pipelines

```python
list_pipelines(self) -> list[str]
```

Return the sorted list of pipeline names.

```python
names = manager.registry.list_pipelines()
```

### show_pipelines

```python
show_pipelines(self) -> None
```

Print all available pipelines in a formatted table.

```python
manager.registry.show_pipelines()
```

### get_summary

```python
get_summary(
    self,
    name: str | None = None,
    cfg: bool = True,
    code: bool = True,
    project: bool = True,
) -> dict[str, dict | str]
```

Return a detailed summary of one or all pipelines. The summary contains configuration, code, and project sections.

```python
summary = manager.registry.get_summary("my_pipeline")
print(summary["pipelines"]["my_pipeline"]["cfg"]["name"])
```

### show_summary

```python
show_summary(
    self,
    name: str | None = None,
    cfg: bool = True,
    code: bool = True,
    project: bool = True,
    to_html: bool = False,
    to_svg: bool = False,
) -> str | None
```

Print or return a formatted summary of one or all pipelines.

```python
output = manager.registry.show_summary("my_pipeline", to_html=True)
```

### add_hook

```python
add_hook(
    self,
    name: str,
    type: HookType,
    to: str | None = None,
    function_name: str | None = None,
) -> None
```

Add a hook to a pipeline module.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `name` | `str` | Pipeline name. |
| `type` | `HookType` | Hook type. Only `MQTT_BUILD_CONFIG` is supported. |
| `to` | `str \| None` | Target file or node. | `None` |
| `function_name` | `str \| None` | Function name. | Defaults from hook type. |

```python
from flowerpower.pipeline.registry import HookType

manager.registry.add_hook(
    name="my_pipeline",
    type=HookType.MQTT_BUILD_CONFIG,
    function_name="build_mqtt_config",
)
```

### clear_cache

```python
clear_cache(self, name: str | None = None) -> None
```

Clear cached pipeline data. If `name` is provided, only that pipeline's cache is cleared.

```python
manager.registry.clear_cache("my_pipeline")
manager.registry.clear_cache()  # clear all
```

## Properties

| Property | Type | Description |
|:---------|:-----|:------------|
| `pipelines` | `list[str]` | Names of all discovered pipelines. |
| `summary` | `dict` | Full summary of all pipelines. |
| `project_cfg` | `ProjectConfig` | Current project configuration. |
