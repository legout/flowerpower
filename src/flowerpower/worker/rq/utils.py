from rich.console import Console
from rich.table import Table
from rq import Queue
from rq_scheduler import Scheduler


def show_schedules(scheduler: Scheduler) -> None:
    """
    Display the schedules in a user-friendly format.

    Args:
        scheduler (Scheduler): An instance of rq_scheduler.Scheduler.
    """
    console = Console()
    table = Table(title="Scheduled Jobs")

    table.add_column("ID", style="cyan")
    table.add_column("Function", style="green")
    table.add_column("Schedule", style="yellow")
    table.add_column("Next Run", style="magenta")

    for job in scheduler.get_jobs():
        # Determine schedule type and format
        schedule_type = "Unknown"
        if hasattr(job, "meta"):
            if job.meta.get("cron"):
                schedule_type = f"Cron: {job.meta['cron']}"
            elif job.meta.get("interval"):
                schedule_type = f"Interval: {job.meta['interval']}s"

        next_run = (
            job.scheduled_at.strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(job, "scheduled_at") and job.scheduled_at
            else "Unknown"
        )

        table.add_row(job.id, job.func_name, schedule_type, next_run)

    console.print(table)


def show_jobs(queue: Queue) -> None:
    """
    Display the jobs in a user-friendly format.

    Args:
        queue (Queue): An instance of rq.Queue.
    """
    console = Console()
    table = Table(title="Jobs")

    table.add_column("ID", style="cyan")
    table.add_column("Function", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Enqueued At", style="magenta")
    table.add_column("Result", style="blue")

    for job in queue.get_jobs():
        table.add_row(
            job.id,
            job.func_name,
            job.get_status(),
            job.enqueued_at.strftime("%Y-%m-%d %H:%M:%S")
            if job.enqueued_at
            else "Unknown",
            str(job.result) if job.result else "None",
        )

    console.print(table)
