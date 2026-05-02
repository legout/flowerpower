---
id: flo-m81z
status: closed
deps: []
links: [flo-en6e]
created: 2026-02-17T10:44:55Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:core, component:filesystem]
---
# Fix project existence detection for cached dir filesystems

## Task
Fix project existence checks so valid projects are detected when using cached and dir-like filesystem wrappers.

## Context
`FlowerPowerProject._check_project_exists()` uses strict `isinstance(fs, DirFileSystem)` checks to determine the root path. When the filesystem is wrapped in a cached layer (e.g., `CachingFileSystem`), the isinstance check fails and the wrong root path is used for existence checks.

This breaks `pipeline run --base-dir examples/hello-world` because the cached filesystem reports "project does not exist" even though the project directory is valid.

The return type of `load()` is also wrong — it returns `None` when the project doesn't exist but is annotated as `FlowerPowerProject` (non-Optional). This means callers that don't check for `None` will get confusing type errors.

## Acceptance Criteria
- [ ] Loading an existing project works with cached and dir-like filesystem variants.
- [ ] CLI `pipeline run --base-dir examples/hello-world ...` no longer reports false missing project.
- [ ] `FlowerPowerProject.load()` either raises `FileNotFoundError` or returns `Optional[FlowerPowerProject]` consistently.
- [ ] Add/adjust tests covering this detection path.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #15 (return type mismatch)



## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `_check_project_exists()` still uses `isinstance(fs, DirFileSystem)` check (line 185) without handling CachingFileSystem or other wrappers.
- No `hasattr` or duck-typing fallback for wrapped filesystems.
- CLI `pipeline run --base-dir examples/hello-world` will still fail with cached filesystem variants.

**2026-05-02T21:28:24Z**

Gate: PASS — Fixed _check_project_exists() to detect DirFileSystem through cached/wrapped layers via recursive _is_dir_fs() helper. Fixed load() return type to Optional["FlowerPowerProject"]. Added 2 unit tests with real fsspec instances. Validation passed: 15/15 tests. Review not run.
