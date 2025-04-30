+++
# --- Basic Metadata ---
id = "KB-COREWEB-WORKFLOW-V1"
title = "KB: Core Web Developer - Standard Workflow"
context_type = "process_definition"
scope = "Standard operational steps for implementing features/fixes"
target_audience = ["dev-core-web"]
granularity = "detailed"
status = "active"
last_updated = "2025-04-22"
tags = ["kb", "workflow", "sop", "html", "css", "javascript", "dev-core-web"]
related_context = [
    ".roo/rules-dev-core-web/01-task-logging.md",
    ".ruru/modes/dev-core-web/kb/01-principles.md"
]
template_schema_doc = ".ruru/templates/toml-md/08_ai_context_source.README.md"
relevance = "High: Defines the standard execution process"
+++

# KB: Core Web Developer - Standard Workflow

Follow these steps when assigned an implementation task (typically received via an MDTM task file):

1.  **Receive Task & Understand Context:**
    *   **Action:** Read the assigned MDTM task file (`.ruru/tasks/TASK-....md`) fully using `read_file`.
    *   **Focus:** Understand the `title`, `objective`, `description`, `acceptance_criteria`, and any specific implementation notes or checklist items.
    *   **Context:** Use `read_file` to examine any `related_docs` mentioned in the TOML block (e.g., design specs, API docs) or relevant existing code files.
    *   **Log:** Initialize logging in the assigned task file as per Rule `01`. Log understanding of the goal.

2.  **Analyze & Plan Implementation:**
    *   **Action:** Plan the approach based on requirements and principles (KB `01`).
    *   **Consider:**
        *   HTML structure needed (KB `03`).
        *   CSS styling approach (layout, responsiveness, specific styles) (KB `04`).
        *   JavaScript logic required (DOM interactions, event handling, `fetch` calls) (KB `05`).
        *   Basic accessibility needs (KB `06`).
    *   **Clarification:** If requirements are ambiguous or seem technically problematic, use `ask_followup_question` (directed back to your coordinator/lead, usually `frontend-lead`) *before* starting implementation. Log the clarification needed.
    *   **Log:** Briefly log the planned implementation approach in the task file.

3.  **Implement (Iteratively):**
    *   **Action:** Write or modify HTML, CSS, and JavaScript files as planned.
    *   **Tools:**
        *   Use `write_to_file` for new files.
        *   Use `apply_diff` (preferred) or `search_and_replace` for modifying existing files. Use `read_file` first to get context for diffs.
    *   **Checklist:** Update the checklist items (`- [ ]` -> `- [✅]`) in the MDTM task file as logical units of work are completed (Rule `01`). Add brief notes as needed.
    *   **Principles:** Adhere to core principles (KB `01`) and specific guidelines (KB `03`, `04`, `05`, `06`).

4.  **Test & Verify:**
    *   **Action:** Perform basic testing of the implemented changes.
    *   **Methods:**
        *   Mentally review code against requirements and acceptance criteria.
        *   Suggest manual verification steps for the user/lead (e.g., "Please open `index.html` and verify the modal opens/closes.").
        *   If linters/formatters are configured, use `execute_command` to run them (e.g., `npm run lint`) and address reported issues (Rule `02`).
    *   **Log:** Log testing steps performed and their outcomes in the task file.

5.  **Refine & Document:**
    *   **Action:** Refactor code for clarity if needed. Add necessary code comments explaining non-obvious logic.
    *   **Tools:** Use `apply_diff`.

6.  **Log Completion & Final Summary:**
    *   **Action:** Once all acceptance criteria are met and testing passes:
        *   Update the `status` field in the **TOML block** of the MDTM task file to `"🟢 Done"` (or `"🟣 Review"` if review by the lead is explicitly required).
        *   Update the `updated_date` field.
        *   Add a final summary comment to the Markdown body of the task file.
    *   **Tools:** Use `apply_diff`.

7.  **Report Back:**
    *   **Action:** Notify the delegating coordinator/lead (`frontend-lead`) that the task is complete.
    *   **Tool:** Use `attempt_completion`.
    *   **Content:** State success, reference the completed MDTM task file path (`.ruru/tasks/TASK-....md`).

**Error Handling:** If tools fail or blockers are encountered, log the issue in the task file, update the TOML `status` to `"⚪ Blocked"`, and report the specific problem back using `attempt_completion`.