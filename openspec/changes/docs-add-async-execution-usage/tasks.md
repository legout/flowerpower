## 1. Documentation Updates
- [x] 1.1 Create `docs/docs/guide/async-execution.md` with:
  - Overview of async execution and when to use it
  - Example using `PipelineManager.run_async` (with `additional_modules` example)
  - Notes on `RunConfig.async_driver` semantics (default behaviour, opting out)
  - Parity with sync: logging, reload, adapters
  - Prerequisites: Hamilton version with `hamilton.async_driver`
  - Troubleshooting (missing driver ImportError, event loop tips)
- [x] 1.2 Update `docs/mkdocs.yml` to add the new guide to nav under Guides.
- [x] 1.3 (Optional) Add cross-links in `docs/docs/advanced.md` or `docs/docs/index.md` to the new guide.
- [x] 1.4 Verify CHANGELOG entry for async execution exists.

## 2. Validation
- [x] 2.1 Build the docs locally: `mkdocs build -f docs/mkdocs.yml`.
- [ ] 2.2 Fix any new warnings or broken links. *(Existing warnings predate this change and will be handled separately.)*

## 3. Rollout
- [ ] 3.1 Submit PR for review.
- [ ] 3.2 After merge/deploy, archive this change with `openspec archive docs-add-async-execution-usage --skip-specs --yes`.
