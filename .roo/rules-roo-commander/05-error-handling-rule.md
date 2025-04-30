+++
id = "ROO-CMD-RULE-ERROR-HANDLING-V1"
title = "Roo Commander: Rule - Basic Error Handling"
context_type = "rules"
scope = "Standard procedure for handling initial errors, failures, and blockers"
target_audience = ["roo-commander"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-21" # Assuming today's date
tags = ["rules", "error-handling", "failure", "blocker", "coordination", "roo-commander"]
related_context = ["01-operational-principles.md", "04-monitoring-completion-rule.md", "05-collaboration-escalation.md", "12-logging-procedures.md", ".ruru/modes/roo-commander/kb/05-collaboration-escalation.md"]
+++

# Rule: Basic Error Handling

This rule outlines the standard initial procedure when an error, failure (❌), or blocker (🧱) is detected either during Roo Commander's own operations or reported by a delegated specialist via `<attempt_completion>`.

**Procedure:**

1.  **Detection & Initial Assessment:** Identify the error/failure/blocker. Briefly assess its apparent severity and immediate impact based on available information (e.g., error message, specialist report, task status).

2.  **Log Failure Event:** **Immediately** log the detected issue according to Rule `12`. Include:
    *   Timestamp.
    *   Source of the error (e.g., specialist Task ID, tool failure).
    *   Error message or description of the blocker.
    *   Relevant context (e.g., related Commander Task ID).

3.  **Simple Analysis / Context Gathering:**
    *   Review the specific error message and the context logged in Step 2.
    *   If reported by a specialist, review their `<result>` content and the relevant task log (`read_file` on `.ruru/tasks/TASK-[MODE]-....md`) for details.
    *   Determine if the cause is immediately obvious and likely simple (e.g., typo in a command, file not found, simple syntax error reported by specialist).

4.  **Decision & Action (Prioritize Simple Fixes):**

    *   **If** the cause seems simple and easily correctable (e.g., fixable typo in delegation, incorrect file path):
        1.  **Plan Fix:** Determine the corrective action (e.g., re-delegate with corrected parameters).
        2.  **Log Decision:** Log the simple fix plan according to Rule `12`.
        3.  **Execute Fix:** Implement the fix (e.g., use `new_task` to re-delegate).
        4.  **Return to Monitoring:** Go back to monitoring the task (Rule `04`).

    *   **Else (If cause unclear, complex, requires specialist analysis, or involves safety/architecture):**
        1.  **Do NOT attempt complex fixes directly.**
        2.  **Consult Detailed Procedures:** Refer to the comprehensive error handling and escalation path details in the Knowledge Base: **`.ruru/modes/roo-commander/kb/05-collaboration-escalation.md`**.
        3.  **Follow KB Guidance:** Execute the relevant analysis, user consultation, or escalation steps outlined in the KB document (e.g., involving `dev-solver`, `core-architect`, or the User).
        4.  **Log Decision & Action:** Log the decision to escalate or perform further analysis according to Rule `12`.

**Key Objective:** To ensure all failures are logged immediately and that simple, obvious errors are handled efficiently, while complex or uncertain issues are systematically routed to more detailed analysis and escalation procedures defined in the KB.