# CLI Pipeline Commands

These commands are available under `flowerpower pipeline`.

```bash
flowerpower pipeline [OPTIONS] COMMAND [ARGS]...
```

| Command | Description |
|:--------|:------------|
| `run` | Run a pipeline immediately. |
| `new` | Create a new pipeline structure. |
| `delete` | Delete a pipeline's configuration and/or module. |
| `show-dag` | Show a pipeline DAG. |
| `save-dag` | Save a pipeline DAG to a file. |
| `show-pipelines` | List all pipelines. |
| `show-summary` | Show a pipeline summary. |
| `add-hook` | Add a hook to a pipeline. |

## run

```bash
flowerpower pipeline run [OPTIONS] NAME
```

| Option | Type | Description | Default |
|:-------|:-----|:------------|:--------|
| `NAME` | `str` | Pipeline name (required). | — |
| `--executor` | `str` | Executor type. | `None` |
| `--executor-cfg` | `str` | Executor config as JSON/dict string. | `None` |
| `--executor-max-workers` | `int` | Set `executor.max_workers`. | `None` |
| `--executor-num-cpus` | `int` | Set `executor.num_cpus`. | `None` |
| `--base-dir`, `-d` | `str` | Base directory. | `None` |
| `--inputs` | `str` | Inputs as JSON/dict or key=value pairs. | `None` |
| `--final-vars`, `--outputs`, `-o` | `str` | Final variables as JSON or list. | `None` |
| `--config` | `str` | Hamilton runtime config as JSON/dict. | `None` |
| `--cache` | `str` | Cache config as JSON/dict. | `None` |
| `--storage-options`, `-s` | `str` | Storage options as JSON/dict. | `None` |
| `--log-level` | `str` | Logging level. | `None` |
| `--with-adapter` | `str` | Adapter config as JSON/dict. | `None` |
| `--max-retries` | `int` | Deprecated retry setting. | `0` |
| `--retry-delay` | `float` | Deprecated retry setting. | `1.0` |
| `--jitter-factor` | `float` | Deprecated retry setting. | `0.1` |

!!! warning "Deprecated retry flags"
    `--max-retries`, `--retry-delay`, and `--jitter-factor` are deprecated. Use `retry` configuration in the YAML config or `RunConfigBuilder` in Python instead.

```bash
flowerpower pipeline run my_pipeline
flowerpower pipeline run my_pipeline --inputs '{"data_path": "data/myfile.csv"}'
flowerpower pipeline run my_pipeline --final-vars '["output_table"]'
flowerpower pipeline run my_pipeline --executor threadpool --executor-max-workers 4
flowerpower pipeline run my_pipeline --with-adapter '{"hamilton_tracker": true}'
```

## new

```bash
flowerpower pipeline new [OPTIONS] NAME
```

| Option | Type | Description | Default |
|:-------|:-----|:------------|:--------|
| `NAME` | `str` | Pipeline name (required). | — |
| `--base-dir`, `-d` | `str` | Base directory. | `None` |
| `--storage-options`, `-s` | `str` | Storage options. | `None` |
| `--log-level` | `str` | Logging level. | `None` |
| `--overwrite` | `bool` | Overwrite existing pipeline. | `False` |

```bash
flowerpower pipeline new my_pipeline
flowerpower pipeline new my_pipeline --overwrite
```

## delete

```bash
flowerpower pipeline delete [OPTIONS] NAME
```

| Option | Type | Description | Default |
|:-------|:-----|:------------|:--------|
| `NAME` | `str` | Pipeline name (required). | — |
| `--base-dir`, `-d` | `str` | Base directory. | `None` |
| `--storage-options`, `-s` | `str` | Storage options. | `None` |
| `--log-level` | `str` | Logging level. | `None` |
| `--cfg`, `-c` | `bool` | Delete only the config file. | `False` |
| `--module`, `-m` | `bool` | Delete only the module file. | `False` |

If neither `--cfg` nor `--module` is set, both files are deleted.

```bash
flowerpower pipeline delete my_pipeline
flowerpower pipeline delete my_pipeline --cfg
flowerpower pipeline delete my_pipeline --module
```

## show-dag

```bash
flowerpower pipeline show-dag [OPTIONS] NAME
```

| Option | Type | Description | Default |
|:-------|:-----|:------------|:--------|
| `NAME` | `str` | Pipeline name (required). | — |
| `--base-dir`, `-d` | `str` | Base directory. | `None` |
| `--storage-options`, `-s` | `str` | Storage options. | `None` |
| `--log-level` | `str` | Logging level. | `None` |
| `--format` | `str` | Output format: `png`, `svg`, `pdf`, or `raw`. | `png` |

```bash
flowerpower pipeline show-dag my_pipeline
flowerpower pipeline show-dag my_pipeline --format svg
flowerpower pipeline show-dag my_pipeline --format raw
```

## save-dag

```bash
flowerpower pipeline save-dag [OPTIONS] NAME
```

| Option | Type | Description | Default |
|:-------|:-----|:------------|:--------|
| `NAME` | `str` | Pipeline name (required). | — |
| `--base-dir`, `-d` | `str` | Base directory. | `None` |
| `--storage-options`, `-s` | `str` | Storage options. | `None` |
| `--log-level` | `str` | Logging level. | `None` |
| `--format` | `str` | Output format: `png`, `svg`, or `pdf`. | `png` |
| `--output-path` | `str` | Custom output path. | `<name>.<format>` |

```bash
flowerpower pipeline save-dag my_pipeline
flowerpower pipeline save-dag my_pipeline --format svg
flowerpower pipeline save-dag my_pipeline --output-path ./visuals/my_pipeline.svg
```

## show-pipelines

```bash
flowerpower pipeline show-pipelines [OPTIONS]
```

| Option | Type | Description | Default |
|:-------|:-----|:------------|:--------|
| `--base-dir`, `-d` | `str` | Base directory. | `None` |
| `--storage-options`, `-s` | `str` | Storage options. | `None` |
| `--log-level` | `str` | Logging level. | `None` |
| `--format` | `str` | Output format: `table`, `json`, or `yaml`. | `table` |

```bash
flowerpower pipeline show-pipelines
flowerpower pipeline show-pipelines --format json
```

## show-summary

```bash
flowerpower pipeline show-summary [OPTIONS]
```

| Option | Type | Description | Default |
|:-------|:-----|:------------|:--------|
| `--name` | `str` | Specific pipeline name. | `None` |
| `--cfg` | `bool` | Include configuration details. | `True` |
| `--code` | `bool` | Include code details. | `True` |
| `--project` | `bool` | Include project details. | `True` |
| `--base-dir`, `-d` | `str` | Base directory. | `None` |
| `--storage-options`, `-s` | `str` | Storage options. | `None` |
| `--log-level` | `str` | Logging level. | `None` |
| `--to-html` | `bool` | Output as HTML. | `False` |
| `--to-svg` | `bool` | Output as SVG. | `False` |
| `--output-file` | `str` | Save to a file instead of printing. | `None` |

```bash
flowerpower pipeline show-summary
flowerpower pipeline show-summary --name my_pipeline
flowerpower pipeline show-summary --name my_pipeline --cfg --no-code --no-project
flowerpower pipeline show-summary --to-html --output-file report.html
```

## add-hook

```bash
flowerpower pipeline add-hook [OPTIONS] NAME
```

| Option | Type | Description | Default |
|:-------|:-----|:------------|:--------|
| `NAME` | `str` | Pipeline name (required). | — |
| `--function`, `-f` | `str` | Hook function name (required). | — |
| `--type` | `str` | Hook type. Only `MQTT_BUILD_CONFIG` is supported. | `MQTT_BUILD_CONFIG` |
| `--to` | `str` | Target node or tag. | `None` |
| `--base-dir`, `-d` | `str` | Base directory. | `None` |
| `--storage-options`, `-s` | `str` | Storage options. | `None` |
| `--log-level` | `str` | Logging level. | `None` |

!!! note
    Only `MQTT_BUILD_CONFIG` hooks are supported. There are no additional MQTT CLI commands beyond `add-hook`.

```bash
flowerpower pipeline add-hook my_pipeline --function build_mqtt_config
flowerpower pipeline add-hook my_pipeline --function build_mqtt_config --type MQTT_BUILD_CONFIG
```
