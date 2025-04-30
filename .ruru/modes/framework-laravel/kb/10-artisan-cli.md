# Laravel: Artisan Console Commands

Using Laravel's command-line interface, Artisan.

## Core Concept

Artisan is the command-line interface included with Laravel. It provides helpful commands for common tasks during application development, such as database migrations, code generation, clearing caches, running queues, and more.

*   **Execution:** Run commands from your project's root directory using `php artisan <command>`.
*   **Help:** Get a list of all commands with `php artisan list` or `php artisan`. Get help for a specific command with `php artisan help <command>` or `php artisan <command> --help`.

## Common Commands

### Code Generation (`make:*`)

*   `php artisan make:controller <Name> [--resource] [--api]`: Create a new controller class. `--resource` adds CRUD methods. `--api` adds API resource methods.
*   `php artisan make:model <Name> [-m] [-f] [-s]`: Create a new Eloquent model. `-m` creates migration. `-f` creates factory. `-s` creates seeder. `-c` creates controller. `-r` creates resource controller. `-a` creates migration, factory, seeder, and resource controller.
*   `php artisan make:migration <name> [--create=table] [--table=table]`: Create a new database migration file.
*   `php artisan make:seeder <Name>`: Create a new database seeder class.
*   `php artisan make:factory <Name> [--model=Model]`: Create a new model factory.
*   `php artisan make:policy <Name> [--model=Model]`: Create a new policy class.
*   `php artisan make:middleware <Name>`: Create a new middleware class.
*   `php artisan make:request <Name>`: Create a new form request class for validation.
*   `php artisan make:event <Name>`: Create a new event class.
*   `php artisan make:listener <Name> [--event=Event]`: Create a new event listener class.
*   `php artisan make:job <Name>`: Create a new queued job class.
*   `php artisan make:notification <Name>`: Create a new notification class.
*   `php artisan make:mail <Name> [--markdown=view.name]`: Create a new Mailable class.
*   `php artisan make:component <Name>`: Create a new Blade component class and view.
*   `php artisan make:test <Name> [--unit] [--pest]`: Create a new test class (Feature test by default). `--unit` for unit test. `--pest` for Pest test.
*   `php artisan make:command <Name>`: Create a new custom Artisan command class.

### Database (`db:*`, `migrate:*`)

*   `php artisan migrate`: Run pending database migrations.
*   `php artisan migrate:fresh [--seed]`: Drop all tables and re-run all migrations. Optionally run seeders.
*   `php artisan migrate:refresh [--seed]`: Rollback and re-run all migrations. Optionally run seeders.
*   `php artisan migrate:rollback [--step=N]`: Rollback the last batch (or N batches) of migrations.
*   `php artisan migrate:status`: Show the status of each migration.
*   `php artisan db:seed [--class=SeederName]`: Run database seeders.
*   `php artisan db:wipe [--drop-views] [--drop-types]`: Drop all tables, views, and types.

### Routing (`route:*`)

*   `php artisan route:list`: List all registered routes. Useful for debugging.
*   `php artisan route:cache`: Create a route cache file for faster registration (production).
*   `php artisan route:clear`: Remove the route cache file.

### Configuration (`config:*`)

*   `php artisan config:cache`: Create a configuration cache file (production).
*   `php artisan config:clear`: Remove the configuration cache file.

### Caching (`cache:*`)

*   `php artisan cache:clear`: Flush the application cache.
*   `php artisan cache:forget <key>`: Remove an item from the cache.

### Queues (`queue:*`)

*   `php artisan queue:work [connection] [--queue=...] [--tries=...] [--timeout=...]`: Start a worker process to handle jobs on the queue.
*   `php artisan queue:listen`: Listen to a given queue (less efficient than `work`).
*   `php artisan queue:retry [id|--all]`: Retry failed queue jobs.
*   `php artisan queue:failed`: List failed queue jobs.
*   `php artisan queue:flush`: Flush all failed queue jobs.
*   `php artisan queue:table`: Create migration for the `failed_jobs` database table.

### Scheduling (`schedule:*`)

*   `php artisan schedule:run`: Run scheduled commands that are due (needs to be run via cron every minute in production).
*   `php artisan schedule:list`: List all scheduled commands.

### Development Server

*   `php artisan serve [--host=...] [--port=...]`: Start the built-in PHP development server (for local development only).

### Maintenance Mode

*   `php artisan down [--secret=...]`: Put the application into maintenance mode.
*   `php artisan up`: Bring the application out of maintenance mode.

### Tinker

*   `php artisan tinker`: Start an interactive REPL (Read-Eval-Print Loop) with your Laravel application bootstrapped. Allows interacting with models, services, etc., directly.

Artisan is a powerful tool that significantly speeds up common development and administrative tasks in Laravel.

*(Refer to the official Laravel Artisan Console documentation: https://laravel.com/docs/artisan)*