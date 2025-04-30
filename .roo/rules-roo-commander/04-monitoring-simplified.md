+++
id = "ROO-CMD-RULE-MONITOR-SIMPLE-V1"
title = "Roo Commander: Rule - Task Monitoring & Completion (Simplified)"
context_type = "rules"
scope = "Monitoring delegated tasks and processing completion signals"
target_audience = ["roo-commander"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "monitoring", "completion", "mdtm", "roo-commander"]
related_context = [
    "01-operational-principles.md",
    "03-delegation-simplified.md",
    "05-error-handling-rule.md",
    "08-logging-procedure-simplified.md",
    ".ruru/modes/roo-commander/kb/04-delegation-mdtm.md" # For detailed MDTM update info
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Processing results from delegates"
+++

# Rule: Task Monitoring & Completion (Simplified)

1.  **Await Signal:** Wait for `<attempt_completion>` from specialist modes.
2.  **Process Signal:** Extract result, identify task, assess success/failure/blocker.
3.  **Update MDTM Status (If Applicable):** If the task used MDTM (`.ruru/tasks/TASK-[MODE]-...`), update the `status` field in the task file's TOML block based on the outcome (e.g., `"🟣 Review"`, `"🟢 Done"`, `"⚪ Blocked"`) using `apply_diff`. Update `updated_date`. Log update (Rule `08`). Consult KB `04-delegation-mdtm.md` for detailed status guidance if needed.
4.  **Review Output:** Briefly review specialist output against acceptance criteria. Consider deeper review (`util-reviewer`) for complex changes.
5.  **Handle Failures/Blockers:** Initiate error handling (Rule `05`).
6.  **Log Completion:** Log task outcome in Commander's log (Rule `08`).
7.  **Proceed:** Determine and execute the next workflow step.
8.  **Handle Stalled Tasks:** For MDTM, if no response is received, check task file (`read_file`) and consider re-delegating (pointing to the *existing* task file). Log action (Rule `08`).