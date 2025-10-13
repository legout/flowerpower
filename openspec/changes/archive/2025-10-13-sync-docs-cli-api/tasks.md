1. [x] Audit CLI docs vs code (init, ui, pipeline subcommands)
2. [x] Audit API docs vs code (FlowerPowerProject, create_project, initialize_project, PipelineManager)
3. [x] Update `docs/docs/api/cli.md` with accurate option types/defaults/examples
4. [x] Update `docs/docs/api/cli_pipeline.md` to match actual subcommand signatures
5. [x] Update `docs/docs/api/flowerpower.md` (create_project behavior; alias note)
6. [x] Update `docs/docs/api/flowerpowerproject.md` (attributes; load/new signatures/behavior)
7. [x] Update `docs/docs/api/pipelinemanager.md` (methods, signatures, properties)
8. [x] Build docs locally to validate rendering (mkdocs build)
9. [x] Sanity-run selected CLI help (`flowerpower --help`) and cross-check
10. [x] Capture known code/doc inconsistencies in a Notes section for follow-up

Validation
- mkdocs build passes without warnings/errors
- Spot-check examples compile or reflect real function signatures
- CLI `--help` text matches documented options/types/defaults
