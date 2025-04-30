# Laravel: Authentication & Authorization

Handling user login, registration, and controlling access to resources.

## Core Concept: Authentication (AuthN)

Authentication is the process of verifying a user's identity. Laravel provides several ways to handle this, often facilitated by "Starter Kits".

*   **Built-in Services:** Laravel offers services for session management, password hashing (`Hash` facade), and retrieving the authenticated user (`Auth` facade, `auth()` helper).
*   **Starter Kits (Scaffolding):**
    *   **Laravel Breeze:** Simple, minimal scaffolding using Blade templates and Tailwind CSS. Provides login, registration, password reset, email verification views, routes, and controllers.
    *   **Laravel Jetstream:** More advanced scaffolding with choices for frontend stack (Livewire or Inertia.js with Vue/React) and features like team management, API support (Sanctum), two-factor authentication.
    *   **Manual Implementation:** You can build authentication entirely from scratch using Laravel's core components.
*   **Guards:** Define how users are authenticated for each request (e.g., `web` guard uses sessions, `api` guard uses tokens). Configured in `config/auth.php`.
*   **Providers:** Define how users are retrieved from storage (e.g., `eloquent` provider uses the `User` model). Configured in `config/auth.php`.

## Core Concept: Authorization (AuthZ)

Authorization is the process of determining if an authenticated user has permission to perform a specific action. Laravel provides two primary ways:

*   **Gates:** Simple, Closure-based checks for specific abilities. Often defined in `AuthServiceProvider`. Good for actions not tied to a specific model or for admin-level checks.
*   **Policies:** Classes that group authorization logic for a particular model or resource. Define methods like `viewAny`, `view`, `create`, `update`, `delete`, `restore`, `forceDelete`. More organized for complex model-based permissions.

## Authentication Implementation

### Using Starter Kits (Breeze/Jetstream)

1.  **Install:** Follow the official documentation for Breeze or Jetstream installation (`composer require laravel/breeze --dev`, `php artisan breeze:install`, etc.).
2.  **Run Migrations:** `php artisan migrate`.
3.  **Result:** The starter kit publishes routes (`routes/auth.php`), controllers (`app/Http/Controllers/Auth/`), views (`resources/views/auth/`), and sometimes request objects needed for authentication flows.

### Manual Authentication (Example)

```php
// routes/web.php
use App\Http\Controllers\AuthController;

Route::get('/login', [AuthController::class, 'showLoginForm'])->name('login');
Route::post('/login', [AuthController::class, 'login']);
Route::post('/logout', [AuthController::class, 'logout'])->name('logout');
// Add routes for registration, password reset etc.

// app/Http/Controllers/AuthController.php
<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth; // Auth Facade
use App\Models\User; // Assuming User model exists
use Illuminate\Support\Facades\Hash; // Hash Facade

class AuthController extends Controller
{
    public function showLoginForm() {
        return view('auth.login');
    }

    public function login(Request $request) {
        $credentials = $request->validate([
            'email' => ['required', 'email'],
            'password' => ['required'],
        ]);

        // Attempt to authenticate using the 'web' guard (default)
        if (Auth::attempt($credentials, $request->boolean('remember'))) {
            $request->session()->regenerate(); // Regenerate session ID for security
            return redirect()->intended('dashboard'); // Redirect to intended page or dashboard
        }

        // Authentication failed
        return back()->withErrors([
            'email' => 'The provided credentials do not match our records.',
        ])->onlyInput('email');
    }

    public function logout(Request $request) {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();
        return redirect('/');
    }
    // Add methods for registration, password reset etc.
}
```

### Accessing Authenticated User

*   **`Auth` Facade:** `Auth::user()`, `Auth::id()`, `Auth::check()`.
*   **`auth()` Helper:** `auth()->user()`, `auth()->id()`, `auth()->check()`.
*   **`Request` Object:** `$request->user()`.

## Authorization Implementation

### Gates

1.  **Define Gate:** In `app/Providers/AuthServiceProvider.php` within the `boot` method.
    ```php
    use Illuminate\Support\Facades\Gate;
    use App\Models\User;
    use App\Models\Post;

    public function boot(): void
    {
        // Define a gate named 'update-post'
        Gate::define('update-post', function (User $user, Post $post) {
            // Only allow update if the user is the author
            return $user->id === $post->user_id;
        });

        // Define an admin gate
        Gate::define('view-admin-dashboard', function (User $user) {
            return $user->is_admin; // Assuming an 'is_admin' attribute/method on User model
        });
    }
    ```
2.  **Check Gate:**
    *   In Controllers/Middleware: `Gate::allows('update-post', $post)`, `Gate::denies('update-post', $post)`, `$request->user()->can('update-post', $post)`, `$request->user()->cannot('update-post', $post)`. Use `$this->authorize('update-post', $post)` to automatically throw an `AuthorizationException` if denied.
    *   In Blade: `@can('update-post', $post) ... @endcan`, `@cannot('update-post', $post) ... @endcannot`.

### Policies

1.  **Create Policy:** `php artisan make:policy PostPolicy --model=Post`. Creates `app/Policies/PostPolicy.php`.
2.  **Register Policy:** In `app/Providers/AuthServiceProvider.php`, map the model to its policy in the `$policies` array.
    ```php
    protected $policies = [
        Post::class => PostPolicy::class,
    ];
    ```
3.  **Define Policy Methods:** Implement methods corresponding to abilities (e.g., `view`, `update`, `delete`). Methods receive the authenticated user and optionally the model instance. Return `true` or `false`.
    ```php
    <?php
    namespace App\Policies;

    use App\Models\Post;
    use App\Models\User;
    use Illuminate\Auth\Access\Response;

    class PostPolicy
    {
        /**
         * Determine whether the user can view any models.
         */
        public function viewAny(User $user): bool { return true; } // Anyone can view list

        /**
         * Determine whether the user can view the model.
         */
        public function view(User $user, Post $post): bool { return true; } // Anyone can view single

        /**
         * Determine whether the user can create models.
         */
        public function create(User $user): bool { return $user->hasVerifiedEmail(); } // Must have verified email

        /**
         * Determine whether the user can update the model.
         */
        public function update(User $user, Post $post): bool
        {
            return $user->id === $post->user_id; // Only author can update
        }

        // ... other methods like delete, restore, forceDelete ...

        // Optional: before method runs before any other check
        // public function before(User $user, string $ability): bool|null
        // {
        //     if ($user->is_admin) { return true; } // Admin bypasses other checks
        //     return null; // Continue to specific ability check
        // }
    }
    ```
4.  **Check Policy:**
    *   In Controllers/Middleware: `Gate::allows('update', $post)`, `$request->user()->can('update', $post)`. Use `$this->authorize('update', $post)` (preferred in controllers) to automatically check the policy method corresponding to the controller action name (`update` method checks `update` policy method).
    *   In Blade: `@can('update', $post) ... @endcan`.

Use Gates for simple checks and Policies for model-specific authorization logic.

*(Refer to the official Laravel documentation on Authentication and Authorization.)*