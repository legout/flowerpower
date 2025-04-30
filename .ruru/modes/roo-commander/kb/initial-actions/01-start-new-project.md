+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-01-NEW"
title = "KB: Initial Action - Start New Project"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "new-project", "onboarding"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/manager-onboarding/manager-onboarding.mode.md",
    ".ruru/modes/manager-onboarding/kb/02-workflow.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Confirm user intent to start a new project and delegate the detailed onboarding process to `manager-onboarding`."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Start a NEW project from scratch' option from the initial prompt."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`manager-onboarding`)"]
trigger = "User selection of '🚀 Start a NEW project from scratch'."
success_criteria = [
    "User confirms intent to start a new project.",
    "Task successfully delegated to `manager-onboarding` with 'new' intent.",
    "Coordinator informs the user that the onboarding process has started."
]
failure_criteria = [
    "User cancels the new project creation.",
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

# KB: Initial Action - Start New Project

## 1. Objective 🎯
*   Confirm the user's choice to start a new project from scratch and initiate the specialized onboarding workflow managed by `manager-onboarding`.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Confirms user choice, delegates to `manager-onboarding`, reports initiation to the user.
*   **User:** Confirms or cancels the action.
*   **Delegate (`manager-onboarding`):** Executes the detailed new project onboarding workflow (defined in its own KB).

## 3. Procedure Steps 🪜

*   **Step 1: Confirm User Intent (Coordinator Task)**
    *   **Description:** Double-check that the user intended to start a new project.
    *   **Inputs:** User selected "🚀 Start a NEW project from scratch".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present a confirmation prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, let's start a new project! We'll set up the basic structure and gather some initial requirements. Are you ready to begin?</question>
              <follow_up>
                <suggest>Yes, start the new project onboarding!</suggest>
                <suggest>No, I chose the wrong option / Cancel</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response.
    *   **Outputs:** User confirmation (`[User Confirmation]`).
    *   **Error Handling:** If the user selects "No" or cancels, report "Okay, cancelling new project setup. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.**

*   **Step 2: Delegate to Onboarding Manager (Coordinator delegates to `manager-onboarding`)**
    *   **Description:** Hand off the detailed onboarding process to the specialized manager mode.
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
              🎯 Project Onboarding (New Project): Initiate the onboarding process for a NEW project.
              Initial User Request Context: "[initial_request]"
              Intent: 'new'
              Goal: Determine project name, setup core structure, optionally delegate tech init, perform initial discovery via agent-context-discovery, and report completion.
              Follow your standard workflow defined in `.ruru/modes/manager-onboarding/kb/02-workflow.md`.
              Your Task ID: [Generated TASK-ONBOARD-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `manager-onboarding`.
    *   **Error Handling:** If the `new_task` tool fails, log the error, report "Failed to initiate onboarding process due to a delegation error." to the user via `attempt_completion`, and stop.

*   **Step 3: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that the onboarding process has begun and what to expect.
    *   **Inputs:** Successful delegation in Step 2.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "Okay, I've handed off the initial setup to the Project Onboarding manager (`manager-onboarding`). They will guide you through naming the project, setting up basic files, and gathering initial requirements. Please follow their prompts."
    *   **Outputs:** User is informed, control is passed to `manager-onboarding` for the next interaction steps.
    *   **Error Handling:** N/A for this step.

## 4. Postconditions ✅
*   The user's intent to start a new project is confirmed.
*   The `manager-onboarding` mode has been delegated the task of performing the detailed onboarding workflow.
*   The user has been informed that the onboarding process is starting.
*   The Coordinator's responsibility for *this specific initial action* is complete. Further steps are managed by `manager-onboarding` until it reports back to the Coordinator.

## 5. Rationale / Notes 🤔
*   This procedure acts as a simple router and confirmation step.
*   It ensures the user's choice is deliberate before starting file system operations or more detailed prompts.
*   It leverages the specialized `manager-onboarding` mode for the complex steps involved in setting up a new project context, adhering to the principle of delegation.
*   Passing the `initial_request` context is important for `manager-onboarding` to potentially extract project name hints or understand the user's original phrasing.