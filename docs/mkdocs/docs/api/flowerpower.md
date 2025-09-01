# FlowerPower

**Module:** [`flowerpower`](../../../src/flowerpower/__init__.py)

The `FlowerPower` name is an alias for the `create_project` function, which is the main entry point for initializing and interacting with FlowerPower projects. It acts as a factory for `FlowerPowerProject` instances, allowing users to load existing projects or create new ones.

**Note:** `FlowerPower` and `create_project` are functionally identical. `FlowerPower` is provided as an alias for convenience and backward compatibility.

## Initialization

### create_project (aliased as FlowerPower)

```python
create_project(name: str | None = None, base_dir: str | None = None, storage_options: dict | BaseStorageOptions | None = {}, fs: AbstractFileSystem | None = None, hooks_dir: str = settings.HOOKS_DIR) -> FlowerPowerProject
...
```

This function is called when you use `FlowerPower()` or `create_project()`. It checks if a project already exists at the specified `base_dir` and either loads it or initializes a new one.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str \| None` | The name of the project. If `None`, it defaults to the current directory name. | `None` |
| `base_dir` | `str \| None` | The base directory where the project will be created or loaded. If `None`, it defaults to the current working directory. | `None` |
| `storage_options` | `dict \| BaseStorageOptions \| None` | Storage options for the filesystem. | `{}` |
| `fs` | `AbstractFileSystem \| None` | An fsspec-compatible filesystem instance to use for file operations. If None, uses the `get_filesystem` helper. | `None` |
| `hooks_dir` | `str` | The directory where the project hooks will be stored. | `settings.HOOKS_DIR` |

**Returns:** `FlowerPowerProject` - An instance of `FlowerPowerProject` initialized with the new or loaded project.

#### Example

```python
from flowerpower import FlowerPower, create_project

# Initialize or load a project in the current directory using the alias
project = FlowerPower()

# Initialize or load a project in the current directory using the function name
project = create_project()

# Initialize or load a project with a specific name
project = FlowerPower(name="my-data-project")
```

For documentation on the `FlowerPowerProject` class and its methods, see [FlowerPowerProject](./flowerpowerproject.md).