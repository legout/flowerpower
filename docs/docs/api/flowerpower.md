# FlowerPower

**Module:** [`flowerpower`](../../../src/flowerpower/__init__.py)

The `FlowerPower` name is an alias for the `create_project` function. It is the primary entry point for loading FlowerPower projects. It acts as a factory for `FlowerPowerProject` instances for existing projects; use `initialize_project` or `FlowerPowerProject.new()` to create new projects.

**Note:** `FlowerPower` and `create_project` are functionally identical. `FlowerPower` is provided as an alias for convenience and backward compatibility.

## Initialization

### create_project (aliased as FlowerPower)

```python
create_project(name: str | None = None, base_dir: str | None = None, storage_options: dict | BaseStorageOptions | None = {}, fs: AbstractFileSystem | None = None, hooks_dir: str = settings.HOOKS_DIR) -> FlowerPowerProject
...
```

This function is called when you use `FlowerPower()` or `create_project()`. It loads an existing project at `base_dir`. If the project does not exist, it raises `FileNotFoundError` with guidance to initialize a new project.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str \| None` | The name of the project. If `None`, it defaults to the current directory name. | `None` |
| `base_dir` | `str \| None` | The base directory where the project will be created or loaded. If `None`, it defaults to the current working directory. | `None` |
| `storage_options` | `dict \| BaseStorageOptions \| None` | Storage options for the filesystem. | `{}` |
| `fs` | `AbstractFileSystem \| None` | An fsspec-compatible filesystem instance to use for file operations. If None, uses the `get_filesystem` helper. | `None` |
| `hooks_dir` | `str` | The directory where the project hooks will be stored. | `settings.HOOKS_DIR` |

**Returns:** `FlowerPowerProject` - An instance of `FlowerPowerProject` for the loaded project.

**Raises:** `FileNotFoundError` if the project does not exist at `base_dir`.

#### Example

```python
from flowerpower import FlowerPower, create_project

# Load a project in the current directory using the alias
project = FlowerPower()

# Load a project in a specific directory
project = create_project(base_dir="/path/to/existing/project")

# Initialize a new project instead of loading
from flowerpower import initialize_project
project = initialize_project(name="my-data-project")
```

For documentation on the `FlowerPowerProject` class and its methods, see [FlowerPowerProject](./flowerpowerproject.md).
