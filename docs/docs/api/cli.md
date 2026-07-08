# CLI Reference

The `flowerpower` command-line interface is built on [Typer](https://typer.tiangolo.com/). It provides project initialization, pipeline management, and the Hamilton UI.

```bash
flowerpower [OPTIONS] COMMAND [ARGS]...
```

## Top-level commands

| Command | Description |
|:--------|:------------|
| `init` | Initialize a new FlowerPower project. |
| `ui` | Start the Hamilton UI web application. |
| `pipeline` | Manage and execute pipelines. |

## Global options

| Option | Description |
|:-------|:------------|
| `--install-completion` | Install shell completion for the current shell. |
| `--show-completion` | Print shell completion for the current shell. |
| `--help` | Show help and exit. |

## flowerpower init

Initialize a new FlowerPower project.

```bash
flowerpower init [OPTIONS]
```

| Option | Type | Description | Default |
|:-------|:-----|:------------|:--------|
| `--name`, `-n` | `str` | Project name. | Current directory name |
| `--base-dir`, `-d` | `str` | Base directory for the project. | Current directory |
| `--storage-options`, `-s` | `str` | Storage options as JSON or dict string. | `None` |

```bash
flowerpower init
flowerpower init --name my-project
flowerpower init --name my-project --base-dir /path/to/projects
```

## flowerpower ui

Start the Hamilton UI.

!!! note
    Requires the `[ui]` extra: `pip install "sf-hamilton[ui]"` or `uv pip install 'flowerpower[ui]'`.

```bash
flowerpower ui [OPTIONS]
```

| Option | Type | Description | Default |
|:-------|:-----|:------------|:--------|
| `--port`, `-p` | `int` | Port to run the UI on. | `8241` |
| `--base-dir`, `-d` | `str` | Directory for Hamilton UI data. | `~/.hamilton/db` |
| `--no-migration` | `bool` | Skip database migrations. | `False` |
| `--no-open` | `bool` | Do not open the browser automatically. | `False` |
| `--settings`, `-s` | `str` | Settings profile (`mini`, `dev`, `prod`). | `mini` |
| `--config`, `-c` | `str` | Custom configuration file path. | `None` |

```bash
flowerpower ui
flowerpower ui --port 9000
flowerpower ui --no-open
flowerpower ui --settings prod
```

## flowerpower pipeline

See [CLI Pipeline Commands](./cli_pipeline.md) for the full reference.

```bash
flowerpower pipeline [COMMAND] [OPTIONS]
```

| Command | Description |
|:--------|:------------|
| `run` | Run a pipeline immediately. |
| `new` | Create a new pipeline. |
| `delete` | Delete a pipeline. |
| `show-dag` | Show a pipeline DAG. |
| `save-dag` | Save a pipeline DAG to a file. |
| `show-pipelines` | List all pipelines. |
| `show-summary` | Show pipeline summary. |
| `add-hook` | Add a hook to a pipeline. |
