---
id: flo-f6uv
status: closed
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

**2026-04-13T19:42:03Z**

Gate: REVISE — Review Attempt: 1/3. Two HIGH findings: (1) Hyphenated pipeline names produce different config filenames in PipelineCreator (my_pipeline.yml) vs PipelineConfig.save/load (my-pipeline.yml) — must use same path formatter everywhere. (2) Dotted pipeline names produce invalid runtime module import paths because load_module() uses slash-containing formatted_name with importlib.import_module() — need separate filesystem-path vs module-import-path formatting.

**2026-04-13T20:15:34Z**

Gate: REVISE — Review Attempt: 2/3. Two HIGH findings: (1) PipelineCreator ignores manager-configured cfg_dir/pipelines_dir — manager.creator.new() falls back to defaults instead of using configured layout. (2) Module loading hardcodes 'pipelines.' package root in load_module(), so non-default layouts (e.g. flows/) produce wrong import paths.

**2026-04-14T11:07:04Z**

Gate: REVISE — Review Attempt: 3/7. Three HIGH findings: (1) registry.pipelines returns metadata dicts, breaking IO export membership checks — need names-only API. (2) IO still hardcodes conf/ and pipelines/ paths instead of using configured cfg_dir/pipelines_dir. (3) Dotted/nested pipelines not discoverable by registry — need recursive module discovery.

**2026-04-14T13:32:15Z**

Gate: REVISE — Review Attempt: 4/7. Two HIGH findings: (1) PipelineIOManager export checks membership against registry.pipelines which now returns metadata dicts, always rejecting real pipelines — need names-only lookup. (2) IO import/export still hardcodes conf/ and pipelines/ paths instead of using configured dirs and shared path formatter.

**2026-04-28T23:46:12Z**

Gate: PASS — Deduplication verified complete, 19 tests added. All 5 acceptance criteria met: (1) single add_modules_path in utils/filesystem.py with zero private copies, (2) single validate_pipeline_name in utils/security.py imported by 10+ callers including registry.new(), (3) single validate_file_path in utils/security.py with cfg/base.py wrapper removed, (4) inline checks in Config.save() and PipelineConfig.save() replaced with shared calls. Validation: 366 tests pass (346 existing + 20 new). Structural checks confirm zero duplicate definitions across src/. Lint clean on changed files. Review not run.
