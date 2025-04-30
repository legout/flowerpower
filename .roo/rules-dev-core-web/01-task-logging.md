+++
# --- Basic Metadata ---
id = "RULE-COREWEB-LOGGING-V1"
title = "Core Web Developer: Task Logging Requirement"
context_type = "rules"
scope = "Logging procedure for Core Web Developer tasks"
target_audience = ["dev-core-web"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "logging", "mdtm", "dev-core-web", "worker"]
related_context = [
    ".roo/rules/08-logging-procedure-simplified.md", # Workspace logging rule
    ".ruru/modes/dev-core-web/kb/02-workflow.md" # Specific workflow
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Ensures traceability of implementation tasks"
+++

# Mandatory Rule: Task Logging

1.  **Use Assigned Task File:** When delegated a task referencing an MDTM task file (e.g., via `new_task` message "Process MDTM task file: `.ruru/tasks/TASK-...md`"), that specific file **is your primary log**.
2.  **Update Checklist:** As you complete steps defined in the task file's Markdown checklist, update the status marker (e.g., `- [ ]` to `- [✅]`) using `apply_diff` or `search_and_replace`.
3.  **Add Notes/Logs:** Add brief, relevant notes about implementation details, decisions made, resources consulted, or testing results directly into the Markdown body of the assigned task file, often under relevant checklist items or in a dedicated "Log" section. Use `apply_diff` or `insert_content`.
4.  **Update TOML Status:** Upon successful completion of the entire task defined in the file, update the `status` field in the **TOML block** to `"🟢 Done"` using `apply_diff`. If blocked, update to `"⚪ Blocked"` and clearly state the blocker in the Markdown body. Always update the `updated_date` field when changing the status.
5.  **Consult Workspace Standard:** Refer to the workspace logging rule (`.roo/rules/08-logging-procedure-simplified.md`) and its associated KB (`.ruru/modes/roo-commander/kb/12-logging-procedures.md`) for detailed tool usage guidance (`apply_diff`, `insert_content`, etc.).