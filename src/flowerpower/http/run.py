from sanic import Sanic, json
from orjson import dumps, loads
from ..scheduler import SchedulerManager


def create_app(args):
    print(args)
    app = Sanic("pipeline_server", dumps=dumps, loads=loads)
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #    "--base-dir", required=True, help="Base directory for pipelines"
    # )
    # args = parser.parse_args()

    @app.listener("before_server_start")
    def init_scheduler(app, loop):
        app.ctx.scheduler = SchedulerManager(base_dir=args.base_dir)
        app.ctx.scheduler.start_worker(background=True)

    @app.listener("before_server_stop")
    def cleanup_scheduler(app, loop):
        if hasattr(app.ctx, "scheduler"):
            app.ctx.scheduler.stop_worker()

    @app.route("/test")
    async def test(request):
        return json({"hello": "world"})

    return app
