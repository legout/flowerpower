# Use Adapters

FlowerPower supports optional adapters for observability, experiment tracking, and distributed execution. Adapters are configured in `conf/project.yml` (and optionally per-pipeline in `conf/pipelines/<name>.yml`) and are toggled per run via `with_adapter_cfg`.

## Available adapters

The `with_adapter_cfg` toggle accepts the following fields from `WithAdapterConfig`:

| Field | Adapter | Purpose |
| --- | --- | --- |
| `hamilton_tracker` | Hamilton Tracker | Capture dataflow lineage and execution metadata. |
| `mlflow` | MLflow | Log runs, parameters, and artifacts to MLflow. |
| `ray` | Ray | Execute nodes across a Ray cluster. |
| `progressbar` | Progress bar | Show a terminal progress bar during the run. |
| `future` | Future | Reserved for upcoming adapters. |

All fields default to `false`. Enable only the ones you need.

## Adapter configuration

A generated `conf/project.yml` contains an `adapter` block like this:

```yaml
name: hello-world
adapter:
  hamilton_tracker:
    api_url: http://localhost:8241
    ui_url: http://localhost:8242
    api_key: null
    username: null
    verify: false
  mlflow:
    tracking_uri: null
    registry_uri: null
    artifact_location: null
  ray:
    ray_init_config: null
    shutdown_ray_on_completion: false
```

Set the URLs and credentials before enabling an adapter. For per-pipeline overrides, add an `adapter` block under `conf/pipelines/<name>.yml`.

## Run with the Hamilton Tracker

Enable the tracker at run time:

```python
from flowerpower import FlowerPowerProject

project = FlowerPowerProject.load('.')
result = project.run(
    'hello_world',
    with_adapter_cfg={'hamilton_tracker': True},
    final_vars=['full_greeting'],
)
```

Visualize tracked runs with the Hamilton UI:

```bash
pip install 'flowerpower[ui]'
flowerpower ui
```

The UI opens on `http://localhost:8242` by default. Tracker data is sent to the `api_url` configured in `conf/project.yml`.

## Run with MLflow

Enable MLflow and point it at a tracking server in `conf/project.yml`:

```yaml
adapter:
  mlflow:
    tracking_uri: http://localhost:5000
    registry_uri: null
    artifact_location: null
```

Then enable it on the run:

```python
result = project.run(
    'hello_world',
    with_adapter_cfg={'mlflow': True},
    final_vars=['full_greeting'],
)
```

## Run with Ray

Use Ray for distributed execution by installing the extra and enabling the Ray adapter:

```bash
pip install 'flowerpower[ray]'
```

```python
result = project.run(
    'hello_world',
    with_adapter_cfg={'ray': True},
    executor_cfg={'num_cpus': 4},
    final_vars=['full_greeting'],
)
```

Ray settings such as `ray_init_config` and `shutdown_ray_on_completion` are read from `conf/project.yml`.

## Layering and precedence

- Project-level adapter settings live in `conf/project.yml`.
- Per-pipeline settings in `conf/pipelines/<name>.yml` override the project defaults.
- Runtime `with_adapter_cfg` toggles which adapters are actually instantiated for that run.

!!! tip
    Keep sensitive credentials in environment variables and reference them in YAML with `${API_KEY}` or `${API_KEY:-default}`.

## Related

- [Asynchronous Execution](./async-execution.md)
- [CLI Reference](../cli.md)
