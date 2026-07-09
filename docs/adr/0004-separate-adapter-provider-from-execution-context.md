# Separate adapter provider from execution context

FlowerPower will move adapter config resolution and runtime adapter construction behind an execution-facing adapter provider in `pipeline/adapter_provider.py`. The provider will return an internal `ResolvedAdapterSet` containing the resolved with-adapter, pipeline-adapter, and project-adapter configs plus runtime adapter instances; resolved adapter configs are still written back into the resolved `RunConfig` for compatibility.

## Considered Options

- Keep adapter resolution and construction in `utils/adapter.py` and `ExecutionContextBuilder`: rejected because config precedence, runtime construction, and project-context extraction remain spread across execution seams.
- Resolve adapter configs only and keep runtime construction in `ExecutionContextBuilder`: rejected because execution context would still know adapter construction details.
- Move adapter state into `ProjectRuntimeContext`: rejected because project runtime context is intentionally facts-only and config freshness belongs to registry/loader.

## Consequences

- `PipelineExecutor`/run planning should use the provider on the main execution path, passing explicit project adapter config from loader-owned project config rather than opaque project-context extraction.
- `ExecutionContextBuilder` should consume resolved runtime adapters instead of creating adapters or peeking into project context.
- Ray shutdown policy should come from the resolved project adapter config in `ResolvedAdapterSet`, not from duck-typed project context lookup.
- `extract_project_adapter_base(...)` may remain as a compatibility fallback for direct `Pipeline.run(...)` / `run_async(...)`, but it should not be used on the main executor path.
