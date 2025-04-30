+++
id = "ROO-CMD-RULE-DELEGATION-SIMPLE-V1"
title = "Roo Commander: Rule - Task Delegation (Simplified)"
context_type = "rules"
scope = "Delegating tasks to specialist modes, including MDTM decision"
target_audience = ["roo-commander"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-25"
tags = ["rules", "delegation", "mdtm", "specialists", "roo-commander"]
related_context = [
    "01-operational-principles.md",
    ".ruru/docs/standards/mode_selection_guide.md",
    ".ruru/context/stack_profile.json",
    ".ruru/modes/roo-commander/kb/04-delegation-mdtm.md", # For detailed MDTM steps
    "04-mdtm-workflow-initiation.md" # Workspace rule
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Core delegation logic"
+++

# Rule: Task Delegation (Simplified)

1.  **Define Goal:** Clearly define the task objective.
2.  **Select Specialist:** Consult Stack Profile (`.ruru/context/stack_profile.json`) and the **Mode Selection Guide (`.ruru/docs/standards/mode_selection_guide.md`)**. Match task requirements/tags to specialist capabilities. Prioritize specific modes over generalists. Log rationale (Rule `08`).
3.  **Determine Method:**
    *   **Use MDTM Workflow if:** Task is complex, stateful, high-risk, requires detailed tracking/handoffs (Ref: Rule `04-mdtm-workflow-initiation.md`). Consult KB `.ruru/modes/roo-commander/kb/04-delegation-mdtm.md` for detailed procedure if needed.
    *   **Use Simple `new_task` if:** Task is straightforward, read-only, or low-risk.
4.  **Prepare Context:** Gather essential context (goal, criteria, file paths, Task IDs, Stack Profile).
5.  **Execute Delegation:** Use `new_task`. For MDTM, follow Rule `04-mdtm-workflow-initiation.md` (which includes creating the task file first). For simple tasks, provide context directly in the message.
6.  **Log & Monitor:** Log delegation (Rule `08`). Monitor via Rule `04`.