# flowerpower job-queue Commands { #flowerpower-job-queue }

This section details the commands available under `flowerpower job-queue`.

## start_worker { #flowerpower-start_worker }

Start a worker or worker pool to process jobs.

This command starts a worker process (or a pool of worker processes) that will
execute jobs from the queue. The worker will continue running until stopped
or can be run in the background.

### Usage

```bash
flowerpower job-queue start_worker [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| type | str | Type of job queue backend (rq) | Required |
| name | str | Name of the scheduler configuration to use | Required |
| base_dir | str | Base directory for the scheduler configuration | Required |
| background | str | Run the worker in the background | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level (debug, info, warning, error, critical) | Required |
| num_workers | str | Number of worker processes to start (pool mode) | Required |


### Examples

```bash
$ flowerpower job-queue start-worker

# Start a worker for a specific backend type
```

```bash
$ flowerpower job-queue start-worker --type rq

# Start a worker pool with 4 processes
```

```bash
$ flowerpower job-queue start-worker --num-workers 4

# Run a worker in the background
```

```bash
$ flowerpower job-queue start-worker --background

# Set a specific logging level
```

```bash
$ flowerpower job-queue start-worker --log-level debug
```

---

## cancel_job { #flowerpower-cancel_job }

Cancel a job or multiple jobs in the queue.

This command stops a job from executing (if it hasn't started yet) or signals
it to stop (if already running). Canceling is different from deleting as it
maintains the job history but prevents execution.

### Usage

```bash
flowerpower job-queue cancel_job [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| job_id | str | ID of the job to cancel (ignored if --all is used) | Required |
| all | str | Cancel all jobs instead of a specific one | Required |
| queue_name | str | For RQ only, specifies the queue to cancel jobs from | Required |
| type | str | Type of job queue backend (rq) | Required |
| name | str | Name of the scheduler configuration to use | Required |
| base_dir | str | Base directory for the scheduler configuration | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level (debug, info, warning, error, critical) | Required |


### Examples

```bash
$ flowerpower job-queue cancel-job job-123456

# Cancel all jobs in the default queue
```

```bash
$ flowerpower job-queue cancel-job --all dummy-id

# Cancel all jobs in a specific queue (RQ only)
```

```bash
$ flowerpower job-queue cancel-job --all dummy-id --queue-name high-priority

# Specify the backend type explicitly
```

```bash
$ flowerpower job-queue cancel-job job-123456 --type rq
```

---

## cancel_schedule { #flowerpower-cancel_schedule }

Cancel a specific schedule.

Note: This is different from deleting a schedule as it only stops it from running but keeps its configuration.

### Usage

```bash
flowerpower job-queue cancel_schedule [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| schedule_id | str | ID of the schedule to cancel | Required |
| all | str | If True, cancel all schedules | Required |
| type | str | Type of the job queue (rq) | Required |
| name | str | Name of the scheduler | Required |
| base_dir | str | Base directory for the scheduler | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level | Required |


---

## delete_job { #flowerpower-delete_job }

Delete a specific job.

### Usage

```bash
flowerpower job-queue delete_job [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| job_id | str | ID of the job to delete | Required |
| all | str | If True, delete all jobs | Required |
| queue_name | str | Name of the queue (RQ only). If provided and all is True, delete all jobs in the queue | Required |
| type | str | Type of the job queue (rq) | Required |
| name | str | Name of the scheduler | Required |
| base_dir | str | Base directory for the scheduler | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level | Required |


---

## delete_schedule { #flowerpower-delete_schedule }

Delete a specific schedule.

### Usage

```bash
flowerpower job-queue delete_schedule [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| schedule_id | str | ID of the schedule to delete | Required |
| all | str | If True, delete all schedules | Required |
| type | str | Type of the job queue (rq) | Required |
| name | str | Name of the scheduler | Required |
| base_dir | str | Base directory for the scheduler | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level | Required |


---

## show_job_ids { #flowerpower-show_job_ids }

Show all job IDs in the job queue.

This command displays all job IDs currently in the system, helping you identify
jobs for other operations like getting results, canceling, or deleting jobs.

### Usage

```bash
flowerpower job-queue show_job_ids [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| type | str | Type of job queue backend (rq) | Required |
| name | str | Name of the scheduler configuration to use | Required |
| base_dir | str | Base directory for the scheduler configuration | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level (debug, info, warning, error, critical) | Required |


### Examples

```bash
$ flowerpower job-queue show-job-ids

# Show job IDs for a specific queue type
```

```bash
$ flowerpower job-queue show-job-ids --type rq

# Show job IDs with a custom scheduler configuration
```

```bash
$ flowerpower job-queue show-job-ids --name my-scheduler

# Show job IDs with debug logging
```

```bash
$ flowerpower job-queue show-job-ids --log-level debug
```

---

## show_schedule_ids { #flowerpower-show_schedule_ids }

Show all schedule IDs in the job queue.

This command displays all schedule IDs currently in the system, helping you
identify schedules for other operations like pausing, resuming, or deleting schedules.

### Usage

```bash
flowerpower job-queue show_schedule_ids [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| type | str | Type of job queue backend (rq) | Required |
| name | str | Name of the scheduler configuration to use | Required |
| base_dir | str | Base directory for the scheduler configuration | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level (debug, info, warning, error, critical) | Required |


### Examples

```bash
$ flowerpower job-queue show-schedule-ids

# Show schedule IDs for RQ
```

```bash
$ flowerpower job-queue show-schedule-ids --type rq

# Show schedule IDs with a custom scheduler configuration
```

```bash
$ flowerpower job-queue show-schedule-ids --name my-scheduler

# Show schedule IDs with debug logging
```

```bash
$ flowerpower job-queue show-schedule-ids --log-level debug
```

---

## pause_schedule { #flowerpower-pause_schedule }

Pause a schedule or multiple schedules.

This command temporarily stops a scheduled job from running while maintaining its
configuration. Paused schedules can be resumed later. 

### Usage

```bash
flowerpower job-queue pause_schedule [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| schedule_id | str | ID of the schedule to pause (ignored if --all is used) | Required |
| all | str | Pause all schedules instead of a specific one | Required |
| type | str | Type of job queue backend (rq) | Required |
| name | str | Name of the scheduler configuration to use | Required |
| base_dir | str | Base directory for the scheduler configuration | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level (debug, info, warning, error, critical) | Required |


### Examples

```bash
$ flowerpower job-queue pause-schedule schedule-123456

# Pause all schedules
```

```bash
$ flowerpower job-queue pause-schedule --all dummy-id

# Note: Schedule pausing is not supported for RQ workers
```

---

## resume_schedule { #flowerpower-resume_schedule }

Resume a paused schedule or multiple schedules.

This command restarts previously paused schedules, allowing them to run again according
to their original configuration. 

### Usage

```bash
flowerpower job-queue resume_schedule [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| schedule_id | str | ID of the schedule to resume (ignored if --all is used) | Required |
| all | str | Resume all schedules instead of a specific one | Required |
| type | str | Type of job queue backend (rq) | Required |
| name | str | Name of the scheduler configuration to use | Required |
| base_dir | str | Base directory for the scheduler configuration | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level (debug, info, warning, error, critical) | Required |


### Examples

```bash
$ flowerpower job-queue resume-schedule schedule-123456

# Resume all schedules
```

```bash
$ flowerpower job-queue resume-schedule --all dummy-id

# Note: Schedule resuming is not supported for RQ workers

# Set a specific logging level
```

```bash
$ flowerpower job-queue resume-schedule schedule-123456 --log-level debug
```

---

## show_jobs { #flowerpower-show_jobs }

Display detailed information about all jobs in the queue.

This command shows comprehensive information about jobs including their status,
creation time, execution time, and other details in a user-friendly format.

### Usage

```bash
flowerpower job-queue show_jobs [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| type | str | Type of job queue backend (rq) | Required |
| queue_name | str | Name of the queue to show jobs from (RQ only) | Required |
| name | str | Name of the scheduler configuration to use | Required |
| base_dir | str | Base directory for the scheduler configuration | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level (debug, info, warning, error, critical) | Required |
| format | str | Output format for the job information | Required |


### Examples

```bash
$ flowerpower job-queue show-jobs

# Show jobs for a specific queue type
```

```bash
$ flowerpower job-queue show-jobs --type rq

# Show jobs in a specific RQ queue
```

```bash
$ flowerpower job-queue show-jobs --queue-name high-priority

# Display jobs in JSON format
```

```bash
$ flowerpower job-queue show-jobs --format json
```

---

## show_schedules { #flowerpower-show_schedules }

Display detailed information about all schedules.

This command shows comprehensive information about scheduled jobs including their
timing configuration, status, and other details in a user-friendly format.

### Usage

```bash
flowerpower job-queue show_schedules [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| type | str | Type of job queue backend (rq) | Required |
| name | str | Name of the scheduler configuration to use | Required |
| base_dir | str | Base directory for the scheduler configuration | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level (debug, info, warning, error, critical) | Required |
| format | str | Output format for the schedule information | Required |


### Examples

```bash
$ flowerpower job-queue show-schedules

# Show schedules for RQ
```

```bash
$ flowerpower job-queue show-schedules --type rq

# Display schedules in JSON format
```

```bash
$ flowerpower job-queue show-schedules --format json
```

---

## enqueue_pipeline { #flowerpower-enqueue_pipeline }

Enqueue a pipeline for execution via the job queue.

This command queues a pipeline for asynchronous execution using the configured
job queue backend (RQ). The job can be executed immediately, after a delay,
or at a specific time.

### Usage

```bash
flowerpower job-queue enqueue_pipeline [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| name | str | Name of the pipeline to enqueue | Required |
| base_dir | str | Base directory containing pipelines and configurations | Required |
| inputs | str | Input parameters for the pipeline | Required |
| final_vars | str | Final variables to request from the pipeline | Required |
| storage_options | str | Options for storage backends | Required |
| log_level | str | Set the logging level | Required |
| run_in | str | Delay before execution (duration format like '5m', '1h', '30s') | Required |
| run_at | str | Specific datetime for execution (ISO format) | Required |


### Examples

```bash
$ flowerpower job-queue enqueue-pipeline my_pipeline

# Enqueue with custom inputs
```

```bash
$ flowerpower job-queue enqueue-pipeline my_pipeline --inputs '{"data_path": "data/file.csv"}'

# Enqueue with delay
```

```bash
$ flowerpower job-queue enqueue-pipeline my_pipeline --run-in "30m"

# Enqueue for specific time
```

```bash
$ flowerpower job-queue enqueue-pipeline my_pipeline --run-at "2025-01-01T09:00:00"
```

---

## schedule_pipeline { #flowerpower-schedule_pipeline }

Schedule a pipeline for recurring or future execution.

This command sets up recurring or future execution of a pipeline using cron
expressions or interval-based scheduling via the configured job queue backend.

### Usage

```bash
flowerpower job-queue schedule_pipeline [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| name | str | Name of the pipeline to schedule | Required |
| base_dir | str | Base directory containing pipelines and configurations | Required |
| cron | str | Cron expression for scheduling (e.g., '0 9 * * *' for 9 AM daily) | Required |
| interval | str | Interval for recurring execution (duration format) | Required |
| inputs | str | Input parameters for the pipeline | Required |
| final_vars | str | Final variables to request from the pipeline | Required |
| storage_options | str | Options for storage backends | Required |
| log_level | str | Set the logging level | Required |
| schedule_id | str | Custom identifier for the schedule | Required |


### Examples

```bash
$ flowerpower job-queue schedule-pipeline my_pipeline --cron "0 9 * * *"

# Schedule every 30 minutes
```

```bash
$ flowerpower job-queue schedule-pipeline my_pipeline --interval "30m"

# Schedule with custom inputs and ID
```

```bash
$ flowerpower job-queue schedule-pipeline my_pipeline --cron "0 0 * * *" \\
--inputs '{"env": "prod"}' --schedule-id "nightly-prod"
```

---

## run_job { #flowerpower-run_job }

Execute a specific job by its ID.

This command runs a job that has been previously enqueued in the job queue.
The job will be executed immediately regardless of its original schedule.

### Usage

```bash
flowerpower job-queue run_job [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| job_id | str | ID of the job to run | Required |
| type | str | Type of job queue backend (rq) | Required |
| name | str | Name of the scheduler configuration to use | Required |
| base_dir | str | Base directory for the scheduler configuration | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level (debug, info, warning, error, critical) | Required |


### Examples

```bash
$ flowerpower job-queue run-job job-123456

# Run a job with a specific backend type
```

```bash
$ flowerpower job-queue run-job job-123456 --type rq

# Run a job with debug logging
```

```bash
$ flowerpower job-queue run-job job-123456 --log-level debug
```

---

## list_schedules { #flowerpower-list_schedules }

List all schedules with detailed status information.

This command provides enhanced schedule listing showing trigger configuration,
status, next run time, and execution history. This is an enhanced version of
show-schedules with more detailed information.

### Usage

```bash
flowerpower job-queue list_schedules [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| type | str | Type of job queue backend (rq) | Required |
| name | str | Name of the scheduler configuration to use | Required |
| base_dir | str | Base directory for the scheduler configuration | Required |
| storage_options | str | Storage options as JSON or key=value pairs | Required |
| log_level | str | Logging level (debug, info, warning, error, critical) | Required |
| format | str | Output format for the schedule information | Required |
| show_status | str | Include schedule status information | Required |
| show_next_run | str | Include next execution time information | Required |


### Examples

```bash
$ flowerpower job-queue list-schedules

# List schedules in JSON format
```

```bash
$ flowerpower job-queue list-schedules --format json

# List schedules without status information
```

```bash
$ flowerpower job-queue list-schedules --no-show-status

# List schedules for a specific backend
```

```bash
$ flowerpower job-queue list-schedules --type rq
```

---

