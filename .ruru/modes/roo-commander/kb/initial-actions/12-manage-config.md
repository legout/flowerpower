+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-12-CONFIG"
title = "KB: Initial Action - Manage Roo Configuration (Advanced)"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "configuration", "modes", "rules", "advanced", "prime-coordinator"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/prime-coordinator/prime-coordinator.mode.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Identify user intent to modify Roo Commander's own configuration (modes, rules, KB) and hand off the request to the specialized `prime-coordinator` mode for safe execution."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Manage Roo Configuration (Advanced)' option. It does NOT perform configuration changes directly."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`prime-coordinator`)"]
trigger = "User selection of '⚙️ Manage Roo Configuration (Advanced)'."
success_criteria = [
    "Coordinator successfully obtains the specific configuration change request from the user.",
    "Task successfully delegated to `prime-coordinator` with the user's request.",
    "Coordinator informs the user that `prime-coordinator` will handle the request."
]
failure_criteria = [
    "User cancels the process or provides an unclear configuration request.",
    "Delegation to `prime-coordinator` fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Handoff workflow
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Manage Roo Configuration (Advanced)

## 1. Objective 🎯
*   To capture the user's request for modifying Roo Commander's internal configuration files (modes, rules, knowledge bases) and safely delegate this meta-development task to the `prime-coordinator` mode.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Confirms user intent, gathers the specific change request, delegates to `prime-coordinator`, reports the handoff.
*   **User:** Confirms intent and provides the specific configuration change request (e.g., which file to edit, what change to make).
*   **Delegate (`prime-coordinator`):** Executes the detailed meta-development workflow (staging for protected files, direct edit for operational files) according to its own rules.

## 3. Procedure Steps 🪜

*   **Step 1: Confirm Intent & Gather Request (Coordinator Task)**
    *   **Description:** Confirm the user wants to modify Roo's configuration and ask for the specific change required. Explain that this will be handled by `prime-coordinator`.
    *   **Inputs:** User selected "⚙️ Manage Roo Configuration (Advanced)".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, we can manage Roo's configuration. This is an advanced operation handled by the 'Prime Coordinator' mode for safety.
              Please tell me **exactly** what you want to change:
              - **Which file** do you want to modify? (e.g., `.ruru/modes/dev-react/kb/01-core-concepts.md`, `.roo/rules/05-os-aware-commands.md`)
              - **What specific change** needs to be made? (e.g., "Add a section about X", "Update the title field in the TOML", "Correct the command in step 3")
              </question>
              <follow_up>
                <suggest>Cancel configuration change</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store it as `[Config Change Request]`.
    *   **Outputs:** `[Config Change Request]` provided by the user.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling configuration management. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the request is unclear (e.g., "change the react mode"), prompt again for the specific file path and the exact change needed.

*   **Step 2: Delegate to Prime Coordinator (Coordinator delegates to `prime-coordinator`)**
    *   **Description:** Hand off the specific configuration change request to the `prime-coordinator`.
    *   **Inputs:** `[Config Change Request]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for the `prime-coordinator` task (e.g., `TASK-PRIME-YYYYMMDD-HHMMSS`).
        2.  Log the delegation action in the Coordinator's log (Rule `08`).
        3.  Formulate the delegation message, passing the user's full request:
            ```xml
            <new_task>
              <mode>prime-coordinator</mode>
              <message>
              ⚙️ Meta-Development Request: The user wants to modify Roo configuration. Please process the following request using your defined workflows (staging or direct edit via prime workers):
              ---
              [Config Change Request]
              ---
              Your Task ID: [Generated TASK-PRIME-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `prime-coordinator`.
    *   **Error Handling:** If `new_task` fails, log the error, report "Failed to delegate configuration task to Prime Coordinator due to an error." to the user via `attempt_completion`, and stop.

*   **Step 3: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that the request has been handed off to `prime-coordinator`.
    *   **Inputs:** Successful delegation in Step 2.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "Okay, I've passed your configuration change request to the Prime Coordinator (`prime-coordinator`). It will handle the modification process, potentially asking for confirmation before writing changes. Please follow its prompts."
    *   **Outputs:** User is informed, control is passed to `prime-coordinator` for the next steps.
    *   **Error Handling:** N/A.

## 4. Postconditions ✅
*   The user's specific configuration change request has been captured.
*   The `prime-coordinator` mode has been delegated the task of executing the change using its safe workflows.
*   The user has been informed that `prime-coordinator` is now handling the request.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   This workflow acts as a safe entry point for meta-development tasks initiated via the main Commander interface.
*   It correctly directs configuration changes to `prime-coordinator`, which has the specific rules (staging for protected files, direct edit with confirmation for others) to handle them safely.
*   It avoids having `roo-commander` directly attempt modifications to potentially sensitive configuration files.