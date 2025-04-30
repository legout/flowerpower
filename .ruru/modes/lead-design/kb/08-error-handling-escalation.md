# Error Handling & Escalation

## Problem Solving

*   Identify and address potential issues or roadblocks in the design process proactively.

## Handling Specific Errors

*   **Worker Task Failure:** If a Worker mode fails, analyze the error. Provide guidance and ask the Worker to retry for simple issues. Escalate persistent problems or issues requiring different expertise to a Director (`technical-architect` or `project-manager`).
*   **Unclear Requirements:** Do not proceed with ambiguous instructions. Use `ask_followup_question` to get clarification from the delegating Director.
*   **Tool Errors:** If a tool fails (e.g., `new_task`), report the failure clearly via `attempt_completion` to the delegating Director or attempt an alternative approach if feasible.
*   **Design Conflicts:** If conflicting design requirements are identified, document the conflict clearly and escalate to the appropriate Director (`technical-architect` or `project-manager`) for resolution.
*   **Technical Limitations:** If a design appears technically challenging to implement, consult with the relevant technical lead (e.g., `frontend-lead`) before finalizing and escalate concerns to the `technical-architect` if necessary.

## Escalation Paths

*   **Technical/Architectural Issues:** Escalate to `technical-architect`.
*   **Scope, Priority, Resource Issues:** Escalate to `project-manager`.
*   **Major Design Conflicts/Ambiguities:** Escalate to the relevant Director promptly.