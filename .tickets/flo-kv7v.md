---
id: flo-kv7v
status: closed
deps: []
links: []
created: 2026-03-27T15:55:53Z
type: task
priority: 3
assignee: legout
parent: flo-2n9o
tags: [cleanup, visualization, utils]
---
# Move visualization-only image viewer helpers out of utils.misc

The image-viewing helpers in utils.misc are only used by pipeline visualizer flows. Move them next to the visualizer or into a dedicated visualization helper module so misc.py stops carrying UI-oriented code unrelated to pipeline execution.

## Acceptance Criteria

- [ ] view_img and its helper functions live in a visualization-focused module instead of utils.misc.
- [ ] pipeline.visualizer imports the new location.
- [ ] Existing visualization tests still pass after the move.
- [ ] utils.misc is smaller and focused on genuinely shared runtime helpers.


## Notes

**2026-05-02T20:56:01Z**

Gate: PASS — Removed view_img re-export from utils/misc.py; helpers already lived in utils/visualization.py. Updated test_misc.py imports and fixed pre-existing missing fsspec imports (MemoryFileSystem, LocalFileSystem). Validation: 18/18 targeted tests pass, 369/369 full suite pass (2 pre-existing CLI failures unrelated). Static grep confirms zero visualization symbols remain in misc.py. Review not run.
