# 03 - Workflow: Project Coordination & Execution

This phase covers the core activities after initial intent is clear and any necessary onboarding is complete. It implements principles from `01-operational-principles.md`.

1.  **Understand Goals:** Ensure user objectives for the session or next steps are clearly defined.
2.  **Plan Strategically:**
    *   Break down high-level goals into logical phases or actionable tasks.
    *   Generate unique Task IDs (e.g., `TASK-CMD-YYYYMMDD-HHMMSS` for own tasks, `TASK-[MODE]-...` for delegated). Log task creation according to `12-logging-procedures.md`.
    *   Consider delegating plan creation to `manager-project` via `new_task` if a formal plan document (`.ruru/planning/project_plan.md`) is needed.
3.  **Check Context:** Before complex delegations or resuming work, assess the need for context gathering based on situational judgment (see `01-operational-principles.md`). Consider delegating to `agent-context-resolver` via `new_task` if indicators suggest high complexity, ambiguity, or broad impact: "🔍 Provide current status summary relevant to [goal/task ID] based on `.ruru/tasks/`, `.ruru/decisions/`, `.ruru/planning/` docs, and the Stack Profile (`.ruru/context/stack_profile.json`)." Ensure specialists receive up-to-date context.
4.  **Delegate Tasks:** Follow the detailed procedures in `04-delegation-mdtm.md`. Ensure MDTM is used according to the criteria defined therein (typically for complex/critical tasks).
5.  **Monitor Progress:**
    *   Review task logs (`.ruru/tasks/TASK-... .md`) via `read_file`.
    *   Use `agent-context-resolver` for broader status checks, especially for complex, multi-delegate workflows, based on situational judgment.
6.  **Coordinate & Decide:** Follow the detailed procedures in `05-collaboration-escalation.md`.
7.  **Completion:**
    *   Review the final state of the project or task.
    *   Potentially use `agent-context-resolver` for a final summary.
    *   Use `attempt_completion` to summarize the overall outcome and the coordinated effort to the user. Log completion according to `12-logging-procedures.md`.