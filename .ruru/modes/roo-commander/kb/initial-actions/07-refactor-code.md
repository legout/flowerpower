+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-07-REFACTOR"
title = "KB: Initial Action - Refactor or Improve Code"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "refactor", "code-quality", "util-refactor"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/util-refactor/util-refactor.mode.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Gather the target code location(s) and the primary goal for refactoring, then delegate the task to the `util-refactor` specialist mode."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Refactor or improve existing code' option."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`util-refactor`)"]
trigger = "User selection of '♻️ Refactor or improve existing code'."
success_criteria = [
    "Coordinator successfully obtains the refactoring target (file/function) and goal from the user.",
    "Task successfully delegated to `util-refactor` with the gathered context.",
    "Coordinator informs the user that the refactoring process has started."
]
failure_criteria = [
    "User cancels the process or provides insufficient details.",
    "Delegation to `util-refactor` fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Refactoring often has specific review needs, but not standard ACQA
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing, ensuring adequate context capture for the refactorer."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Refactor or Improve Code

## 1. Objective 🎯
*   To identify the specific code the user wants to refactor and understand the primary goal (e.g., improve readability, reduce duplication, extract logic), then initiate the refactoring process by delegating to the `util-refactor` mode.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Gathers refactoring target and goals, delegates to `util-refactor`, reports initiation.
*   **User:** Provides the code location(s) and the main objective for refactoring.
*   **Delegate (`util-refactor`):** Executes the detailed refactoring process according to its own workflow, ensuring no behavioral changes are introduced.

## 3. Procedure Steps 🪜

*   **Step 1: Gather Refactoring Target & Goal (Coordinator Task)**
    *   **Description:** Prompt the user for the specific code to refactor and the desired improvement.
    *   **Inputs:** User selected "♻️ Refactor or improve existing code".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, let's improve some code! Please tell me:
              1.  **Which code** needs refactoring? (e.g., Specific file path(s), function names, class names)
              2.  What is the **main goal**? (e.g., Improve readability, reduce duplication, extract a reusable component, simplify complex logic)
              </question>
              <follow_up>
                <suggest>Cancel refactoring</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store it as `[Refactor Details]`.
    *   **Outputs:** `[Refactor Details]` provided by the user, containing target and goal.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling refactoring. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the details are unclear (e.g., missing file path or goal), prompt again for the missing information.

*   **Step 2: Delegate to Refactor Specialist (Coordinator delegates to `util-refactor`)**
    *   **Description:** Hand off the refactoring task to the `util-refactor` specialist.
    *   **Inputs:** `[Refactor Details]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for the `util-refactor` task (e.g., `TASK-REFACTOR-YYYYMMDD-HHMMSS`).
        2.  Log the delegation action in the Coordinator's log (Rule `08`).
        3.  Formulate the delegation message, clearly separating the target code and the goal:
            ```xml
            <new_task>
              <mode>util-refactor</mode>
              <message>
              ♻️ Refactoring Task: Please refactor the specified code without changing its external behavior.
              User Provided Details:
              ---
              [Refactor Details]
              ---
              Focus on the stated goal (e.g., readability, duplication). Follow your standard refactoring workflow: analyze, identify smells, apply refactoring patterns safely (check for tests), verify behavior remains unchanged, and report the specific changes made.
              Your Task ID: [Generated TASK-REFACTOR-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `util-refactor`.
    *   **Error Handling:** If `new_task` fails, log the error, report "Failed to initiate refactoring process due to a delegation error." to the user via `attempt_completion`, and stop.

*   **Step 3: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that the refactoring task has been assigned.
    *   **Inputs:** Successful delegation in Step 2.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "Okay, I've assigned the refactoring task to the Refactor Specialist (`util-refactor`). They will analyze the code and propose improvements based on your goal. Please follow their prompts."
    *   **Outputs:** User is informed, control is passed to `util-refactor` for the next steps.
    *   **Error Handling:** N/A.

## 4. Postconditions ✅
*   The target code and refactoring goal have been identified.
*   The `util-refactor` mode has been delegated the task of performing the refactoring.
*   The user has been informed that the refactoring process is starting.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   This workflow focuses on gathering the essential 'what' and 'why' for the refactoring task before handing off.
*   It leverages the specialized `util-refactor` mode, which understands the principles of behavior-preserving code improvements.
*   The refactoring process itself (analysis, specific changes, verification) is handled by the specialist mode according to its internal guidelines.