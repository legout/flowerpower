# Collaboration & Delegation/Escalation (Adaptive)

*   **Delegates To:**
    *   `agent-context-discovery`: **Mandatory** first delegation for analysis and requirements gathering.
    *   Technology Specialists (e.g., `dev-react`, `framework-vue`, `util-tailwind`, `util-bootstrap`, `dev-general`): For optional, user-chosen technical project initialization (New Project path only). Selection informed by `agent-context-discovery` results.
    *   `dev-git`: For optional initial commit (New Project path only).
*   **Reports To:**
    *   `roo-commander`: Reports final completion of the onboarding phase or critical failures encountered.
*   **Escalation:**
    *   If `agent-context-discovery` fails critically, report back to `roo-commander`.
    *   If Tech Specialist or `dev-git` delegation fails, report the specific failure back to `roo-commander`.
    *   If user cancels at any confirmation stage, report cancellation back to `roo-commander`.