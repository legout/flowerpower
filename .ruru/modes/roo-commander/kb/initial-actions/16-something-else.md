+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-16-ELSE"
title = "KB: Initial Action - Handle 'Something Else' / Clarify Goal"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "clarification", "fallback", "intent-analysis"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Prompt the user to describe their goal more clearly when none of the standard initial options fit, then re-analyze the user's response to determine the appropriate next step or workflow."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Something else... (Describe your goal)' option from the initial prompt."
roles = ["Coordinator (Roo Commander)", "User"]
trigger = "User selection of '🤔 Something else... (Describe your goal)'."
success_criteria = [
    "Coordinator successfully prompts the user for a clearer goal description.",
    "Coordinator receives the user's description.",
    "Coordinator successfully re-analyzes the new description to trigger a more specific workflow (e.g., planning, fixing, research, delegation)."
]
failure_criteria = [
    "User cancels or provides an equally unclear goal description.",
    "Coordinator fails to re-analyze the new goal effectively."
]

# --- Integration ---
acqa_applicable = false # Dialogue/Clarification
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Handle 'Something Else' / Clarify Goal

## 1. Objective 🎯
*   To handle cases where the user's initial goal doesn't fit the predefined starting options by prompting for a clearer description and then re-initiating the intent analysis process based on the new information.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Prompts for clarification, receives the new goal description, re-analyzes intent.
*   **User:** Provides a more detailed description of their goal.

## 3. Procedure Steps 🪜

*   **Step 1: Prompt for Goal Description (Coordinator Task)**
    *   **Description:** Ask the user to elaborate on what they want to achieve since the standard options didn't fit.
    *   **Inputs:** User selected "🤔 Something else...".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, please describe what you'd like to achieve in more detail. What is the main goal or task you have in mind?</question>
              <follow_up>
                <suggest>Cancel</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store it as `[New Goal Description]`.
    *   **Outputs:** `[New Goal Description]` provided by the user.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling. Let me know if you have another task." using `attempt_completion` and **stop this workflow.**

*   **Step 2: Re-Analyze Intent & Route (Coordinator Task)**
    *   **Description:** Process the `[New Goal Description]` to determine the appropriate next workflow, similar to the initial request analysis but with potentially more specific information.
    *   **Inputs:** `[New Goal Description]`.
    *   **Procedure:**
        1.  Analyze the `[New Goal Description]` for keywords and intent (planning, building, fixing, research, config change, specific delegation, etc.).
        2.  **Attempt to match** the described goal to one of the primary workflows or initial actions (Options 1-15).
        3.  **If** a clear match is found (e.g., description clearly indicates a need for onboarding, bug fixing, refactoring, research):
            *   Initiate the corresponding workflow defined in the relevant KB file (e.g., `01_start_new_project.md`, `06_fix_bug.md`, `10_research_topic.md`). **Transition control to that workflow.**
        4.  **Else (if still unclear or complex):**
            *   Acknowledge the goal description.
            *   Explain that you will proceed with a more general planning or coordination approach.
            *   Transition to the main **Project Coordination & Execution** workflow (defined in KB `03-workflow-coordination.md`), using the `[New Goal Description]` as the primary input objective.
    *   **Outputs:** Transition to a specific workflow or the main coordination loop.
    *   **Error Handling:** If the goal remains completely ambiguous even after clarification, inform the user you need more specific direction and perhaps present the main options again.

## 4. Postconditions ✅
*   The user has provided a more detailed description of their goal.
*   The Coordinator has attempted to route the user to the most appropriate workflow based on the new description.
*   The system has either initiated a specific workflow (like onboarding, bug fixing) or transitioned to the main coordination phase.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   This acts as a necessary fallback to capture user intent not covered by the primary options.
*   It forces a clarification step, which is essential when the initial categorization fails.
*   The re-analysis step attempts to leverage the more detailed user input to make a better routing decision.
*   Transitioning to the main coordination workflow (`03-workflow-coordination.md`) provides a path forward even if the goal remains somewhat complex or doesn't fit a simple starting template.