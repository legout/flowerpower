# Processes (`.ruru/processes/`)

This directory contains detailed Standard Operating Procedures (SOPs) and process definitions that describe *how* specific, granular tasks or activities are performed within the workspace, often by specific roles or as part of larger workflows.

Unlike documents in `.ruru/workflows/` which focus on high-level coordination, files here provide the specific step-by-step instructions, algorithms, or procedures (the "how-to").

## Key Processes:

*   **`acqa-process.md`**: Defines the Adaptive Confidence-based Quality Assurance process for reviewing AI-generated artifacts.
*   **`afr-process.md`**: Defines the Adaptive Failure Resolution process for handling recurring errors identified during QA.
*   **`pal-process.md`**: Defines the Process Assurance Lifecycle for creating and validating SOPs and workflows themselves.

## Usage:

*   Workflows defined in `.ruru/workflows/` may reference specific processes documented here.
*   Agents performing tasks should consult relevant process documents for detailed instructions when directed by a workflow or coordinator.
*   New processes should ideally be defined using the SOP template (`.ruru/templates/toml-md/15_sop.md`) or the Enhanced Workflow Boilerplate (`.ruru/templates/workflows/00_workflow_boilerplate.md`) and validated using PAL (`.ruru/processes/pal-process.md`).