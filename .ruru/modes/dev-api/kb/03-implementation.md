# 03: API Implementation &amp; Performance

This document covers the implementation phase of API development, including workflow, resolver logic, and performance considerations.

## Implementation Workflow (General Steps)

1.  **Receive Task &amp; Initialize Log:** Understand requirements, API style (REST/GraphQL), data models, security needs. Clarify with lead. Log goal in task log (e.g., `.ruru/tasks/[TaskID].md`).
2.  **Design/Refine API:** Define resources/schema, endpoints/operations, data models, request/response formats, basic security, versioning. Log design decisions. *Optional:* Start/update OpenAPI spec or GraphQL schema. Report specialist needs (DB, Security, Frontend) to lead.
3.  **Implement API Logic:**
    *   Write code for controllers/handlers, routes, services, data access logic using the project's backend stack.
    *   Implement input validation rigorously.
    *   Implement basic security checks (e.g., checking for authenticated user if framework provides it). Coordinate complex AuthN/AuthZ with `security-specialist` via lead.
    *   Implement consistent error handling (see `05-error-handling.md`).
    *   Integrate with backend services/DB. Coordinate complex DB interactions with `database-specialist` via lead.
    *   **Guidance:** Use `write_to_file`, `apply_diff`. Log significant steps.
4.  **Test API:** Write/run unit and integration tests (see `04-testing.md`). Manually test CRUD operations (`execute_command` with `curl`/`httpie`). Validate schemas, status codes, error handling, basic security. Log test results. Report need for comprehensive testing to lead.
5.  **Optimize API (Basic):** Implement basic performance considerations (see below). Report need for advanced optimization (caching, deep query tuning) to lead (suggesting `performance-optimizer`). Log optimization details.
6.  **Document API:** Generate/update API specification (OpenAPI/Swagger or GraphQL schema docs). Ensure clarity. Save final spec using `write_to_file` (e.g., `.ruru/docs/api/openapi.yaml`). Report need for formal documentation to lead (suggesting `technical-writer`).
7.  **Log Completion &amp; Final Summary:** Append final status, outcome, summary, and references to the task log.
8.  **Report Back:** Use `attempt_completion` to notify the delegating lead, referencing the task log file.

## GraphQL Resolver Best Practices

*   **Keep Resolvers Thin:** Delegate data fetching and business logic to dedicated service/data access layers. Resolvers should primarily handle request context and call appropriate services.
*   **Batching &amp; Caching (DataLoader):** Crucial for performance. Avoid the "N+1 problem" by using DataLoader (or similar patterns) to batch database queries or external API calls within a single request lifecycle.
*   **Authorization:** Implement authorization checks within resolvers or dedicated middleware/directives. Ensure the user has permission *before* fetching/returning data.
*   **Error Handling:** Catch errors from service layers and map them to appropriate GraphQL error responses (either top-level `errors` for system issues or specific error types in mutation payloads for user errors).

## Performance Optimization &amp; Caching

*   **Database Query Optimization:**
    *   Ensure proper indexing (coordinate with `database-specialist`).
    *   Select only necessary columns.
    *   Avoid N+1 problems (use Eager Loading or DataLoader).
*   **Efficient Data Processing:** Minimize complex computations in the request cycle; use background jobs if needed.
*   **Payload Size:** Implement pagination; allow clients to select fields (GraphQL native, `?fields=` in REST).
*   **Asynchronous Operations:** Use async programming effectively to avoid blocking.
*   **Caching Strategies:**
    *   **HTTP Caching (REST GET):** Use `Cache-Control`, `ETag`, `Last-Modified` headers appropriately.
    *   **Server-Side Caching:**
        *   **In-Memory:** For simple, non-shared caching (use libraries like `node-cache`).
        *   **Distributed Cache (Redis/Memcached):** For scalable, shared caching across instances.
        *   **What to Cache:** Expensive query results, computed data, external API responses.
        *   **Cache Invalidation:** Critical! Use TTL (Time-To-Live) or explicit invalidation when source data changes. Plan this carefully.
    *   **CDN Caching:** Useful for public, static-like API responses (controlled via `Cache-Control: s-maxage`).
*   **Considerations:** Cache appropriately (expensive &amp; infrequent changes). Balance freshness vs. performance. Monitor cache effectiveness.

Consult with `performance-optimizer`, `database-specialist`, and `infrastructure-specialist` (via lead) for complex performance tuning and caching implementations.