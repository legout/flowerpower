import os

from .backend import BACKEND_PROPERTIES
from .executor import EXECUTOR_NUM_CPUS

# WORKER
JOB_QUEUE_TYPE = os.getenv("FP_JOB_QUEUE_TYPE", "rq")

# RQ WORKER
RQ_BACKEND = os.getenv("FP_RQ_BACKEND", "redis")
RQ_BACKEND_HOST = os.getenv(
    "FP_RQ_BACKEND_HOST", BACKEND_PROPERTIES[RQ_BACKEND]["default_host"]
)
RQ_BACKEND_PORT = int(
    os.getenv("FP_RQ_BACKEND_PORT", BACKEND_PROPERTIES[RQ_BACKEND]["default_port"])
)
RQ_BACKEND_DB = int(
    os.getenv("FP_RQ_BACKEND_DB", BACKEND_PROPERTIES[RQ_BACKEND]["default_database"])
)
RQ_BACKEND_PASSWORD = os.getenv(
    "FP_RQ_BACKEND_PASSWORD", BACKEND_PROPERTIES[RQ_BACKEND]["default_password"]
)
RQ_BACKEND_USERNAME = os.getenv(
    "FP_RQ_BACKEND_USERNAME", BACKEND_PROPERTIES[RQ_BACKEND]["default_username"]
)
RQ_QUEUES = (
    os.getenv("FP_RQ_QUEUES", "default, high, low, scheduler")
    .replace(" ", "")
    .split(",")
)
RQ_NUM_WORKERS = int(os.getenv("FP_RQ_NUM_WORKERS", EXECUTOR_NUM_CPUS))
