---
id: flo-l5no
status: closed
deps: []
links: [flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:pipeline, bug:medium]
---
# Fix env overlay silent error swallowing and mutable default arguments

## Task
Replace bare `except Exception: pass` blocks with logging, and fix mutable default arguments in IO method signatures.

## Context
Two code hygiene issues:

**Silent error swallowing** — `PipelineConfigManager.load_project_config()` and `load_pipeline_config()` both have:
```python
try:
    overrides = parse_env_overrides()
    ...
except Exception:
    pass  # ← completely invisible
```
If env overlay parsing has a bug, it's impossible to diagnose. At minimum, the error should be logged at DEBUG level.

**Mutable default arguments** — `PipelineIOManager` methods use `{}` as default:
```python
def import_pipeline(self, ..., src_storage_options: dict | None = {}):
```
Classic Python anti-pattern. While not currently mutated, it's a latent bug.

## Acceptance Criteria
- [x] `except Exception: pass` in config manager replaced with `except Exception as e: logger.debug(...)`.
- [x] All `src_storage_options={}` and `dest_storage_options={}` defaults in `PipelineIOManager` changed to `None` with `storage_options = storage_options or {}` inside the function body.
- [x] Same pattern applied in `PipelineManager` delegation methods if they survive flo-c9pq.
- [x] Tests verify env overlay errors are logged (not silently swallowed).

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Findings #17, #22

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `PipelineConfigManager.load_project_config()` (line 83) still has `except Exception: pass`.
- `PipelineConfigManager.load_pipeline_config()` (line 151) still has `except Exception: pass`.
- `PipelineIOManager` methods still have mutable defaults: `src_storage_options: dict | ... | None = {}` (lines 98, 99, 180, 224, 269, 311) and `dest_storage_options: dict | ... | None = {}` (lines 311, 358, 408).

**2026-05-02T15:33:00Z**

AUDIT: Status changed from open → **closed**. The fixes were **already implemented** in a prior refactor (between 2026-04-01 and 2026-05-02). Verification performed:

- `src/flowerpower/utils/env.py` `apply_env_overlays()` (line ~230) catches `Exception` and logs via `logger.debug(f"Env overlay application failed: {e}")` — no `pass`.
- `src/flowerpower/pipeline/config_manager.py` lines 99 and 137 delegate directly to `apply_env_overlays` — no bare `except Exception: pass` anywhere in the file.
- `src/flowerpower/pipeline/io.py` all `storage_options` parameters default to `None` (verified at lines 249, 250, 306, 357, 409, 449, 503, 553); `or {}` used inside method bodies (e.g., lines 271, 277, 336, 389).
- `src/flowerpower/pipeline/manager.py` has no `import_*`/`export_*` delegation methods — AC3 vacuously satisfied.
- `tests/pipeline/test_env_overlay_logging.py` (2 tests) verifies debug logging for both `load_project_config` and `load_pipeline_config` paths.
- `grep -rn 'except.*Exception.*pass' src/ --include='*.py'` returns zero matches.

No code changes required.

**2026-05-02T20:24:27Z**

Gate: PASS — All acceptance criteria already satisfied by current codebase. apply_env_overlays() logs at DEBUG (utils/env.py:230), all IO storage_options use =None, PipelineManager has no delegation methods. Validation: 2 targeted tests passed, 57 broader tests passed, static grep confirms zero bare except/pass in scope. Review not run. No code changes needed.
