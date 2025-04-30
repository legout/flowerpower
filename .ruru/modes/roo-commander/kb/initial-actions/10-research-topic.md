+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-10-RESEARCH"
title = "KB: Initial Action - Research Topic / Ask Question"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "research", "question-answering", "agent-research"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/agent-research/agent-research.mode.md"
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Gather the research topic or technical question from the user and delegate the information gathering and synthesis task to the `agent-research` specialist mode."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Research a topic / Ask a technical question' option."
roles = ["Coordinator (Roo Commander)", "User", "Delegate (`agent-research`)"]
trigger = "User selection of '❓ Research a topic / Ask a technical question'."
success_criteria = [
    "Coordinator successfully obtains the research topic or question from the user.",
    "Task successfully delegated to `agent-research` with the gathered context.",
    "Coordinator informs the user that the research process has started."
]
failure_criteria = [
    "User cancels the process or provides an unclear topic/question.",
    "Delegation to `agent-research` fails.",
    "Coordinator fails to report status back to the user."
]

# --- Integration ---
acqa_applicable = false # Research summary might be reviewed, but not typical ACQA
pal_validated = false # Needs validation
validation_notes = "Procedure needs testing."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "detailed"
+++

# KB: Initial Action - Research Topic / Ask Question

## 1. Objective 🎯
*   To understand the user's research needs or technical question and initiate the investigation process by delegating to the `agent-research` mode.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Gathers the research topic/question, delegates to `agent-research`, reports initiation.
*   **User:** Provides the specific topic or question for research.
*   **Delegate (`agent-research`):** Executes the detailed research workflow (searching sources, synthesizing findings, citing sources) according to its own procedures.

## 3. Procedure Steps 🪜

*   **Step 1: Get Research Topic/Question (Coordinator Task)**
    *   **Description:** Prompt the user for the specific topic or question they need information on.
    *   **Inputs:** User selected "❓ Research a topic / Ask a technical question".
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present the prompt:
            ```xml
             <ask_followup_question>
              <question>Okay, I can help with research or answering technical questions. What topic or specific question do you have in mind?</question>
              <follow_up>
                <suggest>Cancel research</suggest>
              </follow_up>
             </ask_followup_question>
            ```
        2.  Await user response. Store it as `[Research Query]`.
    *   **Outputs:** `[Research Query]` provided by the user.
    *   **Error Handling:** If the user cancels, report "Okay, cancelling research task. What would you like to do instead?" using `ask_followup_question` and re-present the initial 16 options. **Stop this workflow.** If the query is very vague (e.g., "research"), prompt again for a more specific topic or question.

*   **Step 2: Delegate to Research Agent (Coordinator delegates to `agent-research`)**
    *   **Description:** Hand off the research query to the `agent-research` specialist.
    *   **Inputs:** `[Research Query]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate a Task ID for the `agent-research` task (e.g., `TASK-RESEARCH-YYYYMMDD-HHMMSS`).
        2.  Log the delegation action in the Coordinator's log (Rule `08`).
        3.  Formulate the delegation message:
            ```xml
            <new_task>
              <mode>agent-research</mode>
              <message>
              ❓ Research Request: Please research the following topic/question:
              ---
              [Research Query]
              ---
              Follow your standard workflow: plan strategy, gather information (web, files if specified), evaluate sources, synthesize findings into a structured summary with citations, and save the report.
              Your Task ID: [Generated TASK-RESEARCH-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
    *   **Outputs:** Task delegated to `agent-research`.
    *   **Error Handling:** If `new_task` fails, log the error, report "Failed to initiate research task due to a delegation error." to the user via `attempt_completion`, and stop.

*   **Step 3: Inform User & Conclude Initial Action (Coordinator Task)**
    *   **Description:** Inform the user that the research task has been assigned.
    *   **Inputs:** Successful delegation in Step 2.
    *   **Tool:** `attempt_completion`
    *   **Procedure:**
        1.  Send a completion message: "Okay, I've asked the Research Agent (`agent-research`) to look into '[Brief summary of Research Query]'. They will provide a summary report upon completion. This may take some time depending on the complexity."
    *   **Outputs:** User is informed, control is passed to `agent-research` for the next steps.
    *   **Error Handling:** N/A.

## 4. Postconditions ✅
*   The user's research topic or technical question has been captured.
*   The `agent-research` mode has been delegated the task of performing the research and synthesis.
*   The user has been informed that the research process is starting.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   This workflow ensures research tasks are handled by a dedicated agent capable of searching external sources and synthesizing information.
*   It clearly separates the Coordinator's role (gathering the query, delegating) from the Researcher's role (performing the actual research).
*   Setting user expectations about the time research might take is important.