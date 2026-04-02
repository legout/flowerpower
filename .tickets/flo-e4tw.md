---
id: flo-e4tw
status: open
deps: []
links: [flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:config, component:duplication]
---
# Consolidate config loading — 4 duplicate paths → 1 canonical path

## Task
Eliminate duplicate pipeline config loading logic so there is exactly one code path from YAML file to `PipelineConfig` instance.

## Context
Pipeline configuration loading currently happens in 4 places, each with subtle differences:
1. `PipelineConfig.load()` in `cfg/pipeline/__init__.py` — canonical, handles YAML + env interpolation + legacy migration
2. `PipelineConfigManager.load_pipeline_config()` in `pipeline/config_manager.py` — searches multiple paths, applies env overlays
3. `PipelineRegistry.load_config()` in `pipeline/registry.py` — caching wrapper around `PipelineConfig.load()`
4. `PipelineConfig._load_pipeline_config()` in `cfg/pipeline/__init__.py` — private duplicate of `load()`

Additionally, env overlays are applied inconsistently:
- `PipelineConfigManager` applies them (both project and pipeline overlays)
- `Config.load()` in `cfg/__init__.py` applies them
- `PipelineConfig.load()` does NOT apply them
- `PipelineRegistry.load_config()` does NOT apply them

## Acceptance Criteria
- [ ] `PipelineConfig.load()` is the single canonical loader (YAML parse + env interpolation + legacy migration).
- [ ] `PipelineConfigManager.load_pipeline_config()` calls `PipelineConfig.load()` then applies env overlays (only place overlays are applied).
- [ ] `PipelineRegistry.load_config()` delegates to config manager or uses its cache.
- [ ] Dead private method `PipelineConfig._load_pipeline_config()` is removed.
- [ ] Dead `ProjectConfig._load_project_config()` / `_save_project_config()` private methods are removed (same pattern).
- [ ] Env overlay application happens in exactly one place with clear documentation.
- [ ] Tests verify config loading produces identical results regardless of entry point.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #5

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- 4 config loading paths still exist: `PipelineConfig._load_pipeline_config()`, `PipelineConfigManager.load_pipeline_config()`, `PipelineRegistry.load_config()`, `PipelineConfig.load()`.
- Dead private methods still present: `_load_config()` in `cfg/__init__.py` (line 375), `_save_pipeline_config()` (line 403), `_save_project_config()` (line 412).
- `_load_pipeline_config()` and `_save_pipeline_config()` in `cfg/pipeline/__init__.py` (lines 268, 291).
- `_load_project_config()` and `_save_project_config()` in `cfg/project/__init__.py` (lines 67, 85).
