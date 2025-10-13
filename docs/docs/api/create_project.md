# create_project

**Module:** `flowerpower.flowerpower`

The `create_project` function either loads an existing FlowerPower project or raises an error if the project does not exist. It is a convenient top-level function.

```python
create_project(name: str | None = None, base_dir: str | None = None, storage_options: dict | BaseStorageOptions | None = {}, fs: AbstractFileSystem | None = None, hooks_dir: str = settings.HOOKS_DIR) -> FlowerPowerProject
```

Loads an existing FlowerPower project.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `name` | `str` &#124; `None` | The name of the project. Defaults to the current directory name. |
| `base_dir` | `str` &#124; `None` | The base directory where the project will be created or loaded from. Defaults to the current working directory. |
| `storage_options` | `dict` &#124; `BaseStorageOptions` &#124; `None` | Storage options for the filesystem. |
| `fs` | `AbstractFileSystem` &#124; `None` | An instance of AbstractFileSystem to use for file operations. |
| `hooks_dir` | `str` | The directory where the project hooks will be stored. |

**Returns:** A `FlowerPowerProject` instance.

**Raises:** `FileNotFoundError` if the project does not exist at the specified base directory.

## Example

```python
from flowerpower import create_project

# Load an existing project
project = create_project(base_dir=".")

# Attempt to load a non-existent project (will raise FileNotFoundError)
try:
    project = create_project(base_dir="./non_existent_project")
except FileNotFoundError as e:
    print(e)
```

```python
from flowerpower import FlowerPower

# Alias for create_project
project = FlowerPower(base_dir=".")