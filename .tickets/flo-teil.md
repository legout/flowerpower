---
id: flo-teil
status: open
deps: []
links: []
created: 2026-03-27T15:55:53Z
type: task
priority: 2
assignee: legout
parent: flo-2n9o
tags: [cleanup, utils, dead-code]
---
# Remove residual dead helper code from utils

Delete helper functions and methods that have no production callers and no meaningful documentation footprint. Current candidates: utils.misc.update_config_from_dict, utils.misc.update_nested_dict, utils.security.sanitize_log_data, utils.env._merge_dict, FilesystemHelper.resolve_path, FilesystemHelper.sync_filesystem, FilesystemHelper.clear_cache, AdapterManager.clear_cache, ExecutorFactory.clear_cache, plus stale imports left behind by prior refactors.

## Acceptance Criteria

- [ ] Dead helpers with zero runtime call sites are removed.
- [ ] Corresponding stale tests are removed or updated.
- [ ] Unused imports flagged by lint in the touched files are cleaned up.
- [ ] No behavioral changes to pipeline execution, config loading, or CLI flows.


## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

All 9 dead helpers still exist:
- `update_config_from_dict` and `update_nested_dict` in `utils/misc.py` (lines 339, 370) — no external callers
- `sanitize_log_data` in `utils/security.py` (line 154) — only self-referential (recursive), no external callers
- `_merge_dict` in `utils/env.py` (line 94) — only self-referential, no external callers
- `FilesystemHelper.resolve_path` in `utils/filesystem.py` (line 99) — no callers
- `FilesystemHelper.sync_filesystem` in `utils/filesystem.py` (line 140) — no callers
- `FilesystemHelper.clear_cache` in `utils/filesystem.py` (line 175) — no callers
- `AdapterManager.clear_cache` in `utils/adapter.py` (line 256) — no callers
- `ExecutorFactory.clear_cache` in `utils/executor.py` (line 172) — no callers
