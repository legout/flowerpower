# Migration Plan: APScheduler to RQ & RQ-Scheduler in FlowerPower

This document outlines the plan for migrating the scheduling and background job processing in the `flowerpower` framework from APScheduler (v4) to RQ (Redis Queue) and RQ-Scheduler.

## 1. Understanding the Current APScheduler Implementation

The current system (`src/flowerpower/scheduler.py`, `src/flowerpower/pipeline.py`) uses APScheduler for:

*   **Job Persistence & Coordination:** Configurable data stores (e.g., SQL databases) and event brokers.
*   **Job Execution:** Embedded executors (Async, ThreadPool, ProcessPool) within `SchedulerManager`.
*   **Immediate Job Enqueueing:** `add_job` for background execution, returning a job ID.
*   **Immediate Job Execution & Result:** `run_job` for potentially synchronous execution and direct result return.
*   **Scheduled Job Enqueueing:** `schedule` method using various triggers.
*   **Management Interface:** Methods within `SchedulerManager` for inspection.
*   **Worker Lifecycle:** `start_worker` for embedded execution.

## 2. Introduction to RQ and RQ-Scheduler

*   **RQ (Redis Queue):** Simple library for queueing jobs using Redis as the broker and backend. Requires separate worker processes (`rq worker`).
*   **RQ-Scheduler:** Extension for scheduling jobs to be enqueued later. Uses Redis and requires a separate `rqscheduler` process.

## 3. High-Level Migration Steps

### 3.1. Dependencies

*   Add `rq` and `rq-scheduler` to `pyproject.toml`.
*   Remove `apscheduler` from `pyproject.toml`.

### 3.2. Backend Configuration

*   **Requirement:** Ensure a Redis server is available and accessible.
*   **Remove:** APScheduler data store and event broker setup logic (`_setup_data_store`, `_setup_event_broker` in `scheduler.py`) and related configuration entries in `project.yml` (or similar).
*   **Add:** Configuration for Redis connection details (host, port, db, password) in `project.yml` for RQ and RQ-Scheduler.

### 3.3. Scheduler/Queue Management Code

*   **Replace `SchedulerManager`:** Remove the `SchedulerManager` class.
*   **Introduce RQ/RQ-Scheduler Objects:** Interact primarily with:
    *   `rq.Queue`: For enqueuing jobs. Instantiate based on Redis connection config.
    *   `rq_scheduler.Scheduler`: For scheduling jobs. Instantiate based on Redis connection config.

### 3.4. Job Definition

*   The target function for jobs remains `PipelineManager.run`.

### 3.5. Job Enqueueing (Immediate Execution)

*   **Replace `add_job`/`run_job`:** Replace calls to `SchedulerManager.add_job` and `SchedulerManager.run_job` in `PipelineManager` and elsewhere.
*   **Use `queue.enqueue()`:** Use `rq.Queue.enqueue(PipelineManager.run, kwargs={...}, ...)` to add jobs to the Redis queue.
*   **Handle Asynchronicity:**
    *   `add_job` equivalent: `enqueue` returns a job object immediately. The result can be fetched later via `Job.fetch(job_id).result`.
    *   `run_job` equivalent (synchronous): This requires adaptation as `enqueue` is async. Options:
        1.  Enqueue and poll `job.result`.
        2.  Refactor calling code to be asynchronous.
        3.  (Less ideal) Run a temporary worker in the same process.

### 3.6. Job Scheduling

*   **Replace `schedule`:** Replace calls to `SchedulerManager.add_schedule` in `PipelineManager`.
*   **Use `scheduler` methods:** Use methods from `rq_scheduler.Scheduler`:
    *   `scheduler.enqueue_at(datetime, ...)`
    *   `scheduler.enqueue_in(timedelta, ...)`
    *   `scheduler.schedule(datetime, ..., interval=..., repeat=...)`
    *   `scheduler.cron(cron_string, ...)`

### 3.7. Worker/Scheduler Processes

*   **Remove:** Embedded worker logic (`start_worker`, `stop_worker`).
*   **Requirement:** Run separate, external processes:
    *   **RQ Workers:** `rq worker <queue_name> --url <redis_url>`
    *   **RQ Scheduler:** `rqscheduler --url <redis_url>`
*   **Management:** Use process managers like `supervisor`, `systemd`, Docker Compose, or Kubernetes.

### 3.8. Management Interface

*   **Replace:** APScheduler-specific methods (`get_schedules`, `get_jobs`, etc.).
*   **Use RQ/Redis:** Query RQ queues and the RQ-Scheduler via their APIs or by inspecting Redis directly.
    *   `queue.jobs`, `queue.finished_jobs`, `queue.failed_jobs`
    *   `scheduler.get_jobs()`
    *   `rq.job.Job.fetch(job_id, ...)`
*   **Update Utilities:** Adapt `display_jobs`, `display_schedules` etc. Consider `rq-dashboard`.

### 3.9. Configuration File (`project.yml`)

*   **Remove:** Sections related to APScheduler `data_store`, `event_broker`, `job_executors`.
*   **Add:** A section for Redis connection details (e.g., `redis_url` or host/port/db/password).

## 4. Key Differences Summary

*   **Simplicity (RQ) vs. Flexibility (APScheduler):** RQ is simpler, Redis-focused. APScheduler has more backend options.
*   **External Processes:** RQ mandates external worker/scheduler processes.
*   **Backend:** RQ requires Redis.
*   **API:** Significant API changes.
*   **Process Management:** External process management is crucial for RQ.

## 5. Next Steps

Proceed with implementation, likely by switching to a coding-focused mode.