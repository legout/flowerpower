import posixpath

from sanic import Blueprint
from sanic.exceptions import SanicException
from sanic.response import json
from sanic_ext import openapi, validate

from ...cfg import PipelineConfig, ProjectConfig

bp = Blueprint("api_flowerpower_cfg", url_prefix="api/cfg")


@bp.get("/project")
async def get_project(request) -> json:
    cfg = request.app.ctx.pipeline_manager.cfg.project.to_dict()
    # cfg.pop("fs")
    return json({"cfg": cfg})


@bp.post("/project")
@validate(json=ProjectConfig)
async def update_project(request, body: ProjectConfig) -> json:
    cfg = request.app.ctx.pipeline_manager.cfg.copy()
    cfg.project.update(body.model_dump())
    try:
        cfg.save()
    except NotImplementedError as e:
        raise SanicException(f"Update failed. {e}", status_code=404)
    return json({"cfg": cfg})


@bp.get("/pipeline/<pipeline_name>")
async def get_pipeline(request, pipeline_name) -> json:
    if pipeline_name != request.app.ctx.pipeline_manager.cfg.pipeline.name:
        request.app.ctx.pipeline_manager.load_config(pipeline_name)
    cfg = request.app.ctx.pipeline_manager.cfg.pipeline.to_dict()
    return json({"cfg": cfg})


@bp.post("/pipeline/<pipeline_name>")
@validate(json=PipelineConfig)
async def update_pipeline(request, pipeline_name, body: PipelineConfig) -> json:
    if pipeline_name != request.app.ctx.pipeline_manager.cfg.pipeline.name:
        request.app.ctx.pipeline_manager.load_config(pipeline_name)
    cfg = request.app.ctx.pipeline_manager.cfg.copy()
    cfg.pipeline.update(body.model_dump())
    try:
        cfg.save()
    except NotImplementedError as e:
        raise SanicException(f"Update failed. {e}", status_code=404)

    return json({"cfg": cfg})
