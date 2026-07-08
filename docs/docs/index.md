# FlowerPower

FlowerPower is a Python framework that builds data pipelines on top of [Hamilton](https://hamilton.dagworks.io/). You write ordinary Python functions; FlowerPower handles configuration, execution, CLI, UI, and I/O so your project stays organized and portable.

## Choose your path

- **New here?** [Install FlowerPower](installation.md) and follow the [Quickstart tutorial](quickstart.md) to run your first pipeline.
- **Looking for task guides?** See [How-to guides](guide/additional-modules.md) for composing modules, [async execution](guide/async-execution.md), [adapters](guide/adapters.md), and [advanced workflows](advanced.md).
- **Want the big picture?** Read the [Architecture concepts](architecture.md) overview.
- **Need API details?** Browse the [CLI reference](cli.md) and [API reference](api/index.md).
- **Prefer examples?** Explore the [example projects](examples.md).
- **Interested in contributing?** Check out the [Contributing guide](contributing.md).

## What is FlowerPower?

- **Modular DAGs via Hamilton:** define transformations as plain Python functions and let Hamilton assemble them into a directed acyclic graph.
- **Config-driven YAML:** separate pipeline logic from parameters, adapters, and runtime settings using layered YAML and environment variables.
- **Unified interfaces:** interact with the same project through the Python API, the CLI, or a web-based UI.
- **Filesystem abstraction:** run locally or against remote storage (S3, GCS, etc.) through fsspec-compatible filesystems.
- **Extensible I/O:** connect to CSV, JSON, Parquet, Delta, DuckDB, SQL databases, and more via optional I/O plugins.

!!! note "FlowerPower is an orchestration layer"

    It does not replace Hamilton. You still write pipeline logic with Hamilton's function-based syntax; FlowerPower adds project structure, configuration, and lifecycle tooling.

Source code and issue tracker are on [GitHub](https://github.com/legout/flowerpower).
