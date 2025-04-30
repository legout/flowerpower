+++
id = "PRIME-RULE-OPS-DELEGATE-SIMPLE-V1"
title = "Prime Coordinator: Rule - Operational Task Delegation (Simplified)"
context_type = "rules"
scope = "Delegating standard development tasks"
target_audience = ["prime"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "delegation", "operational", "mdtm", "prime"]
related_context = [
    "01-operational-principles.md",
    ".roo/rules/04-mdtm-workflow-initiation.md", # Workspace MDTM Rule
    ".ruru/modes/roo-commander/kb/kb-available-modes-summary.md", # For specialist selection
    ".ruru/context/stack_profile.json", # Assumed available
    ".ruru/modes/roo-commander/kb/04-delegation-mdtm.md" # Can reference for detailed MDTM steps
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Core workflow for operational tasks"
+++

# Rule: Operational Task Delegation (Simplified)

This rule defines how to handle requests (Type B from Rule `02`) for standard software development tasks.

**Procedure:**

1.  **Receive Goal:** Understand the operational goal from the user.
2.  **Select Specialist:** Choose the appropriate *operational* specialist mode (e.g., `framework-react`, `dev-api`). Consult Stack Profile and KB Mode Summary (`.ruru/modes/roo-commander/kb/kb-available-modes-summary.md`). **Do NOT select Prime modes (`prime-txt`, `prime-dev`) for operational tasks.** Log rationale (Rule `07`).
3.  **Determine Method:** Decide between simple `new_task` or MDTM workflow based on complexity/risk criteria (refer to workspace Rule `04-mdtm-workflow-initiation.md`, section 1).
4.  **Execute Delegation:**
    *   **If MDTM:** Follow the procedure defined in the workspace rule **`.roo/rules/04-mdtm-workflow-initiation.md`** (Create Task File -> Delegate via `new_task` pointing to file). Consult KB `.ruru/modes/roo-commander/kb/04-delegation-mdtm.md` if detailed steps are needed.
    *   **If Simple:** Delegate directly using `new_task` with clear objective, acceptance criteria, and context.
5.  **Log & Monitor:** Log delegation (Rule `07`). Monitor progress (Rule `09`).