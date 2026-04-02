# FlowerPower Deep Analysis & Refactoring Plan

## Project Overview

**FlowerPower** is a Python framework (~10.5K lines across 53 source files) that wraps [Hamilton](https://github.com/apache/hamilton) to provide configuration-driven pipeline orchestration with YAML configs, CLI, filesystem abstraction, and adapter support.

### Architecture Summary

```
CLI (typer) → FlowerPowerProject → PipelineManager → PipelineExecutor → Pipeline → PipelineRunner → Hamilton Driver
                                    ↓                    ↓               ↓
                              PipelineConfigManager  PipelineRegistry  AdapterManager
                              PipelineLifecycleManager                 ExecutorFactory
                              PipelineVisualizer                       RetryManager
                              PipelineIOManager                        ExecutionContextBuilder
```

### Key Abstractions
- **Config layer**: `BaseConfig` (msgspec.Struct) → `ProjectConfig`, `PipelineConfig`, `RunConfig`, etc.
- **Pipeline layer**: `PipelineManager` → delegates to `PipelineExecutor`, `PipelineLifecycleManager`, `PipelineIOManager`, `PipelineVisualizer`, `PipelineRegistry`
- **Execution layer**: `Pipeline` → `PipelineRunner` → `ExecutionContextBuilder` → Hamilton Driver

---

## 🔴 CRITICAL FINDINGS: Overcomplexity & KISS Violations

### 1. Duplicate `RunConfigBuilder` — TWO implementations exist

**Files:**
- `src/flowerpower/cfg/pipeline/builder.py` (389 lines) — `RunConfigBuilder` class
- `src/flowerpower/utils/config.py` (lines 200-430) — **another** `RunConfigBuilder` class

**Problem:** Two completely different `RunConfigBuilder` classes with different APIs, different feature sets, and different import paths. The one in `builder.py` loads defaults from YAML files and has sub-builders (`ExecutorBuilder`, `AdapterBuilder`). The one in `utils/config.py` is simpler but duplicates much of the same logic.

**Impact:** Users importing from different locations get different builders. Test confusion. Maintenance nightmare.

**Fix:** Delete one. Keep the one in `utils/config.py` (simpler, already used by `merge_run_config_with_kwargs`). If YAML-defaults-loading is needed, add it as an optional `.from_pipeline()` classmethod.

---

### 2. `PipelineLifecycleManager` is a pure pass-through wrapper

**File:** `src/flowerpower/pipeline/lifecycle_manager.py` (230 lines)

**Problem:** Every single method in `PipelineLifecycleManager` is a direct delegation to `self._registry`:
```python
def create_pipeline(self, name, overwrite=False, template=None, tags=None, description=None):
    self._registry.create_pipeline(name=name, overwrite=overwrite, template=template, tags=tags, description=description)

def delete_pipeline(self, name, cfg=True, module=False):
    self._registry.delete_pipeline(name=name, cfg=cfg, module=module)

def list_pipelines(self):
    return self._registry.list_pipelines()

def add_hook(self, name, type, to=None, function_name=None):
    self._registry.add_hook(name=name, type=type, to=to, function_name=function_name)
```

But `PipelineLifecycleManager.show_summary()` and `PipelineLifecycleManager.show_pipelines()` call `self._registry.get_summaries()` and `self._registry.get_pipeline_object()` — **methods that don't exist on `PipelineRegistry`!** This is a latent bug (calls would fail at runtime).

**Fix:** Delete `PipelineLifecycleManager` entirely. Have `PipelineManager` call `self.registry.*` directly.

---

### 3. `PipelineManager` is a 1109-line god class of pure delegation

**File:** `src/flowerpower/pipeline/manager.py` (1109 lines)

**Problem:** `PipelineManager` has 5 sub-managers but is mostly a thin forwarding layer. The `__init__` alone sets up filesystem, config manager, registry, executor, lifecycle manager, visualizer, IO manager — each with their own init. The `run()` method (line ~195) does nothing but `self._executor.run()`.

The IO delegation methods (`import_pipeline`, `export_pipeline`, `import_many`, `export_many`, `import_all`, `export_all`) are 6 near-identical methods each forwarding to `self.io.*` with full docstrings repeated.

**Fix:** 
- Expose sub-managers as public properties and let users call them directly
- Remove the 6 IO delegation methods (just use `pm.io.import_pipeline(...)`)
- Remove the 6 registry delegation methods  
- Target: reduce from ~1109 lines to ~300 lines

---

### 4. `PipelineRegistry` mixes concerns (875 lines)

**File:** `src/flowerpower/pipeline/registry.py`

**Problem:** The registry handles:
1. Pipeline discovery and listing (`_get_files`, `_get_names`)
2. Pipeline creation/deletion (`new`, `delete`, `create_pipeline`, `delete_pipeline`)
3. Pipeline caching (`_pipeline_data_cache`, `CachedPipelineData`)
4. Pipeline visualization/showing (`show_pipelines`, `show_summary`, `_all_pipelines`)
5. Hook management (`add_hook`)
6. Module path manipulation (`_add_modules_path`)
7. Module loading (`load_module`)

That's 7 responsibilities in one class. The `show_summary` method (lines ~400-500) renders Rich panels, tables, and syntax highlighting — completely unrelated to registry concerns.

**Fix:** Split into:
- `PipelineRegistry` — discovery, listing, caching only
- `PipelineCreator` — creation, deletion, hooks (or merge into manager)
- Move Rich rendering to a separate `PipelineFormatter` or `PipelinePresenter`

---

### 5. Config loading is duplicated in 4+ places

**Problem:** Pipeline config loading happens in:
1. `PipelineConfig.load()` in `cfg/pipeline/__init__.py`
2. `PipelineConfigManager.load_pipeline_config()` in `pipeline/config_manager.py`
3. `PipelineRegistry.load_config()` in `pipeline/registry.py`
4. `PipelineConfig._load_pipeline_config()` in `cfg/pipeline/__init__.py`

All do essentially the same thing: find YAML file, parse it, create PipelineConfig. The config_manager also applies env overlays (which the others don't consistently).

**Fix:** Single canonical load path: `PipelineConfig.load()`. Everyone else calls that.

---

### 6. `_add_modules_path()` is duplicated 3 times

**Files:**
- `PipelineManager._add_modules_path()` (manager.py)
- `PipelineRegistry._add_modules_path()` (registry.py)
- `BasePipeline._add_modules_path()` (base.py)

All three do the same thing: check if cache_fs, sync cache, add to sys.path. Each has slightly different fallback logic.

**Fix:** Single function in `utils/filesystem.py`, called by all three.

---

### 7. Overengineered callback system

**File:** `src/flowerpower/utils/callback.py` (164 lines)

**Problem:** There's a full callback framework with `_prepare_callback_details`, `_parse_tuple_callback_args`, `_add_exception_to_simple_callback`, `_add_exception_to_tuple_callback`, `run_with_callback` decorator, and `CallbackSpec` struct. 

Meanwhile, `RetryManager` has its own simpler `_handle_success`/`_handle_failure` static methods that take `CallbackSpec`. The callback.py module is **never imported** by any production code — only tests reference it.

**Fix:** Delete `callback.py` entirely. The `RetryManager`'s simple approach is sufficient.

---

### 8. `BasePipeline` class is dead code

**File:** `src/flowerpower/pipeline/base.py` (130 lines)

**Problem:** `BasePipeline` has `_setup_paths`, `_setup_directories`, `_add_modules_path`, `_load_project_cfg`, `_load_pipeline_cfg`. But it's never used anywhere in the production code path. The actual pipeline class is `Pipeline` in `pipeline.py` (a msgspec.Struct, not inheriting from BasePipeline).

`load_module()` from `base.py` IS used by registry and visualizer, but that's just a 10-line utility function.

**Fix:** Move `load_module()` to `utils/misc.py`. Delete `BasePipeline` class entirely.

---

### 9. `Config` class in `cfg/__init__.py` duplicates `PipelineConfig` + `ProjectConfig`

**File:** `src/flowerpower/cfg/__init__.py` (385 lines)

**Problem:** The `Config` class combines project and pipeline configs, but so does `PipelineManager` (via `PipelineConfigManager`). The `Config.load()` method (line ~115) applies env overlays, but so does `PipelineConfigManager.load_pipeline_config()`. There are also standalone `load()`, `save()`, `init_config()` functions that duplicate the class methods.

The module-level `_load_config()` and `_save_pipeline_config()`/`_save_project_config()` functions at the bottom of the file (lines ~300-385) appear to be dead code — they're module-level functions that are never called.

**Fix:** 
- Remove the standalone helper functions at the bottom of `cfg/__init__.py`
- Decide: is `Config` the canonical combined config, or is it `PipelineConfigManager`? Pick one.

---

### 10. `RunConfig` has deprecated fields kept for "backward compatibility" but they create confusion

**File:** `src/flowerpower/cfg/pipeline/run.py`

**Problem:** `RunConfig` has BOTH:
- New nested: `retry: RetryConfig | None`
- Old flat: `max_retries: int`, `retry_delay: int | float`, `jitter_factor: float`, `retry_exceptions: list[str]`

The `__post_init__` syncs them bidirectionally. The `to_dict()` strips the old ones. `merge_run_config_with_kwargs()` maps old kwargs to the nested field. `migrate_legacy_retry_fields()` handles YAML migration.

This is 4 different places handling the same deprecation.

**Fix:** Just keep the nested `retry` field. Add a simple `__post_init__` that migrates if old fields are passed. Remove the old fields from the struct. This eliminates ~100 lines of sync/migration code.

---

## 🟡 MEDIUM FINDINGS: Performance Issues

### 11. Unbounded filesystem cache in `BaseConfig._fs_cache`

**File:** `src/flowerpower/cfg/base.py`

```python
class BaseConfig(msgspec.Struct, kw_only=True):
    _fs_cache = {}  # CLASS-LEVEL, never cleared, no size limit
    
    @classmethod
    @lru_cache(maxsize=32)
    def _get_cached_filesystem(cls, base_dir: str, storage_options_hash: int) -> ...
```

**Problem:** `_fs_cache` is a class-level dict that grows forever. The `@lru_cache` on `_get_cached_filesystem` provides its own caching (maxsize=32), but `_fs_cache` is a separate, redundant cache that's never bounded.

**Fix:** Delete `_fs_cache` entirely. The `lru_cache` is sufficient.

---

### 12. Executor cache in `ExecutorFactory._executor_cache` is unbounded

**File:** `src/flowerpower/utils/executor.py`

```python
self._executor_cache: Dict[str, Any] = {}
```

**Problem:** Cache key is `f"{executor_type}_{hash(str(executor_cfg.to_dict()))}"`. Every unique config creates a new cached executor that's never evicted. With many different pipeline configs, this leaks memory.

**Fix:** Use `@lru_cache` or an LRU dict with a reasonable max size.

---

### 13. `_convert_dict_recursively` in `BaseConfig.to_dict()` is deeply nested

**File:** `src/flowerpower/cfg/base.py`

**Problem:** `to_dict()` calls `_convert_dict_recursively()` which creates new dicts at every level. For deeply nested configs, this creates many intermediate objects. Called frequently during serialization.

**Fix:** Use `msgspec.to_builtins()` which already handles this efficiently. The custom `to_dict()` seems to exist to handle Munch objects — consider not using Munch at all (see finding #15).

---

### 14. `sys.path` manipulation is unsafe and repeated

**Files:** manager.py, registry.py, base.py

**Problem:** `sys.path.insert(0, ...)` is called every time a `PipelineManager` or `PipelineRegistry` is created, with no deduplication guarantee (the `if project_path not in sys.path` check uses string comparison which can miss equivalent paths like `/foo/bar` vs `/foo/bar/`).

**Fix:** Use a set to track added paths. Or better yet, use a proper Python package approach.

---

## 🟠 BUG FINDINGS

### 15. `FlowerPowerProject.load()` can return `None`

**File:** `src/flowerpower/flowerpower.py`, line ~196

```python
@classmethod
def load(cls, ...) -> "FlowerPowerProject":
    ...
    if project_exists:
        ...
        return project
    else:
        rich.print(f"[red]{message}[/red]")
        return None  # ← Return type annotation says FlowerPowerProject, not Optional[FlowerPowerProject]
```

**Problem:** The return type is `FlowerPowerProject` but it returns `None`. Every caller must check for `None`, and the CLI does (`if project is None`), but the type system doesn't enforce this. Static type checkers won't catch missing None checks.

**Fix:** Either raise `FileNotFoundError` instead of returning None, or change the return type to `FlowerPowerProject | None`.

---

### 16. `PipelineRegistry` delete doesn't use `formatted_name`

**File:** `src/flowerpower/pipeline/registry.py`, `delete()` method (line ~475)

```python
def delete(self, name: str, cfg: bool = True, module: bool = False):
    if cfg:
        pipeline_cfg_path = posixpath.join(self._cfg_dir, PIPELINES_DIR, f"{name}.yml")
    if module:
        pipeline_py_path = posixpath.join(self._pipelines_dir, f"{name}.py")
```

But in `new()` (line ~370):
```python
formatted_name = name.replace(".", "/").replace("-", "_")
pipeline_file = posixpath.join(self._pipelines_dir, f"{formatted_name}.py")
cfg_file = posixpath.join(self._cfg_dir, PIPELINES_DIR, f"{formatted_name}.yml")
```

**Problem:** `new()` replaces dots and hyphens in the name, but `delete()` uses the raw name. If you create a pipeline named "my-pipeline", the files are "my_pipeline.py" / "my_pipeline.yml", but `delete("my-pipeline")` looks for "my-pipeline.yml" — **file not found**.

**Fix:** Apply the same `formatted_name = name.replace(".", "/").replace("-", "_")` transformation in `delete()`.

---

### 17. `PipelineConfigManager.load_pipeline_config()` silently swallows env overlay errors

**File:** `src/flowerpower/pipeline/config_manager.py`

```python
try:
    overrides = parse_env_overrides()
    proj_overlay, pipe_overlay = build_specific_overlays(overrides)
    apply_global_shims(overrides, proj_overlay, pipe_overlay)
    if pipe_overlay.get("pipeline") and hasattr(self._pipeline_cfg, "update"):
        self._pipeline_cfg.update(pipe_overlay["pipeline"])  
except Exception:
    pass  # ← Silently swallows ALL errors
```

**Problem:** If env overlay parsing has a bug, it's completely invisible. This happens in both `load_project_config()` and `load_pipeline_config()`.

**Fix:** At minimum, log the error: `except Exception as e: logger.debug(f"Env overlay failed: {e}")`.

---

### 18. `PipelineLifecycleManager.get_summary()` calls non-existent methods

**File:** `src/flowerpower/pipeline/lifecycle_manager.py`

```python
def get_summary(self, name=None, cfg=True, code=True, project=True):
    if name is None:
        return self._registry.get_summaries(cfg=cfg, code=code, project=project)  # ← doesn't exist
    else:
        pipeline = self._registry.get_pipeline_object(name=name)  # ← doesn't exist
        return pipeline.get_summary(cfg=cfg, code=code, project=project)
```

**Problem:** `PipelineRegistry` has `get_summary()` (singular), not `get_summaries()`. And there's no `get_pipeline_object()` method. This would crash at runtime if `get_summary(name=None)` is called on `PipelineLifecycleManager`.

**Fix:** Fix the method names or delete `PipelineLifecycleManager` (see finding #2).

---

### 19. `HookType` default_function_name has a self-comparison bug

**File:** `src/flowerpower/pipeline/registry.py`

```python
class HookType(str, Enum):
    MQTT_BUILD_CONFIG = "mqtt-build-config"

    def default_function_name(self) -> str:
        match self.value:
            case HookType.MQTT_BUILD_CONFIG:  # ← compares string to Enum
                return self.value.replace("-", "_")
```

**Problem:** `self.value` is a string (`"mqtt-build-config"`), but the case pattern is `HookType.MQTT_BUILD_CONFIG` which is an Enum. This comparison will never match. It should be `case "mqtt-build-config":` or `case self.MQTT_BUILD_CONFIG:`.

Actually, since there's only one enum value and the fallback does `return self.value`, this happens to work by accident — but it's still a bug in the pattern matching logic.

**Fix:** Use `case "mqtt-build-config":` or simply `return self.value.replace("-", "_")`.

---

### 20. `RetryConfig.to_dict()` has fragile string parsing

**File:** `src/flowerpower/cfg/pipeline/run.py`

```python
if (isinstance(exc, str) and exc.startswith("<class '") and exc.endswith("'>")):
    class_name = exc[8:-2]  # Remove "<class '" and "'>"
```

**Problem:** This tries to clean up `<class 'ValueError'>` strings, but the `to_dict()` override from `BaseConfig` already handles type objects via `str(value)`. This double-conversion is fragile and depends on exact Python repr format.

**Fix:** In `RetryConfig.to_dict()`, directly convert exception classes to names: `exc.__name__ if isinstance(exc, type) else exc`.

---

### 21. `view_img()` has a race condition with temp file cleanup

**File:** `src/flowerpower/utils/misc.py`

```python
def view_img(data, format="svg"):
    tmp_path = _create_temp_image_file(data, validated_format)
    try:
        _open_image_viewer(tmp_path)
    except ...:
        _cleanup_temp_file(tmp_path)
        raise
    time.sleep(2)  # ← hope the viewer opened the file in 2 seconds
    _cleanup_temp_file(tmp_path)
```

**Problem:** After 2 seconds, the temp file is deleted. If the viewer is slow (network mount, large file), it may not have read the file yet. The `time.sleep(2)` is a hack.

**Fix:** Use `atexit` to clean up, or don't clean up (OS handles temp files), or use `tempfile.NamedTemporaryFile(delete=True)` and pass the file handle.

---

### 22. Mutable default arguments in `PipelineIOManager` methods

**File:** `src/flowerpower/pipeline/io.py`

```python
def import_pipeline(self, name, src_base_dir, src_fs=None, 
                    src_storage_options: dict | BaseStorageOptions | None = {},  # ← MUTABLE DEFAULT
                    overwrite=False):
```

**Problem:** `{}` is a mutable default argument. While in this case it's not modified (passed directly to `_sync_filesystem`), it's a well-known Python anti-pattern that can cause subtle bugs if the default is ever mutated.

**Fix:** Use `None` as default and set to `{}` inside the function.

---

## 🔵 CODE QUALITY & DUPLICATION FINDINGS

### 23. Pipeline name validation is duplicated 5 times

**Locations:**
- `PipelineConfig._validate_pipeline_name()` in `cfg/pipeline/__init__.py`
- `Config.save()` in `cfg/__init__.py` (inline check)
- `validate_pipeline_name()` in `utils/security.py`
- `FlowerPowerProject._validate_pipeline_name()` in `flowerpower.py` (calls security.py)
- Registry's `new()` doesn't validate at all!

**Fix:** One canonical validation function: `validate_pipeline_name()` in `utils/security.py`. Everyone calls it.

---

### 24. Path traversal validation is duplicated 3 times

**Locations:**
- `validate_file_path()` in `utils/security.py` (comprehensive)
- `validate_file_path()` in `cfg/base.py` (wraps security.py)
- Inline checks in `PipelineConfig._validate_pipeline_name()` and `Config.save()` (simple `..` checks)

**Fix:** Use `utils/security.validate_file_path()` everywhere. Remove the wrapper in `cfg/base.py` and the inline checks.

---

### 25. `Munch` is used inconsistently

**Problem:** `Munch` (dot-access dicts) is used for:
- `RunConfig.config` — converted to Munch in `__post_init__`
- `RunConfig.cache` — conditionally converted to Munch
- `PipelineConfig.params` and `h_params` — converted to Munch
- `Config.storage_options` — stored as Munch

But most other places use plain dicts. This inconsistency means callers sometimes get Munch, sometimes dict, sometimes msgspec.Struct.

**Fix:** Remove Munch dependency entirely. Use plain dicts everywhere. The dot-access convenience isn't worth the type confusion.

---

### 26. Massive commented-out code block in `utils/misc.py`

**File:** `src/flowerpower/utils/misc.py` (lines 15-130)

~115 lines of commented-out `run_parallel()` implementation using joblib. This is dead code that clutters the file.

**Fix:** Delete it. If needed later, it's in git history.

---

### 27. `cfg/pipeline/builder_executor.py` and `builder_adapter.py` are barely used

**Problem:** `ExecutorBuilder` (107 lines) and `AdapterBuilder` (141 lines) are only used by `RunConfigBuilder` in `builder.py` — which is the duplicate builder identified in finding #1. If that builder is removed, these become dead code too.

**Fix:** If keeping the `builder.py` builder, inline the simple logic from `ExecutorBuilder` and `AdapterBuilder` (they're trivial). If deleting `builder.py`, delete these too.

---

### 28. Exception handling in CLI is overly broad

**File:** `src/flowerpower/cli/pipeline.py`

Every command wraps everything in:
```python
except Exception as e:
    logger.error(f"Pipeline execution failed: {e}")
    raise typer.Exit(1)
```

This catches `KeyboardInterrupt` and `SystemExit`, preventing clean cancellation.

**Fix:** Catch `(Exception)` explicitly but exclude `KeyboardInterrupt` and `SystemExit`, or use a base exception class.

---

## 📋 REFACTORING PLAN

### Phase 1: Delete Dead Code (Risk: LOW, Effort: LOW)
1. Delete `BasePipeline` class, keep `load_module()` → move to `utils/misc.py`
2. Delete `utils/callback.py` (unused in production)
3. Delete commented-out code in `utils/misc.py` (~115 lines)
4. Delete dead module-level functions in `cfg/__init__.py` (lines ~300-385)
5. Delete `_fs_cache` class variable in `BaseConfig`

### Phase 2: Eliminate Duplicates (Risk: LOW, Effort: MEDIUM)
6. Delete duplicate `RunConfigBuilder` from `utils/config.py` (keep simpler one)
7. Evaluate `ExecutorBuilder`/`AdapterBuilder` — inline if `builder.py` is kept
8. Consolidate `_add_modules_path()` into one utility function
9. Consolidate pipeline name validation to one function
10. Consolidate path traversal validation to one function

### Phase 3: Flatten Over-Abstraction (Risk: MEDIUM, Effort: MEDIUM)
11. Delete `PipelineLifecycleManager` — forward calls to registry
12. Slim `PipelineManager` by removing pure delegation methods (IO, registry)
13. Move Rich rendering out of `PipelineRegistry` to a `PipelinePresenter`
14. Consolidate config loading to single paths

### Phase 4: Simplify Config Layer (Risk: MEDIUM, Effort: HIGH)
15. Remove deprecated flat retry fields from `RunConfig`
16. Remove `Munch` dependency — use plain dicts
17. Decide canonical config loading: `Config` vs `PipelineConfigManager`
18. Simplify `to_dict()` — use `msgspec.to_builtins()` + custom Munch→dict handling

### Phase 5: Fix Bugs (Risk: LOW, Effort: LOW)
19. Fix `PipelineRegistry.delete()` name formatting
20. Fix `FlowerPowerProject.load()` return type
21. Fix `HookType.default_function_name()` match pattern
22. Fix env overlay error swallowing (add logging)
23. Fix `view_img()` temp file race condition
24. Fix mutable default arguments in IO methods

### Phase 6: Performance (Risk: LOW, Effort: LOW)
25. Bound `ExecutorFactory._executor_cache` with LRU
26. Remove redundant `_fs_cache`

### Expected Outcome
- **Lines removed:** ~2,500-3,000 (25-30% reduction)
- **Files removed:** 3-4 (`callback.py`, `base.py`, possibly `lifecycle_manager.py`, `builder_executor.py`, `builder_adapter.py`)
- **Complexity reduction:** God class `PipelineManager` reduced from 1109 to ~300 lines
- **Bug fixes:** 8 confirmed bugs fixed
- **Test coverage:** Current ~2,800 lines of tests; many tests for deleted code can be removed

### Estimated Effort
- Phase 1: 1-2 hours
- Phase 2: 3-4 hours  
- Phase 3: 4-6 hours
- Phase 4: 6-8 hours
- Phase 5: 2-3 hours
- Phase 6: 1 hour
- **Total: ~17-24 hours**

### Testing Strategy
After each phase, run full test suite. Many existing tests test delegation patterns that will change — update tests to match new direct-call patterns. Add regression tests for the 8 bugs found.
