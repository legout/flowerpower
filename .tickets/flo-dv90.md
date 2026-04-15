---
id: flo-dv90
status: closed
deps: []
links: [flo-p15d, flo-b3nm]
created: 2026-02-17T10:44:55Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:pipeline, component:io]
---
# Fix export_many pipeline validation path

## Task
Fix export-many pipeline existence validation by implementing or replacing missing registry checks.

## Context
`PipelineIOManager.export_many()` currently calls `self.registry.has_pipeline(name)` which does not exist on `PipelineRegistry`, causing a runtime crash.

This is the same class of bug as flo-p15d — calling non-existent registry methods. If flo-b3nm (lifecycle manager removal) and flo-c9pq (PipelineManager slimming) are done first, this method may be refactored out entirely.

## Acceptance Criteria
- [ ] `PipelineManager.export_many(...)` no longer raises missing-method errors.
- [ ] Non-existent pipeline names still fail with clear error messages.
- [ ] Tests cover success and failure validation paths.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #18 (same pattern)
- See also: flo-b3nm (broader fix for missing-method pattern), flo-c9pq (IO methods may move)



## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `PipelineIOManager.export_many()` still calls `self.registry.has_pipeline(name)` at line 383.
- `has_pipeline()` does NOT exist on `PipelineRegistry` — will crash at runtime.
- Blocked by flo-b3nm and flo-c9pq which are also not done.

**2026-04-13T15:26:18Z**

Gate: PASS — Review passed on first attempt. Replaced non-existent registry.has_pipeline() call in export_many() with name not in registry.pipelines. Added matching validation to export_pipeline(). Fixed test mocks and added new coverage test. 2/2 ticket-relevant tests pass.
