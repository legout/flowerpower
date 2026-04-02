---
id: flo-e0im
status: open
deps: [flo-en6e]
links: [flo-t1hq, flo-m7pr]
created: 2026-02-17T10:44:55Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:ci, component:tests]
---
# Add CI quality gate before publish and clean brittle tests

## Task
Add CI checks (lint + tests) before publish and remove exception-swallowing patterns in critical tests.

## Context
Current release flow can publish without full quality gating; some tests mask failures by catching broad exceptions.

## Acceptance Criteria
- [ ] A CI workflow runs lint and test gates before publishing actions.
- [ ] Critical tests assert failures explicitly instead of swallowing exceptions.
- [ ] Publish path is blocked when quality checks fail.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- See also: flo-m7pr (CLI exception handling — related pattern)



## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `.github/workflows/publish.yml` still has NO lint or test gate — it builds and publishes directly.
- No separate CI workflow exists for quality checks.
- 43 tests currently fail, which would block publish if a gate existed.
