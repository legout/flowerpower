import os

# Define backend properties in a dictionary for easier maintenance

BACKEND_PROPERTIES = {
    "postgresql": {
        "uri_prefix": "postgresql+asyncpg://",
        "default_port": 5432,
        "default_host": "localhost",
        "default_database": "postgres",
        "default_username": "postgres",
        "default_password": None,
        "is_sqla_type": True,
    },
    "mysql": {
        "uri_prefix": "mysql+aiomysql://",
        "default_port": 3306,
        "default_host": "localhost",
        "default_database": "mysql",
        "default_username": "root",
        "default_password": None,
        "is_sqla_type": True,
    },
    "sqlite": {
        "uri_prefix": "sqlite+aiosqlite://",
        "default_port": None,
        "default_host": "",
        "default_database": "",
        "default_username": None,
        "default_password": None,
        "is_sqla_type": True,
        "is_sqlite_type": True,
    },
    "mongodb": {
        "uri_prefix": "mongodb://",
        "default_port": 27017,
        "default_host": "localhost",
        "default_database": "admin",
        "default_username": None,
        "default_password": None,
        "is_sqla_type": False,
    },
    "mqtt": {
        "uri_prefix": "mqtt://",
        "default_port": 1883,
        "default_host": "localhost",
        "default_database": "mqtt",
        "default_username": None,
        "default_password": None,
        "is_sqla_type": False,
    },
    "redis": {
        "uri_prefix": "redis://",
        "default_port": 6379,
        "default_host": "localhost",
        "default_database": 0,
        "default_username": None,
        "default_password": None,
    },
    "nats_kv": {
        "uri_prefix": "nats://",
        "default_port": 4222,
        "default_host": "localhost",
        "default_database": "default",
        "default_username": None,
        "default_password": None,
    },
    "memory": {
        "uri_prefix": "memory://",
        "default_port": 0,
        "default_host": "",
        "default_database": "",
        "default_username": None,
        "default_password": None,
    },
}

# # REDIS ENVIRONMENT VARIABLES
# REDIS_HOST = os.getenv("FP_REDIS_HOST", BACKEND_PROPERTIES["redis"]["default_host"])
# REDIS_PORT = int(
#     os.getenv("FP_REDIS_PORT", BACKEND_PROPERTIES["redis"]["default_port"])
# )
# REDIS_DB = int(
#     os.getenv("FP_REDIS_DB", BACKEND_PROPERTIES["redis"]["default_database"])
# )
# REDIS_PASSWORD = os.getenv("FP_REDIS_PASSWORD", None)
# REDIS_USERNAME = os.getenv("FP_REDIS_USERNAME", None)
# REDIS_SSL = bool(os.getenv("FP_REDIS_SSL", False))

# # POSTGRES ENVIRONMENT VARIABLES
# POSTGRES_HOST = os.getenv(
#     "FP_POSTGRES_HOST", BACKEND_PROPERTIES["postgresql"]["default_host"]
# )
# POSTGRES_PORT = int(
#     os.getenv("FP_POSTGRES_PORT", BACKEND_PROPERTIES["postgresql"]["default_port"])
# )
# POSTGRES_DB = os.getenv(
#     "FP_POSTGRES_DB", BACKEND_PROPERTIES["postgresql"]["default_database"]
# )
# POSTGRES_USER = os.getenv(
#     "FP_POSTGRES_USER", BACKEND_PROPERTIES["postgresql"]["default_username"]
# )
# POSTGRES_PASSWORD = os.getenv("FP_POSTGRES_PASSWORD", None)
# POSTGRES_SSL = bool(os.getenv("FP_POSTGRES_SSL", False))

# # MYSQL ENVIRONMENT VARIABLES
# MYSQL_HOST = os.getenv("FP_MYSQL_HOST", BACKEND_PROPERTIES["mysql"]["default_host"])
# MYSQL_PORT = int(
#     os.getenv("FP_MYSQL_PORT", BACKEND_PROPERTIES["mysql"]["default_port"])
# )
# MYSQL_DB = os.getenv("FP_MYSQL_DB", BACKEND_PROPERTIES["mysql"]["default_database"])
# MYSQL_USER = os.getenv(
#     "FP_MYSQL_USER", BACKEND_PROPERTIES["mysql"]["default_username"]
# )
# MYSQL_PASSWORD = os.getenv("FP_MYSQL_PASSWORD", None)
# MYSQL_SSL = bool(os.getenv("FP_MYSQL_SSL", False))

# # MONGODB ENVIRONMENT VARIABLES
# MONGODB_HOST = os.getenv(
#     "FP_MONGODB_HOST", BACKEND_PROPERTIES["mongodb"]["default_host"]
# )
# MONGODB_PORT = int(
#     os.getenv("FP_MONGODB_PORT", BACKEND_PROPERTIES["mongodb"]["default_port"])
# )
# MONGODB_DB = os.getenv(
#     "FP_MONGODB_DB", BACKEND_PROPERTIES["mongodb"]["default_database"]
# )
# MONGODB_USER = os.getenv("FP_MONGODB_USER", None)
# MONGODB_PASSWORD = os.getenv("FP_MONGODB_PASSWORD", None)
# MONGODB_SSL = bool(os.getenv("FP_MONGODB_SSL", False))

# # MQTT ENVIRONMENT VARIABLES
# MQTT_HOST = os.getenv("FP_MQTT_HOST", BACKEND_PROPERTIES["mqtt"]["default_host"])
# MQTT_PORT = int(
#     os.getenv("FP_MQTT_PORT", BACKEND_PROPERTIES["mqtt"]["default_port"])
# )
# MQTT_USER = os.getenv("FP_MQTT_USER", None)
# MQTT_PASSWORD = os.getenv("FP_MQTT_PASSWORD", None)
# MQTT_SSL = bool(os.getenv("FP_MQTT_SSL", False))

# # NATS ENVIRONMENT VARIABLES
# NATS_HOST = os.getenv("FP_NATS_HOST", BACKEND_PROPERTIES["nats_kv"]["default_host"])
# NATS_PORT = int(
#     os.getenv("FP_NATS_PORT", BACKEND_PROPERTIES["nats_kv"]["default_port"])
# )
# NATS_USER = os.getenv("FP_NATS_USER", None)
# NATS_PASSWORD = os.getenv("FP_NATS_PASSWORD", None)
# NATS_SSL = bool(os.getenv("FP_NATS_SSL", False))
