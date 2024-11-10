from sanic import Sanic
from .api import bp
from ..scheduler import SchedulerManager

def setup(app:Sanic, base_dir:str):

    #app = Sanic("flowerpower")
    app.config.BASE_DIR = base_dir

    @app.listener("before_server_start")
    def init_scheduler(app, loop):
        app.ctx.scheduler = SchedulerManager(base_dir=base_dir)
        app.ctx.scheduler.start_worker(background=True)


    @app.listener("before_server_stop")
    def cleanup_scheduler(app, loop):
        if hasattr(app.ctx, "scheduler"):
            app.ctx.scheduler.stop_worker()

    app.blueprint(bp)

    return app