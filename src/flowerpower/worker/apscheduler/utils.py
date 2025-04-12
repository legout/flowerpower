from operator import attrgetter
from typing import List

from rich.console import Console
from rich.table import Table


def humanize_crontab(minute, hour, day, month, day_of_week):
    days = {
        "0": "Sunday",
        "sun": "Sunday",
        "7": "Sunday",
        "1": "Monday",
        "mon": "Monday",
        "2": "Tuesday",
        "tue": "Tuesday",
        "3": "Wednesday",
        "wed": "Wednesday",
        "4": "Thursday",
        "thu": "Thursday",
        "5": "Friday",
        "fri": "Friday",
        "6": "Saturday",
        "sat": "Saturday",
        "*": "*",
    }
    months = {
        "1": "January",
        "2": "February",
        "3": "March",
        "4": "April",
        "5": "May",
        "6": "June",
        "7": "July",
        "8": "August",
        "9": "September",
        "10": "October",
        "11": "November",
        "12": "December",
        "*": "*",
    }

    def get_day_name(day_input):
        day_input = str(day_input).lower().strip()
        if "-" in day_input:
            start, end = day_input.split("-")
            return f"{days.get(start.strip(), start)}-{days.get(end.strip(), end)}"
        if "," in day_input:
            return ", ".join(
                days.get(d.strip(), d.strip()) for d in day_input.split(",")
            )
        return days.get(day_input, day_input)

    try:
        minute, hour, day, month, day_of_week = map(
            str.strip, map(str, [minute, hour, day, month, day_of_week])
        )

        if "/" in minute:
            return f"every {minute.split('/')[1]} minutes"
        if "/" in hour:
            return f"every {hour.split('/')[1]} hours"

        if all(x == "*" for x in [minute, hour, day, month, day_of_week]):
            return "every minute"
        if [minute, hour, day, month, day_of_week] == ["0", "*", "*", "*", "*"]:
            return "every hour"

        if (
            minute == "0"
            and hour != "*"
            and day == "*"
            and month == "*"
            and day_of_week == "*"
        ):
            return (
                "every day at midnight"
                if hour == "0"
                else "every day at noon"
                if hour == "12"
                else f"every day at {hour}:00"
            )

        if (
            minute == "0"
            and hour == "0"
            and day == "*"
            and month == "*"
            and day_of_week != "*"
        ):
            return f"every {get_day_name(day_of_week)} at midnight"

        if (
            minute == "0"
            and hour != "*"
            and day == "*"
            and month == "*"
            and day_of_week != "*"
        ):
            return (
                "every weekday at {hour}:00"
                if "-" in day_of_week
                and "mon" in day_of_week.lower()
                and "fri" in day_of_week.lower()
                else f"every {get_day_name(day_of_week)} at {hour}:00"
            )

        if (
            minute != "*"
            and hour != "*"
            and day == "*"
            and month == "*"
            and day_of_week == "*"
        ):
            return f"every day at {hour}:{minute.zfill(2)}"

        if day != "*" and month != "*" and minute == "0" and hour == "0":
            return f"on day {day} of {months.get(month, month)} at midnight"

        if (
            minute != "*"
            and hour == "*"
            and day == "*"
            and month == "*"
            and day_of_week == "*"
        ):
            return f"every hour at minute {minute}"

        parts = []
        if minute != "*":
            parts.append(f"at minute {minute}")
        if hour != "*":
            parts.append(f"hour {hour}")
        if day != "*":
            parts.append(f"day {day}")
        if month != "*":
            parts.append(f"month {months.get(month, month)}")
        if day_of_week != "*":
            parts.append(f"on {get_day_name(day_of_week)}")

        return f"runs {' '.join(parts)}" if parts else "every minute"
    except Exception:
        return f"{minute} {hour} {day} {month} {day_of_week}"


def format_trigger(trigger):
    trigger_type = trigger.__class__.__name__

    if trigger_type == "IntervalTrigger":
        for unit in ["seconds", "minutes", "hours", "days"]:
            if value := getattr(trigger, unit, None):
                return f"Interval: Every {value}{unit[0]}"
        return "Interval"

    if trigger_type == "CronTrigger":
        try:
            cron_parts = dict(
                part.split("=")
                for part in str(trigger).strip("CronTrigger(").rstrip(")").split(", ")
            )
            cron_parts = {k: v.strip("'") for k, v in cron_parts.items()}
            crontab = f"{cron_parts['minute']} {cron_parts['hour']} {cron_parts['day']} {cron_parts['month']} {cron_parts['day_of_week']}"
            human_readable = humanize_crontab(
                **{
                    k: cron_parts[k]
                    for k in ["minute", "hour", "day", "month", "day_of_week"]
                }
            )
            return f"Cron: {human_readable} ({crontab})"
        except Exception:
            return f"Cron: {str(trigger)}"

    if trigger_type == "DateTrigger":
        return f"Date: Once at {trigger.run_date.strftime('%Y-%m-%d %H:%M:%S')}"

    return f"{trigger_type}: {str(trigger)}"


def display_schedules(schedules: List):
    console = Console()
    total_width = console.width - 10

    width_ratios = {
        "id": 0.20,
        "task": 0.10,
        "trigger": 0.25,
        "name": 0.15,
        "run_args": 0.15,
        "next_fire": 0.08,
        "last_fire": 0.08,
        "paused": 0.01,
    }

    widths = {k: max(10, int(total_width * ratio)) for k, ratio in width_ratios.items()}

    table = Table(
        show_header=True,
        header_style="bold magenta",
        width=total_width,
        row_styles=["", "dim"],
        border_style="blue",
        show_lines=True,
    )

    for col, style, width in [
        ("ID", "dim", widths["id"]),
        ("Task", "cyan", widths["task"]),
        ("Trigger", "blue", widths["trigger"]),
        ("Name", "yellow", widths["name"]),
        ("Run Args", "yellow", widths["run_args"]),
        ("Next Fire Time", "green", widths["next_fire"]),
        ("Last Fire Time", "red", widths["last_fire"]),
        ("Paused", "bold", widths["paused"]),
    ]:
        table.add_column(col, style=style, width=width)

    for schedule in sorted(schedules, key=attrgetter("next_fire_time")):
        table.add_row(
            schedule.id,
            schedule.task_id.split(":")[-1],
            format_trigger(schedule.trigger),
            (
                str(schedule.args[1])
                if schedule.args and len(schedule.args) > 1
                else "None"
            ),
            "\n".join(f"{k}: {v}" for k, v in (schedule.kwargs or {}).items())
            or "None",
            (
                schedule.next_fire_time.strftime("%Y-%m-%d %H:%M:%S")
                if schedule.next_fire_time
                else "Never"
            ),
            (
                schedule.last_fire_time.strftime("%Y-%m-%d %H:%M:%S")
                if schedule.last_fire_time
                else "Never"
            ),
            "✓" if schedule.paused else "✗",
        )

    console.print(table)


def display_tasks(tasks):
    console = Console()
    table = Table(title="Tasks")

    widths = {"id": 50, "executor": 15, "max_jobs": 15, "misfire": 20}

    for col, style, width in [
        ("ID", "cyan", widths["id"]),
        ("Job Executor", "blue", widths["executor"]),
        ("Max Running Jobs", "yellow", widths["max_jobs"]),
        ("Misfire Grace Time", "green", widths["misfire"]),
    ]:
        table.add_column(col, style=style, width=width)

    for task in sorted(tasks, key=attrgetter("id")):
        table.add_row(
            task.id,
            str(task.job_executor),
            str(task.max_running_jobs or "None"),
            str(task.misfire_grace_time or "None"),
        )

    console.print(table)


def display_jobs(jobs):
    console = Console()
    table = Table(title="Jobs")

    widths = {
        "id": 10,
        "task_id": 40,
        "args": 20,
        "kwargs": 20,
        "schedule": 15,
        "created": 25,
        "status": 15,
    }

    for col, style, width in [
        ("ID", "cyan", widths["id"]),
        ("Task ID", "blue", widths["task_id"]),
        ("Args", "yellow", widths["args"]),
        ("Kwargs", "yellow", widths["kwargs"]),
        ("Schedule ID", "green", widths["schedule"]),
        ("Created At", "magenta", widths["created"]),
        ("Status", "red", widths["status"]),
    ]:
        table.add_column(col, style=style, width=width)

    for job in sorted(jobs, key=attrgetter("id")):
        status = "Running" if job.acquired_by else "Pending"
        table.add_row(
            str(job.id),
            job.task_id,
            str(job.args if job.args else "None"),
            (
                "\n".join(f"{k}: {v}" for k, v in job.kwargs.items())
                if job.kwargs
                else "None"
            ),
            str(job.schedule_id or "None"),
            job.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            status,
        )

    console.print(table)
