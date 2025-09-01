# FlowerPower: Data Pipeline Orchestration

Welcome to the official documentation for **FlowerPower**, a powerful Python library designed to help you build, configure, schedule, and execute data processing pipelines with ease.

[
  ![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)
](https://github.com/legout/flowerpower)

FlowerPower streamlines complex data workflows by integrating the modularity of [Hamilton](https://hamilton.dagworks.io/) for pipeline logic with optional job scheduling capabilities.

## Get Started

Ready to dive in? Our **[Quickstart Guide](quickstart.md)** will walk you through installing FlowerPower and running your first pipeline in just a few minutes.

## Core Concepts

FlowerPower is built around a few key concepts that make it both powerful and flexible:

*   **Modular Pipeline Design**: Define your data transformations as a collection of simple Python functions. FlowerPower, using Hamilton, automatically understands their dependencies and assembles them into a Directed Acyclic Graph (DAG).
*   **Configuration-Driven**: Separate your pipeline logic from its execution parameters. Environments, data sources, and pipeline settings are all managed through clear and simple YAML files.
*   **Optional Job Scheduling**: Scale your data processing by offloading tasks to a distributed job queue. FlowerPower provides a seamless interface for sending, managing, and monitoring asynchronous jobs with optional scheduler support.
*   **Unified Project Interface**: Interact with your pipelines through the method that suits you best—a Python API (`FlowerPowerProject`), a command-line interface (CLI), or a web-based UI for visualization and monitoring.
*   **Extensible I/O**: Easily read from and write to various data sources with built-in and custom I/O plugins, ensuring your pipelines can connect to any data, anywhere.

!!! note "A Note on Hamilton"

    FlowerPower acts as an orchestrator, not a replacement. You will still write your pipeline logic using Hamilton's function-based syntax. FlowerPower's role is to provide a structured project environment and simplify pipeline management.