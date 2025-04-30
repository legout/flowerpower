# 02: API Design Principles (REST &amp; GraphQL)

This document covers key principles for designing RESTful and GraphQL APIs, including resource modeling, schema design, data formats, and versioning.

## General Design Principles (Recap)

*   **Resource/Type Orientation:** Focus on the "nouns" (resources in REST, types in GraphQL) rather than actions/verbs.
*   **Predictability &amp; Consistency:** Use consistent naming, data formats, and structures.
*   **Simplicity &amp; Clarity:** Use intuitive names, expose only necessary data, and provide clear documentation.
*   **Consumer Focus:** Design with client application needs in mind.

## REST API Design

*   **Resource Naming:**
    *   Use plural nouns for collections (e.g., `/users`, `/products`).
    *   Use consistent casing (e.g., lowercase, kebab-case: `/product-categories`).
    *   Avoid deep nesting; use query parameters for filtering related resources (e.g., `/orders?customerId=123`).
*   **HTTP Methods:** Use standard methods semantically:
    *   `GET`: Retrieve resource(s).
    *   `POST`: Create a new resource in a collection.
    *   `PUT`: Replace an existing resource entirely.
    *   `PATCH`: Partially update an existing resource.
    *   `DELETE`: Remove a resource.
*   **Filtering, Sorting, Pagination:** Provide query parameters for:
    *   Filtering: `/products?category=electronics&amp;status=available`
    *   Sorting: `/users?sort=lastName,-createdAt`
    *   Pagination: Offset/Limit (`?offset=20&amp;limit=10`) or Cursor-based (`?cursor=abc&amp;limit=10`). Include pagination metadata in responses.
*   **HATEOAS (Hypermedia):** Consider including links (`_links`) in responses to guide clients to related resources and actions.
    ```json
    "_links": {
      "self": { "href": "/orders/123" },
      "customer": { "href": "/customers/456" }
    }
    ```

## GraphQL API Design

*   **Schema-First:** Define the API contract using the Schema Definition Language (SDL).
*   **Think in Graphs:** Model data as interconnected types.
*   **Client-Driven:** Design the schema based on client data consumption patterns.
*   **Strong Typing &amp; Nullability:**
    *   Use specific scalar types, enums, interfaces, unions. Avoid generic JSON scalars.
    *   Be intentional with non-null (`!`). Mark as non-null only when a value is guaranteed. Consider list nullability (`[Type!]!`, `[Type]!`, `[Type!]`).
*   **Descriptive Naming &amp; Documentation:** Use clear names (PascalCase for types/enums, camelCase for fields/args) and add descriptions (`"""Description"""`).
*   **Queries:**
    *   Design for client needs, allowing fetching required data in one request.
    *   Implement standardized pagination (Relay Cursor Connections recommended).
    *   Provide filtering/sorting arguments on list fields.
*   **Mutations:**
    *   Use verb-based names (e.g., `createUser`).
    *   Use a single, non-nullable `input` object argument.
    *   Return a payload containing the modified data and potential user errors.
    ```graphql
    input CreateUserInput { name: String!, email: String! }
    type UserError { message: String!, field: String }
    type CreateUserPayload { user: User, errors: [UserError!] }
    type Mutation { createUser(input: CreateUserInput!): CreateUserPayload }
    ```
*   **Interfaces &amp; Unions:** Use for polymorphic relationships.
*   **Enums:** Use for fields with a fixed set of allowed string values.

## Data Formats (JSON Conventions for REST)

*   **Content-Type:** Use `application/json` for requests/responses. Clients send `Accept: application/json`.
*   **Property Naming:** Be consistent (e.g., `camelCase` or `snake_case`). Document the choice.
*   **Dates/Times:** Use ISO 8601 strings (e.g., `"2023-10-27T10:30:00Z"`).
*   **Relationships:** Choose between nested objects, resource IDs, or hypermedia links based on needs.
*   **Nulls:** Use JSON `null` for absent values. Represent empty collections as `[]`.
*   **Booleans:** Use JSON `true` and `false`.

## API Versioning

*   **Purpose:** Manage breaking changes without disrupting existing clients.
*   **Strategies:**
    *   **URI Path (Recommended):** `/v1/users`, `/v2/users`. Explicit, simple routing.
    *   **Query Parameter:** `/users?version=1`. Keeps URI clean, but easy to omit.
    *   **Custom Header:** `X-API-Version: 1`. Keeps URI clean, less visible.
    *   **Accept Header (Media Type):** `Accept: application/vnd.example.v1+json`. "Purest" REST, often complex.
*   **Best Practices:**
    *   Version only for breaking changes (use major versions: `v1`, `v2`).
    *   Document changes and deprecation timelines clearly.
    *   Prefer explicit versioning over relying on defaults.

Choose design patterns and versioning strategies early and apply them consistently. Prioritize clarity, consistency, and client needs.