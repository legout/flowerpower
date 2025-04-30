+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-02-EXISTING"
title = "KB: Initial Action - Onboard Existing Project"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "existing-project", "onboarding", "analysis"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/manager-onboarding/manager-onboarding.mode.md",
    ".ruru/modes/manager-onboarding/kb/02-workflow.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Confirm user intent to analyze and onboard the current project workspace and delegate the detailed onboarding process to `manager-onboarding`."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Analyze/Onboard the CURRENT project workspace' option from the initial prompt."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`manager-onboarding`)"]
trigger = "User selection of '📂 Analyze/Onboard the CURRENT project workspace'."
success_criteria = [
    "User confirms intent to onboard the current workspace.",
    "Task successfully delegated to `manager-onboarding` with 'existing' intent.",
    "Coordinator informs the user that the analysis and onboarding process has started."
]
failure_criteria = [
    "User cancels the onboarding process.",
    "Delegation to `manager-onboarding` fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Primarily coordination/delegation
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing in practice."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Onboard Existing Project

## 1. Objective 🎯
*   Confirm the user's choice to onboard the project located in the current VS Code workspace directory and initiate the specialized onboarding workflow managed by `manager-onboarding`.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Confirms user choice, delegates to `manager-onboarding`, reports initiation to the user.
*   **User:** Confirms or cancels the action.
*   **Delegate (`manager-onboarding`):** Executes the detailed existing project onboarding workflow (defined in its own KB).

## 3. Procedure Steps 🪜

*   **Step 1: Confirm User Intent (Coordinator Task)**
    *   **Description:** Double-check that the user intended to onboard the project in the current directory.
    *   **Inputs:** User selected "📂 Analyze/Onboard the CURRENT project workspace".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present a confirmation prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, let's analyze and set up the project currently open in your workspace (`{Current Working Directory}`). We'll detect the tech stack and gather some context. Proceed?</question>
              <follow_up>
                <suggest>Yes, analyze and onboard this project.</suggest>
                <suggest>No, I chose the wrong option / Cancel</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response.
    *   **Outputs:** User confirmation (`[User Confirmation]`).
    *   **Error Handling:** If the user selects "No" or cancels, report "Okay, cancelling onboarding for this project. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.**

*   **Step 2: Delegate to Onboarding Manager (Coordinator delegates to `manager-onboarding`)**
    *   **Description:** Hand off the detailed analysis and onboarding process for the existing project to the specialized manager mode.
    *   **Inputs:** User Confirmation = Yes, Initial User Request message (`[initial_request]` - should be stored from the very first interaction).
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for the `manager-onboarding` task (e.g., `TASK-ONBOARD-YYYYMMDD-HHMMSS`).
        2.  Log the delegation action in the Coordinator's log (Rule `08`).
        3.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>manager-onboarding</mode>
              <message>
              🎯 Project Onboarding (Existing Project): Initiate the onboarding process for the EXISTING project in directory '{Current Working Directory}'.
              Initial User Request Context: "[initial_request]"
              Intent: 'existing'
              Goal: Perform stack detection, gather context/requirements outline, ensure journal structure exists, and report completion.
              Follow your standard workflow defined in `.ruru/modes/manager-onboarding/kb/02-workflow.md`.
              Your Task ID: [Generated TASK-ONBOARD-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `manager-onboarding`.
    *   **Error Handling:** If the `new_task` tool fails, log the error, report "Failed to initiate onboarding process due to a delegation error." to the user via `attempt_completion`, and stop.

*   **Step 3: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that the analysis and onboarding process has begun.
    *   **Inputs:** Successful delegation in Step 2.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "Okay, I've asked the Project Onboarding manager (`manager-onboarding`) to analyze the project in `{Current Working Directory}` and guide the next steps. Please follow their prompts."
    *   **Outputs:** User is informed, control is passed to `manager-onboarding` for the next interaction steps.
    *   **Error Handling:** N/A for this step.

## 4. Postconditions ✅
*   The user's intent to onboard the current project is confirmed.
*   The `manager-onboarding` mode has been delegated the task of performing the detailed analysis and onboarding workflow for the existing project.
*   The user has been informed that the analysis/onboarding process is starting.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   This procedure confirms the user's choice for the current workspace context.
*   It leverages the specialized `manager-onboarding` mode, which contains the logic to handle existing projects differently from new ones (primarily skipping Git init and focusing on analysis/context).