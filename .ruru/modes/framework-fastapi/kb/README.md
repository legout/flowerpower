# Custom Instructions for 🚀 FastAPI Developer Mode

This directory contains specific instructions and guidelines for the `fastapi-developer` mode, supplementing the core role definition.

## Files

1.  [`01-core-principles-workflow.md`](./01-core-principles-workflow.md): General operational guidelines, best practices, and standard workflow steps.
2.  [`02-pydantic-models.md`](./02-pydantic-models.md): Using Pydantic `BaseModel` for data validation, serialization, and documentation.
3.  [`03-path-query-params.md`](./03-path-query-params.md): Defining and validating parameters from URL paths and query strings.
4.  [`04-request-body.md`](./04-request-body.md): Handling request body data, typically JSON, using Pydantic models.
5.  [`05-dependency-injection.md`](./05-dependency-injection.md): Using `Depends` for shared logic, resource management, and code reuse.
6.  [`06-async-await.md`](./06-async-await.md): Best practices for asynchronous path operations and handling I/O-bound tasks.
7.  [`07-error-handling.md`](./07-error-handling.md): Using `HTTPException` and custom exception handlers for graceful error responses.
8.  [`08-middleware.md`](./08-middleware.md): Implementing custom logic to process requests and responses globally.
9.  [`09-project-structure-routing.md`](./09-project-structure-routing.md): Organizing larger applications using `APIRouter` for modular path operations.
10. [`10-security-auth.md`](./10-security-auth.md): Implementing basic security measures and authentication patterns (e.g., OAuth2 Bearer).
11. [`11-orm-sqlmodel.md`](./11-orm-sqlmodel.md): Integrating with databases using SQLModel (SQLAlchemy + Pydantic).
12. [`12-websockets.md`](./12-websockets.md): Implementing real-time bidirectional communication using WebSockets.
13. [`13-background-tasks.md`](./13-background-tasks.md): Running tasks in the background after returning a response using `BackgroundTasks`.
14. [`14-testing.md`](./14-testing.md): Writing automated tests using `pytest` and FastAPI's `TestClient`.
15. [`15-deployment.md`](./15-deployment.md): Considerations for deploying FastAPI applications (ASGI servers, Docker, reverse proxies).
16. [`16-collaboration-escalation.md`](./16-collaboration-escalation.md): Guidelines for collaborating with other modes and escalating tasks when necessary.