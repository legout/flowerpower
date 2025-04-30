+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-05-PLAN"
title = "KB: Initial Action - Plan/Design New Feature or Project"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "planning", "design", "architecture", "product"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/core-architect/core-architect.mode.md",
    ".ruru/modes/manager-product/manager-product.mode.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Gather the initial goal for planning or designing a new feature/project and delegate the detailed planning/design task to the appropriate mode (`core-architect` or `manager-product`)."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Plan/Design a new feature or project' option."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`core-architect` or `manager-product`)"]
trigger = "User selection of '💡 Plan/Design a new feature or project'."
success_criteria = [
    "Coordinator successfully obtains the high-level goal/scope from the user.",
    "Coordinator identifies the primary focus (technical vs. product).",
    "Task successfully delegated to either `core-architect` or `manager-product`.",
    "Coordinator informs the user that the planning/design process has started."
]
failure_criteria = [
    "User cancels the process or provides an unclear goal.",
    "Delegation to the chosen planning mode fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Primarily coordination/delegation
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing, including the handoff logic."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Plan/Design New Feature or Project

## 1. Objective 🎯
*   To understand the user's high-level goal for planning or designing a new feature/project and delegate the detailed work to the appropriate strategic mode (`core-architect` for technical focus, `manager-product` for product/feature focus).

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Gathers initial goal, helps determine focus, delegates to planner, reports initiation.
*   **User:** Provides the initial goal/scope and clarifies focus if needed.
*   **Delegate (`core-architect` / `manager-product`):** Executes the detailed planning or design process according to their specific workflow.

## 3. Procedure Steps 🪜

*   **Step 1: Get Initial Goal/Scope (Coordinator Task)**
    *   **Description:** Ask the user to briefly describe the feature or project they want to plan or design.
    *   **Inputs:** User selected "💡 Plan/Design...".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Great! Let's start planning/designing. Please briefly describe the project or feature you have in mind. What is its main purpose or goal?</question>
              <follow_up>
                <suggest>Cancel planning</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store it as `[Initial Goal]`.
    *   **Outputs:** `[Initial Goal]` provided by the user.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling planning/design. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the goal is very unclear, prompt again for more specific information.

*   **Step 2: Determine Planning Focus (Coordinator Task)**
    *   **Description:** Based on the `[Initial Goal]`, determine if the primary focus is technical architecture or product definition. Ask the user if unsure.
    *   **Inputs:** `[Initial Goal]`.
    *   **Tool:** `ask_followup_question` (if needed)
    *   **Procedure:**
        1.  Analyze `[Initial Goal]`. Does it sound more like defining *how* something will be built technically (architecture, tech stack, high-level components) or *what* should be built and *why* (features, user needs, market fit)?
        2.  **If** focus is clearly technical architecture -> Set `[Target Delegate]` = `core-architect`. Proceed to Step 3.
        3.  **If** focus is clearly product/feature definition -> Set `[Target Delegate]` = `manager-product`. Proceed to Step 3.
        4.  **Else (Ambiguous):** Present clarification prompt:
            ```xml
             <ask_followup_question>
              <question>Thanks! To make sure we start correctly, is your primary focus right now on the **technical architecture** (how it's built, technology choices) or the **product/feature definition** (what it does, user needs, market goals)?</question>
              <follow_up>
                <suggest>Focus on Technical Architecture (`core-architect`)</suggest>
                <suggest>Focus on Product/Feature Definition (`manager-product`)</suggest>
                <suggest>Both are equally important right now</suggest>
                <suggest>Cancel planning</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        5.  Await user response. If "Both", default to `core-architect` first or `manager-product` based on which seems slightly more relevant from `[Initial Goal]`, or ask user to pick one to start. If user cancels, handle cancellation as in Step 1. Set `[Target Delegate]` based on choice.
    *   **Outputs:** `[Target Delegate]` (either `core-architect` or `manager-product`).

*   **Step 3: Delegate Planning/Design Task (Coordinator delegates to Target Delegate)**
    *   **Description:** Hand off the detailed planning/design work to the selected strategic mode.
    *   **Inputs:** `[Initial Goal]`, `[Target Delegate]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for the delegate (e.g., `TASK-ARCH-...` or `TASK-PROD-...`).
        2.  Log the delegation action in the Coordinator's log (Rule `08`).
        3.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>[Target Delegate]</mode> <!-- core-architect or manager-product -->
              <message>
              🎯 Initiate Planning/Design: The user wants to plan/design a new project/feature.
              Initial Goal Statement: "[Initial Goal]"
              Please begin your standard planning/design process based on this initial goal. Gather necessary details, define scope/vision/architecture [adjust based on target delegate's role], and produce relevant artifacts (e.g., ADRs, planning docs, requirement outlines).
              Your Task ID: [Generated TASK-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `core-architect` or `manager-product`.
    *   **Error Handling:** If `new_task` fails, log the error, report "Failed to initiate planning/design process due to a delegation error." to the user via `attempt_completion`, and stop.

*   **Step 4: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that the planning/design process has begun with the chosen specialist.
    *   **Inputs:** Successful delegation in Step 3, `[Target Delegate]`.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "Okay, I've handed off the planning/design request to the `{Target Delegate Name}` (`[Target Delegate]`). They will guide you through the detailed process. Please follow their prompts."
    *   **Outputs:** User is informed, control is passed to the delegate mode.
    *   **Error Handling:** N/A.

## 4. Postconditions ✅
*   The user's initial planning/design goal has been captured.
*   The task has been delegated to the appropriate mode (`core-architect` or `manager-product`).
*   The user has been informed that the detailed planning/design process is starting.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   This workflow acts as a bridge between a high-level user idea and the detailed processes managed by `core-architect` or `manager-product`.
*   It helps direct the user to the correct starting point based on whether their initial focus is more technical or product-oriented.
*   The delegate modes (`core-architect`, `manager-product`) are responsible for their own detailed workflows, including potentially triggering project setup via `manager-onboarding` if required.