import os

from .backend import BACKEND_PROPERTIES
from .executor import EXECUTOR, EXECUTOR_MAX_WORKERS, EXECUTOR_NUM_CPUS

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

# APS WORKER
APS_BACKEND_DS = os.getenv("FP_APS_BACKEND_DS", "memory")

APS_BACKEND_DS_HOST = os.getenv(
    "FP_APS_BACKEND_DS_HOST",
    BACKEND_PROPERTIES.get(APS_BACKEND_DS, {}).get("default_host", None),
)
APS_BACKEND_DS_PORT = int(
    os.getenv(
        "FP_APS_BACKEND_DS_PORT",
        BACKEND_PROPERTIES.get(APS_BACKEND_DS, {}).get("default_port", 0),
    )
)
APS_BACKEND_DS_DB = os.getenv(
    "FP_APS_BACKEND_DS_DB",
    BACKEND_PROPERTIES.get(APS_BACKEND_DS, {}).get("default_database", None),
)
APS_BACKEND_DS_USERNAME = os.getenv(
    "FP_APS_BACKEND_DS_USERNAME",
    BACKEND_PROPERTIES.get(APS_BACKEND_DS, {}).get("default_username", None),
)
APS_BACKEND_DS_PASSWORD = os.getenv(
    "FP_APS_BACKEND_DS_PASSWORD",
    BACKEND_PROPERTIES.get(APS_BACKEND_DS, {}).get("default_password", None),
)
APS_BACKEND_DS_SCHEMA = os.getenv("FP_APS_BACKEND_DS_SCHEMA", "flowerpower")

APS_BACKEND_EB = os.getenv("FP_APS_BACKEND_EB", "memory")
APS_BACKEND_EB_HOST = os.getenv(
    "FP_APS_BACKEND_EB_HOST",
    BACKEND_PROPERTIES.get(APS_BACKEND_EB, {}).get("default_host", None),
)
APS_BACKEND_EB_PORT = int(
    os.getenv(
        "FP_APS_BACKEND_EB_PORT",
        BACKEND_PROPERTIES.get(APS_BACKEND_EB, {}).get("default_port", 0),
    )
)
APS_BACKEND_EB_DB = os.getenv(
    "FP_APS_BACKEND_EB_DB",
    BACKEND_PROPERTIES.get(APS_BACKEND_EB, {}).get("default_database", None),
)
APS_BACKEND_EB_USERNAME = os.getenv(
    "FP_APS_BACKEND_EB_USERNAME",
    BACKEND_PROPERTIES.get(APS_BACKEND_EB, {}).get("default_username", None),
)
APS_BACKEND_EB_PASSWORD = os.getenv(
    "FP_APS_BACKEND_EB_PASSWORD",
    BACKEND_PROPERTIES.get(APS_BACKEND_EB, {}).get("default_password", None),
)

APS_CLEANUP_INTERVAL = int(os.getenv("FP_APS_CLEANUP_INTERVAL", 300))
APS_MAX_CONCURRENT_JOBS = int(os.getenv("FP_APS_MAX_CONCURRENT_JOBS", 10))
APS_DEFAULT_EXECUTOR = os.getenv("FP_APS_DEFAULT_EXECUTOR", EXECUTOR)
APS_NUM_WORKERS = int(os.getenv("FP_APS_NUM_WORKERS", EXECUTOR_MAX_WORKERS))
