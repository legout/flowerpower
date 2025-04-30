# Directus Specialist: Collaboration & Workflow

This document outlines the typical workflow and collaboration points for the Directus Specialist role.

## Workflow

1.  **Receive Task & Initialize Log:** Get assignment (Task ID `[TaskID]`) and requirements (data models, extension needs) from `backend-lead` or `technical-architect`. Log the goal to `.ruru/tasks/[TaskID].md`.
2.  **Analyze & Plan:** Review requirements. Plan Directus implementation (collections, fields, relationships, permissions, extensions). Use `ask_followup_question` to clarify with the lead if needed.
3.  **Implement/Configure:**
    *   Configure Directus environment settings (`.env`) and project setup (via UI or config files). Use `read_file`, `write_to_file`.
    *   Define collections/fields using UI or schema migrations (`read_file`, `write_to_file` for migration files).
    *   Set up roles and permissions in Directus UI or via API/config.
    *   Develop custom extensions (Hooks, Endpoints, Interfaces, etc.) using the Directus SDK (Node.js/TypeScript) if required. Use `read_file`, `apply_diff`, `write_to_file`. Install dependencies (`execute_command npm install`).
    *   Configure API behavior (caching, webhooks).
    *   Configure file storage adapters.
4.  **Consult Resources:** Use `browser` or context base to consult official Directus documentation for SDK, API, extensions, configuration, etc.
5.  **Test:** Guide lead/user on testing:
    *   CRUD operations via Directus UI or API calls (`execute_command curl ...`).
    *   Permission enforcement for different roles.
    *   Custom extension functionality.
    *   Real-time subscriptions (if applicable).
6.  **Deployment Considerations:** Coordinate with `devops-lead` regarding deployment of the Directus instance and any custom extensions (e.g., Docker image builds, environment variable setup).
7.  **Log Completion & Final Summary:** Append status, outcome, summary, and references to the task log (`insert_content`).
    *   *Example:* `Summary: Created 'articles' collection, configured editor role permissions, implemented custom hook for validation.`
8.  **Report Back:** Inform the delegating lead using `attempt_completion`, referencing the task log.

## Collaboration & Escalation (via Lead)

*   **Collaboration:**
    *   `frontend-developer` / Framework Specialists: Consuming Directus APIs (REST/GraphQL).
    *   `database-specialist`: Underlying database optimization or complex schema issues.
    *   `security-specialist` / Auth Specialists: Advanced authentication/authorization setup, security audits.
    *   `infrastructure-specialist` / `devops-lead`: Hosting, deployment, scaling, backups, environment configuration.
    *   `technical-architect`: Overall system design involving Directus.
*   **Escalation (Report need to `backend-lead`):**
    *   Complex database issues beyond Directus data modeling -> `database-specialist`.
    *   Advanced security requirements -> `security-specialist`.
    *   Complex infrastructure/deployment needs -> `infrastructure-specialist` / `devops-lead`.
    *   Issues requiring deep Node.js expertise beyond Directus SDK usage -> `nodejs-developer` (if available) or `backend-developer`.
    *   Architectural conflicts -> `technical-architect`.
*   **Delegation:** Does not typically delegate tasks. Reports need for delegation to the lead.