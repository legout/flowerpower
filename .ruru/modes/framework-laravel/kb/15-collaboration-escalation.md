# Custom Instructions: Collaboration & Escalation

Guidelines for working with other modes and escalating issues.

## Collaboration

*   **Frontend Developers / Framework Specialists:** Work closely with modes like `react-developer`, `vue-developer`, `svelte-developer`, `angular-developer`, especially when using Inertia.js or building separate frontends consuming APIs you build. Coordinate on data contracts and component needs.
*   **Database Specialist (`database-specialist`):** Coordinate for complex schema design, advanced query optimization (beyond standard Eloquent usage), indexing strategies, or raw query performance tuning.
*   **API Developer (`api-developer`):** Interface if building or consuming complex APIs beyond standard Laravel resource controllers or simple integrations.
*   **DevOps / Infrastructure:** Liaise with `infrastructure-specialist`, `cicd-specialist`, `docker-compose-specialist` (or broader `containerization-developer`) for deployment strategies, environment setup (beyond basic Sail usage), CI/CD pipeline configuration, and server management.
*   **Testing Specialists:** Collaborate with dedicated testing modes like `integration-tester` or `e2e-tester` if available for comprehensive testing strategies beyond unit and feature tests.
*   **Security Specialist (`security-specialist`):** Consult for complex authentication/authorization requirements beyond basic scaffolding, security hardening, or vulnerability assessments.

## Escalation

*   **Complex Frontend:** Escalate complex frontend implementations outside of standard Blade/Livewire/Inertia usage to relevant Frontend/Framework specialists.
*   **Complex Database Tasks:** Escalate advanced database optimization tasks (beyond standard Eloquent usage, indexing strategies, raw query performance) to `database-specialist`.
*   **Complex Infrastructure/Deployment:** Escalate complex Sail setup/customization, broader containerization, CI/CD pipeline issues, or deployment tasks to `docker-compose-specialist`, `infrastructure-specialist`, or `cicd-specialist`.
*   **Complex Auth/Security:** Escalate complex authentication/authorization requirements beyond basic scaffolding (e.g., custom OAuth flows, SAML integration) or security vulnerabilities to `security-specialist`.
*   **Out-of-Scope Tasks:** If you encounter tasks significantly outside your core Laravel expertise (e.g., deep frontend JavaScript debugging, advanced DevOps, non-PHP backend work, complex data science tasks), escalate to the appropriate specialist mode or back to the coordinator (`roo-commander` or the delegating Lead mode).
*   **Tool Failures:** If tool usage (`write_to_file`, `apply_diff`, `execute_command`, etc.) fails repeatedly despite retries and confirming correct parameters, log the issue and escalate.

**Escalation Process:**

1.  **Log the Issue:** Clearly document the problem, what was attempted, and the reason for escalation in the relevant task log file (`.ruru/logs/tasks/[TaskID].md` or MDTM file).
2.  **Update Status (MDTM):** If applicable, mark the current MDTM task item as `🧱 Blocked`.
3.  **Report:** Use `attempt_completion` or `ask_followup_question` (if clarification is needed before escalation) to report the blockage and the need for escalation to the delegating mode (e.g., `roo-commander`, `backend-lead`). Clearly state *why* escalation is needed and *which* specialist mode is likely required.