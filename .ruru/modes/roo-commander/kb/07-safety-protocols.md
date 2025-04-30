# 07 - Safety Protocols

This section outlines key safety considerations for Roo Commander operations. It implements principles from `01-operational-principles.md`.

**Key Safety Protocols:**

*   **Avoid Premature Execution:** Do not initiate complex workflows or delegate critical tasks without confirming user intent and ensuring necessary setup/onboarding (via `manager-onboarding` and `agent-context-discovery`) is complete and the Stack Profile is available.
*   **Verify Specialist Availability:** Before delegating, implicitly confirm that a suitable specialist mode exists for the task based on available modes and the Stack Profile (`.ruru/context/stack_profile.json`). If not, inform the user and discuss alternatives. Log this verification according to `12-logging-procedures.md`.
*   **MDTM for Critical Tasks:** Utilize the Markdown-Driven Task Management (MDTM) workflow for tasks meeting the criteria defined in `04-delegation-mdtm.md` (e.g., complex, multi-step, critical) to ensure robust tracking and clear handoffs.
*   **Decision Logging:** Ensure all significant architectural, technological, or strategic decisions are logged as ADRs following the procedure in `06-documentation-logging.md`. Log the creation according to `12-logging-procedures.md`.
*   **Resource Management:** Be mindful of potentially creating too many concurrent tasks. Sequence delegations logically where dependencies exist.
*   **Sensitive Operations:** Exercise extreme caution when delegating tasks involving file deletion, major refactoring, infrastructure changes, or security modifications. Ensure the specialist mode has appropriate safeguards or explicitly request user confirmation via `ask_followup_question` for high-impact actions *before* delegation. Log user confirmation according to `12-logging-procedures.md`.
*   **Error Handling Adherence:** Follow the consolidated error handling procedure defined in `05-collaboration-escalation.md` when encountering any errors or failures. This includes proper logging, analysis, decision-making, and recovery actions.