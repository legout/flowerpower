# 04 - Delegation & MDTM Workflow

This document details procedures for effective task delegation, emphasizing the use of the Markdown-Driven Task Management (MDTM) workflow for complex or critical tasks. It implements principles from `01-operational-principles.md`.

**Core Delegation Principles**

*   Delegate strategically to the *most appropriate* specialist.
*   Provide clear goals, acceptance criteria, and necessary context.
*   Leverage Stack Profile (`.ruru/context/stack_profile.json`) and mode `tags` for specialist selection.

**Specialist Selection Guidance**

1.  **Analyze Task:** Determine the primary domain and required technologies/skills.
2.  **Consult Stack Profile:** Check `.ruru/context/stack_profile.json` for relevant project technologies and team familiarity.
3.  **Consult Mode Summary:** Review `kb-available-modes-summary.md` (in this KB) or use system knowledge of available modes.
4.  **Match Tags:** Prioritize specialists whose `tags` in their `.mode.md` file closely match the task requirements and Stack Profile entries.
5.  **Specificity:** Prefer more specific specialists (e.g., `framework-react` over `lead-frontend` for React component work) if available and appropriate.
6.  **Generalists:** If no specific specialist matches, select the most relevant generalist Lead or Worker (e.g., `lead-backend`, `dev-general`).
7.  **Log Rationale:** Justify the chosen specialist according to the procedures in `12-logging-procedures.md`.

**Delegation Methods**

*   **Simple Tasks (`new_task` directly):**
    *   **Criteria:** Suitable for straightforward, single-step, read-only, or low-risk tasks that do not require detailed tracking or multiple handoffs.
    *   **Message Content:** Must include:
        *   Clear Goal / Objective.
        *   Acceptance Criteria (how to know it's done).
        *   Relevant context references (Task IDs, file paths, Stack Profile path `.ruru/context/stack_profile.json`, relevant ADRs from `.ruru/decisions/`, planning docs from `.ruru/planning/`).
        *   Mention relevant specialist tags if applicable.
    *   **Example:** `<new_task><mode>agent-context-resolver</mode><message>Summarize decisions related to database choice from .ruru/decisions/.</message></new_task>`

*   **Complex/Critical Tasks (MDTM Workflow):**
    *   **Criteria:** Use for tasks that are:
        *   Multi-step or involve sequential dependencies.
        *   Stateful (require tracking progress across interruptions).
        *   High-risk (e.g., modifying core logic, infrastructure changes, security configurations).
        *   Require detailed tracking, clear handoffs, or auditable progress.
        *   Involve significant file modifications needing careful review.
        *   **Examples:** Implementing a new feature involving multiple components, refactoring a critical module, setting up CI/CD pipelines, performing database migrations.
    *   **Step 1: Create Task File:**
        *   Use `write_to_file` to create `.ruru/tasks/TASK-[MODE]-[YYYYMMDD-HHMMSS].md`.
        *   Use the `01_mdtm_feature.md` or a similar MDTM template from `.ruru/templates/toml-md/`.
        *   **Essential Fields:**
            *   `title`: Clear task title.
            *   `status`: "Pending".
            *   `assignee`: Specialist mode slug (e.g., `framework-react`).
            *   `coordinator`: Commander's Task ID (`TASK-CMD-...`).
            *   `objective`: High-level goal.
            *   `acceptance_criteria`: Specific, measurable criteria for completion.
            *   `context_files`: List relevant files (Stack Profile, requirements, ADRs, etc.).
            *   `checklist`: Detailed, sequential steps for the specialist. Use `- [⏳] Step description...`. Mark steps requiring specialist reporting/confirmation with `📣`.
    *   **Step 2: Delegate via `new_task`:**
        *   Target the chosen specialist mode.
        *   **Message Content:** Primarily point to the task file. Include the Commander's Task ID.
        *   **Example:** `<new_task><mode>framework-react</mode><message>Process MDTM task file: .ruru/tasks/TASK-REACT-20250420-183000.md. Coordinator Task: TASK-CMD-20250420-182500.</message></new_task>`
    *   **Step 3: Log Delegation:**
        *   Log the delegation details (specialist Task ID/file path, rationale) according to the procedures in `12-logging-procedures.md`.

**Monitoring MDTM Tasks:**

*   Await `attempt_completion` from the specialist.
*   If interrupted, use `read_file` on the task file (`.ruru/tasks/TASK-[MODE]-... .md`) to check the checklist status before re-delegating.
*   If stalled, re-delegate using `new_task` pointing to the *existing* task file.