from sanic import Blueprint
from sanic.response import json, raw
from sanic.exceptions import SanicException
import uuid
import dill
import pickle
import cloudpickle

bp = Blueprint("api_flowerpower_scheduler", url_prefix="api/scheduler")


# @bp.post("/start-worker")
# async def start_worker(request) -> json:
#    request.app.ctx.scheduler.start_worker(background=True)
#    id_ = request.app.ctx.scheduler.identity
#    return json({"status": f"worker {id_} started"})


# @bp.post("/stop-worker")
# async def stop_worker(request) -> json:
#    request.app.ctx.scheduler.stop_worker()
#    id_ = request.app.ctx.scheduler.identity
#    return json({"status": f"worker {id_} stopped"})


@bp.get("/status")
async def status(request) -> json:
    status = request.app.ctx.scheduler.state
    return json({"status": status.__str__()})


@bp.get("/jobs")
async def jobs(request) -> json:
    jobs = request.app.ctx.scheduler.get_jobs()
    return json({"jobs": jobs})


@bp.get("/job-result/<job_id>")
async def job_result(request, job_id) -> json:
    job_id = uuid.UUID(job_id)
    job = request.app.ctx.scheduler.get_job_result(job_id)
    return raw(dill.dumps(job))
