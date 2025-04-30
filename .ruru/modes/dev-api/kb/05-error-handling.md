# 05: API Error Handling Patterns

This document outlines patterns for consistent and informative error handling in REST and GraphQL APIs.

## Goals of Good Error Handling

*   **Informative:** Help clients understand what went wrong.
*   **Consistent:** Use a standard format across the API.
*   **Secure:** Avoid leaking sensitive internal details in production.
*   **Actionable:** Provide guidance for resolution where possible.

## REST API Error Handling

*   **Use Appropriate HTTP Status Codes:** Select the most specific 4xx (client error) or 5xx (server error) code. Key codes include:
    *   `400 Bad Request`: General client error, validation issues.
    *   `401 Unauthorized`: Authentication required/failed.
    *   `403 Forbidden`: Authenticated but lacks permission.
    *   `404 Not Found`: Resource not found.
    *   `405 Method Not Allowed`: HTTP method not supported.
    *   `409 Conflict`: Resource state conflict (e.g., duplicate creation).
    *   `422 Unprocessable Entity`: Semantic validation errors.
    *   `429 Too Many Requests`: Rate limit exceeded.
    *   `500 Internal Server Error`: Unexpected server error (log details server-side).
    *   `503 Service Unavailable`: Temporary unavailability.
*   **Consistent JSON Error Body:** Define a standard structure. Options include:
    *   **RFC 7807 Problem Details (Recommended):** Provides a standard structure with fields like `type`, `title`, `status`, `detail`, `instance`, and allows extensions.
        ```json
        // Status: 400 Bad Request
        {
          "type": "https://example.com/probs/validation-error",
          "title": "Validation Failed",
          "status": 400,
          "detail": "One or more fields failed validation.",
          "invalid-params": [
            { "name": "email", "reason": "must be a valid email address" }
          ]
        }
        ```
    *   **Simpler Custom Format:** Define a consistent structure with `code`, `message`, and optional `details`.
        ```json
        // Status: 400 Bad Request
        {
          "error": {
            "code": "VALIDATION_ERROR",
            "message": "Input validation failed.",
            "details": [ { "field": "email", "issue": "Invalid format" } ]
          }
        }
        ```
*   **Validation Errors:** For `400` or `422`, include details about which fields failed and why in the response body.
*   **Security:** Never expose stack traces or sensitive internal details in production error responses.

## GraphQL API Error Handling

*   **Top-Level `errors` Array:** GraphQL responses include a standard `errors` array.
    *   **Use For:** System-level errors (query syntax, internal server errors during resolution), request-level errors.
    *   **Structure:** Each error includes `message`, `locations`, `path`, and optional `extensions` (use this for custom codes like `INTERNAL_SERVER_ERROR`).
    *   **Partial Responses:** Failures in nullable fields return `null` for the field and add an error to the `errors` array; failures in non-nullable fields propagate up.
*   **Application/User Errors (In Payload):** Handle predictable business logic or validation errors within the `data` payload.
    *   **Method:** Use Union Types or specific error fields within mutation response payloads. Define specific error types (e.g., `EmailTakenError`) often implementing a common interface (`UserError`).
    ```graphql
    interface UserError { message: String!, field: String }
    type EmailTakenError implements UserError { message: String!, field: String!, email: String! }
    type CreateUserSuccess { user: User! }
    union CreateUserResult = CreateUserSuccess | EmailTakenError // Add other specific errors

    type Mutation { createUser(input: CreateUserInput!): CreateUserResult! }
    ```
    *   **Response:** The `__typename` field indicates which type in the union was returned.
    ```json
    // Example Validation Error Response
    {
      "data": {
        "createUser": {
          "__typename": "EmailTakenError",
          "message": "Email address is already in use.",
          "field": "email",
          "email": "test@example.com"
        }
      }
    }
    ```
    *   **Avoid:** Don't pollute the top-level `errors` array with expected validation or business rule failures.

## General Best Practices

*   **Log Server Errors:** Always log detailed internal server errors (`5xx` in REST, unexpected resolver errors in GraphQL) server-side for debugging.
*   **Machine-Readable Codes:** Include unique error codes (e.g., `AUTH_INVALID_TOKEN`, `VALIDATION_REQUIRED_FIELD`) to allow programmatic handling by clients (in REST body, in GraphQL `extensions` or payload error types).
*   **Human-Readable Messages:** Provide clear messages suitable for end-users (but avoid sensitive details).
*   **Documentation:** Clearly document your error response formats and common error codes/types.

Choose a consistent error handling strategy (RFC 7807 for REST, Payload errors for GraphQL user issues) and apply it uniformly.