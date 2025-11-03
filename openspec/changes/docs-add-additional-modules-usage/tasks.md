## 1. Documentation Updates
- [x] 1.1 README: add "Compose Pipelines With Additional Modules" section with examples for `project.run(...)` and `pm.run(...)` using `additional_modules=["setup"]`.
- [x] 1.2 README: document precedence (last module passed wins on duplicate node names) and `reload=True` behavior (reloads all loaded modules).
- [x] 1.3 Visualizer docs: show `additional_modules` usage in `save_dag`/`show_dag` examples.
- [x] 1.4 Cross-reference examples: highlight `examples/hello-world/pipelines/setup.py` with `hello_world.py` for composition.
- [x] 1.5 API docstrings: verify/expand `additional_modules` param documentation in `PipelineManager.run` and `PipelineVisualizer` methods.
- [x] 1.6 Confirm CHANGELOG Unreleased entry includes this feature.

## 2. Optional Guides (if docs site in use)
- [ ] 2.1 Create `docs/guide/additional-modules.md` with deeper explanation (import resolution, tips, troubleshooting, best practices).

## 3. Validation
- [x] 3.1 Render README locally to verify code blocks and formatting.
- [ ] 3.2 (If docs site) run docs build locally to ensure no broken links.

## 4. Rollout
- [ ] 4.1 Submit PR for review.
- [ ] 4.2 After merge/deploy, archive change with `openspec archive docs-add-additional-modules-usage --skip-specs --yes`.
