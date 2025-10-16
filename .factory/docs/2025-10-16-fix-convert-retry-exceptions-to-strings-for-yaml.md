# OpenSpec Change Proposal: Convert Retry Exceptions to Strings for YAML Serialization

## Why
When saving PipelineConfig to YAML, the `retry_exceptions` field in RetryConfig contains actual exception class objects (like `<class 'ValueError'>`) which cannot be properly serialized to YAML. These need to be converted to their string representations before writing to disk.

## What Changes
- **MODIFIED**: Update `RunConfig.to_dict()` method to properly convert exception classes to strings in the nested `retry.retry_exceptions` field
- Ensure backward compatibility when loading YAML files with string representations
- Maintain existing exception conversion logic during loading

## Impact
- **Affected specs**: config-pipeline-yaml-serialization
- **Affected code**: `src/flowerpower/cfg/pipeline/run.py:207-230` (RunConfig.to_dict method)
- **Files to modify**: `src/flowerpower/cfg/pipeline/run.py`
- **Tests to update**: `tests/cfg/test_run_config.py` (test_to_dict_removes_deprecated_retry_fields and related)

## Technical Details
The current `RunConfig.to_dict()` method has logic to convert exceptions to strings, but it may not be handling all cases correctly when nested exceptions are present in the `retry` configuration. The fix will ensure that exception classes in `retry.retry_exceptions` are properly converted to their string names before YAML serialization.

This is a targeted fix that maintains existing behavior while ensuring proper YAML serialization.