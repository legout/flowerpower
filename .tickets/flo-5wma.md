---
id: flo-5wma
status: closed
deps: []
links: [flo-en6e, flo-h9yz]
created: 2026-02-17T10:44:55Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:pipeline, component:retry]
---
# Make retry callback execution compatible with CallbackSpec

## Task
Make retry callback handling execute configured callbacks correctly when callbacks are provided as CallbackSpec.

## Context
`RetryManager._handle_success(callback, result)` and `_handle_failure(callback, error)` expect a raw callable and call `callback(result, None)` or `callback(None, error)`. But `RunConfig.on_success` and `on_failure` store `CallbackSpec` objects, which are NOT callable.

The `CallbackSpec` struct has `func`, `args`, and `kwargs` fields — the retry manager needs to unwrap these before calling.

Note: `utils/callback.py` has elaborate callback handling logic, but it's dead code (never imported by production). The fix should be simple: unwrap `CallbackSpec` in the retry manager's `_handle_success`/`_handle_failure`.

## Acceptance Criteria
- [ ] Success and failure callbacks execute for configured CallbackSpec inputs.
- [ ] Callback behavior is covered in sync and async execution tests.
- [ ] Error logging remains clear when callback execution itself fails.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #7 (dead callback.py)
- See also: flo-h9yz (retry field cleanup — complementary)



## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `retry.py` `_handle_success` and `_handle_failure` still accept raw callables, no `CallbackSpec` unwrapping.
- `RunConfig.on_success`/`on_failure` store `CallbackSpec` objects but retry manager calls them as `callback(result, None)` — will crash if a CallbackSpec is passed.
- No tests cover CallbackSpec execution in retry paths.

**2026-04-01T21:47:54Z**

Review complete.
Gate: REVISE
Review Attempt: 1/3

Findings:
- [HIGH] Async retry tests not constrained to asyncio — file: tests/pipeline/test_retry_manager.py:8 — pytestmark = pytest.mark.anyio(backend='asyncio') does not prevent trio parametrization. Pin backend explicitly with anyio_backend fixture or switch to pytest.mark.asyncio.

Status:
- ticket remains in_progress

**2026-04-02T10:05:26Z**

Implementation complete.
Gate: PASS

Summary:
- RetryManager._handle_success/_handle_failure now unwrap CallbackSpec objects before calling
- Added _is_callback_spec() helper using callable() check
- Added anyio_backend fixture to pin async tests to asyncio
- Added 5 new tests covering sync/async CallbackSpec success/failure callbacks

Validation:
- pytest tests/pipeline/test_retry_manager.py -v: PASS (7/7)

Review:
- acceptance criteria satisfied
- prior review findings resolved
