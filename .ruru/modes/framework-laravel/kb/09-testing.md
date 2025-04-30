# Laravel: Testing with PHPUnit & Pest

Writing automated tests for Laravel applications.

## Core Concept

Laravel provides excellent testing support out-of-the-box, built on top of **PHPUnit**. **Pest** is an alternative testing framework built on PHPUnit that offers a more expressive, function-based syntax. Laravel supports both seamlessly.

*   **Purpose:** Verify application logic, prevent regressions, and ensure code quality.
*   **Types of Tests:**
    *   **Unit Tests:** Test small, isolated pieces of code (like a single method in a class) in isolation, often mocking dependencies. Located in `tests/Unit`.
    *   **Feature Tests:** Test a larger portion of functionality, often involving making HTTP requests to your application and asserting responses or database state. Located in `tests/Feature`. These simulate how a user might interact with the application.
*   **Configuration:** `phpunit.xml` in the project root configures PHPUnit (test suites, environment variables, etc.).
*   **Environment:** Tests typically run using the configuration defined in `phpunit.xml` (often setting `APP_ENV=testing` and using a separate testing database like SQLite in-memory).

## Setup

*   PHPUnit is included as a development dependency in Laravel projects.
*   Pest can be installed via Composer: `composer require pestphp/pest --dev --with-all-dependencies` and then `php artisan pest:install`.

## Creating Tests

*   **Artisan Command:**
    *   `php artisan make:test <TestName> [--unit]`: Creates a PHPUnit test class in `tests/Feature` or `tests/Unit`.
    *   `php artisan make:test <TestName> --pest [--unit]`: Creates a Pest test file.

## Writing Tests (PHPUnit)

*   Test classes extend `Tests\TestCase` (which sets up the Laravel application for testing).
*   Test methods start with the prefix `test_` or use the `#[Test]` attribute (PHP 8).
*   Use various assertion methods provided by PHPUnit (e.g., `assertEquals`, `assertTrue`, `assertCount`, `assertInstanceOf`).
*   Laravel provides additional testing helpers and assertions.

```php
<?php
// tests/Unit/ExampleUnitTest.php

namespace Tests\Unit;

// use PHPUnit\Framework\TestCase; // Use this for pure PHP unit tests without Laravel app
use Tests\TestCase; // Use this for tests needing Laravel features

class ExampleUnitTest extends TestCase
{
    /**
     * A basic unit test example.
     */
    public function test_basic_assertion(): void
    {
        $this->assertTrue(true);
        $this->assertEquals(5, 2 + 3);
    }

    // Add tests for specific class methods, mocking dependencies if needed
}
```

```php
<?php
// tests/Feature/HomepageTest.php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase; // Trait to reset DB for each test
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;
use App\Models\User; // Import models if needed

class HomepageTest extends TestCase
{
    use RefreshDatabase; // Reset the database before each test in this class

    /**
     * Test the homepage loads correctly for guests.
     */
    public function test_homepage_loads_for_guests(): void
    {
        $response = $this->get('/'); // Simulate GET request

        $response->assertStatus(200); // Assert HTTP status code
        $response->assertSee('Welcome'); // Assert response body contains text
        $response->assertDontSee('Dashboard'); // Assert response body does NOT contain text
    }

    /**
     * Test the homepage loads correctly for authenticated users.
     */
    public function test_homepage_loads_for_authenticated_users(): void
    {
        $user = User::factory()->create(); // Create a user using a factory

        $response = $this->actingAs($user) // Simulate request as this authenticated user
                         ->get('/');

        $response->assertStatus(200);
        $response->assertSee("Welcome, {$user->name}"); // Check for personalized greeting
    }

    /**
     * Test posting data to a route.
     */
    public function test_can_create_post(): void
    {
        $user = User::factory()->create();
        $postData = [
            'title' => 'My Test Post',
            'content' => 'This is the content.',
            // Add other required fields based on validation/model
        ];

        $response = $this->actingAs($user)
                         ->post(route('posts.store'), $postData); // Use route() helper

        $response->assertStatus(302); // Expect a redirect after successful creation
        $response->assertRedirect(route('posts.index')); // Check redirect location (adjust as needed)
        $response->assertSessionHas('success'); // Check for flash message

        // Assert the data was actually saved in the database
        $this->assertDatabaseHas('posts', [
            'title' => 'My Test Post',
            'user_id' => $user->id,
        ]);
    }
}
```

## Writing Tests (Pest)

*   Uses functions (`test()`, `it()`) instead of classes/methods.
*   Syntax is often more fluent and readable.
*   Uses the same underlying PHPUnit assertions and Laravel helpers.

```php
<?php
// tests/Feature/HomepagePestTest.php

use App\Models\User;
use function Pest\Laravel\{get, post, actingAs}; // Import Pest helpers

uses(Tests\TestCase::class, Illuminate\Foundation\Testing\RefreshDatabase::class); // Apply traits globally or per file

test('homepage loads for guests', function () {
    get('/') // Simulate GET request
        ->assertStatus(200)
        ->assertSee('Welcome')
        ->assertDontSee('Dashboard');
});

test('homepage loads for authenticated users', function () {
    $user = User::factory()->create();

    actingAs($user) // Simulate acting as user
        ->get('/')
        ->assertStatus(200)
        ->assertSee("Welcome, {$user->name}");
});

test('can create post', function () {
    $user = User::factory()->create();
    $postData = [
        'title' => 'My Pest Post',
        'content' => 'This is the content.',
    ];

    actingAs($user)
        ->post(route('posts.store'), $postData)
        ->assertStatus(302)
        ->assertRedirect(route('posts.index')) // Adjust as needed
        ->assertSessionHas('success');

    $this->assertDatabaseHas('posts', [ // Use standard assertions for DB checks
        'title' => 'My Pest Post',
        'user_id' => $user->id,
    ]);
});
```

## Running Tests

*   **`php artisan test`**: Runs all tests (PHPUnit or Pest).
*   **`./vendor/bin/phpunit`**: Runs PHPUnit tests directly.
*   **`./vendor/bin/pest`**: Runs Pest tests directly.
*   **Filtering:** Both support filtering by file, directory, method name, or group (`--filter=...`, `--group=...`).
*   **Coverage:** Generate code coverage reports (`php artisan test --coverage` or add flags to phpunit/pest). Requires Xdebug or PCOV.

## Common Laravel Testing Helpers

*   **HTTP Tests:** `$this->get()`, `$this->post()`, `$this->put()`, `$this->delete()`, `$this->json()`.
*   **Authentication:** `$this->actingAs($user, 'guard')`.
*   **Session:** `$response->assertSessionHas('key', 'value')`, `$response->assertSessionMissing('key')`.
*   **Validation Errors:** `$response->assertSessionHasErrors(['field'])`, `$response->assertInvalid(['field'])`.
*   **Database:**
    *   `$this->assertDatabaseHas('table', ['column' => 'value'])`.
    *   `$this->assertDatabaseMissing('table', [...])`.
    *   `$this->assertDatabaseCount('table', count)`.
*   **Events:** `Event::fake()`, `Event::assertDispatched(MyEvent::class)`.
*   **Jobs/Queues:** `Queue::fake()`, `Queue::assertPushed(MyJob::class)`.
*   **Mail:** `Mail::fake()`, `Mail::assertSent(MyMailable::class)`.
*   **Notifications:** `Notification::fake()`, `Notification::assertSentTo($user, MyNotification::class)`.

Automated testing is crucial for building reliable Laravel applications. Choose either PHPUnit or Pest based on preference.

*(Refer to the official Laravel documentation on Testing.)*