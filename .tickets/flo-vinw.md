---
id: flo-vinw
status: closed
deps: []
links: [flo-f891]
created: 2026-04-29T09:08:49Z
type: bug
priority: 1
assignee: legout
parent: flo-2n9o
tags: [cleanup, config, docs, api, followup]
---
# Fix remaining RunConfigBuilder docs drift after flo-f891

Follow-up from /ef-review of flo-f891. The implementation standardized import paths, but the canonical docs still mix constructor patterns and document legacy-only method names against the canonical flowerpower.utils.config.RunConfigBuilder. This leaves flo-f891 acceptance criteria incomplete.

## Acceptance Criteria

README.md and docs/docs/quickstart.md use one canonical constructor pattern for flowerpower.utils.config.RunConfigBuilder, without pipeline_name= unless it is intentionally documented as a no-op compatibility argument.\ndocs/docs/api/runconfig.md documents only methods that actually exist on flowerpower.utils.config.RunConfigBuilder, or the canonical builder grows tested compatibility aliases for the documented names.\nA validation command verifies no docs examples use legacy-only builder method names or the non-canonical builder import path.\nRunConfigBuilder examples for FlowerPowerProject.run and PipelineManager.run remain consistent with the canonical API.


## Notes

**2026-05-02T10:31:21Z**

Gate: PASS — Removed pipeline_name= from RunConfigBuilder() constructor calls in README.md and quickstart.md. Renamed 6 phantom method names in docs/docs/api/runconfig.md to match the actual canonical API (with_executor, with_with_adapter_cfg, with_pipeline_adapter_cfg, with_project_adapter_cfg, with_on_success, with_on_failure). Fixed with_cache type from dict[str, Any] to bool | None. Added tests/test_docs_consistency.py with 3 grep-based guards. Full suite green (369/369). Validation passed; acceptance criteria met. Review not run.
