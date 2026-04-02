---
id: flo-c9pq
status: open
deps: [flo-b3nm]
links: [flo-b3nm, flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:pipeline, component:refactor, kiss]
---
# Slim PipelineManager — remove pure delegation methods

## Task
Remove delegation methods from `PipelineManager` that are thin 1-line forwards to sub-managers, and reduce the class from ~1109 lines to ~300 lines.

## Context
`PipelineManager` creates 5 sub-managers (registry, executor, lifecycle_manager, visualizer, io_manager, config_manager) but then wraps most of their public APIs with near-identical delegation methods that duplicate docstrings and add no value.

The IO methods alone account for ~300 lines of pure forwarding:
- `import_pipeline`, `import_many`, `import_all`
- `export_pipeline`, `export_many`, `export_all`

The registry methods add another ~150 lines:
- `new`, `delete`, `get_summary`, `show_summary`, `list_pipelines`, `show_pipelines`, `add_hook`

The visualizer methods add ~80 lines:
- `save_dag`, `show_dag`

Users can (and should) call `pm.io.import_pipeline(...)`, `pm.registry.new(...)`, `pm.visualizer.save_dag(...)` directly.

## Acceptance Criteria
- [ ] IO delegation methods removed from `PipelineManager`. Users call `pm.io.*` directly.
- [ ] Registry delegation methods removed (after flo-b3nm merges lifecycle manager). Users call `pm.registry.*` directly.
- [ ] Visualizer delegation methods removed. Users call `pm.visualizer.*` directly.
- [ ] `PipelineManager` retains: `__init__`, `run()`, `run_async()`, `load_pipeline()`, core properties (`project_cfg`, `pipeline_cfg`, `pipelines`), and `__enter__`/`__exit__`.
- [ ] Properties `pipelines`, `summary`, `current_pipeline_name` are preserved (they are lightweight).
- [ ] Public sub-managers are accessible as properties: `registry`, `io`, `visualizer`, `executor`.
- [ ] All existing tests updated to use direct sub-manager calls where needed.
- [ ] README and docs updated with new API patterns.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Depends on: flo-b3nm (lifecycle manager removal should happen first)
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #3

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `PipelineManager` is still 1109 lines with all delegation methods intact.
- IO methods (import_pipeline, import_many, import_all, export_pipeline, export_many, export_all) still delegate (~300 lines).
- Registry methods (new, delete, get_summary, show_summary, list_pipelines, show_pipelines, add_hook) still delegate (~150 lines).
- Visualizer methods (save_dag, show_dag) still delegate (~80 lines).
- Depends on flo-b3nm (lifecycle manager removal) which is also not done.
