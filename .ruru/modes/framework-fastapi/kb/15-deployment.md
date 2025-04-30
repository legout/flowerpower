# 15. Deployment Considerations

## ASGI Servers: Uvicorn & Gunicorn

FastAPI is an ASGI (Asynchronous Server Gateway Interface) framework. To run it in production, you need an ASGI server. Common choices include:

-   **Uvicorn:** A lightning-fast ASGI server, built on uvloop and httptools. Often used for development (`uvicorn main:app --reload`) and can be used directly in production, potentially with multiple worker processes.
    ```bash
    # Development
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

    # Production (example with 4 workers)
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    ```
-   **Gunicorn with Uvicorn Workers:** Gunicorn is a mature, robust WSGI server often used as a process manager in production. You can use it to manage Uvicorn workers for running ASGI applications like FastAPI. This provides better process management, graceful restarts, and scaling capabilities compared to running Uvicorn directly with `--workers`.
    ```bash
    # Install gunicorn: pip install gunicorn
    # Run gunicorn managing uvicorn workers
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000
    ```
    -   `-w 4`: Specifies 4 worker processes. Adjust based on CPU cores (e.g., `2 * num_cores + 1`).
    -   `-k uvicorn.workers.UvicornWorker`: Tells Gunicorn to use Uvicorn's worker class for handling ASGI.
    -   `app.main:app`: Path to your FastAPI application instance.
    -   `-b 0.0.0.0:8000`: Bind to address and port.

## Containerization (Docker)

Containerizing your FastAPI application using Docker is highly recommended for consistent deployments.

-   **`Dockerfile`:** Defines the steps to build your application image, including installing dependencies and copying code.
-   **`.dockerignore`:** Excludes unnecessary files/directories from the build context.

```dockerfile
# Dockerfile Example
FROM python:3.11-slim

WORKDIR /app

# Install poetry (or use requirements.txt)
# RUN pip install poetry
COPY poetry.lock pyproject.toml ./
# RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi
# Or using requirements.txt:
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app /app/app

# Command to run the application using Gunicorn + Uvicorn workers
# Adjust the number of workers (-w) based on your server resources
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "-b", "0.0.0.0:8000"]

# Or using Uvicorn directly (simpler, less robust process management)
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Reverse Proxy (Nginx, Traefik)

In production, you typically run your ASGI server (Uvicorn/Gunicorn) behind a reverse proxy like Nginx or Traefik.

**Benefits:**

-   **Load Balancing:** Distribute traffic across multiple instances/workers of your application.
-   **HTTPS/SSL Termination:** Handle SSL certificates and encryption/decryption.
-   **Serving Static Files:** Efficiently serve static assets (CSS, JS, images).
-   **Caching:** Cache responses to improve performance.
-   **Security:** Can provide an additional layer of security (e.g., rate limiting, blocking malicious requests).

## Other Considerations

-   **Environment Variables:** Manage configuration (database URLs, secret keys, etc.) using environment variables, not hardcoded values. Use libraries like Pydantic's `BaseSettings` for loading.
-   **Database Migrations:** Use tools like Alembic (for SQLAlchemy/SQLModel) to manage database schema changes.
-   **Logging:** Configure structured logging to capture important events and errors.
-   **Monitoring:** Set up monitoring tools (e.g., Prometheus, Grafana, Datadog) to track application performance and health.
-   **CI/CD:** Automate testing and deployment using CI/CD pipelines (e.g., GitHub Actions, GitLab CI, Jenkins).

Deployment involves running your FastAPI app with an ASGI server (like Uvicorn managed by Gunicorn), often containerized with Docker, and usually placed behind a reverse proxy like Nginx. Remember to manage configuration via environment variables and set up proper logging and monitoring. For complex deployment scenarios, escalate to `infrastructure-specialist` or `cicd-specialist`.