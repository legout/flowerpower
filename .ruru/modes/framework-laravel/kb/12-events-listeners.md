# Laravel: Events & Listeners

Decoupling application logic using Laravel's event system.

## Core Concept

Laravel's event system provides a simple observer implementation, allowing you to subscribe and listen for various events that occur in your application. This helps decouple different parts of your application, as one part can fire an event without knowing which other parts are listening and reacting to it.

*   **Events:** Classes that represent a significant occurrence in the application (e.g., `UserRegistered`, `OrderShipped`, `PodcastProcessed`). Typically stored in `app/Events`. They often contain data related to the event (e.g., the User or Order model).
*   **Listeners:** Classes that "listen" for specific events and perform actions when those events are fired. Typically stored in `app/Listeners`. They receive the event object in their `handle` method.
*   **Registration:** Events and their corresponding listeners are mapped in the `$listen` array within the `app/Providers/EventServiceProvider.php`.

## Creating Events & Listeners

*   **Artisan Commands:**
    *   `php artisan make:event PodcastProcessed`: Creates `app/Events/PodcastProcessed.php`.
    *   `php artisan make:listener SendPodcastNotification --event=PodcastProcessed`: Creates `app/Listeners/SendPodcastNotification.php` and automatically adds the mapping to `EventServiceProvider`.
    *   `php artisan event:generate`: Generates any missing events and listeners based on the mappings in `EventServiceProvider`.

## Defining Events

*   Event classes are typically simple data containers. Data needed by listeners is passed to the constructor and stored as public properties.
*   Use the `SerializesModels` trait if passing Eloquent models to queued listeners.
*   Use the `Broadcastable` interface and `broadcastOn()` method if the event should be broadcast over WebSocket channels (e.g., using Laravel Echo).

```php
<?php
// app/Events/PodcastProcessed.php

namespace App\Events;

use App\Models\Podcast;
use App\Models\User; // Assuming User model exists
use Illuminate\Broadcasting\Channel; // Correct import for Channel
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Broadcasting\PresenceChannel;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast; // Interface for broadcasting
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels; // Use if passing Eloquent models

class PodcastProcessed implements ShouldBroadcast // Example: Implement broadcasting
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    /**
     * The podcast instance.
     *
     * @var \App\Models\Podcast
     */
    public Podcast $podcast; // Public property for listeners

    /**
     * Create a new event instance.
     */
    public function __construct(Podcast $podcast)
    {
        $this->podcast = $podcast;
    }

    /**
     * Get the channels the event should broadcast on.
     *
     * @return array<int, \Illuminate\Broadcasting\Channel>
     */
    public function broadcastOn(): array
    {
        // Example: Broadcast on a private channel for the podcast owner
        return [
            new PrivateChannel('podcasts.'.$this->podcast->user_id),
        ];
    }

    /**
     * The event's broadcast name. (Optional)
     */
    // public function broadcastAs(): string
    // {
    //     return 'podcast.processed';
    // }

    /**
     * Get the data to broadcast. (Optional)
     */
    // public function broadcastWith(): array
    // {
    //     return ['id' => $this->podcast->id, 'status' => 'processed'];
    // }
}
```

## Defining Listeners

*   Listeners have a `handle` method that receives the event object.
*   Dependencies can be type-hinted in the constructor or `handle` method for automatic injection.
*   Listeners can implement `ShouldQueue` to be executed asynchronously by a queue worker.

```php
<?php
// app/Listeners/SendPodcastNotification.php

namespace App\Listeners;

use App\Events\PodcastProcessed;
use Illuminate\Contracts\Queue\ShouldQueue; // Implement for async execution
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Support\Facades\Mail; // Example: Using Mail facade
use App\Mail\PodcastReadyMail; // Example Mailable
use Illuminate\Support\Facades\Log; // Logging facade

class SendPodcastNotification implements ShouldQueue // Queued listener
{
    use InteractsWithQueue; // Provides methods like release(), fail()

    /**
     * Create the event listener.
     */
    public function __construct()
    {
        // Optionally inject dependencies here
        // $this->onConnection('redis')->onQueue('listeners'); // Specify connection/queue
    }

    /**
     * Handle the event.
     */
    public function handle(PodcastProcessed $event): void // Type-hint the event
    {
        // Access event data via public properties
        $podcast = $event->podcast;
        // Eager load user if not already loaded and needed
        $user = $podcast->user()->first(); // Assuming user relationship exists

        if ($user && $user->email) {
            try {
                Mail::to($user)->send(new PodcastReadyMail($podcast));
                Log::info("Podcast processed notification sent to {$user->email} for podcast {$podcast->id}");
            } catch (\Exception $e) {
                Log::error("Failed sending podcast notification for podcast {$podcast->id}: " . $e->getMessage());
                // Optionally release back to queue or fail explicitly
                $this->fail($e);
            }
        } else {
             Log::warning("No user or email found for podcast {$podcast->id}, cannot send notification.");
        }
    }

    /**
     * Handle a job failure. (Optional: For queued listeners)
     */
    public function failed(PodcastProcessed $event, \Throwable $exception): void
    {
        Log::critical("SendPodcastNotification listener failed for podcast {$event->podcast->id}: " . $exception->getMessage());
        // Add further error reporting if needed
    }
}
```

## Registering Listeners (`EventServiceProvider`)

*   Map events to their listeners in the `$listen` array.

```php
<?php
// app/Providers/EventServiceProvider.php

namespace App\Providers;

use App\Events\PodcastProcessed;
use App\Listeners\SendPodcastNotification;
use Illuminate\Auth\Events\Registered; // Example built-in event
use Illuminate\Auth\Listeners\SendEmailVerificationNotification; // Example built-in listener
use Illuminate\Foundation\Support\Providers\EventServiceProvider as ServiceProvider;
use Illuminate\Support\Facades\Event;

class EventServiceProvider extends ServiceProvider
{
    /**
     * The event to listener mappings for the application.
     *
     * @var array<class-string, array<int, class-string>>
     */
    protected $listen = [
        PodcastProcessed::class => [ // Event class
            SendPodcastNotification::class, // Listener class(es)
            // Add other listeners for the same event here
            // \App\Listeners\UpdatePodcastAnalytics::class,
        ],
        Registered::class => [ // Built-in Laravel event
            SendEmailVerificationNotification::class,
        ],
        // Other event mappings...
    ];

    /**
     * Register any events for your application.
     */
    public function boot(): void
    {
        // Optionally register listeners manually or use anonymous listeners
        // Event::listen(PodcastProcessed::class, function (PodcastProcessed $event) { ... });
    }

    /**
     * Determine if events and listeners should be automatically discovered. (Optional)
     * Requires specific directory structure (app/Listeners) and naming conventions.
     */
    // public function shouldDiscoverEvents(): bool
    // {
    //     return true; // Enables automatic discovery
    // }
}
```

## Dispatching Events

*   **`Event::dispatch()` Facade:** `Event::dispatch(new PodcastProcessed($podcast))`
*   **`event()` Helper:** `event(new PodcastProcessed($podcast))`
*   **Model Events:** Eloquent models fire several events automatically (`creating`, `created`, `updating`, `updated`, `saving`, `saved`, `deleting`, `deleted`, `restoring`, `restored`). You can listen to these using Observers or the `$dispatchesEvents` property on the model.

```php
// Example in a Job or Controller after processing
use App\Events\PodcastProcessed;
use Illuminate\Support\Facades\Event;
use App\Models\Podcast;

// ... process podcast ...
$podcast = Podcast::find($podcastId);
if ($podcast) {
    $podcast->status = 'processed';
    $podcast->save();

    // Dispatch the event
    Event::dispatch(new PodcastProcessed($podcast));
    // or event(new PodcastProcessed($podcast));
}
```

## Queued Listeners

*   Implementing `ShouldQueue` on a listener makes its `handle` method execute asynchronously via the queue worker (`php artisan queue:work`).
*   This is crucial for listeners performing slow tasks like sending emails or calling external APIs.
*   Ensure your queue worker is running in production.
*   Use the `SerializesModels` trait in events if passing Eloquent models to queued listeners.

Events and Listeners provide a great way to decouple parts of your application, making it more maintainable and testable.

*(Refer to the official Laravel documentation on Events.)*