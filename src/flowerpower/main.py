import os
from .cfg import write, TRACKER_TEMPLATE, PIPELINE_TEMPLATE, SCHEDULER_TEMPLATE

def init(conf_path: str = "conf", pipelines_path: str = "pipelines"):
    os.makedirs(conf_path, exist_ok=True)
    os.makedirs(pipelines_path, exist_ok=True)

    write(PIPELINE_TEMPLATE, "pipelines", conf_path)
    write(TRACKER_TEMPLATE, "tracker", conf_path)
    write(SCHEDULER_TEMPLATE, "scheduler", conf_path)
