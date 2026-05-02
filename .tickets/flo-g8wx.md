---
id: flo-g8wx
status: closed
deps: []
links: [flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:pipeline, dead-code]
---
# Remove dead code: callback.py, BasePipeline, commented-out blocks, dead functions

## Task
Delete production-unused code that adds maintenance burden without providing value.

## Context
Four sources of dead code identified:

**`utils/callback.py` (164 lines)** — A full callback framework (`_prepare_callback_details`, `_parse_tuple_callback_args`, `run_with_callback` decorator). Never imported by any production code path. The retry system uses its own simpler `_handle_success`/`_handle_failure` via `CallbackSpec`.

**`pipeline/base.py` `BasePipeline` class (120 lines)** — Has `_setup_paths`, `_setup_directories`, `_add_modules_path`, `_load_project_cfg`, `_load_pipeline_cfg`. Never instantiated. The actual pipeline is `Pipeline` (a msgspec.Struct). Only `load_module()` (10 lines) is used — by registry and visualizer.

**Commented-out joblib code in `utils/misc.py` (~115 lines)** — A full `run_parallel()` implementation using joblib, entirely commented out with `#`.

**Dead module-level functions in `cfg/__init__.py` (~85 lines)** — `_load_config()`, `_save_pipeline_config()`, `_save_project_config()` defined at module scope. Never called by any code.

## Acceptance Criteria
- [ ] `utils/callback.py` deleted.
- [ ] `pipeline/base.py` `BasePipeline` class deleted; `load_module()` moved to `utils/misc.py`.
- [ ] Commented-out joblib block deleted from `utils/misc.py`.
- [ ] Dead functions deleted from `cfg/__init__.py`.
- [ ] Imports to `callback.py` and `BasePipeline` removed from all files.
- [ ] Tests that tested deleted code are removed.
- [ ] No import errors remain.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Findings #7, #8, #9, #26

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `utils/callback.py` still exists (186 lines) — never imported by production code.
- `pipeline/base.py` `BasePipeline` class still exists — never instantiated.
- Dead module-level functions in `cfg/__init__.py` still exist: `_load_config()`, `_save_pipeline_config()`, `_save_project_config()`.
- `cfg/pipeline/__init__.py` still has `_load_pipeline_config()` and `_save_pipeline_config()`.

**2026-05-02T10:48:49Z**

Gate: PASS — Completed remaining dead-code removal. Most items (callback.py, BasePipeline, joblib block, cfg dead functions) were already cleaned in prior work. This run moved load_module() from pipeline/base.py to utils/misc.py, updated imports in registry.py and visualizer.py, and deleted pipeline/base.py. All 8 ACs verified: dead files absent, load_module in new location, no stale imports, full suite green (369/369). Validation passed; acceptance criteria met. Review not run.
