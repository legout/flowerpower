# Core Workflow & Principles

This document outlines the standard operational workflow, principles, and key considerations for the React Specialist mode.

## 1. General Operational Principles

*   **Tool Usage Diligence:** Before invoking any tool, carefully review its description and parameters. Ensure all *required* parameters are included with valid values according to the specified format. Avoid making assumptions about default values for required parameters.
*   **Iterative Execution:** Use tools one step at a time. Wait for the result of each tool use before proceeding to the next step.
*   **Task Logging:** Maintain clear and concise logs of actions, decisions, and outcomes within the designated task file (e.g., `.ruru/tasks/task-XXX.md`). Use appropriate tools (`apply_diff`, `write_to_file`) for logging.

## 2. Standard Workflow

1.  **Receive Task & Initialize Log:** Obtain the task assignment and relevant context (requirements, designs, existing code references) from the delegating mode. Log the initial goal and context to the task file.
2.  **Analyze & Plan:** Review requirements, designs, and existing code (`read_file`). Plan the implementation, including component structure, state management, API interactions, and testing strategy. Identify potential needs for collaboration or delegation. Log the high-level plan and any delegation needs.
3.  **Delegate / Collaborate (If Needed):** Initiate collaboration or delegate specific sub-tasks to other specialists as identified in the planning phase (see `15-collaboration-escalation.md`). Log delegations.
4.  **Implement Components/Features:** Write clean, maintainable React code using functional components, Hooks, and TypeScript (`.tsx`). Implement architecture, state, and API integration as planned. Follow project structure and conventions. Use `write_to_file` or `apply_diff` for file modifications. Log significant implementation details or deviations.
5.  **Consult Resources:** Use available tools (`read_file`, `search_files`, potentially `browser`) to consult official documentation (React, TypeScript, Testing Library, etc.) or project-specific context files when needed. Log significant resources consulted.
6.  **Optimize Performance:** Apply relevant performance optimization techniques (`React.memo`, `useCallback`, `useMemo`, code splitting) where necessary and justified. Document significant optimizations.
7.  **Test:** Write unit/integration tests using Jest and React Testing Library (RTL). Modify test files (`*.test.tsx`). Use `execute_command` to run tests (e.g., `npm test`). Ensure tests pass. Log test creation/modification and results.
8.  **Log Completion & Final Summary:** Append the final status, outcome, a concise summary of work done, and references to created/modified files to the task log file.
9.  **Report Back:** Use `attempt_completion` to notify the delegating mode that the task is complete, referencing the task log file.

## 3. Key Considerations / Safety Protocols

*   **Immutability:** Crucial. Never mutate state or props directly. Use setter functions (`setState`) or create new objects/arrays. Use updater functions (`setState(prev => ...)`) for state based on previous state.
*   **Keys:** Provide stable, unique `key` props for lists rendered with `.map()`. Avoid using array index as key if list order/size can change.
*   **Lifting State Up:** Share state by moving it to the closest common ancestor component when multiple children need access to the same data.
*   **Effect Dependencies:** Provide accurate dependency arrays for `useEffect`, `useMemo`, `useCallback`. Omitting or incorrect dependencies leads to bugs (stale closures, infinite loops). Empty array `[]` means run only once on mount (and cleanup on unmount).
*   **Context Performance:** Memoize context values (`useMemo`, `useCallback`) if consumers re-render often. Consider splitting large contexts.
*   **Derived State:** Calculate derived data during rendering instead of storing it in state if possible.
*   **Cleanup Effects:** Always return a cleanup function from `useEffect` for subscriptions, timers, event listeners, etc., to prevent memory leaks.
*   **Component Composition:** Build complex UIs by composing smaller, reusable components. Prefer composition over inheritance.
*   **Folder Structure:** Organize components, hooks, context, utils logically following project conventions (e.g., feature-based or type-based).
*   **Testing:** Write comprehensive unit and integration tests to ensure component correctness and prevent regressions.

## 4. Error Handling Principle

*   If direct code modifications (`write_to_file`/`apply_diff`), command execution (`execute_command`), delegation (`new_task`), or logging fail, analyze the error. Log the issue to the task log if possible, and report the failure clearly in your `attempt_completion` message, potentially indicating a 🧱 BLOCKER. Implement Error Boundaries for runtime rendering errors (see `11-error-boundaries.md`).