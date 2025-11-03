## Why
The library now supports composing multiple pipeline modules at runtime via `additional_modules` (e.g., `pm.run("pipeline_1", additional_modules=["setup"])`). We should document this capability so users can discover how to:
- Combine a setup module with a main pipeline
- Understand import/name resolution rules and precedence
- Visualize composed DAGs with the visualizer

## What Changes
- README
  - Add a dedicated subsection ("Compose Pipelines With Additional Modules") under Python API usage.
  - Provide examples for both `FlowerPowerProject.run` and `PipelineManager.run` using `additional_modules`.
  - Mention conflict resolution/precedence (last module wins) and `reload=True` behavior.
  - Cross-link to example in `examples/hello-world/`.
- API docstrings
  - Ensure `additional_modules` is present and clearly described in `PipelineManager.run(...)` and visualizer methods `save_dag`/`show_dag`.
- Visualizer docs
  - Show how to pass `additional_modules` to render a composite DAG.
- Examples
  - Reference `examples/hello-world/pipelines/setup.py` alongside `hello_world.py` in docs to illustrate a simple composition path.
- CHANGELOG
  - Already updated; verify entry under Unreleased.

Non‑functional/documentation-only change. No API changes.

## Impact
- Files to update:
  - README.md (new subsection, examples)
  - Optionally add a focused guide: `docs/guide/additional-modules.md` (if guide section exists)
  - Verify docstrings for `PipelineManager.run` and `PipelineVisualizer` mention `additional_modules`
  - Ensure example references align with `examples/hello-world/pipelines/setup.py`

## Risks / Considerations
- Avoid implying CLI support if CLI doesn’t accept `additional_modules` yet (call out Python API only).
- Clarify module import resolution attempts (`"name"`, `"name" with '-'→'_'`, and `"pipelines.<name>"`).
- Note that duplicate node names resolve by standard Hamilton semantics (later modules override earlier ones).

## Acceptance Criteria
- README contains a clear "Compose Pipelines With Additional Modules" section with runnable snippets.
- `PipelineManager.run` and visualizer method docstrings mention and describe `additional_modules`.
- Example code snippet(s) reference hello-world’s `setup.py` and `hello_world.py` to demonstrate composition.
- No claims about CLI support unless implemented.
- CHANGELOG reflects feature under Unreleased.

## Archival
This is a docs-only change. After deployment, archive with:
`openspec archive docs-add-additional-modules-usage --skip-specs --yes`

