## MODIFIED Requirements

### Requirement: Manager supports formatted pipeline listing
PipelineManager.show_pipelines MUST accept a `format` parameter ("table" | "json" | "yaml").
#### Scenario: CLI calls manager.show_pipelines(format="json")
- Manager prints JSON array of pipeline names to stdout without raising errors.
#### Scenario: CLI calls manager.show_pipelines(format="yaml")
- Manager prints YAML list of pipeline names to stdout without raising errors.
#### Scenario: Default format
- When `format` is omitted or "table", manager prints a formatted table via registry.

### Requirement: DAG save returns path and honors output_path
PipelineManager.save_dag and PipelineVisualizer.save_dag SHALL return the final file path and accept optional `output_path`.
#### Scenario: No output_path provided
- Graph is saved under `<project.base_dir>/graphs/<name>.<format>` and function returns that path.
#### Scenario: Custom output_path without extension
- Graph is saved at `<output_path>.<format>` and function returns that path.
#### Scenario: Custom output_path with extension
- Graph is saved at `output_path` as-is and function returns that path.
