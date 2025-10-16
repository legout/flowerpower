# Project Context

## Purpose
FlowerPower is a Python framework for building, configuring, and executing data processing pipelines. It emphasizes a modular, configuration‑driven approach using Hamilton for DAG-based pipeline definitions, with a unified interface (`FlowerPowerProject`), a Typer-based CLI, and optional Hamilton UI integration. Goals: make pipeline creation simple, predictable, and extensible across local and cloud environments.

## Tech Stack
- Runtime: Python >= 3.11
- Core: `sf-hamilton`, `sf-hamilton-sdk`, `msgspec`, `pyyaml`, `munch`
- Filesystems: `fsspec`, `fsspec-utils`, `s3fs` (others via fsspec)
- CLI/UX: `typer`, `rich`; Logging: `loguru`
- Optional extras: `opentelemetry-*` (Jaeger), `openlineage-python`, `ray`, `sf-hamilton-ui`, `flowerpower-io`
- Tooling: `uv` (env/build/publish), `ruff` (lint/format), `mypy` (types), `pytest` (+cov, +mocks), `bandit` and `safety` (security), `mkdocs` (+ material, mkdocstrings) for docs

## Project Conventions

### Code Style
- PEP 8 with full type hints; mypy strict-ish settings via `pyproject.toml`.
- Format with `ruff format`; lint with `ruff` rules: E,W,F,I,B, C4, UP, S; line length 88; per-file ignores allow `assert` in `tests/` and `examples/`.
- Imports organized by ruff/isort; avoid wildcard imports; modules use `snake_case`.
- Public API re-exported from `flowerpower/__init__.py`.

### Architecture & Structure
- Package layout: `src/flowerpower/{cfg,cli,pipeline,settings,utils}`.
- Facade entrypoint: `FlowerPowerProject` encapsulates project context and pipeline operations; CLI entrypoint: `flowerpower = flowerpower.cli:app`.
- Pipelines: Hamilton functions in Python modules under `pipelines/`; configured via YAML under `conf/` (`conf/project.yml`, `conf/pipelines/*.yml`).
- Config layer: `src/flowerpower/cfg/*` (e.g., `RunConfig`, builders) using `msgspec` models with safe path validation.
- Filesystem abstraction: `fsspec` with optional caching; dirs configurable via env vars `FP_CONFIG_DIR`, `FP_PIPELINES_DIR`, `FP_HOOKS_DIR`, `FP_CACHE_DIR`.
- Extension points: optional I/O plugins (`flowerpower-io`), adapters, observability backends.

### Testing & Quality
- Tests: `pytest`; unit + integration under `tests/` (e.g., `tests/cli/test_cli_integration.py`).
- Types: `mypy` with strict flags; missing-imports ignored for selected third-party modules.
- Lint/format: `ruff check` and `ruff format`.
- Security: `bandit` (code), `safety` (deps), ruff security rules (`S`). One-touch script: `scripts/security-audit.sh`.

### Git & Release Workflow
- Pre-commit: `ruff` (fix + format), `bandit`, `mypy` (see `.pre-commit-config.yaml`).
- Versioning: pre-push hook `.github/hooks/version-hook.sh` updates `CHANGELOG.md` and creates annotated tag `v<version>` from `pyproject.toml`.
- CI/CD: `.github/workflows/publish.yml` builds with `uv` and publishes to PyPI on pushes that modify `pyproject.toml` (requires `PYPI_TOKEN`).
- Branching/commits: feature branches + PRs; Conventional Commit style commonly used (not enforced).

## Domain Context
- Data engineering and analytics pipelines as Hamilton DAGs.
- Configuration-driven execution with layered configs: project (`conf/project.yml`) and per‑pipeline (`conf/pipelines/*.yml`).
- Examples: web scraping, ETL (sales), ML training (customer churn), and hello-world under `examples/`.

## Important Constraints
- Python >= 3.11.
- Prefer `uv` for environment management, builds, and publishing.
- Strong typing and security scanning are part of the dev/CI workflow.
- Use OpenSpec for proposing breaking changes, new capabilities, or architecture shifts (see `openspec/AGENTS.md`).

## External Integrations & Optional Components
- Observability: OpenTelemetry (Jaeger exporter), OpenLineage (optional).
- Execution/UI: Ray (optional), Hamilton UI (optional via `sf-hamilton-ui`; CLI: `flowerpower ui`).
- I/O Plugins: `flowerpower-io` optional extras for sources/sinks.

## How to Work With Pipelines
- Create: `PipelineManager.new(name)` or CLI `flowerpower pipeline new <name>`.
- Configure: edit `conf/pipelines/<name>.yml` (params, `run.final_vars`, executor, adapters).
- Run: Python API `FlowerPowerProject.run(...)` or CLI `flowerpower pipeline run <name>` using `--run-config` or `--inputs/--final-vars` overrides.
- Visualize: `PipelineManager.save_dag/show_dag` (Graphviz required for rendering).

## Developer Commands (informal)
- Lint/format: `uv run ruff check` && `uv run ruff format`
- Types: `uv run mypy src/flowerpower`
- Tests: `uv run pytest`
- Security: `bash scripts/security-audit.sh`
- Build/Publish: `uv build` && `uv publish` (CI handles standard publish)
