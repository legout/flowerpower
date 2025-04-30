# 9. Project Structure & Routing (`APIRouter`)

## Problem: Single File Limitations

For very small APIs, defining all path operations in a single `main.py` might be sufficient. However, as the application grows, this becomes unmanageable.

## Solution: `APIRouter`

FastAPI provides `APIRouter`, which works like a mini `FastAPI` application. It allows you to group related path operations together, typically within separate Python modules (files). You can then include these routers in your main `FastAPI` application instance.

**Benefits:**

-   **Modularity:** Keeps related endpoints together (e.g., all user-related endpoints in `users.py`, all item-related endpoints in `items.py`).
-   **Organization:** Improves code readability and maintainability.
-   **Reusability:** Routers can potentially be reused or shared.
-   **Prefixing & Tagging:** Routers can have a common URL prefix (e.g., `/users`) and tags applied to all their path operations for documentation.
-   **Scalability:** Better structure for larger projects with many endpoints.

## Implementation Steps

1.  **Create Router Files:** Create separate Python files for different logical sections of your API (e.g., `app/routers/users.py`, `app/routers/items.py`).
2.  **Instantiate `APIRouter`:** In each router file, import and create an instance of `APIRouter`. Configure `prefix`, `tags`, and router-level `dependencies` or `responses` if needed.
3.  **Define Path Operations on Router:** Use the router instance decorator (`@router.get`, `@router.post`, etc.) instead of the main app instance (`@app.get`).
4.  **Include Router in Main App:** In your main application file (`app/main.py`), import the router instances and include them in the main `FastAPI` app using `app.include_router()`.

**Example Structure:**

```
your_project/
└── app/                  # Main application package
    ├── __init__.py
    ├── main.py           # Main FastAPI app instance, includes routers
    ├── schemas.py        # Pydantic models
    ├── crud.py           # Database interaction functions (optional)
    ├── dependencies.py   # Dependency functions (optional)
    ├── database.py       # Database connection setup (optional)
    └── routers/          # Sub-package for routers
        ├── __init__.py
        ├── items.py      # Router for item-related endpoints
        └── users.py      # Router for user-related endpoints
```

**Example: `app/routers/items.py`**

```python
# app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated
from .. import schemas, crud # Relative imports from parent package
from ..dependencies import SessionDep, get_current_active_user # Relative imports

# Create a router instance
router = APIRouter(
    prefix="/items", # All routes in this router will start with /items
    tags=["Items"], # Group endpoints under "Items" tag in docs
    # dependencies=[Depends(get_current_active_user)], # Apply dependency to ALL routes in this router
    responses={404: {"description": "Item not found"}}, # Default response for this router
)

@router.get("/", response_model=List[schemas.ItemResponse])
async def read_items(
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    items = await crud.get_items(db=db, skip=skip, limit=limit) # Assuming async crud function
    return items

@router.post("/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: schemas.ItemCreate,
    db: SessionDep,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)] # Require auth here
):
    # Example: Check for existing item before creation
    # db_item = await crud.get_item_by_name(db, name=item.name)
    # if db_item:
    #     raise HTTPException(status_code=400, detail="Item name already registered")
    return await crud.create_user_item(db=db, item=item, user_id=current_user.id) # Assuming user ID needed

# ... other item-related endpoints (GET by ID, PUT, DELETE, etc.) ...
```

**Example: `app/main.py`**

```python
# app/main.py
from fastapi import FastAPI
from .routers import items, users # Import routers using relative path

app = FastAPI(title="My Structured API")

# Include the routers
app.include_router(users.router)
app.include_router(items.router)

# You can still define global path operations here if needed
@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

# Example: Add startup event (e.g., for creating DB tables)
# from .database import create_db_and_tables
# @app.on_event("startup")
# async def on_startup():
#     await create_db_and_tables()
```

## `include_router` Options

-   **`prefix`:** Add a URL prefix to all routes defined in the included router (e.g., `prefix="/api/v1"`).
-   **`tags`:** Add tags to all routes in the included router for documentation grouping.
-   **`dependencies`:** Apply dependencies (`List[Depends(...)]`) to all routes in the included router.
-   **`responses`:** Define default responses (`Dict[int | str, Dict[str, Any]]`) for status codes for all routes in the router.

Using `APIRouter` is the standard way to structure FastAPI applications beyond a few endpoints, promoting better organization and maintainability. Organize your code into logical modules (like `schemas`, `crud`, `dependencies`, `routers`) within a main application package (e.g., `app`).