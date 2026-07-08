---
status: accepted
---

# Split PipelineRegistry into catalog, loader, and shared module resolver

FlowerPower will split the current `PipelineRegistry` responsibilities into explicit catalog, loader, and module-resolution modules while keeping `PipelineRegistry` as a backward-compatible facade during the migration.

The catalog interface owns pipeline discovery, listing, metadata, and presentation-free summary payloads. The loader interface owns loading pipeline configuration, loading pipeline modules, constructing `Pipeline` instances, and cache/reload invalidation. A shared pipeline module resolver owns import-name normalization, package-root fallback, hyphen-to-underscore handling, uniqueness, and reload policy for registry loading, execution `additional_modules`, and visualization.

## Considered Options

- Keep `PipelineRegistry` as the single owner for discovery, cache, config loading, module loading, pipeline construction, lifecycle shims, hooks, and summary payload assembly.
- Extract only a standalone module resolver and defer the broader registry/catalog split.
- Split `PipelineRegistry` immediately into separate public modules and remove compatibility methods in one step.
- Keep `PipelineRegistry` as a compatibility facade while extracting catalog, loader, and module-resolution implementations behind it.

The compatibility-facade option was chosen because it concentrates the duplicated import/reload behavior now, clarifies the name-to-pipeline seam that execution depends on, and avoids a hard public API break while the internal ownership boundaries are corrected.

## Consequences

Existing callers may continue to use `PipelineRegistry` methods such as `list_pipelines`, `get_summary`, `load_config`, `load_module`, `get_pipeline`, `clear_cache`, `new`, and `delete` during the migration. Internally, those methods should delegate to narrower modules instead of sharing one broad mutable implementation.

`PipelineModuleResolver` becomes the single place where pipeline module import candidates, custom `pipelines_dir` package roots, nested pipeline names, hyphen-to-underscore conversion, module identity de-duplication, and reload behavior are decided. `PipelineRunner` and `PipelineVisualizer` must not maintain separate fallback candidate algorithms.

The split does not change `RunConfig` resolution, Hamilton execution semantics, environment overlay parsing, or public pipeline lifecycle behavior. It does make cache and reload ownership explicit enough for a later `PipelineConfigManager` config-store deepening pass.
