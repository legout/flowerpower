# Project Context (Proposed for openspec/project.md)

## Purpose
FlowerPower is a Python framework for building, configuring, and executing data processing pipelines. It uses Hamilton for DAG-based pipeline definitions and provides a unified interface (FlowerPowerProject), a Typer-based CLI, optional Hamilton UI integration, and filesystem abstraction for local and remote execution.

## Tech Stack
- Runtime: Python >= 3.11
- Core libraries: sf-hamilton, sf-hamilton-sdk, msgspec, pyyaml, munch
- Filesystems: fsspec, fsspeckit, s3fs (others via fsspec)
- CLI/UX: typer, rich
- Logging: loguru
- Optional extras: openlineage-python, opentelemetry-* (Jaeger), ray, sf-hamilton-ui, flowerpower-io
- Tooling: uv (env, build, publish), ruff (lint/format), mypy (types), pytest (+ pytest-cov, pytest-mock), bandit and safety (security), mkdocs (+ material, mkdocstrings)

## Project Conventions

### Code Style
- PEP 8 with full type hints; mypy strict-ish settings in pyproject.toml.
- Ruff for linting and formatting: line length 88; target-version py311; rules E,W,F,I,B,C4,UP,S; selective ignores; allow asserts in tests/ and examples/.
- Imports organized via ruff/isort; avoid wildcard imports; modules in snake_case; public API re-exported from flowerpower/__init__.py.

### Architecture & Structure
- Package layout: src/flowerpower/{cfg,cli,pipeline,settings,utils}.
- Facade: FlowerPowerProject encapsulates project context and exposes pipeline operations; CLI entrypoint: flowerpower = flowerpower.cli:app (Typer app with subcommands under cli/pipeline.py).
- Pipelines: Python modules under pipelines/ using Hamilton functions; per-pipeline configuration YAMLs under conf/pipelines/*.yml; project config under conf/project.yml.
- Managers: PipelineManager orchestrates config loading, registry, executor, lifecycle, I/O, and visualization. Security: config path validation to prevent directory traversal (cfg/base.py).
- Filesystem abstraction: fsspec with optional caching; storage_options passed through; directories configurable via env vars FP_CONFIG_DIR, FP_PIPELINES_DIR, FP_HOOKS_DIR, FP_CACHE_DIR.

### Testing & Quality
- Tests: pytest; unit + integration tests under tests/ (e.g., tests/cli/test_cli_integration.py, tests/pipeline/*).
- Types: mypy (pyproject config); missing-imports ignored for some third-party modules.
- Lint/format: ruff check and ruff format; CI-ready.
- Security: bandit (code), safety (deps), ruff security rules (S). One-touch script: scripts/security-audit.sh.

### Git & Release Workflow
- Pre-commit: ruff (fix + format), bandit, mypy (see .pre-commit-config.yaml).
- Versioning: pre-push hook .github/hooks/version-hook.sh updates CHANGELOG.md and creates annotated tag v<version> from pyproject.toml.
- CI/CD: .github/workflows/publish.yml builds with uv and publishes to PyPI on pushes that change pyproject.toml (requires PYPI_TOKEN secret).
- Branching: default main; Conventional Commit-style messages observed (not enforced by tooling).

## Domain Context
- Data engineering and analytics workflows as Hamilton DAGs; configuration-driven execution with layered configs (project + per-pipeline). Typical use cases: ETL, ML training, web scraping. Examples live under examples/ (hello-world, data-etl-pipeline, web-scraping-pipeline, ml-training-pipeline, pipeline-only-example).

## Important Constraints
- Requires Python >= 3.11.
- Prefer uv for environment management, builds, and publishing.
- Strong typing and security scanning integrated into dev workflow.
- Use OpenSpec for proposing breaking changes, new capabilities, or architecture shifts (see openspec/AGENTS.md).

## External Integrations & Optional Components
- Observability: OpenTelemetry (Jaeger exporter), OpenLineage (optional).
- Execution/UI: Ray (optional), Hamilton UI (optional via sf-hamilton-ui; CLI command flowerpower ui).
- I/O Plugins: flowerpower-io optional extras for data sources/sinks.

## How to Work With Pipelines
- Create: PipelineManager.new(name) or CLI flowerpower pipeline new <name>.
- Configure: Edit conf/pipelines/<name>.yml (params, run.final_vars, executor, adapters).
- Run: Python API via FlowerPowerProject.run(...) or CLI flowerpower pipeline run <name> with --run-config or --inputs/--final-vars overrides.
- Visualize: PipelineManager.save_dag/show_dag; optional Graphviz required.

## Developer Commands (informal)
- Lint/format: uv run ruff check && uv run ruff format
- Types: uv run mypy src/flowerpower
- Tests: uv run pytest -q
- Security: bash scripts/security-audit.sh
- Build/Publish: uv build && uv publish (CI handles standard publish)
