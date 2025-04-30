# Laravel: Blade Templating Engine

Using Blade for creating dynamic views in Laravel.

## Core Concept

Blade is Laravel's simple, yet powerful templating engine. Unlike some other PHP templating engines, Blade does not restrict you from using plain PHP code in your views. In fact, all Blade views are compiled into plain PHP code and cached until they are modified, meaning Blade adds essentially zero overhead to your application.

*   **Location:** Blade template files use the `.blade.php` extension and are typically stored in the `resources/views` directory.
*   **Rendering:** Views are returned from routes or controllers using the `view()` helper function: `return view('view.name', ['data' => $value]);`.

## Syntax

### Displaying Data

*   **`{{ $variable }}`:** Display the contents of a variable. Data is automatically passed through PHP's `htmlspecialchars` function to prevent XSS attacks.
*   **`{!! $variable !!}`:** Display raw, unescaped data. **Use with extreme caution** and only display content you trust. Never display user-supplied content unescaped.

```blade
<!-- resources/views/greeting.blade.php -->
<h1>Hello, {{ $name }}</h1>

<p>Your raw HTML: {!! $trustedHtml !!}</p>
```

### Control Structures

Blade provides convenient directives for common PHP control structures:

*   **`@if`, `@elseif`, `@else`, `@endif`:**
    ```blade
    @if (count($records) === 1)
        I have one record!
    @elseif (count($records) > 1)
        I have multiple records!
    @else
        I don't have any records!
    @endif
    ```
*   **`@unless (condition)` ... `@endunless`:** The inverse of `@if`.
*   **`@isset($variable)` ... `@endisset`:** Checks if a variable is set and not null.
*   **`@empty($variable)` ... `@endempty`:** Checks if a variable is "empty" (null, empty string, empty array, 0, etc.).
*   **`@auth`, `@guest`, `@endauth`, `@endguest`:** Check authentication status.
    ```blade
    @auth
        // The user is authenticated...
    @endauth

    @guest
        // The user is not authenticated...
    @endguest
    ```
*   **`@switch`, `@case`, `@default`, `@endswitch`:**
    ```blade
    @switch($type)
        @case(1)
            First case...
            @break
        @case(2)
            Second case...
            @break
        @default
            Default case...
    @endswitch
    ```
*   **Loops:**
    *   **`@for ($i = 0; $i < 10; $i++)` ... `@endfor`**
    *   **`@foreach ($users as $user)` ... `@endforeach`**
    *   **`@forelse ($users as $user)` ... `@empty` ... `@endforelse`:** Like `@foreach`, but includes an `@empty` block if the collection is empty.
    *   **`@while (condition)` ... `@endwhile`**
*   **Loop Variable (`$loop`):** Available inside `@foreach` and `@forelse` loops.
    *   `$loop->index`: Current iteration index (1-based).
    *   `$loop->iteration`: Same as `index`.
    *   `$loop->remaining`: Iterations remaining.
    *   `$loop->count`: Total items in the array.
    *   `$loop->first`: Boolean, true on first iteration.
    *   `$loop->last`: Boolean, true on last iteration.
    *   `$loop->even`: Boolean, true on even iterations.
    *   `$loop->odd`: Boolean, true on odd iterations.
    *   `$loop->depth`: Nesting level of the loop.
    *   `$loop->parent`: Access the parent loop's `$loop` variable in nested loops.

### Template Inheritance

*   **`@extends('layouts.app')`:** Specifies that this view extends a parent layout (e.g., `resources/views/layouts/app.blade.php`).
*   **`@section('sectionName')` ... `@endsection`:** Defines a section of content.
*   **`@yield('sectionName')`:** Used in the parent layout to display the content of a section defined in a child view.
*   **`@parent`:** Within a section, appends content to the parent layout's section of the same name.

```blade
<!-- resources/views/layouts/app.blade.php -->
<html>
<head><title>@yield('title', 'Default Title')</title></head>
<body>
    @section('sidebar')
        This is the master sidebar.
    @show {# Use @show as shorthand for @yield + @endsection #}

    <div class="container">
        @yield('content')
    </div>
</body>
</html>
```
```blade
<!-- resources/views/child.blade.php -->
@extends('layouts.app')

@section('title', 'Page Title')

@section('sidebar')
    @parent {# Append to parent sidebar #}
    <p>This is appended to the master sidebar.</p>
@endsection

@section('content')
    <p>This is my body content.</p>
@endsection
```

### Including Subviews

*   **`@include('view.name', ['data' => $value])`:** Includes another Blade view. Variables from the parent view are available unless explicitly passed data.

### Components

*   Reusable Blade snippets defined as classes or anonymous components.
*   **Class-Based:** `php artisan make:component Alert` creates `app/View/Components/Alert.php` and `resources/views/components/alert.blade.php`. Use `<x-alert type="error" :message="$message"/>`.
*   **Anonymous:** Create a file like `resources/views/components/button.blade.php`. Use `<x-button class="primary">Click Me</x-button>`. Props are available as variables (`$class`, `$slot`).
*   **Slots:** Pass content into components using `<x-slot name="title">...</x-slot>` or the main `$slot` variable.

### Other Directives

*   **`@csrf`:** Generates a hidden input field containing the CSRF token (essential for POST/PUT/PATCH/DELETE forms).
*   **`@method('PUT')` / `@method('DELETE')` / `@method('PATCH')`:** Generates a hidden input field to spoof HTTP verbs for forms (since HTML forms only support GET/POST).
*   **`@php` ... `@endphp`:** Execute plain PHP code (use sparingly, prefer logic in controllers/services).
*   **`@json($variable)`:** Safely output a variable as JSON for JavaScript.
*   **`@vite(['resource/css/app.css', 'resource/js/app.js'])`:** Directive for including assets compiled by Vite (common in newer Laravel).

Blade provides a clean and efficient way to build dynamic views in Laravel.

*(Refer to the official Laravel Blade Templates documentation: https://laravel.com/docs/blade)*