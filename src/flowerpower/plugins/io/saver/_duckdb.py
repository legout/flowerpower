import os
from typing import Literal

import duckdb
import pandas as pd
import polars as pl
import pyarrow as pa
from pydantic import BaseModel

from ...utils.misc import _dict_to_dataframe


class DuckDBSaver(BaseModel):
    path: str | None = None
    table_name: str
    mode: Literal["overwrite", "append", "fail", "merge", "update"] = "append"
    key_columns: list[str] | None = None  # Required for merge/update modes
    conn: duckdb.DuckDBPyConnection | None = None
    host: str | None = None
    port: int | None = None
    socket: str | None = None
    user: str | None = None
    password: str | None = None
    database: str | None = None

    def _is_sqlite_file(self, path: str) -> bool:
        """Check if file is SQLite by reading first 16 bytes for SQLite header."""
        if not os.path.exists(path):
            return False
        with open(path, "rb") as f:
            header = f.read(16)
        return header.startswith(b"SQLite format 3\x00")

    def model_post_init(self, __context):
        if self.path is None:
            self.path = ":memory:"
            self.conn = duckdb.connect(self.path)
        else:
            if os.path.exists(self.path):
                if self._is_sqlite_file(self.path):
                    # For SQLite files, create in-memory DuckDB and attach SQLite
                    self.conn = duckdb.connect(":memory:")
                    self.conn.execute("INSTALL sqlite; LOAD sqlite;")
                    self.conn.execute(
                        f"ATTACH '{self.path}' AS sqlite_db (TYPE SQLITE);"
                    )
                else:
                    # For DuckDB files, connect directly
                    self.conn = duckdb.connect(self.path)
            else:
                # For new files, create new DuckDB database
                self.conn = duckdb.connect(self.path)

        if self.host is not None:
            self._update_from_env()

        if self.host is not None:
            if self.port == 5432:
                self._attach_postgres()
            elif self.port == 3306:
                self._attach_mysql()

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

    def _attach_postgres(self):
        self.conn.execute("INSTALL postgres; LOAD postgres;")
        connection_string = " ".join(
            f"{k}={v}"
            for k, v in {
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "password": self.password,
                "database": self.database,
            }.items()
            if v is not None
        )
        self.conn.execute(f"ATTACH {connection_string} AS postgres_db;")

    def _attach_mysql(self):
        self.conn.execute("INSTALL mysql; LOAD mysql;")
        connection_string = " ".join(
            f"{k}={v}"
            for k, v in {
                "host": self.host,
                "port": self.port,
                "socket": self.socket,
                "user": self.user,
                "password": self.password,
                "database": self.database,
            }.items()
            if v is not None
        )
        self.conn.execute(f"ATTACH {connection_string} AS mysql_db;")

    def _validate_merge_params(self):
        if self.mode in ("merge", "update") and not self.key_columns:
            # raise ValueError(f"key_columns must be specified for mode '{self.mode}'")
            # key columns should be all columns in the table
            self.key_columns = self.conn.table(self.table_name).columns

    def _table_exists(self) -> bool:
        tables_query = (
            "SELECT name FROM sqlite_master"
            if self._is_sqlite_file(self.path)
            else "SELECT table_name as name FROM information_schema.tables"
        )
        result = self.conn.execute(
            f"{tables_query} WHERE name='{self.table_name}'"
        ).fetchone()
        return bool(result)

    def _handle_existing_table(self) -> bool:
        """Handle existing table based on mode. Returns True if table exists."""
        exists = self._table_exists()

        if exists:
            if self.mode == "fail":
                raise ValueError(f"Table {self.table_name} already exists")
            elif self.mode == "overwrite":
                self.conn.execute(f"DROP TABLE {self.table_name}")
                return False
            elif self.mode in ("append", "merge", "update"):
                return True
        return False

    def write(
        self,
        data: (
            pd.DataFrame
            | pl.DataFrame
            | pl.LazyFrame
            | pa.Table
            | pa.RecordBatch
            | pa.RecordBatchReader
            | dict
            | list[
                pd.DataFrame
                | pl.DataFrame
                | pl.LazyFrame
                | pa.Table
                | pa.RecordBatch
                | pa.RecordBatchReader
                | dict
            ]
        ),
        mode: Literal["overwrite", "append", "fail", "merge", "update"] = None,
        key_columns: list[str] | None = None,
    ):
        """Write data to database with specified merge strategy.

        Args:
            data: Data to write. Supports pandas/polars DataFrames, pyarrow Tables/Batches, or dicts
        """
        mode = mode or self.mode
        key_columns = key_columns or self.key_columns

        if isinstance(data, dict):
            data = _dict_to_dataframe(data)

        if not isinstance(data, list):
            data = [data]
        if isinstance(data[0], dict):
            data = [_dict_to_dataframe(d) for d in data]
        if isinstance(data[0], pa.LazyFrame):
            data = [d.collect() for d in data]
        if isinstance(data[0], pl.DataFrame):
            data = pl.concat(data, how="diagonal_relaxed").to_arrow()
        if isinstance(data[0], pd.DataFrame):
            data = pa.concat_tables(
                [pa.Table.from_pandas(d, preserve_index=False) for d in data],
                promote_options="permissive",
            )
        if isinstance(data[0], pa.RecordBatch | pa.RecordBatchReader):
            data = pa.Table.from_batches(data)
        if isinstance(data[0], pa.Table):
            data = pa.concat_tables(data, promote_options="permissive")

        self._validate_merge_params()
        table_exists = self._handle_existing_table()

        # Convert input to temporary table
        temp_name = f"temp_{self.table_name}"
        self.conn.execute(f"DROP TABLE IF EXISTS {temp_name}")
        self.conn.execute(f"CREATE TEMP TABLE {temp_name} AS SELECT * FROM data")

        if not table_exists:
            # Simple case - just rename temp table
            self.conn.execute(f"ALTER TABLE {temp_name} RENAME TO {self.table_name}")
            return

        if mode == "append":
            self.conn.execute(
                f"INSERT INTO {self.table_name} SELECT * FROM {temp_name}"
            )

        elif mode == "merge":
            # Insert only rows where key columns don't exist in target
            key_matches = " AND ".join(f"t.{col} = m.{col}" for col in key_columns)
            self.conn.execute(
                f"""
                INSERT INTO {self.table_name}
                SELECT t.* FROM {temp_name} t
                WHERE NOT EXISTS (
                    SELECT 1 FROM {self.table_name} m
                    WHERE {key_matches}
                )
            """
            )

        elif mode == "update":
            # Create staging table
            staging_name = f"staging_{self.table_name}"

            # First copy all rows from target that don't match key columns
            key_matches = " AND ".join(f"t.{col} = m.{col}" for col in key_columns)
            self.conn.execute(
                f"""
                CREATE TABLE {staging_name} AS
                SELECT t.* FROM {self.table_name} t
                WHERE NOT EXISTS (
                    SELECT 1 FROM {temp_name} m
                    WHERE {key_matches}
                )
            """
            )

            # Then add all rows from new data
            self.conn.execute(
                f"""
                INSERT INTO {staging_name}
                SELECT * FROM {temp_name}
            """
            )

            # Replace original with staging
            self.conn.execute(f"DROP TABLE {self.table_name}")
            self.conn.execute(f"ALTER TABLE {staging_name} RENAME TO {self.table_name}")

        # Cleanup
        self.conn.execute(f"DROP TABLE IF EXISTS {temp_name}")
