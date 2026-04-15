---
id: flo-e4tw
status: in_progress
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

**2026-04-13T16:20:43Z**

Gate: REVISE — Review Attempt: 1/3. Two HIGH findings: (1) Dotted pipeline names don't round-trip through PipelineConfig.load() — save writes group/my-pipeline.yml but load probes group.my-pipeline.yml. (2) Env-overlay behavior still diverges across Config.load(), PipelineConfigManager, and standalone registry — overlays must be centralized into one shared helper.

**2026-04-13T18:49:01Z**

Gate: REVISE — Review Attempt: 2/3. Two HIGH findings: (1) Config.load() no longer applies env overlays — diverges from manager-backed path. Must call shared get_env_overlays() helper or route all entrypoints through one overlay path. (2) Config.save() crashes with AttributeError when pipeline.name is None — needs explicit guard before _format_pipeline_path() call.

**2026-04-13T19:15:17Z**

Gate: ESCALATE — Review Attempt: 3/3. Escalated after three failed review attempts. Persistent issue: Config.save() dereferences self.pipeline.pop('h_params') before the pipeline.name None guard, causing AttributeError on unnamed pipelines with non-empty h_params. The null-name check must be moved before any pipeline attribute access. Requires human judgment on whether to refactor Config.save() more broadly or accept a narrower fix scope.

**2026-04-13T21:23:05Z**

Gate: UNESCALATE — Ticket re-entered the ticket-flow pipeline. Previous escalation overridden. Review attempt counter preserved.

**2026-04-13T21:42:10Z**

Gate: REVISE — Review Attempt: 3/7. HIGH: Standalone PipelineRegistry.from_filesystem() still bypasses apply_env_overlays(), so env-driven config values diverge from Config.load() and manager-backed path. Remediation: route standalone registry through PipelineConfigManager or apply the shared overlay helper in the no-manager registry path.

**2026-04-13T21:51:25Z**

Gate: REVISE — Review Attempt: 4/7. HIGH: PipelineRegistry.__init__() still allows config_manager=None, and load_config() falls back to PipelineConfig.load() without apply_env_overlays(). Direct PipelineRegistry(project_cfg=..., fs=...) instances still diverge from canonical config loading. Remediation: remove the no-manager fallback or instantiate a PipelineConfigManager inside PipelineRegistry when one is not supplied.

**2026-04-14T07:23:00Z**

Gate: REVISE — Review Attempt: 5/7. HIGH: load_config() seeds partial cache entries (pipeline=None, module=None) and get_pipeline() treats any cache hit as complete, so prior summary/config lookups make later get_pipeline(..., reload=False) return None. reload=True also leaves existing entries stale. Remediation: stop caching partial entries from load_config(), or make get_pipeline() require a complete cached pipeline. Overwrite cache entries on reload.

**2026-04-14T08:09:24Z**

Gate: ESCALATE — Implementation blocked. Delegated worker aborted with 429 rate limit error before producing changes. No code modifications were made in this attempt. Ticket needs to be un-escalated and re-run once API availability is stable.

**2026-04-14T08:11:51Z**

Gate: UNESCALATE — Ticket re-entered the ticket-flow pipeline. Previous escalation overridden. Review attempt counter preserved.

**2026-04-14T08:25:38Z**

Gate: ESCALATE — implementation blocked by 429 rate limit error. Worker was aborted before any code changes were made. No validation or review artifacts exist for run 20260414T081522Z.

**2026-04-14T08:39:20Z**

Gate: UNESCALATE — Ticket re-entered the ticket-flow pipeline. Previous escalation overridden. Review attempt counter preserved.

**2026-04-14T08:44:00Z**

Gate: ESCALATE — implementation blocked by 429 rate limit error. Worker aborted before any code changes were made. No validation or review artifacts exist for run 20260414T083959Z.
