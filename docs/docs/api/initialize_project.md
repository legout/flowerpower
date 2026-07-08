# initialize_project

**Module:** [`flowerpower.flowerpower`](https://github.com/legout/flowerpower/blob/main/src/flowerpower/flowerpower.py)

The `initialize_project` function creates a new FlowerPower project. It is a thin wrapper around [`FlowerPowerProject.new()`](./flowerpowerproject.md).

```python
initialize_project(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    fs: AbstractFileSystem | None = None,
    hooks_dir: str = settings.HOOKS_DIR,
    log_level: str | None = None,
) -> FlowerPowerProject
```

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str \| None` | Project name. If `None`, the current directory name is used. | `None` |
| `base_dir` | `str \| None` | Directory where the project will be created. | Current working directory |
| `storage_options` | `dict \| BaseStorageOptions \| None` | Filesystem storage options. | `None` |
| `fs` | `AbstractFileSystem \| None` | fsspec-compatible filesystem instance. | `None` |
| `hooks_dir` | `str` | Directory for project hooks. | `settings.HOOKS_DIR` |
| `log_level` | `str \| None` | Logging level for the project. | `None` |

**Returns:** `FlowerPowerProject`

**Raises:** `FileExistsError` if the project already exists and `overwrite` is not set.

!!! note
    `FlowerPowerProject.new()` supports `overwrite=True` for rebuilding an existing project. The `initialize_project` convenience wrapper does not expose that flag; use the class method directly when you need it.

### Example

```python
from flowerpower import initialize_project

project = initialize_project(name="my-new-project")

# Equivalent call with overwrite support
from flowerpower import FlowerPowerProject
project = FlowerPowerProject.new(name="my-new-project", overwrite=False)
```
