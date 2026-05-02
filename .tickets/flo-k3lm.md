---
id: flo-k3lm
status: closed
deps: []
links: [flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:config, perf]
---
# Bound caches and remove redundant _fs_cache

## Task
Fix unbounded caches that can grow without limit, and remove the redundant class-level filesystem cache.

## Context
Two caches grow unboundedly:

**`BaseConfig._fs_cache`** (class-level dict) — Never cleared, no size limit. Redundant with the `@lru_cache(maxsize=32)` on `_get_cached_filesystem()` which already provides bounded caching. The class dict is written to but the lru_cache is what's actually read from.

**`ExecutorFactory._executor_cache`** (instance-level dict) — Cache key is `f"{executor_type}_{hash(str(executor_cfg.to_dict()))}"`. Every unique config creates a new cached executor that's never evicted. With many different pipeline configs over a long-running process, this leaks memory.

## Acceptance Criteria
- [ ] `BaseConfig._fs_cache` class variable removed entirely (lru_cache handles it).
- [ ] `ExecutorFactory._executor_cache` replaced with `@functools.lru_cache(maxsize=16)` or equivalent bounded cache.
- [ ] `ExecutorFactory.clear_cache()` still works (for testing).
- [ ] Tests verify caching behavior with bounded size.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Findings #11, #12

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `BaseConfig._fs_cache` class-level dict still exists (line 42) — never cleared, no size limit, redundant with lru_cache.
- `ExecutorFactory._executor_cache` instance-level dict still exists (line 25) — unbounded, never evicted.

**2026-05-02T13:31:14Z**

Gate: PASS — Replaced unbounded caches with @lru_cache. BaseConfig._filesystem_cache OrderedDict removed; module-level _cached_filesystem with @lru_cache(maxsize=32) added. ExecutorFactory._executor_cache dict removed; _create_cached_executor with @lru_cache(maxsize=16) added, clear_cache() method added. ExecutorConfig.__hash__ added for cache key support. All 109 relevant tests pass; 1 pre-existing CLI integration failure (flo-g8wx load_module move, unrelated). Validation passed; acceptance criteria met. Review not run.
