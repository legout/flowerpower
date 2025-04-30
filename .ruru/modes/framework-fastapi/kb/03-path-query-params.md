# 3. Path and Query Parameters

## Core Concept: Parameter Declaration via Type Hints

FastAPI uses Python type hints in path operation function signatures to declare path and query parameters. This enables automatic data validation, conversion, and documentation.

-   **Path Parameters:** Parts of the URL path itself used to identify a specific resource (e.g., the `123` in `/items/123`). Declared using f-string-like syntax in the path decorator (`@app.get("/items/{item_id}")`) and as a corresponding function argument (`item_id: int`). They are always required.
-   **Query Parameters:** Key-value pairs appended to the URL after a `?` (e.g., `/items/?skip=0&limit=10`). Declared as function arguments that are *not* part of the path string. Providing a default value makes them optional (`limit: int = 10`).

## Declaring Path Parameters

```python
from fastapi import FastAPI, HTTPException, status, Path
from enum import Enum

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int): # Type hint 'int' provides validation
    # FastAPI automatically converts the path segment to an integer.
    # If conversion fails (e.g., /items/foo), it returns a 422 Validation Error.
    if item_id == 0: # Example custom validation
         raise HTTPException(status_code=400, detail="Item ID cannot be zero")
    return {"item_id": item_id}

@app.get("/users/{user_id}/orders/{order_id}")
async def read_user_order(user_id: str, order_id: int): # Multiple path parameters
    return {"user_id": user_id, "order_id": order_id}

# Path parameters with predefined possible values (using Enums)
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName): # Parameter must match one of the Enum values
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet": # Access enum value using .value
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}

# Path parameter containing a path itself
@app.get("/files/{file_path:path}") # Use the 'path' converter
async def read_file(file_path: str = Path(..., description="The full path to the file")):
    # file_path will contain everything after /files/, including slashes
    # Using Path(...) allows adding description, validation etc. '...' means required.
    return {"file_path": file_path}
```

## Declaring Query Parameters

```python
from fastapi import FastAPI, Query
from typing import List, Optional # Use Optional for Python < 3.10, | None for >= 3.10
from typing_extensions import Annotated # For more complex validation (Python 3.9+)

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# Basic query parameters with defaults (making them optional)
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10): # Default values make them optional
    # Access as regular function arguments: skip, limit
    # URL: /items/?skip=5&limit=20 or /items/
    return fake_items_db[skip : skip + limit]

# Optional parameters using Optional or | None
@app.get("/items/{item_id}")
async def read_item_details(item_id: str, q: Optional[str] = None, short: bool = False):
    # URL: /items/foo?q=searchterm&short=true or /items/foo
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"})
    return item

# Required query parameters (no default value)
@app.get("/users/{user_id}/permissions")
async def read_permissions(user_id: str, resource: str): # 'resource' is required
    # URL: /users/me/permissions?resource=articles
    return {"user_id": user_id, "resource": resource, "permissions": ["read", "write"]}

# Query parameters with complex validation using Query() or Annotated
@app.get("/search/")
async def search_items(
    q: Annotated[
            Optional[str],
            Query(
                min_length=3,
                max_length=50,
                title="Query string",
                description="Query string for the items to search",
                alias="query-term", # Use 'query-term' in URL instead of 'q'
                deprecated=True # Mark as deprecated in docs
            )
        ] = None,
    tags: Annotated[Optional[List[str]], Query(description="Tags to filter by")] = None # List/multiple query parameters
):
    # URL: /search/?query-term=test&tags=A&tags=B
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    if tags:
        results.update({"tags": tags})
    return results

# Older syntax using Query directly as default value
# async def search_items_old(
#     q: Optional[str] = Query(None, min_length=3, max_length=50),
#     tags: Optional[List[str]] = Query(None) # Use Query(None) or Query([]) for optional lists
# ): ...
```

## Key Points

-   FastAPI uses the function signature and type hints to determine if a parameter is path or query.
-   Path parameters *must* be present in the path string.
-   Query parameters are any other function arguments. Default values make them optional.
-   Type hints (`int`, `str`, `bool`, `float`, `Enum`) provide automatic data conversion and validation. Invalid data results in a 422 error.
-   Use `Optional[type]` or `type | None` for optional query parameters.
-   Use `List[type]` for query parameters that can appear multiple times (e.g., `?tags=A&tags=B`).
-   Use `Query()` (as default value or via `Annotated`) for adding extra validation (length, regex, etc.), descriptions, aliases, or deprecation status to query parameters. Use `Path()` similarly for path parameters if extra validation is needed beyond type conversion.

Declare path and query parameters directly in your path operation function signature with type hints for automatic validation, conversion, and documentation. Use `Query()` or `Path()` via `Annotated` for more advanced validation and metadata.