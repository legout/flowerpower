import datetime as dt
import os
from pathlib import Path

from anyio import Path

from .cfg import Config
from .pipeline import Pipeline, PipelineManager
from .scheduler import SchedulerManager


def init(name: str, conf_path: str = "conf", pipelines_path: str = "pipelines"):
    if name is None:
        name = Path.cwd().name

    os.makedirs(os.path.join(name, "conf"), exist_ok=True)
    os.makedirs(os.path.join(name, "pipelines"), exist_ok=True)

    cfg = Config(base_dir=name)

    with open(os.path.join(name, "README.md"), "w") as f:
        f.write(
            f"# {name.replace('_', ' ').upper()}\n\n"
            f"**created with FlowerPower**\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )

    # cfg.update(
    #     cfg={
    #         "run": None,
    #         "params": None,
    #     },
    #     name="pipeline",

    # )
    # cfg.update(
    #     cfg={
    #         "username": None,
    #         "api_url": "http://localhost:8241",
    #         "ui_url": "http://localhost:8242",
    #         "api_key": None,
    #         "pipeline": None,
    #     },
    #     name="tracker",

    # )
    # cfg.update(
    #     {
    #         "data_path": {"type": "memory"},
    #         "event_broker": {"type": "local"},
    #         "pipeline": None,
    #     },
    #     name="scheduler",

    # )
    cfg.write(pipeline=True, tracker=True, scheduler=True)
