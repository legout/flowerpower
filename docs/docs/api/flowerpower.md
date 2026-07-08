# FlowerPower

**Module:** [`flowerpower`](https://github.com/legout/flowerpower/blob/main/src/flowerpower/__init__.py)

`FlowerPower` is an alias for the [`create_project`](./create_project.md) function. It is the primary entry point for loading an **existing** FlowerPower project. To create a new project, use [`initialize_project`](./initialize_project.md) or [`FlowerPowerProject.new()`](./flowerpowerproject.md).

## create_project (aliased as FlowerPower)

```python
create_project(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    fs: AbstractFileSystem | None = None,
    hooks_dir: str = settings.HOOKS_DIR,
) -> FlowerPowerProject
```

Loads an existing project. If the project does not exist at `base_dir`, it raises `FileNotFoundError`.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str \| None` | Project name. If `None`, the current directory name is used. | `None` |
| `base_dir` | `str \| None` | Directory to load from. | Current working directory |
| `storage_options` | `dict \| BaseStorageOptions \| None` | Filesystem storage options. | `None` |
| `fs` | `AbstractFileSystem \| None` | fsspec-compatible filesystem instance. | `None` |
| `hooks_dir` | `str` | Directory for project hooks. | `settings.HOOKS_DIR` |

**Returns:** `FlowerPowerProject` — the loaded project.

**Raises:** `FileNotFoundError` if the project does not exist.

!!! tip
    `FlowerPower(...)` and `create_project(...)` are identical. Use whichever reads more naturally in your code.

### Example

```python
from flowerpower import FlowerPower, create_project

# Load a project from the current directory
project = FlowerPower()

# Load from a specific path
project = create_project(base_dir="/path/to/existing/project")

# Create a new project instead
from flowerpower import initialize_project
project = initialize_project(name="my-data-project")
```
