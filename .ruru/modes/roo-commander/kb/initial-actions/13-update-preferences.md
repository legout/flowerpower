+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-13-PREFS"
title = "KB: Initial Action - Update User Preferences / Profile"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "preferences", "profile", "configuration", "user-settings", "prime-coordinator"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".roo/rules/00-user-preferences.md", # The target file
    ".ruru/modes/prime-coordinator/prime-coordinator.mode.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Gather the user's desired preference changes and delegate the update of the `.roo/rules/00-user-preferences.md` file to the `prime-coordinator` mode."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Update my preferences / profile' option."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`prime-coordinator`)"]
trigger = "User selection of '⚙️ Update my preferences / profile'."
success_criteria = [
    "Coordinator successfully obtains the specific preference changes from the user.",
    "Task successfully delegated to `prime-coordinator` with the target file path and changes.",
    "Coordinator informs the user that `prime-coordinator` will handle the update."
]
failure_criteria = [
    "User cancels the process or provides unclear preference changes.",
    "Delegation to `prime-coordinator` fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Configuration update
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Update User Preferences / Profile

## 1. Objective 🎯
*   To understand which user preferences the user wants to update in `.roo/rules/00-user-preferences.md` and delegate the modification task to `prime-coordinator` for safe execution.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Gathers requested preference changes, delegates update task to `prime-coordinator`, reports handoff.
*   **User:** Specifies which preferences to change and their new values.
*   **Delegate (`prime-coordinator`):** Executes the file modification using its workflow (likely involving `prime-txt` with user confirmation).

## 3. Procedure Steps 🪜

*   **Step 1: Identify Desired Preference Changes (Coordinator Task)**
    *   **Description:** Ask the user which preferences they want to update and what the new values should be. Reference the structure of the preferences file.
    *   **Inputs:** User selected "⚙️ Update my preferences / profile".
    *   **Tool:** `ask_followup_question`, `read_file` (optional, to show current settings)
    *   **Procedure:**
        1.  *(Optional)* Use `read_file` to get the current content of `.roo/rules/00-user-preferences.md` to potentially show the user their existing settings.
        2.  Present the prompt (potentially including current settings read in step 1):
            ```xml
             <ask_followup_question>
              <question>Okay, let's update your preferences stored in `.roo/rules/00-user-preferences.md`.
              <!-- Optional: Include current settings here if read -->
              <!-- Example: Current name: '{{current_name}}', Verbosity: '{{current_verbosity}}' -->
              What would you like to change? Please specify the preference (e.g., 'user_name', 'skills', 'verbosity_level', 'auto_execute_commands') and the new value(s).
              </question>
              <follow_up>
                <suggest>Set user_name to "New Name"</suggest>
                <suggest>Change verbosity_level to "verbose"</suggest>
                <suggest>Add "React" to skills list</suggest>
                <suggest>Cancel preference update</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        3.  Await user response. Store the requested changes as `[Preference Changes]`.
    *   **Outputs:** `[Preference Changes]` described by the user.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling preference update. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the request is unclear, prompt again for specific field names and values.

*   **Step 2: Delegate Update to Prime Coordinator (Coordinator delegates to `prime-coordinator`)**
    *   **Description:** Hand off the specific preference update request to the `prime-coordinator`.
    *   **Inputs:** `[Preference Changes]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for `prime-coordinator` (e.g., `TASK-PRIME-...`).
        2.  Log the delegation action (Rule `08`).
        3.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>prime-coordinator</mode>
              <message>
              ⚙️ User Preference Update Request: Please update the user preferences file based on the following user request.
              Target File: `.roo/rules/00-user-preferences.md`
              Requested Changes:
              ---
              [Preference Changes]
              ---
              Use your standard meta-development workflow (direct edit via prime-txt with confirmation, as this is not a core protected file) to apply these changes accurately to the TOML frontmatter.
              Your Task ID: [Generated TASK-PRIME-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `prime-coordinator`.
    *   **Error Handling:** If `new_task` fails, log the error, report "Failed to delegate preference update task to Prime Coordinator due to an error." to the user via `attempt_completion`, and stop.

*   **Step 3: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that the request has been handed off to `prime-coordinator`.
    *   **Inputs:** Successful delegation in Step 2.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "Okay, I've passed your preference update request to the Prime Coordinator (`prime-coordinator`). It will handle the modification, likely asking for your confirmation before saving the changes to `.roo/rules/00-user-preferences.md`. Please follow its prompts."
    *   **Outputs:** User is informed, control passed to `prime-coordinator`.
    *   **Error Handling:** N/A.

## 4. Postconditions ✅
*   The user's specific preference change request has been captured.
*   The `prime-coordinator` mode has been delegated the task of updating the `.roo/rules/00-user-preferences.md` file.
*   The user has been informed that `prime-coordinator` is handling the update.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   Delegating to `prime-coordinator` ensures that even user preference changes go through a controlled workflow (direct edit for this file type, but involving `prime-txt` which requires user confirmation).
*   This avoids having the main `roo-commander` directly modify configuration files.
*   Showing current settings (optional Step 1.1) can improve user experience.