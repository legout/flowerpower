+++
# --- Basic Metadata ---
id = "WF-ADD-MODE-CONTEXT-001"
title = "Workflow: Add Context File to Mode KB"
status = "active"
created_date = "2025-04-19"
updated_date = "2025-04-19"
version = "1.0"
tags = ["workflow", "sop", "modes", "kb", "context", "documentation", "rules"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
  ".ruru/rules/01-standard-toml-md-format.md", # Context files should ideally follow this
  ".ruru/docs/standards/project_structure_inventory.md", # Explains .modes/<slug>/kb structure
  ".ruru/templates/toml-md/08_ai_context_source.md" # Recommended template for context files
]
related_templates = [".ruru/templates/toml-md/08_ai_context_source.md"]

# --- Workflow Specific Fields ---
objective = "To add a new context file (e.g., rule, guideline, best practice) to a specified mode's Knowledge Base (KB) directory and update the corresponding KB README file."
scope = "Applies when adding new, distinct pieces of context information as separate files within an existing mode's `.ruru/modes/<slug>/kb/` directory."
roles = ["Coordinator (Roo Commander)", "Worker Agent (e.g., `util-writer`, `util-mode-maintainer`)"]
trigger = "User request to add specific context information to a mode's KB."
success_criteria = [
  "New context file is created in the correct mode's KB directory (`.ruru/modes/<slug>/kb/<filename>.md`).",
  "The context file contains the specified content, ideally using the AI Context Source template.",
  "The mode's KB README (`.ruru/modes/<slug>/kb/README.md`) is updated to list the new file with a brief description.",
  "Worker Agent confirms successful completion."
]
failure_criteria = [
  "Coordinator cannot determine the target mode slug or KB path.",
  "Worker Agent fails to write the new context file.",
  "Worker Agent fails to update the KB README file.",
  "Content of the created/updated files is incorrect."
]

# --- Integration ---
acqa_applicable = false # Primarily documentation/context creation
pal_validated = true # Conceptually validated
validation_notes = "Simple workflow involving file creation and update."

# --- AI Interaction Hints (Optional) ---
# context_type = "workflow_definition"
+++

# Workflow: Add Context File to Mode KB

## 1. Objective 🎯
*   To add a new context file (e.g., rule, guideline, best practice) to a specified mode's Knowledge Base (KB) directory (`.ruru/modes/<slug>/kb/`) and update the corresponding KB README file.

## 2. Scope ↔️
*   Applies when adding new, distinct pieces of context information as separate files within an existing mode's `.ruru/modes/<slug>/kb/` directory. Does not cover major refactoring of existing KB files.

## 3. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Gathers requirements (target mode, content, filename), delegates file creation and README update, verifies completion.
*   **Worker Agent (e.g., `util-writer`, `util-mode-maintainer`):** Creates the new context file and updates the KB README based on Coordinator's instructions.

## 4. Preconditions🚦
*   The target mode's directory structure (`.ruru/modes/<slug>/kb/`) exists.
*   The target mode's KB README (`.ruru/modes/<slug>/kb/README.md`) exists.
*   The Coordinator has the content for the new context file (either provided by the user or generated).
*   The Coordinator has determined a suitable filename for the new context file (e.g., `NN-topic-summary.md`).

## 5. Reference Documents & Tools 📚🛠️
*   `.ruru/modes/<slug>/kb/`: Target directory.
*   `.ruru/modes/<slug>/kb/README.md`: Target README file.
*   `.ruru/templates/toml-md/08_ai_context_source.md`: Recommended template for the new context file.
*   `write_to_file`: Tool to create the new context file.
*   `apply_diff` / `search_and_replace`: Tools to update the KB README.
*   `read_file`: Tool for Coordinator to verify changes (optional).

## 6. Workflow Steps 🪜

*   **Step 1: Gather Requirements (Coordinator Task)**
    *   **Description:** Identify the target mode, the content for the new context file, and a suitable filename.
    *   **Inputs:** User request specifying the mode and the context to add.
    *   **Procedure:**
        *   Confirm the target mode slug (e.g., `roo-commander`).
        *   Determine the full path to the KB directory (e.g., `.ruru/modes/roo-commander/kb/`).
        *   Determine an appropriate filename (e.g., `10-adding-context-files-rule.md`). Ensure numbering follows existing KB convention if applicable.
        *   Obtain or formulate the content for the new file. Recommend using the `.ruru/templates/toml-md/08_ai_context_source.md` structure for the content.
    *   **Outputs:** Target mode slug, KB directory path, new filename, file content.

*   **Step 2: Delegate Context File Creation (Coordinator delegates to Worker Agent)**
    *   **Description:** Create the new context file in the target mode's KB directory.
    *   **Tool:** `new_task` (delegating to e.g., `util-writer`)
    *   **Inputs Provided by Coordinator:**
        *   Full path for the new file (e.g., `.ruru/modes/roo-commander/kb/10-adding-context-files-rule.md`).
        *   Complete content for the new file.
    *   **Instructions for Delegate:** "Using `write_to_file`, create a new file at the specified path with the provided content."
    *   **Expected Output from Delegate:** Confirmation of successful file creation.
    *   **Coordinator Action (Post-Delegation):** Wait for confirmation.
    *   **Error Handling:** If the delegate fails, analyze the error. Check path validity, content format, and permissions. Retry or report to user.

*   **Step 3: Delegate KB README Update (Coordinator delegates to Worker Agent)**
    *   **Description:** Add an entry for the new context file to the target mode's KB README.
    *   **Tool:** `new_task` (delegating to e.g., `util-writer`)
    *   **Inputs Provided by Coordinator:**
        *   Path to the KB README (e.g., `.ruru/modes/roo-commander/kb/README.md`).
        *   Filename of the newly created context file (e.g., `10-adding-context-files-rule.md`).
        *   A brief description of the new file's content.
    *   **Instructions for Delegate:** "Using `apply_diff` or `search_and_replace`, update the specified KB README file. Add a new bullet point to the list of KB files, including the new filename and the provided description. Ensure the list remains properly formatted." (Consider instructing to insert before a specific line, like a 'Miscellaneous' section or just before the end marker, if applicable).
    *   **Expected Output from Delegate:** Confirmation of successful README update.
    *   **Coordinator Action (Post-Delegation):** Wait for confirmation.
    *   **Error Handling:** If the delegate fails, analyze the error. Use `read_file` on the README to understand the current state. Retry the update with more specific instructions (e.g., using `apply_diff` with exact line numbers) or report to user.

*   **Step 4: Final Report (Coordinator Task)**
    *   **Description:** Inform the user that the context file has been added and the KB README updated.
    *   **Procedure:** Use `attempt_completion`.

## 7. Postconditions ✅
*   The new context file exists in the specified mode's KB directory.
*   The mode's KB README includes an entry for the new file.

## 8. Error Handling & Escalation (Overall) ⚠️
*   If file writing or README updates fail repeatedly, check file system permissions or potential file corruption.
*   Escalate to the user if the target mode or its KB structure doesn't exist as expected.

## 9. PAL Validation Record 🧪
*   Date Validated: 2025-04-19
*   Method: Conceptual Review.
*   Test Case(s): N/A (Simple workflow).
*   Findings/Refinements: Seems straightforward. Emphasized using appropriate tools for README update.

## 10. Revision History 📜
*   v1.0 (2025-04-19): Initial draft.