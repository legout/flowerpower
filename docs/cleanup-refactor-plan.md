# FlowerPower Cleanup & Refactor Plan

## Goals
- Remove dead/unused code and empty directories without breaking public API.
- Fix minor defects that can fail at runtime.
- Improve code hygiene (imports, simple branching) while preserving behavior.

## Non-Goals
- No new features, no architecture shifts, no API changes.

## Public API to preserve
- Exports from `flowerpower.__init__`:
  - `FlowerPower`, `FlowerPowerProject`, `create_project`, `PipelineManager`, `Config`, `ProjectConfig`, `PipelineConfig`, `__version__`.

## Safe-to-delete (now)
- `src/flowerpower/_settings.py` — superseded by `flowerpower.settings.*`; zero references.
- `src/flowerpower/settings/_backend.py` — unused mapping; zero references.
- `src/flowerpower/plugins/mqtt/` — empty directory.
- `src/flowerpower/plugins/io/helpers/` — empty directory.
- `src/flowerpower/utils/monkey.py` — placeholder only; zero references.

## Deprecated (keep; remove next major)
- `src/flowerpower/plugins/io/__init__.py` — emits DeprecationWarning directing to external `flowerpower-io`.

## Safe fixes (no behavior change)
1) `src/flowerpower/pipeline/pipeline.py`
   - Remove duplicate `requests.exceptions` imports.
   - Initialize `synchronous_executor` for the synchronous path to avoid UnboundLocalError:
     ```python
     synchronous_executor = True
     if run_config.executor.type not in ("synchronous", None):
         synchronous_executor = False
     allow_experimental_mode = True
     ```

2) `src/flowerpower/pipeline/io.py`
   - Fix `_print_export_success` recursion by printing directly:
     ```python
     def _print_export_success(self, names: list[str] | None, dest_base_dir: str) -> None:
         if names:
             console.print(
                 f"✅ Exported pipelines [bold blue]{', '.join([self.project_cfg.name + '.' + n for n in names])}[/bold blue] to [green]{dest_base_dir}[/green]"
             )
         else:
             console.print(
                 f"✅ Exported all pipelines from [bold blue]{self.project_cfg.name}[/bold blue] to [green]{dest_base_dir}[/green]"
             )
     ```

## Refactoring (conservative)
- Remove unused/duplicate imports across modules.
- Keep deprecation bridges (retry fields mapping, plugins/io warning) intact.
- Minor branch simplifications that don’t change behavior.

## Risks and Mitigations
- Hidden external imports of internal utils.
  - Only delete files with zero internal references and not exposed by package `__init__`.
- Subtle behavior change in execution path.
  - Keep/extend unit tests around executor selection; run full test suite.

## Acceptance Criteria
- All tests pass; no new warnings beyond the existing deprecation for `plugins/io`.
- `mypy` clean on touched modules; `ruff` clean with autofixes limited to imports/order/whitespace.
- Public API imports remain unchanged.
