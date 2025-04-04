import typer

# Removed SchedulerManager import
import datetime as dt
from pathlib import Path
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from rq import Queue, Worker, registry
from rq.job import Job
from rq.exceptions import NoSuchJobError
from rq_scheduler import Scheduler as RQScheduler

from .utils import parse_dict_or_list_param
from ..cfg import Config # For loading config
from ..fs import get_filesystem # For config loading
from loguru import logger
import rich # For better output formatting
from rich.table import Table
from rich.console import Console

# Create a Typer app for scheduler commands
app = typer.Typer(help="RQ Job and Schedule management commands")

# --- Helper Function ---

def _get_rq_components(base_dir: str | None = None) -> tuple[Redis | None, Queue | None, RQScheduler | None, Config | None]:
    """Loads config and initializes Redis, RQ Queue, and RQ Scheduler."""
    try:
        base_path = base_dir or str(Path.cwd())
        fs = get_filesystem(base_path, cached=True, dirfs=True) # Assuming local fs for CLI context
        cfg = Config.load(base_dir=base_path, fs=fs)

        redis_url = cfg.project.worker.redis_url
        default_queue_name = cfg.project.worker.default_queue

        redis_conn = Redis.from_url(redis_url, decode_responses=True) # Decode for easier handling
        redis_conn.ping()
        queue = Queue(default_queue_name, connection=redis_conn)
        scheduler = RQScheduler(queue_name=default_queue_name, connection=redis_conn)
        logger.info(f"Connected to Redis at {redis_url}")
        return redis_conn, queue, scheduler, cfg
    except RedisConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        rich.print(f"[bold red]Error:[/bold red] Could not connect to Redis at [yellow]{redis_url}[/yellow]. Check connection details and if Redis is running.")
        return None, None, None, None
    except FileNotFoundError:
         logger.error(f"Configuration file not found in {base_path}/conf. Is this a FlowerPower project directory?")
         rich.print(f"[bold red]Error:[/bold red] Configuration not found in [yellow]{base_path}/conf[/yellow].")
         return None, None, None, None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during RQ setup: {e}")
        rich.print(f"[bold red]Error:[/bold red] An unexpected error occurred: {e}")
        return None, None, None, None


# Removed start_worker command (RQ workers started externally)
# Removed remove_all_schedules command (can be done via Redis/RQ directly if needed)


# @app.command()
# def add_schedule(
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     trigger_type: str = "cron",
#     **kwargs,
# ) -> str:
#     """
#     Add a schedule to the scheduler.

#     Args:
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         trigger_type: Type of trigger (cron, interval, etc.)
#         **kwargs: Additional schedule parameters
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with SchedulerManager(name, base_dir, role="scheduler") as manager:
#         schedule_id = manager.add_schedule(
#             storage_options=parsed_storage_options, type=trigger_type, **kwargs
#         )

#     typer.echo(f"Schedule added with ID: {schedule_id}")
#     return schedule_id


# @app.command()
# def add_job(
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     **kwargs,
# ) -> str:
#     """
#     Add a job to the scheduler.

#     Args:
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         **kwargs: Job parameters
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with SchedulerManager(name, base_dir, role="scheduler") as manager:
#         job_id = manager.add_job(storage_options=parsed_storage_options, **kwargs)

#     typer.echo(f"Job added with ID: {job_id}")
#     return str(job_id)


# @app.command()
# def run_job(
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     **kwargs,
# ):
#     """
#     Run a job and return its result.

#     Args:
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         **kwargs: Job parameters
#     """
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

#     with SchedulerManager(name, base_dir, role="scheduler") as manager:
#         result = manager.run_job(storage_options=parsed_storage_options, **kwargs)

#     typer.echo("Job result:")
#     typer.echo(result)
#     return result


@app.command(name="list-scheduled")
def get_scheduled_jobs(
    base_dir: str = typer.Option(None, "--base-dir", "-d", help="Project base directory (defaults to current dir)."),
    raw: bool = typer.Option(False, "--raw", help="Output raw job data."),
):
    """
    List jobs currently scheduled in RQ-Scheduler.
    """
    redis_conn, queue, scheduler, cfg = _get_rq_components(base_dir)
    if not scheduler:
        return # Error handled in helper

    try:
        scheduled_jobs = scheduler.get_jobs(with_times=True) # Get jobs and their scheduled times
    except Exception as e:
        logger.error(f"Failed to get scheduled jobs from RQ-Scheduler: {e}")
        rich.print(f"[bold red]Error:[/bold red] Could not retrieve scheduled jobs.")
        return

    if not scheduled_jobs:
        rich.print("[yellow]No jobs currently scheduled.[/yellow]")
        return

    if raw:
        console = Console()
        console.print(scheduled_jobs)
        return

    table = Table(title="Scheduled Jobs (RQ-Scheduler)", show_header=True, header_style="bold cyan")
    table.add_column("Scheduled Time (UTC)", style="green")
    table.add_column("Job ID", style="blue")
    table.add_column("Target Function", style="magenta")
    table.add_column("Queue", style="yellow")
    table.add_column("Interval/Cron", style="dim")
    table.add_column("Description")


    for job, scheduled_time in scheduled_jobs:
        # Attempt to extract interval/cron info if available (stored in meta)
        interval = job.meta.get('interval', None)
        cron = job.meta.get('cron_string', None)
        schedule_info = ""
        if interval:
            schedule_info = f"Interval: {interval}s"
        elif cron:
            schedule_info = f"Cron: {cron}"

        table.add_row(
            scheduled_time.strftime('%Y-%m-%d %H:%M:%S'),
            job.id,
            job.func_name or str(job.func),
            job.origin, # Queue name
            schedule_info,
            job.description or ""
        )

    console = Console()
    console.print(table)


# Removed get_tasks command (no direct RQ equivalent)


@app.command(name="list-jobs")
def get_jobs_in_queue(
    base_dir: str = typer.Option(None, "--base-dir", "-d", help="Project base directory (defaults to current dir)."),
    queue_name: str = typer.Option(None, "--queue", "-q", help="Specific queue name (defaults to configured default)."),
    status: str = typer.Option("queued", "--status", "-s", help="Job status filter (queued, started, finished, failed)."),
    raw: bool = typer.Option(False, "--raw", help="Output raw job data."),
    limit: int = typer.Option(50, "--limit", "-n", help="Maximum number of jobs to list."),
):
    """
    List jobs in a specific RQ queue or registry.
    """
    redis_conn, default_queue, scheduler, cfg = _get_rq_components(base_dir)
    if not redis_conn:
        return # Error handled in helper

    target_queue_name = queue_name or (default_queue.name if default_queue else 'default')
    target_queue = Queue(target_queue_name, connection=redis_conn)

    job_ids = []
    registry_instance = None
    title = f"Jobs in Queue '{target_queue_name}'"

    try:
        if status == "queued":
            job_ids = target_queue.get_job_ids(offset=0, length=limit)
            title = f"Queued Jobs in '{target_queue_name}'"
        elif status == "started":
            registry_instance = registry.StartedJobRegistry(name=target_queue_name, connection=redis_conn)
            title = f"Started Jobs from '{target_queue_name}'"
        elif status == "finished":
            registry_instance = registry.FinishedJobRegistry(name=target_queue_name, connection=redis_conn)
            title = f"Finished Jobs from '{target_queue_name}'"
        elif status == "failed":
            registry_instance = registry.FailedJobRegistry(name=target_queue_name, connection=redis_conn)
            title = f"Failed Jobs from '{target_queue_name}'"
        else:
            rich.print(f"[bold red]Error:[/bold red] Invalid status '{status}'. Choose from: queued, started, finished, failed.")
            return

        if registry_instance:
            job_ids = registry_instance.get_job_ids(offset=0, length=limit)

    except Exception as e:
        logger.error(f"Failed to get job IDs for status '{status}' from queue '{target_queue_name}': {e}")
        rich.print(f"[bold red]Error:[/bold red] Could not retrieve job IDs.")
        return

    if not job_ids:
        rich.print(f"[yellow]No {status} jobs found in queue '{target_queue_name}'.[/yellow]")
        return

    try:
        jobs = Job.fetch_many(job_ids, connection=redis_conn)
    except Exception as e:
        logger.error(f"Failed to fetch job details: {e}")
        rich.print(f"[bold red]Error:[/bold red] Could not fetch job details.")
        return

    if raw:
        console = Console()
        console.print([job.to_dict() for job in jobs if job])
        return

    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Job ID", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Created", style="dim")
    table.add_column("Enqueued", style="dim")
    table.add_column("Started", style="dim")
    table.add_column("Ended", style="dim")
    table.add_column("Function", style="magenta")
    table.add_column("Description")
    table.add_column("Exc Info", style="red")


    for job in jobs:
        if not job: continue # Handle potential fetch issues for individual jobs
        status_str = job.get_status()
        table.add_row(
            job.id,
            status_str,
            job.created_at.strftime('%Y-%m-%d %H:%M:%S') if job.created_at else "-",
            job.enqueued_at.strftime('%Y-%m-%d %H:%M:%S') if job.enqueued_at else "-",
            job.started_at.strftime('%Y-%m-%d %H:%M:%S') if job.started_at else "-",
            job.ended_at.strftime('%Y-%m-%d %H:%M:%S') if job.ended_at else "-",
            job.func_name or str(job.func),
            job.description or "",
            job.exc_info if status_str == 'failed' else ""
        )

    console = Console()
    console.print(table)


@app.command(name="job-info")
def get_job_info(
    job_id: str = typer.Argument(..., help="The ID of the RQ job."),
    base_dir: str = typer.Option(None, "--base-dir", "-d", help="Project base directory (defaults to current dir)."),
):
    """
    Get detailed information and result (if available) for a specific RQ job.
    """
    redis_conn, _, _, _ = _get_rq_components(base_dir) # Only need redis connection
    if not redis_conn:
        return # Error handled in helper

    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except NoSuchJobError:
        rich.print(f"[bold red]Error:[/bold red] Job with ID '{job_id}' not found.")
        return
    except Exception as e:
        logger.error(f"Failed to fetch job {job_id}: {e}")
        rich.print(f"[bold red]Error:[/bold red] Could not fetch job details.")
        return

    console = Console()
    table = Table(title=f"Job Details: {job.id}", show_header=False, box=rich.box.SIMPLE)
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    table.add_row("Job ID", job.id)
    table.add_row("Status", job.get_status())
    table.add_row("Queue", job.origin)
    table.add_row("Function", job.func_name or str(job.func))
    table.add_row("Description", job.description or "-")
    table.add_row("Created At", str(job.created_at) if job.created_at else "-")
    table.add_row("Enqueued At", str(job.enqueued_at) if job.enqueued_at else "-")
    table.add_row("Started At", str(job.started_at) if job.started_at else "-")
    table.add_row("Ended At", str(job.ended_at) if job.ended_at else "-")
    table.add_row("Result TTL", str(job.result_ttl) if job.result_ttl is not None else "-")
    table.add_row("Job Timeout", str(job.timeout) if job.timeout is not None else "-")
    table.add_row("Worker Name", job.worker_name or "-")

    console.print(table)

    if job.is_finished:
        rich.print("\n[bold green]Result:[/bold green]")
        console.print(job.result)
    elif job.is_failed:
        rich.print("\n[bold red]Failure Traceback:[/bold red]")
        console.print(job.exc_info or "No exception info available.")

    # Optionally return the job object or its dict representation
    # return job.to_dict()


@app.command(name="show-scheduled")
def show_scheduled_jobs_command(
    base_dir: str = typer.Option(None, "--base-dir", "-d", help="Project base directory (defaults to current dir)."),
):
    """
    Show currently scheduled jobs (calls list-scheduled).
    """
    # Simply call the refactored list command's implementation
    get_scheduled_jobs(base_dir=base_dir, raw=False)


@app.command(name="show-jobs")
def show_jobs_command(
    base_dir: str = typer.Option(None, "--base-dir", "-d", help="Project base directory (defaults to current dir)."),
    queue_name: str = typer.Option(None, "--queue", "-q", help="Specific queue name (defaults to configured default)."),
    status: str = typer.Option("queued", "--status", "-s", help="Job status filter (queued, started, finished, failed)."),
    limit: int = typer.Option(50, "--limit", "-n", help="Maximum number of jobs to show."),
):
    """
    Show jobs in a specific RQ queue or registry (calls list-jobs).
    """
    # Simply call the refactored list command's implementation
    get_jobs_in_queue(
        base_dir=base_dir,
        queue_name=queue_name,
        status=status,
        raw=False,
        limit=limit
    )


# Removed show_tasks command (no direct RQ equivalent)
