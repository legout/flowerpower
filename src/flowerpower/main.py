import os

from .cfg import write


def init(conf_path: str = "conf", pipelines_path: str = "pipelines"):
    os.makedirs(conf_path, exist_ok=True)
    os.makedirs(pipelines_path, exist_ok=True)

    write({"path": pipelines_path, "run": None, "params": None}, "pipelines", conf_path)
    write(
        {
            "username": None,
            "api_url": "http://localhost:8241",
            "ui_url": "http://localhost:8242",
            "api_key": None,
            "pipeline": None,
        },
        "tracker",
        conf_path,
    )
    write(
        {
            "data_path": {"type": "memory"},
            "event_broker": {"type": "local"},
            "pipeline": None,
        },
        "scheduler",
        conf_path,
    )
