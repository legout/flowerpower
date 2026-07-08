# Tutorial: Your First Pipeline

This tutorial walks you through building and running a complete FlowerPower
pipeline from scratch. By the end you will have a project, a pipeline that
computes a greeting, and the result printed to your terminal.

Every snippet below was executed against FlowerPower **0.34.1** and is
copy-pasteable.

!!! info "What you should already know"
    Basic Python. You don't need to know [Hamilton](https://hamilton.dagworks.io/)
    beforehand — the one pattern you need is explained in [Step 3](#3-write-the-pipeline).

## Prerequisites

- **Python 3.11 or newer** (`python --version`).
- FlowerPower installed: `uv pip install flowerpower` (see
  [Installation](installation.md)).

---

## 1. Create a project

A FlowerPower project is a directory with a `conf/` folder (configuration) and a
`pipelines/` folder (your code). Create one with the CLI:

```bash
flowerpower init --name hello-flowerpower
cd hello-flowerpower
```

…or with Python:

```python
from flowerpower import FlowerPowerProject

project = FlowerPowerProject.new(name="hello-flowerpower")
```

This produces the standard layout:

```
hello-flowerpower/
├── conf/
│   ├── project.yml
│   └── pipelines/
└── pipelines/
```

!!! note "`.new()` creates, `.load()` opens"
    `FlowerPowerProject.new(...)` creates a **new** project.
    `FlowerPowerProject.load(...)` opens an **existing** one. The two are not
    interchangeable.

## 2. Create a pipeline

A pipeline is a Python module plus a YAML config. Scaffold both at once:

```bash
flowerpower pipeline new hello
```

…or:

```python
from flowerpower import FlowerPowerProject

project = FlowerPowerProject.load(".")
project.pipeline_manager.creator.create_pipeline(name="hello")
```

This writes `pipelines/hello.py` (your logic) and `conf/pipelines/hello.yml`
(its configuration).

## 3. Write the pipeline

Open `pipelines/hello.py` and replace its contents with:

```python
from pathlib import Path

from hamilton.function_modifiers import parameterize

from flowerpower.cfg import Config

# FlowerPower loads your pipeline parameters here. Don't change this line.
PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="hello"
).pipeline.h_params


@parameterize(**PARAMS["greeting_message"])
def greeting_message(message: str) -> str:
    """The greeting word."""
    return f"{message},"


@parameterize(**PARAMS["target_name"])
def target_name(name: str) -> str:
    """Who we're greeting."""
    return f"{name}!"


def full_greeting(greeting_message: str, target_name: str) -> str:
    """Combine the greeting and the target."""
    return f"{greeting_message} {target_name}"
```

### How parameters connect to functions

FlowerPower turns the `params:` block in your YAML into Hamilton
`@parameterize(...)` arguments and exposes them as `PARAMS`. The rule is
simple:

> **Each params key matches the function it feeds, and its value is that
> function's keyword arguments.**

Because `PARAMS` is a plain dictionary, you access entries with **dictionary
syntax**: `PARAMS["greeting_message"]` — not `PARAMS.greeting_message`.

Hamilton reads each function's signature to wire the DAG. `full_greeting` takes
`greeting_message` and `target_name` as inputs, so Hamilton calls the two
`@parameterize`d functions first and feeds their outputs into `full_greeting`.
You never call these functions yourself.

## 4. Configure the pipeline

Open `conf/pipelines/hello.yml` and set the parameters and the output you want:

```yaml
params:
  greeting_message:
    message: "Hello"
  target_name:
    name: "World"

run:
  final_vars:
    - full_greeting   # the node(s) whose result you want returned
```

`params` holds values injected into your functions; `run.final_vars` lists which
nodes to compute and return.

## 5. Run it

### From the CLI

```bash
flowerpower pipeline run hello
```

### From Python

```python
from flowerpower import FlowerPowerProject

project = FlowerPowerProject.load(".")
result = project.run("hello")
print(result)
```

Either way, you get:

```python
{'full_greeting': 'Hello, World!'}
```

🎉 You just built and ran a FlowerPower pipeline.

### Override values at run time

You don't have to edit YAML to change a value. Pass overrides as kwargs (they
win over the file):

```python
result = project.run(
    "hello",
    inputs={"greeting_message": {"message": "Howdy"}, "target_name": {"name": "Partner"}},
    final_vars=["full_greeting"],
)
print(result)  # {'full_greeting': 'Howdy, Partner!'}
```

## Where to go next

- **See the DAG** you just built: `flowerpower pipeline show-dag hello`.
- **Configure execution** (executors, retry, caching): read
  [Configuration & Concepts](advanced.md).
- **Reuse nodes across pipelines** with `additional_modules`: see
  [Compose Multiple Modules](guide/additional-modules.md).
- **Run inside an event loop**: see [Asynchronous Execution](guide/async-execution.md).
- **Track runs** with the Hamilton Tracker / MLflow: see
  [Use Adapters](guide/adapters.md).
- **Every command and flag**: the [CLI reference](cli.md).
