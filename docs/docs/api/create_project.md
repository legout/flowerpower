# create_project

**Module:** [`flowerpower`](https://github.com/legout/flowerpower/blob/main/src/flowerpower/__init__.py)

The `create_project` function loads an existing FlowerPower project. It is also available as the [`FlowerPower`](./flowerpower.md) alias. To create a new project, use [`initialize_project`](./initialize_project.md) or [`FlowerPowerProject.new()`](./flowerpowerproject.md).

```python
create_project(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | BaseStorageOptions | None = None,
    fs: AbstractFileSystem | None = None,
    hooks_dir: str = settings.HOOKS_DIR,
) -> FlowerPowerProject
```

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str \| None` | Project name. If `None`, the current directory name is used. | `None` |
| `base_dir` | `str \| None` | Directory to load from. | Current working directory |
| `storage_options` | `dict \| BaseStorageOptions \| None` | Filesystem storage options. | `None` |
| `fs` | `AbstractFileSystem \| None` | fsspec-compatible filesystem instance. | `None` |
| `hooks_dir` | `str` | Directory for project hooks. | `settings.HOOKS_DIR` |

**Returns:** `FlowerPowerProject`

**Raises:** `FileNotFoundError` if the project does not exist at `base_dir`.

### Example

```python
from flowerpower import create_project

project = create_project(base_dir=".")

# Non-existent projects raise FileNotFoundError
try:
    project = create_project(base_dir="./non_existent_project")
except FileNotFoundError as e:
    print(e)
```

```python
from flowerpower import FlowerPower

# Same function, exposed as a callable alias
project = FlowerPower(base_dir=".")
```
