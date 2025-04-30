# Laravel: Routing & Controllers

Defining URL endpoints and connecting them to controller logic.

## Core Concept: Routing

*   **Purpose:** Maps incoming HTTP requests (URL path + HTTP method) to the code that should handle them (usually a Controller method or a Closure).
*   **Location:** Route definitions are typically stored in files within the `routes/` directory:
    *   `routes/web.php`: For web interface routes (usually apply session state, CSRF protection via `web` middleware group).
    *   `routes/api.php`: For stateless API routes (usually apply throttling via `api` middleware group).
    *   `routes/console.php`: For Artisan console commands.
    *   `routes/channels.php`: For broadcasting channels.
*   **Facade:** Routes are defined using the `Route` facade (`Illuminate\Support\Facades\Route`).

## Defining Routes

*   **Basic Routing:** Use methods corresponding to HTTP verbs (`get`, `post`, `put`, `patch`, `delete`, `options`).
    ```php
    use Illuminate\Support\Facades\Route;
    use App\Http\Controllers\PostController;

    // routes/web.php
    Route::get('/', function () {
        return view('welcome'); // Closure route
    });

    Route::get('/posts', [PostController::class, 'index'])->name('posts.index'); // Controller action
    Route::get('/posts/create', [PostController::class, 'create'])->name('posts.create');
    Route::post('/posts', [PostController::class, 'store'])->name('posts.store');
    Route::get('/posts/{post}', [PostController::class, 'show'])->name('posts.show'); // Route Model Binding
    Route::get('/posts/{post}/edit', [PostController::class, 'edit'])->name('posts.edit');
    Route::put('/posts/{post}', [PostController::class, 'update'])->name('posts.update'); // Or Route::patch
    Route::delete('/posts/{post}', [PostController::class, 'destroy'])->name('posts.destroy');

    // Match multiple verbs
    Route::match(['get', 'post'], '/contact', [ContactController::class, 'handle']);

    // Any verb
    Route::any('/legacy', [LegacyController::class, 'handle']);
    ```
*   **Route Parameters:** Capture segments of the URI.
    *   Required: `{param}` (e.g., `/users/{id}`)
    *   Optional: `{param?}` (e.g., `/search/{query?}`). Requires a default value in the controller method signature.
    *   Constraints: Use `->where('param', '[regex]')` or global patterns in `RouteServiceProvider`.
        ```php
        Route::get('/users/{id}', [UserController::class, 'show'])->where('id', '[0-9]+');
        Route::get('/users/{name}', [UserController::class, 'showByName'])->whereAlpha('name');
        Route::get('/category/{slug}', [CategoryController::class, 'show'])->whereAlphaNumeric('slug');
        ```
*   **Named Routes:** Assign names using `->name('routeName')`. Useful for generating URLs (`route()` helper) and redirects. Convention: `resource.action` (e.g., `posts.show`).
*   **Route Groups:** Apply attributes (middleware, prefix, namespace, name prefix) to multiple routes.
    ```php
    // Apply middleware
    Route::middleware(['auth', 'admin'])->group(function () {
        Route::get('/admin/dashboard', [AdminController::class, 'dashboard']);
        // ... other admin routes
    });

    // Apply prefix and name prefix
    Route::prefix('admin')->name('admin.')->group(function () {
        Route::get('/users', [AdminUserController::class, 'index'])->name('users.index'); // Full name: admin.users.index
    });
    ```
*   **Resource Controllers:** Quickly define standard CRUD routes for a controller.
    ```php
    Route::resource('photos', PhotoController::class);
    // Creates routes for index, create, store, show, edit, update, destroy
    // Use ->only([...]) or ->except([...]) to limit generated routes
    // Use Route::apiResource for API routes (omits create/edit views)
    ```
*   **Route Model Binding:** Automatically inject model instances into your controller methods based on route parameters.
    *   Implicit Binding: Type-hint the parameter with the Model class. The variable name must match the route segment (e.g., `{post}` matches `Post $post`). Laravel automatically fetches the model by primary key.
    *   Explicit Binding: Define custom resolution logic in `RouteServiceProvider`.
    *   Custom Key: `Route::get('/posts/{post:slug}', ...)` binds using the `slug` column instead of `id`.

## Controllers (`app/Http/Controllers/`)

*   **Purpose:** Group related request handling logic into a single class.
*   **Artisan Command:** `php artisan make:controller ControllerName [--resource] [--api]` (`--resource` adds CRUD methods, `--api` adds API CRUD methods).
*   **Structure:** Methods receive dependencies via type-hinting (Dependency Injection) and often receive the `Request` object and route parameters.
*   **Actions:** Each public method typically corresponds to a route action (e.g., `index`, `show`, `store`, `update`, `destroy`).

```php
<?php

namespace App\Http\Controllers;

use App\Models\Post;
use Illuminate\Http\Request; // Import Request facade or type-hint
use App\Http\Requests\StorePostRequest; // Example Form Request for validation

class PostController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $posts = Post::latest()->paginate(15);
        return view('posts.index', compact('posts')); // Pass data to Blade view
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        return view('posts.create');
    }

    /**
     * Store a newly created resource in storage.
     * Use Form Request for validation
     */
    public function store(StorePostRequest $request) // Type-hint Form Request
    {
        // Validation passed automatically if using Form Request
        $validatedData = $request->validated();

        // Add user_id before creating
        $validatedData['user_id'] = auth()->id();

        $post = Post::create($validatedData);

        return redirect()->route('posts.show', $post)->with('success', 'Post created successfully!'); // Redirect with flash message
    }

    /**
     * Display the specified resource.
     * Implicit Route Model Binding
     */
    public function show(Post $post) // Type-hint Post model, variable name matches route segment {post}
    {
        // $post is automatically fetched or 404s
        return view('posts.show', compact('post'));
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(Post $post)
    {
        // Add authorization check (e.g., using Gates or Policies)
        // $this->authorize('update', $post);
        return view('posts.edit', compact('post'));
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(StorePostRequest $request, Post $post) // Use Form Request again
    {
        // $this->authorize('update', $post);
        $validatedData = $request->validated();
        $post->update($validatedData);

        return redirect()->route('posts.show', $post)->with('success', 'Post updated successfully!');
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Post $post)
    {
        // $this->authorize('delete', $post);
        $post->delete();
        return redirect()->route('posts.index')->with('success', 'Post deleted successfully!');
    }
}
```

Routing and Controllers form the backbone of handling requests in a Laravel application.

*(Refer to the official Laravel documentation on Routing and Controllers.)*