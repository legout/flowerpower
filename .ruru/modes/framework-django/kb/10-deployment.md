# Django: Deployment Strategies Overview

Considerations and common patterns for deploying Django applications to production.

## Core Concept: Moving from Development to Production

Deployment involves moving from the development server (`runserver`) to a production environment with a robust setup for reliability, security, and performance.

**Key Differences & Requirements in Production:**

*   **Web Server:** Use Nginx or Apache (not `runserver`). Handles HTTP requests, serves static files, terminates SSL, acts as reverse proxy.
*   **Application Server (WSGI/ASGI):** Runs the Django application.
    *   **WSGI (Synchronous):** Gunicorn, uWSGI. Use `project.wsgi:application`.
    *   **ASGI (Asynchronous):** Uvicorn, Daphne, Hypercorn. Use `project.asgi:application`. Needed for async features (Channels).
*   **Static Files:** Served directly by the web server or CDN (via `collectstatic` and `STATIC_ROOT`).
*   **Database:** Use PostgreSQL, MySQL, etc. (not SQLite).
*   **Security:** `DEBUG = False`, secret `SECRET_KEY` (via env vars), `ALLOWED_HOSTS` configured, HTTPS enforced.
*   **Environment Variables:** Manage configuration (secrets, DB URLs) via environment variables.

## Common Deployment Architecture

```
User -> DNS -> [Load Balancer] -> Web Server (Nginx/Apache)
                                     |        ^
                                     |        | (Static/Media Files)
                                     v        |
                  [Process Mgr (systemd)] -> App Server (Gunicorn/Uvicorn) <-> Django App
                                                 |
                                                 v
                                             Database (Postgres/MySQL)
                                                 |
                                                 v
                                             [Cache (Redis)]
                                                 |
                                                 v
                                             [Task Queue (Celery)]
```

*   **Web Server (Nginx/Apache):** Handles connections, serves static/media, proxies to App Server.
*   **App Server (Gunicorn/Uvicorn):** Runs Django via WSGI/ASGI interface, manages worker processes.
*   **Process Manager (systemd/supervisor):** Keeps the App Server running reliably.

## Deployment Checklist (Conceptual)

1.  **Production Settings (`settings.py`):**
    *   `DEBUG = False`
    *   `ALLOWED_HOSTS = ['yourdomain.com', ...]`
    *   Load `SECRET_KEY`, `DATABASES`, etc., from environment variables.
    *   Configure `STATIC_ROOT`, `STATIC_URL`, `MEDIA_ROOT`, `MEDIA_URL`.
    *   Configure production `CACHES`, `LOGGING`.
    *   Configure HTTPS settings (`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, etc.).
2.  **Server Setup:** Provision server (VPS, cloud instance) or use PaaS (Heroku, Render).
3.  **Install Dependencies:** Python, `pip`, DB drivers, `requirements.txt` (in virtual env).
4.  **Database Setup:** Create production DB/user. Run `python manage.py migrate`.
5.  **Collect Static Files:** `python manage.py collectstatic`.
6.  **Configure Web Server (e.g., Nginx):**
    *   Server block for domain.
    *   Serve `/static/` from `STATIC_ROOT`.
    *   Serve `/media/` from `MEDIA_ROOT` (if applicable).
    *   Reverse proxy requests to App Server (e.g., via Unix socket `proxy_pass http://unix:/path/to/gunicorn.sock;`).
    *   Configure SSL/TLS (HTTPS).
7.  **Configure Application Server (e.g., Gunicorn):**
    *   Install (`pip install gunicorn`).
    *   Run via Process Manager.
    *   Command: `gunicorn --workers 3 --bind unix:/path/to/socket.sock project.wsgi:application` (adjust workers, binding, WSGI path).
    *   For ASGI (Uvicorn): `uvicorn --workers 3 --uds /path/to/socket.sock project.asgi:application`
8.  **Configure Process Manager (e.g., `systemd`):**
    *   Create service file (`.service`) to manage the Gunicorn/Uvicorn process (user, working directory, virtual env activation, start command, restart policy).
9.  **System Checks:** `python manage.py check --deploy`.
10. **Start Services:** Enable/start systemd service, ensure web server is running.
11. **Monitoring & Logging:** Set up application/server monitoring and log aggregation.

**Platform-as-a-Service (PaaS):** Services like Heroku, Render, PythonAnywhere abstract server management. Typically involves pushing code, `requirements.txt`, and a `Procfile` (e.g., `web: gunicorn project.wsgi`).

Deployment requires careful configuration. Choose between manual setup or PaaS. Coordinate closely with `infrastructure-specialist` / `devops-lead`.