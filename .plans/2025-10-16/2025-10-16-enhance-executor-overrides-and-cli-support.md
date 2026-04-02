# Proposal: Improve ExecutorConfig selection and overrides (change-id: enhance-executor-overrides)

## Current behavior (from code analysis)
- ExecutorConfig fields: type | max_workers | num_cpus (defaults from settings: threadpool, cpu*5, cpu count).
- Selecting synchronous executor works now:
  - YAML: run.executor.type: "synchronous"
  - Python: executor_cfg="synchronous" or ExecutorConfig(type="synchronous")
  - Pipeline uses SynchronousLocalTaskExecutor when type in {None, "synchronous"}; otherwise sets a remote executor (threadpool/processpool/ray/dask) created by ExecutorFactory.
- Runtime overrides vs YAML:
  - Python/REPL: pass executor_cfg (str|dict|ExecutorConfig) via kwargs; merge_run_config_with_kwargs sets run_config.executor; Pipeline._get_executor merges pipeline YAML defaults with provided executor (ExecutorConfig.merge) and then builds the executor using ExecutorFactory.
  - CLI: can only override executor type via --executor; there is no flag to pass max_workers/num_cpus or an executor config object, so advanced overrides are not possible from CLI.
- Merge caveat: BaseConfig.merge treats a source field as “default” when equal to class default; thus if a user sets max_workers to the class default value, it won’t override YAML. Also, None in source is considered non-default for explicit-default fields and will override to None.

## Gaps / issues
1. CLI lacks a way to pass executor parameters (max_workers/num_cpus) or a JSON executor config.
2. Merge semantics can be surprising: user-provided values equal to class defaults don’t override YAML; None overrides even when likely unintended.
3. Minor doc inconsistency: references to "local"/"distributed" vs implemented types {synchronous, threadpool, processpool, ray, dask}.

## Goals
- Allow full executor overrides via CLI, matching Python API capabilities.
- Make merge semantics predictable: user-provided executor fields (via REPL/CLI) should take precedence over YAML, even when equal to class defaults; None should not override unless explicitly requested.
- Keep synchronous behavior unchanged and clearly selectable.

## Spec (delta)
### ADDED Requirements
- CLI pipeline run accepts executor configuration:
  - --executor-cfg: JSON/dict string with keys {type, max_workers, num_cpus}.
  - Convenience flags: --executor-max-workers INT, --executor-num-cpus INT (optional sugar; merged into executor-cfg if provided).
- Validation: reject executor types not in {synchronous, threadpool, processpool, ray, dask}; error out with clear message.

### MODIFIED Requirements
- Merge precedence for executor:
  - When runtime executor_cfg is provided (via REPL/CLI), its non-missing fields override YAML executor fields regardless of whether they equal class defaults.
  - Treat None as “missing” for override purposes by default (i.e., do not overwrite YAML with None unless the user passed it explicitly in a dict).
- Pipeline._get_executor merging updated to prefer explicit runtime values; YAML remains fallback.
- CLI pipeline.run maps new flags into RunConfig.executor consistently with Python API.

### REMOVED Requirements
- None.

## Design notes
- Keep ExecutorFactory unchanged; only adjust how ExecutorConfig is composed.
- Implement a targeted merge for ExecutorConfig (prefer_source semantics):
  - For each field in override: if key present and value is not msgspec.MISSING (and not None unless explicitly provided in dict), set it on a copy of YAML ExecutorConfig.
  - Distinguish between “field omitted” vs “explicitly set to None” by how we build the override struct from dict; explicit dict None should override to None, but builder-created struct default-None should be treated as missing.
- CLI parsing: extend pipeline.run to accept --executor-cfg; parse JSON/dict; apply convenience flags after parsing.

## Minimal code changes (illustrative snippets)
- Update Pipeline._get_executor merging:
```python
# before
executor_cfg = self.config.run.executor.merge(executor_cfg)
# after (helper prefers explicit override values)
executor_cfg = prefer_executor_override(self.config.run.executor, executor_cfg)
```
- New helper (utils/config.py):
```python
def prefer_executor_override(base: ExecutorConfig, override: ExecutorConfig|dict|str|None) -> ExecutorConfig:
    if override is None:
        return base
    if isinstance(override, str):
        override = ExecutorConfig(type=override)
    if isinstance(override, dict):
        override = ExecutorConfig.from_dict(override)
    merged = ExecutorConfig(
        type = override.type if override.type is not None else base.type,
        max_workers = override.max_workers if override.max_workers is not None else base.max_workers,
        num_cpus = override.num_cpus if override.num_cpus is not None else base.num_cpus,
    )
    return merged
```
- CLI additions (cli/pipeline.py):
```python
executor_cfg: str|None = typer.Option(None, help="Executor config as JSON/dict")
executor_max_workers: int|None = typer.Option(None)
executor_num_cpus: int|None = typer.Option(None)
# parse and apply
parsed_exec_cfg = parse_dict_or_list_param(executor_cfg, "dict") or {}
if executor is not None:
    parsed_exec_cfg["type"] = executor
if executor_max_workers is not None:
    parsed_exec_cfg["max_workers"] = executor_max_workers
if executor_num_cpus is not None:
    parsed_exec_cfg["num_cpus"] = executor_num_cpus
if parsed_exec_cfg:
    run_config.executor = ExecutorConfig.from_dict(parsed_exec_cfg)
```

## Validation plan
- Unit tests:
  - Selecting synchronous via YAML, REPL (executor_cfg="synchronous"), and CLI (executor or executor-cfg) yields SynchronousLocalTaskExecutor; nodes run sequentially.
  - CLI overrides for max_workers/num_cpus create the expected Hamilton executors with parameters.
  - Merge precedence: REPL/CLI values override YAML even when equal to class defaults; None in override does not clobber YAML unless explicitly provided via dict.
  - Invalid executor type -> CLI and Python raise clear error.
- Backward compatibility: no behavior changes unless new flags used; existing flows remain.

## Tasks
1. Add prefer_executor_override helper and use it in Pipeline._get_executor; keep existing behavior for other config fields.
2. Extend CLI pipeline.run with --executor-cfg, --executor-max-workers, --executor-num-cpus; wire into RunConfig.executor.
3. Add validation of executor type at CLI (reuse utils.security.validate_executor_type where appropriate).
4. Tests: REPL override precedence, CLI overrides, synchronous selection paths, invalid type errors.
5. Update minimal docs/CLI help strings (no README changes unless requested later).
