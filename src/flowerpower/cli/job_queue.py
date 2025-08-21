import datetime as dt

import duration_parser
import typer
from loguru import logger

from .. import settings
from ..flowerpower import FlowerPowerProject
from ..job_queue import JobQueueManager  # Adjust import as needed
from ..utils.logging import setup_logging
from .utils import parse_dict_or_list_param

# Create a Typer app for job queue management commands
app = typer.Typer(help="Job queue management commands")

setup_logging(level=settings.LOG_LEVEL)


@app.command()
def start_worker(
    type: str | None = typer.Option(None, help="Type of job queue backend (rq)"),
    name: str | None = typer.Option(
        None, help="Name of the scheduler configuration to use"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory for the scheduler configuration"
    ),
    background: bool = typer.Option(
        False, "--background", "-b", help="Run the worker in the background"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON or key=value pairs"
    ),
    log_level: str = typer.Option(
        "info", help="Logging level (debug, info, warning, error, critical)"
    ),
    num_workers: int | None = typer.Option(
        None,
        "--num-workers",
        "-n",
        help="Number of worker processes to start (pool mode)",
    ),
):
    """
    Start a worker or worker pool to process jobs.

    This command starts a worker process (or a pool of worker processes) that will
    execute jobs from the queue. The worker will continue running until stopped
    or can be run in the background.

    Args:
        type: Type of job queue backend (rq)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        background: Run the worker in the background
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        num_workers: Number of worker processes to start (pool mode)

    Examples:
        # Start a worker with default settings
        $ flowerpower job-queue start-worker

        # Start a worker for a specific backend type
        $ flowerpower job-queue start-worker --type rq

        # Start a worker pool with 4 processes
        $ flowerpower job-queue start-worker --num-workers 4

        # Run a worker in the background
        $ flowerpower job-queue start-worker --background

        # Set a specific logging level
        $ flowerpower job-queue start-worker --log-level debug
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        if not num_workers:
            num_workers = worker.cfg.num_workers

        if num_workers and num_workers > 1:
            worker.start_worker_pool(num_workers=num_workers, background=background)
        else:
            worker.start_worker(background=background)


# @app.command()
# def cancel_all_jobs(
#     type: str | None = None,
#     queue_name: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     Cancel all jobs from the scheduler.

#     Note: This is different from deleting jobs as it only stops them from running but keeps their history.

#     Args:
#         type: Type of the job queue (rq)
#         queue_name: Name of the queue (RQ only)
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         if worker.cfg.backend.type != "rq":
#             logger.info(f"Job cancellation is not supported for {worker.cfg.backend.type} workers. Skipping.")
#             return

#         worker.cancel_all_jobs(queue_name=queue_name)

# @app.command()
# def cancel_all_schedules(
#     type: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     Cancel all schedules from the scheduler.

#     Note: This is different from deleting schedules as it only stops them from running but keeps their configuration.

#     Args:
#         type: Type of the job queue (rq)
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         worker.cancel_all_schedules()


@app.command()
def cancel_job(
    job_id: str = typer.Argument(..., help="ID of the job to cancel"),
    all: bool = typer.Option(
        False, "--all", "-a", help="Cancel all jobs instead of a specific one"
    ),
    queue_name: str | None = typer.Option(
        None,
        help="Name of the queue (RQ only). If provided with --all, cancels all jobs in the queue",
    ),
    type: str | None = typer.Option(None, help="Type of job queue backend (rq)"),
    name: str | None = typer.Option(
        None, help="Name of the scheduler configuration to use"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory for the scheduler configuration"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON or key=value pairs"
    ),
    log_level: str = typer.Option(
        "info", help="Logging level (debug, info, warning, error, critical)"
    ),
):
    """
    Cancel a job or multiple jobs in the queue.

    This command stops a job from executing (if it hasn't started yet) or signals
    it to stop (if already running). Canceling is different from deleting as it
    maintains the job history but prevents execution.

    Args:
        job_id: ID of the job to cancel (ignored if --all is used)
        all: Cancel all jobs instead of a specific one
        queue_name: For RQ only, specifies the queue to cancel jobs from
        type: Type of job queue backend (rq)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Cancel a specific job
        $ flowerpower job-queue cancel-job job-123456

        # Cancel all jobs in the default queue
        $ flowerpower job-queue cancel-job --all dummy-id

        # Cancel all jobs in a specific queue (RQ only)
        $ flowerpower job-queue cancel-job --all dummy-id --queue-name high-priority

        # Specify the backend type explicitly
        $ flowerpower job-queue cancel-job job-123456 --type rq
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        if all:
            count = worker.cancel_all_jobs(
                queue_name=queue_name if worker.cfg.backend.type == "rq" else None
            )
            logger.info(
                f"Cancelled {count} jobs"
                + (f" in queue '{queue_name}'" if queue_name else "")
            )
        else:
            worker.cancel_job(job_id)
            logger.info(f"Job {job_id} cancelled")


@app.command()
def cancel_schedule(
    schedule_id: str,
    all: bool = False,
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Cancel a specific schedule.

    Note: This is different from deleting a schedule as it only stops it from running but keeps its configuration.

    Args:
        schedule_id: ID of the schedule to cancel
        all: If True, cancel all schedules
        type: Type of the job queue (rq)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        if all:
            worker.cancel_all_schedules()
        else:
            worker.cancel_schedule(schedule_id)


# @app.command()
# def delete_all_jobs(
#     type: str | None = None,
#     queue_name: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     Delete all jobs from the scheduler. Note that this is different from cancelling jobs
#     as it also removes job history and results.

#     Args:
#         queue_name: Name of the queue (RQ only)
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         worker.delete_all_jobs(queue_name=queue_name if worker.cfg.backend.type == "rq" else None)

# @app.command()
# def delete_all_schedules(
#     type: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     Delete all schedules from the scheduler.

#     Args:
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         worker.delete_all_schedules()


@app.command()
def delete_job(
    job_id: str,
    all: bool = False,
    queue_name: str | None = None,
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Delete a specific job.

    Args:
        job_id: ID of the job to delete
        all: If True, delete all jobs
        queue_name: Name of the queue (RQ only). If provided and all is True, delete all jobs in the queue
        type: Type of the job queue (rq)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        if all:
            worker.delete_all_jobs(
                queue_name=queue_name if worker.cfg.backend.type == "rq" else None
            )
        else:
            worker.delete_job(job_id)


@app.command()
def delete_schedule(
    schedule_id: str,
    all: bool = False,
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Delete a specific schedule.

    Args:
        schedule_id: ID of the schedule to delete
        all: If True, delete all schedules
        type: Type of the job queue (rq)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        if all:
            worker.delete_all_schedules()
        else:
            worker.delete_schedule(schedule_id)


# @app.command()
# def get_job(
#     job_id: str,
#     type: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     Get information about a specific job.

#     Args:
#         job_id: ID of the job
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         # show_jobs should display the job info
#         worker.show_jobs(job_id=job_id)

# @app.command()
# def get_job_result(
#     job_id: str,
#     type: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
#     wait: bool = True,
# ):
#     """
#     Get the result of a specific job.

#     Args:
#         job_id: ID of the job
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#         wait: Wait for the result if job is still running (APScheduler only)
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         # worker's get_job_result method will handle the result display
#         worker.get_job_result(job_id, wait=wait if worker.cfg.backend.type == "apscheduler" else False)

# @app.command()
# def get_jobs(
#     type: str | None = None,
#     queue_name: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     List all jobs.

#     Args:
#         queue_name: Name of the queue (RQ only)
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         worker.show_jobs()

# @app.command()
# def get_schedule(
#     schedule_id: str,
#     type: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     Get information about a specific schedule.

#     Args:
#         schedule_id: ID of the schedule
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         # show_schedule should display the schedule info
#         worker.show_schedules(schedule_id=schedule_id)

# @app.command()
# def get_schedules(
#     type: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     List all schedules.

#     Args:
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         worker.show_schedules()


@app.command()
def show_job_ids(
    type: str | None = typer.Option(None, help="Type of job queue backend (rq)"),
    name: str | None = typer.Option(
        None, help="Name of the scheduler configuration to use"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory for the scheduler configuration"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON or key=value pairs"
    ),
    log_level: str = typer.Option(
        "info", help="Logging level (debug, info, warning, error, critical)"
    ),
):
    """
    Show all job IDs in the job queue.

    This command displays all job IDs currently in the system, helping you identify
    jobs for other operations like getting results, canceling, or deleting jobs.

    Args:
        type: Type of job queue backend (rq)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Show job IDs using default settings
        $ flowerpower job-queue show-job-ids

        # Show job IDs for a specific queue type
        $ flowerpower job-queue show-job-ids --type rq

        # Show job IDs with a custom scheduler configuration
        $ flowerpower job-queue show-job-ids --name my-scheduler

        # Show job IDs with debug logging
        $ flowerpower job-queue show-job-ids --log-level debug
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        # worker's job_ids property will print the IDs
        ids = worker.job_ids
        # Ensure we always print something meaningful
        if not ids:
            logger.info("No job IDs found")
        # If the worker's property doesn't already print the IDs, print them here
        elif not isinstance(ids, type(None)):  # Check if None was returned
            for job_id in ids:
                print(f"- {job_id}")


@app.command()
def show_schedule_ids(
    type: str | None = typer.Option(None, help="Type of job queue backend (rq)"),
    name: str | None = typer.Option(
        None, help="Name of the scheduler configuration to use"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory for the scheduler configuration"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON or key=value pairs"
    ),
    log_level: str = typer.Option(
        "info", help="Logging level (debug, info, warning, error, critical)"
    ),
):
    """
    Show all schedule IDs in the job queue.

    This command displays all schedule IDs currently in the system, helping you
    identify schedules for other operations like pausing, resuming, or deleting schedules.

    Args:
        type: Type of job queue backend (rq)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Show schedule IDs using default settings
        $ flowerpower job-queue show-schedule-ids

        # Show schedule IDs for RQ
        $ flowerpower job-queue show-schedule-ids --type rq

        # Show schedule IDs with a custom scheduler configuration
        $ flowerpower job-queue show-schedule-ids --name my-scheduler

        # Show schedule IDs with debug logging
        $ flowerpower job-queue show-schedule-ids --log-level debug
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        # worker's schedule_ids property will print the IDs
        ids = worker.schedule_ids
        # Ensure we always print something meaningful
        if not ids:
            logger.info("No schedule IDs found")
        # If the worker's property doesn't already print the IDs, print them here
        elif not isinstance(ids, type(None)):  # Check if None was returned
            for schedule_id in ids:
                print(f"- {schedule_id}")


# @app.command()
# def pause_all_schedules(
#     type: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     Pause all schedules.

#     Note: This functionality is only available for APScheduler workers.

#     Args:
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         if worker.cfg.backend.type != "apscheduler":
#             logger.info(f"Schedule pausing is not supported for {worker.cfg.backend.type} workers.")
#             return
#         worker.pause_all_schedules()


@app.command()
def pause_schedule(
    schedule_id: str = typer.Argument(..., help="ID of the schedule to pause"),
    all: bool = typer.Option(
        False, "--all", "-a", help="Pause all schedules instead of a specific one"
    ),
    type: str | None = typer.Option(None, help="Type of job queue backend (rq)"),
    name: str | None = typer.Option(
        None, help="Name of the scheduler configuration to use"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory for the scheduler configuration"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON or key=value pairs"
    ),
    log_level: str = typer.Option(
        "info", help="Logging level (debug, info, warning, error, critical)"
    ),
):
    """
    Pause a schedule or multiple schedules.

    This command temporarily stops a scheduled job from running while maintaining its
    configuration. Paused schedules can be resumed later. Note that this functionality
    is only available for APScheduler workers.

    Args:
        schedule_id: ID of the schedule to pause (ignored if --all is used)
        all: Pause all schedules instead of a specific one
        type: Type of job queue backend (rq)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Pause a specific schedule
        $ flowerpower job-queue pause-schedule schedule-123456

        # Pause all schedules
        $ flowerpower job-queue pause-schedule --all dummy-id

        # Note: Schedule pausing is not supported for RQ workers
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        logger.info("Schedule pausing is not supported for RQ workers.")
        return
        if all:
            count = worker.pause_all_schedules()
            logger.info(f"Paused {count} schedules")
        else:
            success = worker.pause_schedule(schedule_id)
            if success:
                logger.info(f"Schedule {schedule_id} paused successfully")
            else:
                logger.error(f"Failed to pause schedule {schedule_id}")


# @app.command()
# def resume_all_schedules(
#     type: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     Resume all paused schedules.

#     Note: This functionality is only available for APScheduler workers.

#     Args:
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         if worker.cfg.backend.type != "apscheduler":
#             logger.info(f"Schedule resuming is not supported for {worker.cfg.backend.type} workers.")
#             return
#         worker.resume_all_schedules()


@app.command()
def resume_schedule(
    schedule_id: str = typer.Argument(..., help="ID of the schedule to resume"),
    all: bool = typer.Option(
        False, "--all", "-a", help="Resume all schedules instead of a specific one"
    ),
    type: str | None = typer.Option(None, help="Type of job queue backend (rq)"),
    name: str | None = typer.Option(
        None, help="Name of the scheduler configuration to use"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory for the scheduler configuration"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON or key=value pairs"
    ),
    log_level: str = typer.Option(
        "info", help="Logging level (debug, info, warning, error, critical)"
    ),
):
    """
    Resume a paused schedule or multiple schedules.

    This command restarts previously paused schedules, allowing them to run again according
    to their original configuration. Note that this functionality is only available for
    APScheduler workers.

    Args:
        schedule_id: ID of the schedule to resume (ignored if --all is used)
        all: Resume all schedules instead of a specific one
        type: Type of job queue backend (rq)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Resume a specific schedule
        $ flowerpower job-queue resume-schedule schedule-123456

        # Resume all schedules
        $ flowerpower job-queue resume-schedule --all dummy-id

        # Note: Schedule resuming is not supported for RQ workers

        # Set a specific logging level
        $ flowerpower job-queue resume-schedule schedule-123456 --log-level debug
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        logger.info("Schedule resuming is not supported for RQ workers.")
        return
        if all:
            count = worker.resume_all_schedules()
            logger.info(f"Resumed {count} schedules")
        else:
            success = worker.resume_schedule(schedule_id)
            if success:
                logger.info(f"Schedule {schedule_id} resumed successfully")
            else:
                logger.error(f"Failed to resume schedule {schedule_id}")


@app.command()
def show_jobs(
    type: str | None = typer.Option(None, help="Type of job queue backend (rq)"),
    queue_name: str | None = typer.Option(
        None, help="Name of the queue to show jobs from (RQ only)"
    ),
    name: str | None = typer.Option(
        None, help="Name of the scheduler configuration to use"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory for the scheduler configuration"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON or key=value pairs"
    ),
    log_level: str = typer.Option(
        "info", help="Logging level (debug, info, warning, error, critical)"
    ),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
):
    """
    Display detailed information about all jobs in the queue.

    This command shows comprehensive information about jobs including their status,
    creation time, execution time, and other details in a user-friendly format.

    Args:
        type: Type of job queue backend (rq)
        queue_name: Name of the queue to show jobs from (RQ only)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        format: Output format for the job information

    Examples:
        # Show all jobs using default settings
        $ flowerpower job-queue show-jobs

        # Show jobs for a specific queue type
        $ flowerpower job-queue show-jobs --type rq

        # Show jobs in a specific RQ queue
        $ flowerpower job-queue show-jobs --queue-name high-priority

        # Display jobs in JSON format
        $ flowerpower job-queue show-jobs --format json
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        worker.show_jobs(queue_name=queue_name, format=format)


@app.command()
def show_schedules(
    type: str | None = typer.Option(None, help="Type of job queue backend (rq)"),
    name: str | None = typer.Option(
        None, help="Name of the scheduler configuration to use"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory for the scheduler configuration"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON or key=value pairs"
    ),
    log_level: str = typer.Option(
        "info", help="Logging level (debug, info, warning, error, critical)"
    ),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
):
    """
    Display detailed information about all schedules.

    This command shows comprehensive information about scheduled jobs including their
    timing configuration, status, and other details in a user-friendly format.

    Args:
        type: Type of job queue backend (rq)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        format: Output format for the schedule information

    Examples:
        # Show all schedules using default settings
        $ flowerpower job-queue show-schedules

        # Show schedules for RQ
        $ flowerpower job-queue show-schedules --type rq

        # Display schedules in JSON format
        $ flowerpower job-queue show-schedules --format json
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        worker.show_schedules(format=format)


@app.command()
def enqueue_pipeline(
    name: str = typer.Argument(..., help="Name of the pipeline to enqueue"),
    base_dir: str | None = typer.Option(None, help="Base directory for the pipeline"),
    inputs: str | None = typer.Option(
        None, help="Input parameters as JSON, dict string, or key=value pairs"
    ),
    final_vars: str | None = typer.Option(None, help="Final variables as JSON or list"),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    run_in: str | None = typer.Option(
        None, help="Schedule job to run after a delay (e.g., '5m', '1h', '30s')"
    ),
    run_at: str | None = typer.Option(
        None, help="Schedule job to run at a specific datetime (ISO format)"
    ),
):
    """
    Enqueue a pipeline for execution via the job queue.

    This command queues a pipeline for asynchronous execution using the configured
    job queue backend (RQ). The job can be executed immediately, after a delay,
    or at a specific time.

    Args:
        name: Name of the pipeline to enqueue
        base_dir: Base directory containing pipelines and configurations
        inputs: Input parameters for the pipeline
        final_vars: Final variables to request from the pipeline
        storage_options: Options for storage backends
        log_level: Set the logging level
        run_in: Delay before execution (duration format like '5m', '1h', '30s')
        run_at: Specific datetime for execution (ISO format)

    Examples:
        # Enqueue for immediate execution
        $ flowerpower job-queue enqueue-pipeline my_pipeline

        # Enqueue with custom inputs
        $ flowerpower job-queue enqueue-pipeline my_pipeline --inputs '{"data_path": "data/file.csv"}'

        # Enqueue with delay
        $ flowerpower job-queue enqueue-pipeline my_pipeline --run-in "30m"

        # Enqueue for specific time
        $ flowerpower job-queue enqueue-pipeline my_pipeline --run-at "2025-01-01T09:00:00"
    """
    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    # Use FlowerPowerProject for consistency
    project = FlowerPowerProject.load(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    )

    if project is None:
        logger.error(f"Failed to load FlowerPower project from {base_dir or '.'}")
        raise typer.Exit(1)

    if project.job_queue_manager is None:
        logger.error("No job queue configured. Cannot enqueue pipeline jobs.")
        raise typer.Exit(1)

    try:
        # Parse run_in duration if provided
        kwargs = {}
        if run_in:
            try:
                delay_seconds = duration_parser.parse(run_in).total_seconds()
                kwargs["run_in"] = delay_seconds
            except Exception as e:
                logger.error(f"Invalid duration format '{run_in}': {e}")
                raise typer.Exit(1)

        # Parse run_at datetime if provided
        if run_at:
            try:
                run_at_dt = dt.datetime.fromisoformat(run_at)
                kwargs["run_at"] = run_at_dt
            except Exception as e:
                logger.error(f"Invalid datetime format '{run_at}': {e}")
                raise typer.Exit(1)

        # Add pipeline execution parameters
        if parsed_inputs:
            kwargs["inputs"] = parsed_inputs
        if parsed_final_vars:
            kwargs["final_vars"] = parsed_final_vars

        job_id = project.enqueue(name, **kwargs)

        if run_in:
            logger.info(
                f"Pipeline '{name}' enqueued to run in {run_in}. Job ID: {job_id}"
            )
        elif run_at:
            logger.info(
                f"Pipeline '{name}' enqueued to run at {run_at}. Job ID: {job_id}"
            )
        else:
            logger.info(
                f"Pipeline '{name}' enqueued for immediate execution. Job ID: {job_id}"
            )

    except Exception as e:
        logger.error(f"Failed to enqueue pipeline '{name}': {e}")
        raise typer.Exit(1)


@app.command()
def schedule_pipeline(
    name: str = typer.Argument(..., help="Name of the pipeline to schedule"),
    base_dir: str | None = typer.Option(None, help="Base directory for the pipeline"),
    cron: str | None = typer.Option(
        None, help="Cron expression for recurring execution (e.g., '0 9 * * *')"
    ),
    interval: str | None = typer.Option(
        None, help="Interval for recurring execution (e.g., '1h', '30m')"
    ),
    inputs: str | None = typer.Option(
        None, help="Input parameters as JSON, dict string, or key=value pairs"
    ),
    final_vars: str | None = typer.Option(None, help="Final variables as JSON or list"),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON, dict string, or key=value pairs"
    ),
    log_level: str | None = typer.Option(
        None, help="Logging level (debug, info, warning, error, critical)"
    ),
    schedule_id: str | None = typer.Option(
        None, help="Unique identifier for the schedule"
    ),
):
    """
    Schedule a pipeline for recurring or future execution.

    This command sets up recurring or future execution of a pipeline using cron
    expressions or interval-based scheduling via the configured job queue backend.

    Args:
        name: Name of the pipeline to schedule
        base_dir: Base directory containing pipelines and configurations
        cron: Cron expression for scheduling (e.g., '0 9 * * *' for 9 AM daily)
        interval: Interval for recurring execution (duration format)
        inputs: Input parameters for the pipeline
        final_vars: Final variables to request from the pipeline
        storage_options: Options for storage backends
        log_level: Set the logging level
        schedule_id: Custom identifier for the schedule

    Examples:
        # Schedule daily at 9 AM
        $ flowerpower job-queue schedule-pipeline my_pipeline --cron "0 9 * * *"

        # Schedule every 30 minutes
        $ flowerpower job-queue schedule-pipeline my_pipeline --interval "30m"

        # Schedule with custom inputs and ID
        $ flowerpower job-queue schedule-pipeline my_pipeline --cron "0 0 * * *" \\
            --inputs '{"env": "prod"}' --schedule-id "nightly-prod"
    """
    if not cron and not interval:
        logger.error("Either --cron or --interval must be specified")
        raise typer.Exit(1)

    if cron and interval:
        logger.error("Cannot specify both --cron and --interval")
        raise typer.Exit(1)

    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    # Use FlowerPowerProject for consistency
    project = FlowerPowerProject.load(
        base_dir=base_dir,
        storage_options=parsed_storage_options or {},
        log_level=log_level,
    )

    if project is None:
        logger.error(f"Failed to load FlowerPower project from {base_dir or '.'}")
        raise typer.Exit(1)

    if project.job_queue_manager is None:
        logger.error("No job queue configured. Cannot schedule pipeline jobs.")
        raise typer.Exit(1)

    try:
        # Prepare schedule parameters
        kwargs = {}
        if cron:
            kwargs["cron"] = cron
        if interval:
            try:
                interval_seconds = duration_parser.parse(interval).total_seconds()
                kwargs["interval"] = {"seconds": interval_seconds}
            except Exception as e:
                logger.error(f"Invalid interval format '{interval}': {e}")
                raise typer.Exit(1)

        if schedule_id:
            kwargs["schedule_id"] = schedule_id
        if parsed_inputs:
            kwargs["inputs"] = parsed_inputs
        if parsed_final_vars:
            kwargs["final_vars"] = parsed_final_vars

        schedule_result = project.schedule(name, **kwargs)

        if cron:
            logger.info(
                f"Pipeline '{name}' scheduled with cron '{cron}'. Schedule ID: {schedule_result}"
            )
        elif interval:
            logger.info(
                f"Pipeline '{name}' scheduled every {interval}. Schedule ID: {schedule_result}"
            )

    except Exception as e:
        logger.error(f"Failed to schedule pipeline '{name}': {e}")
        raise typer.Exit(1)


@app.command()
def run_job(
    job_id: str = typer.Argument(..., help="ID of the job to run"),
    type: str | None = typer.Option(None, help="Type of job queue backend (rq)"),
    name: str | None = typer.Option(
        None, help="Name of the scheduler configuration to use"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory for the scheduler configuration"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON or key=value pairs"
    ),
    log_level: str = typer.Option(
        "info", help="Logging level (debug, info, warning, error, critical)"
    ),
):
    """
    Execute a specific job by its ID.

    This command runs a job that has been previously enqueued in the job queue.
    The job will be executed immediately regardless of its original schedule.

    Args:
        job_id: ID of the job to run
        type: Type of job queue backend (rq)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Run a specific job
        $ flowerpower job-queue run-job job-123456

        # Run a job with a specific backend type
        $ flowerpower job-queue run-job job-123456 --type rq

        # Run a job with debug logging
        $ flowerpower job-queue run-job job-123456 --log-level debug
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        try:
            worker.run_job(job_id)
            logger.info(f"Job '{job_id}' finished running.")
        except Exception as e:
            logger.error(f"Failed to run job '{job_id}': {e}")
            raise typer.Exit(1)


@app.command()
def list_schedules(
    type: str | None = typer.Option(None, help="Type of job queue backend (rq)"),
    name: str | None = typer.Option(
        None, help="Name of the scheduler configuration to use"
    ),
    base_dir: str | None = typer.Option(
        None, help="Base directory for the scheduler configuration"
    ),
    storage_options: str | None = typer.Option(
        None, help="Storage options as JSON or key=value pairs"
    ),
    log_level: str = typer.Option(
        "info", help="Logging level (debug, info, warning, error, critical)"
    ),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
    show_status: bool = typer.Option(
        True, help="Show schedule status (active, paused, etc.)"
    ),
    show_next_run: bool = typer.Option(True, help="Show next scheduled execution time"),
):
    """
    List all schedules with detailed status information.

    This command provides enhanced schedule listing showing trigger configuration,
    status, next run time, and execution history. This is an enhanced version of
    show-schedules with more detailed information.

    Args:
        type: Type of job queue backend (rq)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        format: Output format for the schedule information
        show_status: Include schedule status information
        show_next_run: Include next execution time information

    Examples:
        # List all schedules with full details
        $ flowerpower job-queue list-schedules

        # List schedules in JSON format
        $ flowerpower job-queue list-schedules --format json

        # List schedules without status information
        $ flowerpower job-queue list-schedules --no-show-status

        # List schedules for a specific backend
        $ flowerpower job-queue list-schedules --type rq
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with JobQueueManager(
        type=type,
        name=name,
        base_dir=base_dir,
        storage_options=parsed_storage_options,
        log_level=log_level,
    ) as worker:
        # This will use the enhanced show_schedules method with additional options
        try:
            worker.show_schedules(
                format=format,
                show_status=show_status,
                show_next_run=show_next_run,
            )
        except TypeError:
            # Fallback if the show_schedules method doesn't support new parameters
            logger.warning(
                "Using basic schedule listing (enhanced options not supported)"
            )
            worker.show_schedules(format=format)
