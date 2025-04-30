+++
# --- Metadata ---
id = "PLAYBOOK-API-CRUD-V1"
title = "Project Playbook: Developing a REST API Resource (CRUD)"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "api", "rest", "crud", "backend", "database", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/dev-api/dev-api.mode.md",
    ".ruru/modes/lead-backend/lead-backend.mode.md",
    ".ruru/modes/lead-db/lead-db.mode.md",
    ".ruru/modes/util-writer/util-writer.mode.md",
    ".ruru/modes/test-integration/test-integration.mode.md"
]
objective = "Provide a structured process for designing, implementing, testing, and documenting a new RESTful API resource with standard CRUD operations using the Roo Commander Epic-Feature-Task hierarchy."
scope = "Covers data modeling, API endpoint design, backend implementation (Create, Read, Update, Delete), testing, and documentation for a single resource."
target_audience = ["Users", "Backend Developers", "API Designers", "Architects", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Backend API for Web/Mobile applications"
resource_name_placeholder = "[ResourceName]" # e.g., "Product", "BlogPost", "UserProfile"
resource_name_plural_placeholder = "[ResourceNamePlural]" # e.g., "products", "blog-posts", "user-profiles"
+++

# Project Playbook: Developing a REST API Resource (CRUD)

This playbook outlines a recommended approach for adding a new REST API resource (e.g., managing "Products" or "Articles") with Create, Read, Update, and Delete (CRUD) operations to your backend application, using Roo Commander's Epic-Feature-Task hierarchy.

**Scenario:** You need to expose data management capabilities for a new entity (`[ResourceName]`) through your application's API.

## Phase 1: Definition & Design

1.  **Define the Need (Epic/Feature):**
    *   **Goal:** Articulate the business need for managing `[ResourceName]`.
    *   **Action:** Determine if this new resource is part of a larger Epic or if it constitutes a Feature itself. Create the corresponding Epic/Feature artifact (e.g., `.ruru/features/FEAT-020-manage-[ResourceNamePlural].md`).
    *   **Content:** Describe *why* this resource is needed, who uses it, and the basic operations required. Set `status` to "Planned" or "Draft".

2.  **Data Modeling:**
    *   **Goal:** Define the attributes and database schema for `[ResourceName]`.
    *   **Action:** Delegate to `lead-db` or `data-specialist`.
    *   **Tasks (Examples):**
        *   "Design database schema for `[ResourceName]` table, including fields like [field1], [field2], timestamps."
        *   "Define relationships to other tables (if any)."
        *   "Create database migration script for `[ResourceName]` table."
        *   "Define ORM/Data Model class for `[ResourceName]` (if applicable)."
    *   **Output:** Document the schema design (e.g., in the Feature file, a separate design doc, or an ADR). Implement and test the migration script (can be a separate task).

3.  **API Endpoint Design:**
    *   **Goal:** Define the standard RESTful endpoints, request/response formats, and status codes.
    *   **Action:** Delegate to `lead-backend` or `core-architect`.
    *   **Tasks (Examples):**
        *   "Design REST endpoints for `[ResourceNamePlural]` CRUD operations (e.g., `POST /[ResourceNamePlural]`, `GET /[ResourceNamePlural]`, `GET /[ResourceNamePlural]/{id}`, `PUT /[ResourceNamePlural]/{id}`, `DELETE /[ResourceNamePlural]/{id}`)."
        *   "Define JSON request body schema for POST/PUT."
        *   "Define JSON response body schema for GET/POST/PUT."
        *   "Specify standard HTTP status codes for success and error conditions (e.g., 200, 201, 204, 400, 404, 500)."
    *   **Output:** Document the API design (e.g., using OpenAPI/Swagger specs, markdown tables in the Feature file, or an ADR).

## Phase 2: Implementation (Feature per CRUD Operation Group)

*Note: You can group related operations (e.g., Read List & Read Detail) into single Features if preferred.*

1.  **Implement Create Operation (Feature):**
    *   **Goal:** Build the `POST /[ResourceNamePlural]` endpoint.
    *   **Action:** Define as a Feature (`FEAT-021-create-[ResourceName].md`), linked to the parent Epic/Feature. Set `status` to "Ready for Dev". Decompose into Tasks.
    *   **Tasks (Examples - Delegate to `dev-api`, Framework Specialist):**
        *   "Implement request body validation for Create `[ResourceName]`."
        *   "Implement service logic to create `[ResourceName]` record in database."
        *   "Implement API route/controller for `POST /[ResourceNamePlural]`."
        *   "Format successful response (e.g., 201 Created with resource representation)."
        *   "Write integration test for `POST /[ResourceNamePlural]` endpoint." (Delegate to `test-integration`)
    *   **Process:** Use MDTM workflow, link tasks to `FEAT-021`.

2.  **Implement Read Operations (Feature):**
    *   **Goal:** Build `GET /[ResourceNamePlural]` (list) and `GET /[ResourceNamePlural]/{id}` (detail) endpoints.
    *   **Action:** Define as a Feature (`FEAT-022-read-[ResourceName].md`), linked to the parent. Set `status` to "Ready for Dev". Decompose into Tasks.
    *   **Tasks (Examples - Delegate to `dev-api`):**
        *   "Implement service logic to fetch list of `[ResourceNamePlural]` (with pagination/filtering parameters)."
        *   "Implement service logic to fetch single `[ResourceName]` by ID."
        *   "Implement API route/controller for `GET /[ResourceNamePlural]`."
        *   "Implement API route/controller for `GET /[ResourceNamePlural]/{id}`."
        *   "Handle 404 Not Found for detail view."
        *   "Format successful responses (200 OK)."
        *   "Write integration tests for both GET endpoints." (Delegate to `test-integration`)
    *   **Process:** Use MDTM workflow, link tasks to `FEAT-022`.

3.  **Implement Update Operation (Feature):**
    *   **Goal:** Build the `PUT /[ResourceNamePlural]/{id}` (or `PATCH`) endpoint.
    *   **Action:** Define as a Feature (`FEAT-023-update-[ResourceName].md`), linked to the parent. Set `status` to "Ready for Dev". Decompose into Tasks.
    *   **Tasks (Examples - Delegate to `dev-api`):**
        *   "Implement request body validation for Update `[ResourceName]`."
        *   "Implement service logic to find and update `[ResourceName]` record by ID."
        *   "Handle 404 Not Found."
        *   "Implement API route/controller for `PUT /[ResourceNamePlural]/{id}`."
        *   "Format successful response (e.g., 200 OK with updated resource)."
        *   "Write integration test for `PUT /[ResourceNamePlural]/{id}` endpoint." (Delegate to `test-integration`)
    *   **Process:** Use MDTM workflow, link tasks to `FEAT-023`.

4.  **Implement Delete Operation (Feature):**
    *   **Goal:** Build the `DELETE /[ResourceNamePlural]/{id}` endpoint.
    *   **Action:** Define as a Feature (`FEAT-024-delete-[ResourceName].md`), linked to the parent. Set `status` to "Ready for Dev". Decompose into Tasks.
    *   **Tasks (Examples - Delegate to `dev-api`):**
        *   "Implement service logic to find and delete `[ResourceName]` record by ID."
        *   "Handle 404 Not Found."
        *   "Implement API route/controller for `DELETE /[ResourceNamePlural]/{id}`."
        *   "Format successful response (e.g., 204 No Content)."
        *   "Write integration test for `DELETE /[ResourceNamePlural]/{id}` endpoint." (Delegate to `test-integration`)
    *   **Process:** Use MDTM workflow, link tasks to `FEAT-024`.

## Phase 3: Testing, Documentation & Finalization

1.  **Task Execution & Backend Testing:**
    *   **Goal:** Implement and unit/integration test the backend logic and endpoints.
    *   **Action:** Specialists execute tasks. `test-integration` verifies endpoint behavior, contracts, and status codes. Progress tracked via MDTM task files.

2.  **API Documentation:**
    *   **Goal:** Create clear documentation for the new API endpoints.
    *   **Action:** Define as a Feature or Task (`FEAT-025-document-[ResourceName]-api.md`). Delegate to `util-writer`.
    *   **Process:** `util-writer` reads the API design (Phase 1, Step 3) and potentially the implementation code (`read_file`) to generate documentation (e.g., OpenAPI/Swagger definition, updates to API documentation portal/markdown files).

3.  **Final Review & Feature Completion:**
    *   **Action:** Code review (`util-reviewer`) completed features. `manager-project` or Leads update Feature statuses to "Done". Update parent Epic status if applicable.

## Key Considerations for API Development:

*   **Consistency:** Maintain consistency with existing API design patterns in the application (authentication, error handling, response structure, naming conventions).
*   **Validation:** Implement robust input validation (e.g., using libraries like Zod, Pydantic) at the API boundary.
*   **Error Handling:** Implement consistent error handling and return appropriate HTTP status codes and informative error messages.
*   **Security:** Consider authorization (who can perform which actions?) and apply relevant security middleware/checks. Sanitize inputs to prevent injection attacks.
*   **Performance:** Consider database indexing for query performance, especially for list endpoints.
*   **Documentation Standard:** Use or establish a clear standard for API documentation (e.g., OpenAPI).

This playbook provides a structured flow for adding standard CRUD functionality to your backend API using Roo Commander.