# Deepen PipelineManager as the project facade

PipelineManager remains the stable public project facade for coordinating pipeline catalog, configuration, execution, visualization, creation, and transfer workflows. We will deepen it by introducing an internal frozen `ProjectRuntimeContext` in `pipeline/project_context.py` for project runtime facts only (filesystem, base directory, storage options, configured directories, and filesystem ownership), adding `PipelineManager.load_existing()` and `PipelineManager.new_project()` factories, and making `FlowerPowerProject` a compatibility wrapper that delegates to PipelineManager rather than duplicating project setup policy.

## Considered Options

- Promote `FlowerPowerProject` as the primary facade: rejected because `PipelineManager` is already the stable public coordination surface and changing that would add migration churn.
- Introduce a new `ProjectFacade` type: rejected because it would add another public concept instead of deepening the existing one.
- Put config loaders or component instances in `ProjectRuntimeContext`: rejected to avoid turning the context into a service locator; project config freshness remains owned by the registry/loader cache.

## Consequences

- Existing component access (`registry`, `visualizer`, `io`, `creator`, `executor`) remains compatible, but components should be constructed from context-aware factories such as `from_context(...)`.
- PipelineManager owns filesystem setup/caching policy and tracks whether it owns the filesystem; context-manager cleanup clears only owned filesystem caches.
- Execution receives project runtime context through constructor injection rather than private per-run mutation.
- Project creation moves toward `PipelineManager.new_project()`, while `FlowerPowerProject.new()` remains as a delegating compatibility API.
