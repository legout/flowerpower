# 13. Background Tasks

## Core Concept

Sometimes you need to perform an operation after sending a response to the client, without making the client wait for that operation to complete. Examples include sending email notifications, processing uploaded data, logging analytics, or calling slow external APIs not critical for the main response.

FastAPI provides a `BackgroundTasks` utility for these scenarios.

## Using `BackgroundTasks`

1.  **Import:** `from fastapi import BackgroundTasks, FastAPI, Depends`
2.  **Parameter:** Add a parameter to your path operation function (or a dependency) with a type hint of `BackgroundTasks`. FastAPI will automatically inject an instance.
3.  **Add Tasks:** Call the `.add_task()` method on the `BackgroundTasks` instance *before* returning the response.
    -   **Arguments:** `background_tasks.add_task(func, arg1, arg2, ..., kwarg1=value1, ...)`
        -   `func`: The function to run in the background (can be `def` or `async def`).
        -   Subsequent arguments (`arg1`, `arg2`, `kwarg1`, etc.) are passed directly to `func`.

```python
from fastapi import FastAPI, BackgroundTasks, Depends
import time
import asyncio

app = FastAPI()

# --- Example Background Task Functions ---

def write_log(message: str):
    # Simulate writing to a log file
    time.sleep(0.5) # Simulate blocking I/O (runs in threadpool if called from async def)
    with open("log.txt", mode="a") as log_file:
        log_file.write(message + "\n")
    print(f"Log written: {message}")

async def send_email_async(email: str, message: str):
    # Simulate sending an email asynchronously
    await asyncio.sleep(1) # Simulate async I/O
    print(f"Email sent to {email}: '{message}'")

# --- Path Operations ---

@app.post("/send-notification/{email}")
async def send_notification(
    email: str,
    message: str,
    background_tasks: BackgroundTasks # Inject BackgroundTasks
):
    # Add tasks to run *after* the response is sent
    background_tasks.add_task(write_log, f"Notification sent to {email}: {message}")
    background_tasks.add_task(send_email_async, email, message=f"Subject: Notification\n\n{message}")

    # Return response immediately
    return {"message": "Notification sending initiated in background"}

# --- Using BackgroundTasks with Dependencies ---

async def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        message = f"Query received: {q}"
        background_tasks.add_task(write_log, message) # Add task within dependency
    return q

@app.post("/query/")
async def process_query(query: str = Depends(get_query)):
    # The background task from get_query will run after this response
    if not query:
        return {"message": "No query provided"}
    return {"message": f"Processing query: {query}"}

```

## How it Works

-   FastAPI collects all tasks added via `background_tasks.add_task()` during the request-response cycle.
-   After the response is sent to the client, FastAPI runs the added tasks in the background using `anyio` (which handles both `async def` and standard `def` functions appropriately).
-   Standard `def` functions added as background tasks are run in a separate threadpool, preventing them from blocking the main event loop.
-   `async def` functions added as background tasks run directly within the event loop.

## Limitations & Alternatives

-   **Reliability:** `BackgroundTasks` are executed "fire and forget." If the server process crashes *after* the response is sent but *before* the background task completes, the task might be lost.
-   **No Return Value:** You cannot get a return value from a background task directly back to the client that initiated the request.
-   **Resource Intensive Tasks:** For very long-running or resource-intensive tasks, using a dedicated task queue system (like Celery with Redis/RabbitMQ, or ARQ) is generally more robust and scalable. Task queues provide features like retries, persistent storage, dedicated workers, and better monitoring.

Use `BackgroundTasks` for simple, relatively quick operations that need to happen after a response is sent and where occasional loss due to server restarts/crashes is acceptable. For critical or heavy background processing, prefer a dedicated task queue.