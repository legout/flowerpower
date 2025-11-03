## 1. Implementation
- [x] 1.1 Add `additional_modules` to `RunConfig` (list[str] | None)
- [x] 1.2 Extend kwargs merge to support `additional_modules` (merge + dedupe)
- [x] 1.3 Runner: resolve additional modules (string or module) and call `.with_modules(*modules)`
- [x] 1.4 Reload logic: reload all additional modules when `reload=True`
- [x] 1.5 PipelineManager.run docs: document `additional_modules`
- [x] 1.6 (Optional) Visualizer: accept `additional_modules` to render composite DAG

## 2. Tests
- [x] 2.1 Runner passes multiple modules to Builder (sync)
- [x] 2.2 Runner passes multiple modules to Builder (async)
- [x] 2.3 Import resolution: string success and helpful ImportError on failure
- [x] 2.4 Reload reloads all modules
- [x] 2.5 Config merge: kwargs + config `additional_modules` merge and dedupe

## 3. Docs & Release
- [x] 3.1 README usage example (`pm.run("pipeline_1", additional_modules=["setup"])`)
- [x] 3.2 CHANGELOG entry under Added
- [ ] 3.3 Version bump as needed
