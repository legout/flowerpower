from sanic import Sanic

from ..scheduler import SchedulerManager
from .api.cfg import bp as bp_api_cfg
from .api.pipeline import bp as bp_api_pipeline
from .api.scheduler import bp as bp_api_scheduler


def setup(
    app: Sanic,
    base_dir: str | None = None,
    storage_options: dict | None = None,
    cfg_dir: str = "conf",
    pipelines_dir: str = "pipelines",
) -> Sanic:

    app.config.BASE_DIR = base_dir
    app.config.STORAGE_OPTIONS = storage_options
    app.config.CFG_DIR = cfg_dir
    app.config.PIPELINES_DIR = pipelines_dir

    @app.listener("before_server_start")
    def init_scheduler(app, loop):

        app.ctx.scheduler = SchedulerManager(
            base_dir=base_dir, storage_options=storage_options
        )
        app.ctx.scheduler.start_worker(background=True)

    @app.listener("before_server_stop")
    def cleanup_scheduler(app, loop):
        if hasattr(app.ctx, "scheduler"):
            app.ctx.scheduler.stop_worker()

    app.blueprint(bp_api_pipeline)
    app.blueprint(bp_api_scheduler)
    app.blueprint(bp_api_cfg)

    return app
