import os

PIPELINES_DIR = os.getenv("FP_PIPELINES_DIR", "pipelines")
CONFIG_DIR = os.getenv("FP_CONFIG_DIR", "conf")
HOOKS_DIR = os.getenv("FP_HOOKS_DIR", "hooks")

# EXECUTOR
EXECUTOR = os.getenv("FP_EXECUTOR", "threadpool")
EXECUTOR_MAX_WORKERS = int(
    os.getenv("FP_EXECUTOR_MAX_WORKERS", os.cpu_count() * 5 or 10)
)
EXECUTOR_NUM_CPUS = int(os.getenv("FP_EXECUTOR_NUM_CPUS", os.cpu_count() or 1))

# RETRY
MAX_RETRIES = int(os.getenv("FP_MAX_RETRIES", 1))
RETRY_DELAY = float(os.getenv("FP_RETRY_DELAY", 1.0))
JITTER_FACTOR = float(os.getenv("FP_JITTER_FACTOR", 0.1))

# LOGGING
LOG_LEVEL = os.getenv("FP_LOG_LEVEL", "INFO")

# WORKER
DEFAULT_JOB_QUEUE = os.getenv("FP_JOB_QUEUE_TYPE", "rq")
# RQ WORKER
RQ_BACKEND = os.getenv("FP_RQ_BACKEND", "redis")
RQ_QUEUES = (
    os.getenv("FP_RQ_QUEUES", "default, high, low, scheduler")
    .replace(" ", "")
    .split(",")
)
RQ_NUM_WORKERS = int(os.getenv("FP_RQ_NUM_WORKERS", EXECUTOR_NUM_CPUS))

# APS WORKER
APS_BACKEND_DS = os.getenv("FP_APS_DS_BACKEND", "postgresql")
APS_SCHEMA_DS = os.getenv("FP_APS_SCHEMA", "flowerpower")
APS_BACKEND_EB = os.getenv("FP_APS_EB_BACKEND", "postgresql")
APS_CLEANUP_INTERVAL = int(os.getenv("FP_APS_CLEANUP_INTERVAL", 300))
APS_MAX_CONCURRENT_JOBS = int(os.getenv("FP_APS_MAX_CONCURRENT_JOBS", 10))
APS_DEFAULT_EXECUTOR = os.getenv("FP_APS_DEFAULT_EXECUTOR", EXECUTOR)
APS_NUM_WORKERS = int(os.getenv("FP_APS_NUM_WORKERS", EXECUTOR_MAX_WORKERS))

# Define backend properties in a dictionary for easier maintenance
BACKEND_PROPERTIES = {
    "postgresql": {
        "uri_prefix": "postgresql+asyncpg://",
        "default_port": 5432,
        "default_host": "localhost",
        "default_database": "postgres",
        "default_username": "postgres",
        "is_sqla_type": True,
    },
    "mysql": {
        "uri_prefix": "mysql+aiomysql://",
        "default_port": 3306,
        "default_host": "localhost",
        "default_database": "mysql",
        "default_username": "root",
        "is_sqla_type": True,
    },
    "sqlite": {
        "uri_prefix": "sqlite+aiosqlite://",
        "default_port": None,
        "default_host": "",
        "default_database": "",
        "is_sqla_type": True,
        "is_sqlite_type": True,
    },
    "mongodb": {
        "uri_prefix": "mongodb://",
        "default_port": 27017,
        "default_host": "localhost",
        "default_database": "admin",
        "is_sqla_type": False,
    },
    "mqtt": {
        "uri_prefix": "mqtt://",
        "default_port": 1883,
        "default_host": "localhost",
        "default_database": "mqtt",
    },
    "redis": {
        "uri_prefix": "redis://",
        "default_port": 6379,
        "default_host": "localhost",
        "default_database": 0,
    },
    "nats_kv": {
        "uri_prefix": "nats://",
        "default_port": 4222,
        "default_host": "localhost",
        "default_database": "default",
    },
    "memory": {
        "uri_prefix": "memory://",
        "default_port": None,
        "default_host": "",
        "default_database": "",
    },
}

# HAMILTON
HAMILTON_MAX_LIST_LENGTH_CAPTURE = int(
    os.getenv("HAMILTON_MAX_LIST_LENGTH_CAPTURE", 50)
)
HAMILTON_MAX_DICT_LENGTH_CAPTURE = int(
    os.getenv("HAMILTON_MAX_DICT_LENGTH_CAPTURE", 10)
)
HAMILTON_CAPTURE_DATA_STATISTICS = bool(
    os.getenv("HAMILTON_CAPTURE_DATA_STATISTICS", True)
)

HAMILTON_AUTOLOAD_EXTENSIONS = int(os.getenv("HAMILTON_AUTOLOAD_EXTENSIONS", 0))
HAMILTON_TELEMETRY_ENABLED = bool(os.getenv("HAMILTON_TELEMETRY_ENABLED", False))
HAMILTON_API_URL = os.getenv("HAMILTON_API_URL", "http://localhost:8241")
HAMILTON_UI_URL = os.getenv("HAMILTON_UI_URL", "http://localhost:8242")
