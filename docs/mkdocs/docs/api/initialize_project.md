# initialize_project

**Module:** `flowerpower.flowerpower`

The `initialize_project` function initializes a new FlowerPower project. It is a convenient top-level function that wraps `FlowerPowerProject.new()`.

```python
initialize_project(name: str | None = None, base_dir: str | None = None, storage_options: dict | BaseStorageOptions | None = {}, fs: AbstractFileSystem | None = None, hooks_dir: str = settings.HOOKS_DIR, log_level: str | None = None, overwrite: bool = False) -> FlowerPowerProject
```

Initializes a new FlowerPower project.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `name` | `str` &#124; `None` | The name of the project. Defaults to the current directory name. |
| `base_dir` | `str` &#124; `None` | The base directory where the project will be created. Defaults to the current working directory. |
| `storage_options` | `dict` &#124; `BaseStorageOptions` &#124; `None` | Storage options for the filesystem. |
| `fs` | `AbstractFileSystem` &#124; `None` | An instance of AbstractFileSystem to use for file operations. |
| `hooks_dir` | `str` | The directory where the project hooks will be stored. |
| `log_level` | `str` &#124; `None` | The logging level to set for the project. If None, it uses the default log level. |
| `overwrite` | `bool` | If True, deletes existing project files and creates a new plain project. |

**Returns:** A `FlowerPowerProject` instance initialized with the new project.

**Raises:** `FileExistsError` if the project already exists at the specified base directory and `overwrite` is `False`.

## Example

```python
from flowerpower import initialize_project

# Initialize a new project
project = initialize_project(name="my-new-project")

# Overwrite an existing project
project = initialize_project(name="my-existing-project", overwrite=True)