import os
import datetime as dt
from .cfg import Config


def init(name: str, conf_path: str = "conf", pipelines_path: str = "pipelines"):
    os.makedirs(os.path.join(name, conf_path), exist_ok=True)
    os.makedirs(os.path.join(name, pipelines_path), exist_ok=True)
    
    cfg = Config(path=os.path.join(name, conf_path))

    with open(os.path.join(name, "README.md"), "w") as f:
        f.write(
            f"# {name.replace('_', ' ').upper()}\n\n"
            f"**created with FlowerPower**\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )

    cfg.update(
        cfg={
            "run": None,
            "params": None,
        },
        name="pipeline",
        
    )
    cfg.update(
        cfg={
            "username": None,
            "api_url": "http://localhost:8241",
            "ui_url": "http://localhost:8242",
            "api_key": None,
            "pipeline": None,
        },
        name="tracker",
       
    )
    cfg.update(
        {
            "data_path": {"type": "memory"},
            "event_broker": {"type": "local"},
            "pipeline": None,
        },
        name="scheduler",
        
    )
    cfg.write(pipeline=True, tracker=True, scheduler=True)