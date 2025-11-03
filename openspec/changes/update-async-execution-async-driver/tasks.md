## 1. Implementation
- [ ] 1.1 Add `async_driver: bool` to `RunConfig` (default False globally; treated as True in `run_async` unless explicitly set False).
- [ ] 1.2 Extend `merge_run_config_with_kwargs` to accept/merge `async_driver`.
- [ ] 1.3 Update `PipelineRunner.run_async` to use `hamilton.async_driver`:
  - Build the same module list as sync path (respecting `additional_modules`).
  - Use the async driver to execute, rather than calling `.execute_async` on the sync driver.
  - Keep logging and reload behaviour.
- [ ] 1.4 Provide clear error messaging when import fails for the async driver.
- [ ] 1.5 Ensure adapters are applied as in sync mode.

## 2. Tests
- [ ] 2.1 `run_async` constructs and uses the async driver (mock/patch to assert).
- [ ] 2.2 Logging and reload behaviours are honoured.
- [ ] 2.3 Adapters propagate to the async driver.
- [ ] 2.4 Helpful ImportError when `hamilton.async_driver` is unavailable.

## 3. Documentation
- [ ] 3.1 README: add an "Asynchronous Execution" section with example usage via `PipelineManager.run_async`.
- [ ] 3.2 API docstrings: update `PipelineManager.run_async` to clarify its use of Hamilton’s async driver and the `async_driver` toggle in `RunConfig`.
- [ ] 3.3 CHANGELOG: add entry under Unreleased.

## 4. Rollout
- [ ] 4.1 Submit PR for review.
- [ ] 4.2 After merge/deploy, archive change with `openspec archive update-async-execution-async-driver --skip-specs --yes`.

