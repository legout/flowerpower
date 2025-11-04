## Why
Current asynchronous execution attempts to call `execute_async` on the standard
Hamilton driver (`hamilton.driver`), which is not supported. As a result, async
paths do not work reliably. Hamilton provides a dedicated async driver under
`hamilton.async_driver` that must be used for correct asynchronous execution.

## What Changes
- Switch the internal async execution path to use `hamilton.async_driver`.
- Add a configuration toggle to explicitly control async driver usage:
  - Introduce `RunConfig.async_driver: bool` (default: True for `run_async()` path).
  - Allow overriding through `PipelineManager.run_async(..., async_driver=...)` and
    `merge_run_config_with_kwargs`.
- Keep `PipelineManager.run` strictly synchronous; `PipelineManager.run_async` is the
  primary async API.
- Ensure adapters and logging/reload behaviour remain consistent across sync/async.
- Provide clear failure messages when `hamilton.async_driver` is not available.

## Impact
- Files to update:
  - Code: `src/flowerpower/pipeline/runner.py`, `src/flowerpower/utils/config.py`,
    `src/flowerpower/cfg/pipeline/run.py`, and tests in `tests/pipeline/`.
  - Docs: README (new Asynchronous Execution section), API docstrings for
    `PipelineManager.run_async`, CHANGELOG (Unreleased).

## Non‑Goals / Out of Scope
- Changing the sync execution path or default behaviour of `PipelineManager.run`.
- Guaranteeing compatibility with every remote executor in async mode; we’ll document
  known limitations and fallbacks.

## Risks / Mitigations
- Missing `hamilton.async_driver`: raise an ImportError with guidance on the minimum
  Hamilton version that supports the async driver and how to upgrade.
- Adapter compatibility: reuse existing adapter creation; add a targeted test to
  ensure adapters are passed through to the async driver.
- Executor interplay: prefer local/synchronous executors for async mode; document
  limitations where remote executors are not applicable.

## Acceptance Criteria
- `PipelineManager.run_async(...)` uses `hamilton.async_driver` and successfully
  executes a composed DAG (with or without `additional_modules`).
- `RunConfig.async_driver` default behaviour: True when invoking `run_async`, can be
  overridden via RunConfig or kwargs.
- Logging (`log_level`) and `reload=True` are honoured in async runs.
- Helpful ImportError when the async driver cannot be imported.
- Tests cover the async path using the async driver and key behaviours.

