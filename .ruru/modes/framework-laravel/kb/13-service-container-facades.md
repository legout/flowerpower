# Laravel: Service Container & Facades

Understanding Laravel's core mechanisms for managing dependencies and accessing services.

## Core Concept: Service Container (IoC Container)

*   **Purpose:** A powerful tool for managing class dependencies and performing dependency injection (IoC - Inversion of Control). Instead of manually creating objects with their dependencies inside your classes, you "bind" how to create an object into the container, and then "resolve" the object out of the container when needed. Laravel automatically resolves many dependencies via type-hinting in constructors and controller methods.
*   **Binding:** Telling the container *how* to create an instance of a class or interface.
    *   **Simple Binding:** `app()->bind('service-key', ConcreteClass::class);` or `app()->bind(Interface::class, ConcreteClass::class);`
    *   **Singleton Binding:** `app()->singleton(Service::class, function ($app) { return new Service($app->make('OtherDependency')); });` Ensures only one instance is created and shared.
    *   **Instance Binding:** `app()->instance('api-key', 'ABC-123');` Binds an existing instance.
    *   **Interface to Implementation:** `app()->bind(PaymentGateway::class, StripeGateway::class);` Allows swapping implementations easily.
*   **Resolving:** Getting an instance out of the container.
    *   **Automatic Resolution (Dependency Injection):** Laravel automatically resolves dependencies type-hinted in constructors, controller methods, Job `handle` methods, Event listeners, etc. This is the **preferred** way.
        ```php
        public function __construct(private PaymentGateway $gateway) {} // Automatically resolved

        public function store(Request $request, StripeGateway $stripe) {} // Automatically resolved
        ```
    *   **Manual Resolution:**
        *   `app('service-key')` or `app(ClassName::class)`
        *   `resolve('service-key')` or `resolve(ClassName::class)` (Global helper)
        *   `$this->app->make('service-key')` (Within service providers)
*   **Location:** Bindings are typically registered within the `register` method of Service Providers (`app/Providers/`).

## Core Concept: Facades

*   **Purpose:** Provide a static-like, convenient syntax for accessing services resolved from the service container. They act as "static proxies" to underlying objects.
*   **Example:** Instead of injecting and using a `Mailer` instance, you can use `Mail::send(...)`. Behind the scenes, Laravel resolves the actual mailer instance from the container via the `Mail` facade.
*   **How it Works:** Each facade defines a `getFacadeAccessor()` method that returns the container binding key (string or class name) for the underlying service. When you call a static method on the facade (e.g., `Cache::get('key')`), Laravel resolves the service using the accessor and calls the corresponding instance method on the resolved object.
*   **Built-in Facades:** Laravel provides facades for most of its core services (`Route`, `View`, `Cache`, `Log`, `Auth`, `DB`, `Schema`, `Mail`, `Queue`, `Storage`, `Hash`, `Session`, `Request`, `URL`, etc.). See `config/app.php` for aliases.
*   **Real-Time Facades:** Prefix your imported class with `Facades\` to use any class as if it were a facade (useful for your own classes without creating a dedicated Facade class): `use Facades\App\Services\MyCustomService; ... MyCustomService::doSomething();`

## Service Providers (`app/Providers/`)

*   **Purpose:** The central place to bootstrap your application. Used to register service container bindings, event listeners, middleware, route model bindings, validation rules, console commands, and more.
*   **`register()` Method:** Used **only** for binding things into the service container. Do not attempt to resolve services within this method.
*   **`boot()` Method:** Called after all service providers have been registered. Used for logic that needs access to already registered services (e.g., defining Gates, registering view composers, route model bindings). Dependencies type-hinted in the `boot` method will be resolved by the container.
*   **Registration:** Service providers are registered in the `providers` array in `config/app.php`.

```php
<?php
// app/Providers/PaymentServiceProvider.php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use App\Services\PaymentGateways\StripeGateway;
use App\Services\PaymentGateways\PayPalGateway;
use App\Contracts\PaymentGateway; // Assuming an interface exists

class PaymentServiceProvider extends ServiceProvider
{
    /**
     * Register services.
     */
    public function register(): void
    {
        // Bind the PaymentGateway interface to a concrete implementation
        $this->app->singleton(PaymentGateway::class, function ($app) {
            // Choose implementation based on config or other logic
            if (config('services.payment.default') === 'stripe') {
                return new StripeGateway(config('services.stripe.secret'));
            } else {
                return new PayPalGateway(config('services.paypal.client_id'), config('services.paypal.secret'));
            }
        });

        // Simple binding for another service
        // $this->app->bind(AnotherService::class, function ($app) {
        //     return new AnotherService();
        // });
    }

    /**
     * Bootstrap services.
     */
    public function boot(): void
    {
        // Example: Registering a view composer that needs a resolved service
        // View::composer('profile', function ($view) use ($app) {
        //    $stats = $app->make(UserStatsService::class)->getStats(auth()->id());
        //    $view->with('userStats', $stats);
        // });
    }
}
```

## When to Use What

*   **Dependency Injection (Type-hinting):** **Preferred method** for resolving dependencies in constructors and controller/job/listener methods. It's explicit and better for testability (easy mocking).
*   **Facades:** Convenient for quick access within controllers, views, or closures where injection might be cumbersome. Can be slightly harder to mock in tests than direct injection, though Laravel provides facade mocking helpers (`Mail::fake()`).
*   **`app()` / `resolve()` Helpers:** Useful within service providers, configuration files, or places where dependency injection isn't readily available. Use sparingly in application code; prefer injection.

Understanding the Service Container is fundamental to leveraging Laravel's power for dependency management and building testable applications. Facades offer a convenient syntax on top of the container.

*(Refer to the official Laravel documentation on Service Container, Service Providers, and Facades.)*