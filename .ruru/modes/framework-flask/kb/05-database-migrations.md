# Flask: Database Migrations (Flask-Migrate / Alembic)

Managing database schema changes using Flask-Migrate, which integrates Alembic.

## Core Concept

As your application evolves, your database models (`models.py`) will change. You need a way to apply these changes to your actual database schema without losing data. **Flask-Migrate** is a Flask extension that handles SQLAlchemy database migrations using **Alembic**, a powerful database migration tool for SQLAlchemy.

## Setup

1.  **Install:**
    ```bash
    pip install Flask-Migrate # Also installs Alembic
    # Ensure Flask-SQLAlchemy is also installed
    pip install Flask-SQLAlchemy
    ```
2.  **Initialize Extension (App Factory Recommended):**
    ```python
    # extensions.py
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate

    db = SQLAlchemy()
    migrate = Migrate()

    # In your app factory (create_app function)
    from .extensions import db, migrate
    def create_app(config_class=Config):
        app = Flask(__name__)
        app.config.from_object(config_class)

        db.init_app(app)
        migrate.init_app(app, db) # Initialize Flask-Migrate AFTER SQLAlchemy

        # ... register blueprints, other extensions ...
        return app
    ```
    If not using an app factory, initialize directly: `db = SQLAlchemy(app)`, `migrate = Migrate(app, db)`.
3.  **Import Models:** Ensure your SQLAlchemy models (defined using `db.Model`) are imported somewhere Flask-Migrate can see them, often by importing them in your main application package's `__init__.py` or a dedicated `models.py` that's imported.

## Workflow & CLI Commands

Flask-Migrate adds commands to the `flask` CLI (or uses its own `flask db` subcommand).

1.  **Initialize Migration Repository (Run Once):**
    *   Creates a `migrations/` directory to store migration scripts.
    *   **Command:** `flask db init`
2.  **Generate Migration Script:**
    *   Compares your current models (`models.py`) against the schema recorded in the database (tracked by Alembic).
    *   Generates a new migration script in `migrations/versions/` containing the necessary Alembic operations (`op.create_table`, `op.add_column`, `op.drop_column`, etc.) to bridge the difference.
    *   **Command:** `flask db migrate -m "Short description of changes"` (The `-m` message is optional but highly recommended).
    *   **Review:** Always review the generated migration script before applying it, especially for complex changes like column renames or type changes, as automatic detection might not be perfect. You may need to edit the script manually.
3.  **Apply Migrations:**
    *   Applies any pending migration scripts to the database, updating the schema.
    *   **Command:** `flask db upgrade`
4.  **Downgrade Migrations (Use with Caution):**
    *   Reverts the last applied migration (or multiple steps).
    *   **Command:** `flask db downgrade` (Reverts one step)
    *   **Command:** `flask db downgrade -N` (Reverts N steps)
    *   **Command:** `flask db downgrade base` (Reverts all migrations)
5.  **Other Useful Commands:**
    *   `flask db current`: Show the current migration revision applied to the database.
    *   `flask db history`: List migration scripts and their status.
    *   `flask db show <revision>`: Show details about a specific migration revision.
    *   `flask db stamp <revision>`: Manually set the database's current revision without running migrations (useful for syncing environments).

## Example Workflow

```bash
# 1. After changing models.py...
# Activate virtual environment: source venv/bin/activate
# Set FLASK_APP environment variable: export FLASK_APP=your_app_entrypoint.py

# 2. Generate the migration script
flask db migrate -m "Add user bio field"
# Output: INFO  [alembic.runtime.migration] Generating /path/to/your_project/migrations/versions/xxxx_add_user_bio_field.py ... done

# 3. Review the generated script (migrations/versions/xxxx_add_user_bio_field.py) - IMPORTANT!

# 4. Apply the migration to the database
flask db upgrade
# Output: INFO  [alembic.runtime.migration] Running upgrade yyyy -> xxxx, Add user bio field

# Check current revision
flask db current
# Output: INFO  [alembic.runtime.migration] Current revision for 'default': xxxx (head), Add user bio field
```

## Best Practices

*   **Version Control:** Always commit your `migrations/` directory (including `env.py`, `script.py.mako`, and the `versions/` subdirectory) to version control along with your model changes.
*   **Review Migrations:** Carefully review auto-generated scripts, especially for potentially destructive changes (dropping tables/columns) or complex alterations (renames, type changes). Alembic might require manual adjustments using `op.batch_alter_table()` for SQLite or specific directives for other databases.
*   **Linear History:** Avoid branching migration histories in team environments if possible. Ensure developers pull latest changes and run `flask db upgrade` before generating new migrations.
*   **Never Edit Old Migrations:** Once a migration is applied (especially in shared environments like staging/production), do not edit it. Create a *new* migration to make further changes or corrections.
*   **Test Migrations:** Test migrations in a development or staging environment before applying them to production. Test both `upgrade` and `downgrade` paths if possible.
*   **Backups:** Always back up your production database before applying migrations.

Flask-Migrate and Alembic provide a robust system for managing database schema evolution alongside your Flask application code.

*(Refer to the official Flask-Migrate documentation.)*