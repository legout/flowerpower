# Laravel: Request Handling & Validation

Accessing request data and validating incoming information.

## Accessing Request Data

*   **`Request` Object:** Laravel automatically injects the incoming HTTP request instance (`Illuminate\Http\Request`) into your controller methods or route closures via dependency injection or the `request()` helper function.
*   **Retrieving Input:**
    *   `$request->input('key', 'default_value')`: Retrieve a value from the request payload (works for query string, form data, JSON).
    *   `$request->query('key', 'default_value')`: Retrieve specifically from the query string.
    *   `$request->post('key', 'default_value')`: Retrieve specifically from POST form data.
    *   `$request->all()`: Get all input data as an array.
    *   `$request->only(['key1', 'key2'])`: Get a subset of input data.
    *   `$request->except(['key1', 'key2'])`: Get all input data except specified keys.
    *   `$request->boolean('key')`: Retrieve input as a boolean.
    *   `$request->integer('key')`, `$request->float('key')`, `$request->string('key')`.
*   **Retrieving Files:**
    *   `$request->file('key')`: Retrieve an uploaded file instance (`Illuminate\Http\UploadedFile`).
    *   `$request->hasFile('key')`: Check if a file was uploaded.
    *   `$file->isValid()`: Check if the file was uploaded successfully.
    *   `$file->store('path', 'disk')`: Store the uploaded file.
    *   `$file->getClientOriginalName()`, `$file->getClientMimeType()`, `$file->getSize()`.
*   **Other Request Info:**
    *   `$request->method()`: Get the HTTP method (GET, POST, etc.).
    *   `$request->path()`: Get the request path info.
    *   `$request->url()`, `$request->fullUrl()`: Get the URL.
    *   `$request->header('key', 'default')`: Get a request header.
    *   `$request->bearerToken()`: Get the bearer token from the Authorization header.
    *   `$request->ip()`: Get the client's IP address.
    *   `$request->expectsJson()`: Check if the request expects a JSON response (Accept header).
    *   `$request->isJson()`: Check if the request contains JSON data (Content-Type header).

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class ExampleController extends Controller
{
    public function process(Request $request) // Dependency Injection
    {
        $name = $request->input('name', 'Guest');
        $limit = $request->query('limit', 10);
        $isAdmin = $request->boolean('is_admin');

        if ($request->hasFile('avatar') && $request->file('avatar')->isValid()) {
            $path = $request->file('avatar')->store('avatars', 'public'); // Store in storage/app/public/avatars
            // ... save $path to user model ...
        }

        // Using the helper
        $searchTerm = request('search');

        return response()->json([
            'name' => $name,
            'limit' => $limit,
            'ip' => $request->ip(),
        ]);
    }
}
```

## Validation

Laravel provides several ways to validate incoming data. If validation fails, Laravel automatically redirects the user back to the previous location (for web requests) or returns a JSON error response (for API/AJAX requests) with validation errors.

### 1. Manual Validation (`$request->validate()`)

*   Call the `validate` method on the `Request` instance within your controller method.
*   Pass an array of validation rules.
*   If validation passes, execution continues. If it fails, an exception is thrown, leading to the automatic redirect/JSON response.

```php
public function store(Request $request)
{
    $validatedData = $request->validate([
        'title' => 'required|unique:posts|max:255', // Required, unique in 'posts' table, max 255 chars
        'body' => 'required',
        'publish_at' => 'nullable|date', // Optional, but must be a valid date if present
        'status' => 'required|in:draft,published,archived', // Must be one of these values
        'image' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:2048', // Optional, must be image, specific types, max 2MB
    ]);

    // Validation passed, $validatedData contains only the validated fields
    // ... create post using $validatedData ...

    return redirect('/posts')->with('success', 'Post created!');
}
```

### 2. Form Requests (Recommended)

*   **Purpose:** Encapsulate validation logic into a dedicated request class. Keeps controllers cleaner.
*   **Artisan Command:** `php artisan make:request StorePostRequest`
*   **Location:** `app/Http/Requests/`.
*   **Structure:**
    *   `authorize()`: Method to determine if the *authenticated user* is authorized to make this request (e.g., check permissions). Return `true` to allow, `false` to deny (results in 403 Forbidden).
    *   `rules()`: Method that returns the array of validation rules, just like in `$request->validate()`.
*   **Usage:** Type-hint the Form Request class in your controller method signature instead of the standard `Request`. Laravel automatically resolves it, runs `authorize()`, and then `rules()`. If either fails, the appropriate response is sent automatically. If successful, the validated data is available via `$request->validated()`.

```php
<?php
// app/Http/Requests/StorePostRequest.php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Support\Facades\Gate; // Example for authorization

class StorePostRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        // Example: Only allow users who can 'create posts'
        // return Gate::allows('create-posts');
        return true; // Allow anyone for now (or check auth()->check())
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array|string>
     */
    public function rules(): array
    {
        return [
            'title' => 'required|unique:posts|max:255',
            'body' => 'required',
            'publish_at' => 'nullable|date',
            'status' => 'required|in:draft,published,archived',
            'image' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:2048',
        ];
    }

    /**
     * Get custom messages for validator errors. (Optional)
     */
    public function messages(): array
    {
        return [
            'title.required' => 'A title is absolutely required!',
            'body.required' => 'Please provide some content.',
        ];
    }

     /**
     * Get custom attributes for validator errors. (Optional)
     */
    public function attributes(): array
    {
        return [
            'body' => 'post content',
        ];
    }
}
```
```php
<?php
// app/Http/Controllers/PostController.php
// ... other use statements ...
use App\Http\Requests\StorePostRequest; // Import Form Request

class PostController extends Controller
{
    // Use the Form Request via type-hinting
    public function store(StorePostRequest $request)
    {
        // Authorization and Validation automatically handled here!
        $validatedData = $request->validated(); // Get validated data

        $validatedData['user_id'] = auth()->id();
        $post = Post::create($validatedData);

        return redirect()->route('posts.show', $post)->with('success', 'Post created!');
    }
    // ... other methods ...
}
```

### Displaying Validation Errors (Blade)

*   Laravel automatically flashes validation errors to the session for web requests.
*   The `$errors` variable (an `Illuminate\Support\MessageBag` instance) is available in your Blade views.

```blade
<!-- resources/views/posts/create.blade.php -->

<form method="POST" action="{{ route('posts.store') }}">
    @csrf

    <div>
        <label for="title">Title</label>
        <input type="text" name="title" id="title" value="{{ old('title') }}" required>
        @error('title') {# Check for error for 'title' field #}
            <div class="alert alert-danger">{{ $message }}</div> {# $message contains the error string #}
        @enderror
    </div>

    <div>
        <label for="body">Content</label>
        <textarea name="body" id="body" required>{{ old('body') }}</textarea>
        @error('body')
            <div class="alert alert-danger">{{ $message }}</div>
        @enderror
    </div>

    <!-- Display all errors at the top (optional) -->
    @if ($errors->any())
        <div class="alert alert-danger">
            <ul>
                @foreach ($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        </div>
    @endif

    <button type="submit">Create Post</button>
</form>
```
*   `@error('field_name') ... @enderror`: Directive to display errors for a specific field.
*   `$errors->any()`: Check if there are any validation errors.
*   `$errors->all()`: Get all error messages as an array.
*   `old('field_name')`: Helper to repopulate form fields with previous input after validation failure.

Form Requests are the preferred way to handle validation for cleaner controllers and reusable validation logic.

*(Refer to the official Laravel documentation on HTTP Requests and Validation.)*