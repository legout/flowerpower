---
status: accepted
---

# Centralize RunConfig resolution before pipeline execution

FlowerPower will resolve each pipeline run into one canonical `RunConfig` before execution begins. The resolution will be pure and clone-on-write, using the existing configuration helpers rather than a new stateful configuration module; execution modules consume the resolved `RunConfig` through an internal resolved-only seam instead of re-merging defaults, overrides, adapter settings, or retry settings.

## Considered Options

- Keep merge logic distributed across project, executor, pipeline, runner, and execution-context modules.
- Add a new stateful configuration module that owns run state during execution.
- Add public flags or types to mark a `RunConfig` as already resolved.
- Use one pure resolver plus a private resolved-only execution seam.

The pure resolver was chosen because it concentrates precedence rules without adding runtime state or a second public execution interface.

## Consequences

Public run entrypoints keep their current shape, but all of them must reach the same resolution path. Legacy retry fields remain input compatibility only; the canonical retry model is nested under `RunConfig.retry`. Execution code may build runtime objects from the resolved configuration, but it must not fall back to pipeline defaults or project context to re-decide configuration precedence.
