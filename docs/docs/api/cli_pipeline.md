# flowerpower pipeline Commands { #flowerpower-pipeline }

This section details the commands available under `flowerpower pipeline`.

## run { #flowerpower-run }

Run a pipeline immediately.

This command executes a pipeline with the specified configuration and inputs.
The pipeline will run synchronously, and the command will wait for completion.

### Usage

```bash
flowerpower pipeline run [options]
```

### Options

| Name | Type | Description | Default |
|---|---|---|---|
| name | str (arg) | Name of the pipeline to run. | — |
| --executor | str | Executor type (e.g., "local", "threadpool"). | None |
| --base-dir | str | Base directory for the pipeline/project. | None |
| --inputs | str | Inputs as JSON/dict string; parsed to dict. | None |
| --final-vars | str | Final variables as JSON/list string; parsed to list. | None |
| --config | str | Hamilton executor config as JSON/dict string. | None |
| --cache | str | Cache config as JSON/dict string. | None |
| --storage-options | str | Storage options as JSON/dict string; parsed to dict. | None |
| --log-level | str | Logging level: debug, info, warning, error, critical. | None |
| --with-adapter | str | Adapter config as JSON/dict string. | None |
| --max-retries | int | Max retry attempts on failure. | 0 |
| --retry-delay | float | Base delay between retries (seconds). | 1.0 |
| --jitter-factor | float | Random jitter factor [0-1]. | 0.1 |


### Examples

```bash
# Basic pipeline execution
$ flowerpower pipeline run my_pipeline

# Run with individual parameters (kwargs)
$ flowerpower pipeline run my_pipeline --inputs '{"data_path": "data/myfile.csv"}' --final-vars '["output_table", "summary_metrics"]'

# Run using a RunConfig from a YAML file
# Assuming you have a run_config.yaml like:
# inputs:
#   data_path: "data/myfile.csv"
# log_level: "INFO"
$ flowerpower pipeline run my_pipeline --run-config ./run_config.yaml

# Run using a RunConfig provided as a JSON string
$ flowerpower pipeline run my_pipeline --run-config '{"inputs": {"data_path": "data/myfile.csv"}, "log_level": "INFO"}'

# Mixing RunConfig with individual parameters (kwargs overrides RunConfig)
# This will run with log_level="DEBUG" and inputs={"data_path": "new_data.csv"}
$ flowerpower pipeline run my_pipeline --run-config '{"inputs": {"data_path": "original_data.csv"}, "log_level": "INFO"}' --inputs '{"data_path": "new_data.csv"}' --log-level DEBUG

# Configure automatic retries on failure using kwargs
$ flowerpower pipeline run my_pipeline --max-retries 3 --retry-delay 2.0 --jitter-factor 0.2

# Configure automatic retries on failure using RunConfig
# Assuming run_config_retries.yaml contains:
# retry_config:
#   max_retries: 3
#   retry_delay: 2.0
#   jitter_factor: 0.2
$ flowerpower pipeline run my_pipeline --run-config ./run_config_retries.yaml
```

---

## new { #flowerpower-new }

Create a new pipeline structure.

This command creates a new pipeline with the necessary directory structure,
configuration file, and skeleton module file. It prepares all the required
components for you to start implementing your pipeline logic.

### Usage

```bash
flowerpower pipeline new [options]
```

### Options

| Name | Type | Description | Default |
|---|---|---|---|
| name | str (arg) | Name for the new pipeline | — |
| --base-dir | str | Base directory to create the pipeline in | None |
| --storage-options | str | Options for storage backends (JSON/dict string) | None |
| --log-level | str | Logging level (debug, info, warning, error, critical) | None |
| --overwrite | bool | Overwrite existing pipeline if it exists | False |


### Examples

```bash
$ pipeline new my_new_pipeline

# Create a pipeline, overwriting if it exists
```

```bash
$ pipeline new my_new_pipeline --overwrite

# Create a pipeline in a specific directory
```

```bash
$ pipeline new my_new_pipeline --base-dir /path/to/project
```

---

## delete { #flowerpower-delete }

Delete a pipeline's configuration and/or module files.

This command removes a pipeline's configuration file and/or module file from the project.
If neither --cfg nor --module is specified, both will be deleted.

### Usage

```bash
flowerpower pipeline delete [options]
```

### Options

| Name | Type | Description | Default |
|---|---|---|---|
| name | str (arg) | Name of the pipeline to delete | — |
| --base-dir | str | Base directory containing the pipeline | None |
| --cfg | bool | Delete only the configuration file | False |
| --module | bool | Delete only the pipeline module | False |
| --storage-options | str | Options for storage backends (JSON/dict string) | None |
| --log-level | str | Logging level | None |

Behavior: If neither `--cfg` nor `--module` is specified, both config and module are deleted.


### Examples

```bash
$ pipeline delete my_pipeline

# Delete only the configuration file
```

```bash
$ pipeline delete my_pipeline --cfg

# Delete only the module file
```

```bash
$ pipeline delete my_pipeline --module
```

---

## show_dag { #flowerpower-show_dag }

Show the DAG (Directed Acyclic Graph) of a pipeline.

This command generates and displays a visual representation of the pipeline's
execution graph, showing how nodes are connected and dependencies between them.

### Usage

```bash
flowerpower pipeline show_dag [options]
```

### Options

| Name | Type | Description | Default |
|---|---|---|---|
| name | str (arg) | Name of the pipeline to visualize | — |
| --base-dir | str | Base directory containing the pipeline | None |
| --storage-options | str | Options for storage backends (JSON/dict string) | None |
| --log-level | str | Logging level | None |
| --format | str | Output format: png, svg, pdf; `raw` returns the graph object | "png" |


### Examples

```bash
$ pipeline show-dag my_pipeline

# Generate SVG format visualization
```

```bash
$ pipeline show-dag my_pipeline --format svg

# Get raw graphviz object
```

```bash
$ pipeline show-dag my_pipeline --format raw
```

---

## save_dag { #flowerpower-save_dag }

Save the DAG (Directed Acyclic Graph) of a pipeline to a file.

This command generates a visual representation of the pipeline's execution graph
and saves it to a file in the specified format.

### Usage

```bash
flowerpower pipeline save_dag [options]
```

### Options

| Name | Type | Description | Default |
|---|---|---|---|
| name | str (arg) | Name of the pipeline to visualize | — |
| --base-dir | str | Base directory containing the pipeline | None |
| --storage-options | str | Options for storage backends (JSON/dict string) | None |
| --log-level | str | Logging level | None |
| --format | str | Output format: png, svg, pdf | "png" |
| --output-path | str | Custom file path to save the output (default: <name>.<format>) | None |



### Examples

```bash
$ pipeline save-dag my_pipeline

# Save in SVG format
```

```bash
$ pipeline save-dag my_pipeline --format svg

# Save to a custom location
```

```bash
$ pipeline save-dag my_pipeline --output-path ./visualizations/my_graph.png
```

---

## show_pipelines { #flowerpower-show_pipelines }

List all available pipelines in the project.

This command displays a list of all pipelines defined in the project,
providing an overview of what pipelines are available to run.

### Usage

```bash
flowerpower pipeline show_pipelines [options]
```

### Options

| Name | Type | Description | Default |
|---|---|---|---|
| --base-dir | str | Base directory containing pipelines | None |
| --storage-options | str | Options for storage backends (JSON/dict string) | None |
| --log-level | str | Logging level | None |
| --format | str | Output format (table, json, yaml) | "table" |



### Examples

```bash
$ pipeline show-pipelines

# Output in JSON format
```

```bash
$ pipeline show-pipelines --format json

# List pipelines from a specific directory
```

```bash
$ pipeline show-pipelines --base-dir /path/to/project
```

---

## show_summary { #flowerpower-show_summary }

Show summary information for one or all pipelines.

This command displays detailed information about pipelines including their
configuration, code structure, and project context. You can view information
for a specific pipeline or get an overview of all pipelines.

### Usage

```bash
flowerpower pipeline show_summary [options]
```

### Options

| Name | Type | Description | Default |
|---|---|---|---|
| --name | str | Name of specific pipeline to summarize (all if not specified) | None |
| --cfg | bool | Include configuration details | True |
| --code | bool | Include code/module details | True |
| --project | bool | Include project context information | True |
| --base-dir | str | Base directory containing pipelines | None |
| --storage-options | str | Options for storage backends (JSON/dict string) | None |
| --log-level | str | Logging level | None |
| --to-html | bool | Generate HTML output instead of text | False |
| --to-svg | bool | Generate SVG output (where applicable) | False |
| --output-file | str | File path to save the output instead of printing to console | None |


### Examples

```bash
$ pipeline show-summary

# Show summary for a specific pipeline
```

```bash
$ pipeline show-summary --name my_pipeline

# Show only configuration information
```

```bash
$ pipeline show-summary --name my_pipeline --cfg --no-code --no-project

# Generate HTML report
```

```bash
$ pipeline show-summary --to-html --output-file pipeline_report.html
```

---

## add_hook { #flowerpower-add_hook }

Add a hook to a pipeline configuration.

This command adds a hook function to a pipeline's configuration. Hooks are functions
that are called at specific points during pipeline execution to perform additional
tasks like logging, monitoring, or data validation.

### Usage

```bash
flowerpower pipeline add_hook [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| name | str | Name of the pipeline to add the hook to | Required |
| function_name | str | Name of the hook function (must be defined in the pipeline module) | Required |
| type | str | Type of hook (determines when the hook is called during execution) | Required |
| to | str | Target node or tag (required for node-specific hooks) | Required |
| base_dir | str | Base directory containing the pipeline | Required |
| storage_options | str | Options for storage backends | Required |
| log_level | str | Set the logging level | Required |


### Examples

```bash
$ pipeline add-hook my_pipeline --function log_results

# Add a pre-run hook
```

```bash
$ pipeline add-hook my_pipeline --function validate_inputs --type PRE_RUN

# Add a node-specific hook (executed before a specific node runs)
```

```bash
$ pipeline add-hook my_pipeline --function validate_data --type NODE_PRE_EXECUTE --to data_processor

# Add a hook for all nodes with a specific tag
```

```bash
$ pipeline add-hook my_pipeline --function log_metrics --type NODE_POST_EXECUTE --to @metrics
```

---
