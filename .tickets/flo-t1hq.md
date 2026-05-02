---
id: flo-t1hq
status: closed
deps: []
links: [flo-e0im, flo-h9yz, flo-g8wx, flo-f891]
created: 2026-02-17T10:44:55Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:config, component:refactor]
---
# Consolidate duplicate RunConfigBuilder implementations

## Task
Consolidate duplicate RunConfigBuilder implementations into one authoritative implementation.

## Context
Two completely different `RunConfigBuilder` classes exist:
1. `cfg/pipeline/builder.py` (389 lines) — loads defaults from YAML, uses sub-builders (`ExecutorBuilder`, `AdapterBuilder`)
2. `utils/config.py` (lines 200-430) — simpler, used by `merge_run_config_with_kwargs()`

They have different APIs, different feature sets, and different import paths. This creates drift and confusion.

Additionally, `builder_executor.py` (107 lines) and `builder_adapter.py` (141 lines) are only used by the `builder.py` version. If that builder is removed, they become dead code (see flo-g8wx).

## Recommended Resolution
Keep the simpler builder in `utils/config.py` (already used by merge logic). If YAML-defaults-loading is needed, add a `.from_pipeline()` classmethod to it. Delete `cfg/pipeline/builder.py`, `builder_executor.py`, and `builder_adapter.py`.

## Acceptance Criteria
- [ ] One source-of-truth `RunConfigBuilder` remains for runtime and tests.
- [ ] Deprecated/duplicate builder path is removed.
- [ ] `builder_executor.py` and `builder_adapter.py` are deleted (or inlined if kept).
- [ ] Relevant docs/imports are updated to match the canonical builder path.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #1, #27
- See also: flo-h9yz (retry field cleanup — do after builder consolidation), flo-g8wx (dead code removal)



## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The consolidation was **never done**:

- Two `RunConfigBuilder` classes still exist:
  - `cfg/pipeline/builder.py` (389 lines) — rich builder with YAML defaults, sub-builders
  - `utils/config.py` (527 lines) — simpler builder used by merge logic
- `builder_executor.py` (107 lines) and `builder_adapter.py` (141 lines) still exist.
- Different APIs, different feature sets, different import paths — drift unresolved.

**2026-05-02T21:46:11Z**

Gate: PASS — Consolidated duplicate RunConfigBuilder by deleting deprecated builder and its exclusive sub-builders. Deleted: cfg/pipeline/builder.py (388 lines), builder_executor.py (108 lines), builder_adapter.py (147 lines). Updated tests/cfg/test_config_paths.py (removed import and 2 legacy test functions). Canonical RunConfigBuilder in utils/config.py remains the single source of truth. Validation: 374 passed, 2 pre-existing failures (CLI integration tests, confirmed on clean code via git stash). Zero dangling references across src/ and tests/. Lint clean on changed files. Review not run.
