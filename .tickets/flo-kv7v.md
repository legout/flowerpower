---
id: flo-kv7v
status: open
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

