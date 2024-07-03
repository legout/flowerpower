import os
import datetime as dt
from .cfg import write


def init(name: str, conf_path: str = "conf", pipelines_path: str = "pipelines"):
    os.makedirs(os.path.join(name, conf_path), exist_ok=True)
    os.makedirs(os.path.join(name, pipelines_path), exist_ok=True)

    with open(os.path.join(name, "README.md"), "w") as f:
        f.write(
            f"# {name.replace('_', ' ').upper()}\n\n"
            f"**created with FlowerPower**\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )

    write(
        {
            "run": None,
            "params": None,
        },
        "pipeline",
        os.path.join(name, conf_path),
    )
    write(
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
    write(
        {
            "data_path": {"type": "memory"},
            "event_broker": {"type": "local"},
            "pipeline": None,
        },
        "scheduler",
        os.path.join(name, conf_path),
    )
