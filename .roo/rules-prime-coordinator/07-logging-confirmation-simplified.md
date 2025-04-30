+++
id = "PRIME-RULE-LOG-CONFIRM-SIMPLE-V1"
title = "Prime Coordinator: Rule - Logging & Prime Worker Confirmation Awareness"
context_type = "rules"
scope = "Logging requirements and awareness of worker confirmation step"
target_audience = ["prime"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "logging", "confirmation", "safety", "prime"]
related_context = [
    "01-operational-principles.md",
    "03-meta-dev-workflow-simplified.md",
    ".roo/rules/08-logging-procedure-simplified.md", # Workspace logging rule
    "prime-txt", "prime-dev"
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Emphasizes safety and logging standard"
+++

# Rule: Logging & Prime Worker Confirmation Awareness

1.  **Logging Requirement:**
    *   Log significant coordination activities, decisions, delegations, errors, and outcomes.
    *   Follow the standard procedure defined in the workspace rule **`.roo/rules/08-logging-procedure-simplified.md`**.

2.  **Prime Worker Confirmation Awareness:**
    *   **CRITICAL:** Remember that `prime-txt` and `prime-dev` are REQUIRED by their own rules to use `<ask_followup_question>` to seek explicit user confirmation *before* executing `write_to_file` or `apply_diff` for operational configuration files.
    *   **Expect this step:** When delegating direct edits (non-staging workflow), anticipate this user confirmation check by the worker before they report completion.
    *   **Safety:** This is a key safety mechanism. Do not try to circumvent it.