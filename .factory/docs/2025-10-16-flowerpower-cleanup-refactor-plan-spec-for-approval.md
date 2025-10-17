# Cleanup & Refactor Plan (Spec for Approval)

I’ll create a cleanup branch, audit and prune dead code, fix two safe bugs, and propose conservative refactors with zero public API breakage. Below are the findings and the exact Markdown files I’ll add; after approval I’ll create the branch and commit them before any code changes.

## Branching
- Note: gh does not provide a native “create branch” command. Plan:
  - Create local branch: `git switch -c chore/cleanup-refactor`
  - Push and set upstream: `git push -u origin chore/cleanup-refactor`
  - Use gh for PR later: `gh pr create --fill --draft`

## Public API surface (do not break)
- Exposed in `src/flowerpower/__init__.py`:
  - `FlowerPower`, `FlowerPowerProject`, `create_project`, `PipelineManager`, `Config`, `ProjectConfig`, `PipelineConfig`, `__version__`
- All refactors will preserve import paths and behavior; deletions target internal, unused, or empty artifacts only.

## Safe-to-delete items (no references in repo; not imported in public API)
- Files/dirs:
  - `src/flowerpower/_settings.py` — superseded by `flowerpower.settings.*`; no references found.
  - `src/flowerpower/settings/_backend.py` — not imported anywhere; dead data mapping.
  - `src/flowerpower/plugins/mqtt/` (empty dir) — no package, no code.
  - `src/flowerpower/plugins/io/helpers/` (empty dir) — no code.
  - `src/flowerpower/utils/monkey.py` — placeholder only; no references.
- Deprecated but keep for now:
  - `src/flowerpower/plugins/io/__init__.py` — emits DeprecationWarning guiding to external `flowerpower-io`; keep through next minor, remove in next major.

## Safe bug fixes (no API change)
- `src/flowerpower/pipeline/pipeline.py`
  - Duplicate imports of `requests.exceptions` — remove duplicates.
  - Uninitialized variable in executor path:
    - Current:
      ```python
      if (run_config.executor.type != "synchronous" or run_config.executor.type == "local"):
          allow_experimental_mode = True
          synchronous_executor = False
      else:
          allow_experimental_mode = True
      # later: if not synchronous_executor: ...  # can raise UnboundLocalError
      ```
    - Fix:
      ```python
      synchronous_executor = True
      if run_config.executor.type not in ("synchronous", None):
          synchronous_executor = False
      allow_experimental_mode = True
      ```
- `src/flowerpower/pipeline/io.py`
  - `_print_export_success` is recursively calling itself instead of printing; replace with a single console print that handles both cases.

## Refactoring opportunities (conservative)
- Pipeline execution path: simplify the executor/experimental-mode branching as above; no behavior change.
- Minor hygiene
  - Remove unused imports and duplicated imports across modules.
  - Prefer consistent logging over ad-hoc prints in internal helpers (keep CLI-facing rich prints unchanged).
  - Keep deprecation bridges in place (retry fields mapping, plugins/io warning).

## Validation and Safety
- Run and keep green:
  - `pytest -q`
  - `ruff --fix .` (non-invasive fixes only)
  - `mypy` (adjust only if fixes introduce type errors)
- No public API moves/renames. Any internal deletions are strictly unreferenced.

---

# Files I will add (Markdown)

## docs/cleanup-refactor-plan.md
```markdown
# FlowerPower Cleanup & Refactor Plan

## Goals
- Remove dead/unused code and empty directories without breaking public API.
- Fix minor defects that can fail at runtime.
- Improve code hygiene (imports, simple branching) while preserving behavior.

## Non-Goals
- No new features, no architecture shifts, no API changes.

## Public API to preserve
- `flowerpower.__init__` exports: FlowerPower, FlowerPowerProject, create_project, PipelineManager, Config, ProjectConfig, PipelineConfig, __version__.

## Safe-to-delete (now)
- src/flowerpower/_settings.py — superseded, zero references.
- src/flowerpower/settings/_backend.py — unused mapping, zero references.
- src/flowerpower/plugins/mqtt/ — empty directory.
- src/flowerpower/plugins/io/helpers/ — empty directory.
- src/flowerpower/utils/monkey.py — placeholder, zero references.

## Deprecated (keep, remove next major)
- src/flowerpower/plugins/io/__init__.py — warns and forwards users to external package.

## Safe fixes
1) pipeline/pipeline.py
- Remove duplicate `requests.exceptions` imports.
- Initialize `synchronous_executor` for the synchronous path:
```python
synchronous_executor = True
if run_config.executor.type not in ("synchronous", None):
    synchronous_executor = False
allow_experimental_mode = True
```

2) pipeline/io.py
- Replace recursive `_print_export_success` with a single print, e.g.:
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

## Refactoring (no behavior change)
- Remove unused/duplicate imports across modules.
- Keep deprecation bridges (retry fields) intact; do not alter CLI interfaces.
- Minor branch simplifications where they only affect internal flags.

## Risks and Mitigations
- Risk: hidden external imports of internal utils.
  - Mitigation: only delete files with zero internal references and not imported by package __init__.
- Risk: subtle behavior change in execution path.
  - Mitigation: add/keep unit tests around synchronous vs remote executors; run full test suite.

## Acceptance Criteria
- All tests pass; no new warnings beyond the existing deprecation for plugins/io.
- mypy clean on touched modules; ruff clean with autofixes limited to import/order/whitespace.
- Public API imports remain unchanged.
```

## docs/cleanup-tasks.md
```markdown
# Cleanup Tasks (Step-by-Step)

## 1. Branch and scaffold
- [ ] Create branch: `git switch -c chore/cleanup-refactor` and push with `git push -u origin chore/cleanup-refactor`
- [ ] Commit this plan and tasks markdown

## 2. Safe deletions (no code change risk)
- [ ] Remove `src/flowerpower/_settings.py`
- [ ] Remove `src/flowerpower/settings/_backend.py`
- [ ] Remove empty dir `src/flowerpower/plugins/mqtt/`
- [ ] Remove empty dir `src/flowerpower/plugins/io/helpers/`
- [ ] Remove `src/flowerpower/utils/monkey.py`

## 3. Safe bug fixes
- [ ] Fix `pipeline/pipeline.py` executor branching and duplicate imports
- [ ] Fix `pipeline/io.py` `_print_export_success` recursion

## 4. Hygiene
- [ ] Remove unused/duplicate imports (ruff --fix)
- [ ] Ensure no behavior changes in logs/prints

## 5. Validation
- [ ] Run tests: `pytest -q`
- [ ] Run typecheck: `mypy`
- [ ] Run lint: `ruff .`

## 6. PR
- [ ] `gh pr create --fill` (or `--draft`) and request review
```

---

If you approve, I’ll create the branch, add these Markdown files, then proceed with the safe deletions and fixes while keeping tests and type checks green.