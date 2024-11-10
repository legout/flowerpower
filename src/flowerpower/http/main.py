from orjson import dumps, loads
from ..scheduler import SchedulerManager
from .setup import setup
from sanic import Sanic

def create_app(args):
    # Note: args is the parsed command line arguments when the server is
    # started using sanic build-in server. e.g. 
    # sanic src.flowerpower.http.main:create_app -factory --base-dir /path/to/base_dir
    #app = setup(args.base_dir)
    print(args)
    app = Sanic("flowerpower")
    setup(app, args.base_dir)

    @app.get("/")
    async def index(request):
        return json({"status": "success", "message": "Welcome to FlowerPower"})
        
    return app
