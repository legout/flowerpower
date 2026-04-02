---
id: flo-a7kx
status: closed
deps: []
links: [flo-t1hq, flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 1
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:pipeline, bug:high, component:registry]
---
# Fix pipeline delete() name formatting — cannot delete pipelines with hyphens

## Task
Apply the same name formatting in `PipelineRegistry.delete()` that `new()` uses, so pipelines created with hyphens or dots can actually be deleted.

## Context
`PipelineRegistry.new()` transforms the name: `formatted_name = name.replace(".", "/").replace("-", "_")` before creating files. But `delete()` uses the raw name directly. This means `new("my-pipeline")` creates `my_pipeline.py` / `my_pipeline.yml`, but `delete("my-pipeline")` looks for `my-pipeline.yml` — silently skipping deletion because the file is "not found" (only a warning is logged).

This is a data-loss prevention issue in the opposite direction: users cannot clean up pipelines they created.

## Acceptance Criteria
- [ ] `delete("my-pipeline")` correctly finds and removes `my_pipeline.yml` and `my_pipeline.py`.
- [ ] `delete()` uses the same name formatting logic as `new()`.
- [ ] Regression test: create → delete round-trip with hyphenated/dotted names.
- [ ] Consider extracting the formatting into a shared helper so new/delete/search all stay in sync.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #16

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `PipelineRegistry.delete()` at line 393 still uses raw `name` without `formatted_name = name.replace(".", "/").replace("-", "_")`.
- `new()` applies the transformation (line 297-298) but `delete()` does not.
- Creating `my-pipeline` and then `delete("my-pipeline")` will fail to find the files.
- Regression test for this scenario does not exist or doesn't actually test the formatting.

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `PipelineRegistry.delete()` at line 393 still uses raw `name` without `formatted_name = name.replace(".", "/").replace("-", "_")`.
- `new()` applies the transformation (line 297-298) but `delete()` does not.
- Creating `my-pipeline` and then `delete("my-pipeline")` will fail to find the files.

**2026-04-01T12:14:09Z**

Review #1: Gate: PASS. Fixed pipeline delete() name formatting by extracting _format_pipeline_name() helper used by new(), delete(), and load_module(). Added 3 regression tests for hyphenated, dotted, and mixed special character names.
