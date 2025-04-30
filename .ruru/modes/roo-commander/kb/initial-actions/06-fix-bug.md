+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-06-BUGFIX"
title = "KB: Initial Action - Fix a Specific Bug"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "bug-fix", "debugging", "dev-fixer"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/dev-fixer/dev-fixer.mode.md",
    ".ruru/templates/toml-md/02_mdtm_bug.md" # Optional template for bug reporting
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Gather initial information about a specific bug and delegate the diagnosis and fixing process to the `dev-fixer` specialist mode."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Fix a specific bug' option from the initial prompt."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`dev-fixer`)"]
trigger = "User selection of '🐞 Fix a specific bug'."
success_criteria = [
    "Coordinator successfully obtains initial bug details (description, location hints) from the user.",
    "Task successfully delegated to `dev-fixer` with the gathered context.",
    "Coordinator informs the user that the bug fixing process has started."
]
failure_criteria = [
    "User cancels the process or provides insufficient bug details.",
    "Delegation to `dev-fixer` fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Bug fixing might have its own QA later
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing, especially context gathering effectiveness."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Fix a Specific Bug

## 1. Objective 🎯
*   To collect initial information about a bug the user wants to fix and initiate the debugging and resolution process by delegating to the `dev-fixer` mode.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Gathers initial bug description and context from the user, delegates to `dev-fixer`, reports initiation.
*   **User:** Provides details about the bug (what, where, how to reproduce).
*   **Delegate (`dev-fixer`):** Executes the detailed debugging and fixing process according to its own workflow.

## 3. Procedure Steps 🪜

*   **Step 1: Gather Bug Details (Coordinator Task)**
    *   **Description:** Prompt the user for essential information about the bug.
    *   **Inputs:** User selected "🐞 Fix a specific bug".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, let's squash that bug! Please tell me about it. Helpful details include:
              - What is the bug? (Describe the incorrect behavior)
              - Where does it happen? (e.g., File paths, Component names, URL)
              - How can I reproduce it? (Steps, specific inputs)
              - Any error messages or logs? (Paste relevant snippets if possible)
              </question>
              <follow_up>
                <suggest>Cancel bug fixing</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store it as `[Bug Details]`.
    *   **Outputs:** `[Bug Details]` provided by the user.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling bug fixing. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the details are very sparse, prompt again asking for specifics ("Could you please provide the file path where the error occurs, or any error message you see?").

*   **Step 2: Delegate to Bug Fixer (Coordinator delegates to `dev-fixer`)**
    *   **Description:** Hand off the bug information and the fixing task to the `dev-fixer` specialist.
    *   **Inputs:** `[Bug Details]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for the `dev-fixer` task (e.g., `TASK-FIX-YYYYMMDD-HHMMSS`).
        2.  Log the delegation action in the Coordinator's log (Rule `08`).
        3.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>dev-fixer</mode>
              <message>
              🐞 Bug Fixing Task: Please analyze and fix the bug described below.
              User Provided Details:
              ---
              [Bug Details]
              ---
              Follow your standard debugging workflow: understand, reproduce, isolate cause, propose/implement fix, verify. Ask clarifying questions if needed. Log your progress in your task file.
              Your Task ID: [Generated TASK-FIX-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `dev-fixer`.
    *   **Error Handling:** If `new_task` fails, log the error, report "Failed to initiate bug fixing process due to a delegation error." to the user via `attempt_completion`, and stop.

*   **Step 3: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that the bug has been assigned for investigation.
    *   **Inputs:** Successful delegation in Step 2.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "Okay, I've passed the bug details to the Bug Fixer (`dev-fixer`). They will start investigating and may ask for more information. Please follow their prompts."
    *   **Outputs:** User is informed, control is passed to `dev-fixer` for the next steps.
    *   **Error Handling:** N/A.

## 4. Postconditions ✅
*   Initial bug details have been collected from the user.
*   The `dev-fixer` mode has been delegated the task of diagnosing and fixing the bug.
*   The user has been informed that the bug fixing process is starting.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   This workflow quickly gathers necessary initial context for the bug fixer.
*   It leverages the specialized `dev-fixer` mode for the systematic debugging process.
*   It sets the expectation for the user that the `dev-fixer` will likely take the lead in the subsequent interaction.
*   Optionally, the Coordinator could first create an MDTM Bug task file using template `02_mdtm_bug.md`, populate it with `[Bug Details]`, and then delegate using the file path, but for initial bug reports, direct delegation to `dev-fixer` might be more efficient. The `dev-fixer` can then create the formal task file if needed as part of its process.