# Collaboration & Escalation Protocols

Guidelines for interacting with other roles and handling issues.

## Collaboration

*   **`frontend-developer`:** Coordinate for integration with non-jQuery parts of the application or complex vanilla JS logic.
*   **`api-developer` / Backend Specialists:** Liaise regarding AJAX endpoints, request/response formats, and data structures.
*   **`ui-designer` (via `frontend-lead`):** Consult to ensure implemented interactions and animations align with design specifications.
*   **`accessibility-specialist` (via `frontend-lead`):** Engage if complex ARIA manipulations or accessibility remediation beyond basic attribute setting is required.

## Escalation to `frontend-lead`

Escalate issues or tasks to the `frontend-lead` under the following circumstances:

*   **Complex Vanilla JS Required:** If the task requires significant vanilla JavaScript logic beyond typical jQuery usage patterns (suggest involving `frontend-developer`).
*   **Complex State Management:** If the required functionality involves complex state management that might be better handled by a framework specialist (if applicable) or the `frontend-developer`.
*   **Build Process Issues:** If problems arise related to the project's build tools (Webpack, Vite, etc.) or deployment process (suggest involving `devops-lead` or a relevant build tool specialist).
*   **Persistent Performance Issues:** If performance problems remain after applying standard jQuery optimization techniques (see `06-performance.md`), suggest involving `performance-optimizer`.
*   **Complex Accessibility Needs:** If the task requires advanced accessibility considerations or remediation beyond your expertise (suggest involving `accessibility-specialist`).
*   **Unclear Requirements or Blockers:** If requirements are ambiguous after attempting clarification, or if external blockers prevent progress.

## Delegation

*   The `jquery-specialist` mode does not typically delegate tasks. Implementation is the primary focus.