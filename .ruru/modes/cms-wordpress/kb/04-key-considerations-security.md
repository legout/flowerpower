# Custom Instructions: Key Considerations & Security Protocols

*   **Security First:** Security is paramount in WordPress development.
    *   **Input Validation/Sanitization:** Always validate and sanitize ALL external data (user input, API responses, URL parameters, etc.) before processing or saving. Use appropriate WordPress functions like `sanitize_text_field()`, `sanitize_email()`, `absint()`, `wp_kses_post()`, etc.
    *   **Nonces:** Use nonces (`wp_create_nonce()`, `wp_verify_nonce()`) to protect against Cross-Site Request Forgery (CSRF) attacks on forms, AJAX actions, and admin URLs.
    *   **Capability Checks:** Always check if the current user has the required permissions using `current_user_can()` before performing sensitive actions or displaying sensitive data.
    *   **Output Escaping:** Escape ALL data before outputting it to the browser to prevent Cross-Site Scripting (XSS) attacks. Use appropriate functions like `esc_html()`, `esc_attr()`, `esc_url()`, `esc_js()`.
    *   **Database Preparation:** Use `$wpdb->prepare()` for ALL database queries that include variable input, even if you think the input is safe. This is the primary defense against SQL injection.
    *   **REST API Security:** Implement robust permission callbacks (`permission_callback`) for all custom REST API endpoints using `register_rest_route`. Ensure these callbacks correctly check user authentication status and capabilities. Sanitize any parameters passed to the endpoint.

*   **Coding Standards:** Strictly follow the official [WordPress Coding Standards](https://developer.wordpress.org/coding-standards/) for PHP, HTML, CSS, and JavaScript. Consistent code style improves readability and maintainability.

*   **Hooks (Actions & Filters):** Leverage the hook system for extensibility. Prefer adding functionality via hooks over modifying core files or parent theme files directly. Understand the difference between actions (do something) and filters (modify something).

*   **Database Interaction:**
    *   Understand the core WordPress database schema ([Database Description](https://developer.wordpress.org/reference/classes/wpdb/#database-description)).
    *   Use core functions (`get_post()`, `wp_insert_post()`, `get_post_meta()`, `update_user_meta()`, etc.) whenever possible.
    *   Use `$wpdb` methods (`$wpdb->get_results`, `$wpdb->insert`, etc.) correctly when core functions are insufficient. Remember `$wpdb->prepare()`!

*   **REST API Implementation:**
    *   Use `register_rest_route()` correctly, defining namespaces, routes, methods, callbacks, and crucially, `permission_callback`.
    *   Structure your response data clearly and consistently.
    *   Consider versioning your custom endpoints (e.g., `/myplugin/v1/data`).

*   **Updates & Compatibility:**
    *   Write code that is compatible with the target WordPress and PHP versions specified for the project.
    *   Avoid deprecated functions. Check the [WordPress Developer Resources](https://developer.wordpress.org/reference/) for function status.
    *   Follow best practices for plugin/theme updates to ensure smooth transitions for users. Use activation/deactivation hooks for setup/cleanup.