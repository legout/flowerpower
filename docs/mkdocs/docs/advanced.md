# Advanced Usage

Welcome to the advanced usage guide for FlowerPower. This document covers more complex configurations and use cases to help you get the most out of the library.

## Configuration Flexibility

FlowerPower offers multiple ways to configure your project, ensuring flexibility for different environments and workflows. The configuration is loaded in the following order of precedence:

1.  **Programmatic Overrides**: Highest priority.
2.  **Environment Variables**: Set in your shell or `.env` file.
3.  **Settings Module**: Values from the settings/general.py module.
4.  **YAML files**: conf/project.yml and conf/pipelines/*.yml for project and pipeline settings.

### Programmatic Configuration

You can override configuration settings directly in your Python code. This is useful for dynamic adjustments or for settings that are determined at runtime.

```python
from flowerpower import settings

# Override the default Redis host
settings.set('redis.host', 'localhost')

# You can also update nested settings
settings.set('pipelines.my_pipeline.retries', 3)
```

## Direct Module Usage

For fine-grained control, you can work directly with `PipelineManager`.


### `PipelineManager`

The `PipelineManager` is responsible for loading, validating, and executing data pipelines.

```python
from flowerpower.pipeline import PipelineManager
from flowerpower.cfg.pipeline.run import RunConfig

# Initialize the manager
pipeline_manager = PipelineManager()

# Access the registry to load a specific pipeline
pipeline = pipeline_manager.registry.get_pipeline("sales_etl")

# Execute the pipeline with RunConfig
result = pipeline.run(run_config=RunConfig(inputs={"input_data": "path/to/data.csv"}))
print(result)
```

## Hooks

Hooks allow you to inject custom logic at specific points in the pipeline lifecycle, such as pre-execution validation or post-execution logging.

### Adding Hooks

Use the `add_hook` method in the PipelineRegistry to add hooks to your pipeline.

```python
from flowerpower.pipeline import PipelineManager
from flowerpower.pipeline.hooks import HookType

manager = PipelineManager()

manager.registry.add_hook(
    name="my_pipeline",
    type=HookType.MQTT_BUILD_CONFIG,
    to=None,  # Defaults to hooks/my_pipeline/hook.py
    function_name="build_mqtt_config"  # Optional; defaults to type value
)
```

This appends a template function to the hook file. Customize the function in `hooks/my_pipeline/hook.py` to implement your logic, e.g., for MQTT config building.

Hooks are executed automatically during pipeline runs based on their type.
## Adapters

Integrate with popular MLOps and observability tools using adapters.

*   **Hamilton Tracker**: For dataflow and lineage tracking.
*   **MLflow**: For experiment tracking.
*   **OpenTelemetry**: For distributed tracing and metrics.

## Filesystem Abstraction

FlowerPower uses the library [`fsspec-utils`](https://legout.github.io/fsspec-utils) to provide a unified interface for interacting with different filesystems, including local storage, S3, and GCS. This allows you to switch between storage backends without changing your code.

### Security

FlowerPower includes built-in security features to prevent common vulnerabilities, such as directory traversal attacks. All file paths provided to configuration loaders and filesystem utilities are validated to ensure they are within the project's base directory.

```python
from flowerpower.utils.security import validate_file_path

# This will pass
validate_file_path("my/safe/path.yml")

# This will raise a ConfigPathError
try:
    validate_file_path("../../../etc/passwd")
except Exception as e:
    print(e)
```
## Extensible I/O Plugins

The FlowerPower plugin [`flowerpower-io`](https://legout.github.io/flowerpower-io) enhances FlowerPower's I/O capabilities, allowing you to connect to various data sources and sinks using a simple plugin architecture.

**Supported Types Include:**

*   CSV, JSON, Parquet
*   DeltaTable
*   DuckDB, PostgreSQL, MySQL, MSSQL, Oracle, SQLite
*   MQTT

To use a plugin, simply specify its type in your pipeline configuration.


## Troubleshooting

Here are some common issues and how to resolve them:

*   **Redis Connection Error**: Ensure your Redis server is running and accessible. Check the `redis.host` and `redis.port` settings in your configuration.
*   **Configuration Errors**: Use the `flowerpower pipeline show-summary` command to inspect the loaded configuration and identify any misconfigurations.
*   **Module Not Found**: Make sure your pipeline and task modules are in Python's path. You can add directories to the path using the `PYTHONPATH` environment variable.

!!! note
    For more detailed information, refer to the API documentation.