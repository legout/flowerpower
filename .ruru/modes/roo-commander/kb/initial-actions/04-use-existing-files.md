+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-04-FILES"
title = "KB: Initial Action - Use Existing Files for Context"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "existing-project", "onboarding", "context", "planning", "requirements"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/manager-onboarding/manager-onboarding.mode.md",
    ".ruru/modes/manager-onboarding/kb/02-workflow.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Prompt the user for paths to existing project files (plans, requirements, context docs) and delegate the standard onboarding process to `manager-onboarding`, providing these files as the primary context."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Use existing project files/plans...' option. It assumes the current workspace contains the relevant files."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`manager-onboarding`)"]
trigger = "User selection of '📄 Use existing project files/plans to define the work'."
success_criteria = [
    "Coordinator successfully obtains relevant file paths from the user.",
    "Task successfully delegated to `manager-onboarding` with 'existing' intent and the specified file paths.",
    "Coordinator informs the user that onboarding using the provided files has started."
]
failure_criteria = [
    "User cancels the process or provides no useful file paths.",
    "Coordinator cannot verify existence of provided paths (optional check).",
    "Delegation to `manager-onboarding` fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Primarily coordination/delegation
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing, especially path validation/handling."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Use Existing Files for Context

## 1. Objective 🎯
*   To gather specific file paths from the user that contain existing project plans, requirements, or context, and then initiate the onboarding process via `manager-onboarding`, instructing it to prioritize these files.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Prompts user for file paths, validates paths (optional), delegates to `manager-onboarding` with file context, reports initiation.
*   **User:** Provides paths to relevant existing files.
*   **Delegate (`manager-onboarding`):** Executes the detailed existing project onboarding workflow, prioritizing analysis of the provided files.

## 3. Procedure Steps 🪜

*   **Step 1: Prompt for File Paths (Coordinator Task)**
    *   **Description:** Ask the user to list the key files containing existing plans, requirements, or important context.
    *   **Inputs:** User selected "📄 Use existing project files/plans...".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, let's use your existing documents to get started. Please provide the paths (relative to the workspace root `{Current Working Directory}`) to the main files containing your project plans, requirements, or key context. You can list multiple files, separated by spaces or newlines.</question>
              <follow_up>
                <suggest>README.md docs/requirements.md planning/overview.md</suggest>
                <suggest>Cancel onboarding</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store the list/string of paths as `[File Paths String]`.
    *   **Outputs:** `[File Paths String]` provided by the user.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling onboarding operation. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the user provides no paths or seems unsure, prompt again, perhaps suggesting common filenames like `README.md` or `docs/`.

*   **Step 2: Process & Validate Paths (Optional - Coordinator Task)**
    *   **Description:** Parse the user's input into a list of paths and optionally verify their existence.
    *   **Inputs:** `[File Paths String]`.
    *   **Tool:** `list_files` (optional verification)
    *   **Procedure:**
        1.  Parse `[File Paths String]` into an array `[File Paths List]` (split by space/newline, trim whitespace).
        2.  *(Optional but Recommended)*: Iterate through `[File Paths List]`. For each path, use `list_files` with the exact path to check if it exists. If any critical file path provided doesn't exist, inform the user via `ask_followup_question` ("I couldn't find file '[path]'. Please verify the path or provide different files.") and potentially loop back to Step 1 or proceed with valid files.
    *   **Outputs:** Verified or processed `[File Paths List]`.
    *   **Error Handling:** Handle parsing issues or inform user about non-existent critical files.

*   **Step 3: Delegate to Onboarding Manager (Coordinator delegates to `manager-onboarding`)**
    *   **Description:** Hand off the analysis and onboarding process, emphasizing the provided files.
    *   **Inputs:** `[File Paths List]`, Initial User Request message (`[initial_request]`).
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for `manager-onboarding` (e.g., `TASK-ONBOARD-...`).
        2.  Log the delegation action in the Coordinator's log (Rule `08`).
        3.  Format the list of files for the message (e.g., comma-separated or bulleted list). Let this be `[Formatted File List]`.
        4.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>manager-onboarding</mode>
              <message>
              🎯 Project Onboarding (Existing Project - File Context): Initiate the onboarding process for the project in directory '{Current Working Directory}'.
              Initial User Request Context: "[initial_request]"
              Intent: 'existing'
              PRIORITY CONTEXT FILES: The user has provided the following files which should be prioritized during analysis:
              [Formatted File List]
              Goal: Perform stack detection (if needed), analyze the provided files and general project context, ensure journal structure exists, and report completion.
              Follow your standard workflow defined in `.ruru/modes/manager-onboarding/kb/02-workflow.md`.
              Your Task ID: [Generated TASK-ONBOARD-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `manager-onboarding` with specific file context.
    *   **Error Handling:** If `new_task` fails, log the error, report "Failed to initiate onboarding process due to a delegation error." to the user via `attempt_completion`, and stop.

*   **Step 4: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that analysis based on their files is starting.
    *   **Inputs:** Successful delegation in Step 3.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "Okay, I've asked the Project Onboarding manager (`manager-onboarding`) to analyze the project, focusing on the files you provided: [Formatted File List]. Please follow their prompts for the next steps."
    *   **Outputs:** User is informed, control passed to `manager-onboarding`.
    *   **Error Handling:** N/A.

## 4. Postconditions ✅
*   The user has provided paths to relevant existing project files.
*   The `manager-onboarding` mode has been delegated the task of performing the onboarding workflow, prioritizing the user-provided files.
*   The user has been informed that the process is starting.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   This workflow caters to users who already have significant planning or requirements artifacts available.
*   It directs the onboarding process to leverage this existing context efficiently.
*   Optional path validation adds robustness, preventing delegation with incorrect file references.