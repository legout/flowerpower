# 05 - Collaboration, Error Handling & Escalation

This document covers managing dependencies, handling issues (including a consolidated error procedure), and escalating problems during task execution. It implements principles from `01-operational-principles.md`.

**Collaboration & Dependency Management:**

*   Manage dependencies between tasks and specialists. Ensure tasks are delegated in a logical order if one depends on another's output.
*   Log significant coordination actions according to `12-logging-procedures.md`.

**Consolidated Error Handling Procedure:**

This procedure applies when blockers (🧱), failures (❌), unexpected behavior, or safety protocol violations are reported by specialists or identified during monitoring.

1.  **Detection:** Identify the error through specialist reports (`attempt_completion`), monitoring task logs, or observing system behavior.
2.  **Initial Assessment:** Quickly gauge the severity and potential impact. Is it a minor issue, a task blocker, or a critical system failure?
3.  **Logging:** Immediately log the detected error, including relevant context (Task IDs, error messages, observed behavior), following the procedures in `12-logging-procedures.md`. This ensures a record exists even if further analysis is interrupted.
4.  **Analysis:**
    *   Review the specialist's report and relevant task logs (`read_file` for MDTM task files at `.ruru/tasks/TASK-[MODE]-....md`).
    *   Use `agent-context-resolver` based on situational judgment (see `01-operational-principles.md`) if needed to understand the broader project state or historical context.
    *   If the root cause is unclear or complex, consider escalating analysis (see Escalation Paths below).
5.  **Decision & Planning:** Determine the next steps:
    *   Retry the task (potentially with adjusted parameters, the same specialist, or a different one).
    *   Propose an alternative approach or workaround.
    *   Break the task down into smaller, more manageable steps.
    *   Escalate the problem for specialized analysis or decision-making (see Escalation Paths).
    *   Report the issue to the user via `ask_followup_question` to seek guidance or inform them of a significant deviation.
6.  **Log Decision:** Record the chosen course of action and the rationale behind it, following the procedures in `12-logging-procedures.md` (e.g., creating an ADR in `.ruru/decisions/` for significant decisions, updating task logs).
7.  **Recovery/Action:** Implement the decided next steps (e.g., re-delegate the task, initiate escalation).

**Handle Interruption / Lack of Response:**

*   If a delegated MDTM task seems interrupted (no completion received within a reasonable timeframe), use `read_file` on the specific `.ruru/tasks/TASK-[MODE]-....md` file to check the checklist status *before* assuming failure or re-delegating.
*   If the task appears stalled, re-delegate using `new_task` pointing to the *existing* task file, asking the specialist to resume from the last completed step. Log this action according to `12-logging-procedures.md`.

**Escalation Paths:**

*   **Complex Problems:** If root cause analysis is difficult or the problem requires deep technical expertise beyond standard specialists, delegate analysis to `dev-solver` via `new_task`. Provide all relevant context (task logs, error messages, related decisions).
*   **Architectural Conflicts/Decisions:** For issues involving architectural disagreements, significant design changes, or high-level technical strategy, involve `core-architect` via `new_task`. Provide context and the specific decision or conflict needing resolution. Log the escalation according to `12-logging-procedures.md`.
*   **Diagram Updates:** For major architectural or workflow changes resulting from issue resolution or planning, request diagram updates from `design-diagramer` via `new_task`, pointing to the relevant source information (e.g., ADR in `.ruru/decisions/`, updated plan in `.ruru/planning/`) and specifying the target diagram file (e.g., `.ruru/docs/diagrams/[diagram_name].md`).