# 8. Middleware

## Core Concept: Intercepting Requests & Responses

Middleware in FastAPI (and underlying Starlette) are functions or classes that sit between the web server and your path operation functions. They allow you to execute code globally for every incoming request and/or outgoing response, implementing cross-cutting concerns.

**Use Cases:**

-   Adding custom headers to responses (e.g., `X-Process-Time`).
-   Logging request/response details.
-   Handling CORS (Cross-Origin Resource Sharing).
-   Implementing GZip compression.
-   Adding global exception handling (though `@app.exception_handler` is often preferred).
-   Modifying request/response objects (use with caution).
-   Measuring request processing time.
-   Implementing certain types of authentication/authorization checks (though dependency injection is often preferred for endpoint-specific auth).

## Adding Middleware

Middleware is added to the FastAPI application instance using `app.add_middleware()`. The order matters, as middleware are processed sequentially for requests and in reverse order for responses.

```python
import time
import asyncio
from fastapi import FastAPI, Request
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
# from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseCall

app = FastAPI()

# --- Built-in Middleware Examples ---

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"], # Or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"], # Or specific methods ["GET", "POST"]
    allow_headers=["*"], # Or specific headers
)

# GZip Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000) # Compress responses > 1000 bytes

# --- Custom Middleware Example (@app.middleware) ---
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Calculates request processing time and adds 'X-Process-Time' header.
    """
    start_time = time.time()
    # Process the request by calling the next middleware or path operation
    response: Response = await call_next(request)
    # Code here runs *after* the response is generated
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request {request.method} {request.url.path} processed in {process_time:.4f} secs")
    return response

# --- Custom Middleware Example (Class-based) ---
# class CustomHeaderMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next: RequestResponseCall):
#         response = await call_next(request)
#         response.headers['X-Custom-Header'] = 'MyValue'
#         return response
# app.add_middleware(CustomHeaderMiddleware)

@app.get("/")
async def root():
    await asyncio.sleep(0.05) # Simulate work
    return {"message": "Hello World"}

```

## Middleware Types

-   **ASGI Middleware:** The most common type, operating directly on the ASGI `scope`, `receive`, and `send` messages. Added via `app.add_middleware()`. Examples: `CORSMiddleware`, `GZipMiddleware`.
-   **`@app.middleware("http")` Decorator:** A simpler way to define custom ASGI middleware. The decorated `async` function receives `request: Request` and `call_next`. You **must** `await call_next(request)` to pass control down the chain. Code *after* the `await` processes the response.
-   **`BaseHTTPMiddleware`:** A Starlette class providing a slightly higher-level abstraction for creating custom middleware classes. Implement `async def dispatch(self, request, call_next)`. Added via `app.add_middleware()`.

## Order of Execution

Middleware is processed in the order it is added for requests, and in reverse order for responses:

```
Request -> Middleware 1 -> Middleware 2 -> Path Op -> Middleware 2 -> Middleware 1 -> Response
```

## Middleware vs. Dependencies

-   **Middleware:** Applied broadly (often globally). Good for cross-cutting concerns like logging, CORS, compression, adding global headers. Operates on the raw request/response.
-   **Dependencies (`Depends`):** Applied per-path operation (or router). Better for logic specific to certain endpoints, sharing business logic, managing resources (DB sessions), complex parameter processing, fine-grained auth. Operates with parsed/validated data.

Often, a combination is used. Middleware provides a powerful way to add cross-cutting concerns to your FastAPI application.