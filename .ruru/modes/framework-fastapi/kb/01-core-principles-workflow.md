# 1. Core Principles & Workflow

## General Operational Principles

-   **Clarity and Precision:** Ensure all Python code, type hints, Pydantic models, path operations, explanations, and instructions are clear, concise, and accurate.
-   **Best Practices:** Adhere to established best practices for FastAPI, including project structure, path operation functions, Pydantic models for request/response validation, dependency injection, authentication/authorization, background tasks, WebSockets, ORM integration (e.g., SQLModel), custom middleware, and asynchronous programming (`async`/`await`).
-   **Type Hints & Pydantic:** Leverage Python type hints and Pydantic `BaseModel` extensively for automatic data validation, serialization, and API documentation.
-   **Async Operations:** Utilize `async def` for path operations involving I/O (network, database) to maximize performance.
-   **Dependency Injection:** Use FastAPI's `Depends` system effectively for managing dependencies (like database sessions, authentication logic) and promoting code reusability.
-   **Tool Usage Diligence:**
    -   Use tools iteratively, waiting for confirmation after each step.
    -   Analyze API requirements (endpoints, data models, validation) and **project context (Stack Profile)** before coding.
    -   Prefer precise tools (`apply_diff`, `insert_content`) over `write_to_file` for existing Python files.
    -   Use `read_file` to examine existing API code, Pydantic models, or relevant context files.
    -   Use `ask_followup_question` only when necessary information (like specific endpoint logic, data validation rules, or clarification on requirements) is missing.
    -   Use `execute_command` for CLI tasks (e.g., running the Uvicorn/Gunicorn server: `uvicorn main:app --reload`), explaining the command clearly. Check `environment_details` for running terminals.
    -   Use `attempt_completion` only when the task is fully verified and meets acceptance criteria.
-   **Documentation:** Leverage FastAPI's automatic interactive API documentation (Swagger UI / ReDoc) by using type hints, Pydantic models, and docstrings effectively.
-   **Efficiency:** Write performant API endpoints, utilizing asynchronous operations where appropriate.
-   **Communication:** Report progress clearly and indicate when tasks are complete.

## Workflow / Operational Steps

1.  **Receive Task & Context:** Get assignment (with Task ID `[TaskID]`), API requirements (endpoints, models, validation, auth), and **relevant context** (e.g., Stack Profile, related task logs, architecture docs). **Guidance:** Log the initial goal to the task log file (`.ruru/tasks/[TaskID].md`).
    *   *Initial Log Content Example:*
        ```markdown
        # Task Log: [TaskID] - FastAPI Feature: [Feature Purpose]

        **Goal:** Implement [brief goal, e.g., WebSocket endpoint for real-time updates].
        **Context:** [Link to Stack Profile/Requirements Doc]
        ```
2.  **Plan:** Define Pydantic models (`BaseModel`) for data validation/serialization. Outline path operation functions (`@app.get`, `@app.post`, `@app.websocket`, etc.) using `async def` where appropriate. Plan dependency injection (`Depends`). Consider necessary middleware, background tasks, or ORM integration (e.g., SQLModel). Plan application structure (`APIRouter`) if applicable.
3.  **Implement:** Write or modify Python code (`.py` files). Define Pydantic models. Create path operation functions (using `async def` for I/O). Implement business logic, validation, WebSockets, background tasks, or middleware as required. Utilize `Depends` for dependency injection. Integrate with ORMs if needed.
4.  **Consult Resources:** When specific FastAPI features, Pydantic validation, dependency injection patterns, authentication methods, WebSocket handling, ORM usage, or advanced patterns are needed, consult:
    *   Official FastAPI Docs: https://fastapi.tiangolo.com/
    *   Project-specific documentation or existing code patterns.
    *   Relevant files within this `custom-instructions` directory.
    (Use `browser` tool or `read_file` as appropriate).
5.  **Test:** Guide the user on running the development server (e.g., `uvicorn main:app --reload` or using Gunicorn) and testing the API endpoints (using `curl`, Postman, or built-in docs `/docs`). Emphasize writing automated tests using **`pytest`** and FastAPI's **`TestClient`** (which supports `async` via **`httpx`**).
6.  **Log Completion & Final Summary:** Append the final status, outcome, concise summary, and references to the task log file (`.tasks/[TaskID].md`). **Guidance:** Log completion using `insert_content`.
    *   *Final Log Content Example:*
        ```markdown
        ---
        **Status:** ✅ Complete
        **Outcome:** Success
        **Summary:** Implemented WebSocket endpoint `/ws/updates` using Pydantic for messages and async handling.
        **References:** [`main.py` (modified), `schemas.py` (created)]
        ```
7.  **Report Back:** Inform the user or coordinator of the completion using `attempt_completion`, referencing the task log file (`.ruru/tasks/[TaskID].md`).

## Core Concepts Reminder

FastAPI is a modern, high-performance Python web framework for building APIs, particularly RESTful APIs. It leverages standard Python type hints for data validation, serialization/deserialization (via Pydantic), and automatic interactive API documentation (Swagger UI, ReDoc). It is designed for high performance, ease of use, and rapid development, supporting both asynchronous (async/await) and synchronous code.