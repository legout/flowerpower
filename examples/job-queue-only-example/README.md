# Job Queue-Only Example

This example demonstrates pure job queue functionality using FlowerPower's job processing capabilities without any pipeline dependencies.

## Prerequisites

- Python 3.11+
- Redis (for job queue backend)

## Quick Start

All commands should be run from the `examples/job-queue-only-example` directory.

### 1. Run Jobs Directly

Execute jobs directly. Ideal for development and testing.

**Using the script:**
```bash
uv run scripts/run_example.py calculations
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower job-queue enqueue calculations
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
job = project.job_queue_manager.enqueue(
    func="tasks.data_processing.simple_calculation",
    queue_name="calculations",
    x=10,
    y=5,
    operation="add"
)
```

### 2. Run with the Job Queue

Add jobs to be processed asynchronously.

**Terminal 1: Enqueue Job**

**Using the script:**
```bash
uv run scripts/run_example.py batch
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower job-queue enqueue batch
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
job = project.job_queue_manager.enqueue(
    func="tasks.data_processing.process_batch_data",
    queue_name="batch",
    data_list=[{"id": 1, "value": 10}, {"id": 2, "value": 20}],
    batch_size=10
)
```

**Terminal 2: Start Worker**
```bash
uv run flowerpower job-queue start-worker
```

### 3. Schedule a Job

Schedule jobs to run at a predefined time (e.g., daily at 2 AM).

**Terminal 1: Schedule Job**

**Using the script:**
```bash
uv run scripts/run_example.py scheduled
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower job-queue schedule --cron "0 2 * * *" --queue-name "maintenance" --func "tasks.data_processing.cleanup_old_files"
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
job = project.job_queue_manager.schedule(
    func="tasks.data_processing.cleanup_old_files",
    cron="0 2 * * *",
    queue_name="maintenance",
    directory="/tmp/logs",
    days_old=7
)
```

**Terminal 2: Start Worker with Scheduler**
```bash
uv run flowerpower job-queue start-worker --with-scheduler
```

## Project Structure

```
job-queue-only-example/
├── README.md                    # This file
├── requirements.txt             # Minimal dependencies (job queue only)
├── .env.example                # Environment variables template
├── conf/
│   └── project.yml             # Project configuration (job queue only)
├── tasks/
│   └── data_processing.py      # Standalone task functions
├── data/                       # Sample data (if needed)
└── scripts/
    └── run_example.py          # Script to run the example
```

## Key Components

- **Project Configuration (`conf/project.yml`):** Defines job queue settings and Redis connection.
- **Task Functions (`tasks/data_processing.py`):** Contains standalone functions that can be executed via the job queue.

## Task Function Examples

- `simple_calculation()` - Basic mathematical operations
- `process_batch_data()` - Batch data processing with progress tracking
- `generate_report()` - Report generation with different types
- `send_notification()` - Message sending simulation
- `cleanup_old_files()` - File maintenance tasks

## Expected Output

Running the examples will enqueue jobs and display their IDs. When workers process the jobs, you'll see the results of the calculations, data processing, or other task operations.

## Job Queue-Only vs Full FlowerPower

The job queue-only approach is ideal for simple function execution, background task processing, and microservice communication. Full FlowerPower is better suited for complex data processing pipelines with multi-step workflows and dependencies.

## Customizing the Example

- **Add New Tasks:** Create new functions in `tasks/data_processing.py` and enqueue them using the same pattern.
- **Configure Queues:** Modify `conf/project.yml` to adjust Redis connection settings or add queue-specific configurations.
- **Schedule Jobs:** Use the scheduling examples to set up recurring tasks with different cron expressions.

## Troubleshooting

- **Redis Connection Error:** Make sure the Redis server is running before using the job queue.
- **Import Errors:** Check that task functions are properly importable from the `tasks` directory.
- **Worker Not Processing:** Verify queue names match between enqueuing and workers.