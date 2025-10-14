# Proposal: Sync Docs with Code (CLI + API)

## Summary
Bring the mkdocs documentation in `docs/docs` back in sync with the single source of truth (`src/flowerpower`). Focus scope: public Python API (FlowerPowerProject, create_project/initialize_project, PipelineManager) and CLI (`flowerpower` and `flowerpower pipeline` commands).

## Rationale
Several user-facing docs are out of date or inaccurate vs. current code. Key risks include incorrect function signatures, wrong option types/defaults, and behavior mismatches that mislead users. Aligning docs reduces support issues and improves onboarding.

## Scope
- Update CLI reference pages: `docs/docs/api/cli.md`, `docs/docs/api/cli_pipeline.md`.
- Update API reference pages: `docs/docs/api/flowerpower.md`, `docs/docs/api/flowerpowerproject.md`, `docs/docs/api/pipelinemanager.md`.
- Leave architecture, quickstart, and advanced docs unchanged unless accuracy issues are found incidentally.

## Non-Goals
- Do not change code behavior; fix docs to match code. Note any code/doc conflicts separately for follow-up.

## Risks / Open Questions
- The CLI subcommands `show_pipelines` and `save_dag` appear to pass arguments not supported by the underlying manager methods. We will document the current CLI surface but call out known inconsistencies in a “Notes” section until code is fixed.

