# Project Context

## Purpose
FlowerPower is a Python framework for building, configuring, and executing data processing pipelines. It emphasizes a modular, configuration‑driven approach using Hamilton for DAG-based pipeline definitions, with a unified interface (`FlowerPowerProject`), a CLI (Typer), and optional UI integration. The goals are to make pipeline creation simple, predictable, and extensible across local and cloud environments.

## Tech Stack
- Python 3.11+
- Core: `sf-hamilton`, `msgspec`, `pyyaml`, `munch`
- Filesystems: `fsspec`, `s3fs`, `fsspec-utils`
- CLI/UX: `typer`, `rich`
- Optional: `opentelemetry-*`, `openlineage-python`, `ray`, `sf-hamilton-ui`, `flowerpower-io`
- Tooling: `uv` (env/build), `ruff` (lint/format), `mypy` (types), `pytest` (tests), `bandit` and `safety` (security), `mkdocs` (+ mkdocstrings, material) for docs

## Project Conventions

### Code Style
- PEP 8 with type hints everywhere (mypy strict settings enabled).
- Formatting via `ruff format`; lint via `ruff` with rules: E,W,F,I,B,C4,UP,S; line length 88; per-file ignores allow `assert` in `tests/` and `examples/`.
- Imports managed by ruff/isort; prefer explicit names; avoid wildcard imports.
- Public API exposed via `flowerpower` package; keep module naming snake_case.

### Architecture Patterns
- Facade entrypoint: `FlowerPowerProject` encapsulates access to the pipeline subsystem.
- Pipeline subsystem: `PipelineManager` handles creation, configuration, execution, visualization.
- Pipeline logic defined as Hamilton functions in Python modules (DAG) under `pipelines/`; configured via YAML under `conf/` (per‑project and per‑pipeline files).
- Configuration layer under `src/flowerpower/cfg/*` (e.g., `RunConfig`, builders) with msgspec-based models.
- Plugin/extension points: I/O plugins (`flowerpower-io` optional), adapters, and filesystem abstraction via `fsspec`.
- CLI built with Typer (`flowerpower.cli:app`); optional UI via `sf-hamilton-ui`.

### Testing Strategy
- Test runner: `pytest` with unit and integration tests under `tests/`.
- CLI integration tests use Typer’s `CliRunner` (see `tests/cli/test_cli_integration.py`).
- Pipeline behavior covered by unit tests (see `tests/pipeline/*`).
- Type checking with `mypy` (strict settings in `pyproject.toml`).
- Security checks: `bandit` (code) and `safety` (dependencies); ruff includes `S` security rules.
- Run via `uv run pytest`; type/security audits via `scripts/security-audit.sh`.

### Git Workflow
- Pre-commit hooks: `ruff` (fix + format), `bandit`, and `mypy` (configured in `.pre-commit-config.yaml`).
- Pre-push versioning: `.github/hooks/version-hook.sh` updates `CHANGELOG.md` and creates annotated git tags (`v<version>` from `pyproject.toml`).
- CI/CD: GitHub Actions workflow `publish.yml` builds with `uv` and publishes to PyPI on pushes that modify `pyproject.toml` (requires `PYPI_TOKEN`).
- Branching/commit conventions: Not explicitly documented; typical feature branches + PRs recommended. Confirm if Conventional Commits or a specific branching model should be enforced.

## Domain Context
- Data engineering and analytics pipelines implemented as Hamilton DAGs.
- Configuration-driven execution with layered configs: project (`conf/project.yml`) and per‑pipeline (`conf/pipelines/*.yml`).
- Example domains included: web scraping, ETL (sales), ML training (customer churn) under `examples/`.

## Important Constraints
- Python >= 3.11.
- Prefer `uv` for environment management, builds, and publishing.
- Strong typing (mypy strict) and security scanning (bandit, safety) are part of CI/dev workflow.
- Use OpenSpec for planning/approval of breaking changes, new capabilities, or architecture shifts (see `openspec/AGENTS.md`).

## External Dependencies
- Hamilton (sf-hamilton) for DAG execution.
- Filesystem backends via `fsspec`/`s3fs` (S3 and other remote stores).
- Optional observability: OpenTelemetry (Jaeger exporter supported), OpenLineage.
- Optional execution/UI: Ray, Hamilton UI.
- Dev/ops (docker/): configurations for Prometheus, Grafana, Mosquitto, and Caddy for local setups.
