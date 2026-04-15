---
id: flo-b3nm
status: closed
deps: []
links: [flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:pipeline, component:refactor]
---
# Remove PipelineLifecycleManager — pure pass-through with broken methods

## Task
Delete `PipelineLifecycleManager` and have `PipelineManager` call `self.registry.*` directly.

## Context
Every method in `PipelineLifecycleManager` (230 lines) is a direct 1-line delegation to `self._registry.*`. Worse, two of its methods call **non-existent** registry methods:
- `get_summary(name=None)` calls `self._registry.get_summaries()` — should be `get_summary()`
- `get_summary(name="x")` calls `self._registry.get_pipeline_object(name)` — doesn't exist at all

This is the root cause of ticket flo-p15d. Deleting the lifecycle manager eliminates the indirection and the broken calls simultaneously.

Note: flo-p15d suggests "aligning" the API. This ticket proposes the simpler alternative: remove the indirection entirely. If flo-p15d is resolved via this approach, it can be closed.

## Acceptance Criteria
- [ ] `PipelineLifecycleManager` class and file are deleted.
- [ ] `PipelineManager.__init__()` no longer creates a lifecycle manager.
- [ ] `PipelineManager` methods that delegated to lifecycle manager now call `self.registry.*` directly (or are removed if they were pure delegation themselves).
- [ ] `show_summary()` and `show_pipelines()` on `PipelineManager` call registry methods that actually exist.
- [ ] All tests pass; tests for lifecycle manager are removed or redirected.
- [ ] flo-p15d can be closed as resolved-by.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Supersedes: flo-p15d (same root cause, simpler fix)
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Findings #2, #18

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `pipeline/lifecycle_manager.py` still exists (233 lines).
- `PipelineManager.__init__()` still creates `PipelineLifecycleManager` (line 205).
- All methods delegate through lifecycle manager: `new()`, `delete()`, `get_summary()`, `show_summary()`, `list_pipelines()`, `show_pipelines()`, `add_hook()`.
- Lifecycle manager still calls non-existent registry methods: `get_summaries()` (should be `get_summary()`) and `get_pipeline_object()` (doesn't exist at all).

**2026-04-10T15:42:50Z**

Gate: PASS — PipelineLifecycleManager deleted, PipelineManager delegates directly to self.registry.*, 58/58 pipeline tests pass. Review confirmed clean refactor.
