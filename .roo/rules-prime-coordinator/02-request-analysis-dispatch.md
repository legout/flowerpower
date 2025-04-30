+++
id = "PRIME-RULE-DISPATCH-V1"
title = "Prime Coordinator: Rule - Request Analysis & Dispatch"
context_type = "rules"
scope = "Initial analysis of user requests and workflow routing"
target_audience = ["prime"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-21"
tags = ["rules", "workflow", "dispatch", "analysis", "intent", "prime"]
related_context = ["03-meta-dev-workflow-rule.md", "04-operational-delegation-rule.md", "05-research-procedure-rule.md"]
+++

# Rule: Request Analysis & Dispatch

This rule defines how to analyze incoming user requests and dispatch them to the appropriate workflow.

**Procedure:**

1.  **Analyze Request:** Examine the user's request message and any mentioned file paths (`@`).
2.  **Determine Request Type:**
    *   **Type A (Meta-Development / Config Change):** Request involves modifying files related to Roo Commander's configuration (e.g., files in `.modes/`, `.roo/rules-*/`, `.workflows/`, `.processes/`, `.templates/`, `.roomodes*`, build scripts). **Action:** Proceed to Rule `03` (Meta-Dev Workflow).
    *   **Type B (Operational Task):** Request involves standard software development tasks (e.g., build feature, fix bug, write tests, refactor app code, manage git for the *project*). **Action:** Proceed to Rule `04` (Operational Delegation).
    *   **Type C (Research/Information):** Request asks for information, research, or analysis. **Action:** Proceed to Rule `05` (Research Procedure).
    *   **Type D (Ambiguous/Unclear):** Request is too vague to categorize. **Action:** Use `ask_followup_question` to request clarification on the goal and affected files/areas. Repeat Step 1 upon response.