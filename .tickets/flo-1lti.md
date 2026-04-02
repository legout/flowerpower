---
id: flo-1lti
status: closed
deps: []
links: [flo-en6e]
created: 2026-02-17T10:44:55Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:settings]
---
# Fix settings parsing for booleans and cpu_count fallback

## Task
Correct settings environment parsing for booleans and handle `os.cpu_count()` returning None safely.

## Context
In `settings/executor.py`:
- `EXECUTOR = os.getenv("FP_EXECUTOR", "threadpool")` is fine as a string, but if any setting uses `bool(os.getenv(...))` semantics, `"False"` and `"0"` would parse as `True`.
- `EXECUTOR_MAX_WORKERS = int(os.getenv(...) or (os.cpu_count() or 2) * 5)` — the parenthesization means if `os.cpu_count()` returns `None`, `(None or 2) * 5 = 10`, which is correct. But if someone changes the expression order, it could crash with `TypeError: unsupported operand type(s)`.
- `EXECUTOR_NUM_CPUS = int(os.getenv(...) or os.cpu_count() or 1)` — correct, but fragile.

## Acceptance Criteria
- [ ] Env values like "False"/"0" are parsed as false (if any bool settings exist).
- [ ] Executor defaults do not crash when `os.cpu_count()` is None.
- [ ] Settings parsing uses a helper function that handles None safely.
- [ ] Tests cover parsing and fallback edge cases (including `os.cpu_count() = None` mock).

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md (settings not individually flagged but part of config layer review)



## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `settings/executor.py` still has `os.cpu_count() * 5` which crashes with `TypeError` when `cpu_count()` returns `None`.
- No `_safe_cpu_count()` helper function exists (tests import it and fail).
- No boolean parsing helper for env vars.
- 3 tests in `tests/settings/test_executor.py` FAIL:
  - `test_cpu_count_none_does_not_crash` — TypeError at module load
  - `test_safe_cpu_count_returns_default_on_none` — ImportError
  - `test_safe_cpu_count_returns_actual_count` — ImportError

**2026-04-01T12:16:28Z**

dummy

**2026-04-01T12:22:00Z**

Review #1: Gate: REVISE. Issues to fix:

1. [HIGH] Boolean settings in settings/hamilton.py (HAMILTON_CAPTURE_DATA_STATISTICS, HAMILTON_TELEMETRY_ENABLED) still use bool(os.getenv(...)) so 'False'/'0' parse as True. Route them through _env_bool() or a shared utility.
2. [HIGH] Tests in tests/settings/test_executor.py only cover cpu_count fallback, not boolean env parsing edge cases. Add tests verifying 'False', '0', unset values map to False.

**2026-04-01T21:27:28Z**

Review complete.
Gate: REVISE
Review Attempt: 2/3

Findings:
- [HIGH] EXECUTOR_NUM_CPUS fallback changed from 1 to 2 on os.cpu_count() is None — file: src/flowerpower/settings/executor.py:38 — Use _safe_cpu_count(1) for EXECUTOR_NUM_CPUS to preserve prior fallback semantics.
- [HIGH] New test file fails Ruff (F401 pytest imported but unused) — file: tests/settings/test_executor.py:6 — Remove unused pytest import.

Status:
- ticket remains in_progress

**2026-04-01T21:35:27Z**

Implementation complete.
Gate: PASS

Summary:
- Fixed settings/hamilton.py to use _env_bool() for boolean env vars (HAMILTON_CAPTURE_DATA_STATISTICS, HAMILTON_TELEMETRY_ENABLED)
- Fixed EXECUTOR_NUM_CPUS fallback to use _safe_cpu_count(1) preserving prior semantics
- Added comprehensive boolean env parsing tests (TestEnvBoolParsing)

Validation:
- ty check: N/A (pre-existing unrelated issues)
- mypy src/: PASS
- pytest tests/settings/ -x -v: PASS (10/10)

Review:
- acceptance criteria satisfied
- prior review findings resolved
