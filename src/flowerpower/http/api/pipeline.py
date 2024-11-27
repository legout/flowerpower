from sanic import Blueprint
from sanic.response import json, raw

bp = Blueprint("api_flowerpower_pipeline", url_prefix="api/pipeline")


@bp.post("add/<name>")
async def add_(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    _ = request.app.ctx.pipeline_manager.add(name=name, **kwargs)
    return json({"status": "success"})


@bp.post("/add-job/<name>")
async def add_job(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    id_ = request.app.ctx.pipeline_manager.add_job(name=name, **kwargs)
    return json({"job_id": str(id_)})


@bp.get("/all-pipelines")
async def all_pipelines(
    request,
) -> json:
    pipelines = request.app.ctx.pipeline_manager.all_pipelines(show=False)
    return json({"pipelines": pipelines})


@bp.delete("/delete/<name>")
async def delete(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    _ = request.app.ctx.pipeline_manager.delete(name, **kwargs)
    return json({"status": "success"})


@bp.post("/new/<name>")
async def new(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    _ = request.app.ctx.pipeline_manager.new(name, **kwargs)
    return json({"status": "success"})


@bp.get("/summary")
async def summary_all(
    request,
    name: str | None = None,
) -> json:
    pipeline = request.app.ctx.pipeline_manager.get_summary(name)
    return json({"pipeline": pipeline})


@bp.get("/summary/<name>")
async def summary(
    request,
    name: str | None = None,
) -> json:
    pipeline = request.app.ctx.pipeline_manager.get_summary(name)
    return json({"pipeline": pipeline})


@bp.post("/run/<name>")
async def run_(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    _ = request.app.ctx.pipeline_manager.run(name, **kwargs)
    return json({"status": "success"})


@bp.post("/run-job/<name>")
async def run_job(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    _ = request.app.ctx.pipeline_manager.run_job(name, **kwargs)
    return json({"status": "success"})


@bp.post("/schedule/<name>")
async def schedule_pipeline(request, name):
    kwargs = request.json or {}
    id_ = request.app.ctx.pipeline_manager.schedule(name, **kwargs)
    return json({"schedule_id": str(id_)})


@bp.post("/start-mqtt-listener/<name>")
async def start_mqtt_listener(request, name):
    kwargs = request.json or {}
    _ = request.app.ctx.pipeline_manager.start_mqtt_listener(name, **kwargs)
    return json({"status": "success"})


@bp.post("/stop-mqtt-listener/<name>")
async def stop_mqtt_listener(request, name):
    kwargs = request.json or {}
    _ = request.app.ctx.pipeline_manager.stop_mqtt_listener(name, **kwargs)
    return json({"status": "success"})


@bp.get("/show/<name>")
async def show(
    request,
    name: str,
) -> json:
    pipeline_dag = request.app.ctx.pipeline_manager.show_dag(name=name)
    return raw(pipeline_dag.pipe("svg"))


@bp.post("/set-abc/<value>")
async def set_abc(request, value):
    request.app.ctx.abc = value
    return json({"status": "success"})
