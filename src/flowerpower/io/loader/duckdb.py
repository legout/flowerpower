import duckdb

from hamilton.function_modifiers import dataloader
import datetime as dt


@dataloader()
def connect_duckdb(
    path: str | None = None, **kwargs
) -> tuple[duckdb.DuckDBPyConnection, dict]:
    """
    Connect to a DuckDB database.

    Args:
        path: (str) Path to the database file. If None, an in-memory database is created.
        **kwargs: Additional keyword arguments to pass to `duckdb.connect`.

    Returns:
        conn: (DuckDBPyConnection) DuckDB connection.
        metadata: (dict) Metadata dictionary.
    """
    if path is None:
        path = ":memory:"
    conn = duckdb.connect(path, **kwargs)
    metadata = {
        "path": path,
        "format": "duckdb",
        "timestamp": dt.datetime.now().timestamp(),
    }
    return conn, metadata


@dataloader()
def connect_sqlite(
    path: str | None = None, **kwargs
) -> tuple[duckdb.DuckDBPyConnection, dict]:
    """
    Create a DuckDB connection to a SQLite database.

    Args:
        path: (str) Path to the database file. If None, an in-memory database is created.
        **kwargs: Additional keyword arguments to pass to `duckdb.connect`.

    Returns:
        conn: (DuckDBPyConnection) DuckDB connection.
        metadata: (dict) Metadata dictionary.
    """
    if path is None:
        path = ":memory:"
    conn = duckdb.connect(path, **kwargs)
    metadata = {
        "path": path,
        "format": "sqlite",
        "timestamp": dt.datetime.now().timestamp(),
    }
    return conn, metadata


@dataloader()
def attach_postgres(
    path: str | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None,
    database: str | None = None,
    **kwargs,
) -> tuple[duckdb.DuckDBPyConnection, dict]:
    """
    Attach a PostgreSQL database to a DuckDB connection.

    Args:
        path: (str) Path to the database file. If None, an in-memory database is created.
        conn: (DuckDBPyConnection) DuckDB connection.
        host: (str) PostgreSQL host.
        port: (int) PostgreSQL port.
        user: (str) PostgreSQL user.
        password: (str) PostgreSQL password.
        database: (str) PostgreSQL database.
        **kwargs: Additional keyword arguments to pass to `duckdb.connect`.

    Returns:
        conn: (DuckDBPyConnection) DuckDB connection.
        metadata: (dict) Metadata dictionary.
    """
    if conn is None:
        if path is None:
            path = ":memory:"

        conn = duckdb.connect(path, **kwargs)

    conn.execute("INSTALL postgres; LOAD postgres;")
    connection_string = " ".join(
        f"{k}={v}"
        for k, v in {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }.items()
        if v is not None
    )
    conn.execute(
        f"ATTACH {connection_string} AS postgres_db (TYPE POSTGRES, READ_ONLY);"
    )

    metadata = {
        "database": database,
        "format": "postgres",
        "timestamp": dt.datetime.now().timestamp(),
    }
    return conn, metadata


@dataloader()
def attach_mysql(
    path: str | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None,
    database: str | None = None,
    **kwargs,
) -> tuple[duckdb.DuckDBPyConnection, dict]:
    """
    Attach a MySQL database to a DuckDB connection.

    Args:
        path: (str) Path to the database file. If None, an in-memory database is created.
        conn: (DuckDBPyConnection) DuckDB connection.
        host: (str) MySQL host.
        port: (int) MySQL port.
        user: (str) MySQL user.
        password: (str) MySQL password.
        database: (str) MySQL database.
        **kwargs: Additional keyword arguments to pass to `duckdb.connect`.

    Returns:
        conn: (DuckDBPyConnection) DuckDB connection.
        metadata: (dict) Metadata dictionary.
    """
    if conn is None:
        if path is None:
            path = ":memory:"

        conn = duckdb.connect(path, **kwargs)

    conn.execute("INSTALL mysql; LOAD mysql;")
    connection_string = " ".join(
        f"{k}={v}"
        for k, v in {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }.items()
        if v is not None
    )
    conn.execute(f"ATTACH {connection_string} AS mysql_db (TYPE POSTGRES, READ_ONLY);")

    metadata = {
        "database": database,
        "format": "mysql",
        "timestamp": dt.datetime.now().timestamp(),
    }
    return conn, metadata


@dataloader()
def load_from_duckdb(
    query: str,
    path: str | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
    **kwargs,
) -> tuple[duckdb.DuckDBPyRelation, dict]:
    """
    Load data from a DuckDB database.

    Args:
        query: (str) SQL query.
        path: (str) Path to the database file. If None, an in-memory database is created.
        conn: (DuckDBPyConnection) DuckDB connection.
        **kwargs: Additional keyword arguments to pass to `duckdb.connect`.

    Returns:
        table: (DuckDBPyRelation) DuckDB relation.
        metadata: (dict) Metadata dictionary.
    """
    if conn is None:
        conn = duckdb.connect(path, **kwargs)

    table = conn.sql(query)
    metadata = {
        "path": path,
        "format": "duckdb",
        "timestamp": dt.datetime.now().timestamp(),
        "query": query,
    }
    return table, metadata


@dataloader()
def load_from_sqlite(
    query: str,
    path: str | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
    **kwargs,
) -> tuple[duckdb.DuckDBPyRelation, dict]:
    """
    Load data from a SQLite database.

    Args:
        query: (str) SQL query.
        path: (str) Path to the database file. If None, an in-memory database is created.
        conn: (DuckDBPyConnection) DuckDB connection.
        **kwargs: Additional keyword arguments to pass to `duckdb.connect`.

    Returns:
        table: (DuckDBPyRelation) DuckDB relation.
        metadata: (dict) Metadata dictionary.
    """
    if conn is None:
        conn = duckdb.connect(path, **kwargs)

    table = conn.sql(query)
    metadata = {
        "path": path,
        "format": "sqlite",
        "timestamp": dt.datetime.now().timestamp(),
        "query": query,
    }
    return table, metadata


@dataloader()
def load_from_postgres(
    query: str,
    path: str | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None,
    database: str | None = None,
    **kwargs,
) -> tuple[duckdb.DuckDBPyRelation, dict]:
    """
    Load data from a PostgreSQL database.

    Args:
        query: (str) SQL query.
        path: (str) Path to the database file. If None, an in-memory database is created.
        conn: (DuckDBPyConnection) DuckDB connection.
        host: (str) PostgreSQL host.
        port: (int) PostgreSQL port.
        user: (str) PostgreSQL user.
        password: (str) PostgreSQL password.
        database: (str) PostgreSQL database.
        **kwargs: Additional keyword arguments to pass to `duckdb.connect`.

    Returns:
        table: (DuckDBPyRelation) DuckDB relation.
        metadata: (dict) Metadata dictionary.
    """
    if conn is None:
        if path is None:
            path = ":memory:"

        conn = duckdb.connect(path, **kwargs)

    conn.execute("INSTALL postgres; LOAD postgres;")
    connection_string = " ".join(
        f"{k}={v}"
        for k, v in {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }.items()
        if v is not None
    )
    conn.execute(
        f"ATTACH {connection_string} AS postgres_db (TYPE POSTGRES, READ_ONLY);"
    )

    table = conn.sql(query)
    metadata = {
        "path": path,
        "format": "postgres",
        "timestamp": dt.datetime.now().timestamp(),
        "query": query,
    }
    return table, metadata


@dataloader()
def load_from_mysql(
    query: str,
    path: str | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None,
    database: str | None = None,
    **kwargs,
) -> tuple[duckdb.DuckDBPyRelation, dict]:
    """
    Load data from a MySQL database.

    Args:
        query: (str) SQL query.
        path: (str) Path to the database file. If None, an in-memory database is created.
        conn: (DuckDBPyConnection) DuckDB connection.
        host: (str) MySQL host.
        port: (int) MySQL port.
        user: (str) MySQL user.
        password: (str) MySQL password.
        database: (str) MySQL database.
        **kwargs: Additional keyword arguments to pass to `duckdb.connect`.

    """
    if conn is None:
        if path is None:
            path = ":memory:"

        conn = duckdb.connect(path, **kwargs)

    conn.execute("INSTALL mysql; LOAD mysql;")
    connection_string = " ".join(
        f"{k}={v}"
        for k, v in {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }.items()
        if v is not None
    )
    conn.execute(f"ATTACH {connection_string} AS mysql_db (TYPE MYSQL, READ_ONLY);")

    table = conn.sql(query)
    metadata = {
        "path": path,
        "format": "mysql",
        "timestamp": dt.datetime.now().timestamp(),
        "query": query,
    }
    return table, metadata
