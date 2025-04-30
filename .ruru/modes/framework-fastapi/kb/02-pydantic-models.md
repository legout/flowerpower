# 2. Pydantic Models: Validation & Serialization

## Core Concept: Data Shapes with Type Hints

Pydantic is a data validation and settings management library using Python type annotations. FastAPI leverages Pydantic models (`BaseModel`) extensively to:

1.  **Declare Request Bodies:** Define the expected structure and types of incoming JSON data.
2.  **Validate Data:** Automatically validate incoming request data against the model's type hints and validators. Returns structured HTTP 422 validation errors if checks fail.
3.  **Serialize Response Data:** Define the structure and types of outgoing JSON data using `response_model`. Pydantic handles converting your return data (e.g., ORM objects, dictionaries) into the specified JSON structure.
4.  **Generate OpenAPI Schema:** FastAPI uses Pydantic models to automatically generate the JSON Schema definitions within the OpenAPI documentation (`/docs`, `/redoc`), making the API structure clear.
5.  **Editor Support:** Provides excellent autocompletion and type checking within your editor for model attributes.
6.  **Data Conversion:** Pydantic attempts to convert incoming data to the declared types where possible (e.g., string "true" to boolean `True`).

## Defining Models (`BaseModel`)

It's common practice to define Pydantic models in a separate file, often named `schemas.py`.

-   Import `BaseModel` from `pydantic`.
-   Define a class inheriting from `BaseModel`.
-   Declare fields using standard Python type hints (`str`, `int`, `float`, `bool`, `list[T]`, `dict[K, V]`, `datetime`, etc.) and types from `typing` (`List`, `Optional`, `Union`, `Any`).
-   Provide default values if needed.
-   Use `Optional[T]` or `T | None` for optional fields (defaulting to `None` or using `Field(default=None)`).

```python
# schemas.py (example)
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Optional
from datetime import datetime

# --- Base Schema ---
class ItemBase(BaseModel):
    name: str = Field(..., min_length=3, description="The name of the item") # ... means required
    description: Optional[str] = Field(default=None, description="Optional item description")
    price: float = Field(..., gt=0, description="Price must be positive") # gt = greater than
    tags: List[str] = [] # List of strings, defaults to empty list

# --- Schema for Creation (Request Body) ---
class ItemCreate(ItemBase):
    # Inherits fields from ItemBase
    pass # No additional fields needed for creation in this example

    # Example configuration for automatic documentation
    class Config:
        schema_extra = {
            "example": {
                "name": "Example Item",
                "description": "A useful item.",
                "price": 19.99,
                "tags": ["new", "featured"]
            }
        }

# --- Schema for Update (Request Body - Partial Updates) ---
class ItemUpdate(BaseModel):
    # All fields optional for partial updates (PATCH)
    name: Optional[str] = Field(default=None, min_length=3)
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    tags: Optional[List[str]] = None

# --- Schema for User (Example of nested model) ---
class User(BaseModel):
    id: int
    username: str
    email: EmailStr # Pydantic provides specific types like EmailStr
    website: Optional[HttpUrl] = None # And HttpUrl

# --- Schema for Response ---
class ItemResponse(ItemBase):
    id: int
    owner: User # Nested Pydantic model
    created_at: datetime

    # Pydantic V2: Use model_config = ConfigDict(...)
    # Pydantic V1: Use class Config: orm_mode = True
    model_config = {
        "from_attributes": True # Allow creating model from ORM object attributes
    }
    # class Config: # Pydantic V1 syntax
    #     orm_mode = True
```

## Key Pydantic Features for FastAPI

-   **`BaseModel`:** Inherit from this to create your data models.
-   **Type Hints:** Use standard Python types and `typing` module types.
-   **`Field()`:** Used to provide extra validation rules and metadata:
    -   `...` (Ellipsis): Marks a field as required.
    -   `default=None` or `Optional[type]` or `type | None`: Marks a field as optional.
    -   `min_length`, `max_length`: For strings.
    -   `gt`, `ge`, `lt`, `le`: For numbers (greater than, greater/equal, less than, less/equal).
    -   `description`: Adds description to OpenAPI schema.
    -   `example`/`examples`: Adds example data to OpenAPI schema.
    -   `alias`: Use a different name for the field in JSON.
-   **Special Types:** Pydantic provides useful types like `EmailStr`, `HttpUrl`, `UUID`, etc., for specific format validation.
-   **Nested Models:** You can nest Pydantic models within each other (e.g., an `Order` model containing a `List[Item]`).
-   **`Config` / `model_config`:** Inner class or attribute for configuring model behavior (e.g., `orm_mode`/`from_attributes` for ORM integration, `schema_extra` for examples).

## Using Models in Path Operations

-   **Request Body:** Type hint a path operation parameter with your Pydantic model. FastAPI automatically reads the request body as JSON, validates it, and provides the parsed Pydantic model instance.
-   **Response Model:** Use the `response_model` parameter in the path operation decorator (`@app.post(...)`) to specify the Pydantic model for the response. FastAPI filters the return value to match the model and serializes it.

```python
# main.py
from fastapi import FastAPI, HTTPException, Depends, status
from typing import List
from .schemas import ItemCreate, ItemResponse, ItemUpdate, User # Import models
from datetime import datetime

app = FastAPI()

# In-memory "database" for example
fake_items_db = []

@app.post(
    "/items/",
    response_model=ItemResponse, # Define the response shape
    status_code=status.HTTP_201_CREATED # Set default success status code
)
async def create_item(
    item_in: ItemCreate, # Request body validated against ItemCreate model
):
    # 'item_in' is now a validated Pydantic model instance
    # In a real app, save to DB and get ID, owner, created_at
    # Placeholder response:
    owner_data = User(id=1, username="testuser", email="test@example.com")
    response_data = ItemResponse(
        id=len(fake_items_db) + 1,
        owner=owner_data,
        created_at=datetime.now(),
        **item_in.model_dump() # Use model_dump() in Pydantic V2
    )
    fake_items_db.append(response_data) # Store the response-like object
    return response_data

@app.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(item_id: int):
    if item_id < 1 or item_id > len(fake_items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_items_db[item_id - 1]

@app.patch("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_update: ItemUpdate):
    if item_id < 1 or item_id > len(fake_items_db):
        raise HTTPException(status_code=404, detail="Item not found")

    stored_item_model = fake_items_db[item_id - 1]
    update_data = item_update.model_dump(exclude_unset=True) # Get only provided fields

    # Update the stored model - Pydantic V2
    updated_item = stored_item_model.model_copy(update=update_data)

    # # Pydantic V1 way:
    # stored_item_data = stored_item_model.dict()
    # stored_item_data.update(update_data)
    # updated_item = ItemResponse(**stored_item_data)

    fake_items_db[item_id - 1] = updated_item
    return updated_item
```

Pydantic models are fundamental to FastAPI, providing data validation, serialization, and documentation with minimal code. Define them clearly using type hints and `Field` for validation rules. Use separate models for creation/input (`ItemCreate`) and output (`ItemResponse`) to control data exposure and validation requirements.