---
id: flo-l5no
status: open
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
- [ ] `except Exception: pass` in config manager replaced with `except Exception as e: logger.debug(...)`.
- [ ] All `src_storage_options={}` and `dest_storage_options={}` defaults in `PipelineIOManager` changed to `None` with `storage_options = storage_options or {}` inside the function body.
- [ ] Same pattern applied in `PipelineManager` delegation methods if they survive flo-c9pq.
- [ ] Tests verify env overlay errors are logged (not silently swallowed).

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Findings #17, #22

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `PipelineConfigManager.load_project_config()` (line 83) still has `except Exception: pass`.
- `PipelineConfigManager.load_pipeline_config()` (line 151) still has `except Exception: pass`.
- `PipelineIOManager` methods still have mutable defaults: `src_storage_options: dict | ... | None = {}` (lines 98, 99, 180, 224, 269, 311) and `dest_storage_options: dict | ... | None = {}` (lines 311, 358, 408).
