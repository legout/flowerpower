## Why
Running a single pipeline module limits composition. Many FlowerPower projects benefit from shared setup/teardown steps (e.g., DB connections, secrets bootstrapping) and auxiliary pipelines. Hamilton natively supports composing multiple modules via `driver.Builder.with_modules(...)`. FlowerPower should expose this ability so users can run `pm.run("pipeline_1", additional_modules=["setup"])` without custom wiring.

## What Changes
- Add runtime support for specifying additional pipeline modules to load alongside the main pipeline.
- Extend `RunConfig` with `additional_modules` (list of strings or modules at runtime) and plumb through to the runner.
- Update runner to import and pass all modules to `driver.Builder.with_modules(*modules)`.
- Ensure `reload=True` reloads all loaded modules.
- Support both sync and async execution paths.

Non‑breaking: Defaults preserve current single‑module behavior.

## Impact
- Affected specs: `pipeline-execution`
- Affected code:
  - `src/flowerpower/cfg/pipeline/run.py`
  - `src/flowerpower/utils/config.py`
  - `src/flowerpower/pipeline/runner.py`
  - `src/flowerpower/pipeline/manager.py` (docs / passthrough)
  - Tests under `tests/pipeline/` and `tests/cfg/`

## Out of Scope
- Changes to persistence, scheduling, or adapters behavior beyond module loading.
- DAG conflict resolution beyond standard Hamilton rules (last definition wins).

## Risks / Mitigations
- Import errors for missing modules → raise clear ImportError with actionable path/name tips.
- Conflicting node names across modules → document precedence (order) and suggest namespacing.

## Rollout
- Add tests for sync/async, reload, error handling.
- Update README usage and CHANGELOG.

