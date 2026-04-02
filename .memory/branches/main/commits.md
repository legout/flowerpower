# main

**Purpose:** Main project memory branch

---

## Commit 90250146 | 2026-03-27T06:49:06.793Z

### Branch Purpose

The main project memory branch, tracking the roadmap, core architecture decisions, and overall development of the FlowerPower Python framework.

### Previous Progress Summary

Initial commit.

### This Commit's Contribution

- Initialized Brain memory for FlowerPower (v0.34.1), a Python framework wrapping Apache Hamilton for YAML-driven DAG orchestration.
- Documented core architecture: `FlowerPowerProject` (unified API), `PipelineManager` (CRUD), and specialized `PipelineRunner`, `RetryManager`, and `ExecutionContext` components.
- Formalized key design decisions: Hamilton as the underlying DAG engine, YAML configuration with multi-layer precedence (kwargs > env > YAML), and a migration to nested `RetryConfig`.
- Mapped the project structure, including the core library (`src/flowerpower/`), external I/O plugins (`flowerpower-io`), and the Typer-based CLI.
- Summarized recent development milestones: async execution support (`run_async`), module composition via `additional_modules`, and environment overlays with YAML interpolation.
- Integrated `OpenSpec` for authoritative change management and architectural planning.
- Verified the current production status: Python >= 3.11 compatibility, active PyPI publishing, and comprehensive MkDocs documentation.

---

## Commit 908f64ef | 2026-03-27T10:57:45.930Z

### Branch Purpose

The main project memory branch, tracking the roadmap, core architecture decisions, and overall development of the FlowerPower Python framework.

### Previous Progress Summary

Initial commit.

### This Commit's Contribution

- Fixed a fundamental configuration lifecycle bug by resolving `CONFIG_DIR` and `PIPELINES_DIR` at runtime rather than binding stale import-time defaults in `load`/`save` methods.
- Standardized the configuration filesystem layout by normalizing pipeline names (e.g., `group.my-pipeline` → `group/my_pipeline.yml`) during `PipelineConfig.save()`.
- Enhanced portability in `PipelineConfig.to_yaml()` by replacing the private `fs._parent()` API with a standard `posixpath` implementation.
- Streamlined `PipelineRegistry.new()` by consolidating the configuration write logic, eliminating redundant legacy write/rename workarounds.
- Improved API consistency in `FlowerPowerProject.new()` by converting low-level `SecurityError` exceptions into clean, user-facing `ValueError` messages.
- Normalized project initialization in `initialize_project()` to ensure `storage_options` defaults to `{}` instead of `None`, matching the internal project API.
- Refined error reporting in `run`/`run_async` to suppress confusing "pipeline ''" logs when a pipeline name is missing.
- Resolved a critical test suite hang by correctly patching the Hamilton `driver.Builder` in `tests/pipeline/test_runner.py`.

---

## Commit a4705e48 | 2026-03-27T13:14:04.196Z

### Branch Purpose

The main development branch for FlowerPower, tracking the core framework architecture, configuration lifecycle, and Hamilton-based DAG orchestration features.

### Previous Progress Summary

FlowerPower is a YAML-driven DAG orchestration framework built on Apache Hamilton, providing a configuration-centric approach to data pipelines. The project has matured through the establishment of a multi-layered architecture featuring a unified `FlowerPowerProject` API and a coordinated `PipelineManager`. Key progress includes the implementation of async execution, environment-based configuration overlays, and robust pipeline discovery. Recent stability improvements resolved critical lifecycle bugs in path resolution and project initialization while standardizing the filesystem layout for pipeline configurations.

### This Commit's Contribution

- Mapped the core execution flow from the `FlowerPowerProject` facade through `PipelineExecutor` to the specialized `PipelineRunner` and `ExecutionContextBuilder`.
- Confirmed the layered configuration precedence model where runtime overrides take priority over environment-specific overlays and YAML-defined defaults.
- Identified `PipelineRegistry` as the primary complexity hub, managing high-stakes filesystem-to-module mapping, caching, and lifecycle operations.
- Flagged the potential for mapping drift between CLI parameters and runtime `RunConfig` objects as a significant maintenance hotspot.
- Documented the transition from legacy flat retry fields to a nested `RetryConfig` structure in the configuration model.
- Observed that the local environment currently lacks the `Hamilton` dependency, which prevents full test suite validation in this session.

---

## Commit 2be047bd | 2026-03-27T17:42:00.154Z

### Branch Purpose

The main development branch for FlowerPower, tracking the core framework architecture, configuration lifecycle, and Hamilton-based DAG orchestration features.

### Previous Progress Summary

FlowerPower is a YAML-driven DAG orchestration framework built on Apache Hamilton, providing a configuration-centric approach to data pipelines. The project has established a layered architecture featuring a unified `FlowerPowerProject` API, a central `PipelineManager`, and specialized execution components (Runner, Executor, ContextBuilder). Key progress includes the implementation of async support and environment-based configuration overlays, alongside the resolution of critical lifecycle bugs in path resolution and filesystem normalization. Development is currently focused on standardizing the registry's lifecycle operations and hardening the codebase through rigorous linting and architectural audits.

### This Commit's Contribution

- Eliminated 419 linting errors to reach a zero-error baseline, significantly improving code quality and maintainability across the core library and tests.
- Hardened exception handling by addressing 44 `B904` (raise-without-from) violations, ensuring proper traceback preservation during error wrapping.
- Improved security posture by refactoring subprocess calls to use absolute paths and disabling `shell=True` to prevent injection vulnerabilities.
- Modernized the codebase using `ruff` autofixes for collection literals (`C401/C408`), `StrEnum` usage (`UP042`), and strict zip operations (`B905`).
- Conducted a deep architectural audit identifying significant "code drift," specifically the existence of two divergent `RunConfigBuilder` implementations.
- Discovered several dead or internally unused utility helpers in `misc.py`, `security.py`, and `env.py` that are candidates for removal.
- Flagged a likely-broken OpenTelemetry integration path where `init_tracer` was being called with a signature mismatch and zero test coverage.

---

## Commit 892829d0 | 2026-04-01T21:18:00.560Z

### Branch Purpose

The main development branch for FlowerPower, tracking the core framework architecture, configuration lifecycle, and Hamilton-based DAG orchestration features.

### Previous Progress Summary

FlowerPower is a YAML-driven DAG orchestration framework built on Apache Hamilton, providing a configuration-centric approach to data pipelines. The project has established a layered architecture featuring a unified `FlowerPowerProject` API, a central `PipelineManager`, and specialized execution components. After reaching a zero-error linting baseline through a massive refactor that hardened exception handling and security, development has shifted toward resolving architectural "code drift" and hardening core settings. Recent work includes standardizing pipeline name formatting and initiating a robust overhaul of environment variable parsing to prevent crashes and ensure correct boolean evaluation. A project-wide status review has mapped out 16 active P2 tasks focused on utils cleanup, dead code removal, and consolidating redundant configuration builders.

### This Commit's Contribution

- Completed a comprehensive project status review using the `tk` ticket system, identifying 16 open P2 tasks ready for development and 6 blocked by dependencies.
- Fixed name formatting bugs in `PipelineRegistry.delete()` by extracting a shared `_format_pipeline_name()` helper, now used by new, delete, and load operations.
- Identified a critical flaw in environment variable parsing where `bool(os.getenv())` incorrectly treats `"False"` as truthy, leading to a planned overhaul of boolean settings.
- Introduced `_safe_cpu_count()` and `_env_bool()` helpers in `settings/executor.py` to prevent `TypeError` crashes when `os.cpu_count()` returns `None`.
- Rejected the initial implementation of `flo-1lti` (Gate: REVISE) due to missing edge-case tests and incomplete application of the new boolean parser in `hamilton.py`.
- Prioritized high-impact maintenance tasks including the removal of dead utility code and the standardization of the divergent `RunConfigBuilder` implementations.
