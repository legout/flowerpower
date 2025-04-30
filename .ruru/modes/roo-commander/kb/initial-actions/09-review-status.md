+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-09-STATUS"
title = "KB: Initial Action - Review Project Status / Manage Tasks"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "status", "review", "mdtm", "task-management", "manager-project", "agent-context-resolver"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/manager-project/manager-project.mode.md",
    ".ruru/modes/agent-context-resolver/agent-context-resolver.mode.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Determine the user's area of interest for status review or task management, and delegate the task to the appropriate mode (`manager-project` for MDTM-based management, `agent-context-resolver` for general status summaries)."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Review project status / Manage tasks (MDTM)' option."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`manager-project` or `agent-context-resolver`)"]
trigger = "User selection of '📊 Review project status / Manage tasks (MDTM)'."
success_criteria = [
    "Coordinator successfully obtains the user's area of focus.",
    "Coordinator correctly identifies if MDTM is in use for the focus area.",
    "Task successfully delegated to the appropriate mode (`manager-project` or `agent-context-resolver`).",
    "Coordinator informs the user that the status review/task management process has started."
]
failure_criteria = [
    "User cancels the process or provides an unclear area of focus.",
    "Coordinator cannot determine if MDTM is applicable.",
    "Delegation to the chosen mode fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Coordination/delegation
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Review Project Status / Manage Tasks

## 1. Objective 🎯
*   To understand which aspect of the project the user wants to review the status of or manage tasks for, and then delegate this to the appropriate agent: `manager-project` if the project utilizes MDTM, or `agent-context-resolver` for a general status summary based on available artifacts.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Gathers user's focus area, determines if MDTM is used, delegates to the appropriate mode, reports initiation.
*   **User:** Specifies the area of interest for status review or task management.
*   **Delegate (`manager-project`):** Handles MDTM-based task viewing, updating, and status reporting.
*   **Delegate (`agent-context-resolver`):** Provides a general status summary based on reading project artifacts like logs, plans, and decisions.

## 3. Procedure Steps 🪜

*   **Step 1: Identify Focus Area (Coordinator Task)**
    *   **Description:** Ask the user what specific feature, epic, task ID, or general area they want to review or manage.
    *   **Inputs:** User selected "📊 Review project status / Manage tasks (MDTM)".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, let's look at the project status or manage some tasks. What specific area are you interested in?
              (e.g., 'Overall project status', 'Status of the Authentication feature', 'Details for task TASK-FEAT-123', 'Tasks assigned to dev-react')
              </question>
              <follow_up>
                <suggest>Show overall project status summary</suggest>
                <suggest>Cancel status review</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store it as `[Focus Area]`.
    *   **Outputs:** `[Focus Area]` specified by the user.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling status review. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the focus is unclear, prompt again for specifics.

*   **Step 2: Determine Workflow (Coordinator Task)**
    *   **Description:** Check if the project seems to be using the MDTM system (i.e., if the `.ruru/tasks/` directory exists and contains relevant files).
    *   **Inputs:** `[Focus Area]`.
    *   **Tool:** `list_files`
    *   **Procedure:**
        1.  Use `list_files` to check for the existence and content of the `.ruru/tasks/` directory.
        2.  Based on the presence of `.ruru/tasks/` and task files (`TASK-...md`), determine if MDTM is likely the appropriate system for the user's `[Focus Area]`.
            *   If the user asked for specific task management ("manage tasks", "update task status", "view tasks for X") AND MDTM files exist -> **Use MDTM Path (Step 3A)**.
            *   If the user asked for a general status summary OR MDTM files do *not* seem relevant/present -> **Use Context Resolver Path (Step 3B)**.
    *   **Outputs:** Decision on which path to follow (MDTM or Context Resolver).

*   **Step 3A: Delegate to Project Manager (Coordinator delegates to `manager-project`)**
    *   **Description:** Hand off the MDTM-related task management or status review to the `manager-project`.
    *   **Inputs:** `[Focus Area]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for `manager-project` (e.g., `TASK-PM-YYYYMMDD-HHMMSS`).
        2.  Log the delegation in the Coordinator's log (Rule `08`).
        3.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>manager-project</mode>
              <message>
              📊 MDTM Status/Management Request: The user wants to review status or manage tasks related to: "[Focus Area]".
              Please interact with the user to fulfill their request using the MDTM files in `.ruru/tasks/`. You can list tasks, show details, update status (based on user input), etc.
              Your Task ID: [Generated TASK-PM-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
        4.  Proceed to Step 4.
    *   **Outputs:** Task delegated to `manager-project`.
    *   **Error Handling:** If `new_task` fails, log the error, report "Failed to delegate to Project Manager due to an error." to the user via `attempt_completion`, and stop.

*   **Step 3B: Delegate to Context Resolver (Coordinator delegates to `agent-context-resolver`)**
    *   **Description:** Request a general status summary based on project artifacts.
    *   **Inputs:** `[Focus Area]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for `agent-context-resolver` (e.g., `TASK-RESOLVE-...`).
        2.  Log the delegation in the Coordinator's log (Rule `08`).
        3.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>agent-context-resolver</mode>
              <message>
              📊 Project Status Request: The user wants a status summary for: "[Focus Area]".
              Please read relevant files in `.ruru/tasks/`, `.ruru/planning/`, `.ruru/decisions/` and provide a concise summary of the current status, recent activity, and any known blockers related to the focus area. Cite your sources.
              Your Task ID: [Generated TASK-RESOLVE-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
        4.  Proceed to Step 4.
    *   **Outputs:** Task delegated to `agent-context-resolver`.
    *   **Error Handling:** If `new_task` fails, log the error, report "Failed to delegate to Context Resolver due to an error." to the user via `attempt_completion`, and stop.

*   **Step 4: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that the request has been assigned.
    *   **Inputs:** Successful delegation in Step 3A or 3B.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Determine the delegate mode (`manager-project` or `agent-context-resolver`).
        2.  Send a completion message: "Okay, I've asked the `{Delegate Mode Name}` (`{Delegate Mode Slug}`) to handle your request regarding '[Focus Area]'. Please follow their prompts or await their summary."
    *   **Outputs:** User is informed, control passed to the delegate mode.
    *   **Error Handling:** N/A.

## 4. Postconditions ✅
*   The user's area of focus for status review/task management has been identified.
*   The task has been delegated to the appropriate mode (`manager-project` or `agent-context-resolver`) based on the applicability of MDTM.
*   The user has been informed that the process is starting.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   This workflow distinguishes between structured task management (MDTM) and general status reporting.
*   It leverages `manager-project` for interacting with the MDTM system if it's in use.
*   It uses `agent-context-resolver` for generating summaries when MDTM isn't applicable or a broader overview is needed.
*   Checking for the `.ruru/tasks/` directory provides a heuristic for determining if MDTM is being used.