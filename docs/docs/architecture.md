# Architecture

FlowerPower is an orchestration and configuration layer on top of [Hamilton](https://hamilton.dagworks.io/). Hamilton lets you define a data pipeline as a DAG of plain Python functions: each function is a node, and its arguments declare dependencies. FlowerPower adds project structure, YAML-driven configuration, execution plumbing, and lifecycle management so that Hamilton pipelines can be organized, configured, and run as production projects.

## What FlowerPower adds to Hamilton

In a pure Hamilton workflow you import modules into a `Driver` and call `execute()`. FlowerPower keeps that model but wraps it in conventions:

- **Projects** — a directory layout (`conf/`, `pipelines/`, `hooks/`) that separates configuration from code.
- **Configuration** — `project.yml` plus per-pipeline YAML files, merged with environment overrides and runtime `RunConfig`.
- **Execution** — a runtime stack that handles sync and async drivers, adapters, retries, logging, and executors.
- **I/O & visualization** — helpers for importing/exporting pipelines, rendering DAGs, and working with remote filesystems.

You still write Hamilton functions. FlowerPower discovers them, wires them into a driver, and runs them.

## Core components

```mermaid
graph TD
    A[FlowerPowerProject] -->|owns| B(PipelineManager)
    B -->|manages| C[PipelineConfigManager]
    B -->|discovers/creates| D[PipelineRegistry]
    D -->|facade| D1[PipelineCatalog]
    D -->|facade| D2[PipelineLoader]
    D -->|facade| D3[PipelineModuleResolver]
    B -->|creates| D4[PipelineCreator]
    B -->|executes| E[PipelineExecutor]
    B -->|visualizes| F[PipelineVisualizer]
    B -->|imports/exports| G[PipelineIOManager]
    E -->|runs| H[Pipeline]
    H -->|drives| I[Hamilton Driver]
    H -->|via| J[PipelineRunner]
    J -->|uses| K[ExecutionContextBuilder]
    J -->|uses| L[RetryManager]
    J -->|uses| M[Telemetry / Logging helpers]
    K -->|creates| N[Hamilton Executor]
    K -->|resolves| O[Adapters]
        A
        B
        C
        D
        D1
        D2
        D3
        D4
        E
        F
        G
        H
        J
        K
        L
        M
        O
    end

    subgraph Hamilton
        I
        N
    end
```

### `FlowerPowerProject`

The public entry point. It creates or loads a project directory and exposes a `pipeline_manager` that does the real work. Use `FlowerPowerProject.new()` to scaffold a project and `FlowerPowerProject.load()` to open an existing one.

```python
from flowerpower import FlowerPowerProject
project = FlowerPowerProject.new(name="my_project")
project = FlowerPowerProject.load(".")
```

### `PipelineManager`

The operational hub. It is initialized with a base directory and an optional fsspec filesystem, then loads the project configuration and exposes the sub-managers listed below.

| Property / method | Responsibility |
| --- | --- |
| `creator` | Scaffolds new pipelines. |
| `registry` | Lists, loads, and deletes pipelines; manages hooks. |
| `executor` | Runs a pipeline synchronously or asynchronously. |
| `visualizer` | Renders or saves pipeline DAGs. |
| `io` | Imports/exports pipeline definitions. |
| `pipelines` | List of discovered pipeline names. |
| `summary` | Dictionary summarizing the project pipelines. |

The manager does not run the DAG directly; it delegates to a `Pipeline` instance, which owns a `PipelineRunner`.

### `PipelineRegistry` — facade over catalog, loader, and resolver

`PipelineRegistry` is a compatibility facade. It composes three internal modules so that discovery, loading, and caching concerns each have a single owner:

- **`PipelineCatalog`** — pipeline file discovery, canonical name derivation (including nested modules and stored YAML names), listing, metadata payloads, and presentation-free summary assembly.
- **`PipelineLoader`** — config and module loading via `PipelineConfigManager` + `PipelineModuleResolver`, `Pipeline` instance construction, and cache/reload invalidation.
- **`PipelineModuleResolver`** — the single shared import policy: package-root fallback, hyphen-to-underscore handling, candidate generation, de-duplication, and reload. The runner and visualizer use the same resolver so import behavior is decided once.

The public methods (`list_pipelines`, `get_summary`, `load_config`, `load_module`, `get_pipeline`, `clear_cache`, `new`/`delete` aliases, `add_hook`) remain source-compatible and delegate to these modules. See [ADR 0002](adr/0002-split-pipeline-registry-into-catalog-loader-and-module-resolver.md) for the decision record.

## Execution runtime stack

When you call `project.run("my_pipeline")`, the request flows through a small stack of dedicated helpers so the pipeline object itself stays focused on configuration.

### `PipelineRunner`

`PipelineRunner` is the facade for a single execution. It:

- Clones and merges the pipeline's default `RunConfig` with any runtime kwargs.
- Resolves the Python modules that contain the Hamilton functions (including `additional_modules`).
- Reloads modules when `reload=True`.
- Delegates to `ExecutionContextBuilder` for adapters and executors.
- Wraps the actual Hamilton call in `RetryManager`.

It has symmetric `run()` and `run_async()` paths.

### `ExecutionContextBuilder`

Builds the concrete context needed for a Hamilton execution: a Hamilton executor, an optional shutdown/cleanup callback, and the list of adapters to apply. It resolves configuration from three sources in priority order:

1. Runtime `RunConfig`.
2. Per-pipeline `conf/pipelines/<name>.yml`.
3. Project-wide `conf/project.yml`.

It also handles Ray shutdown hooks when the Ray adapter is enabled and configured to shut down on completion.

### `RetryManager`

Implements exponential backoff with jitter. It retries the pipeline execution on configured exceptions, calls optional success/failure callbacks, and logs each attempt. The same logic is used for both sync and async runs.

### Telemetry and logging helpers

`initialize_telemetry()` and `ensure_logging_initialized()` are used to avoid import-time side effects and to make log-level overrides predictable. Logging is set up once per process and reused thereafter.

## Layered configuration system

Configuration is merged in strict precedence, highest first:

1. **Runtime kwargs / `RunConfig`** — values passed to `run()` or built with `RunConfigBuilder`.
2. **Environment overlays** — variables prefixed with `FP_PIPELINE__*` or `FP_PROJECT__*` using double-underscore nested paths (for example, `FP_PIPELINE__RUN__LOG_LEVEL=DEBUG`). Values are JSON-coerced when possible.
3. **YAML after environment interpolation** — `${VAR}`, `${VAR:-default}`, `${VAR-default}`, `${VAR:?err}`, and `$${...}` escapes are expanded. Valid JSON strings become typed values.
4. **Global shims** — `FP_LOG_LEVEL`, `FP_EXECUTOR`, `FP_EXECUTOR_MAX_WORKERS`, `FP_EXECUTOR_NUM_CPUS`, `FP_MAX_RETRIES`, `FP_RETRY_DELAY`, `FP_JITTER_FACTOR` are used only when the corresponding specific key is absent.
5. **Code defaults** — struct defaults on `RunConfig` and related configuration classes.

!!! tip
    For a deeper look at overrides, environment variables, and adapter configuration, see [Advanced configuration](advanced.md).

## Filesystem abstraction

FlowerPower uses `fsspeckit` for filesystem access, so the same project can live on local disk, S3, GCS, or another `fsspec`-compatible backend. The `storage_options` passed to `FlowerPowerProject` or `PipelineManager` are forwarded to the filesystem constructor, and a local cache is configured automatically when remote storage is used.

```python
PipelineManager(
    base_dir="s3://my-bucket/project",
    storage_options={"key": "ACCESS_KEY", "secret": "SECRET_KEY"},
)
```

## Security

FlowerPower validates path fragments before using them to build filesystem paths. Functions such as `validate_file_path`, `validate_pipeline_name`, and `validate_directory_fragment` reject directory-traversal patterns like `../../../etc/passwd`. A `SecurityError` is raised on violations, keeping project and pipeline names bounded to the intended directory tree.

## Summary

FlowerPower does not replace Hamilton; it operationalizes it. You write plain Python functions that Hamilton turns into a DAG. FlowerPower provides the project scaffold, the configuration hierarchy, the execution runtime, and the lifecycle utilities that turn a notebook script into a maintainable, configurable pipeline project.
