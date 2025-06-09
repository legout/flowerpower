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
