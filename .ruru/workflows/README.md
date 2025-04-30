# Workflows (`.ruru/workflows/`)

This directory contains documents defining **high-level, multi-phase workflows**. These workflows typically describe sequences of activities involving coordination between multiple agent roles (e.g., Coordinator, Developer, Reviewer, User) to achieve a significant project goal.

Workflows focus on the **overall orchestration and flow** of tasks, decisions, and information. They may reference more detailed procedures or SOPs documented in the `.ruru/processes/` directory.

## Key Workflows:

*   **`new_mode_creation_workflow.md`**: Defines the interactive process for creating a new Roo Commander mode from scratch, involving user input, context gathering, generation, QA, and refinement.

## Usage:

*   Consult these documents to understand the standard sequence for complex operations.
*   The Coordinator role (e.g., `Roo Commander`) typically orchestrates the execution of these workflows.
*   New workflows should ideally be defined using the Enhanced Workflow Boilerplate (`.templates/workflows/00_workflow_boilerplate.md`) and validated using PAL (`.ruru/processes/pal-process.md`).