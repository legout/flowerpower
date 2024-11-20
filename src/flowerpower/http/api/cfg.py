from sanic import Blueprint
from sanic.response import json

bp = Blueprint("api_flowerpower_cfg", url_prefix="api/cfg")

@bp.get("/")
async def get_cfg(request) -> json:
    cfg = request.app.ctx.scheduler.cfg.to_dict()
    cfg.pop("fs")
    return json({"cfg": cfg})