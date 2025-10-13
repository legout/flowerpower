# Proposal: Align Manager API with CLI (show_pipelines format, save_dag output)

## Summary
Modify PipelineManager and PipelineVisualizer to match the CLI surface:
- PipelineManager.show_pipelines(format) should accept a `format` parameter ("table" | "json" | "yaml").
- PipelineManager.save_dag(...) should return the output file path and accept an optional `output_path` override, which PipelineVisualizer implements.

## Rationale
Current CLI calls `manager.show_pipelines(format=...)` and expects `manager.save_dag(...)` to return a file path; the Manager doesn’t accept `format`, and Visualizer/Manager don’t return a path nor accept `output_path`. This causes runtime inconsistencies and complicates downstream scripting.

## Scope
- Add `format: str = "table"` to `PipelineManager.show_pipelines` and implement JSON/YAML output for non-table formats.
- Add `output_path: str | None = None` to `PipelineManager.save_dag` and return `str` path from Manager/Visualizer.
- Update `PipelineVisualizer.save_dag` to accept `output_path` and return the final path with extension.

## Non-Goals
- Change CLI behavior or options.
- Change registry internals; keep formatting logic in Manager.

## Risks
- Minor API change on Manager method signatures—backward compatible due to defaults.
