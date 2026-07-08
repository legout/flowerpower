# CLI Reference

FlowerPower provides a **Typer**-based command-line interface accessible as `flowerpower`. It is the fastest way to initialize projects, manage pipelines, and start the Hamilton UI.

```bash
flowerpower [OPTIONS] COMMAND [ARGS]...
```

Use `flowerpower --help` or `flowerpower <COMMAND> --help` to see the live options for your installed version.

## Global options

| Option | Description |
|--------|-------------|
| `--install-completion` | Install shell completion for the current shell. |
| `--show-completion` | Print the shell completion script for copying or customizing. |
| `--help` | Show the help message and exit. |

## `flowerpower init`

Create a new FlowerPower project. This calls `FlowerPowerProject.new(...)` under the hood.

```bash
flowerpower init [OPTIONS]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--name TEXT` | `-n` | Project name. If omitted, the current directory name is used. |
| `--base-dir TEXT` | `-d` | Directory where the project is created. If omitted, the parent of the current directory is used. |
| `--storage-options TEXT` | `-s` | Storage options as a JSON/dict string. |
| `--help` | | Show help. |

```bash
flowerpower init --name my_project
flowerpower init --name my_project --base-dir ./projects
```

!!! note
    The old `FlowerPowerProject.init(...)` method has been removed. Use `.new(...)` or the `flowerpower init` command instead.

## `flowerpower ui`

Start the Hamilton UI web application.

```bash
flowerpower ui [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--port INTEGER` | `-p` | `8241` | Port for the UI server. |
| `--base-dir TEXT` | `-d` | `~/.hamilton/db` | Directory where the UI stores its data. |
| `--no-migration` | | | Skip database migrations on startup. |
| `--no-open` | | | Do not open the UI automatically in a browser. |
| `--settings TEXT` | `-s` | `mini` | UI settings profile (`mini`, `dev`, `prod`). |
| `--config TEXT` | `-c` | | Custom UI configuration file. |
| `--help` | | | Show help. |

```bash
flowerpower ui
flowerpower ui --port 9000 --no-open
```

!!! tip
    Requires the `ui` extra. Install it with `pip install "flowerpower[ui]"` or `uv pip install 'flowerpower[io,ray,ui]'`.

## `flowerpower pipeline`

Manage and execute pipelines.

```bash
flowerpower pipeline [OPTIONS] COMMAND [ARGS]...
```

### `flowerpower pipeline run`

Run a pipeline synchronously. The command builds a `RunConfig` internally from the supplied flags and waits for the pipeline to finish.

```bash
flowerpower pipeline run [OPTIONS] NAME
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--executor TEXT` | | | Executor type (e.g. `threadpool`, `local`). |
| `--executor-cfg TEXT` | | | Executor configuration as a JSON/dict string. |
| `--executor-max-workers INTEGER` | | | Convenience flag: set `max_workers`. |
| `--executor-num-cpus INTEGER` | | | Convenience flag: set `num_cpus`. |
| `--base-dir TEXT` | `-d` | | Base directory containing the project. |
| `--inputs TEXT` | | | Input parameters as JSON, dict string, or `key=value` pairs. |
| `--final-vars TEXT`, `--outputs TEXT`, `-o` | | | Final variables to compute, as JSON or a list. |
| `--config TEXT` | | | Hamilton executor configuration as JSON/dict string. |
| `--cache TEXT` | | | Cache configuration as JSON/dict string. |
| `--storage-options TEXT` | `-s` | | Storage options as JSON, dict string, or `key=value` pairs. |
| `--log-level TEXT` | | | Logging level (`debug`, `info`, `warning`, `error`, `critical`). |
| `--with-adapter TEXT` | | | Adapter configuration as JSON/dict string. |
| `--max-retries INTEGER` | | `0` | Deprecated. Use the nested `retry` config via Python when possible. |
| `--retry-delay FLOAT` | | `1.0` | Deprecated. Use the nested `retry` config via Python when possible. |
| `--jitter-factor FLOAT` | | `0.1` | Deprecated. Use the nested `retry` config via Python when possible. |
| `--help` | | | Show help. |

```bash
flowerpower pipeline run hello
flowerpower pipeline run hello --inputs '{"message": "Hi"}'
flowerpower pipeline run hello --final-vars '["full_greeting"]' --log-level debug
flowerpower pipeline run hello --executor threadpool --executor-max-workers 4
flowerpower pipeline run hello --with-adapter '{"hamilton_tracker": true}'
```

!!! warning
    `--max-retries`, `--retry-delay`, and `--jitter-factor` are deprecated and emit a `DeprecationWarning`. For production retry logic, build a `RunConfig` in Python and use the nested `retry` block (see the API reference).

!!! tip
    The adapter key is `hamilton_tracker`, not `tracker`. The `opentelemetry` adapter has been removed.

### `flowerpower pipeline new`

Create a new pipeline scaffold: a configuration file under `conf/pipelines/` and a module file under `pipelines/`.

```bash
flowerpower pipeline new [OPTIONS] NAME
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--base-dir TEXT` | `-d` | | Base directory for the project. |
| `--storage-options TEXT` | `-s` | | Storage options as JSON/dict string or `key=value` pairs. |
| `--log-level TEXT` | | | Logging level. |
| `--overwrite` / `--no-overwrite` | | `no-overwrite` | Overwrite an existing pipeline with the same name. |
| `--help` | | | Show help. |

```bash
flowerpower pipeline new hello
flowerpower pipeline new hello --overwrite
```

### `flowerpower pipeline delete`

Delete a pipeline's configuration file and/or module file. If neither `--cfg` nor `--module` is passed, both are removed.

```bash
flowerpower pipeline delete [OPTIONS] NAME
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--base-dir TEXT` | `-d` | | Base directory for the project. |
| `--storage-options TEXT` | `-s` | | Storage options. |
| `--log-level TEXT` | | | Logging level. |
| `--cfg` | `-c` | | Delete only the configuration file. |
| `--module` | `-m` | | Delete only the pipeline module. |
| `--help` | | | Show help. |

```bash
flowerpower pipeline delete hello
flowerpower pipeline delete hello --cfg
flowerpower pipeline delete hello --module
```

### `flowerpower pipeline show-dag`

Display the execution graph of a pipeline.

```bash
flowerpower pipeline show-dag [OPTIONS] NAME
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--base-dir TEXT` | `-d` | | Base directory for the project. |
| `--storage-options TEXT` | `-s` | | Storage options. |
| `--log-level TEXT` | | | Logging level. |
| `--format TEXT` | | `png` | Output format: `png`, `svg`, `pdf`, or `raw` (returns the graph object). |
| `--help` | | | Show help. |

```bash
flowerpower pipeline show-dag hello
flowerpower pipeline show-dag hello --format svg
```

### `flowerpower pipeline save-dag`

Save a pipeline DAG to a file.

```bash
flowerpower pipeline save-dag [OPTIONS] NAME
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--base-dir TEXT` | `-d` | | Base directory for the project. |
| `--storage-options TEXT` | `-s` | | Storage options. |
| `--log-level TEXT` | | | Logging level. |
| `--format TEXT` | | `png` | Output format: `png`, `svg`, or `pdf`. |
| `--output-path TEXT` | | `<name>.<format>` | Custom path for the saved file. |
| `--help` | | | Show help. |

```bash
flowerpower pipeline save-dag hello
flowerpower pipeline save-dag hello --format svg --output-path ./vis/hello.svg
```

### `flowerpower pipeline show-pipelines`

List all available pipelines in the project.

```bash
flowerpower pipeline show-pipelines [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--base-dir TEXT` | `-d` | | Base directory for the project. |
| `--storage-options TEXT` | `-s` | | Storage options. |
| `--log-level TEXT` | | | Logging level. |
| `--format TEXT` | | `table` | Output format: `table`, `json`, or `yaml`. |
| `--help` | | | Show help. |

```bash
flowerpower pipeline show-pipelines
flowerpower pipeline show-pipelines --format json
```

### `flowerpower pipeline show-summary`

Show summary information for one or all pipelines, optionally including configuration, code, and project context.

```bash
flowerpower pipeline show-summary [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--name TEXT` | | | Specific pipeline name. All pipelines are summarized if omitted. |
| `--cfg` / `--no-cfg` | | `cfg` | Include configuration details. |
| `--code` / `--no-code` | | `code` | Include code/module details. |
| `--project` / `--no-project` | | `project` | Include project context. |
| `--base-dir TEXT` | `-d` | | Base directory for the project. |
| `--storage-options TEXT` | `-s` | | Storage options. |
| `--log-level TEXT` | | | Logging level. |
| `--to-html` / `--no-to-html` | | `no-to-html` | Output as HTML. |
| `--to-svg` / `--no-to-svg` | | `no-to-svg` | Output as SVG. |
| `--output-file TEXT` | | | Save the output to a file instead of printing. |
| `--help` | | | Show help. |

```bash
flowerpower pipeline show-summary
flowerpower pipeline show-summary --name hello --cfg --code --no-project
flowerpower pipeline show-summary --to-html --output-file report.html
```

### `flowerpower pipeline add-hook`

Add a hook to a pipeline configuration.

```bash
flowerpower pipeline add-hook [OPTIONS] NAME
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--function TEXT` | `-f` | (required) | Name of the hook function. |
| `--type [mqtt-build-config]` | | `mqtt-build-config` | Hook type. |
| `--to TEXT` | | | Target node name or tag (required for node-specific hooks). |
| `--base-dir TEXT` | `-d` | | Base directory for the project. |
| `--storage-options TEXT` | `-s` | | Storage options. |
| `--log-level TEXT` | | | Logging level. |
| `--help` | | | Show help. |

```bash
flowerpower pipeline add-hook hello --function log_results --type MQTT_BUILD_CONFIG
```

!!! note
    Only `MQTT_BUILD_CONFIG` (`mqtt-build-config`) is currently supported as a hook type.
