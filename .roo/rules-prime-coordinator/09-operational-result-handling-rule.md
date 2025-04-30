+++
id = "PRIME-RULE-OPS-RESULT-SIMPLE-V1"
title = "Prime Coordinator: Rule - Operational Delegate Result Handling (Simplified)"
context_type = "rules"
scope = "Processing completion signals from delegated operational tasks"
target_audience = ["prime"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "delegation", "result-handling", "monitoring", "operational", "prime"]
related_context = [
    "01-operational-principles.md",
    "04-operational-delegation-simplified.md",
    "07-logging-confirmation-simplified.md",
    ".ruru/modes/roo-commander/kb/05-collaboration-escalation.md" # For complex error handling
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Processing results from operational delegates"
+++

# Rule: Operational Delegate Result Handling (Simplified)

This rule defines how to process `<attempt_completion>` signals from delegated *operational* tasks (Rule `04`).

**Procedure:**

1.  **Await Signal:** Wait for `<attempt_completion>` from the specialist.
2.  **Process Signal:** Extract result, identify task, assess outcome (✅ success, ❌ failure, 🧱 blocker).
3.  **Log Outcome:** Log the reported outcome (Rule `07`).
4.  **Handle Failure/Blocker:**
    *   If failure/blocker reported:
        *   **Do NOT retry automatically.**
        *   Analyze the error message. Is the cause simple/obvious?
        *   **If Simple:** Report failure to user via `ask_followup_question` with suggested next steps (e.g., retry, cancel, stage files). Await user direction.
        *   **If Complex/Unclear:** Consult detailed error handling/escalation procedures (e.g., KB `.ruru/modes/roo-commander/kb/05-collaboration-escalation.md`) or escalate analysis.
5.  **Handle Success:**
    *   If success reported:
        *   Review success message/artifacts.
        *   Determine the next logical step.
        *   Report success/next step to user (`attempt_completion` or `ask_followup_question`).