# FlowerPower — Project Roadmap

## Purpose

FlowerPower is a Python framework for building, configuring, and executing data processing pipelines. It wraps [Hamilton](https://github.com/apache/hamilton) to provide DAG-based dataflows with a configuration-driven approach (YAML), extensible I/O plugins, CLI, and web UI.

## Current State

- **Version:** 0.34.1
- **Python:** >= 3.11
- **Status:** Active development, published on PyPI
- **Recent work:** Added async execution support (`run_async`), composed pipeline modules (`additional_modules`), nested `RetryConfig`, executor overrides, and env overlay with YAML interpolation.
- **Structure:** Monorepo-style layout under `src/flowerpower/` with `cfg/`, `cli/`, `pipeline/`, `plugins/`, `settings/`, `utils/` packages. Tests under `tests/`. Examples under `examples/`.

## Architecture

- **`FlowerPowerProject`** — Unified API (load, init, run pipelines)
- **`PipelineManager`** — CRUD + run for pipelines (also usable standalone)
- **`PipelineRunner` / `RetryManager` / `ExecutionContext`** — Extracted from monolithic `Pipeline`
- **`Config` / `RunConfig` / `RunConfigBuilder`** — Layered config system (project.yml → pipeline.yml → kwargs)
- **`ExecutorConfig`** — Threadpool/multiprocessing/ray executor selection
- **I/O plugins** — External package `flowerpower-io` (CSV, JSON, Parquet, DeltaTable, DuckDB, SQL databases, MQTT, SQLite)
- **CLI** — Typer-based (`flowerpower init`, `pipeline run/new/delete/list`, `ui`)
- **Docs** — MkDocs Material site at legout.github.io/flowerpower

## Key Decisions Made

1. **Hamilton as DAG engine** — Core design choice; FlowerPower orchestrates Hamilton drivers and adds config/CLI/UI
2. **YAML-driven configuration** — Params + run config in `conf/pipelines/*.yml`; project-level in `conf/project.yml`
3. **Config precedence:** kwargs > `FP_PIPELINE__*` env > YAML > `FP_*` env > defaults
4. **RetryConfig nested block** — Migrated from flat retry fields; legacy fields emit deprecation warnings
5. **Async via Hamilton async_driver** — `run_async()` uses Hamilton's async driver; not opt-outable per-run
6. **additional_modules for composition** — Mix shared setup/teardown modules; string resolution with fallback to `pipelines.<name>`
7. **OpenSpec for change management** — Proposals/specs/tasks tracked in `openspec/`

## Milestones

- [x] v0.31.x — Executor config, parallel example, CLI alignment
- [x] v0.32.x — RetryConfig nesting, executor override fixes
- [x] v0.33.x — Pipeline refactor (extract Runner, RetryManager, ExecutionContext)
- [x] v0.34.x — Additional modules composition, async execution, docs
- [ ] Next — TBD

## Open Questions

- What's the next major feature or release focus?
- Any planned breaking changes?
