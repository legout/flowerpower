+++
id = "ROO-CMD-KB-INIT-ACTION-17-V1"
title = "Roo Commander: Initial Action - Create New Custom Mode"
context_type = "kb"
scope = "Procedure for initiating the creation of a new custom Roo mode"
target_audience = ["roo-commander"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-25" # Use current date
tags = ["kb", "initial-action", "mode-creation", "workflow-trigger", "roo-commander"]
related_context = [
    "`.ruru/workflows/WF-NEW-MODE-CREATION-004.md`",
    "`.roo/rules-roo-commander/02-initialization-workflow-rule.md`",
    "`.ruru/modes/roo-commander/kb/available-modes-summary.md`"
]
template_schema_doc = "`.ruru/templates/toml-md/16_ai_rule.README.md`" # Assuming this is the correct schema doc for KB procedures
relevance = "High: Defines the entry point for the custom mode creation workflow"
+++

# Initial Action: Create New Custom Mode

This procedure introduces the workflow for creating a new custom Roo mode and confirms the user is ready to begin. It prepares the user by outlining the process and suggesting information they might want to have ready, before triggering the main mode creation workflow (`WF-NEW-MODE-CREATION-004.md`) which handles the detailed requirements gathering.

**Procedure:**

1.  **Acknowledge Request:** Confirm the user wants to create a new custom mode.
2.  **Introduce Process & Check Readiness:** Use `ask_followup_question` to briefly explain the upcoming steps and confirm the user is ready.
    *   **Question:** "Okay, let's get ready to create a new custom mode! The process involves defining the mode's purpose, gathering context (like relevant files or topics), creating the necessary files, and updating the system. You might want to think about any specific files or documentation that could help define the mode's knowledge base. Are you ready to begin the interactive mode creation workflow?"
    *   **Follow-up Suggestions:**
        *   `<suggest>Yes, let's start the workflow.</suggest>`
        *   `<suggest>No, I need a moment to prepare.</suggest>`
        *   `<suggest>Show me the existing modes first.</suggest>`
3.  **Process User Response:**
    *   **If User selects "Yes, let's start the workflow.":**
        1.  Acknowledge readiness.
        2.  Log the initiation of the workflow (Rule `08`).
        3.  State that you will now initiate the main mode creation workflow (`WF-NEW-MODE-CREATION-004.md`).
        4.  **Proceed to execute Step 1.1 of `.ruru/workflows/WF-NEW-MODE-CREATION-004.md`**. **End this initial action procedure.**
    *   **If User selects "No, I need a moment to prepare.":**
        1.  Acknowledge and inform the user they can restart the process when ready.
        2.  Log the postponement (Rule `08`). **End this initial action procedure.**
    *   **If User selects "Show me the existing modes first.":**
        1.  Use `read_file` to display the contents of `.ruru/modes/roo-commander/kb/available-modes-summary.md`.
        2.  After displaying, return to Step 2 (Readiness Check).
4.  **Error Handling:** If the user repeatedly indicates they are not ready or cannot proceed after being shown existing modes, log the situation and end the procedure.

**Next Step:** Upon user confirmation, the main workflow `.ruru/workflows/WF-NEW-MODE-CREATION-004.md` is triggered starting at Step 1.1.