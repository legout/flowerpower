# FlowerPower: Data Pipeline Orchestration

Welcome to the official documentation for **FlowerPower**, a powerful Python library designed to help you build, configure, schedule, and execute data processing pipelines with ease.

[
  ![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)
](https://github.com/legout/flowerpower)

FlowerPower streamlines complex data workflows by integrating the modularity of [Hamilton](https://hamilton.dagworks.io/) for pipeline logic with optional job scheduling capabilities.

## Get Started

Ready to dive in? Our **[Quickstart Guide](quickstart.md)** will walk you through installing FlowerPower and running your first pipeline in just a few minutes.

Looking for more? Check out these guides:

- [Compose Pipelines With Additional Modules](guide/additional-modules.md)
- [Asynchronous Execution](guide/async-execution.md)

## Core Concepts

FlowerPower is built around a few key concepts that make it both powerful and flexible:

*   **Modular Pipeline Design**: Define your data transformations as a collection of simple Python functions. FlowerPower, using Hamilton, automatically understands their dependencies and assembles them into a Directed Acyclic Graph (DAG).
*   **Configuration-Driven**: Separate your pipeline logic from its execution parameters. Environments, data sources, and pipeline settings are all managed through clear and simple YAML files.
    - Precedence (highest wins): runtime kwargs/RunConfig > env overlays (`FP_PIPELINE__*`, `FP_PROJECT__*`) > YAML (after `${VAR}` interpolation) > global shims (`FP_LOG_LEVEL`, `FP_EXECUTOR`, …) > code defaults.
    - YAML supports Docker Compose–style env interpolation: `${VAR}`, `${VAR:-default}`, `${VAR?err}`; JSON values are coerced when valid.
*   **Configurable Pipeline Scheduling**: Define scheduling parameters for pipelines via configuration files. FlowerPower supports configuring job scheduling options, but runtime scheduling is not yet implemented.
*   **Unified Project Interface**: Interact with your pipelines through the method that suits you best—a Python API (`FlowerPowerProject`), a command-line interface (CLI), or a web-based UI for visualization and monitoring.
*   **Extensible I/O**: Easily read from and write to various data sources with built-in and custom I/O plugins, ensuring your pipelines can connect to any data, anywhere.

!!! note "A Note on Hamilton"

    FlowerPower acts as an orchestrator, not a replacement. You will still write your pipeline logic using Hamilton's function-based syntax. FlowerPower's role is to provide a structured project environment and simplify pipeline management.
