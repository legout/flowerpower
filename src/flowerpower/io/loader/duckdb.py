import datetime as dt
import os

import duckdb
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.dataset as pds
from hamilton.function_modifiers import dataloader
from pydantic import BaseModel


class DuckDBLoader(BaseModel):
    path: str | None = None
    read_only: bool = False
    conn: duckdb.DuckDBPyConnection | None = None
    host: str | None = None
    port: int | None = None
    socket: str | None = None
    user: str | None = None
    password: str | None = None
    database: str | None = None

    def model_post_init(self, __context):
        if self.path is None:
            self.path = ":memory:"
        if self.conn is None:
            self.conn = duckdb.connect(self.path, self.read_only)

        if self.host is not None:
            self._update_from_env()

        if self.host is not None:
            if self.port == 5432:
                self.attach_postgres()
            elif self.port == 3306:
                self.attach_mysql()

    def _update_from_env(self):
        self.host = (
            os.getenv("POSTGRES_HOST") or os.getenv("PGHOST") or os.getenv("MYSQL_HOST")
        )
        self.port = (
            os.getenv("POSTGRES_PORT")
            or os.getenv("PGPORT")
            or os.getenv("MYSQL_TCP_PORT")
        )
        self.user = (
            os.getenv("POSTGRES_USER") or os.getenv("PGUSER") or os.getenv("MYSQL_USER")
        )
        self.password = (
            os.getenv("POSTGRES_PASSWORD")
            or os.getenv("PGPASSWORD")
            or os.getenv("MYSQL_PW")
        )
        self.database = (
            os.getenv("POSTGRES_DB")
            or os.getenv("PGDATABASE")
            or os.getenv("MYSQL_DATABASE")
        )
        self.socket = os.getenv("MYSQL_UNIX_PORT")

    def attach_postgres(
        self,
    ):
        self.conn.execute("INSTALL postgres; LOAD postgres;")
        connection_string = ""
        for k, v in {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
        }.items():
            if v is not None:
                connection_string += f"{k}={v} "

        self.conn.execute(
            f"ATTACH {connection_string} AS postgres_db (TYPE POSTGRES, READ_ONLY);"
        )

    def attach_mysql(
        self,
    ):
        self.conn.execute("INSTALL mysql; LOAD mysql;")
        connection_string = ""
        for k, v in {
            "host": self.host,
            "port": self.port,
            "socket": self.socket,
            "user": self.user,
            "password": self.password,
            "database": self.database,
        }.items():
            if v is not None:
                connection_string += f"{k}={v} "
        self.conn.execute(
            f"ATTACH {connection_string} AS mysql_db (TYPE MYSQL, READ_ONLY);"
        )

    def to_duckdb_relation(self, query: str) -> duckdb.DuckDBPyRelation:
        return self.conn.sql(query)

    def to_pandas(self, query: str) -> pd.DataFrame:
        return self.to_duckdb_relation(query).tdf()

    def to_polars(self, query: str) -> pl.DataFrame:
        return self.to_duckdb_relation(query).pl()

    def to_pyarrow_table(self, query: str) -> pa.Table:
        return self.to_duckdb_relation(query).arrow()

    def to_dataset(self, query: str) -> pds.Dataset:
        return pds.dataset(self.to_pyarrow_table(query))


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
