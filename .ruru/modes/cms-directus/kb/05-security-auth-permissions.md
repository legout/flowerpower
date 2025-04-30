# Directus: Security (Authentication & Permissions)

Configuring user authentication and role-based access control (RBAC) is critical for securing your Directus instance and data.

## 1. Authentication: Verifying User Identity

Authentication confirms *who* a user is. Directus supports several methods, configured primarily via environment variables (`.env`).

*   **Local Authentication:**
    *   Default method using email/password stored securely (hashed) in `directus_users`.
    *   Login via `POST /auth/login`. Returns JWT access/refresh tokens.
    *   Supports password resets and optional Two-Factor Authentication (2FA).
*   **Single Sign-On (SSO):**
    *   Delegate authentication to external providers (Google, GitHub, Okta, Azure AD, etc.) using OAuth 2.0, OpenID Connect (OIDC), LDAP, or SAML.
    *   Configure providers via `AUTH_PROVIDERS` and specific `AUTH_{PROVIDER_NAME}_*` environment variables (Client ID, Secret, Scope, Issuer URL, etc.).
    *   Requires `PUBLIC_URL` to be set correctly for redirects.
    *   Configure default role for new SSO users (`AUTH_PROVIDER_DEFAULT_ROLE_ID`).
*   **Static Tokens:**
    *   Fixed, long-lived tokens assigned to specific users (via UI or API).
    *   Useful for server-to-server communication or scripts.
    *   Pass via `Authorization: Bearer <static_token>`.
    *   Use with caution; assign to roles with minimal necessary permissions.

**API Authentication:**

*   **Bearer Tokens (JWT/Static):** Standard method for SPAs, mobile apps, server-to-server. Send token in `Authorization: Bearer <token>` header. Use refresh tokens (`/auth/refresh`) to get new access tokens.
*   **Session Cookies:** Set via `/auth/login`. Suitable for traditional web apps on the same domain. Requires CSRF protection if used cross-origin.

**Key Auth Configuration (`.env`):**

*   `SECRET`: **CRITICAL** random string for signing tokens.
*   `PUBLIC_URL`: Public-facing URL for redirects.
*   `ACCESS_TOKEN_TTL`, `REFRESH_TOKEN_TTL`: Token lifetimes.
*   `AUTH_PROVIDERS`, `AUTH_{PROVIDER_NAME}_*`: SSO provider settings.
*   `AUTH_PROVIDER_DEFAULT_ROLE_ID`: Default role for new SSO users.

## 2. Permissions: Controlling Access (RBAC)

Permissions determine *what* an authenticated user (or the public role) can do. Directus uses Role-Based Access Control (RBAC).

*   **Users** are assigned to **Roles**.
*   **Permissions** are configured for **Roles**.

**Configuration (Settings -> Roles & Permissions):**

1.  **Select Role:** Choose a role (e.g., `Public`, `Editor`, custom role).
2.  **Configure Collection Permissions:** For each collection:
    *   **CRUD:** Enable/disable Create, Read, Update, Delete.
    *   **Custom Permissions (Granular):**
        *   **Item Permissions:** Filter access based on item data (e.g., `{"author": {"_eq": "$CURRENT_USER"}}`). Uses API filter syntax and variables like `$CURRENT_USER`, `$CURRENT_ROLE`.
        *   **Field Permissions:** Whitelist fields the role can read or write.
        *   **Validation:** Role-specific validation rules.
        *   **Presets:** Auto-fill field values on creation (e.g., set `author` to `$CURRENT_USER`).
3.  **System Permissions:** Control access to `directus_*` collections (Users, Files, Settings, etc.).
4.  **Admin Access:** Toggle grants full system access, bypassing permissions. Use sparingly.
5.  **App Access:** Toggle allows role members to log into the Directus Admin App.

**Public Role:**

*   Defines access for unauthenticated API requests.
*   Crucial for public websites/apps. By default, has no access.
*   Grant specific `Read` permissions with Item Permission filters (e.g., `{"status": {"_eq": "published"}}`) and Field Permission whitelists for public data.

**Best Practices:**

*   **Least Privilege:** Grant only necessary permissions. Start restrictive.
*   **Custom Roles:** Create roles for specific user groups.
*   **Test Thoroughly:** Verify permissions via UI and API for each role.
*   **Secure Admin Role:** Strictly limit who has Administrator access.
*   **Review Regularly:** Periodically audit permissions.

Properly configuring authentication and permissions is essential for Directus security. Coordinate with `security-specialist` for complex setups.

*(Refer to the official Directus documentation on Authentication, SSO, Users, Roles & Permissions.)*