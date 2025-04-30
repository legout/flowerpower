+++
# --- Basic Metadata ---
id = "RULE-ONBOARD-DELEGATE-WAIT-V1"
title = "Onboarding Manager: Synchronous Delegation Handling"
context_type = "rules"
scope = "Handling delegated tasks to other modes"
target_audience = ["manager-onboarding"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "delegation", "workflow", "synchronous", "onboarding"]
related_context = [
    ".ruru/modes/manager-onboarding/kb/02-workflow-adaptive.md" # Specific workflow
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Critical for correct workflow execution"
+++

# Mandatory Rule: Wait for Delegated Task Completion

1.  **Synchronous Nature:** Understand that delegating a task using `<new_task>` is **synchronous** from your perspective. You must wait for the delegate mode to finish its work and report back via `<attempt_completion>`.
2.  **Await Completion:** After using `<new_task>` to delegate to `discovery-agent`, `git-manager`, or any technology specialist, you **MUST** pause your workflow and wait for their `<attempt_completion>` signal before proceeding to the next step in your own workflow (`.ruru/modes/manager-onboarding/kb/02-workflow-adaptive.md`).
3.  **Handle Results:** Process the `result` from the `<attempt_completion>` signal. Handle success or failure appropriately as defined in your workflow's error handling sections. Log the outcome.