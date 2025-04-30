# Flask: Configuration & Deployment

Handling application configuration and deploying Flask applications using WSGI/ASGI servers.

## Configuration Management

### Core Concept
Flask applications need configuration for various settings, such as secret keys, database URIs, debugging flags, and extension-specific options. Flask provides a flexible system for loading configuration from different sources.

### `app.config` Object
*   The central place where Flask stores configuration values is the `app.config` object, which behaves like a dictionary.
*   Keys are typically uppercase (e.g., `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`).
*   Flask itself, as well as extensions, use values from `app.config`.

### Loading Configuration
There are several ways to load configuration, often used in combination, especially with the Application Factory pattern. Later sources override earlier ones.

1.  **Default Values (Directly on `app.config`):**
    ```python
    app = Flask(__name__)
    app.config['DEBUG'] = False # Set a default
    ```
2.  **From a Python File (`app.config.from_pyfile()`):**
    ```python
    # config.py
    DEBUG = True
    SECRET_KEY = 'my-dev-secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    ```
    ```python
    # In your app setup
    app.config.from_pyfile('config.py', silent=False)
    ```
3.  **From an Object (`app.config.from_object()`):** (Common for environments)
    ```python
    # config.py
    import os
    basedir = os.path.abspath(os.path.dirname(__file__))

    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-fallback-key'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        DEBUG = False
        TESTING = False
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'app.db')

    class DevelopmentConfig(Config):
        DEBUG = True
        SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'dev.db')

    class TestingConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
            'sqlite:///:memory:'
        WTF_CSRF_ENABLED = False

    class ProductionConfig(Config):
        pass # Load sensitive vars from environment

    config = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
    }
    ```
    ```python
    # In create_app() factory
    from config import config

    def create_app(config_name='default'):
        app = Flask(__name__)
        app.config.from_object(config[config_name])
        # ... initialize extensions ...
        return app
    ```
4.  **From Environment Variables (`app.config.from_envvar()`):** (Less common for direct loading)
    ```bash
    export YOURAPP_SETTINGS='/path/to/settings.cfg'
    ```
    ```python
    app.config.from_envvar('YOURAPP_SETTINGS')
    ```
5.  **From JSON (`app.config.from_json()`):**
    ```python
    app.config.from_json('config.json')
    ```
6.  **From Mapping (`app.config.from_mapping()` or `update()`):**
    ```python
    app.config.from_mapping(SECRET_KEY='dev')
    app.config.update(TESTING=True)
    ```

### Important Configuration Values
*   **`SECRET_KEY` (Critical):** Long, random, secret string. Load from environment in production.
*   **`DEBUG` (Boolean):** Enables debug mode. **Never `True` in production.**
*   **`TESTING` (Boolean):** Enables testing mode.
*   **`SQLALCHEMY_DATABASE_URI`:** Database connection string.
*   **`SQLALCHEMY_TRACK_MODIFICATIONS`:** Set to `False` unless needed.
*   **Extension-Specific Keys:** Refer to extension docs.

### Configuration Best Practices
*   **Use Environment Variables for Secrets:** Load `SECRET_KEY`, DB passwords, API keys from environment variables (use `.env` locally, ensure it's in `.gitignore`).
*   **Use Configuration Objects/Files:** Organize by environment (dev, test, prod).
*   **Application Factory:** Load configuration within `create_app`.
*   **Default Values:** Provide sensible defaults in a base `Config` class.

---

## Deployment (WSGI / ASGI)

### Core Concept: WSGI & ASGI
*   **WSGI (Web Server Gateway Interface):** Standard interface for **synchronous** Python web apps and servers.
*   **ASGI (Asynchronous Server Gateway Interface):** Successor for **asynchronous** apps (WebSockets, etc.), backward compatible with WSGI.
*   **Flask:** Fundamentally WSGI, can run on ASGI servers via adapters (e.g., Uvicorn's).

### Development Server vs. Production Servers
*   **Flask Dev Server (`flask run`):** For development ONLY. Not performant, secure, or stable for production.
*   **Production Servers:** Need a dedicated WSGI/ASGI server:
    *   **Gunicorn:** Mature, popular WSGI server (UNIX).
    *   **uWSGI:** Feature-rich WSGI/ASGI server (UNIX).
    *   **Uvicorn:** Fast ASGI server, can run WSGI apps (like Flask). Good for async needs.
    *   **Waitress:** Pure-Python WSGI server (Windows/UNIX).

### Deployment Strategy Overview
1.  **Choose & Install Server:** Select (Gunicorn, Uvicorn, etc.) and add to `requirements.txt`.
2.  **Create App Entry Point:** Ensure access to your `app` instance (often via `create_app()` in `wsgi.py`).
    ```python
    # wsgi.py
    from app import create_app
    app = create_app('production')
    ```
3.  **Configure Server:**
    *   **Gunicorn:** `gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app`
    *   **Uvicorn (WSGI):** `uvicorn --workers 4 --host 0.0.0.0 --port 8000 wsgi:app`
    *   **Waitress:** `waitress-serve --host 0.0.0.0 --port 8000 wsgi:app`
4.  **Reverse Proxy (Recommended):** Use **Nginx** or **Caddy** in front of the WSGI/ASGI server.
    *   **Benefits:** Handles HTTPS, serves static files, load balancing, security.
    *   **Config:** Proxy requests to the WSGI/ASGI server (e.g., `proxy_pass http://127.0.0.1:8000;` in Nginx).
5.  **Process Management:** Use `systemd`, `supervisor`, or container orchestrators (Docker/Kubernetes) to manage the server process.
6.  **Static Files:** Configure the reverse proxy (Nginx) to serve static files directly for better performance.

### Deployment Platforms
*   **PaaS:** Heroku, Google App Engine, Render, PythonAnywhere simplify deployment.
*   **Containers (Docker):** Package app and server, deploy via Docker Compose, Kubernetes, etc.
*   **Serverless:** Use Zappa, Chalice, etc., for AWS Lambda/API Gateway.
*   **VPS:** Manual setup of server, database, proxy, etc.

Choose based on needs, scalability, and operational preference. Always use a production server and preferably a reverse proxy.

*(Refer to the official Flask Configuration Handling and Deployment Options documentation.)*