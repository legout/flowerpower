import os
import datetime as dt
from .cfg import Config
from flowerpower import cfg


def init(name: str, conf_path: str = "conf", pipelines_path: str = "pipelines"):
    os.makedirs(os.path.join(name, conf_path), exist_ok=True)
    os.makedirs(os.path.join(name, pipelines_path), exist_ok=True)
    
    cfg = Config(path=conf_path)

    with open(os.path.join(name, "README.md"), "w") as f:
        f.write(
            f"# {name.replace('_', ' ').upper()}\n\n"
            f"**created with FlowerPower**\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )

    cfg._write(
        {
            "run": None,
            "params": None,
        },
        "pipeline",
        os.path.join(name, conf_path),
    )
    cfg._write(
        {
            "username": None,
            "api_url": "http://localhost:8241",
            "ui_url": "http://localhost:8242",
            "api_key": None,
            "pipeline": None,
        },
        "tracker",
        os.path.join(name, conf_path),
    )
    cfg._write(
        {
            "data_path": {"type": "memory"},
            "event_broker": {"type": "local"},
            "pipeline": None,
        },
        "scheduler",
        os.path.join(name, conf_path),
    )
