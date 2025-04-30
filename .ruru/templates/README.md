# Templates (`.templates/`)

This directory serves as the central repository for standardized templates used throughout the workspace. Using templates ensures consistency and provides a starting point for creating various project artifacts.

## Template Subdirectories:

*   **`modes/`**: Contains templates and specifications related to defining Roo Commander custom modes (v7.1+ structure). Includes the base template (`example_mode_template/mode.md`) and the core specification (`mode_specification.md`).
*   **`toml-md/`**: Contains general-purpose TOML+Markdown templates for various document types like MDTM tasks, ADRs, documentation, simple SOPs, etc. See `.templates/toml-md/README.md` for a detailed list and usage instructions.
*   **`workflows/`**: Contains templates for defining complex, multi-step workflows or detailed SOPs, typically involving multiple agents and phases. Includes the `00_workflow_boilerplate.md`. Documents created from these templates usually reside in the root `.workflows/` or `.processes/` directories.
*   **(Future)** `processes/`: Could potentially hold templates specifically for documents intended for the root `.processes/` directory if they differ significantly from workflow templates.

## Usage:

When creating a new artifact (mode, task, ADR, workflow, process, doc), first identify the appropriate template from these subdirectories. Copy the template to the target location (e.g., `.tasks/`, `.decisions/`, `.workflows/`, `v7.1/modes/...`) and populate it according to the instructions within the template and relevant specifications or rules.