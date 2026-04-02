---
id: flo-2n9o
status: in_progress
deps: []
links: []
created: 2026-03-27T15:55:53Z
type: epic
priority: 2
assignee: legout
tags: [cleanup, utils, refactor]
---
# Slim utils module and remove non-core helper surface

Follow-up cleanup after the recent architecture scouting. The goal is to make FlowerPower easier to maintain by trimming dead helpers, shrinking the public utils surface, and moving optional UX helpers closer to the features that use them.

This epic intentionally excludes broad architectural rewrites and focuses on small, reviewable cleanup tasks.

## Acceptance Criteria

- [ ] Runtime-irrelevant helper code is either deleted, moved, or explicitly justified.
- [ ] utils/ contains fewer public-facing convenience exports and less non-core logic.
- [ ] Docs and tests reflect the retained APIs.
- [ ] Each child task is small enough to review independently.


## Notes

**2026-03-27T18:23:46Z**


