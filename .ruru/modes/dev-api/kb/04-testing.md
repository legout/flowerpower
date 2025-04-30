# 04: API Testing Strategies

This document outlines testing approaches relevant to the API Developer, focusing on ensuring correctness, reliability, and adherence to contracts.

## Core Concept: Ensuring API Quality

Testing is crucial for verifying that the API functions as expected, handles errors correctly, meets performance criteria (basic checks), remains secure (basic checks), and fulfills the contract defined for its consumers.

## Key Testing Levels (API Developer Focus)

1.  **Unit Testing:**
    *   **Goal:** Verify the logic of individual functions, modules, or classes in isolation.
    *   **Scope:** Test business logic, validation functions, data transformations, utility functions.
    *   **Method:** Use standard testing frameworks (Jest, Pytest, PHPUnit, etc.) and mocking libraries. Mock external dependencies (database, external APIs). Tests should be fast and independent.
    *   **Example:** Testing an `isValidEmail` function, testing a service method with mocked database calls.

2.  **Integration Testing:**
    *   **Goal:** Verify the interaction between different components of the API, often including database interactions or calls to other internal services.
    *   **Scope:** Test routing, controllers/resolvers, services, data access layers, and potentially the database (using a test database).
    *   **Method:** Make actual HTTP requests to the API endpoints running in a test environment. Use HTTP client libraries (Supertest, `requests`, `httpx`, Guzzle) within a testing framework. Assert HTTP status codes, response headers, and response body content/structure. Verify data changes in the test database.
    *   **Example:** Testing a `POST /users` endpoint, verifying the user is created in the test database and the correct response (e.g., `201 Created` with user data) is returned. Testing a `GET /users/{id}` endpoint for both existing and non-existent users.

3.  **Contract Testing (Basic):**
    *   **Goal:** Verify that the API implementation adheres to its defined contract (OpenAPI spec or GraphQL schema).
    *   **Scope:** Check if requests and responses match the expected structure, types, and constraints defined in the specification.
    *   **Method:** Can often be integrated into integration tests using schema validation libraries or middleware that checks requests/responses against the API specification.
    *   **Example:** Using an OpenAPI validator middleware during integration tests to ensure a `POST /users` request body matches the defined schema and the `201` response also matches its schema.

## Testing Best Practices

*   **Test Pyramid:** Emphasize unit tests (many, fast), have a solid suite of integration tests (fewer, verify interactions), and rely on dedicated testers (`e2e-tester`, `qa-lead`) for broader E2E tests.
*   **Isolation:** Ensure tests are independent and don't rely on the state left by others. Clean up test data between tests.
*   **Coverage:** Test happy paths, edge cases, invalid inputs, boundary conditions, error responses (4xx, 5xx), and basic security constraints (AuthN/AuthZ checks).
*   **Automation:** Integrate tests into the Continuous Integration (CI) pipeline for automatic execution on code changes.

## Collaboration

*   Coordinate with `qa-lead` or testing specialists for defining comprehensive test plans and strategies.
*   Report needs for E2E, performance (`performance-optimizer`), or security (`security-specialist`) testing to the lead.

API developers are primarily responsible for writing thorough unit and integration tests to guarantee the correctness of their code and the interactions between API components.