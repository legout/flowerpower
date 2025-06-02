from logging.config import fileConfig

import sqlite3
from pathlib import Path
from sqlalchemy import create_engine # Import create_engine

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata # Keep this commented out for manual migrations
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Since we are not using SQLAlchemy ORM for schema definition,
    we connect directly using sqlite3.
    """
    # Get the database URL from alembic.ini
    db_url = config.get_main_option("sqlalchemy.url")
    if not db_url or not db_url.startswith("sqlite:///"):
        raise ValueError("sqlalchemy.url must be set to a sqlite path in alembic.ini (e.g., sqlite:///path/to/db.sqlite)")
    
    # Extract the file path from the URL
    db_path = Path(db_url.replace("sqlite:///", ""))

    # This connection is for Alembic's internal use, not for direct SQL execution
    # It must be wrapped in a SQLAlchemy engine to provide the 'dialect' attribute
    # even though we are doing manual migrations.
    engine = create_engine(db_url)

    with engine.connect() as connection: # Use engine.connect() to get a connection with dialect
        context.configure(
            connection=connection, target_metadata=None # Explicitly None for manual migrations
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
