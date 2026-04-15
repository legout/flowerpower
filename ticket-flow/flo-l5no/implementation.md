# Ticket flo-l5no Implementation

**Status:** ready-for-review

## Summary

Fixed env overlay silent error swallowing and mutable default arguments in pipeline modules.

## Changes Made

### 1. Fixed Silent Error Swallowing in `src/flowerpower/pipeline/config_manager.py`

**Lines 83-85 (load_project_config):**
- Changed from: `except Exception: pass`
- Changed to: `except Exception as e: logger.debug(f"Env overlay parsing failed: {e}")`

**Lines 151-153 (load_pipeline_config):**
- Changed from: `except Exception: pass`
- Changed to: `except Exception as e: logger.debug(f"Env overlay parsing failed: {e}")`

**Lines 128-130 (config path search):**
- Changed from: `except Exception: continue`
- Changed to: `except Exception as e: logger.debug(f"Could not check path {path}: {e}"); continue`

### 2. Fixed Mutable Default Arguments in `src/flowerpower/pipeline/manager.py`

Changed all delegation methods from mutable defaults `{}` to `None`:

- Line 702: `import_pipeline()` - `src_storage_options: dict | BaseStorageOptions | None = None`
- Line 761: `import_many()` - `src_storage_options: dict | BaseStorageOptions | None = None`
- Line 812: `import_all()` - `src_storage_options: dict | BaseStorageOptions | None = None`
- Line 862: `export_pipeline()` - `dest_storage_options: dict | BaseStorageOptions | None = None`
- Line 921: `export_many()` - `dest_storage_options: dict | BaseStorageOptions | None = None`
- Line 975: `export_all()` - `dest_storage_options: dict | BaseStorageOptions | None = None`

### 3. Fixed Mutable Default Arguments in `src/flowerpower/pipeline/base.py`

**Line 42:**
- Changed from: `storage_options: dict | Munch | BaseStorageOptions = {}`
- Changed to: `storage_options: dict | Munch | BaseStorageOptions | None = None`

**Line 46:**
- Changed from: `self._storage_options = storage_options`
- Changed to: `self._storage_options = storage_options or {}`

### 4. Added Tests

Created `tests/pipeline/test_env_overlay_logging.py` with two tests:
- `test_env_overlay_error_is_logged_at_debug()`: Verifies env overlay errors in `load_project_config()` are logged at DEBUG level
- `test_pipeline_config_env_overlay_error_is_logged_at_debug()`: Verifies env overlay errors in `load_pipeline_config()` are logged at DEBUG level

## Verification

### Tests Pass
```bash
$ uv run pytest tests/pipeline/test_env_overlay_logging.py -v
============================= test session starts ==============================
tests/pipeline/test_env_overlay_logging.py::test_env_overlay_error_is_logged_at_debug PASSED
tests/pipeline/test_env_overlay_logging.py::test_pipeline_config_env_overlay_error_is_logged_at_debug PASSED
============================== 2 passed in 0.56s ===============================
```

### No More Mutable Defaults in Pipeline Files
```bash
$ grep -n "storage_options.*= {}" src/flowerpower/pipeline/*.py
# No output - all mutable defaults fixed
```

### No More Silent Error Swallowing
```bash
$ grep -n "except Exception: pass\|except Exception:\s*$" src/flowerpower/pipeline/*.py
# No output - all silent error swallowing fixed
```

### Imports Work
```bash
$ uv run python -c "
from flowerpower.pipeline.config_manager import PipelineConfigManager
from flowerpower.pipeline.io import PipelineIOManager
from flowerpower.pipeline.manager import PipelineManager
from flowerpower.pipeline.base import BasePipeline
print('All imports successful')
"
All imports successful
```

## Acceptance Criteria Checklist

- [x] `except Exception: pass` in config manager replaced with `except Exception as e: logger.debug(...)`
- [x] All `src_storage_options={}` and `dest_storage_options={}` defaults in `PipelineIOManager` changed to `None` (was already done)
- [x] Same pattern applied in `PipelineManager` delegation methods
- [x] Tests verify env overlay errors are logged (not silently swallowed)

## Notes

The `PipelineIOManager` already had the correct pattern (`storage_options = storage_options or {}` inside function bodies), so only the delegation methods in `PipelineManager` and `BasePipeline` needed updating.
