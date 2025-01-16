import uuid

import dill
from sanic import Blueprint
from sanic.exceptions import SanicException
from sanic.response import json, raw
from sanic_ext import openapi

from ..models.scheduler import (
    SchedulerAdd,
    SchedulerModify,
    SchedulerDelete,
    SchedulerList,
    SchedulerInfo,
)
from ..utils import deserialize_and_validate

bp = Blueprint("api_flowerpower_scheduler", url_prefix="api/scheduler")


@bp.get("/status")
@openapi.summary("Get scheduler status")
@openapi.description("Get the current status of the scheduler")
@openapi.response(200, {"application/json": dict})
async def status(request) -> json:
    try:
        status = request.app.ctx.scheduler.state
        return json({"status": status.__str__()})
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/jobs")
@openapi.summary("List all jobs")
@openapi.description("Get a list of all scheduled jobs")
@openapi.response(200, {"application/json": dict})
async def jobs(request) -> json:
    try:
        jobs = request.app.ctx.scheduler.get_jobs(as_dict=True)
        return json({"jobs": jobs})
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/job-result/<job_id>")
@openapi.summary("Get job result")
@openapi.description("Get the result of a specific job by ID")
@openapi.parameter("job_id", str, required=True)
@openapi.response(200, {"application/octet-stream": bytes})
@openapi.response(404, {"application/json": dict})
async def job_result(request, job_id: str) -> raw:
    try:
        job_id = uuid.UUID(job_id)
        if job_id not in [job.id for job in request.app.ctx.scheduler.get_jobs()]:
            raise SanicException("Job not found", status_code=404)
        job = request.app.ctx.scheduler.get_job_result(job_id)
        return raw(dill.dumps(job))
    except ValueError:
        raise SanicException("Invalid job ID format", status_code=400)
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/schedules")
@openapi.summary("List all schedules")
@openapi.description("Get a list of all pipeline schedules")
@openapi.body({"application/json": SchedulerList}, required=False)
@openapi.response(200, {"application/json": dict})
async def schedules(request) -> json:
    try:
        body = await deserialize_and_validate(SchedulerList, query=request.args)
        schedules = request.app.ctx.scheduler.get_schedules(
            pattern=body.pattern, as_dict=True
        )
        return json({"schedules": schedules})
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/schedule/<schedule_id>")
@openapi.summary("Get schedule details")
@openapi.description("Get details of a specific schedule by ID")
@openapi.parameter("schedule_id", str, required=True)
@openapi.body({"application/json": SchedulerInfo}, required=False)
@openapi.response(200, {"application/json": dict})
@openapi.response(404, {"application/json": dict})
async def schedule(request, schedule_id: str) -> json:
    try:
        # body = await deserialize_and_validate(SchedulerInfo, body=request.json)
        if schedule_id not in [s.id for s in request.app.ctx.scheduler.get_schedules()]:
            raise SanicException("Schedule not found", status_code=404)
        schedule = request.app.ctx.scheduler.get_schedule(schedule_id, as_dict=True)
        return json(schedule)
    except Exception as e:
        raise SanicException(str(e))


@bp.post("/schedule")
@openapi.summary("Add new schedule")
@openapi.description("Create a new pipeline schedule")
@openapi.body({"application/json": SchedulerAdd}, required=True)
@openapi.response(200, {"application/json": dict})
async def add_schedule(request) -> json:
    try:
        body = await deserialize_and_validate(SchedulerAdd, body=request.json)
        schedule_id = request.app.ctx.scheduler.add_schedule(**body.model_dump())
        return json({"schedule_id": str(schedule_id)})
    except Exception as e:
        raise SanicException(str(e))


@bp.patch("/schedule/<schedule_id>")
@openapi.summary("Modify schedule")
@openapi.description("Modify an existing pipeline schedule")
@openapi.parameter("schedule_id", str, required=True)
@openapi.body({"application/json": SchedulerModify}, required=True)
@openapi.response(200, {"application/json": dict})
@openapi.response(404, {"application/json": dict})
async def modify_schedule(request, schedule_id: str) -> json:
    try:
        if schedule_id not in [s.id for s in request.app.ctx.scheduler.get_schedules()]:
            raise SanicException("Schedule not found", status_code=404)

        body = await deserialize_and_validate(SchedulerModify, body=request.json)
        request.app.ctx.scheduler.modify_schedule(schedule_id, **body.model_dump())
        return json({"status": "success"})
    except Exception as e:
        raise SanicException(str(e))


@bp.delete("/schedule/<schedule_id>")
@openapi.summary("Delete schedule")
@openapi.description("Delete a pipeline schedule")
@openapi.parameter("schedule_id", str, required=True)
@openapi.body({"application/json": SchedulerDelete}, required=False)
@openapi.response(200, {"application/json": dict})
@openapi.response(404, {"application/json": dict})
async def remove_schedule(request, schedule_id: str) -> json:
    try:
        # body = await deserialize_and_validate(SchedulerDelete, body=request.json)
        if schedule_id not in [s.id for s in request.app.ctx.scheduler.get_schedules()]:
            raise SanicException("Schedule not found", status_code=404)
        request.app.ctx.scheduler.remove_schedule(schedule_id)
        return json({"status": "success"})
    except Exception as e:
        raise SanicException(str(e))


@bp.delete("/schedules")
@openapi.summary("Delete all schedules")
@openapi.description("Delete all pipeline schedules")
@openapi.response(200, {"application/json": dict})
async def remove_schedules(request) -> json:
    try:
        request.app.ctx.scheduler.remove_all_schedules()
        return json({"status": "success"})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("/pause-schedule/<schedule_id>")
@openapi.summary("Pause schedule")
@openapi.description("Pause a pipeline schedule")
@openapi.parameter("schedule_id", str, required=True)
@openapi.response(200, {"application/json": dict})
@openapi.response(404, {"application/json": dict})
async def pause_schedule(request, schedule_id: str) -> json:
    try:
        if schedule_id not in [s.id for s in request.app.ctx.scheduler.get_schedules()]:
            raise SanicException("Schedule not found", status_code=404)
        request.app.ctx.scheduler.pause_schedule(schedule_id)
        return json({"status": "success"})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("/resume-schedule/<schedule_id>")
@openapi.summary("Resume schedule")
@openapi.description("Resume a paused pipeline schedule")
@openapi.parameter("schedule_id", str, required=True)
@openapi.response(200, {"application/json": dict})
@openapi.response(404, {"application/json": dict})
async def resume_schedule(request, schedule_id: str) -> json:
    try:
        if schedule_id not in [s.id for s in request.app.ctx.scheduler.get_schedules()]:
            raise SanicException("Schedule not found", status_code=404)
        request.app.ctx.scheduler.resume_schedule(schedule_id)
        return json({"status": "success"})
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/tasks")
@openapi.summary("List all tasks")
@openapi.description("Get a list of all tasks")
@openapi.response(200, {"application/json": dict})
async def tasks(request) -> json:
    try:
        tasks = request.app.ctx.scheduler.get_tasks(as_dict=True)
        return json({"tasks": tasks})
    except Exception as e:
        raise SanicException(str(e))
