# 6. Asynchronous Operations (`async`/`await`)

## Core Concept: Non-Blocking I/O

Traditional synchronous web frameworks handle one request at a time per worker process/thread. If a request involves waiting for external operations (like database queries, network API calls, reading files), the worker is blocked and cannot handle other requests during that wait time.

Asynchronous frameworks like FastAPI (built on Starlette and `asyncio`) use an event loop to handle multiple I/O-bound operations concurrently within a single process. When an operation needs to wait (e.g., waiting for a database response), the event loop switches to handle other tasks, and resumes the original operation once the wait is over. This allows a single worker to handle many concurrent requests efficiently, especially when requests involve waiting for external resources.

**Key Syntax:**

-   **`async def`:** Defines an asynchronous function (a coroutine).
-   **`await`:** Used *inside* an `async def` function to pause its execution and wait for an awaitable object (like another coroutine, e.g., an async database call or network request) to complete before resuming.

## Using `async def` in FastAPI

FastAPI seamlessly supports both standard synchronous (`def`) and asynchronous (`async def`) path operation functions.

-   **Use `async def` for I/O-bound operations:** If your path operation needs to perform network calls, database queries (using an async driver/ORM), file I/O, or wait for other external resources, declare it with `async def` and use `await` when calling those I/O-bound functions. This allows FastAPI/Starlette to handle other requests while waiting.
-   **Use `def` for CPU-bound operations:** If your path operation performs primarily CPU-intensive calculations (e.g., complex data processing, machine learning inference) without significant waiting, use a standard `def`. FastAPI/Starlette will run these in a separate threadpool to avoid blocking the main event loop.

```python
import asyncio
import httpx # Example async HTTP client
from fastapi import FastAPI, Depends

app = FastAPI()

# --- Async Path Operation ---
@app.get("/call-external-api")
async def get_external_data():
    # Use an async HTTP client like httpx
    async with httpx.AsyncClient() as client:
        # 'await' pauses this function while waiting for the network response,
        # allowing the server to handle other requests.
        response = await client.get("https://jsonplaceholder.typicode.com/todos/1")
        response.raise_for_status() # Raise exception for bad status codes
        external_data = response.json()

    # Simulate some async database query (using a hypothetical async ORM)
    # db_result = await async_db.fetch_one("SELECT * FROM items WHERE id = :id", {"id": 1})

    # Simulate another async operation
    await asyncio.sleep(0.1) # Non-blocking sleep

    return {"external": external_data, "message": "Data fetched"}

# --- Sync Path Operation (CPU-bound example) ---
def complex_calculation(n: int) -> int:
    # Simulate a CPU-intensive task
    result = 0
    for i in range(n):
        result += i * i % 1234
    return result

@app.get("/calculate/{number}")
def calculate_stuff(number: int):
    # FastAPI runs this 'def' function in a threadpool,
    # preventing it from blocking the main event loop.
    result = complex_calculation(number * 10000) # Simulate work
    return {"number": number, "result": result}

# --- Mixing Sync and Async Dependencies/Calls ---
async def async_dependency():
    await asyncio.sleep(0.05)
    return {"dep": "async"}

def sync_dependency():
    # Simulate some work
    _ = complex_calculation(1000)
    return {"dep": "sync"}

@app.get("/mixed")
async def read_mixed(
    # FastAPI handles calling sync dependencies correctly from async path ops
    sync_dep_result: dict = Depends(sync_dependency),
    async_dep_result: dict = Depends(async_dependency)
):
    # Calling sync code directly inside async def is generally okay if it's fast/non-blocking
    sync_calc_result = complex_calculation(500)

    # Calling blocking I/O inside async def is BAD - use await with async libraries
    # BAD: time.sleep(1) -> blocks the event loop! Use await asyncio.sleep(1)

    return {
        "sync_dep": sync_dep_result,
        "async_dep": async_dep_result,
        "sync_calc": sync_calc_result
    }

```

## When to Use `async def`

-   When your path operation needs to `await` an async function (database query with an async driver, HTTP request with `httpx`, `asyncio.sleep`, etc.).
-   When interacting with WebSocket connections (`await websocket.receive_text()`, `await websocket.send_text()`).
-   When calling other async libraries.
-   When using async dependencies.

## Common Pitfalls & Key Considerations

-   **Async Libraries:** To get the benefits of `async def`, you must use libraries that support `asyncio` for I/O operations (e.g., `httpx` for HTTP requests, `asyncpg` or SQLAlchemy 1.4+/2.0 with async drivers for databases, `aiofiles` for file I/O). Using standard blocking libraries (like `requests` or older database drivers) inside an `async def` function will still block the event loop.
-   **Mixing Sync and Async Incorrectly:** Calling a blocking synchronous function (like `time.sleep()` or a sync database call) inside an `async def` path operation *without* running it in a threadpool (e.g., using `asyncio.to_thread` in Python 3.9+) will block the entire event loop, defeating the purpose of async. FastAPI handles standard `def` functions in a threadpool automatically, but be careful with libraries called *within* an `async def`.
-   **`await` Everything:** If you call an `async def` function, you *must* use `await` to actually run it and get its result. Forgetting `await` will not execute the coroutine and will likely cause errors or unexpected behavior.
-   **Sync in Async:** Calling *short-running*, non-blocking synchronous code from an `async def` function is generally fine.
-   **Async in Sync:** Calling `async def` functions from a standard `def` function requires special handling (e.g., `asyncio.run()`), which is usually *not* done within FastAPI path operations (declare the path operation as `async def` instead).
-   **Dependencies:** Dependencies can be `async def` or `def`. FastAPI handles calling them correctly regardless of whether the path operation function is `async def` or `def`.

Use `async def` for path operations that perform I/O-bound tasks using compatible asynchronous libraries to achieve high concurrency and performance in FastAPI. Use standard `def` for CPU-bound tasks.