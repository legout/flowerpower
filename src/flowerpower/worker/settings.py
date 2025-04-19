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