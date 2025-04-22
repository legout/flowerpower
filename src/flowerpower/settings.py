import os

from hamilton import registry

registry.disable_autoload()

# EXECUTOR
FP_DEFAULT_EXECUTOR = os.getenv("FP_DEFAULT_EXECUTOR", "threadpool")
FP_DEFAULT_EXECUTOR_MAX_WORKERS = int(os.getenv("FP_DEFAULT_EXECUTOR_MAX_WORKERS", 10))
FP_DEFAULT_EXECUTOR_NUM_CPUS = int(
    os.getenv("FP_DEFAULT_EXECUTOR_NUM_CPUS", os.cpu_count() or 1)
)

# LOGGING
FP_LOG_LEVEL = os.getenv("FP_LOG_LEVEL", "INFO")

# WORKER
FP_DEFAULT_WORKER_TYPE = os.getenv("FP_WORKER_TYPE", "rq")

FP_RQ_WORKER_BACKEND = os.getenv("FP_RQ_BACKEND", "redis")
FP_APS_WORKER_BACKEND_DS = os.getenv("FP_APS_DS_BACKEND", "postgresql")
FP_APS_WORKER_BACKEND_EB = os.getenv("FP_APS_EB_BACKEND", "postgresql")

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
        "default_database": "0",
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
