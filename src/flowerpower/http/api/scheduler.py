import uuid

import dill
from sanic import Blueprint
from sanic.exceptions import SanicException
from sanic.response import json, raw

bp = Blueprint("api_flowerpower_scheduler", url_prefix="api/scheduler")


@bp.get("/status")
async def status(request) -> json:
    status = request.app.ctx.scheduler.state
    return json({"status": status.__str__()})


@bp.get("/jobs")
async def jobs(request) -> json:
    jobs = request.app.ctx.scheduler.get_jobs(as_dict=True)
    return json({"jobs": jobs})


@bp.get("/job-result/<job_id>")
async def job_result(request, job_id) -> raw:
    job_id = uuid.UUID(job_id)
    if job_id not in [job.id for job in request.app.ctx.scheduler.get_jobs()]:
        raise SanicException("Job not found", status_code=404)
    job = request.app.ctx.scheduler.get_job_result(job_id)
    return raw(dill.dumps(job))


@bp.get("/schedules")
async def schedules(request) -> json:
    schedules = request.app.ctx.scheduler.get_schedules(as_dict=True)
    return json({"schedules": schedules})


@bp.get("/schedule/<schedule_id>")
async def schedule(request, schedule_id) -> json:
    if schedule_id not in [
        sched.id for sched in request.app.ctx.scheduler.get_schedules()
    ]:
        raise SanicException("Schedule not found", status_code=404)
    schedule = request.app.ctx.scheduler.get_schedule(schedule_id, as_dict=True)
    return json(schedule)


@bp.delete("/schedule/<schedule_id>")
async def remove_schedule(request, schedule_id) -> json:
    if schedule_id not in [
        sched.id for sched in request.app.ctx.scheduler.get_schedules()
    ]:
        raise SanicException("Schedule not found", status_code=404)
    request.app.ctx.scheduler.remove_schedule(schedule_id)
    return json({"status": "success"})


@bp.delete("/schedules")
async def remove_schedules(request) -> json:
    request.app.ctx.scheduler.remove_all_schedules()
    return json({"status": "success"})


@bp.post("/pause-schedule/<schedule_id>")
async def pause_schedule(request, schedule_id) -> json:
    if schedule_id not in [
        sched.id for sched in request.app.ctx.scheduler.get_schedules()
    ]:
        raise SanicException("Schedule not found", status_code=404)
    request.app.ctx.scheduler.pause_schedule(schedule_id)
    return json({"status": "success"})


@bp.get("/tasks")
async def tasks(request) -> json:
    tasks = request.app.ctx.scheduler.get_tasks(as_dict=True)
    return json({"tasks": tasks})
