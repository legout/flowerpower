+++
id = "ROO-CMD-RULE-COMPLEX-DELEGATION-PLAN-V1"
title = "Roo Commander: Rule - Complex Delegation Planning & Confidence Check"
context_type = "rules"
scope = "Procedure for planning multi-step delegations and consulting user when confidence is low"
target_audience = ["roo-commander"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-25" # Use current date
tags = ["rules", "delegation", "planning", "confidence", "multi-step", "mdtm", "roo-commander", "user-consultation"]
related_context = [
    "03-delegation-simplified.md", # The basic delegation rule
    ".roo/rules/04-mdtm-workflow-initiation.md", # Workspace MDTM rule
    ".roo/rules/06-iterative-execution-policy.md", # Iteration policy
    ".ruru/docs/standards/mode_selection_guide.md" # Mode selection guide
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Enhances strategic delegation for complex tasks"
+++

# Rule: Complex Delegation Planning & Confidence Check

This rule extends the basic delegation procedure (`03-delegation-simplified.md`) for tasks identified as particularly complex, ambiguous, or requiring a sequence of coordinated steps beyond a single MDTM task file.

**1. Trigger Conditions:**

*   Apply this procedure when a task involves:
    *   Significant ambiguity in requirements or implementation path.
    *   Multiple distinct phases or dependencies requiring different specialists or sequential execution.
    *   High uncertainty about the best approach or required modes.
    *   Initial analysis suggests the task breakdown might exceed simple MDTM checklist granularity or requires strategic sequencing.

**2. Planning Procedure:**

1.  **Analyze Goal:** Deeply analyze the user's goal, acceptance criteria, and any provided context. Identify ambiguities and potential complexities.
2.  **Break Down Task:** Decompose the overall goal into smaller, logical sub-tasks or phases.
3.  **Identify Specialists & Sequence:** For each sub-task, identify the most appropriate specialist mode(s) using the Mode Selection Guide (`.ruru/docs/standards/mode_selection_guide.md`). Determine the logical sequence or potential parallel execution paths.
4.  **Estimate Effort/Risk:** Briefly assess the estimated effort and risk associated with each sub-task and the overall plan.
5.  **Formulate Plan:** Outline the proposed delegation plan, including:
    *   Sequence of sub-tasks.
    *   Assigned specialist mode for each sub-task.
    *   Whether MDTM or simple `new_task` is appropriate for each step (following Rule `04-mdtm-workflow-initiation.md`).
    *   Key dependencies or handoffs between steps.

**3. Confidence Assessment:**

*   Evaluate your confidence in the formulated plan's success and efficiency. Consider:
    *   Clarity of requirements for each step.
    *   Availability and suitability of specialist modes.
    *   Potential risks or unknowns.
*   Assign a subjective confidence level (e.g., High, Medium, Low).

**4. User Consultation (Low/Medium Confidence):**

*   **If confidence is assessed as Low or Medium:**
    1.  **Do NOT proceed with delegation immediately.**
    2.  Use the `<ask_followup_question>` tool to present the situation to the user.
    3.  **Question Content:**
        *   Briefly explain the task's complexity and the reason for uncertainty.
        *   Present the proposed delegation plan (sub-tasks, modes, sequence).
        *   State your confidence level and the reasons (e.g., "Medium confidence due to ambiguity in API specification").
    4.  **Suggested Follow-ups:** Provide 2-4 actionable suggestions for the user, such as:
        *   "Proceed with the proposed plan."
        *   "Modify the plan: [Suggest a specific alternative sequence or mode]."
        *   "Provide clarification on: [Specify the ambiguous point]."
        *   "Delegate to [Alternative Lead/Mode] for further planning."
    5.  Await user direction before proceeding with delegation based on their choice.

**5. Execution (High Confidence or User Approval):**

*   If confidence is High, or if the user approves a plan after consultation:
    *   Proceed with executing the delegation plan step-by-step, using MDTM or simple `new_task` as determined for each sub-task.
    *   Follow standard logging (Rule `08`) and monitoring (Rule `04`) procedures.
    *   Utilize the Iterative Execution Policy (Rule `06`) for individual delegated steps as needed.

**Rationale:** This provides a mechanism for `roo-commander` to handle complex scenarios more robustly, leveraging user input when its own planning confidence is insufficient, thereby reducing the risk of inefficient or failed delegation chains.