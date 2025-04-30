+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-03-CLONE"
title = "KB: Initial Action - Clone Git Repository & Onboard"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "clone", "git", "onboarding"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/dev-git/dev-git.mode.md",
    ".ruru/modes/manager-onboarding/manager-onboarding.mode.md",
    ".ruru/modes/manager-onboarding/kb/02-workflow.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Prompt the user for a Git repository URL, clone the repository into the workspace (optionally into a specific subdirectory), and then delegate the standard onboarding process for the newly cloned repository to `manager-onboarding`."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Clone a Git repository & onboard' option from the initial prompt."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`dev-git`)", "Delegate (`manager-onboarding`)"]
trigger = "User selection of '🌐 Clone a Git repository & onboard'."
success_criteria = [
    "Coordinator successfully obtains a Git repository URL from the user.",
    "`dev-git` successfully clones the repository into the specified directory.",
    "Task successfully delegated to `manager-onboarding` with 'existing' intent for the cloned directory.",
    "Coordinator informs the user that cloning is complete and onboarding has started."
]
failure_criteria = [
    "User cancels the process or provides an invalid URL.",
    "`dev-git` fails to clone the repository (e.g., authentication error, repo not found, directory exists).",
    "Delegation to `manager-onboarding` fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Primarily coordination/delegation
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing in practice, especially error handling for clone failures."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Clone Git Repository & Onboard

## 1. Objective 🎯
*   To obtain a Git repository URL from the user, clone it locally, and then initiate the standard onboarding process for the cloned repository via `manager-onboarding`.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Prompts user for URL/directory, delegates clone to `dev-git`, handles clone result, delegates onboarding to `manager-onboarding`, reports status.
*   **User:** Provides repository URL and optional directory name, confirms actions.
*   **Delegate (`dev-git`):** Executes the `git clone` command.
*   **Delegate (`manager-onboarding`):** Executes the detailed existing project onboarding workflow for the cloned repository.

## 3. Procedure Steps 🪜

*   **Step 1: Get Repository URL (Coordinator Task)**
    *   **Description:** Prompt the user for the repository URL they wish to clone.
    *   **Inputs:** User selected "🌐 Clone a Git repository & onboard".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Please provide the HTTPS or SSH URL of the Git repository you want to clone and onboard.</question>
              <follow_up>
                <suggest>Cancel cloning</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store it as `[Repo URL]`.
    *   **Outputs:** `[Repo URL]` provided by the user.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling clone operation. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the response doesn't look like a URL, ask again for a valid URL.

*   **Step 2: Get Optional Directory Name (Coordinator Task)**
    *   **Description:** Ask the user if they want to clone into a specific subdirectory, otherwise use the default name derived from the URL.
    *   **Inputs:** `[Repo URL]`.
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Infer the default directory name from the URL (e.g., `https://github.com/jezweb/roo-commander.git` -> `roo-commander`). Let this be `[Default Dir Name]`.
        2.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>The repository will be cloned into a directory named '`[Default Dir Name]`' inside your current workspace (`{Current Working Directory}`). Is this okay, or do you want to specify a different directory name?</question>
              <follow_up>
                <suggest>Yes, clone into '`[Default Dir Name]`'</suggest>
                <suggest>Let me specify a different directory name...</suggest>
                <suggest>Cancel cloning</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        3.  Await user response.
        4.  If user selects "Yes", set `[Target Dir]` = `[Default Dir Name]`.
        5.  If user selects "Let me specify...", ask for the name and store it as `[Target Dir]`. Validate it's a safe relative path segment.
        6.  If user selects "Cancel", handle cancellation as in Step 1.
    *   **Outputs:** `[Target Dir]` (relative path segment).
    *   **Error Handling:** Handle cancellation. Validate user-provided directory name is simple (no `../`, `/`, etc.).

*   **Step 3: Delegate Clone Task (Coordinator delegates to `dev-git`)**
    *   **Description:** Instruct `dev-git` to perform the clone operation.
    *   **Inputs:** `[Repo URL]`, `[Target Dir]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for the `dev-git` task (e.g., `TASK-GIT-YYYYMMDD-HHMMSS`).
        2.  Log the delegation action in the Coordinator's log (Rule `08`).
        3.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>dev-git</mode>
              <message>
              Clone the repository from '[Repo URL]' into the relative directory '`[Target Dir]`'. Use the command 'git clone "[Repo URL]" "`[Target Dir]`"'. Report success or failure, including any specific error messages from Git (e.g., authentication failed, repository not found, directory already exists).
              Your Task ID: [Generated TASK-GIT-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
        4.  Await `attempt_completion` from `dev-git`.
    *   **Outputs:** Success or Failure result from `dev-git`, including error details.
    *   **Error Handling (Coordinator):**
        *   If `dev-git` reports failure (e.g., auth error, repo not found, dir exists): Log the failure, report the *specific error* from `dev-git` to the user via `attempt_completion`, and explain that onboarding cannot proceed. **Stop this workflow.**
        *   If `new_task` itself fails: Log the error, report "Failed to initiate clone task due to a delegation error." to the user via `attempt_completion`, and stop.

*   **Step 4: Delegate Onboarding (Coordinator delegates to `manager-onboarding`)**
    *   **Description:** Hand off the analysis and onboarding process for the newly cloned repository.
    *   **Inputs:** Successful clone confirmation from Step 3, `[Target Dir]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for `manager-onboarding` (e.g., `TASK-ONBOARD-...`).
        2.  Log the delegation in the Coordinator's log (Rule `08`).
        3.  Construct the full path to the cloned directory: `[Cloned Path]` = `{Current Working Directory}/{Target Dir}` (adjust path separator based on OS if necessary).
        4.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>manager-onboarding</mode>
              <message>
              🎯 Project Onboarding (Existing Project - Cloned): Initiate the onboarding process for the newly cloned project in directory '`[Target Dir]`' (Full path: '`[Cloned Path]`').
              Intent: 'existing'
              Goal: Perform stack detection, gather context/requirements outline, ensure journal structure exists, and report completion.
              Follow your standard workflow defined in `.ruru/modes/manager-onboarding/kb/02-workflow.md`.
              Your Task ID: [Generated TASK-ONBOARD-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `manager-onboarding`.
    *   **Error Handling:** If the `new_task` tool fails, log the error, report "Successfully cloned repository, but failed to initiate onboarding process due to a delegation error." to the user via `attempt_completion`, and stop.

*   **Step 5: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that cloning was successful and onboarding is starting.
    *   **Inputs:** Successful delegation in Step 4.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "✅ Repository successfully cloned into '`[Target Dir]`'. I've now asked the Project Onboarding manager (`manager-onboarding`) to analyze the project and guide the next steps. Please follow their prompts."
    *   **Outputs:** User is informed, control passed to `manager-onboarding`.
    *   **Error Handling:** N/A.

## 4. Postconditions ✅
*   The specified Git repository is cloned into the target local directory.
*   The `manager-onboarding` mode has been delegated the task of performing the onboarding workflow for the cloned repository.
*   The user has been informed about the successful clone and the start of the onboarding process.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   Separates cloning (handled by `dev-git`) from onboarding (handled by `manager-onboarding`).
*   Includes user confirmation for the target directory name.
*   Provides basic error handling for common clone failures.
*   Ensures the onboarding manager receives the correct context (intent 'existing' and the path to the cloned code).