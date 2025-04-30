# 12. WebSockets

## Core Concept

WebSockets provide a full-duplex communication channel over a single TCP connection, allowing servers to push data to clients proactively without the client having to poll constantly. FastAPI has built-in support for handling WebSocket connections.

## Defining WebSocket Endpoints

-   Use the `@app.websocket("/path")` decorator on an `async def` function.
-   The function receives a `websocket: WebSocket` parameter.
-   The connection remains open as long as the function is running and the connection is active. You typically use a `while True` loop or similar structure within the function to continuously handle messages.

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query, Cookie, status
from typing import List, Annotated

app = FastAPI()

# Simple echo endpoint
@app.websocket("/ws/echo")
async def websocket_echo_endpoint(websocket: WebSocket):
    await websocket.accept() # Accept the incoming connection
    try:
        while True:
            # Wait for a message from the client
            data = await websocket.receive_text()
            # Send the received message back
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print(f"Client disconnected from /ws/echo")
    except Exception as e:
        print(f"Error in /ws/echo: {e}")
        # Optionally close with a code: await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

# Example: Simple Chat Broadcast Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, sender: WebSocket | None = None):
        for connection in self.active_connections:
            if connection != sender: # Don't send back to sender if specified
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"Failed to send message to a client: {e}")
                    # Consider disconnecting the problematic client
                    # self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws/chat/{client_id}")
async def websocket_chat_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    await manager.broadcast(f"Client #{client_id} joined the chat", sender=websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}", sender=websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat", sender=websocket)
        print(f"Client #{client_id} disconnected")
    except Exception as e:
        print(f"Error in /ws/chat/{client_id}: {e}")
        manager.disconnect(websocket) # Ensure disconnect on error
```

## `WebSocket` Object Methods

-   **`await websocket.accept()`:** Accepts the WebSocket connection. Must be called before sending/receiving messages.
-   **`await websocket.receive_text()`:** Waits for and receives a text message.
-   **`await websocket.receive_bytes()`:** Waits for and receives a binary message.
-   **`await websocket.receive_json()`:** Waits for and receives a JSON message (parses text/bytes as JSON). Raises `WebSocketDisconnect` or `RuntimeError` if data is not valid JSON.
-   **`await websocket.send_text(data: str)`:** Sends a text message.
-   **`await websocket.send_bytes(data: bytes)`:** Sends a binary message.
-   **`await websocket.send_json(data: Any, mode: str = "text")`:** Sends Python data as JSON (text or binary mode).
-   **`await websocket.close(code: int = 1000)`:** Closes the WebSocket connection with an optional status code (e.g., `status.WS_1000_NORMAL_CLOSURE`).

## Handling Disconnects

-   When a client disconnects, `websocket.receive_*` methods will raise a `WebSocketDisconnect` exception.
-   Use a `try...except WebSocketDisconnect:` block to handle cleanup logic (e.g., removing the connection from a list of active connections).
-   It's also good practice to include a general `except Exception:` block to catch other errors and potentially close the connection gracefully.

## Dependencies and Authentication

-   You can use `Depends` with WebSocket path operation functions just like with HTTP endpoints.
-   This is the standard way to handle authentication for WebSockets: create a dependency that verifies credentials (e.g., from query parameters or subprotocols during connection) and returns the user or raises an exception if authentication fails *before* `websocket.accept()` is called.

```python
async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    if session is None and token is None:
        # Close the connection if no credential provided
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        # Return None or raise to prevent endpoint execution after close
        return None
    # In a real app, validate session/token and return user or raise exception/close
    credential = session or token
    # user = await get_user_from_credential(credential) # Hypothetical validation
    # if not user:
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #     return None
    # return user
    return credential # Return validated credential/user

@app.websocket("/ws/secure")
async def secure_websocket_endpoint(
    websocket: WebSocket,
    # Use dependency to get credentials *before* accepting
    credential_or_user: Annotated[str | None, Depends(get_cookie_or_token)]
    # Use your actual User type hint if dependency returns it
):
    # If dependency closed the connection or returned None, stop processing
    if credential_or_user is None:
        return

    # If Depends didn't raise/close, credential is valid
    await websocket.accept()
    await websocket.send_text(f"Authenticated with credential: {credential_or_user}")
    # ... rest of the WebSocket logic ...
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Secure echo: {data}")
    except WebSocketDisconnect:
        print("Secure client disconnected")
```

## Scalability (Broadcasting)

-   Broadcasting messages to multiple clients (like in the chat example) requires a central `ConnectionManager`.
-   If running multiple instances of your FastAPI application, this simple in-memory manager won't work. You'll need a message queue or pub/sub system (like Redis, RabbitMQ, Kafka) to broadcast messages across instances. Each instance subscribes to the pub/sub channel and forwards messages to its connected WebSocket clients.