import os

from dotenv import load_dotenv
from orjson import dumps, loads
from sanic import Sanic

# from sanic.response import json

from .setup import setup
from ..cli.utils import parse_dict_or_list_param

load_dotenv()


def create_app(args):
    # Note: args is the parsed command line arguments when the server is
    # started using sanic build-in server. e.g.
    # sanic src.flowerpower.http.main:create_app -factory --base-dir /path/to/base_dir
    # app = setup(args.base_dir)
    base_dir = (
        args.base_dir
        if hasattr(args, "base_dir") or os.getenv("FLOWERPOWER_BASE_DIR")
        else None
    )

    storage_options = (
        args.storage_options
        if hasattr(args, "storage_options") or os.getenv("FLOWERPOWER_STORAGE_OPTIONS")
        else None
    )
    storage_options = parse_dict_or_list_param(storage_options, param_type="dict") or {}

    cfg_dir = args.cfg_dir if hasattr(args, "cfg_dir") else "conf"
    pipelines_dir = (
        args.pipelines_dir if hasattr(args, "pipelines_dir") else "pipelines"
    )

    app = Sanic("flowerpower", dumps=dumps, loads=loads)
    setup(
        app=app,
        base_dir=base_dir,
        storage_options=storage_options,
        cfg_dir=cfg_dir,
        pipelines_dir=pipelines_dir,
    )

    # @app.get("/")
    # async def t2(request):
    #     print(request.args)
    #     print(request.json)
    #     return json({"status": "success", "message": "Welcome to FlowerPower"})

    # @app.post("/")
    # async def t1(request):
    #     print(request.args)
    #     print(request.args.get("name"))
    #     print(request.json)
    #     return json({"status": "success", "message": "Welcome to FlowerPower"})

    # # @app.get("/health")
    # # async def health(request):
    # #     return json({"status": "success", "message": "Healthy"})

    # @app.get("/health/<name>")
    # async def health(request, name):
    #     if name is None:
    #         return json({"status": "success", "message": "Healthy"})
    #     return json({"status": "success", "message": f"Healthy {name}"})

    return app
