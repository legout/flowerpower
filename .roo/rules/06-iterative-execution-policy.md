+++
id = "RURU-RULE-ITERATIVE-EXECUTION-V1"
title = "Standard Iterative Execution Policy"
context_type = "rules"
scope = "Defines how modes should handle potentially long-running or complex tasks"
target_audience = ["all"] # Primarily relevant for modes performing implementation/generation
granularity = "procedure"
status = "active"
last_updated = "2025-04-21"
tags = ["rules", "workflow", "iteration", "context-management", "safety", "mdtm", "chunking"]
related_context = ["00-user-preferences.md", "01-standard-toml-md-format.md", "04-standard-workflows.md"]
+++

# Standard Iterative Execution Policy

**Objective:** To ensure reliable task completion by preventing context window overflows and promoting manageable work increments, especially for generative or implementation tasks.

**Applies To:** All modes performing tasks that involve significant code generation, file modification, analysis, or following multi-step procedures (e.g., developers, writers, refactorers, testers, sometimes architects/managers). Less critical for simple lookups or coordination.

**Core Principles:**

1.  **Prefer Smaller Steps:** Whenever feasible, break down complex requests into smaller, logical sub-tasks during the planning phase. For tasks managed via MDTM, this means creating granular checklist items.
2.  **Context Awareness:** Modes **MUST** be aware of their context window usage (`{{CONTEXT_PERCENTAGE}}`).
3.  **Proactive Checkpointing:** Do not attempt to complete overly large tasks in a single execution turn, even if instructed broadly.

**Procedure:**

1.  **Task Planning:** When starting a task (especially one involving multiple steps or significant generation):
    *   Review the overall goal and acceptance criteria.
    *   If using MDTM, review the checklist items.
    *   Mentally estimate the complexity. If a task or a single MDTM checklist item *appears* likely to require extensive code/output generation or numerous tool calls:
        *   **Plan for Iteration:** Anticipate that completing the task/item might require more than one execution cycle.
        *   **(Optional but Recommended):** Inform the delegator (via `ask_followup_question` *before starting*) if you anticipate needing multiple steps/checkpoints for a single requested item.

2.  **Execution & Monitoring:** While executing the task (writing code, applying diffs, following checklist items):
    *   Periodically self-monitor context window usage (`{{CONTEXT_PERCENTAGE}}`).
    *   **Trigger Checkpoint:** If context usage approaches a threshold (e.g., **around 40-50%**), prepare to pause *after completing the current logical unit of work*.
        *   A "logical unit" could be:
            *   Completing the current MDTM checklist item (`- [✅]`).
            *   Finishing a complete function, class, or coherent block of code.
            *   Completing a specific file modification.
            *   Finishing a distinct step in an analysis process.

3.  **Checkpoint & Handover:** When pausing due to the context threshold OR completing a step marked for reporting (e.g., `📣` in MDTM):
    *   **Finalize Current Unit:** Ensure the immediate work unit is complete and syntactically correct (e.g., finish the function, close code blocks).
    *   **Summarize Progress:** Briefly state what was completed in the current turn.
    *   **Identify Next Step:** Clearly state the *next logical step* required to continue the overall task (e.g., "Next step is to implement the `handleUpdate` function", "Next step is to process MDTM item #3").
    *   **Report Status:** Use `<attempt_completion>` to report back to the delegator. Include:
        *   Confirmation of completed unit/step.
        *   Current context percentage.
        *   The identified *next step*.
        *   Any partial results or paths to modified/created files.
        *   *(Example Result):* "✅ Completed implementation of `getUserData` function (MDTM item #2). Context at 55%. Next step is to implement the `UserProfile` component using this data. Modified: `src/hooks/useUserData.ts`."

4.  **Receiving Mode Action (Coordinator/Lead):**
    *   Acknowledge the partial completion and the stated next step.
    *   Log the progress (Rule `12`).
    *   Re-delegate the *next step* back to the specialist mode, providing the necessary context (including the original goal and referencing the previous work/files).

**Rationale:**

*   **Context Safety:** Prevents hitting hard context limits which often lead to truncated, incomplete, or erroneous responses.
*   **Error Reduction:** Smaller execution units reduce the chance of complex errors accumulating within a single turn.
*   **State Management:** Encourages breaking work into steps that align well with MDTM tracking, improving visibility.
*   **User Experience:** While it involves more turns, it leads to more reliable progress compared to large failures requiring complete restarts.

**Note:** The 50-60% threshold is a guideline. Modes should use judgment. If a small, final step pushes usage slightly over, completing it might be acceptable. The key is to avoid *starting* a large unit of work when context is already high.