# CLI Reference

The FlowerPower CLI provides command-line tools for managing projects and pipelines. It is built with Typer and accessible via the `flowerpower` command.

## Usage

```bash
flowerpower [OPTIONS] COMMAND [ARGS]...
```

Run `flowerpower --help` for a full list of commands.

## Commands

### pipeline

Manage pipelines.

#### pipeline run

Run a pipeline.

**Usage:**
```bash
flowerpower pipeline run [OPTIONS] NAME
```

**Arguments:**
- `NAME`: Name of the pipeline to run [required]

**Options:**
- `--executor TEXT`: Executor to use for running the pipeline
- `--base-dir TEXT`: Base directory for the pipeline
- `--inputs TEXT`: Input parameters as JSON, dict string, or key=value pairs
- `--final-vars TEXT`: Final variables as JSON or list
- `--config TEXT`: Config for the hamilton pipeline executor
- `--cache TEXT`: Cache configuration as JSON or dict string
- `--storage-options TEXT`: Storage options as JSON, dict string, or key=value pairs
- `--log-level TEXT`: Logging level (debug, info, warning, error, critical)
- `--with-adapter TEXT`: Adapter configuration as JSON or dict string
- `--max-retries INTEGER`: Maximum number of retry attempts on failure [default: 0]
- `--retry-delay FLOAT`: Base delay between retries in seconds [default: 1.0]
- `--jitter-factor FLOAT`: Random factor applied to delay for jitter (0-1) [default: 0.1]

**Examples:**
```bash
# Basic run
flowerpower pipeline run my_pipeline

# With custom inputs
flowerpower pipeline run my_pipeline --inputs '{"data_date": "2025-04-28"}'

# Specify final variables
flowerpower pipeline run my_pipeline --final-vars '["result"]' --log-level DEBUG
```

#### pipeline new

Create a new pipeline.

**Usage:**
```bash
flowerpower pipeline new [OPTIONS] NAME
```

**Arguments:**
- `NAME`: Name of the pipeline to create [required]

**Options:**
- `--base-dir TEXT`: Base directory for the pipeline
- `--storage-options TEXT`: Storage options as JSON, dict string, or key=value pairs
- `--log-level TEXT`: Logging level (debug, info, warning, error, critical)
- `--overwrite`: Overwrite existing pipeline if it exists [default: no]

**Examples:**
```bash
# Create new pipeline
flowerpower pipeline new my_pipeline

# Overwrite if exists
flowerpower pipeline new my_pipeline --overwrite
```

#### pipeline delete

Delete a pipeline.

**Usage:**
```bash
flowerpower pipeline delete [OPTIONS] NAME
```

**Arguments:**
- `NAME`: Name of the pipeline to delete [required]

**Options:**
- `--base-dir TEXT`: Base directory for the pipeline
- `--storage-options TEXT`: Storage options as JSON, dict string, or key=value pairs
- `--log-level TEXT`: Logging level (debug, info, warning, error, critical)
- `--cfg`: Delete only the configuration file [default: no]
- `--module`: Delete only the pipeline module [default: no]

**Examples:**
```bash
# Delete pipeline (config and module)
flowerpower pipeline delete my_pipeline

# Delete only config
flowerpower pipeline delete my_pipeline --cfg
```

#### pipeline show-dag

Show the DAG of a pipeline.

**Usage:**
```bash
flowerpower pipeline show-dag [OPTIONS] NAME
```

**Arguments:**
- `NAME`: Name of the pipeline to visualize [required]

**Options:**
- `--base-dir TEXT`: Base directory for the pipeline
- `--storage-options TEXT`: Storage options as JSON, dict string, or key=value pairs
- `--log-level TEXT`: Logging level (debug, info, warning, error, critical)
- `--format TEXT`: Output format (e.g., png, svg, pdf). If 'raw', returns object. [default: png]

**Examples:**
```bash
# Show DAG
flowerpower pipeline show-dag my_pipeline

# SVG format
flowerpower pipeline show-dag my_pipeline --format svg
```

#### pipeline save-dag

Save the DAG of a pipeline to a file.

**Usage:**
```bash
flowerpower pipeline save-dag [OPTIONS] NAME
```

**Arguments:**
- `NAME`: Name of the pipeline to visualize [required]

**Options:**
- `--base-dir TEXT`: Base directory for the pipeline
- `--storage-options TEXT`: Storage options as JSON, dict string, or key=value pairs
- `--log-level TEXT`: Logging level (debug, info, warning, error, critical)
- `--format TEXT`: Output format (e.g., png, svg, pdf) [default: png]
- `--output-path TEXT`: Custom path to save the file (default: <name>.<format>)

**Examples:**
```bash
# Save DAG
flowerpower pipeline save-dag my_pipeline

# Custom path
flowerpower pipeline save-dag my_pipeline --output-path ./vis/my_graph.png --format svg
```

#### pipeline show-pipelines

List all pipelines.

**Usage:**
```bash
flowerpower pipeline show-pipelines [OPTIONS]
```

**Options:**
- `--base-dir TEXT`: Base directory for the pipeline
- `--storage-options TEXT`: Storage options as JSON, dict string, or key=value pairs
- `--log-level TEXT`: Logging level (debug, info, warning, error, critical)
- `--format TEXT`: Output format (table, json, yaml) [default: table]

**Examples:**
```bash
# List pipelines
flowerpower pipeline show-pipelines

# JSON format
flowerpower pipeline show-pipelines --format json
```

#### pipeline show-summary

Show summary of pipelines.

**Usage:**
```bash
flowerpower pipeline show-summary [OPTIONS]
```

**Options:**
- `--name TEXT`: Name of specific pipeline (all if not specified)
- `--cfg`: Include configuration details [default: True]
- `--code`: Include code/module details [default: True]
- `--project`: Include project context [default: True]
- `--base-dir TEXT`: Base directory for the pipeline
- `--storage-options TEXT`: Storage options as JSON, dict string, or key=value pairs
- `--log-level TEXT`: Logging level (debug, info, warning, error, critical)
- `--to-html`: Output summary as HTML [default: no]
- `--to-svg`: Output summary as SVG (if applicable) [default: no]
- `--output-file TEXT`: Save output to file instead of printing

**Examples:**
```bash
# Summary for all pipelines
flowerpower pipeline show-summary

# Summary for specific pipeline
flowerpower pipeline show-summary --name my_pipeline --cfg --code --no-project
```

#### pipeline add-hook

Add a hook to a pipeline.

**Usage:**
```bash
flowerpower pipeline add-hook [OPTIONS] NAME
```

**Arguments:**
- `NAME`: Name of the pipeline to add the hook to [required]

**Options:**
- `--function TEXT`: Name of the hook function [required]
- `--type [MQTT_BUILD_CONFIG]`: Type of hook to add [default: MQTT_BUILD_CONFIG]
- `--to TEXT`: Target node name or tag (required for node hooks)
- `--base-dir TEXT`: Base directory for the pipeline
- `--storage-options TEXT`: Storage options as JSON, dict string, or key=value pairs
- `--log-level TEXT`: Logging level (debug, info, warning, error, critical)

**Examples:**
```bash
# Add hook
flowerpower pipeline add-hook my_pipeline --function log_results --type MQTT_BUILD_CONFIG
```

### init

Initialize a new FlowerPower project.

**Usage:**
```bash
flowerpower init [OPTIONS] [NAME]
```

**Options:**
- `--name TEXT`: The name of the project
- `--base-dir TEXT`: Base directory where the project will be created
- `--storage-options TEXT`: Storage options as JSON, dict string, or key=value pairs
- `--log-level TEXT`: Logging level (debug, info, warning, error, critical)

**Examples:**
```bash
# Initialize project
flowerpower init --name my_project