---
id: flo-h9yz
status: open
deps: [flo-t1hq]
links: [flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:config, component:refactor, kiss]
---
# Remove deprecated flat retry fields from RunConfig

## Task
Remove the deprecated top-level retry fields (`max_retries`, `retry_delay`, `jitter_factor`, `retry_exceptions`) from `RunConfig` and keep only the nested `retry: RetryConfig`.

## Context
`RunConfig` currently maintains BOTH:
- New nested: `retry: RetryConfig | None`
- Old flat: `max_retries`, `retry_delay`, `jitter_factor`, `retry_exceptions`

Synchronization between them happens in 4 places:
1. `RunConfig.__post_init__()` — creates nested from flat, syncs back
2. `merge_run_config_with_kwargs()` — maps flat kwargs to nested
3. `migrate_legacy_retry_fields()` — handles YAML migration
4. `RetryConfig.to_dict()` — fragile string parsing to clean up class reprs

This is ~100 lines of compatibility code for a feature that should have been a simple deprecation.

## Acceptance Criteria
- [ ] `max_retries`, `retry_delay`, `jitter_factor`, `retry_exceptions` fields removed from `RunConfig`.
- [ ] `RunConfig.__post_init__()` simplified — only handles `RetryConfig` creation if `retry` is None (with sensible defaults).
- [ ] `merge_run_config_with_kwargs()` only handles `retry` dict/RetryConfig, not flat fields.
- [ ] `migrate_legacy_retry_fields()` remains for YAML backward compatibility (reads old format, writes new).
- [ ] `RetryConfig.to_dict()` cleaned up — no fragile string parsing of `<class '...'>`.
- [ ] Deprecation warnings removed (no longer needed).
- [ ] `RunConfigBuilder` (after flo-t1hq consolidation) only exposes `with_retries()`.
- [ ] All tests updated.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Depends on: flo-t1hq (RunConfigBuilder consolidation first)
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #10, #20

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `RunConfig` (run.py) still has `max_retries`, `retry_delay`, `jitter_factor`, `retry_exceptions` as top-level fields (lines 112-116).
- `RetryConfig` conversion logic in `__post_init__` still exists.
- Deprecation warnings were NOT added.
- All 4 synchronization points (post_init, merge, migration, to_dict) still present.
