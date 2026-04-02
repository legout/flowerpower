---
id: flo-p15d
status: open
deps: [flo-b3nm]
links: [flo-dv90, flo-b3nm]
created: 2026-02-17T10:44:55Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:pipeline, component:api]
---
# Repair lifecycle and registry API mismatch for summary flows

## Task
Align lifecycle manager summary calls with actual registry API (or remove broken indirection).

## Context
`show-summary` currently fails because lifecycle manager calls non-existent registry methods (`get_summaries()`, `get_pipeline_object()`).

## Recommended Resolution
Ticket flo-b3nm proposes deleting `PipelineLifecycleManager` entirely (it's a pure pass-through). If that approach is taken, this ticket is resolved-by flo-b3nm since the broken indirection is removed at the root.

If lifecycle manager is kept instead, the specific fixes are:
- `get_summary(name=None)` → call `self._registry.get_summary(...)` (method exists, just wrong name)
- `get_summary(name="x")` → load pipeline via existing registry methods instead of non-existent `get_pipeline_object()`

## Acceptance Criteria
- [ ] `pipeline show-summary` works for both all pipelines and single pipeline mode.
- [ ] No calls remain to missing registry methods.
- [ ] Tests cover summary path behavior.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Findings #2, #18
- See also: flo-b3nm (lifecycle manager removal — alternative resolution)



## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The note claiming "Resolved by flo-b3nm" was premature — flo-b3nm was **never implemented**:

- `PipelineLifecycleManager` still exists and is used.
- It still calls non-existent registry methods: `get_summaries()` (line 87, should be `get_summary()`) and `get_pipeline_object()` (line 90, doesn't exist).
- `show-summary` will still fail at runtime.
