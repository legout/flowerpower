---
id: flo-j1kp
status: open
deps: []
links: [flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:config, component:deps, kiss]
---
# Remove Munch dependency — use plain dicts consistently

## Task
Replace all `Munch` usage with plain `dict` to eliminate type confusion and reduce dependencies.

## Context
`Munch` (dot-access dicts) is used inconsistently across the config layer:
- `RunConfig.config` — converted to Munch in `__post_init__`
- `RunConfig.cache` — conditionally converted to Munch
- `PipelineConfig.params` and `h_params` — converted to Munch
- `Config.storage_options` — stored as Munch

Most other parts of the codebase use plain dicts. This means callers sometimes receive `Munch`, sometimes `dict`, sometimes `msgspec.Struct` — depending on which code path was taken. Type checkers can't reason about Munch, and it adds cognitive overhead.

The only benefit Munch provides is `config.some_key` syntax instead of `config["some_key"]`. Hamilton's own config system accepts plain dicts.

## Acceptance Criteria
- [ ] `munch` removed from `pyproject.toml` dependencies.
- [ ] All `munchify()` calls replaced with plain dict construction or removed.
- [ ] `to_h_params()` in `PipelineConfig` returns plain dicts (already does, but callers may expect Munch).
- [ ] `Config.storage_options` changed from `Munch` to `dict`.
- [ ] `BaseConfig.to_dict()` simplified — no more `_convert_dict_recursively` for Munch handling (use `msgspec.to_builtins()` instead).
- [ ] `PipelineConfig.update()` works with plain dicts.
- [ ] All tests pass without Munch.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #13, #25

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `munch` still in dependencies and used in 20+ locations:
  - `pipeline/manager.py` — `from munch import Munch`
  - `pipeline/base.py` — `from munch import Munch`
  - `cfg/pipeline/run.py` — `from munch import munchify` (lines 318, 320)
  - `cfg/pipeline/adapter.py` — `from munch import munchify` (lines 24, 38, 40)
  - `cfg/pipeline/__init__.py` — `from munch import Munch, munchify` (lines 56, 57, 103, 162, 168)
