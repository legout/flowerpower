# 14. Testing (`pytest` & `TestClient`)

## Core Concept

FastAPI provides a `TestClient` class (based on `httpx`) that allows you to make requests directly to your FastAPI application *without* needing a running server. This makes testing fast and efficient. It's commonly used with `pytest` for test organization and fixtures.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install pytest httpx
    ```
2.  **Test File Structure:** Organize tests in a `tests/` directory. Use filenames like `test_main.py`, `test_users.py`, etc.
3.  **Import `TestClient`:** `from fastapi.testing import TestClient`
4.  **Import your FastAPI app:** `from app.main import app` (adjust path as needed).

## Basic Test Example (`pytest`)

```python
# tests/test_items.py
from fastapi.testclient import TestClient
from app.main import app # Import your FastAPI app instance

# Create a TestClient instance using your app
client = TestClient(app)

def test_create_item():
    item_data = {
        "name": "Test Item",
        "description": "A test description",
        "price": 12.50,
        "tags": ["testing"]
    }
    response = client.post(
        "/items/", # Assuming /items/ prefix is handled by router or app
        json=item_data # Pass request body data as json parameter
    )
    assert response.status_code == 201 # Check for 201 Created status
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["price"] == item_data["price"]
    assert "id" in data # Check if ID was assigned

def test_read_item_success():
    # Assuming an item with ID 1 exists (created in another test or fixture)
    response = client.get("/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data

def test_read_item_not_found():
    response = client.get("/items/99999") # Non-existent ID
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"} # Match your API's error response

def test_create_item_invalid_data():
    item_data = {"name": "No Price"} # Missing required 'price' field
    response = client.post("/items/", json=item_data)
    # FastAPI/Pydantic automatically return 422 for validation errors
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
    # Check that the error message relates to the missing 'price' field
    assert any(err["loc"] == ["body", "price"] for err in data["detail"])

# Add tests for PUT, PATCH, DELETE, authentication, edge cases, etc.
```

## Running Tests

-   Run `pytest` in your terminal from the project root directory. `pytest` will automatically discover files named `test_*.py` or `*_test.py` and functions/methods prefixed with `test_`.

## Testing Asynchronous Code

-   `TestClient` uses `httpx` which supports `asyncio`.
-   If your path operations are `async def`, your tests using `TestClient` **do not** need to be `async def`. `TestClient` handles the async execution internally.

## Testing Dependencies (`Depends`)

-   **Overriding Dependencies:** FastAPI allows you to override dependencies during testing. This is crucial for mocking external services, database connections, or authentication.
    -   Use `app.dependency_overrides[original_dependency] = override_function`.
    -   Define an `override_function` that returns the desired mock value or performs mock actions.
    -   Use `pytest` fixtures to manage the setup and teardown of overrides, ensuring tests are isolated.

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_current_user # Import original dependency
# from app import schemas # Import User schema if needed

# --- Mock Dependency ---
async def override_get_current_user_unauthenticated():
    # Simulate no user being authenticated
    # Depending on original dependency, either return None or raise HTTPException
    # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return None # Or adjust based on how get_current_user handles failure

async def override_get_current_user_authenticated():
    # Return a specific user for testing protected endpoints
    # return schemas.User(id=1, username="testuser", email="test@example.com", ...)
    return {"username": "testuser", "id": 1} # Simplified

# --- Test Client ---
client = TestClient(app)

# --- Tests ---
def test_read_users_me_authenticated():
    # Apply override specifically for this test (or use fixtures)
    app.dependency_overrides[get_current_user] = override_get_current_user_authenticated
    response = client.get("/users/me") # Assuming this endpoint requires auth
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    app.dependency_overrides = {} # Clean up override

def test_read_users_me_unauthenticated():
    app.dependency_overrides[get_current_user] = override_get_current_user_unauthenticated
    response = client.get("/users/me")
    # Assert based on how the original dependency handles failure
    assert response.status_code == 401 # Or check if endpoint allows None user
    assert "Not authenticated" in response.json().get("detail", "") # Example check
    app.dependency_overrides = {} # Clean up override

# Using fixtures for cleaner setup/teardown
@pytest.fixture
def authenticated_client():
    app.dependency_overrides[get_current_user] = override_get_current_user_authenticated
    yield TestClient(app) # Provide the client with override applied
    app.dependency_overrides = {} # Cleanup

def test_read_protected_resource(authenticated_client):
    response = authenticated_client.get("/items/protected") # Use the fixture
    assert response.status_code == 200
    # ... more assertions ...

```

## Testing WebSockets

-   `TestClient` provides a `websocket_connect()` context manager.

```python
def test_websocket_echo():
    with client.websocket_connect("/ws/echo") as websocket:
        websocket.send_text("Hello")
        data = websocket.receive_text()
        assert data == "Message text was: Hello"
        websocket.send_json({"msg": "test"})
        data = websocket.receive_json()
        assert data == {"msg": "test"} # Assuming endpoint echoes JSON too
```

Writing comprehensive tests using `TestClient` and `pytest` is crucial for ensuring the reliability and correctness of your FastAPI application. Utilize dependency overrides extensively to isolate your API logic from external systems during testing.