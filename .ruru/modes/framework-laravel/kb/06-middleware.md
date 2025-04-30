# Laravel: Middleware

Intercepting and filtering HTTP requests entering your application.

## Core Concept

Middleware provide a convenient mechanism for filtering HTTP requests entering your application. For example, Laravel includes middleware that verifies the user is authenticated. If the user is not authenticated, the middleware redirects the user to the login screen. However, if the user is authenticated, the middleware allows the request to proceed further into the application.

*   **Purpose:** Perform actions *before* or *after* a request reaches its intended route/controller action. Common uses include authentication, authorization, logging, CORS handling, modifying requests/responses, maintenance mode checks.
*   **HTTP Kernel:** Middleware are processed sequentially by the HTTP Kernel (`app/Http/Kernel.php`).
*   **Structure:** Middleware are typically classes with a `handle` method.

## Creating Middleware

*   **Artisan Command:** `php artisan make:middleware <MiddlewareName>` (e.g., `php artisan make:middleware CheckUserRole`).
*   **Location:** Generated middleware are placed in the `app/Http/Middleware` directory.
*   **`handle` Method:**
    *   Receives the incoming `Illuminate\Http\Request` object (`$request`) and a `Closure` (`$next`).
    *   The `$next($request)` call passes the request deeper into the application (to the next middleware or the controller).
    *   Code *before* `$next($request)` executes before the request reaches the controller.
    *   Code *after* `$response = $next($request)` executes after the controller has generated a response.

```php
<?php
// app/Http/Middleware/LogRequests.php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log; // Import Log facade
use Symfony\Component\HttpFoundation\Response;

class LogRequests
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        // Action BEFORE the request reaches the controller
        Log::info('Incoming Request:', [
            'method' => $request->method(),
            'url' => $request->fullUrl(),
            'ip' => $request->ip(),
        ]);

        // Pass the request to the next middleware/controller
        $response = $next($request);

        // Action AFTER the controller returns a response
        Log::info('Outgoing Response:', ['status' => $response->getStatusCode()]);

        // Optionally modify the response
        // $response->headers->set('X-Custom-Header', 'Value');

        return $response;
    }
}
```

## Registering Middleware

Middleware must be registered in `app/Http/Kernel.php` before they can be used.

1.  **Global Middleware (`$middleware`):** Run on *every* HTTP request to your application.
    ```php
    // app/Http/Kernel.php
    protected $middleware = [
        // ... other global middleware (TrustProxies, PreventRequestsDuringMaintenance, etc.)
        \App\Http\Middleware\LogRequests::class, // Add your global middleware
    ];
    ```
2.  **Route Middleware Groups (`$middlewareGroups`):** Group middleware under a key (e.g., `web`, `api`). These groups are typically applied automatically to routes in `routes/web.php` and `routes/api.php` by the `RouteServiceProvider`.
    ```php
    // app/Http/Kernel.php
    protected $middlewareGroups = [
        'web' => [
            \App\Http\Middleware\EncryptCookies::class,
            \Illuminate\Cookie\Middleware\AddQueuedCookiesToResponse::class,
            \Illuminate\Session\Middleware\StartSession::class,
            // \Illuminate\Session\Middleware\AuthenticateSession::class, // Optional session auth
            \Illuminate\View\Middleware\ShareErrorsFromSession::class,
            \App\Http\Middleware\VerifyCsrfToken::class, // CSRF Protection
            \Illuminate\Routing\Middleware\SubstituteBindings::class, // For Route Model Binding
            // Add custom middleware specific to the 'web' group
        ],
        'api' => [
            // \Laravel\Sanctum\Http\Middleware\EnsureFrontendRequestsAreStateful::class, // If using Sanctum SPA auth
            'throttle:api', // API Rate Limiting
            \Illuminate\Routing\Middleware\SubstituteBindings::class,
        ],
    ];
    ```
3.  **Route Middleware Aliases (`$middlewareAliases` or `$routeMiddleware` in older versions):** Assign a short alias to a middleware class. This allows applying middleware individually to specific routes or route groups using the alias.
    ```php
    // app/Http/Kernel.php
    protected $middlewareAliases = [
        'auth' => \App\Http\Middleware\Authenticate::class,
        'auth.basic' => \Illuminate\Auth\Middleware\AuthenticateWithBasicAuth::class,
        'cache.headers' => \Illuminate\Http\Middleware\SetCacheHeaders::class,
        'can' => \Illuminate\Auth\Middleware\Authorize::class,
        'guest' => \App\Http\Middleware\RedirectIfAuthenticated::class,
        'throttle' => \Illuminate\Routing\Middleware\ThrottleRequests::class,
        'signed' => \Illuminate\Routing\Middleware\ValidateSignature::class,
        'verified' => \Illuminate\Auth\Middleware\EnsureEmailIsVerified::class,
        // Add your custom aliases
        'role' => \App\Http\Middleware\CheckUserRole::class,
    ];
    ```

## Applying Middleware to Routes

*   **Individual Routes:** Use the `middleware()` method after defining the route.
    ```php
    Route::get('/profile', [ProfileController::class, 'show'])->middleware('auth');
    Route::post('/admin/posts', [AdminPostController::class, 'store'])->middleware(['auth', 'role:editor']); // Multiple middleware
    ```
*   **Route Groups:** Apply middleware to all routes within a group.
    ```php
    Route::middleware(['auth'])->group(function () {
        Route::get('/dashboard', ...);
        Route::get('/settings', ...);
    });
    ```
*   **Controllers:** Apply middleware within the controller's constructor (affects all methods or specific ones using `only`/`except`).
    ```php
    // app/Http/Controllers/AdminController.php
    public function __construct()
    {
        $this->middleware('auth');
        $this->middleware('role:admin')->only(['users', 'settings']);
        $this->middleware('log')->except(['publicAction']);
    }
    ```

## Middleware Parameters

*   Middleware can receive additional parameters specified after the alias in the route definition.
*   These parameters are passed to the `handle` method *after* the `$next` closure.

```php
// Route definition
Route::put('/post/{id}', function ($id) {
    // ...
})->middleware('role:editor'); // 'editor' is passed as $role

// Middleware handle method
public function handle(Request $request, Closure $next, string $role): Response
{
    if (! $request->user()->hasRole($role)) { // Check if user has the required role
        abort(403, 'Unauthorized action.');
    }
    return $next($request);
}
```

Middleware are a powerful tool for processing requests and enforcing cross-cutting concerns in Laravel.

*(Refer to the official Laravel Middleware documentation: https://laravel.com/docs/middleware)*