# RQManager

**Module:** `flowerpower.job_queue.rq.RQManager`

The `RQManager` is the implementation of `JobQueueManager` for Redis Queue (RQ). It handles the specifics of interacting with an RQ backend.

## Initialization

### __init__
```python
__init__(self, name: str, base_dir: str | None = None, backend: RQBackend | None = None, storage_options: dict | None = None, fs: AbstractFileSystem | None = None, log_level: str | None = None)
```

Initializes the `RQManager`.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `name` | `str` | The name of the scheduler instance. | |
| `base_dir` | `str \| None` | The base directory of the project. | `None` |
| `backend` | `RQBackend \| None` | An `RQBackend` instance for Redis connection configuration. | `None` |
| `storage_options` | `dict \| None` | Storage options for the filesystem. | `None` |
| `fs` | `AbstractFileSystem \| None` | An fsspec-compatible filesystem instance. | `None` |
| `log_level` | `str \| None` | The logging level. | `None` |

## Methods

### add_job
```python
add_job(self, func: Callable, func_args: list | None = None, func_kwargs: dict | None = None, job_id: str | None = None, result_ttl: int | None = None, ttl: int | None = None, timeout: int | None = None, queue_name: str | None = None, run_at: datetime | None = None, run_in: timedelta | int | str | None = None, retry: Retry | None = None, repeat: int | None = None, meta: dict | None = None, failure_ttl: int | None = None, group_id: str | None = None, on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = None, on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = None, on_stopped: Callable | tuple[Callable, tuple | None, dict | None] | None = None, **job_kwargs)
```

Adds a job to the queue for immediate or scheduled execution.

!!! warning
    This method is deprecated. Use `enqueue`, `enqueue_in`, or `enqueue_at` instead.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `func` | `Callable` | The function to execute. | |
| `func_args` | `list | None` | Positional arguments for the function. | `None` |
| `func_kwargs` | `dict | None` | Keyword arguments for the function. | `None` |
| `job_id` | `str | None` | Unique identifier for the job. | `None` |
| `result_ttl` | `int | None` | Time to live for job result (seconds). | `None` |
| `ttl` | `int | None` | Total time to live for the job (seconds). | `None` |
| `timeout` | `int | None` | Job execution timeout (seconds). | `None` |
| `queue_name` | `str | None` | The name of the RQ queue to use. | `None` |
| `run_at` | `datetime | None` | Specific datetime to run the job. | `None` |
| `run_in` | `timedelta | int | str | None` | Delay before running the job. | `None` |
| `retry` | `Retry | None` | Retry policy for the job. | `None` |
| `repeat` | `int | None` | Number of times to repeat the job. | `None` |
| `meta` | `dict | None` | Arbitrary metadata for the job. | `None` |
| `failure_ttl` | `int | None` | Time to live for failed job result (seconds). | `None` |
| `group_id` | `str | None` | Group ID for the job. | `None` |
| `on_success` | `Callable | tuple[Callable, tuple | None, dict | None] | None` | Callback on job success. | `None` |
| `on_failure` | `Callable | tuple[Callable, tuple | None, dict | None] | None` | Callback on job failure. | `None` |
| `on_stopped` | `Callable | tuple[Callable, tuple | None, dict | None] | None` | Callback on job stopped. | `None` |
| `**job_kwargs` | `Any` | Additional keyword arguments for RQ's `Job` class. | |

**Returns:** `Job` - The enqueued job object.

**Raises:** `ValueError`: If required parameters are missing or invalid.

#### Example

```python
from flowerpower.job_queue.rq import RQManager
from datetime import datetime, timedelta

manager = RQManager(name="my_rq_manager")

# Enqueue a simple job
def my_task(x, y):
    return x + y

job = manager.add_job(my_task, func_args=[1, 2], queue_name="default")
print(f"Enqueued job {job.id}")

# Schedule a job to run in 5 minutes
job = manager.add_job(my_task, func_args=[3, 4], run_in=timedelta(minutes=5), queue_name="default")

# Schedule a job to run at a specific time
target_time = datetime(2025, 1, 1, 10, 0, 0)
job = manager.add_job(my_task, func_args=[5, 6], run_at=target_time, queue_name="default")
```

### start_worker
```python
start_worker(self, background: bool = False, queue_names: list[str] | None = None, with_scheduler: bool = False, **kwargs)
```

Starts a worker process for the job queue.

| Parameter | Type | Description | Default |
|:----------|:-----|:------------|:--------|
| `background` | `bool` | If `True`, runs the worker in the background. | `False` |
| `queue_names` | `list[str] \| None` | A list of RQ queues to listen to. Defaults to all queues. | `None` |
| `with_scheduler` | `bool` | If `True`, the worker also processes scheduled jobs. | `False` |
| `**kwargs` | `Any` | Additional arguments for RQ's `Worker` class. | |

**Returns:** `None`

**Raises:** `RuntimeError`: If the worker fails to start.

#### Example

```python
from flowerpower.job_queue.rq import RQManager

manager = RQManager(name="my_rq_manager")

# Start a worker in the foreground, listening to the 'default' queue
manager.start_worker(queue_names=["default"])

# Start a worker in the background with scheduler enabled
manager.start_worker(background=True, with_scheduler=True)
```