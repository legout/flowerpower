+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-11-EXECDEL"
title = "KB: Initial Action - Execute Command or Delegate Specific Task"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "execute", "command", "delegate", "direct-task"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".roo/rules/05-os-aware-commands.md", # Workspace rule for OS awareness
    ".roo/rules-roo-commander/07-safety-protocols-rule.md", # Contains sensitive operation confirmation rule
    ".ruru/modes/roo-commander/kb/kb-available-modes-summary.md" # To check mode validity
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Allow the user to directly specify either a shell command to execute or a task to delegate to a known specialist mode, bypassing higher-level planning."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Execute a command / Delegate a specific known task' option. It handles either direct command execution (with safety checks) or direct delegation to a user-specified mode."
roles = ["Coordinator (Roo Commander)", "User", "Executor (Terminal via `execute_command`)", "Delegate (Specific Mode via `new_task`)"]
trigger = "User selection of '🛠️ Execute a command / Delegate a specific known task'."
success_criteria = [
    "Coordinator successfully obtains the specific command or delegation details.",
    "If a command, it is executed successfully (potentially after user confirmation for risky commands).",
    "If a delegation, the task is successfully sent to the specified valid mode.",
    "Coordinator reports the outcome (success/failure, output/result) to the user."
]
failure_criteria = [
    "User cancels the process or provides unclear instructions.",
    "User declines confirmation for a risky command.",
    "Command execution fails (non-zero exit code, errors).",
    "Specified delegate mode slug is invalid.",
    "Delegation via `new_task` fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Direct execution/delegation
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing, especially the command safety checks and mode validation."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Execute Command or Delegate Specific Task

## 1. Objective 🎯
*   To directly execute a shell command provided by the user or delegate a task to a specific mode as requested by the user, bypassing the usual planning stages.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Prompts for details, determines action type (command vs. delegation), performs safety checks on commands, validates mode slugs, executes/delegates, reports outcome.
*   **User:** Provides the exact command or the target mode slug and task description. Confirms risky commands.
*   **Executor (Terminal):** Runs the shell command via `execute_command`.
*   **Delegate (Specific Mode):** Receives and executes the task via `new_task`.

## 3. Procedure Steps 🪜

*   **Step 1: Get Command or Delegation Details (Coordinator Task)**
    *   **Description:** Prompt the user for either the exact shell command (including arguments and optionally `cwd`) or the target mode slug and task description.
    *   **Inputs:** User selected "🛠️ Execute a command / Delegate...".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, direct action! Please provide EITHER:
              1.  The **exact shell command** you want to run (e.g., `npm install`, `git status`). Specify `cwd` if not the workspace root.
              OR
              2.  The **target mode slug** (e.g., `dev-react`) AND a **clear task description**.
              </question>
              <follow_up>
                <suggest>Example Command: ls -l src/</suggest>
                <suggest>Example Delegation: Mode: util-writer, Task: Update README.md title</suggest>
                <suggest>Cancel direct action</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store it as `[Action Details]`.
    *   **Outputs:** `[Action Details]` containing either a command string or mode+task description.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling direct action. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the response is unclear whether it's a command or delegation, ask for clarification.

*   **Step 2: Determine Action Type (Coordinator Task)**
    *   **Description:** Analyze `[Action Details]` to determine if it's a command execution request or a delegation request.
    *   **Inputs:** `[Action Details]`.
    *   **Procedure:**
        1.  Check if the response clearly identifies a target mode slug (e.g., starts with "Mode: `mode-slug`").
        2.  If Yes -> It's a Delegation. Proceed to **Step 3A**.
        3.  If No -> Assume it's a Command. Proceed to **Step 3B**.
    *   **Outputs:** Decision (Delegation or Command).

*   **Step 3A: Handle Delegation Request (Coordinator Task)**
    *   **Description:** Validate the mode slug and delegate the task.
    *   **Inputs:** `[Action Details]` (parsed mode slug and task description).
    *   **Tools:** `read_file` (optional), `new_task`, `attempt_completion`
    *   **Procedure:**
        1.  Extract `[Target Mode Slug]` and `[Task Description]` from `[Action Details]`.
        2.  *(Optional but Recommended)* Read the mode summary KB (`.ruru/modes/roo-commander/kb/kb-available-modes-summary.md`) to verify `[Target Mode Slug]` is a valid, known mode. If invalid, report error to user via `attempt_completion` ("Error: Mode slug '[Target Mode Slug]' not found.") and stop.
        3.  Generate a Task ID for the delegate (e.g., `TASK-[SLUG]-...`).
        4.  Log the delegation action (Rule `08`).
        5.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>[Target Mode Slug]</mode>
              <message>
              🛠️ Direct Task: Please execute the following task as requested by the user:
              ---
              [Task Description]
              ---
              Your Task ID: [Generated TASK-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
        6.  Inform user via `attempt_completion`: "Okay, I've delegated the task '[Short Task Summary]' to the `{Delegate Mode Name}` (`[Target Mode Slug]`). Monitoring for completion."
    *   **Outputs:** Task delegated. User informed. Control passes to the delegated mode.
    *   **Error Handling:** Handle invalid mode slug. Handle `new_task` tool failure (log, report to user, stop).

*   **Step 3B: Handle Command Execution Request (Coordinator Task)**
    *   **Description:** Perform safety checks and execute the user-provided command.
    *   **Inputs:** `[Action Details]` (command string, optional `cwd`).
    *   **Tools:** `ask_followup_question` (for confirmation), `execute_command`, `attempt_completion`
    *   **Procedure:**
        1.  Extract `[Command String]` and `[CWD]` (if specified, default to `.`).
        2.  **Analyze Command for Risk:** Check if `[Command String]` contains potentially destructive patterns (e.g., `rm -rf`, `git reset --hard`, `git push --force`, `dd`, `mkfs`, etc.). Refer to Safety Rule `07`.
        3.  **Request Confirmation (If Risky):**
            *   If the command is deemed risky: Use `ask_followup_question`:
                ```xml
                 <ask_followup_question>
                  <question>⚠️ **Safety Check:** The command you provided (`[Command String]`) appears potentially destructive or irreversible. Are you absolutely sure you want to execute it?</question>
                  <follow_up>
                    <suggest>Yes, execute the command</suggest>
                    <suggest>No, cancel the command</suggest>
                  </follow_up>
                 </ask_followup_question>
                ```
            *   Await user response. If "No" or cancelled, report "Command execution cancelled by user." via `attempt_completion` and stop. Log cancellation (Rule `08`).
            *   If "Yes", log user confirmation (Rule `08`).
        4.  **Execute Command:**
            *   Log the command execution attempt (Rule `08`).
            *   Use `execute_command`:
                ```xml
                <execute_command>
                  <command>[Command String]</command>
                  <cwd>[CWD]</cwd>
                  <timeout_seconds>60</timeout_seconds> <!-- Example timeout -->
                </execute_command>
                ```
        5.  **Process Result:**
            *   Analyze the `stdout`, `stderr`, and `exit_code` from the `execute_command` result.
            *   Log the result (Rule `08`).
            *   Report the outcome to the user via `attempt_completion`. Include:
                *   Success/Failure indication.
                *   Exit code.
                *   Relevant `stdout` and `stderr` (potentially truncated if very long).
    *   **Outputs:** Command executed (or cancelled). Result reported to user.
    *   **Error Handling:** Handle `execute_command` tool failures. Clearly report non-zero exit codes and stderr content to the user.

## 4. Postconditions ✅
*   **Command Path:** The specified command has been executed (or cancelled after safety check), and the result (output, errors, exit code) reported to the user.
*   **Delegation Path:** The specified task has been delegated to the target specialist mode, and the user has been informed.

## 5. Rationale / Notes 🤔
*   Provides a direct execution/delegation pathway for users who know what they need.
*   Includes crucial safety checks for potentially destructive commands, requiring explicit user confirmation.
*   Includes validation for delegated mode slugs.
*   Bypasses planning/analysis stages, assuming the user has already performed them.