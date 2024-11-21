from orjson import dumps, loads
from sanic import Sanic
from sanic.response import json

from .setup import setup


def create_app(args):
    # Note: args is the parsed command line arguments when the server is
    # started using sanic build-in server. e.g.
    # sanic src.flowerpower.http.main:create_app -factory --base-dir /path/to/base_dir
    # app = setup(args.base_dir)
    base_dir = args.base_dir if hasattr(args, "base_dir") else None
    storage_options = (
        eval(args.storage_options) if hasattr(args, "storage_options") else {}
    )
    app = Sanic("flowerpower", dumps=dumps, loads=loads)
    setup(app=app, base_dir=base_dir, storage_options=storage_options)

    @app.get("/")
    async def index(request):
        return json({"status": "success", "message": "Welcome to FlowerPower"})

    return app
