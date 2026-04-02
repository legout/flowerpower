---
id: flo-f891
status: open
deps: []
links: [flo-t1hq]
created: 2026-03-27T15:55:53Z
type: task
priority: 2
assignee: legout
parent: flo-2n9o
tags: [cleanup, config, docs, api]
---
# Resolve RunConfigBuilder drift and standardize docs on one builder path

Follow up on the closed builder-consolidation work by picking one canonical user-facing RunConfigBuilder path and making the docs/examples consistent with it. Current docs mix incompatible constructor patterns. If the utils.config builder must remain for compatibility, deprecate it explicitly rather than leaving two quasi-public implementations with conflicting examples.

## Acceptance Criteria

- [ ] README and docs use one canonical RunConfigBuilder import path and constructor pattern.
- [ ] The non-canonical builder path is either removed or clearly deprecated in code and docs.
- [ ] Tests stop depending on the deprecated import path unless the ticket explicitly keeps a compatibility alias.
- [ ] The resulting API story is consistent for FlowerPowerProject.run and PipelineManager.run examples.


## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. Review #2 claimed PASS but the work was **never actually done**:

- No `DeprecationWarning` in `cfg/pipeline/builder.py` — the old builder has no deprecation notice.
- Docs still use the OLD non-canonical import: `from flowerpower.cfg.pipeline.builder import RunConfigBuilder` appears in `flowerpowerproject.md` (line 86), `pipelinemanager.md` (line 107), and `runconfig.md` (10 occurrences).
- The "canonical" builder path `flowerpower.utils.config` is not used in any docs.
