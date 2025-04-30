+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-08-DOCS"
title = "KB: Initial Action - Write or Update Documentation"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "documentation", "technical-writing", "util-writer"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/util-writer/util-writer.mode.md",
    ".ruru/templates/toml-md/09_documentation.md", # General doc template
    ".ruru/templates/toml-md/10_guide_tutorial.md" # Guide template
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Gather the topic, target audience, purpose, and source materials for documentation, then delegate the writing/updating task to the `util-writer` specialist mode."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Write or update documentation' option."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`util-writer`)"]
trigger = "User selection of '✍️ Write or update documentation'."
success_criteria = [
    "Coordinator successfully obtains the documentation requirements (topic, audience, purpose, sources) from the user.",
    "Task successfully delegated to `util-writer` with the gathered context.",
    "Coordinator informs the user that the documentation process has started."
]
failure_criteria = [
    "User cancels the process or provides insufficient details.",
    "Delegation to `util-writer` fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Documentation writing might have its own review, but not typical ACQA
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing, especially context gathering."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Write or Update Documentation

## 1. Objective 🎯
*   To understand the user's documentation needs (what to document, for whom, why, based on what sources) and initiate the writing or updating process by delegating to the `util-writer` mode.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Gathers documentation requirements, delegates to `util-writer`, reports initiation.
*   **User:** Provides details about the documentation needed (topic, audience, sources, purpose).
*   **Delegate (`util-writer`):** Executes the detailed documentation writing/updating process according to its own workflow.

## 3. Procedure Steps 🪜

*   **Step 1: Gather Documentation Requirements (Coordinator Task)**
    *   **Description:** Prompt the user for details about the documentation they need.
    *   **Inputs:** User selected "✍️ Write or update documentation".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, let's work on some documentation! To help me delegate this effectively, please provide some details:
              1.  **What topic** should be documented? (e.g., a specific feature, API endpoint, setup process, concept)
              2.  **Who is the target audience?** (e.g., New Developers, End Users, API Consumers)
              3.  **What is the purpose?** (e.g., User Guide, Tutorial, API Reference, README)
              4.  **Are there source materials?** (e.g., Code file paths, task IDs, existing docs, design specs)
              </question>
              <follow_up>
                <suggest>Cancel documentation task</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store it as `[Doc Details]`.
    *   **Outputs:** `[Doc Details]` provided by the user.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling documentation task. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the details are insufficient (e.g., missing topic or audience), prompt again for the missing information.

*   **Step 2: Delegate to Technical Writer (Coordinator delegates to `util-writer`)**
    *   **Description:** Hand off the documentation task to the `util-writer` specialist.
    *   **Inputs:** `[Doc Details]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for the `util-writer` task (e.g., `TASK-WRITE-YYYYMMDD-HHMMSS`).
        2.  Log the delegation action in the Coordinator's log (Rule `08`).
        3.  Formulate the delegation message, passing the gathered details:
            ```xml
            <new_task>
              <mode>util-writer</mode>
              <message>
              ✍️ Documentation Task: Please write or update documentation based on the following details.
              User Provided Details:
              ---
              [Doc Details]
              ---
              Focus on creating clear, accurate, and audience-appropriate content. Structure the information logically. Use the specified source materials and ask clarifying questions if needed (via your coordinator). Log your progress in your task file.
              Your Task ID: [Generated TASK-WRITE-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `util-writer`.
    *   **Error Handling:** If `new_task` fails, log the error, report "Failed to initiate documentation task due to a delegation error." to the user via `attempt_completion`, and stop.

*   **Step 3: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that the documentation task has been assigned.
    *   **Inputs:** Successful delegation in Step 2.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "Okay, I've passed the documentation request to the Technical Writer (`util-writer`). They will start working on it based on the details you provided and may ask for more information via me if needed."
    *   **Outputs:** User is informed, control is passed to `util-writer` for the next steps.
    *   **Error Handling:** N/A.

## 4. Postconditions ✅
*   The documentation requirements (topic, audience, purpose, sources) have been gathered.
*   The `util-writer` mode has been delegated the task of creating or updating the documentation.
*   The user has been informed that the documentation process is starting.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   This workflow focuses on capturing the essential parameters needed for a technical writer to start work.
*   It leverages the specialized `util-writer` mode for the actual content creation and structuring.
*   The `util-writer` is responsible for following its own detailed process, including potentially asking for clarification or delegating sub-tasks (like diagram creation) back through the Coordinator.