# 07: API Documentation (OpenAPI &amp; GraphQL)

This document covers best practices for documenting REST and GraphQL APIs. Clear documentation is essential for API consumers.

## Core Concept: The API Contract

API documentation serves as the definitive contract between the API provider and its consumers. It should clearly describe how to interact with the API, including endpoints, operations, parameters, request/response formats, authentication, and error handling.

## REST API Documentation (OpenAPI / Swagger)

*   **Use OpenAPI Specification (OAS):** OAS (versions 3.x preferred) is the standard for describing REST APIs. Write the spec in YAML (preferred for readability) or JSON.
*   **Key Sections:**
    *   `openapi`: Spec version (e.g., `3.0.3`).
    *   `info`: API metadata (title, description, version).
    *   `servers`: Base URLs.
    *   `tags`: Grouping operations.
    *   `paths`: Defines endpoints and operations (`get`, `post`, etc.).
        *   Include `summary`, `description`, `operationId`.
        *   Define `parameters` (path, query, header, cookie) with `name`, `in`, `required`, `description`, `schema`.
        *   Define `requestBody` with `description`, `required`, `content` (media types like `application/json` and their `schema`).
        *   Define `responses` for status codes, including `description` and `content` (media types and `schema`).
    *   `components`: Reusable definitions.
        *   `schemas`: Define data models (request/response bodies) using JSON Schema subset. Use `$ref` to link. Add `description`, `example`, `readOnly` where appropriate.
        *   `responses`: Reusable response definitions.
        *   `parameters`: Reusable parameter definitions.
        *   `securitySchemes`: Define authentication methods (API Key, JWT, OAuth2).
    *   `security`: Apply security schemes globally or per operation.
*   **Clarity &amp; Detail:** Provide clear descriptions for paths, operations, parameters, schemas, and responses. Use `example` values to illustrate usage.
*   **Maintenance:** Keep the OpenAPI specification up-to-date as the API evolves. Consider code-first (generating spec from code annotations) or design-first approaches.
*   **Tooling:** Leverage tools like Swagger UI or Redoc to generate interactive documentation from the OAS file. Save the spec file in a standard location (e.g., `.ruru/docs/api/openapi.yaml`).

## GraphQL API Documentation

*   **Schema as Documentation:** The GraphQL Schema Definition Language (SDL) itself is a primary source of documentation due to its strong typing.
*   **Descriptions:** Add descriptions directly within the SDL using string literals or block strings (`"""Description"""`) for:
    *   Types (`type User`, `input CreateUserInput`)
    *   Fields (`name: String`)
    *   Arguments (`(id: ID!)`)
    *   Enums (`enum Status`)
    *   Interfaces (`interface Node`)
    *   Unions (`union SearchResult`)
    ```graphql
    """
    Represents a user in the system.
    """
    type User {
      """Unique identifier for the user (UUID)."""
      id: ID!
      """User's full name."""
      name: String!
      """User's email address (must be unique)."""
      email: String!
    }

    type Mutation {
      """Creates a new user."""
      createUser(
        """Data for the new user."""
        input: CreateUserInput!
      ): CreateUserPayload
    }
    ```
*   **Introspection:** GraphQL APIs support introspection queries, allowing tools like GraphiQL, Apollo Studio Explorer, etc., to automatically build interactive documentation explorers directly from the live schema, including the descriptions you provide.
*   **Markdown Documentation:** Supplement the schema with higher-level documentation in Markdown files explaining concepts, workflows, authentication, and providing examples.

## General Documentation Best Practices

*   **Audience:** Write for the API consumer. Explain concepts clearly.
*   **Examples:** Provide clear request and response examples for common use cases and error scenarios.
*   **Authentication:** Clearly document how clients should authenticate.
*   **Error Handling:** Document the error response format and common error codes/types.
*   **Versioning &amp; Changelog:** Document API versions, changes between them, and deprecation policies.
*   **Accessibility:** Ensure documentation is easily accessible to developers (e.g., hosted web page, included in repository).

Accurate, clear, and up-to-date documentation is crucial for API adoption and usability. Report the need for formal documentation review or generation to the lead (suggesting `technical-writer`).