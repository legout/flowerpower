import os

from sanic import Blueprint
from sanic.exceptions import SanicException
from sanic.response import json
from sanic_ext import openapi, validate

from ...cfg import PipelineConfig

bp = Blueprint("api_flowerpower_cfg", url_prefix="api/cfg")


@bp.get("/project")
async def get_project(request) -> json:
    cfg = request.app.ctx.pipeline_manager.cfg.project.to_dict()
    # cfg.pop("fs")
    return json({"cfg": cfg})


@bp.get("/pipeline/<pipeline_name>")
async def get_pipeline(request, pipeline_name) -> json:
    if pipeline_name != request.app.ctx.pipeline_manager.cfg.pipeline.name:
        request.app.ctx.pipeline_manager.load_config(pipeline_name)
    cfg = request.app.ctx.pipeline_manager.cfg.pipeline.to_dict()
    return json({"cfg": cfg})


@bp.post("/pipeline/<pipeline_name>")
@openapi.body({"application/json": PipelineConfig}, required=True)
@validate(json=PipelineConfig)
async def update_pipeline(request, pipeline_name, body: PipelineConfig) -> json:
    data = request.json
    if pipeline_name != request.app.ctx.pipeline_manager.cfg.pipeline.name:
        request.app.ctx.pipeline_manager.load_config(pipeline_name)
    cfg = request.app.ctx.pipeline_manager.cfg.pipeline.copy()
    cfg.update(data)
    try:
        cfg.to_yaml(
            os.path.join(
                "pipelines",
                pipeline_name + ".yml",
            ),
            fs=request.app.ctx.pipeline_manager.cfg.fs,
        )
    except NotImplementedError as e:
        raise SanicException(f"Update failed. {e}", status_code=404)
    cfg
    return json({"cfg": cfg})
