---
id: flo-d2rs
status: open
deps: [flo-c9pq]
links: [flo-c9pq, flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:pipeline, component:refactor, kiss]
---
# Split PipelineRegistry — separate concerns from 875-line god class

## Task
Split `PipelineRegistry` into focused classes: registry (discovery/caching), creator (CRUD), and presenter (Rich rendering).

## Context
`PipelineRegistry` currently handles 7 distinct responsibilities in 875 lines:
1. Pipeline discovery and file listing (`_get_files`, `_get_names`, `_all_pipelines`)
2. Pipeline caching (`_pipeline_data_cache`, `CachedPipelineData`)
3. Pipeline creation/deletion (`new`, `delete`, `create_pipeline`, `delete_pipeline`)
4. Rich rendering (`show_pipelines`, `show_summary`, `_all_pipelines` with tables/panels/syntax)
5. Hook management (`add_hook`)
6. Module loading (`load_module`)
7. Module path manipulation (`_add_modules_path`)

The Rich rendering code (tables, panels, syntax highlighting, SVG/HTML export) is completely unrelated to registry concerns and makes the class hard to test.

## Acceptance Criteria
- [ ] `PipelineRegistry` retains only: discovery, listing, caching, module loading.
- [ ] Pipeline creation/deletion moves to `PipelineRegistry` (stays — it's core) or a small `PipelineCreator` helper.
- [ ] Rich rendering moves to `PipelinePresenter` (new class, ~150 lines).
- [ ] Hook management stays in registry (it's small and tied to pipeline files).
- [ ] `_add_modules_path()` is extracted to `utils/filesystem.py` (shared utility).
- [ ] All tests pass; new presenter tests cover rendering separately.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Depends on: flo-c9pq (slimming PipelineManager first simplifies the registry split)
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #4

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `PipelineRegistry` is still 876 lines with all 7 responsibilities.
- Rich rendering code (show_summary, show_pipelines with Table/Panel/Syntax/Tree) is still in registry (~200 lines, lines 551-838).
- `PipelinePresenter` class exists (184 lines) but is **never imported or used** anywhere — it's dead code.
- `_add_modules_path` still in registry (not extracted to utils/filesystem.py).
