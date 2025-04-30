# Django: Core Principles & Workflow

Fundamental concepts, operational guidelines, and common commands for Django development.

## 1. General Operational Principles

*   **Clarity and Precision:** Ensure all Python code, Django configurations, explanations, and instructions are clear, concise, and accurate.
*   **Best Practices:** Adhere to established best practices for Django development, including project/app structure, models (ORM), views (function-based and class-based), templates (DTL), forms, URL routing, middleware, security, and testing.
*   **Django Structure:** Follow standard Django project and app layout conventions.
*   **Security:** Prioritize security. Use Django's built-in protections (CSRF, XSS prevention), handle forms securely, manage `SECRET_KEY` appropriately, and be mindful of query escaping. (See `08-security.md`).
*   **Testing:** Write unit and integration tests using Django's testing framework (`TestCase`, test client). (See `07-testing.md`).
*   **Tool Usage Diligence:** Use tools iteratively, waiting for confirmation. Analyze context before acting. Prefer precise tools (`apply_diff`) for existing files. Use `read_file` to confirm content if unsure. Use `ask_followup_question` only when necessary. Use `execute_command` for CLI tasks (especially `manage.py`), explaining clearly. Use `attempt_completion` only when verified.
*   **Documentation:** Provide comments for complex logic.
*   **Efficiency:** Write efficient database queries and optimize view logic. (See `09-performance-caching.md`).
*   **Communication:** Report progress clearly and indicate task completion.

## 2. MVT Pattern (Model-View-Template)

Django follows a variation of the Model-View-Controller (MVC) pattern, often referred to as Model-View-Template (MVT).

*   **Model:** Represents the data structure, typically mapping to database tables. Handles data access and validation logic. (Defined in `models.py`). (See `02-models-orm.md`).
*   **View:** Handles the request/response logic. It receives an HTTP request, interacts with models, processes data, and selects a template to render, passing necessary context data to it. (Defined in `views.py`). (See `03-views-urls.md`).
*   **Template:** Defines the presentation layer (usually HTML). It receives context data from the view and uses Django Template Language (DTL) to display the data dynamically and structure the output. (Stored in `templates/` directories). (See `04-templates-dtl.md`).
*   **URL Dispatcher:** Maps incoming URL paths to specific view functions or classes. (Defined in `urls.py`). (See `03-views-urls.md`).

**Request Flow:** Request -> URL Dispatcher -> View -> Model(s) -> Template -> Response

## 3. Project vs. Apps

*   **Project:** Represents the entire web application. Contains project-wide configurations (`settings.py`, root `urls.py`). Composed of one or more apps.
*   **App:** A self-contained module handling specific functionality (e.g., blog, auth). Designed for reusability. Typically has its own `models.py`, `views.py`, `urls.py`, `forms.py`, `admin.py`, `tests.py`, and `templates/app_name/` directory. Must be listed in `INSTALLED_APPS` in `settings.py`.

## 4. Workflow / Operational Steps

1.  **Receive Task & Initialize Log:** Get assignment (Task ID `[TaskID]`) and requirements. **Guidance:** Log the initial goal to `.ruru/tasks/[TaskID].md` (or relevant task file).
    *   *Initial Log Content Example:*
        ```markdown
        # Task Log: [TaskID] - Django Feature: [Feature Name]

        **Goal:** Implement [brief goal, e.g., user profile editing view].
        ```
2.  **Plan:** Outline implementation steps (MVT components, models, URLs, forms, templates, DRF components if applicable). Consider collaboration needs.
3.  **Implement:** Write/modify Python code (`models.py`, `views.py`, `forms.py`, `urls.py`, `serializers.py`, `admin.py`, etc.). Create/update templates (`.html`). Use `execute_command` for migrations (`python manage.py makemigrations`, `python manage.py migrate`) if models change.
4.  **Collaborate:** Engage with relevant specialists (Frontend, DB, API, Infra) as needed. (See `12-collaboration-escalation.md`).
5.  **Consult Resources:** Use official Django/DRF docs and provided context files. Use `browser` tool if necessary.
    *   Django Docs: https://docs.djangoproject.com/
    *   DRF Docs: https://www.django-rest-framework.org/
6.  **Test:** Guide user on running dev server (`python manage.py runserver`) and tests (`python manage.py test`). Write tests for new/modified code. (See `07-testing.md`).
7.  **Log Completion & Final Summary:** Append status, outcome, summary, and references to the task log file. **Guidance:** Use `apply_diff` or `insert_content`.
    *   *Final Log Content Example:*
        ```markdown
        ---
        **Status:** ✅ Complete
        **Outcome:** Success
        **Summary:** Implemented DRF endpoint for user profiles, including serializer, viewset, and URL registration. Added tests.
        **References:** [`users/serializers.py` (created), `users/views.py` (modified), `project/urls.py` (modified), `users/tests.py` (modified)]
        ```
8.  **Report Back:** Inform coordinator using `attempt_completion`, referencing the task log.

## 5. `manage.py` Utility

`manage.py` is the command-line utility for administrative tasks. Run from the project root.

**Common Commands:**

*   `runserver [port or ip:port]`: Starts the development server (NOT for production).
*   `startapp <app_name>`: Creates a new app structure.
*   `makemigrations [app_name]`: Creates new migration files based on model changes.
*   `migrate [app_name] [migration_name]`: Applies migrations to the database.
*   `showmigrations`: Lists migrations and their status.
*   `sqlmigrate <app_name> <migration_name>`: Shows the SQL for a migration.
*   `test [app_path or test_path]`: Runs automated tests.
*   `shell`: Opens an interactive Python shell with the project environment loaded.
*   `createsuperuser`: Creates an admin user.
*   `changepassword [username]`: Changes a user's password.
*   `collectstatic`: Gathers static files into `STATIC_ROOT` (for production).
*   `check [--deploy]`: Checks for common problems/deployment issues.
*   `dbshell`: Opens the database client shell.
*   `flush`: Removes ALL data from the database (Use with extreme caution!).
*   `loaddata <fixture>`: Loads data from a fixture file.
*   `dumpdata [app[.Model]]`: Dumps database data to stdout (usually JSON).
*   `help [command]`: Shows help information.

Familiarity with `manage.py` is essential for development and deployment.