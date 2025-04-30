+++
id = "ROO-CMD-RULE-DOC-CREATION-V1"
title = "Roo Commander: Rule - Workflow & Process Document Creation"
context_type = "rules"
scope = "Procedure for creating new Workflow or Process (SOP) documents"
target_audience = ["roo-commander"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-21" # Assuming today's date
tags = ["rules", "workflow", "process", "sop", "creation", "documentation", "indexing", "roo-commander"]
related_context = ["01-operational-principles.md", "12-logging-procedures.md", ".ruru/templates/workflows/00_workflow_boilerplate.md", ".ruru/templates/toml-md/15_sop.md", ".ruru/workflows/", ".ruru/processes/", ".ruru/modes/roo-commander/kb/10-standard-processes-index.md", ".ruru/modes/roo-commander/kb/11-standard-workflows-index.md"]
+++

# Rule: Workflow & Process Document Creation

This rule outlines when and how Roo Commander should initiate the creation of new **Workflow** documents (high-level, multi-role sequences stored in `.ruru/workflows/`) or **Process** documents (granular, repeatable SOPs stored in `.ruru/processes/`).

**Procedure:**

1.  **Identify Need:** Determine that a new high-level workflow or a specific, repeatable process needs to be formally documented based on:
    *   User request.
    *   Analysis identifying a recurring, undocumented procedure.
    *   Need to standardize a complex or critical operation.

2.  **Distinguish Type:**
    *   **Workflow:** Is it a high-level, end-to-end sequence involving multiple roles or phases? (e.g., Project Onboarding, Build Process). Use Workflow Template.
    *   **Process (SOP):** Is it a more granular, step-by-step procedure for a specific, repeatable task, often within a single role's domain? (e.g., Running Linters, Creating MDTM Task File). Use SOP Template.

3.  **Select Boilerplate:**
    *   **For Workflows:** Copy `.ruru/templates/workflows/00_workflow_boilerplate.md`.
    *   **For Processes (SOPs):** Copy `.ruru/templates/toml-md/15_sop.md`.

4.  **Define Core Metadata & Content (Initial Draft):**
    *   Initiate the drafting process (either directly or by delegating to `util-writer` if complex content generation is needed).
    *   Fill in essential TOML metadata: `id`, `title`, `objective`, `scope`.
    *   Outline the core steps in the Markdown body.

5.  **Save Draft & Validate:**
    *   Save the initial draft (e.g., in `.ruru/planning/`).
    *   **Recommend PAL:** Propose applying the Process Assurance Lifecycle (PAL) as defined in `.ruru/processes/pal-process.md` for review and simulation before finalizing.

6.  **Finalize & Store:** Once validated (e.g., via PAL and/or user approval):
    *   Ensure all TOML metadata is complete and accurate.
    *   Ensure Markdown body details are correct.
    *   Determine the correct final directory: `.ruru/workflows/` for Workflows, `.ruru/processes/` for Processes.
    *   Use `write_to_file` to save the final version to the correct location with a descriptive filename.
    *   If a draft existed in `.ruru/planning/`, use `execute_command rm` to remove it.

7.  **Update Index File:** **Crucially**, after saving the final document:
    *   **For Workflows:** Update `.ruru/modes/roo-commander/kb/11-standard-workflows-index.md`.
    *   **For Processes (SOPs):** Update `.ruru/modes/roo-commander/kb/10-standard-processes-index.md`.
    *   Use `apply_diff` or `insert_content` to add a new bullet point referencing the newly created document path.

8.  **Log Creation:** Log the creation of the new document and the update to the index file according to Rule `12`.

**Key Objective:** To ensure new workflows and processes are created using standard templates, stored in the correct location, validated before activation, and indexed for discoverability.