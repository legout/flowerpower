import typer
from .. import settings
from ..worker import Worker  # Adjust import as needed
from .utils import  parse_dict_or_list_param 
from ..utils.logging import setup_logging
from loguru import logger

# Create a Typer app for scheduler commands
app = typer.Typer(help="Scheduler management commands")

setup_logging(
    log_level=settings.LOG_LEVEL)

@app.command()
def start_worker(
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    background: bool = False,
    storage_options: str | None = None,
    log_level: str = "info",
    num_workers: int | None = None,
):
    """
    Start a worker or worker pool.

    Args:
        type: Type of the worker (rq, apscheduler)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        background: Run in background
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        num_workers: Number of worker processes to start. If > 1, starts a worker pool
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if num_workers:
            num_workers = worker.cfg.backend.num_workers

        if num_workers and num_workers > 1:
            worker.start_worker_pool(
                num_workers=num_workers, background=background
            )
        else:
            worker.start_worker(
                background=background
            )

@app.command()
def start_scheduler(
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    background: bool = False,
    storage_options: str | None = None,
    log_level: str = "info",
    interval: int = 60,
):
    """
    Start the scheduler. 
    
    Note: This is only needed for RQ workers. APScheduler workers have their own built-in scheduler.

    Args:
        type: Type of the worker (rq, apscheduler)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        background: Run in background
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        interval: Interval for the scheduler in seconds (RQ only)
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if worker.cfg.backend.type != "rq":
            logger.info(f"No scheduler needed for {worker.cfg.backend.type} workers. Skipping.")
            return
        
        worker.start_scheduler(background=background, interval=interval)


@app.command()
def cancel_all_jobs(
    type: str | None = None,
    queue_name: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Cancel all jobs from the scheduler.

    Note: This is different from deleting jobs as it only stops them from running but keeps their history.

    Args:
        type: Type of the worker (rq, apscheduler)
        queue_name: Name of the queue (RQ only)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if worker.cfg.backend.type != "rq":
            logger.info(f"Job cancellation is not supported for {worker.cfg.backend.type} workers. Skipping.")
            return
        
        worker.cancel_all_jobs(queue_name=queue_name)

@app.command()
def cancel_all_schedules(
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Cancel all schedules from the scheduler.

    Note: This is different from deleting schedules as it only stops them from running but keeps their configuration.

    Args:
        type: Type of the worker (rq, apscheduler)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.cancel_all_schedules()

@app.command()
def cancel_job(
    job_id: str,
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Cancel a specific job.

    Note: This is different from deleting a job as it only stops it from running but keeps its history.

    Args:
        job_id: ID of the job to cancel
        type: Type of the worker (rq, apscheduler)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if worker.cfg.backend.type != "rq":
            logger.info(f"Job cancellation is not supported for {worker.cfg.backend.type} workers. Skipping.")
            return
            
        worker.cancel_job(job_id)

@app.command()
def cancel_schedule(
    schedule_id: str,
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
        type: Type of the worker (rq, apscheduler)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.cancel_schedule(schedule_id)

@app.command()
def delete_all_jobs(
    type: str | None = None,
    queue_name: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Delete all jobs from the scheduler. Note that this is different from cancelling jobs
    as it also removes job history and results.

    Args:
        queue_name: Name of the queue (RQ only)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.delete_all_jobs(queue_name=queue_name if worker.cfg.backend.type == "rq" else None)

@app.command()
def delete_all_schedules(
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Delete all schedules from the scheduler.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.delete_all_schedules()

@app.command()
def delete_job(
    job_id: str,
    type: str | None = None,
    queue_name: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Delete a specific job.

    Args:
        job_id: ID of the job to delete
        queue_name: Name of the queue (RQ only)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.delete_job(job_id)

@app.command()
def delete_schedule(
    schedule_id: str,
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
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.delete_schedule(schedule_id)

@app.command()
def get_job(
    job_id: str,
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Get information about a specific job.

    Args:
        job_id: ID of the job
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        # show_jobs should display the job info
        worker.show_jobs(job_id=job_id)

@app.command()
def get_job_result(
    job_id: str,
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
    wait: bool = True,
):
    """
    Get the result of a specific job.

    Args:
        job_id: ID of the job
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
        wait: Wait for the result if job is still running (APScheduler only)
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        # worker's get_job_result method will handle the result display
        worker.get_job_result(job_id, wait=wait if worker.cfg.backend.type == "apscheduler" else False)

@app.command()
def get_jobs(
    type: str | None = None,
    queue_name: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    List all jobs.

    Args:
        queue_name: Name of the queue (RQ only)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.show_jobs()

@app.command()
def get_schedule(
    schedule_id: str,
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Get information about a specific schedule.

    Args:
        schedule_id: ID of the schedule
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        # show_schedule should display the schedule info
        worker.show_schedules(schedule_id=schedule_id)

@app.command()
def get_schedules(
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    List all schedules.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.show_schedules()

@app.command()
def show_job_ids(
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Show all job IDs.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        # worker's get_job_ids method will print the IDs
        worker.job_ids

@app.command()
def show_schedule_ids(
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Show all schedule IDs.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        # worker's get_schedule_ids method will print the IDs
        worker.schedule_ids

@app.command()
def pause_all_schedules(
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Pause all schedules.

    Note: This functionality is only available for APScheduler workers.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if worker.cfg.backend.type != "apscheduler":
            logger.info(f"Schedule pausing is not supported for {worker.cfg.backend.type} workers.")
            return
        worker.pause_all_schedules()

@app.command()
def pause_schedule(
    schedule_id: str,
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Pause a specific schedule.

    Note: This functionality is only available for APScheduler workers.

    Args:
        schedule_id: ID of the schedule to pause
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if worker.cfg.backend.type != "apscheduler":
            logger.info(f"Schedule pausing is not supported for {worker.cfg.backend.type} workers.")
            return
        worker.pause_schedule(schedule_id)

@app.command()
def resume_all_schedules(
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Resume all paused schedules.

    Note: This functionality is only available for APScheduler workers.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if worker.cfg.backend.type != "apscheduler":
            logger.info(f"Schedule resuming is not supported for {worker.cfg.backend.type} workers.")
            return
        worker.resume_all_schedules()

@app.command()
def resume_schedule(
    schedule_id: str,
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Resume a specific paused schedule.

    Note: This functionality is only available for APScheduler workers.

    Args:
        schedule_id: ID of the schedule to resume
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if worker.cfg.backend.type != "apscheduler":
            logger.info(f"Schedule resuming is not supported for {worker.cfg.backend.type} workers.")
            return
        worker.resume_schedule(schedule_id)

@app.command()
def show_jobs(
    type: str | None = None,
    queue_name: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Display all jobs in a user-friendly format.

    Args:
        queue_name: Name of the queue (RQ only)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.show_jobs()

@app.command()
def show_schedules(
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
):
    """
    Display all schedules in a user-friendly format.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.show_schedules()

@app.command()
def run_job(
    func_name: str,
    type: str | None = None,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
    log_level: str = "info",
    args: str | None = None,
    kwargs: str | None = None,
    queue_name: str | None = None,
):
    """
    Run a job immediately and wait for its result.

    Args:
        func_name: Fully qualified name of the function to run (e.g., "module.submodule.function")
        args: JSON-formatted list of positional arguments
        kwargs: JSON-formatted dictionary of keyword arguments
        queue_name: Name of the queue (RQ only)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
    import importlib
    import json

    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}
    
    # Parse function arguments
    func_args = json.loads(args) if args else ()
    func_kwargs = json.loads(kwargs) if kwargs else {}

    # Import the function
    module_path, func_name = func_name.rsplit('.', 1)
    module = importlib.import_module(module_path)
    func = getattr(module, func_name)

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        # worker's run_job method will handle the result display
        worker.run_job(
            func=func,
            func_args=func_args,
            func_kwargs=func_kwargs,
            job_executor=queue_name if worker.cfg.backend.type == "apscheduler" else None,
        )

