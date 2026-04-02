---
id: flo-8qw5
status: closed
deps: []
links: []
created: 2026-03-27T15:55:53Z
type: task
priority: 3
assignee: legout
parent: flo-2n9o
tags: [cleanup, utils, api-surface]
---
# Trim non-core utils exports and test-only convenience helpers

Reduce package surface in flowerpower.utils to helpers that are actually part of the maintained product. Start with get_partitions_from_path (currently test-only), create_filesystem_helper (currently only re-exported), and the broad exports in utils.__init__.py. The intent is to stop advertising convenience helpers that are not needed to use FlowerPower.

## Acceptance Criteria

- [ ] Test-only or non-essential helpers are removed or moved out of the install surface.
- [ ] utils.__init__.py no longer re-exports helpers that are not part of the intended supported API.
- [ ] Any deleted helper has its dedicated tests removed or rewritten.
- [ ] Release notes or docs mention API removals if they affect user imports.


## Notes

**2026-03-27T18:30:09Z**

Review #1: Gate: NITS. Removed test-only helper get_partitions_from_path, stopped re-exporting create_filesystem_helper from flowerpower.utils, and removed the dedicated helper test. Minor nit: CHANGELOG.md was not updated to document the API surface reduction.
