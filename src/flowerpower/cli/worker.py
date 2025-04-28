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
    Start a worker.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        background: Run in background
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if num_workers:
            num_workers = worker.cfg.backend.num_workers

        if num_workers>1:
            worker.start_worker_pool(
                num_workers=num_workers,background=background
            )
        else:
            worker.start_worker(
                background=background
            )

@app.command()
def start_scheduler(
    name: str | None = None,
    base_dir: str | None = None,
    background: bool = False,
    storage_options: str | None = None,
    log_level: str = "info",
    interval: int = 60,
):
    """
    Start the scheduler. 
    
    Note: This is only needed for RQ workers.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        background: Run in background
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        interval: Interval for the scheduler in seconds
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if worker.cfg.backend.type != "rq":
            setup_logging(log_level="info")
            logger.info(f"No scheduler needed for {worker.cfg.backend.type} workers. Skipping.")
            setup_logging(log_level=log_level)
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
    Remove all schedules from the scheduler.

    Args:
        queue_name: Name of the queue 
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}
    

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        if worker.cfg.backend.type != "rq":
            setup_logging(log_level="info")
            logger.info(f"Job cancellation is not supported for {worker.cfg.backend.type} workers. Skipping.")
            setup_logging(log_level=log_level)
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
    Remove all schedules from the scheduler.

    Args:
        queue_name: Name of the queue 
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
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

    Args:
        job_id: ID of the job to cancel
        type: Type of the worker
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
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

    Args:
        schedule_id: ID of the schedule to cancel
        type: Type of the worker
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with Worker(
        type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
    ) as worker:
        worker.cancel_schedule(schedule_id)

