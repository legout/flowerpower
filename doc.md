# Introduction

FlowerPower is a Python framework for building, executing, and managing data processing pipelines. It provides a comprehensive set of tools to define complex workflows, manage their execution asynchronously, and integrate with various external systems. Key features include robust pipeline definition and execution capabilities, job queue management with support for backends like RQ and APScheduler, and flexible scheduling options (cron, interval, date-based). FlowerPower also offers a command-line interface (CLI) for easy project and pipeline management, MQTT integration for event-driven pipeline execution, and visualization tools for pipeline DAGs, including integration with Hamilton UI. Furthermore, it supports extensive configuration management, filesystem abstraction, and can be extended through adapters and hooks to fit diverse project needs.

# Installation

FlowerPower can be installed using pip.

Basic installation:
```bash
pip install flowerpower
```

FlowerPower offers several optional dependencies to enable extra features. You can install them based on your specific requirements:

- **UI**: For using the Hamilton UI for pipeline visualization.
  ```bash
  pip install flowerpower[ui]
  ```
- **MQTT**: For enabling MQTT integration for event-driven pipelines.
  ```bash
  pip install flowerpower[mqtt]
  ```
- **RQ**: For using RQ (Redis Queue) as the job queue backend.
  ```bash
  pip install flowerpower[rq]
  ```

It is recommended to only install the extras that are relevant to your project's needs to keep the environment lean.

# Project Setup

This section guides you through setting up a new FlowerPower project.

## 1. Initializing a Project

FlowerPower provides a convenient CLI command to initialize a new project structure.

**Command:**
```bash
flowerpower init --name <project_name> --base-dir <path_to_create_in> --job-queue-type <type>
```

**Explanation:**

*   `--name <project_name>`: Specifies the name of your project. If you are in a directory named `my_project`, FlowerPower can infer this as `my_project`.
*   `--base-dir <path_to_create_in>`: Defines the directory where the project structure will be created. Defaults to the current directory (`.`). If a directory with `<project_name>` already exists, it will use that; otherwise, it will create a new directory named `<project_name>`.
*   `--job-queue-type <type>`: Sets the default job queue system for the project. Only `rq` (Redis Queue) is supported. The default is `rq`. You can change this later in the project configuration.

In many cases, if you navigate to the desired parent directory for your project and your project directory is already named appropriately, you might only need to run:
```bash
flowerpower init
```
Or if you want to specify the job queue type:
```bash
flowerpower init --job-queue-type rq
```

## 2. Generated Directory Structure

Running `flowerpower init` creates the following directory structure:

```
<project_name>/
├── conf/
│   ├── project.yml           # Main project configuration
│   └── pipelines/            # Directory for individual pipeline configurations (e.g., pipeline_a.yml)
├── pipelines/                # Python modules for pipeline definitions
│   └── __init__.py
├── hooks/                    # Python modules for custom hooks
│   └── __init__.py
└── README.md                 # Basic project README
```

*   **`conf/`**: Contains all configuration files.
    *   **`conf/project.yml`**: The main configuration file for the entire project.
    *   **`conf/pipelines/`**: Holds YAML configuration files for each individual pipeline.
*   **`pipelines/`**: This is where you'll define your pipeline logic in Python modules.
*   **`hooks/`**:  Place your custom hook implementations (Python modules) here. Hooks allow you to extend or modify pipeline behavior at specific lifecycle points.
*   **`README.md`**: A template README file for your project.

## 3. Project Configuration (`conf/project.yml`)

The `conf/project.yml` file is central to your FlowerPower project, containing global settings that apply across all pipelines unless overridden.

Here are the main top-level keys you'll typically find and configure:

*   **`name: <project_name>`**:
    *   The name of your project, as provided during initialization.

*   **`job_queue:`**:
    *   Configuration for the job queue system used for asynchronous task execution.
    *   `type: rq`: Specifies to use RQ (only supported option).
    *   More detailed settings for RQ (e.g., Redis connection details) and APScheduler (e.g., job store configurations) are available and will be covered in the main "Configuration" section of this documentation.

*   **`adapter:`**:
    *   Configuration for various adapters to integrate FlowerPower with external systems.
    *   **`hamilton_tracker:`**: Settings for integrating with Hamilton UI for pipeline visualization and tracking.
        *   `username: <your_hamilton_username>`
        *   `api_url: <hamilton_api_url>`
        *   `ui_url: <hamilton_ui_url>`
        *   `api_key: <your_hamilton_api_key>`
        *   `verify: <true_or_false>` (whether to verify SSL certificates)
    *   **`mlflow:`**: Settings for MLflow integration for experiment tracking and model management.
        *   `tracking_uri: <mlflow_tracking_server_uri>`
        *   `registry_uri: <mlflow_model_registry_uri>`
        *   `artifact_location: <path_or_uri_for_artifacts>`
    *   **`opentelemetry:`**: Configuration for OpenTelemetry for distributed tracing.
        *   `host: <opentelemetry_collector_host>`
        *   `port: <opentelemetry_collector_port>`
    *   **`ray:`**: Configuration for using Ray as a distributed execution backend.
        *   `ray_init_config: {}` (A dictionary of arguments to pass to `ray.init()`, e.g., `{"address": "auto"}`)
        *   `shutdown_ray_on_completion: true` (Whether to automatically shut down Ray when the pipeline completes)

**Example `conf/project.yml`:**

```yaml
name: my_data_project

job_queue:
  type: rq
  # Detailed RQ/APScheduler settings (e.g., connection, stores)
  # will be covered in the "Configuration" section.
  # For RQ, you might have:
  # redis_host: localhost
  # redis_port: 6379

adapter:
  hamilton_tracker:
    username: user@example.com
    api_url: https://hamilton.example.com/api
    ui_url: https://hamilton.example.com
    api_key: your_secret_api_key
    verify: true
  mlflow:
    tracking_uri: http://localhost:5000
  # opentelemetry:
  #   host: localhost
  #   port: 4317
  # ray:
  #   ray_init_config:
  #     address: 'auto'
  #   shutdown_ray_on_completion: true
```

Detailed options for `job_queue` and other configurations will be elaborated upon in the dedicated "Configuration" section.

# Creating and Configuring Pipelines

## Overview

FlowerPower pipelines are built using the Hamilton (Directed Acyclic Graph - DAG) framework. The core logic of your pipeline is defined as a series of Python functions within a dedicated Python module. Each function represents a node in the DAG, transforming inputs and producing outputs.

Alongside the Python module, each pipeline has an associated YAML configuration file (`.yml`). This file allows you to define pipeline parameters, execution settings, scheduling, and adapter configurations specific to that pipeline.

## Creating a New Pipeline (`flowerpower pipeline new`)

To scaffold a new pipeline, FlowerPower provides a CLI command:

```bash
flowerpower pipeline new <pipeline_name>
```

Replace `<pipeline_name>` with the desired name for your pipeline (e.g., `data_processing_main`). This command will generate two key files:

1.  **`pipelines/<pipeline_name>.py`**:
    *   This is the Python module where you will define the logic of your pipeline using Hamilton functions.
    *   **Example `pipelines/my_data_pipeline.py`:**
        ```python
        # pipelines/my_data_pipeline.py
        import pandas as pd

        # Example: A function that takes a configuration parameter
        def data_source_path(default_path: str = "data/input.csv") -> str:
            """Specifies the path to the input data."""
            return default_path

        def raw_data(data_source_path: str) -> pd.DataFrame:
            """Loads raw data from the specified path."""
            print(f"Loading data from: {data_source_path}")
            # In a real scenario, ensure the file exists or handle exceptions
            # For this example, we'll create a dummy DataFrame if path is placeholder
            if data_source_path == "data/input.csv": # Example default
                 return pd.DataFrame({'value': [1, 2, 3, 4, 5]})
            return pd.read_csv(data_source_path)

        def transformed_data(raw_data: pd.DataFrame, scale_factor: float = 2.0) -> pd.DataFrame:
            """Transforms the raw data by scaling a column."""
            # scale_factor could come from pipeline params in the YAML config
            transformed = raw_data.copy()
            transformed['value'] = raw_data['value'] * scale_factor
            print(f"Applied scale_factor: {scale_factor}")
            return transformed

        def final_output(transformed_data: pd.DataFrame) -> pd.DataFrame:
            """Represents the final output of this pipeline segment."""
            print("Final data:")
            print(transformed_data.head())
            return transformed_data
        ```

2.  **`conf/pipelines/<pipeline_name>.yml`**:
    *   This YAML file is dedicated to configuring the behavior and parameters of the corresponding pipeline. Its structure and options are detailed below.

## Defining Pipeline Logic (`pipelines/<pipeline_name>.py`)

The Python module (e.g., `pipelines/my_data_pipeline.py`) is the heart of your pipeline. It contains a collection of Python functions that collectively define the Hamilton DAG.

*   **Hamilton Functions**: Each function typically takes inputs (which are outputs of other functions or external parameters) and produces an output. Type hints are crucial for Hamilton to understand the dependencies and construct the DAG.
*   **External Resources**: For detailed guidance on writing Hamilton functions, including how to use decorators like `@config.when` (for conditional execution based on configuration), `@tag` (for metadata and selecting subsets of the DAG), input types, and output types, please refer to the official [Hamilton Documentation](https://hamilton.dagworks.io/en/latest/).

**Conceptual Example (re-iterating from above):**
```python
# pipelines/my_data_pipeline.py
import pandas as pd

def raw_data(data_path: str) -> pd.DataFrame:
    # data_path would typically be injected via pipeline params (see YAML config)
    return pd.read_csv(data_path)

def transformed_data(raw_data: pd.DataFrame, scale_factor: float) -> pd.DataFrame:
    # scale_factor could also come from pipeline params
    transformed = raw_data.copy()
    transformed['value'] = raw_data['value'] * scale_factor
    return transformed

def final_output(transformed_data: pd.DataFrame) -> pd.DataFrame:
    # This function produces one of the desired final outputs of the pipeline
    return transformed_data
```

## Pipeline Configuration (`conf/pipelines/<pipeline_name>.yml`)

The `conf/pipelines/<pipeline_name>.yml` file provides fine-grained control over a specific pipeline's execution, parameters, scheduling, and adapter integrations. Settings here can override or augment global configurations from `conf/project.yml`.

Here are the main top-level keys you'll work with:

### `run:`
Controls the execution behavior of the pipeline.

*   `inputs: {param1: value1, ...}`:
    *   Provides default input values for the Hamilton driver's `inputs` argument. These are values that might change with each run but are not part of the static configuration.
    *   Can be overridden at runtime (e.g., via CLI arguments or programmatic execution).
    *   Example: `inputs: { "user_id": 123, "target_date": "2024-01-15" }`

*   `final_vars: [var1, var2, ...]`:
    *   A list of Hamilton function names whose outputs are considered the final results of the pipeline. This corresponds to the Hamilton driver's `final_vars` argument.
    *   Example: `final_vars: ["final_output", "validation_summary"]`

*   `config: {hamilton_config_key: value, ...}`:
    *   Configuration passed directly to the Hamilton driver's `config` parameter. This is how you control Hamilton's behavior, such as selecting different function implementations using `@config.when`.
    *   Example: `config: { "data_version": "v2", "feature_set": "extended" }`

*   `cache: true | false | {setting: value, ...}`:
    *   Configures caching behavior for pipeline results.
    *   `true`: Enables caching for all nodes (default behavior might depend on global settings).
    *   `false`: Disables caching for this pipeline.
    *   Object for fine-grained control:
        *   `recompute: ["node_to_always_recompute", "another_node"]`: List of nodes to always recompute, ignoring cached values.
        *   (Other cache settings specific to the chosen cache backend might be available).

*   `with_adapter:`:
    *   Boolean flags to enable or disable specific adapters for this pipeline run, overriding project-level defaults.
    *   `hamilton_tracker: true`
    *   `mlflow: true`
    *   `opentelemetry: false`
    *   `progressbar: true`
    *   `ray: false` (Relevant if Ray is a potential executor)

*   `executor:`:
    *   Defines the default execution environment for this pipeline.
    *   `type: <local | threadpool | processpool | ray | dask>`: Specifies the executor type.
        *   `local`: Single-threaded, in-process execution (Hamilton's default).
        *   `threadpool`: Uses a pool of threads.
        *   `processpool`: Uses a pool of processes.
        *   `ray`: Distributes execution using Ray.
        *   `dask`: Distributes execution using Dask.
    *   `max_workers: int`: For `threadpool` and `processpool` executors, the number of worker threads/processes.
    *   `num_cpus: int`: For `ray` executor, can specify the number of CPUs for the Ray cluster if initialized by FlowerPower.

*   `log_level: <DEBUG | INFO | WARNING | ERROR | CRITICAL>`:
    *   Sets a specific logging level for this pipeline, overriding the global log level.

*   `max_retries: int`:
    *   The maximum number of times to retry the pipeline (or a failing task within it, depending on executor granularity) if it fails. Default: 0.
*   `retry_delay: float`:
    *   The delay in seconds between retries. Default: 5.0.
*   `jitter_factor: float`:
    *   A factor to randomize the retry delay (0.0 to 1.0). `delay * (1 + random.uniform(-jitter_factor, jitter_factor))`. Default: 0.0 (no jitter).
*   `retry_exceptions: ["ExceptionClassName", "module.ExceptionName", ...]`
    *   A list of exception class names (as strings) that should trigger a retry. If empty or not provided, all exceptions might be retried.

### `schedule:`
Defines a default schedule for the pipeline. This schedule is used if `flowerpower pipeline schedule_all` is run, or if `flowerpower pipeline schedule <pipeline_name>` is called without specific trigger arguments (like `--cron` or `--interval`).

*   `cron: <cron_string | {minute: "0", hour: "*/2", ...}>`:
    *   Defines a cron-like schedule.
    *   Can be a standard cron string (e.g., `"0 */2 * * *"` for every two hours at the start of the hour).
    *   Or an object with fields like `year`, `month`, `day`, `week`, `day_of_week`, `hour`, `minute`, `second`.
    *   Example: `cron: {minute: "0", hour: "3", day_of_week: "mon-fri"}` (3 AM on weekdays)

*   `interval: <seconds | "1h30m" | {hours: 1, minutes: 30, ...}>`:
    *   Defines a schedule that runs at fixed intervals.
    *   Can be an integer representing seconds.
    *   Can be a human-readable string like `"2h"`, `"30m"`, `"1h30m"`.
    *   Or an object with fields: `weeks`, `days`, `hours`, `minutes`, `seconds`.
    *   Example: `interval: {hours: 4, minutes: 30}` (every 4 hours and 30 minutes)

*   `date: <ISO_datetime_string>`:
    *   Schedules the pipeline to run once at a specific date and time.
    *   Uses ISO 8601 format (e.g., `"2024-07-01T10:00:00"`).

### `params:`
Defines pipeline-specific parameters that can be directly injected into your Hamilton functions. FlowerPower automatically makes these available to Hamilton (conceptually, it uses Hamilton's `source()` and `value()` constructs or direct parameter injection where appropriate).

*   These parameters are accessible by naming function arguments in your Python pipeline module identically to the keys in the `params` block.
*   Nested dictionaries and lists are also supported.

**Example:**
```yaml
params:
  data_path: "s3://my-production-bucket/latest_data.parquet"
  scale_factor: 1.75
  processing_options:
    filter_threshold: 0.95
    enable_feature_engineering: true
  model_config:
    type: "random_forest"
    estimators: 150
    max_depth: 10
```
In your Hamilton functions:
```python
import pandas as pd

# data_path and scale_factor are directly injected
def load_data(data_path: str) -> pd.DataFrame:
    return pd.read_parquet(data_path)

# processing_options will be injected as a dictionary
def process_data(raw_data: pd.DataFrame, processing_options: dict) -> pd.DataFrame:
    if processing_options.get("enable_feature_engineering", False):
        # ... apply feature engineering
        pass
    # ... use processing_options['filter_threshold']
    return raw_data # Placeholder

# model_config will be injected as a dictionary
def train_model(processed_data: pd.DataFrame, model_config: dict):
    print(f"Training model: {model_config['type']}")
    # ... use model_config['estimators'], model_config['max_depth']
    pass
```

### `adapter:`
Pipeline-specific adapter configurations. These settings will override or augment any configurations defined in the global `conf/project.yml` for the adapters used by this pipeline.

*   **`hamilton_tracker:`** (Overrides for Hamilton UI/Tracker)
    *   `project_id: <integer>`: The Hamilton project ID to associate this pipeline with.
    *   `dag_name: <string>`: A specific name for this DAG in the Hamilton UI. Defaults to pipeline name.
    *   `tags: {key1: value1, key2: value2}`: Tags to associate with the pipeline runs in Hamilton UI.
    *   `capture_data_statistics: <true | false>`: Enable/disable data statistics capture for this pipeline.
    *   `max_list_length_capture: <integer>`: Max length of lists to capture.
    *   `max_dict_length_capture: <integer>`: Max number of items in dictionaries to capture.

*   **`mlflow:`** (Overrides for MLflow Integration)
    *   `experiment_name: <string>`: MLflow experiment name for this pipeline.
    *   `run_name: <string>`: MLflow run name for this pipeline. Can include placeholders like `{pipeline_name}` or `{timestamp}`.
    *   Other MLflow-specific parameters (e.g., `autolog`, `tags`) as defined by FlowerPower's MLFlowConfig.

---

### Example `conf/pipelines/my_data_pipeline.yml`:

```yaml
# conf/pipelines/my_data_pipeline.yml

run:
  inputs:
    # No default inputs for this example, expecting them at runtime if needed
  final_vars:
    - "final_output"
    - "transformed_data" # We might want to inspect this intermediate step too
  config:
    data_processing_mode: "strict" # Example Hamilton @config.when key
  cache:
    recompute: ["raw_data"] # Always reload raw_data for this pipeline
  with_adapter:
    hamilton_tracker: true
    mlflow: true
    progressbar: true
    opentelemetry: false
  executor:
    type: local # Default to local execution for this specific pipeline
  log_level: INFO
  max_retries: 2
  retry_delay: 10.0 # seconds
  jitter_factor: 0.2
  retry_exceptions: ["requests.exceptions.ConnectionError", "TransientDatabaseError"]

schedule:
  cron: "0 5 * * *" # Run daily at 5 AM UTC

params:
  data_path: "/mnt/shared_drive/datasets/input_data.csv"
  scale_factor: 3.14
  model_config:
    type: "linear_regression"
    fit_intercept: true
  validation_split: 0.2

adapter:
  hamilton_tracker:
    project_id: 42
    dag_name: "MyDataPipelineDailyRun"
    tags:
      owner: "data_engineering_team"
      priority: "high"
    capture_data_statistics: true
  mlflow:
    experiment_name: "customer_churn_analysis"
    run_name: "daily_prediction_{timestamp:%Y%m%d_%H%M%S}"
    tags:
      version: "1.2.0"
```
This comprehensive configuration allows for precise control over each pipeline's behavior, making FlowerPower adaptable to a wide range of data processing scenarios.

# Running Pipelines

FlowerPower provides flexible ways to execute your data pipelines, either synchronously (directly in your terminal) or asynchronously (by submitting them to a job queue).

## Synchronous Execution (`flowerpower pipeline run`)

This command executes the specified pipeline immediately in the foreground. Your terminal will be occupied until the pipeline completes, and any output (like logs or print statements) will appear directly. This mode is useful for development, testing, or when you need immediate results.

**Syntax:**
```bash
flowerpower pipeline run <pipeline_name> [OPTIONS]
```

*   `<pipeline_name>`: The name of the pipeline to run (e.g., `my_data_pipeline`).

**Common Options:**

These options allow you to override settings defined in the pipeline's YAML configuration file (`conf/pipelines/<pipeline_name>.yml`) for this specific run.

*   `--inputs '{"key": "value", ...}'`:
    *   A JSON string representing a dictionary of input parameters for the Hamilton driver.
    *   Example: `--inputs '{"target_date": "2024-03-15", "user_id": 123}'`
*   `--final-vars '["var1", "var2"]'`:
    *   A JSON string representing a list of Hamilton function names whose outputs are desired as the final results.
    *   Example: `--final-vars '["final_model_output", "data_quality_report"]'`
*   `--config '{"hamilton_config_key": "value"}'`:
    *   A JSON string for Hamilton driver configurations, often used with `@config.when` to select specific function implementations.
    *   Example: `--config '{"data_source_type": "production"}'`
*   `--cache <true | false | json_string>`:
    *   Controls caching behavior.
    *   `true` or `false` to enable/disable caching for the run.
    *   A JSON string for fine-grained control, e.g., `--cache '{"recompute": ["raw_data_loader"]}'` to force recomputation of specific nodes.
*   `--executor <type_or_json_config>`:
    *   Specifies the execution environment.
    *   Can be a simple type like `local`, `threadpool`, `processpool`.
    *   Or a JSON string for more detailed configuration, e.g., `--executor '{"type": "threadpool", "max_workers": 4}'`.
*   `--with-adapter '{"tracker": true, "mlflow": false}'`:
    *   A JSON string to enable or disable specific adapters for this run, overriding `with_adapter` settings in the pipeline's YAML.
    *   Example: `--with-adapter '{"hamilton_tracker": true, "mlflow": false, "progressbar": true}'`
*   `--max-retries <integer>`:
    *   Overrides the maximum number of retries for this run.
*   `--retry-delay <float>`:
    *   Overrides the delay (in seconds) between retries for this run.
*   `--jitter-factor <float>`:
    *   Overrides the jitter factor for retry delays for this run.
*   `--log-level <DEBUG | INFO | WARNING | ERROR | CRITICAL>`:
    *   Sets the logging level for this specific run.

**Example:**
```bash
flowerpower pipeline run my_data_pipeline --inputs '{"date": "2023-01-15", "region": "emea"}' --final-vars '["processed_report"]' --log-level DEBUG
```
This command runs `my_data_pipeline` with specified inputs for `date` and `region`, requests only the `processed_report` output, and sets the log level to DEBUG for this execution.

## Asynchronous Execution via Job Queue

For longer-running pipelines or when you want to offload execution and free up your terminal, you can submit pipelines as jobs to a background job queue (like RQ or APScheduler, depending on your project setup).

### Adding/Submitting a Job (`flowerpower pipeline add_job`)

This command enqueues the pipeline to be executed by a worker process associated with your chosen job queue.

**Syntax:**
```bash
flowerpower pipeline add_job <pipeline_name> [OPTIONS]
```

*   `<pipeline_name>`: The name of the pipeline to add as a job.

**Common Options:**

Most options available for `flowerpower pipeline run` are also available for `add_job`, allowing you to customize the job's execution parameters:
*   `--inputs '{"key": "value", ...}'`
*   `--final-vars '["var1", "var2"]'`
*   `--config '{"hamilton_config_key": "value"}'`
*   `--cache <true | false | json_string>`
*   `--executor <type_or_json_config>` (Note: The executor choice might be constrained or influenced by the job queue worker's environment).
*   `--with-adapter '{"tracker": true, "mlflow": false}'`
*   `--max-retries <integer>`
*   `--retry-delay <float>`
*   `--jitter-factor <float>`
*   `--log-level <LEVEL>`

**Scheduling Options for `add_job`:**

These options determine when the job should be executed by the queue:

*   `--run-at <iso_datetime_string>`:
    *   Schedules the job to run at a specific future time.
    *   The datetime string should be in ISO 8601 format (e.g., "2024-07-15T14:30:00").
    *   Example: `--run-at "2024-12-25T08:00:00"`
*   `--run-in <duration_string>`:
    *   Schedules the job to run after a specified delay.
    *   The duration string can be like '5m' (5 minutes), '1h' (1 hour), '30s' (30 seconds), '1h30m'.
    *   Example: `--run-in 2h30m`

When you run `add_job`, FlowerPower will submit the job to the queue and typically return a **Job ID**. This ID can be used to monitor the job's status (details on job monitoring are in the "Job Queue Management" section).

**Example:**
```bash
flowerpower pipeline add_job my_nightly_processing --inputs '{"batch_size": 1000}' --run-in 15m --log-level INFO
```
This command submits the `my_nightly_processing` pipeline to the job queue. It will start 15 minutes after the command is run, with a `batch_size` of 1000, and will log at the INFO level.

*Note on `flowerpower pipeline run_job`*: There is also a command `flowerpower pipeline run_job <name_or_id>`. This command is generally used to run a pipeline *as a job* immediately via the queue, similar to `add_job` but without the `--run-at` or `--run-in` scheduling options. It's useful for triggering an asynchronous execution straight away.*

## General Notes on Execution

*   **Configuration Precedence**: Runtime options provided via the CLI (e.g., `--inputs`, `--config`) will override the corresponding settings defined in the pipeline's YAML configuration file (`conf/pipelines/<pipeline_name>.yml`).
*   **Hamilton Driver**: As detailed in the "Creating and Configuring Pipelines" section, the actual execution logic (constructing the DAG, calling functions, managing data flow) is handled by the Hamilton driver. The CLI commands are interfaces to configure and invoke this driver.
*   **Job Queue Workers**: For asynchronous execution (`add_job`), ensure that your job queue workers are running and configured correctly to pick up and process jobs from the queue. This is covered in "Job Queue Management".

This framework allows you to run pipelines in a way that best suits your workflow, from quick interactive tests to scheduled, production-scale asynchronous operations.

# Scheduling Pipelines

FlowerPower enables you to schedule your pipelines for automatic execution at predefined times or intervals. Scheduled jobs are managed by the configured job queue system (e.g., RQ with `rq-scheduler`, or APScheduler). This requires active workers to execute the jobs and, particularly for RQ, a dedicated scheduler process to enqueue jobs based on their schedules.

## Overview

*   **Triggers**: Pipelines can be scheduled using cron expressions (for complex, recurring schedules), fixed time intervals, or for a specific future date and time.
*   **Job Queue Integration**: The scheduling mechanism is tightly integrated with the job queue. When a schedule's trigger time is met, a job is added to the queue for an available worker to pick up.
*   **Prerequisites**:
    *   A configured job queue (see "Configuration" section).
    *   Running worker processes for the job queue.
    *   For RQ-based setups, an `rq-scheduler` instance must be running. APScheduler manages its own scheduling internally if configured as the job queue.

## Scheduling a Specific Pipeline (`flowerpower pipeline schedule`)

This command allows you to define and activate a new schedule for an individual pipeline. You can specify the trigger (cron, interval, or date) and override job execution parameters for that schedule.

**Syntax:**
```bash
flowerpower pipeline schedule <pipeline_name> [TRIGGER_OPTIONS] [JOB_OPTIONS]
```

*   `<pipeline_name>`: The name of the pipeline to schedule.

**Trigger Options (mutually exclusive):**

*   `--cron <cron_string_or_json>`:
    *   Schedules the pipeline based on a cron expression.
    *   Standard cron string: `"*/5 * * * *"` (every 5 minutes).
    *   JSON for more complex APScheduler fields: `'{"minute": "0", "hour": "*/3", "day_of_week": "mon-fri"}'` (every 3 hours on weekdays).
*   `--interval <duration_string_or_json>`:
    *   Schedules the pipeline to run at fixed intervals.
    *   Duration string: `'1h'`, `'30m'`, `'1d6h'`, `'1h30m10s'`.
    *   JSON for precise intervals: `'{"weeks": 1, "days": 2, "hours": 3, "minutes": 4, "seconds": 5}'`.
*   `--date <iso_datetime_string>`:
    *   Schedules the pipeline to run once at a specific date and time (ISO 8601 format).
    *   Example: `"2024-08-15T10:30:00"`

**Job Options:**

These options override the pipeline's default configurations for jobs originating from this schedule.

*   `--inputs '{"key": "value", ...}'`: JSON string for Hamilton driver inputs.
*   `--final-vars '["var1", "var2"]'`: JSON string for desired output variables.
*   `--config '{"hamilton_config_key": "value"}'`: JSON string for Hamilton driver configurations.
*   `--cache '{"recompute": ["node1"], "disable": false}'`: JSON string for cache settings.
*   `--executor <type_or_json_config>`: Executor type (e.g., `local`, `threadpool`) or JSON for detailed configuration.
*   `--with-adapter '{"tracker": true, "mlflow": true}'`: JSON string to enable/disable adapters.
*   `--max-retries <integer>`: Maximum number of retries for scheduled jobs.
*   `--retry-delay <float>`: Delay (seconds) between retries.
*   `--jitter-factor <float>`: Jitter factor for retry delays.
*   `--log-level <LEVEL>`: Logging level for scheduled jobs.
*   `--schedule-id <custom_id_for_schedule>`:
    *   Assigns a custom, unique ID to this schedule. Useful for later management (e.g., canceling or updating).
    *   If not provided, FlowerPower usually generates an ID based on the pipeline name and trigger.
*   `--overwrite`:
    *   If a schedule with the same `schedule-id` (or a default-generated ID that matches an existing one) already exists, this flag allows overwriting it. Otherwise, attempting to create a schedule with a conflicting ID will fail.

**Behavior:**

When you run this command, FlowerPower registers the schedule with the underlying job queue's scheduling system (e.g., `rq-scheduler` or APScheduler). The scheduler will then periodically check if the trigger condition is met.

**Examples:**

1.  Schedule `my_report_pipeline` to run every weekday at 5:00 AM with specific inputs:
    ```bash
    flowerpower pipeline schedule my_report_pipeline --cron "0 5 * * 1-5" --inputs '{"mode": "daily_summary"}' --schedule-id daily-report-pipeline
    ```

2.  Schedule `my_data_check` to run every 45 minutes with a custom schedule ID and overwrite if it exists:
    ```bash
    flowerpower pipeline schedule my_data_check --interval 45m --schedule-id data-check-prod --overwrite
    ```

3.  Schedule `my_maintenance_task` for a specific one-time execution using the `local` executor:
    ```bash
    flowerpower pipeline schedule my_maintenance_task --date "2025-01-01T03:00:00" --executor local --schedule-id new-year-maintenance
    ```

## Scheduling All Configured Pipelines (`flowerpower pipeline schedule_all`)

This command is a convenient way to activate all predefined schedules as defined in the `schedule:` section of your pipeline configuration files (`conf/pipelines/<pipeline_name>.yml`).

**Syntax:**
```bash
flowerpower pipeline schedule_all [OPTIONS]
```

**Behavior:**

*   The command iterates through all pipelines in your project.
*   For each pipeline, if a `schedule:` block is present and enabled in its YAML configuration, FlowerPower will attempt to create and activate that schedule with the job queue scheduler.
*   The parameters for the scheduled job (inputs, config, executor, etc.) will be taken from the `run:` and `params:` sections of the pipeline's YAML, unless overridden by options in the `schedule:` block itself.

**Common Options:**

*   `--executor <type_or_json_config>`:
    *   Globally overrides the executor configuration for all pipelines being scheduled by this command. This can be useful if you want all default-scheduled jobs to use a specific executor, regardless of their individual YAML settings.
*   `--overwrite`:
    *   If schedules previously created by `schedule_all` (or having IDs that would conflict with the default generated ones) exist, this flag allows them to be overwritten. This is useful for ensuring a clean state after deployments or configuration changes.

**Use Case:**

This command is particularly useful for initializing all your project's defined schedules in bulk, for example, after a new deployment, a system restart, or when setting up a new environment.

**Example:**
To activate all schedules defined in pipeline YAML files, overwriting any existing schedules that might conflict:
```bash
flowerpower pipeline schedule_all --overwrite
```

## Managing Schedules

Once pipelines are scheduled, their lifecycle (viewing, pausing, resuming, modifying, or canceling) is typically managed through the job queue's own mechanisms. FlowerPower provides CLI commands that interface with these mechanisms.

For detailed information on how to:
*   View active and scheduled jobs/schedules
*   Pause or resume schedules
*   Cancel or delete schedules
*   Inspect job statuses

Please refer to the **"Job Queue Management"** section of this documentation, which covers commands like `flowerpower job-queue show_schedules`, `flowerpower job-queue cancel_schedule`, and others.

# Job Queue Management

FlowerPower utilizes a job queue system for executing pipelines asynchronously and managing their scheduled runs. This system is configurable, typically using RQ (Redis Queue) with Redis as a message broker, or APScheduler which can use various backends. Asynchronous execution and scheduling rely on worker processes to pick up and run the actual pipeline jobs.

*   **Worker Processes**: You must have one or more worker processes running to execute jobs from the queue.
*   **Scheduler Process (for RQ)**: If you are using RQ as your job queue backend, a separate scheduler process (`flowerpower job-queue start-scheduler`) is essential. This process monitors defined schedules and enqueues jobs when their trigger conditions are met. APScheduler, on the other hand, manages its scheduling internally within its own process and doesn't typically require a separate scheduler command from FlowerPower.

## Starting Workers and Schedulers

### `flowerpower job-queue start-worker`

This command starts one or more worker processes that listen to the job queue and execute pipelines as jobs become available.

**Syntax:**
```bash
flowerpower job-queue start-worker [OPTIONS]
```

**Common Options:**

*   `--type rq`: Specifies the job queue type. If not provided, it defaults to the type configured in your `conf/project.yml`.
*   `--name <config_name>`: Refers to a specific named configuration block under `job_queue` in your `project.yml` (e.g., if you have multiple RQ setups for different queues).
*   `--num-workers <integer>`: (Primarily for RQ) The number of worker processes to start. For APScheduler, this might influence the size of an internal thread or process pool if it's configured to use one and this command supports it. Default is usually 1.
*   `--background`: Runs the worker(s) in the background, detaching from the terminal.
*   `--log-level <DEBUG | INFO | WARNING | ERROR | CRITICAL>`: Sets the logging level for the worker(s).
*   `--queue-names <"q1,q2">` (RQ specific): A comma-separated string of queue names the workers should listen to. Often, workers are configured to listen to specific queues at startup. This option provides an override.
*   `--job-executor <executor_config_json>` (APScheduler specific, potentially): If APScheduler workers can be configured with a specific Hamilton executor (e.g., local, threadpool) for the jobs they run, this option might take a JSON string defining that executor.

**Example:**
To start 4 RQ worker processes in the background, listening to the default queues, with INFO log level:
```bash
flowerpower job-queue start-worker --num-workers 4 --background --log-level INFO --type rq
```

### `flowerpower job-queue start-scheduler` (Primarily for RQ)

This command starts the RQ scheduler process. It is responsible for periodically checking all defined schedules and adding jobs to the appropriate queues when their time comes. This command is generally not needed if you are using APScheduler, as it handles its own scheduling loop.

**Syntax:**
```bash
flowerpower job-queue start-scheduler [OPTIONS]
```

**Common Options:**

*   `--type <rq>`: Specifies the job queue type. This command is most relevant for `rq`.
*   `--name <config_name>`: The name of the scheduler configuration from `project.yml` (if you have multiple named RQ scheduler setups).
*   `--background`: Runs the scheduler in the background.
*   `--interval <seconds>`: (RQ specific) How often, in seconds, the RQ scheduler checks for jobs to enqueue. Default: `60`.
*   `--log-level <DEBUG | INFO | WARNING | ERROR | CRITICAL>`: Sets the logging level for the scheduler process.

**Example:**
To start the RQ scheduler in the background, checking for jobs every 30 seconds:
```bash
flowerpower job-queue start-scheduler --interval 30 --background --type rq
```

## Managing Jobs

These commands help you inspect and manage individual jobs that are currently in the queue, running, or have finished.

*   **`flowerpower job-queue show-jobs`**:
    *   Lists jobs in the queue or in various states (e.g., queued, started, finished, failed).
    *   Options:
        *   `--format <table | json | yaml>`: Output format. Default: `table`.
        *   `--queue-name <queue_name>`: (RQ specific) Filter jobs by a specific queue (e.g., `default`, `high_priority`).
        *   `--state <queued|started|finished|failed|all>`: Filter jobs by their state.

*   **`flowerpower job-queue show-job-ids`**:
    *   Lists only the IDs of jobs, often useful for scripting.
    *   Options:
        *   `--queue-name <queue_name>`: (RQ specific) Filter by queue.
        *   `--state <queued|started|finished|failed|all>`: Filter by state.

*   **`flowerpower job-queue cancel-job <job_id>` or `flowerpower job-queue cancel-job --all`**:
    *   Cancels a specific job by its ID or all jobs.
    *   Options:
        *   `<job_id>`: The ID of the job to cancel.
        *   `--all`: Cancels all jobs (use with caution).
        *   `--queue-name <queue_name>`: (RQ specific) When used with `--all`, cancels all jobs in the specified queue.

*   **`flowerpower job-queue delete-job <job_id>` or `flowerpower job-queue delete-job --all`**:
    *   Deletes a job and its associated data (like results) from the queue system.
    *   Options:
        *   `<job_id>`: The ID of the job to delete.
        *   `--all`: Deletes all jobs (use with extreme caution).
        *   `--queue-name <queue_name>`: (RQ specific) When used with `--all`, deletes all jobs in the specified queue.

*   *(Result retrieval is typically part of `show-jobs` by inspecting job details, or by accessing storage where pipelines save their outputs. A dedicated `get-job-result` CLI command might not always be present, as results can be diverse and large.)*

## Managing Schedules

These commands are used to view, add, remove, or modify the definitions of recurring or future pipeline runs.

*   **`flowerpower job-queue show-schedules`**:
    *   Lists all defined schedules for pipeline execution.
    *   Options:
        *   `--format <table | json | yaml>`: Output format. Default: `table`.

*   **`flowerpower job-queue show-schedule-ids`**:
    *   Lists only the IDs of the defined schedules.

*   **`flowerpower job-queue cancel-schedule <schedule_id>` or `flowerpower job-queue cancel-schedule --all`**:
    *   Removes a schedule by its ID, preventing future job enqueues from this schedule.
    *   Options:
        *   `<schedule_id>`: The ID of the schedule to cancel. (You can set custom schedule IDs using `flowerpower pipeline schedule --schedule-id ...`).
        *   `--all`: Cancels all defined schedules.

*   **`flowerpower job-queue delete-schedule <schedule_id>` or `flowerpower job-queue delete-schedule --all`**:
    *   Deletes a schedule definition. For many backends, this is synonymous with `cancel-schedule`.
    *   Options:
        *   `<schedule_id>`: The ID of the schedule to delete.
        *   `--all`: Deletes all defined schedules.

*   **`flowerpower job-queue pause-schedule <schedule_id>` or `flowerpower job-queue pause-schedule --all`** (Primarily APScheduler):
    *   Temporarily pauses a schedule. The schedule definition remains but won't trigger new jobs until resumed.
    *   Options:
        *   `<schedule_id>`: The ID of the schedule to pause.
        *   `--all`: Pauses all schedules.

*   **`flowerpower job-queue resume-schedule <schedule_id>` or `flowerpower job-queue resume-schedule --all`** (Primarily APScheduler):
    *   Resumes a previously paused schedule.
    *   Options:
        *   `<schedule_id>`: The ID of the schedule to resume.
        *   `--all`: Resumes all paused schedules.

## Backend Specifics

*   The availability and behavior of certain commands (especially around schedule management like `pause-schedule` and `resume-schedule`) can depend on the capabilities of the chosen job queue backend (e.g., APScheduler offers richer direct schedule manipulation than RQ's default scheduler).
*   Always ensure your `conf/project.yml` is correctly configured for your chosen `job_queue` type (e.g., Redis connection details for RQ, database connection for APScheduler if using a persistent job store). Refer to the "Configuration" section for details on setting up these backends.

Effective job queue management is crucial for a robust automated pipeline system. These CLI commands provide the necessary tools to operate and monitor your FlowerPower jobs and schedules.

# Configuration

# Configuration

# Command-Line Interface (CLI) Reference

# Adapters and Hooks

# MQTT Integration

# Visualization

# Filesystem Configuration

# Programmatic Usage
