# Laravel: Database Migrations & Seeding

Managing database schema changes and populating initial data.

## Core Concept: Migrations

Migrations are like version control for your database schema. They allow you to define changes to your database structure (creating tables, adding columns, modifying indexes) in PHP files and apply them incrementally and reversibly.

*   **Purpose:** Keep database schema synchronized with application code across different development environments and in production. Makes collaboration easier.
*   **Location:** `database/migrations/` directory.
*   **Filename:** Timestamp prefix ensures chronological order (e.g., `2024_04_15_100000_create_posts_table.php`).
*   **Structure:** Each migration file contains a class extending `Illuminate\Database\Migrations\Migration` with two methods:
    *   `up()`: Defines the changes to apply (e.g., `Schema::create(...)`, `Schema::table(...)`).
    *   `down()`: Defines how to reverse the changes made in `up()` (e.g., `Schema::dropIfExists(...)`, `Schema::table(...)` with `dropColumn`).

## Creating Migrations

*   **Artisan Command:** `php artisan make:migration <migration_name> [--create=table_name] [--table=table_name]`
    *   `php artisan make:migration create_posts_table --create=posts`: Generates a migration with boilerplate for creating the `posts` table.
    *   `php artisan make:migration add_published_at_to_posts_table --table=posts`: Generates a migration with boilerplate for modifying the existing `posts` table.

```php
<?php
// database/migrations/YYYY_MM_DD_HHMMSS_create_posts_table.php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('posts', function (Blueprint $table) {
            $table->id(); // Auto-incrementing BigInt primary key 'id'
            $table->foreignId('user_id')->constrained()->onDelete('cascade'); // Foreign key to users table
            $table->string('title');
            $table->string('slug')->unique();
            $table->text('content');
            $table->boolean('is_published')->default(false);
            $table->timestamp('published_at')->nullable();
            $table->timestamps(); // Adds created_at and updated_at columns
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('posts');
    }
};
```

```php
<?php
// database/migrations/YYYY_MM_DD_HHMMSS_add_excerpt_to_posts_table.php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('posts', function (Blueprint $table) {
            // Add column after 'content'
            $table->text('excerpt')->nullable()->after('content');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('posts', function (Blueprint $table) {
            // Drop the column if rolling back
            $table->dropColumn('excerpt');
        });
    }
};
```

## Running Migrations

*   **`php artisan migrate`**: Applies all pending migrations (those not yet recorded in the `migrations` table).
*   **`php artisan migrate:rollback [--step=N]`**: Reverts the last batch of migrations (or N batches).
*   **`php artisan migrate:reset`**: Rolls back *all* migrations (destructive).
*   **`php artisan migrate:refresh [--seed]`**: Rolls back all migrations and then runs them all again. Useful for rebuilding the database from scratch. `--seed` runs seeders afterwards.
*   **`php artisan migrate:fresh [--seed]`**: Drops all tables and then runs all migrations. Faster than `refresh` but more destructive. `--seed` runs seeders afterwards.
*   **`php artisan migrate:status`**: Shows the status of each migration (has it run?).

## Core Concept: Seeding

Seeders are classes used to populate your database with initial or dummy data. Useful for setting up default values or providing test data for development.

*   **Location:** `database/seeders/` directory.
*   **Structure:** Seeders extend `Illuminate\Database\Seeder` and have a `run()` method.
*   **Main Seeder:** `DatabaseSeeder.php` is the main entry point, which can call other seeder classes.

## Creating Seeders

*   **Artisan Command:** `php artisan make:seeder <SeederName>` (e.g., `php artisan make:seeder UserSeeder`).

```php
<?php
// database/seeders/UserSeeder.php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;
use App\Models\User; // Import your User model

class UserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Create a specific user
        User::create([
            'name' => 'Admin User',
            'email' => 'admin@example.com',
            'password' => Hash::make('password'), // Always hash passwords
            // Add other required fields
        ]);

        // Create multiple users using a factory
        User::factory()->count(10)->create();
    }
}
```

```php
<?php
// database/seeders/DatabaseSeeder.php

namespace Database\Seeders;

// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // Call other seeders
        $this->call([
            UserSeeder::class,
            PostSeeder::class, // Assuming PostSeeder exists
            // Add other seeders here
        ]);

        // Or create directly here (less organized for larger apps)
        // \App\Models\User::factory(10)->create();
        // \App\Models\User::factory()->create([
        //     'name' => 'Test User',
        //     'email' => 'test@example.com',
        // ]);
    }
}
```

## Running Seeders

*   **`php artisan db:seed`**: Runs the `DatabaseSeeder` class (which typically calls other seeders).
*   **`php artisan db:seed --class=UserSeeder`**: Runs only a specific seeder class.
*   **`php artisan migrate:fresh --seed`**: Drops tables, runs migrations, then runs seeders.

## Model Factories

*   **Purpose:** Define blueprints for creating fake model instances, primarily for testing and seeding.
*   **Location:** `database/factories/`.
*   **Artisan Command:** `php artisan make:factory <FactoryName> --model=<ModelName>` (e.g., `php artisan make:factory PostFactory --model=Post`).
*   **Usage:** Use the `factory()` helper on the model: `User::factory()->count(5)->create();`.

Migrations and seeding are fundamental for managing your database schema and initial data throughout the development lifecycle.

*(Refer to the official Laravel documentation on Migrations and Seeding.)*