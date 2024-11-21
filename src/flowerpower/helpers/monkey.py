import importlib
import sys

from dill import dumps, loads


def patch_pickle():
    """
    Patch the pickle serializer in the apscheduler module.

    This function replaces the `dumps` and `loads` functions in the `apscheduler.serializers.pickle` module
    with custom implementations.

    This is useful when you want to modify the behavior of the pickle serializer used by the apscheduler module.

    Example usage:
    patch_pickle()

    """
    sys.modules["apscheduler.serializers.pickle"].dumps = dumps
    sys.modules["apscheduler.serializers.pickle"].loads = loads


if importlib.util.find_spec("apscheduler"):
    from apscheduler._structures import Job, Schedule, Task

    def job_to_dict(job):
        return {
            "id": str(job.id),
            "task_id": job.task_id,
            "args": [str(arg) for arg in job.args],
            "kwargs": job.kwargs,
            "schedule_id": job.schedule_id,
            "scheduled_fire_time": (
                job.scheduled_fire_time.isoformat() if job.scheduled_fire_time else None
            ),
            "jitter": job.jitter.total_seconds(),
            "start_deadline": (
                job.start_deadline.isoformat() if job.start_deadline else None
            ),
            "result_expiration_time": job.result_expiration_time.total_seconds(),
            "created_at": job.created_at.isoformat(),
            "acquired_by": job.acquired_by,
            "acquired_until": (
                job.acquired_until.isoformat() if job.acquired_until else None
            ),
        }

    Job.to_dict = job_to_dict

    def task_to_dict(task):
        return {
            "id": task.id,
            "func": task.func,
            "job_executor": task.job_executor,
            "max_running_jobs": task.max_running_jobs,
            "misfire_grace_time": task.misfire_grace_time,
        }

    Task.to_dict = task_to_dict

    def schedule_to_dict(schedule):
        return {
            "id": schedule.id,
            "task_id": schedule.task_id,
            "trigger": str(schedule.trigger),
            "args": [str(arg) for arg in schedule.args],
            "kwargs": schedule.kwargs,
            "paused": schedule.paused,
            "coalesce": schedule.coalesce.name if schedule.coalesce else None,
            "misfire_grace_time": schedule.misfire_grace_time,
            "max_jitter": schedule.max_jitter,
            "next_fire_time": (
                schedule.next_fire_time.isoformat() if schedule.next_fire_time else None
            ),
            "last_fire_time": (
                schedule.last_fire_time.isoformat() if schedule.last_fire_time else None
            ),
            "acquired_by": schedule.acquired_by,
            "acquired_until": (
                schedule.acquired_until.isoformat() if schedule.acquired_until else None
            ),
        }

    Schedule.to_dict = schedule_to_dict
