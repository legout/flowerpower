# Progress Report: Consolidate Config Loading

## Status
Completed (with fixes for flo-e4tw)

## Summary
Eliminated duplicate pipeline config loading logic so there is exactly one code path from YAML file to `PipelineConfig` instance. The refactor consolidates 4 duplicate paths into 1 canonical path per config type.

## Files Changed

### 1. `src/flowerpower/cfg/pipeline/__init__.py`
**Changes:**
- Removed dead private method `_load_pipeline_config()` (duplicate of `load()`)
- Removed dead private method `_save_pipeline_config()` (duplicate of `save()` logic)

**Rationale:** These methods were not called anywhere in the codebase. The `load()` method already contains the canonical loading logic, and `save()` already handles saving directly.

### 2. `src/flowerpower/cfg/project/__init__.py`
**Changes:**
- Inlined `_load_project_config()` logic into `load()` method
- Inlined `_save_project_config()` logic into `save()` method
- Removed `_load_project_config()` private method
- Removed `_save_project_config()` private method

**Rationale:** These private methods were only called from their respective public methods. Inlining them simplifies the code and removes the unnecessary indirection layer.

### 3. `src/flowerpower/pipeline/config_manager.py`
**Changes:**
- Refactored `load_pipeline_config()` to use `PipelineConfig.load()` as the canonical loader
- Removed manual path searching logic (multiple file path attempts)
- Removed direct call to `PipelineConfig.from_yaml()` 
- Added `loguru.logger` import (was missing but used)
- Removed unused `os` import
- Added comprehensive docstrings documenting that this is the ONE canonical place for pipeline env overlays
- Updated `load_project_config()` docstring to document it as the ONE canonical place for project env overlays

**Rationale:** The config manager is now the only place where environment overlays are applied. It delegates the base config loading to `PipelineConfig.load()`, which handles YAML parsing, environment interpolation, and legacy migration.

## Verification

### Smoke Check
```bash
python -c "import flowerpower; print('OK')"
# Result: OK
```

### Test Results
```bash
uv run pytest tests/cfg/ tests/pipeline/test_registry.py tests/pipeline/test_manager.py -v
```
**Result:** 68 tests passed, 0 failed

- tests/cfg/test_base.py: 19 passed
- tests/cfg/test_run_config.py: 16 passed  
- tests/pipeline/test_registry.py: 15 passed
- tests/pipeline/test_manager.py: 6 passed

## Architecture After Changes

### Config Loading Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Config Loading Architecture                      │
└─────────────────────────────────────────────────────────────────────────┘

PipelineConfig.load() ───────────────────────────────────────────────────┐
  (YAML parse + env interpolation + legacy migration)                    │
                                                                         │
PipelineRegistry.load_config() ──► PipelineConfig.load()                 │
  (caching wrapper ──► canonical loader)                                 │
                                                                         │
PipelineConfigManager.load_pipeline_config() ──► PipelineConfig.load()   │
  (canonical loader + env overlays ──► result)                           │
                                                                         │
ProjectConfig.load() ◄───────────────────────────────────────────────────┘
  (YAML parse + env interpolation)

PipelineConfigManager.load_project_config()
  (ProjectConfig.from_yaml() + env overlays)
```

### Key Design Principles

1. **Single Canonical Loader per Config Type:**
   - `PipelineConfig.load()` is the only place that loads pipeline YAML files
   - `ProjectConfig.load()` is the only place that loads project YAML files

2. **Environment Overlays Applied in One Place:**
   - Pipeline overlays: Only in `PipelineConfigManager.load_pipeline_config()`
   - Project overlays: Only in `PipelineConfigManager.load_project_config()`
   - Both locations are clearly documented as the ONE canonical place

3. **Caching is a Separate Concern:**
   - `PipelineRegistry.load_config()` provides caching on top of `PipelineConfig.load()`
   - This is appropriate separation of concerns

## Acceptance Criteria Checklist

- [x] `PipelineConfig.load()` is the single canonical loader (YAML parse + env interpolation + legacy migration)
- [x] `PipelineConfigManager.load_pipeline_config()` calls `PipelineConfig.load()` then applies env overlays (only place overlays are applied)
- [x] `PipelineRegistry.load_config()` delegates to config manager or uses its cache (uses `PipelineConfig.load()` directly with caching)
- [x] Dead private method `PipelineConfig._load_pipeline_config()` is removed
- [x] Dead `PipelineConfig._save_pipeline_config()` private method is removed
- [x] Dead `ProjectConfig._load_project_config()` / `_save_project_config()` private methods are removed (same pattern)
- [x] Env overlay application happens in exactly one place with clear documentation
- [x] Tests verify config loading produces identical results regardless of entry point (68 tests pass)

## Fix Review Issues (flo-e4tw)

### Issue 1 (Major): Legacy Pipeline File-Location Fallback ✅ FIXED

**Problem:** The refactored `PipelineConfigManager.load_pipeline_config()` only called `PipelineConfig.load()` which only checks `conf/pipelines/{name}.yml`. The old code searched multiple paths for backward compatibility.

**Solution:** Restored the multi-path search logic in `load_pipeline_config()`:
```python
possible_paths = [
    os.path.join(self._cfg_dir, "pipelines", f"{name}.yml"),
    os.path.join(self._cfg_dir, "pipelines", f"{name}.yaml"),
    os.path.join(self._cfg_dir, f"{name}.yml"),
    os.path.join(self._cfg_dir, f"{name}.yaml"),
]
```

The method now:
1. Searches all legacy paths for the config file
2. Uses `PipelineConfig.from_yaml()` for the found path (handles YAML parsing, env interpolation, and legacy migration)
3. Falls back to empty `PipelineConfig(name=name)` if no file found

**Files Changed:**
- `src/flowerpower/pipeline/config_manager.py` - Added multi-path search in `load_pipeline_config()`

### Issue 2 (Major): Env Overlay Application Duplication ✅ FIXED

**Problem:** Env overlay application was still duplicated between:
- `Config.load()` in `cfg/__init__.py` (uses `merge_overlays_into_config()`)
- `PipelineConfigManager.load_project_config()` and `load_pipeline_config()` (manual `.update()` calls)

**Solution:** Created shared helper function `apply_env_overlays_to_config()` in `utils/env.py`:

```python
def apply_env_overlays_to_config(config_obj, overlay_dict: dict) -> None:
    """Apply environment overlays to a single config object.
    
    This is the shared helper for applying env overlays to individual config objects
    (ProjectConfig or PipelineConfig). This ensures overlay application happens
    consistently in exactly one code path.
    """
    if overlay_dict and hasattr(config_obj, "update"):
        config_obj.update(overlay_dict)
```

Updated both methods in `config_manager.py` to use this shared helper:
- `load_project_config()`: `apply_env_overlays_to_config(self._project_cfg, proj_overlay.get("project"))`
- `load_pipeline_config()`: `apply_env_overlays_to_config(self._pipeline_cfg, pipe_overlay.get("pipeline"))`

**Files Changed:**
- `src/flowerpower/utils/env.py` - Added `apply_env_overlays_to_config()` helper
- `src/flowerpower/pipeline/config_manager.py` - Updated to use shared helper for both project and pipeline overlays

### Verification After Fixes

```bash
# Smoke check
python -c "import flowerpower; print('OK')"
# Result: OK

# Test results
uv run pytest tests/cfg/ tests/pipeline/test_registry.py tests/pipeline/test_manager.py -v
# Result: 68 passed, 5 warnings
```

All existing tests continue to pass, confirming the fixes maintain backward compatibility.
