Parent Task: [ROO#TASK_20250523213800_A1B2C3](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md)
Parent Task ID: ROO#TASK_20250523213800_A1B2C3
Previous Sub-Task ID: [ROO#SUB_A1B2C3_S006_20250523234304_F006](/.rooroo/tasks/ROO#SUB_A1B2C3_S006_20250523234304_F006/context.md) (Pipeline Visualization)

Goal for Expert (rooroo-developer):
Implement Job Queue Operations.
1.  Worker Lifecycle Management UI/Backend:
    *   Display status of FlowerPower workers (e.g., running, stopped).
    *   Buttons to start/stop workers (these would trigger commands or API calls to the FlowerPower worker processes). This might involve `JobQueueManager.has_workers_running()` or similar status checks and methods to manage workers if available directly, or may require shell command execution.
2.  Scheduler Control UI/Backend:
    *   Display status of the FlowerPower scheduler.
    *   Buttons to start/stop the scheduler (interfacing with `JobQueueManager.is_scheduler_running()` and control methods).
3.  Real-time Job Queue Monitoring:
    *   Display a list of jobs in the queue (pending, running, failed, completed) with Datastar for real-time updates.
    *   Allow pausing, resuming, and canceling individual queued jobs.
    *   Sanic endpoints to interact with `JobQueueManager` for these operations (e.g., `get_jobs`, `pause_job`, `resume_job`, `cancel_job`).
4.  Schedule Management:
    *   Display currently scheduled pipeline runs.
    *   Allow pausing, resuming, and deleting scheduled items (interfacing with `JobQueueManager`'s schedule manipulation methods).
5.  Queue Maintenance:
    *   UI elements and backend logic for purging queues or performing cleanup (e.g., `JobQueueManager.purge_queue()`).
6.  Job Execution History:
    *   Display a log or history of job executions.

Key information from parent context:
- User Request (Lines [22-29](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md:22)): Worker lifecycle, scheduler control, job queue monitoring/management, schedule management, queue maintenance, job history.
- FlowerPower library components: `JobQueueManager` ([`src/flowerpower/job_queue/base.py`](/src/flowerpower/job_queue/base.py:1)) and its various methods for queue, job, and schedule manipulation.

Dependencies:
- Application with pipeline features from [ROO#SUB_A1B2C3_S006_20250523234304_F006](/.rooroo/tasks/ROO#SUB_A1B2C3_S006_20250523234304_F006/context.md).
- Analysis report from [ROO#SUB_A1B2C3_S001_20250523233918_A001](/.rooroo/tasks/ROO#SUB_A1B2C3_S001_20250523233918_A001/context.md).

Deliverables:
- Updated Sanic application with comprehensive job queue operation features.
- Documentation for new API endpoints and integration points with `JobQueueManager`.