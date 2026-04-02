---
id: flo-apob
status: closed
deps: []
links: []
created: 2026-03-27T15:55:53Z
type: task
priority: 2
assignee: legout
parent: flo-2n9o
tags: [cleanup, observability, bug]
---
# Fix or remove broken OpenTelemetry adapter glue

The OpenTelemetry integration appears inconsistent: utils.open_telemetry.init_tracer requires a name argument, while AdapterManager currently calls it without one. Either wire this path correctly with tests and a clear configuration contract, or remove/de-scope it until it is actually supported.

## Acceptance Criteria

- [ ] OpenTelemetry adapter setup is either fully functional and covered by tests, or removed from the maintained runtime path.
- [ ] No code path calls init_tracer with an invalid signature.
- [ ] Adapter behavior for missing optional dependencies remains explicit and understandable.
- [ ] Docs reflect the actual support level for OpenTelemetry.


## Notes

**2026-03-27T18:10:25Z**

Review #1: Gate: REVISE. Issues to fix:

- **[HIGH]** README still advertises OpenTelemetry adapter support — needs removal or deprecation notice
- **[HIGH]** Additional doc files (docs/) reference opentelemetry as a supported adapter — must be updated
- **[HIGH]** Docstrings in multiple modules still mention opentelemetry capabilities — need cleanup
- **[HIGH]** Configuration examples/docs still show opentelemetry config fields — need removal
- **[HIGH]** Inline comments referencing opentelemetry setup paths — need cleanup
- **[LOW]** Dead code: adapter.py returns None for opentelemetry — consider removing the branch entirely

Code changes are correct. Documentation must be updated to meet acceptance criterion #4.

**2026-03-27T18:17:08Z**

Review #2: Gate: PASS. All OTEL documentation updated (runconfig.md, flowerpowerproject.md, pipelinemanager.md, advanced.md, configuration.md). Dead open_telemetry.py module deleted. Adapter code stubbed with clear warning. 117 tests pass.
