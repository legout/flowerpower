+++
# --- Basic Metadata ---
id = "RULE-ONBOARD-LOGGING-V1"
title = "Onboarding Manager: Task Logging Requirement"
context_type = "rules"
scope = "Logging procedure for the onboarding manager"
target_audience = ["manager-onboarding"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "logging", "mdtm", "onboarding"]
related_context = [
    ".roo/rules/08-logging-procedure-simplified.md", # Workspace logging rule
    ".ruru/modes/manager-onboarding/kb/02-workflow-adaptive.md" # Specific workflow
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Ensures traceability of the onboarding process"
+++

# Mandatory Rule: Onboarding Task Logging

1.  **Initialize Log:** Upon receiving a task delegation (Task ID `[Your Task ID]`), immediately initialize your *own* task log file at `.ruru/tasks/[Your Task ID].md`. Use the standard TOML+MD format (Template `00_boilerplate.md` or similar). Log the initial goal and context received.
2.  **Record Progress:** Log significant actions, decisions, user interactions, delegations (including the delegated Task ID), and received results within your task log file using appropriate tools (`apply_diff`, `insert_content`).
3.  **Consult Workspace Standard:** Refer to the workspace logging rule (`.roo/rules/08-logging-procedure-simplified.md`) and its associated KB (`.ruru/modes/roo-commander/kb/12-logging-procedures.md`) for detailed tool usage guidance.