# Directus: Configuration & Deployment

Configuring, deploying, and managing Directus instances and extensions.

## 1. Configuration via Environment Variables (`.env`)

Directus is configured primarily through environment variables, typically loaded from a `.env` file in the project root or set directly in the deployment environment. **Never commit `.env` files with production secrets to Git.**

**Key Configuration Variables:**

*   **Database (Required):** `DB_CLIENT`, `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USER`, `DB_PASSWORD` (or `DB_CONNECTION_STRING`).
*   **Security (Required):**
    *   `KEY`: Random string for general crypto.
    *   `SECRET`: **CRITICAL** highly random string for signing auth tokens.
    *   `PUBLIC_URL`: Public-facing URL of the instance (e.g., `https://directus.example.com`).
*   **Admin User (Initial):** `ADMIN_EMAIL`, `ADMIN_PASSWORD`.
*   **Authentication:** `AUTH_PROVIDERS`, `AUTH_{PROVIDER_NAME}_*`, `ACCESS_TOKEN_TTL`, `REFRESH_TOKEN_TTL`, etc. (See `05-security-auth-permissions.md`).
*   **Email:** `EMAIL_FROM`, `EMAIL_TRANSPORT`, `EMAIL_SMTP_*`, etc.
*   **CORS:** `CORS_ENABLED`, `CORS_ORIGIN`, etc.
*   **Rate Limiting:** `RATE_LIMITER_ENABLED`, `RATE_LIMITER_POINTS`, `RATE_LIMITER_DURATION`.
*   **Caching:** `CACHE_ENABLED`, `CACHE_STORE` (`memory` or `redis`), `CACHE_REDIS`, `CACHE_TTL`.
*   **File Storage:** `STORAGE_LOCATIONS`, `STORAGE_{LOCATION}_DRIVER`, `STORAGE_{LOCATION}_*` (see below).
*   **WebSockets:** `WEBSOCKETS_ENABLED`, `WEBSOCKETS_BROKER_URL` (for scaling).
*   **Extensions:** `EXTENSIONS_PATH` (default: `./extensions`).
*   **Logging:** `LOG_LEVEL`, `LOG_TYPE`, `LOG_DESTINATION`.
*   **Node Env:** Set `NODE_ENV=production` for production deployments.

**Applying Configuration:** Changes to `.env` or environment variables require a **restart** of the Directus instance.

## 2. File Storage & Asset Management

Directus abstracts file storage using adapters configured via environment variables. Metadata is stored in `directus_files`.

*   **Local Storage (Default):**
    *   Simple, stores files in `STORAGE_LOCAL_ROOT` (e.g., `./uploads`).
    *   Doesn't scale across multiple instances easily. Requires volume mounting/backups.
    *   `STORAGE_LOCATIONS="local"`, `STORAGE_LOCAL_DRIVER="local"`, `STORAGE_LOCAL_ROOT="./uploads"`.
*   **Cloud Storage (S3, GCS, Azure Blob, etc. - Recommended for Scalability):**
    *   Example (S3):
        ```dotenv
        STORAGE_LOCATIONS="s3"
        STORAGE_S3_DRIVER="s3"
        STORAGE_S3_KEY="YOUR_AWS_ACCESS_KEY_ID"
        STORAGE_S3_SECRET="YOUR_AWS_SECRET_ACCESS_KEY"
        STORAGE_S3_REGION="us-east-1"
        STORAGE_S3_BUCKET="your-directus-bucket-name"
        # Optional: STORAGE_S3_ENDPOINT, STORAGE_S3_ACL, STORAGE_S3_PUBLIC_URL
        ```
    *   Consult docs for specific variables for GCS, Azure, etc.
*   **Accessing Files:**
    *   Metadata via `/files` API endpoint.
    *   Serve files and transformations via `/assets/{file-id}` endpoint (respects permissions). Supports query params like `width`, `height`, `fit`, `format`, `quality`, `key` (for presets).

## 3. Deployment Considerations (Self-Hosted)

*   **Deployment Options:** Directus Cloud (PaaS), Self-Hosted Docker (Recommended), Self-Hosted Node.js.
*   **Environment Variables:** Manage production secrets securely (hosting platform's secrets management). Ensure `PUBLIC_URL`, database, storage, etc., are set correctly for the environment.
*   **Database:** Use a production-grade database (Postgres, MySQL). Configure regular backups.
*   **File Storage:** Use cloud storage (S3, GCS, Azure) for scalability and durability.
*   **Scaling:** For multiple instances, use Redis for caching (`CACHE_STORE=redis`) and potentially messaging (`MESSENGER_STORE=redis`, `WEBSOCKETS_BROKER_URL`) for consistency.
*   **Custom Extensions:**
    *   App extensions require building (`npm run build`).
    *   Deploy built extensions to the `extensions/` directory.
    *   Docker: Mount `extensions` volume to `/directus/extensions`.
    *   Node.js: Ensure `extensions` directory is present.
*   **Updates:** Plan and test Directus core updates in staging. Check release notes for breaking changes.
*   **Process Management (Node.js):** Use PM2 or similar if running directly via Node.js.
*   **HTTPS:** Always run behind a reverse proxy (Nginx, Caddy) or load balancer handling SSL/TLS.
*   **Security:** Keep Directus and OS updated, configure firewalls, review permissions, monitor logs.

Coordinate deployment activities with `devops-lead` and `infrastructure-specialist`.

*(Refer to the official Directus documentation on Environment Variables, File Storage, and Deployment.)*