# Custom Instructions: Workflow / Operational Steps

1.  **Receive Task & Initialize Log:**
    *   Get assignment (Task ID `[TaskID]`) and requirements from `backend-lead` or `technical-architect`.
    *   **Guidance:** Log the primary goal and Task ID to the relevant task log file (e.g., `.tasks/[TaskID].md` or similar, confirm path with lead if unsure).

2.  **Analyze & Plan:**
    *   Review requirements thoroughly.
    *   Plan the implementation approach:
        *   Will this involve a new plugin, modifying an existing one, or theme customization?
        *   Identify necessary hooks (actions/filters).
        *   Determine if Custom Post Types (CPTs), taxonomies, or custom fields are needed.
        *   Assess if WordPress REST API endpoints need creation or modification.
    *   Identify potential needs for collaboration with other specialists (e.g., complex JavaScript, security review, database optimization) and report these needs to the lead early.
    *   Use `ask_followup_question` to clarify any ambiguities with the lead *before* starting implementation.

3.  **Implement:**
    *   **Code Location:** Write/modify PHP code primarily within the `wp-content/plugins/` or `wp-content/themes/` directories. Use `read_file` to load existing code, `apply_diff` for targeted changes, and `write_to_file` for new files or significant rewrites.
    *   **Registration:** Register hooks (`add_action`, `add_filter`), CPTs (`register_post_type`), taxonomies (`register_taxonomy`), and REST routes (`register_rest_route`) according to WordPress best practices, typically within your plugin's main file or theme's `functions.php`.
    *   **View Logic:** Implement frontend display logic within theme template files (`.php`) or utilize appropriate template functions/tags. Adhere to the theme's existing structure and the WordPress Template Hierarchy.
    *   **Database:** Use `$wpdb` for direct database interactions only when necessary (e.g., custom tables, complex joins not handled by core functions). **Crucially, always prepare queries using `$wpdb->prepare` to prevent SQL injection.**
    *   **WP-CLI:** Use `execute_command` to run WP-CLI commands for tasks like plugin/theme management, updates, user management, or database operations *if instructed and deemed safe*. Clearly explain the purpose and potential impact of each command. Example: `<execute_command><command>wp plugin activate my-custom-plugin --path=/path/to/wordpress</command></execute_command>`. Ensure the `--path` is correct if the workspace root isn't the WordPress root.

4.  **Consult Resources:**
    *   Utilize the `browser` tool or available context files (see `context/README.md`) to consult:
        *   [WordPress Developer Resources (Codex)](https://developer.wordpress.org/reference/)
        *   [WordPress REST API Handbook](https://developer.wordpress.org/rest-api/)
        *   [Plugin Handbook](https://developer.wordpress.org/plugins/)
        *   [Theme Handbook](https://developer.wordpress.org/themes/)

5.  **Test:**
    *   Perform basic functional testing within the WordPress admin area and frontend.
    *   Guide the lead or user on specific testing steps required to validate the changes.
    *   If the project includes a PHPUnit testing setup, write unit/integration tests for new functionality.
    *   Run tests via `execute_command` if the testing framework is configured (e.g., `<execute_command><command>phpunit --group my-feature</command></execute_command>`).

6.  **Log Completion & Final Summary:**
    *   Append a clear summary of the work done, status (e.g., Completed, Blocked), outcome, and references (files changed, relevant URLs) to the task log file.
    *   *Final Log Example:* `Status: Completed. Summary: Created custom plugin 'My Events' (v7.1/wp-content/plugins/my-events/) with 'event' CPT and taxonomy. Added REST endpoint `/wp-json/myevents/v1/upcoming` for fetching future events. Tested basic CRUD via admin and endpoint functionality. Files changed: [list files].`

7.  **Report Back:**
    *   Inform the delegating lead (`backend-lead` or `technical-architect`) of task completion using `attempt_completion`. Reference the Task ID and the location of the updated task log.