# 4. Request Body Handling

## Core Concept: Data from the Client

When a client needs to send data to the API (e.g., creating or updating a resource), it usually sends it in the **request body**. FastAPI excels at handling request bodies, especially JSON data, by leveraging Pydantic models.

**Workflow:**

1.  **Define Model:** Create a Pydantic `BaseModel` that defines the expected structure and data types of the incoming request body (see `02-pydantic-models.md`).
2.  **Declare Parameter:** Add a parameter to your path operation function, type-hinting it with the Pydantic model.
3.  **FastAPI Handles It:**
    -   FastAPI detects that the parameter is a Pydantic model.
    -   It reads the request body (assuming JSON by default).
    -   It validates the data against the Pydantic model.
        -   If valid: Converts the JSON data into an instance of your Pydantic model and passes it to your function as the argument.
        -   If invalid: Automatically returns an HTTP 422 Unprocessable Entity error response detailing the validation errors.
    -   It documents the expected request body schema in the OpenAPI documentation.

## Using Pydantic Models for Request Bodies

```python
from fastapi import FastAPI, status, Body, Query
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

app = FastAPI()

# --- Define Pydantic Models (e.g., in schemas.py) ---
class Item(BaseModel):
    name: str = Field(..., min_length=3)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    tags: List[str] = []

class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

# --- Use Models in Path Operations ---

# Example: Creating an item
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item): # 'item' parameter expects JSON matching the Item model
    # If validation passes, 'item' is an instance of the Item model
    print(f"Received item: {item.name}, Price: {item.price}")
    # Access data using dot notation: item.name, item.price
    # ... save item to database ...
    item_dict = item.model_dump() # Use model_dump() in Pydantic V2
    item_dict.update({"id": "new_item_id"}) # Simulate adding an ID
    return item_dict

# Example: Updating an item (using PUT - requires all fields)
@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item): # Expects full Item data in body
    print(f"Updating item {item_id} with data: {item.model_dump()}")
    # ... find existing item and update ...
    return {"item_id": item_id, **item.model_dump()}

# Example: Receiving multiple models (e.g., item and user)
# By default, FastAPI expects separate Pydantic models to be fields of a single JSON body
# Client would send: {"item": {...}, "user": {...}}
@app.post("/offers/")
async def create_offer(item: Item, user: User):
    return {"offer_detail": f"Offer for {item.name} by {user.username}"}

# Example: Receiving a list of items
@app.post("/items/bulk/")
async def create_bulk_items(items: List[Item]):
    # FastAPI expects a JSON array of objects matching the Item model: [{...}, {...}]
    created_ids = []
    for item in items:
        print(f"Processing bulk item: {item.name}")
        # ... save item ...
        created_ids.append(f"new_{item.name}_id")
    return {"created_item_ids": created_ids}

# Example: Embedding a single body parameter
# If you want the client to send {"item": {...}} instead of just {...} for a single model
# Use Body(..., embed=True)
# from fastapi import Body
# @app.post("/items/embedded/")
# async def create_embedded_item(item: Item = Body(..., embed=True)):
#     return {"item": item}

```

## Request Body + Path + Query Parameters

You can mix path parameters, query parameters, and request body parameters in the same path operation function. FastAPI correctly identifies each based on its declaration:

-   Parameters declared in the path are **path parameters**.
-   Parameters that are Pydantic models are **request body** parameters by default.
-   Other parameters (with default values or no default) are **query parameters**.

```python
@app.put("/users/{user_id}/items/{item_id}")
async def update_user_item(
    user_id: int,                 # Path parameter
    item_id: str,                 # Path parameter
    item: Item,                   # Request body
    importance: int = Query(1),   # Query parameter (optional, default 1)
    q: Optional[str] = None       # Query parameter (optional)
):
    results = {"user_id": user_id, "item_id": item_id, "importance": importance, **item.model_dump()}
    if q:
        results.update({"q": q})
    # ... update logic ...
    return results
```

Declare request bodies by type-hinting path operation parameters with Pydantic `BaseModel` subclasses. FastAPI handles reading the body, validating the data against the model, providing the validated data as a model instance to your function, and documenting the expected schema. This significantly simplifies handling complex input data.