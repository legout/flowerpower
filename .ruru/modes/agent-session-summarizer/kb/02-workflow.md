# Workflow
1.  **Receive Task:** Get assignment from Roo Commander, including:
    *   Path to the primary coordination task log (e.g., `.ruru/tasks/TASK-CMD-...`).
    *   Path to the active planning document (e.g., `.ruru/planning/...`).
    *   Current context window size information (Tokens, Percentage).
    *   (Optional) List of specific active/pending delegated task IDs to focus on.
2.  **Read Inputs:**
    *   Use `read_file` to get the content of the coordination log.
    *   Use `read_file` to get the content of the active planning document.
    *   Use `read_file` to get the content of the handover template (`.ruru/templates/handover_summary_template.md`).
    *   *(Optional/Advanced)* If needed to get detailed status of active tasks, use `list_files` on `.ruru/tasks/` and `read_file` on relevant `TASK-[MODE]-...` files identified in the coordination log or provided list.
3.  **Extract Information:**
    *   From coordination log: Identify current goal (from Goal section), recent actions/completions (from Notes/Checklist), known blockers/questions (from Notes).
    *   From planning document: Identify the next planned step(s).
    *   From task files (if read): Extract status, title, assignee for active/pending tasks.
4.  **Populate Template:**
    *   Replace placeholders in the template content (`{{TIMESTAMP}}`, `{{TOKEN_COUNT}}`, `{{PERCENTAGE}}`, `{{CURRENT_GOAL}}`, `{{COORDINATION_TASK_LINK}}`, `{{LAST_ACTION_...}}`, `{{ACTIVE_TASK_...}}`, `{{NEXT_STEP_...}}`, `{{PLANNING_DOC_LINK}}`, `{{BLOCKER_...}}`, `{{OPEN_QUESTION_...}}`) with the extracted information.
    *   Format lists appropriately (e.g., for multiple last actions or active tasks).
    *   Generate the current timestamp (YYYY-MM-DD HH:MM:SS UTC).
5.  **Generate Filename:** Create a timestamped filename using the format `handover_YYYYMMDD_HHMMSS.md`.
6.  **Save Summary:** Use `write_to_file` to save the populated summary content to `.ruru/context/[timestamped_filename].md`.
7.  **Report Completion:** Use `attempt_completion` to report success to Roo Commander, providing the full path to the saved summary file (e.g., `.ruru/context/handover_20250414_153000.md`).