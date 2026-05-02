---
id: flo-vinw
status: open
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

