# Custom Instructions: Error Handling

*   **WordPress Debugging:**
    *   During development, guide the user/lead to enable WordPress debugging constants in `wp-config.php` if necessary:
        *   `define( 'WP_DEBUG', true );`
        *   `define( 'WP_DEBUG_LOG', true );` (Logs errors to `wp-content/debug.log`)
        *   `define( 'WP_DEBUG_DISPLAY', false );` (Set to `false` to avoid displaying errors directly on screen, especially in production-like environments).
    *   Check the `wp-content/debug.log` file for PHP errors, warnings, and notices. Use `read_file` to access it if needed.

*   **`WP_Error` Object:**
    *   Use the `WP_Error` class for returning detailed error information from functions, especially those interacting with core APIs or performing complex operations. This allows calling code to check for errors using `is_wp_error()` and handle them gracefully.
    *   Example:
        ```php
        function my_custom_operation( $param ) {
            if ( empty( $param ) ) {
                return new WP_Error( 'param_empty', __( 'Required parameter is missing.', 'my-text-domain' ) );
            }
            // ... perform operation ...
            if ( $something_went_wrong ) {
                return new WP_Error( 'operation_failed', __( 'The operation failed.', 'my-text-domain' ), $details );
            }
            return $result;
        }
        ```

*   **PHP Exceptions:**
    *   Use standard PHP `try...catch` blocks for handling exceptions, particularly when dealing with external libraries or operations that might throw them.

*   **Tool Errors & Blockers:**
    *   If a tool fails (`apply_diff`, `write_to_file`, `execute_command`, etc.), analyze the error message provided in the response.
    *   Attempt to correct the issue (e.g., fix syntax in `apply_diff`, adjust command parameters).
    *   If the error persists or you encounter a blocker you cannot resolve (e.g., missing permissions, fundamental misunderstanding), report the issue clearly to the lead using `attempt_completion`, detailing the problem and the steps taken.