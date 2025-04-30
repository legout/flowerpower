+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-14-LEARN"
title = "KB: Initial Action - Learn About Roo Commander Capabilities"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "capabilities", "help", "modes", "documentation"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/roo-commander/kb/kb-available-modes-summary.md", # Key source
    "README.md" # Project README often contains overview
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Provide the user with a summary of Roo Commander's available modes and general capabilities, primarily by referencing the mode summary document."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Learn about Roo Commander capabilities' option."
roles = ["Coordinator (Roo Commander)", "User"]
trigger = "User selection of '📖 Learn about Roo Commander capabilities'."
success_criteria = [
    "Coordinator successfully reads the mode summary KB file.",
    "Coordinator presents a concise overview of capabilities and the mode list to the user.",
    "User receives the requested information."
]
failure_criteria = [
    "The mode summary KB file (`kb-available-modes-summary.md`) cannot be read.",
    "Coordinator fails to present the information.",
    "User indicates the information was insufficient or unclear."
]

# --- Integration ---
acqa_applicable = false # Information retrieval
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Learn About Roo Commander Capabilities

## 1. Objective 🎯
*   To provide the user with an overview of the available specialist modes and the general capabilities of the Roo Commander system within the current workspace setup.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Reads the mode summary, presents information, potentially links to further docs.
*   **User:** Receives the information.

## 3. Procedure Steps 🪜

*   **Step 1: Read Mode Summary (Coordinator Task)**
    *   **Description:** Access the centrally maintained list of available modes.
    *   **Inputs:** None required beyond the trigger.
    *   **Tool:** `read_file`
    *   **Procedure:**
        1.  Use `read_file` to get the content of `.ruru/modes/roo-commander/kb/kb-available-modes-summary.md`. Store content as `[Mode Summary Content]`.
    *   **Outputs:** `[Mode Summary Content]` (Markdown).
    *   **Error Handling:** If `read_file` fails, report "Sorry, I encountered an error trying to retrieve the list of available modes. Please check if the file `.ruru/modes/roo-commander/kb/kb-available-modes-summary.md` exists and is readable." using `attempt_completion` and stop.

*   **Step 2: Present Information (Coordinator Task)**
    *   **Description:** Display the overview and list of modes to the user.
    *   **Inputs:** `[Mode Summary Content]`.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Formulate the response message, including a brief explanation and the content read from the summary file:
            ```markdown
            Okay, here's an overview of the modes I can coordinate:

            I act as a central coordinator, understanding your goals and delegating tasks to specialized modes like developers (React, Python, etc.), testers, designers, infrastructure specialists, and more. We use a structured task system (MDTM) for tracking complex work.

            Here is the current list of available specialist modes based on the `.ruru/modes/roo-commander/kb/kb-available-modes-summary.md` file:

            ---
            {{Mode Summary Content}}
            ---

            You can usually ask me to perform a task related to one of these areas (e.g., "Implement the login UI using React", "Write E2E tests for the checkout flow", "Design the database schema for products"). For more details, you might also want to check the main project `README.md`.

            What would you like to do next? *(Present the initial 16 options again via `ask_followup_question` or await next user prompt)*
            ```
        2.  Replace `{{Mode Summary Content}}` with the actual Markdown content stored in `[Mode Summary Content]`.
        3.  Send the information using `attempt_completion`.
        4.  *(Self-Correction/Refinement):* Immediately follow up with `ask_followup_question` presenting the standard 16 initial options to guide the user's next action.
    *   **Outputs:** Information presented to the user.
    *   **Error Handling:** N/A for this step (error handled in Step 1).

## 4. Postconditions ✅
*   The user has been presented with an overview of Roo Commander's role and a list of available specialist modes.
*   The user has been prompted for their next action.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   Provides a direct way for users to understand the system's structure and available expertise.
*   Relies on the accuracy and completeness of the centrally managed `kb-available-modes-summary.md` file (which should be updated when modes are added/removed, potentially via a build script or the `new_mode_creation_workflow`).
*   Directly outputs the content of the summary file for simplicity and maintainability.