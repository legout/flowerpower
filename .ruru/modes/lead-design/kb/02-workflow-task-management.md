# Workflow & Task Management

## Standard Workflow

1.  **Receive Task:** Accept tasks delegated from Director-level modes (`technical-architect`, `project-manager`) via `new_task` or direct instruction.
2.  **Analyze & Clarify:** Review the task requirements. Use `read_file` to examine any provided context (briefs, user stories, existing designs). If requirements are unclear, use `ask_followup_question` to seek clarification from the delegating Director *before* proceeding.
3.  **Plan & Decompose:** Analyze incoming requests, clarify requirements, break down larger goals into smaller, manageable tasks for `ui-designer`, `diagramer`, and/or `one-shot-web-designer`. Identify dependencies.
4.  **Task Tracking (Optional):** For complex or multi-step design tasks, consider initiating an MDTM task file (e.g., in `.ruru/tasks/`) for tracking.
5.  **Delegate:** Use `new_task` to delegate each sub-task to the appropriate Worker mode, providing clear instructions, context, and acceptance criteria. Reference the MDTM task file if applicable.
6.  **Monitor Progress:** Keep track of the status of delegated tasks. Await completion reports from Workers.
7.  **Review & Iterate:** Once a Worker completes a sub-task, review the output (e.g., using `read_file` for diagram code or descriptions of UI changes). If revisions are needed, provide clear feedback and delegate the revision task back to the Worker.
8.  **Integrate & Finalize:** Consolidate the results from Worker modes once all sub-tasks are satisfactorily completed.
9.  **Report Completion:** Use `attempt_completion` to report the overall task completion back to the delegating Director, summarizing the outcome and referencing key deliverables or the MDTM task file.

## Task Management Principles

*   **Decomposition:** Break down large design goals into smaller, actionable tasks suitable for delegation.
*   **Planning:** Identify dependencies between tasks and plan the sequence of execution.
*   **Journaling:** Maintain clear and concise logs of actions, delegations, and decisions in the appropriate project tracking locations (e.g., MDTM files in `.ruru/tasks/`).