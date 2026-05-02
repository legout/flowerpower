---
id: flo-2n9o
status: closed
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



**2026-04-28T23:25:16Z**

Child task flo-teil closed: removed utils/callback.py (dead module, 186 lines) and ExecutorFactory.clear_cache (unused method). 346 tests pass. Remaining open children: flo-kv7v (visualization helpers), flo-f891 (RunConfigBuilder drift).

**2026-05-02T00:00:00Z**

All 6 child tasks closed (flo-8qw5, flo-apob, flo-f891, flo-kv7v, flo-teil, flo-vinw). Epic closed.
