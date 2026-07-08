# PipelineRegistry

**Module:** `flowerpower.pipeline.registry.PipelineRegistry`

The registry is a **compatibility facade** that delegates to three internal modules while preserving the historical public surface:

- [`PipelineCatalog`](#internal-ownership) — pipeline discovery, name derivation, listing, metadata, and presentation-free summary payloads.
- [`PipelineLoader`](#internal-ownership) — config/module loading, `Pipeline` construction, and cache/reload invalidation.
- `PipelineModuleResolver` — shared import-name normalization (package-root fallback, hyphens, reload policy).

Callers continue to use `PipelineRegistry` methods unchanged. The split only clarifies internal ownership for maintainers.

!!! note "Maintainer surface"
    The catalog, loader, and resolver are internal modules. They are not part of the public API and may change between minor versions. Use `PipelineRegistry` for all external access.

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

## Internal ownership

The registry does not implement discovery, loading, or caching itself. It composes three narrower modules and delegates every public method to them. This table maps each responsibility to its owner so maintainers know where to make changes.

| Responsibility | Owner | Registry facade method |
|:---------------|:------|:----------------------|
| Pipeline file discovery, name derivation | `PipelineCatalog` | `list_pipelines`, `pipelines` |
| Listing & metadata payloads | `PipelineCatalog` | `list_pipeline_info`, `show_pipelines` |
| Presentation-free summary assembly | `PipelineCatalog` | `get_summary`, `summary` |
| Config & module loading, cache invalidation | `PipelineLoader` | `load_config`, `load_module`, `clear_cache` |
| `Pipeline` instance construction | `PipelineLoader` | `get_pipeline` |
| Project config sync | `PipelineLoader` | `project_cfg` (delegated) |
| Import-name normalization | `PipelineModuleResolver` | (used by loader) |
| Rich rendering | `PipelinePresenter` | `show_summary`, `show_pipelines` |
| Lifecycle (create/delete) & hooks | `PipelineRegistry` (kept on facade) | `new`, `delete`, `add_hook` |

### Compatibility lifecycle shims

`new`, `delete`, `create_pipeline`, and `delete_pipeline` are backward-compatible shims preserved on the facade. They delegate to `PipelineCreator`. `create_pipeline` aliases `new`, and `delete_pipeline` aliases `delete`. Prefer `manager.creator.create_pipeline(...)` in new code.
