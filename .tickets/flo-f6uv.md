---
id: flo-f6uv
status: open
deps: []
links: [flo-e4tw, flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:utils, component:duplication, kiss]
---
# Deduplicate _add_modules_path and validation helpers

## Task
Extract duplicated utilities into single canonical implementations.

## Context
Three groups of logic are duplicated across the codebase:

**`_add_modules_path()`** — identical logic in 3 files:
- `PipelineManager._add_modules_path()` (manager.py)
- `PipelineRegistry._add_modules_path()` (registry.py)
- `BasePipeline._add_modules_path()` (base.py)

Each checks `is_cache_fs`, calls `sync_cache()`, and inserts into `sys.path` — with slightly different fallback logic.

**Pipeline name validation** — 5 independent checks:
- `PipelineConfig._validate_pipeline_name()` (cfg/pipeline/__init__.py)
- `Config.save()` inline check (cfg/__init__.py)
- `validate_pipeline_name()` (utils/security.py)
- `FlowerPowerProject._validate_pipeline_name()` (flowerpower.py — calls security.py)
- Registry `new()` does NOT validate at all

**Path traversal validation** — 3 independent checks:
- `validate_file_path()` (utils/security.py — comprehensive)
- `validate_file_path()` (cfg/base.py — thin wrapper)
- Inline `..` checks in PipelineConfig and Config.save()

## Acceptance Criteria
- [ ] Single `add_modules_path(fs, pipelines_dir, base_dir)` function in `utils/filesystem.py`.
- [ ] All three classes call the shared function; local copies deleted.
- [ ] Single `validate_pipeline_name()` in `utils/security.py` called everywhere (including registry `new()`).
- [ ] Single `validate_file_path()` in `utils/security.py` called everywhere; wrapper in `cfg/base.py` removed.
- [ ] Inline validation checks in `Config.save()` and `PipelineConfig.save()` replaced with calls to shared functions.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Depends on: flo-e4tw (config consolidation should happen first to avoid conflicts)
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Findings #6, #14, #23, #24

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `_add_modules_path` still duplicated in 4 files:
  - `PipelineManager` (manager.py line 220)
  - `PipelineRegistry` (registry.py line 157)
  - `BasePipeline` (base.py line 83)
  - `PipelineConfigManager` (config_manager.py line 200)
- No shared function in `utils/filesystem.py`.
- Pipeline name validation still duplicated across 5 locations.
- Path traversal validation still duplicated across 3 locations.
