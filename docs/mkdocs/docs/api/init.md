# init

**Module:** `flowerpower.init`

The `init` function is a top-level function that initializes a new FlowerPower project. It is a convenient alias for `FlowerPowerProject.init()`.

```python
init(name: str | None = None, base_dir: str | None = None, storage_options: dict | BaseStorageOptions | None = None, fs: AbstractFileSystem | None = None, job_queue_type: str = settings.JOB_QUEUE_TYPE, hooks_dir: str = settings.HOOKS_DIR)
```

Initializes a new FlowerPower project.

| Parameter         | Type                               | Description                                                                    |
|-------------------|------------------------------------|--------------------------------------------------------------------------------|
| `name`            | `str` &#124; `None`                | The name of the project. Defaults to the current directory name.               |
| `base_dir`        | `str` &#124; `None`                | The base directory for the project. Defaults to the current working directory. |
| `storage_options` | `dict` &#124; `BaseStorageOptions` &#124; `None` | Storage options for the filesystem.                                            |
| `fs`              | `AbstractFileSystem` &#124; `None` | An fsspec-compatible filesystem instance.                                      |
| `job_queue_type`  | `str`                              | The type of job queue to use (e.g., "rq").                                     |
| `hooks_dir`       | `str`                              | The directory for project hooks.                                               |

**Returns:** A `FlowerPowerProject` instance.

**Raises:** `FileExistsError` if the project already exists.

## Example

```python
from flowerpower import init

# Initialize a new project
project = init(name="my-new-project", job_queue_type="rq")