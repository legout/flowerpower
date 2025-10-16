1. [x] Add `format` parameter to `PipelineManager.show_pipelines` with default "table"
2. [x] Implement JSON/YAML printing for non-table formats
3. [x] Add `output_path` to `PipelineVisualizer.save_dag` and return final path
4. [x] Pass `output_path` through `PipelineManager.save_dag` and return path
5. [x] Validate CLI `save-dag` logs the returned path without errors
6. [x] Validate CLI `show-pipelines --format json|yaml` runs without errors
