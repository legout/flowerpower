# 5. Dependency Injection (`Depends`)

## Core Concept: Injecting Dependencies into Path Operations

FastAPI includes a powerful yet simple dependency injection (DI) system based on the `Depends` function (and `Annotated` type hints). It allows you to declare dependencies (which are typically functions, but can also be classes) that your path operation functions require. FastAPI takes care of executing these dependencies and "injecting" their results into your path operation function as arguments.

**Benefits:**

-   **Code Reusability:** Share common logic (e.g., getting the current user, database session management, complex parameter validation) across multiple path operations without repeating code.
-   **Separation of Concerns:** Keep path operation functions focused on their core business logic by moving dependency setup/retrieval elsewhere.
-   **Resource Management:** Dependencies using `yield` can manage setup and teardown logic (e.g., opening and closing database connections/sessions).
-   **Testability:** Dependencies can be easily overridden during testing, allowing you to inject mocks or test doubles.
-   **Automatic Documentation:** Dependencies are integrated into the OpenAPI schema, showing how endpoints rely on shared components.
-   **Hierarchical Dependencies:** Dependencies can depend on other dependencies, creating a graph that FastAPI resolves automatically.
-   **Integration with Path Operations:** Dependencies can receive request data (path/query parameters, request body, headers, cookies) just like path operation functions.

## Defining Dependencies

A dependency is typically a function (sync or async) that can receive parameters just like a path operation function (from path, query, body, etc., including other dependencies).

```python
# dependencies.py (example file)
from fastapi import Depends, HTTPException, status, Header, Query
from typing import Optional, Annotated, AsyncGenerator # Use Annotated for Python 3.9+
from sqlmodel.ext.asyncio.session import AsyncSession # Assuming SQLModel/Async SQLAlchemy
# from database import AsyncSessionLocal # Assuming DB setup exists

# --- Simple Dependency Function ---
async def common_parameters(
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(default=100, le=1000) # Add validation via Query
):
    """Shared logic for common query parameters."""
    return {"q": q, "skip": skip, "limit": limit}

# --- Dependency for Authentication (Simplified) ---
async def get_current_user(token: Annotated[str | None, Header()] = None):
    """Dependency to get the current user based on a token."""
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # In a real app, decode token, fetch user from DB
    if token != "fake-valid-token":
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    # Return user data (e.g., a Pydantic model or dict)
    return {"username": "testuser", "email": "test@example.com", "id": 1}

# --- Dependency using 'yield' (for DB Session Management) ---
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency yielding an async database session."""
    # async with AsyncSessionLocal() as session: # Real implementation
    #     try:
    #         yield session
    #         await session.commit()
    #     except Exception:
    #         await session.rollback()
    #         raise
    #     finally:
    #         await session.close()
    # Placeholder:
    print("DB Session Opened (Simulated)")
    session = {"connection": "fake_db_connection", "exec": lambda stmt: print(f"Executing: {stmt}")} # Simulate session
    yield session # Yield the resource
    print("DB Session Closed (Simulated)")


# --- Type Aliases for Dependencies (Recommended) ---
CommonsDep = Annotated[dict, Depends(common_parameters)]
CurrentUserDep = Annotated[dict, Depends(get_current_user)] # Use your User schema here ideally
SessionDep = Annotated[dict, Depends(get_db_session)] # Use AsyncSession type hint ideally
```

## Using Dependencies in Path Operations

-   Add a parameter to your path operation function, type hint it with `Annotated[ReturnType, Depends(dependency_function)]`.
-   FastAPI will call the `dependency_function`, inject its return value into your path operation parameter, and handle setup/teardown if `yield` is used.

```python
# main.py or routers/items.py
from fastapi import FastAPI
from typing import List
# from .dependencies import CommonsDep, CurrentUserDep, SessionDep
# from . import schemas

app = FastAPI() # Or APIRouter

@app.get("/items/")
async def read_items(commons: CommonsDep, db: SessionDep):
    print(f"Fetching items with params: {commons}")
    # Use db session from 'db' parameter
    # db['exec']("SELECT * FROM items") # Example usage
    return {"message": "Items fetched", "params": commons}

@app.get("/users/me")
async def read_users_me(current_user: CurrentUserDep):
    # If get_current_user raises HTTPException, it won't reach here
    return current_user

# Dependencies can also be used in other dependencies
async def get_admin_user(user: CurrentUserDep):
    if user.get("username") != "admin": # Simplified check
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return user

AdminUserDep = Annotated[dict, Depends(get_admin_user)]

@app.get("/admin/dashboard")
async def admin_dashboard(admin: AdminUserDep):
    return {"message": f"Welcome Admin {admin['username']}!"}
```

## Key Concepts Review

-   **`Depends(dependency)`:** Marks a parameter as requiring a dependency.
-   **`Annotated[Type, Depends(dependency)]`:** The preferred syntax in modern Python/FastAPI, combining the type hint and dependency declaration.
-   **Return Value Injection:** The value returned (or yielded) by the dependency function is passed to the path operation function parameter.
-   **`yield` for Setup/Teardown:** If a dependency function uses `yield`, the code before `yield` runs before the path operation, and the code after `yield` runs after the response is sent (useful for closing DB connections, releasing resources).
-   **Caching:** FastAPI caches the result of a dependency *within the same request*. If multiple path operations or dependencies in the same request depend on the *same* dependency function with the *same* parameters, it's only called once per request.
-   **Sub-Dependencies:** Dependencies can depend on other dependencies using the same `Depends`/`Annotated` syntax. FastAPI resolves the entire dependency graph.
-   **Path/Query/Body in Dependencies:** Dependency functions can declare parameters just like path operation functions to receive path parameters, query parameters, request bodies, headers, etc.

Dependency injection is a cornerstone of FastAPI, promoting cleaner, more modular, and testable code. Use it to handle authentication, database sessions, complex parameter processing, and other shared logic.