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

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| name | str | Name of the pipeline to run. | Required |
| --run-config | str | Path to a YAML file containing `RunConfig` parameters, or a JSON string. | None |
| --inputs | str | JSON string of input parameters for the pipeline. | None |
| --final-vars | str | JSON string of final variables to request from the pipeline. | None |
| --config | str | JSON string of configuration for the Hamilton executor. | None |
| --cache | str | JSON string of cache configuration for improved performance. | None |
| --executor-cfg | str | JSON string or name of executor to use (e.g., "threadpool", "local"). | None |
| --with-adapter-cfg | str | JSON string of configuration for adapters like trackers or monitors. | None |
| --pipeline-adapter-cfg | str | JSON string of pipeline-specific adapter settings. | None |
| --project-adapter-cfg | str | JSON string of project-level adapter settings. | None |
| --adapter | str | JSON string of custom adapter instance for pipeline. | None |
| --reload | bool | Force reload of pipeline configuration. | False |
| --log-level | str | Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). | None |
| --max-retries | int | Maximum number of retry attempts on failure. | None |
| --retry-delay | float | Base delay between retries in seconds. | None |
| --jitter-factor | float | Random factor applied to delay for jitter (0-1). | None |
| --retry-exceptions | str | Comma-separated list of exception types that trigger a retry. | None |
| --on-success | str | Path to a Python function or module:function for success callback. | None |
| --on-failure | str | Path to a Python function or module:function for failure callback. | None |


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

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| name | str | Name for the new pipeline | Required |
| base_dir | str | Base directory to create the pipeline in | Required |
| storage_options | str | Options for storage backends | Required |
| log_level | str | Set the logging level | Required |
| overwrite | str | Whether to overwrite existing pipeline with the same name | Required |


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

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| name | str | Name of the pipeline to delete | Required |
| base_dir | str | Base directory containing the pipeline | Required |
| cfg | str | Delete only the configuration file | Required |
| module | str | Delete only the pipeline module | Required |
| storage_options | str | Options for storage backends | Required |
| log_level | str | Set the logging level | Required |


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

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| name | str | Name of the pipeline to visualize | Required |
| base_dir | str | Base directory containing the pipeline | Required |
| storage_options | str | Options for storage backends | Required |
| log_level | str | Set the logging level | Required |
| format | str | Output format for the visualization | Required |


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

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| name | str | Name of the pipeline to visualize | Required |
| base_dir | str | Base directory containing the pipeline | Required |
| storage_options | str | Options for storage backends | Required |
| log_level | str | Set the logging level | Required |
| format | str | Output format for the visualization | Required |
| output_path | str | Custom file path to save the output (defaults to pipeline name) | Required |


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

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| base_dir | str | Base directory containing pipelines | Required |
| storage_options | str | Options for storage backends | Required |
| log_level | str | Set the logging level | Required |
| format | str | Output format for the list (table, json, yaml) | Required |


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

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| name | str | Name of specific pipeline to summarize (all if not specified) | Required |
| cfg | str | Include configuration details | Required |
| code | str | Include code/module details | Required |
| project | str | Include project context information | Required |
| base_dir | str | Base directory containing pipelines | Required |
| storage_options | str | Options for storage backends | Required |
| log_level | str | Set the logging level | Required |
| to_html | str | Generate HTML output instead of text | Required |
| to_svg | str | Generate SVG output (where applicable) | Required |
| output_file | str | File path to save the output instead of printing to console | Required |


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

