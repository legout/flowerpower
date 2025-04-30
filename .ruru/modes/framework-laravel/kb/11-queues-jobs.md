# Laravel: Queues & Jobs

Deferring time-consuming tasks using Laravel's queue system.

## Core Concept

Queues allow you to defer the processing of time-consuming tasks, such as sending emails, processing images, or calling external APIs, until a later time. This drastically improves the response time of your web requests.

*   **Jobs:** Classes that represent the task to be performed asynchronously. They typically reside in `app/Jobs`.
*   **Queues:** Jobs are pushed onto queues (e.g., stored in Redis, a database, SQS).
*   **Workers:** Separate processes (`php artisan queue:work`) that listen to queues and execute jobs as they become available.
*   **Drivers:** Configure how jobs are stored (database, Redis, Beanstalkd, SQS, sync). Set in `.env` (`QUEUE_CONNECTION`) and `config/queue.php`.

## Creating Jobs

*   **Artisan Command:** `php artisan make:job ProcessPodcast`
*   **Structure:** Job classes typically have a `handle` method where the task logic resides. Dependencies needed by the job can often be type-hinted in the constructor or the `handle` method (resolved by the service container). Data needed for the job is usually passed to the constructor and stored as public properties.

```php
<?php
// app/Jobs/ProcessPodcast.php

namespace App\Jobs;

use App\Models\Podcast; // Example model
use App\Models\User; // Example User model
use App\Services\AudioProcessor; // Example service
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue; // Interface for queued jobs
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels; // Important for Eloquent models
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Notification; // Example Notification facade
use App\Notifications\PodcastProcessed as PodcastProcessedNotification; // Example Notification class

class ProcessPodcast implements ShouldQueue // Implement ShouldQueue for async execution
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    // Public properties are automatically serialized and available in handle()
    public Podcast $podcast;
    public User $user; // Example: User who initiated the job

    /**
     * Create a new job instance.
     */
    public function __construct(Podcast $podcast, User $user)
    {
        $this->podcast = $podcast;
        $this->user = $user;
        // Optionally set queue or connection:
        // $this->onQueue('podcasts');
        // $this->onConnection('redis');
    }

    /**
     * Execute the job.
     * Dependencies can be injected here too.
     */
    public function handle(AudioProcessor $processor): void
    {
        Log::info("Processing podcast {$this->podcast->id} for user {$this->user->id}");
        try {
            // Example: Use an injected service
            $processor->process($this->podcast);

            // Update podcast status (using the serialized model)
            $this->podcast->status = 'processed';
            $this->podcast->save();

            Log::info("Finished processing podcast {$this->podcast->id}");

            // Optionally notify the user
            Notification::send($this->user, new PodcastProcessedNotification($this->podcast));

        } catch (\Exception $e) {
            Log::error("Failed to process podcast {$this->podcast->id}: " . $e->getMessage());
            // Handle failure: release back to queue, fail job, etc.
            // $this->release(60); // Release back to queue, try again in 60 seconds
            $this->fail($e); // Mark job as failed
        }
    }

    /**
     * Handle a job failure. (Optional)
     */
    public function failed(\Throwable $exception): void
    {
        // Send user notification of failure, etc...
        Log::critical("Podcast processing job failed for {$this->podcast->id}: " . $exception->getMessage());
    }
}
```

## Dispatching Jobs

*   **Dispatch Helper:** `dispatch(new ProcessPodcast($podcast, $user))`
*   **Dispatch Method:** `ProcessPodcast::dispatch($podcast, $user)`
*   **Conditional Dispatch:** `ProcessPodcast::dispatchIf($condition, $podcast, $user)`
*   **Dispatch to Specific Queue/Connection:**
    *   `ProcessPodcast::dispatch($podcast, $user)->onQueue('podcasts')`
    *   `ProcessPodcast::dispatch($podcast, $user)->onConnection('redis')`
*   **Delayed Dispatch:**
    *   `ProcessPodcast::dispatch($podcast, $user)->delay(now()->addMinutes(10))`
*   **Chaining Jobs:** Run jobs sequentially.
    ```php
    use Illuminate\Support\Facades\Bus;
    use App\Jobs\FetchPodcastFeed; // Example Job
    use App\Jobs\SendPodcastNotification; // Example Job

    Bus::chain([
        new FetchPodcastFeed($podcast),
        new ProcessPodcast($podcast, $user),
        new SendPodcastNotification($podcast, $user),
    ])->dispatch();
    ```

```php
// Example in a Controller
use App\Jobs\ProcessPodcast;
use App\Models\Podcast;
use Illuminate\Http\Request;

public function store(Request $request)
{
    // ... validate request, create podcast ...
    $podcast = Podcast::create([/* ... data ... */]);
    $user = $request->user();

    // Dispatch the job to the queue
    ProcessPodcast::dispatch($podcast, $user);
    // Or: dispatch(new ProcessPodcast($podcast, $user));

    return redirect()->route('podcasts.index')->with('status', 'Podcast upload successful! Processing will start shortly.');
}
```

## Running Queue Workers

*   **Command:** `php artisan queue:work [connection] [--queue=...] [--tries=N] [--timeout=S] [--sleep=S]`
    *   `connection`: Specify connection (e.g., `redis`, `database`). Defaults to `QUEUE_CONNECTION` in `.env`.
    *   `--queue=high,default`: Process specific queues (comma-separated, processed in order).
    *   `--tries=3`: Number of times to attempt a job before marking as failed.
    *   `--timeout=60`: Max seconds a child process can run.
    *   `--sleep=3`: Seconds to sleep if no jobs are available.
    *   `--daemon`: Run worker in daemon mode (more efficient, but requires code deployment to restart). **Important:** Ensure workers are restarted during deployment if using daemon mode.
*   **Production:** Use a process manager like Supervisor or Systemd to run `php artisan queue:work` continuously and restart it if it fails. Configure multiple workers for different queues (e.g., dedicated workers for `long` queue).

## Configuration (`config/queue.php`, `.env`)

*   **`QUEUE_CONNECTION` (.env):** Set the default queue driver (`sync`, `database`, `redis`, `beanstalkd`, `sqs`).
    *   `sync`: Runs jobs immediately (useful for local testing, disables async behavior).
    *   `database`: Stores jobs in the `jobs` database table (requires `php artisan queue:table` and `php artisan migrate`). Simple but less performant than Redis.
    *   `redis`: Uses Redis lists (recommended for performance). Requires Redis server and `predis/predis` or `phpredis` extension.
*   **`config/queue.php`:** Configure connection details (host, port, password, queue names) for each driver.

## Handling Failed Jobs

*   Jobs that exceed max tries or timeout are moved to the `failed_jobs` table (if using `database` driver or configured).
*   **`php artisan queue:failed`**: List failed jobs.
*   **`php artisan queue:retry [id|--all]`**: Retry failed jobs.
*   **`php artisan queue:forget <id>`**: Delete a specific failed job.
*   **`php artisan queue:flush`**: Delete all failed jobs.
*   Implement the `failed()` method on your Job class for custom failure logic.

Queues are essential for building responsive and scalable Laravel applications by offloading long-running tasks.

*(Refer to the official Laravel Queues documentation: https://laravel.com/docs/queues)*