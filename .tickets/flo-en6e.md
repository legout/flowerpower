---
id: flo-en6e
status: open
deps: [flo-m81z, flo-p15d, flo-dv90, flo-5wma, flo-1lti, flo-a7kx, flo-b3nm, flo-c9pq, flo-d2rs, flo-e4tw, flo-f6uv, flo-g8wx, flo-h9yz, flo-j1kp, flo-k3lm, flo-l5no, flo-m7pr]
links: [flo-5wma]
created: 2026-02-17T10:44:55Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:tests, component:cli, component:pipeline]
---
# Add regression tests for critical WS1 runtime failures

## Task
Add focused regression tests for the known runtime failures identified in WS1 and the deep analysis.

## Context
The project had failures in run/summary/export paths and callback/settings edge cases; these need explicit guard tests. The deep analysis (2026-03-26) added several more findings that need regression coverage.

## Scope
Tests should cover the following scenarios (grouped by source ticket):

**Original WS1 failures:**
- Run path project detection (flo-m81z)
- Show-summary for all/single pipeline (flo-p15d)
- Export-many validation (flo-dv90)
- Callback execution with CallbackSpec (flo-5wma)
- Settings parsing edge cases (flo-1lti)

**Deep analysis additions:**
- Pipeline delete with hyphenated/dotted names (flo-a7kx)
- Config loading from all entry points produces identical results (flo-e4tw)
- Env overlay errors are logged, not swallowed (flo-l5no)
- CLI Ctrl+C produces clean exit (flo-m7pr)

## Acceptance Criteria
- [ ] Tests cover all scenarios listed above.
- [ ] New tests fail before fixes and pass after fixes.
- [ ] Test assertions avoid broad exception swallowing.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md



## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The tests were **not properly implemented**:

- 43 tests currently FAIL (out of 186).
- Tests reference code that doesn't exist: `_safe_cpu_count` (ImportError).
- Tests for deferred tickets (flo-d2rs, flo-e4tw, flo-j1kp) cannot work since underlying fixes weren't done.
- Most regression tests depend on their parent tickets being fixed first.
