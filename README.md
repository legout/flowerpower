<div align="center">
  <h1>FlowerPower 🌸 — Build & Orchestrate Data Pipelines</h1>
  <h3>A simple, configuration-driven workflow framework built on Hamilton</h3>
  <img src="./image.png" alt="FlowerPower Logo" width="400" height="300">
</div>

[![PyPI version](https://img.shields.io/pypi/v/flowerpower.svg?style=flat-square)](https://pypi.org/project/flowerpower/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/legout/flowerpower/blob/main/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/legout/flowerpower)
[![Documentation Status](https://readthedocs.org/projects/flowerpower/badge/?version=latest)](https://legout.github.io/flowerpower/)

**FlowerPower** is a Python framework for building, configuring, and running data
processing pipelines. You write your logic as plain Python functions using
[Hamilton](https://github.com/apache/hamilton); FlowerPower takes care of the
project structure, layered configuration, execution, the CLI, a web UI, and
pluggable I/O.

> **Hamilton = the DAG, FlowerPower = everything around it.** You describe nodes
> as functions; FlowerPower wires up config, runs, retries, visualization, and
> orchestration.

## ✨ Features

- **Modular pipelines** — Define transforms as Python functions; Hamilton assembles
  them into a directed acyclic graph (DAG) from their signatures.
- **Configuration-driven** — Separate logic from settings with layered YAML, env
  overlays (`FP_PIPELINE__*`), `${VAR}` interpolation, and runtime kwargs.
- **Unified interfaces** — Drive everything from the **Python API**
  (`FlowerPowerProject`), the **CLI** (`flowerpower`), or the **web UI**
  ([Hamilton UI](https://hamilton.dagworks.io/en/latest/hamilton-ui/ui/)).
- **Executors** — Run locally, in a thread pool, or distributed with Ray.
- **Adapters** — Track lineage with the Hamilton Tracker, experiments with MLflow.
- **Extensible I/O** — CSV, JSON, Parquet, DeltaTable, DuckDB, PostgreSQL, MySQL,
  MSSQL, Oracle, SQLite, MQTT via the [`flowerpower-io`](https://legout.github.io/flowerpower-io) plugin.
- **Filesystem abstraction** — Local, S3, GCS, and more, through [fsspeckit](https://legout.github.io/fsspeckit).

## 📦 Installation

FlowerPower requires **Python 3.11+**. We recommend [uv](https://github.com/astral-sh/uv):

```bash
uv venv && source .venv/bin/activate
uv pip install flowerpower
```

Optional extras:

```bash
uv pip install 'flowerpower[io]'      # I/O plugins
uv pip install 'flowerpower[ui]'      # Hamilton UI
uv pip install 'flowerpower[ray]'     # distributed execution
uv pip install 'flowerpower[io,ui,ray]'   # combine the extras you need
```

## 🚀 Quick start

Create a project, a pipeline, and run it:

```bash
flowerpower init --name hello-flowerpower
cd hello-flowerpower
flowerpower pipeline new hello
flowerpower pipeline run hello
```

Or in Python:

```python
from flowerpower import FlowerPowerProject

# 1. create the project
FlowerPowerProject.new(name="hello-flowerpower")

# 2. load it and create a pipeline
project = FlowerPowerProject.load("hello-flowerpower")
project.pipeline_manager.creator.create_pipeline(name="hello")

# 3. (edit pipelines/hello.py + conf/pipelines/hello.yml, then run)
result = project.run("hello")
print(result)
```

### A pipeline module

Write your DAG as functions in `pipelines/hello.py`. Parameters come from YAML
and are wired in with Hamilton's `@parameterize`:

```python
from pathlib import Path
from hamilton.function_modifiers import parameterize
from flowerpower.cfg import Config

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="hello"
).pipeline.h_params

@parameterize(**PARAMS["greeting_message"])   # PARAMS is a dict — use ["..."]
def greeting_message(message: str) -> str:
    return f"{message},"

@parameterize(**PARAMS["target_name"])
def target_name(name: str) -> str:
    return f"{name}!"

def full_greeting(greeting_message: str, target_name: str) -> str:
    return f"{greeting_message} {target_name}"
```

```yaml
# conf/pipelines/hello.yml
params:
  greeting_message:
    message: "Hello"
  target_name:
    name: "World"
run:
  final_vars: [full_greeting]
```

`project.run("hello")` → `{'full_greeting': 'Hello, World!'}`.

📖 The full, step-by-step walkthrough is in the
[Tutorial](https://legout.github.io/flowerpower/quickstart/).

## ⚙️ Running pipelines

`FlowerPowerProject.run()` (and `PipelineManager.run()`) accept a `RunConfig` and/or
keyword overrides — kwargs always win:

```python
from flowerpower.cfg.pipeline.run import RunConfig

# simple
result = project.run("hello")

# with a RunConfig
result = project.run("hello", run_config=RunConfig(log_level="DEBUG"))

# with kwargs overrides
result = project.run(
    "hello",
    inputs={"greeting_message": {"message": "Hi"}},
    final_vars=["full_greeting"],
)
```

Async runs use Hamilton's async driver via `PipelineManager.run_async()`:

```python
from flowerpower.pipeline import PipelineManager

pm = PipelineManager(base_dir="hello-flowerpower")
result = await pm.run_async("hello")
```

See the docs for [RunConfig & builders](https://legout.github.io/flowerpower/advanced/),
[additional modules](https://legout.github.io/flowerpower/guide/additional-modules/),
and [adapters](https://legout.github.io/flowerpower/guide/adapters/).

## 🖥️ Web UI

Launch the Hamilton UI to visualize and inspect pipeline runs:

```bash
flowerpower ui
```

## 📖 Documentation

Full documentation — installation, tutorial, how-to guides, concepts, CLI, and
API reference — lives at **<https://legout.github.io/flowerpower/>**.

## 🤝 Contributing

Contributions are welcome. See the
[contributing guide](https://legout.github.io/flowerpower/contributing/) and open
issues or PRs against [legout/flowerpower](https://github.com/legout/flowerpower).

## 📜 License

MIT — see [LICENSE](LICENSE).
