import typer

from ..scheduler import SchedulerManager  # Adjust import as needed
from .utils import \
    parse_dict_or_list_param  # Assuming you have this utility function

# Create a Typer app for scheduler commands
app = typer.Typer(help="Scheduler management commands")


@app.command()
def start_worker(
    name: str | None = None,
    base_dir: str | None = None,
    background: bool = False,
    storage_options: str | None = None,
):
    """
    Start a scheduler worker.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        background: Run in background
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with SchedulerManager(
        name, base_dir, storage_options=parsed_storage_options
    ) as manager:
        manager.start_worker(background=background)


@app.command()
def remove_all_schedules(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Remove all schedules from the scheduler.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with SchedulerManager(
        name, base_dir, role="scheduler", storage_options=parsed_storage_options
    ) as manager:
        manager.remove_all_schedules()


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


@app.command()
def get_schedules(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Get all schedules from the scheduler.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with SchedulerManager(
        name, base_dir, role="scheduler", storage_options=parsed_storage_options
    ) as manager:
        schedules = manager.get_schedules()

    typer.echo("Schedules:")
    for schedule in schedules:
        typer.echo(schedule)
    return schedules


@app.command()
def get_tasks(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Get all tasks from the scheduler.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with SchedulerManager(
        name, base_dir, role="scheduler", storage_options=parsed_storage_options
    ) as manager:
        tasks = manager.get_tasks()

    typer.echo("Tasks:")
    for task in tasks:
        typer.echo(task)
    return tasks


@app.command()
def get_jobs(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Get all jobs from the scheduler.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with SchedulerManager(
        name, base_dir, role="scheduler", storage_options=parsed_storage_options
    ) as manager:
        jobs = manager.get_jobs()

    typer.echo("Jobs:")
    for job in jobs:
        typer.echo(job)
    return jobs


@app.command()
def get_job_result(
    job_id: str,
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Get the result of a specific job.

    Args:
        job_id: ID of the job
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with SchedulerManager(
        name, base_dir, role="scheduler", storage_options=parsed_storage_options
    ) as manager:
        result = manager.get_job_result(job_id)

    typer.echo("Job Result:")
    typer.echo(result)
    return result


@app.command()
def show_schedules(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Show all schedules in the scheduler.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with SchedulerManager(
        name, base_dir, role="scheduler", storage_options=parsed_storage_options
    ) as manager:
        manager.show_schedules()


@app.command()
def show_jobs(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Show all jobs in the scheduler.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with SchedulerManager(
        name, base_dir, role="scheduler", storage_options=parsed_storage_options
    ) as manager:
        manager.show_jobs()


@app.command()
def show_tasks(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: str | None = None,
):
    """
    Show all tasks in the scheduler.

    Args:
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
    """
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}

    with SchedulerManager(
        name, base_dir, role="scheduler", storage_options=parsed_storage_options
    ) as manager:
        manager.show_tasks()
