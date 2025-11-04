## Why
FlowerPower now supports true asynchronous execution via Hamilton’s async driver (`hamilton.async_driver`). The documentation in `docs/` needs a clear, discoverable guide that explains how to run pipelines asynchronously, what the requirements are, and how this differs from synchronous execution.

## What Changes
- Add a new guide page focused on async execution (proposed: `docs/docs/guide/async-execution.md`).
  - Explain the `PipelineManager.run_async(...)` API, the `RunConfig.async_driver` toggle, and behaviour parity with sync (`reload`, adapters, logging).
  - Show working examples with and without `additional_modules`.
  - Document prerequisites: Hamilton version providing `hamilton.async_driver`.
  - Troubleshooting section for common issues (missing async driver, event loop usage, executor considerations).
- Update navigation in `docs/mkdocs.yml` under “Guides” to include the new page.
- Cross-link from existing pages where appropriate (e.g., Advanced Usage) to the new guide.
- Ensure CHANGELOG references the new async capability (already added; verify).

## Impact
- Files to update or add:
  - Add: `docs/docs/guide/async-execution.md` (new page)
  - Update: `docs/mkdocs.yml` (nav entry)
  - Optional updates: link from `docs/docs/advanced.md` or `docs/docs/index.md` to the new guide

## Risks / Considerations
- Avoid implying CLI parity if CLI subcommands do not expose async-specific flags.
- Clarify that `pipelines` code must be compatible with async contexts; blocking IO will block the event loop unless executed via remote executors.
- Note Hamilton version requirement; provide upgrade guidance.

## Acceptance Criteria
- A dedicated async execution guide exists in `docs/` with code examples using `PipelineManager.run_async`.
- The new guide appears in the site navigation.
- The guide links to the additional-modules documentation where relevant, and vice versa when useful.
- Local docs build (`mkdocs build -f docs/mkdocs.yml`) succeeds without new broken links.

