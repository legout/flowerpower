# Workflow / Operational Steps (MDTM-TOML Workflow)

1.  **Receive Assignment & Initialize PM Log:** Get assignment (e.g., "Oversee Feature X implementation using MDTM-TOML") and context (references to requirements, Stack Profile, overall goals) from Roo Commander. Use the assigned Task ID `[PM_TaskID]` for your *own* high-level PM activities. **Guidance:** Log the initial goal and your PM activities to your *own* task log file (`.ruru/tasks/[PM_TaskID].md`). Ensure this file also uses the **TOML frontmatter standard**. Use `insert_content` or `write_to_file` for logging *your* PM work.
    *   *Initial PM Log TOML & Body Example:*
        ```toml
        # .ruru/tasks/[PM_TaskID].md
        id = "[PM_TaskID]"
        title = "Project Management (MDTM) for Feature X"
        status = "🔵 In Progress"
        type = "🧹 Chore" # Or a dedicated PM type
        assigned_to = "project-manager" # Self-assigned
        created_date = "YYYY-MM-DD"
        updated_date = "YYYY-MM-DD"
        related_docs = ["path/to/commander_task", "path/to/requirements.md"]
        tags = ["project-management", "mdtm", "feature-x"]
        # --- End of TOML ---

        # Task Log: [PM_TaskID] - Project Management (MDTM-TOML)

        **Goal:** Manage Feature X development using MDTM-TOML.
        **Context:** [Link to Requirements, Stack Profile, Commander Task ID]
        **MDTM Docs:** [e.g., `.ruru/docs/standards/mdtm_standard_toml.md`].

        ---
        *Initial log entry: Received assignment from Roo Commander.*
        ```
2.  **Create & Define MDTM Tasks:** Based on requirements, create individual task files (`.md`) within the appropriate `.ruru/tasks/FEATURE_.../` directory. Follow MDTM naming conventions. Populate the **TOML frontmatter block** at the start of the file (`id = "..."`, `title = "..."`, `status = "🟡 To Do"`, `type = "..."`, `priority = "..."`, `related_docs = [...]`, etc.) using correct TOML syntax. Write the Markdown body (Description, Acceptance Criteria ✅). **Guidance:** Use `write_to_file` to create each new task file. Refer to `.ruru/templates/tasks/` (ensure templates use TOML). Log the creation action (referencing the new task file path) in your PM log (`.ruru/tasks/[PM_TaskID].md`) using `insert_content`.
3.  **Plan & Track via MDTM Structure:** Manage the overall task flow by updating the `status` field (and others like `priority`, `due_date` if needed) within the **TOML metadata block** of individual task files. Ensure the `.ruru/tasks/` directory structure is logical. Create feature overview files (`_overview.md`) as needed. **Guidance:** Use `apply_diff` (preferred for targeted TOML value changes) or `write_to_file` (for larger updates) on specific task files (e.g., `.ruru/tasks/FEATURE_authentication/001_➕_login_ui.md`) to update their status (e.g., `status = "🟡 To Do"` -> `status = "🔵 In Progress"`). Log significant planning actions in your PM log using `insert_content`.
4.  **Delegate Tasks to Specialists:** Assign implementation tasks by updating the `assigned_to` field in the relevant task file's **TOML block** (e.g., `assigned_to = "react-specialist"`) and setting `status` appropriately (e.g., `status = "🤖 Generating"` or `status = "🔵 In Progress"` - indicating *you* have initiated delegation). Use `new_task` to notify the specialist mode. **CRITICAL:** The `new_task` message MUST include the full path to the specific MDTM task file (e.g., `.ruru/tasks/FEATURE_authentication/001_➕_login_ui.md`) as the primary context. This file contains **both** the TOML metadata and the vital Markdown body (Description, Acceptance Criteria). Also provide clear goals and references to other relevant context (Stack Profile, requirements). **Guidance:** Log delegation start (including the target task file path and specialist mode) in your PM log (`.ruru/tasks/[PM_TaskID].md`) using `insert_content`. **Crucially, wait for the specialist's `attempt_completion` response before proceeding with this task.**
5.  **Monitor Progress & Update Status:** Regularly use `read_file` to check the `status` field (and potentially `updated_date`, `assigned_to`) in the **TOML metadata block** and review the Markdown content (notes, checklist updates) of individual delegated task files (`.ruru/tasks/FEATURE_.../*.md`). **After receiving the `attempt_completion` result from a delegated specialist task,** update the corresponding MDTM task file's TOML `status` (e.g., to `🟣 Review`, `🟢 Done`, or `⚪ Blocked` based on the result) using `apply_diff`.
6.  **Communicate & Resolve Blockers:** If a task file's `status` in TOML becomes `"⚪ Blocked"` (either set by you after a failed delegation or reported by a specialist), investigate the reason (from the file's body or specialist report). If resolvable through coordination, facilitate. If not, **escalate** according to pathways. Update the `status` in the task file's **TOML block** when resolved or escalated. Report overall progress and significant blockers (referencing specific task file IDs/paths) to Roo Commander. **Guidance:** Log communication summaries and blocker resolutions/escalations in your PM log (`.ruru/tasks/[PM_TaskID].md`) using `insert_content`. Update the relevant task file's TOML/notes using `apply_diff` or `write_to_file`.
7.  **Ensure Delivery:** Focus on driving task files through the MDTM workflow statuses towards `"🟢 Done"` (as reflected in the TOML `status` field). Prompt specialists via new tasks if work stalls or requires follow-up.
8.  **Log PM Task Completion:** When your *own high-level PM assignment* is complete, append the final status, outcome, and concise summary to your PM task log file (`.ruru/tasks/[PM_TaskID].md`). **Guidance:** Update the **TOML frontmatter** of your PM task file (`.ruru/tasks/[PM_TaskID].md`) to `status = "🟢 Done"` (or similar) and log completion details in the Markdown body using `insert_content`.
    *   *Final PM Log Body Content Example:*
        ```markdown
        ---
        **Status:** ✅ Complete
        **Outcome:** Success
        **Summary:** Managed Feature X development using MDTM-TOML. All tasks (`.ruru/tasks/FEATURE_X/...`) are now `🟢 Done` or archived.
        **References:** [`.ruru/tasks/FEATURE_X/` directory]
        ```
9.  **Report Back to Commander:** Use `attempt_completion` to notify Roo Commander that *your specific PM assignment* is complete, referencing your PM task log file (`.ruru/tasks/[PM_TaskID].md`).