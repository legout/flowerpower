from typing import Any

import datafusion
import duckdb
import orjson
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.dataset as pds
from pydantic import BaseModel, ConfigDict

from ...utils.sql import sql2polars_filter


class PayloadReader(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    payload: bytes | dict[str, Any]
    topic: str | None = None
    conn: duckdb.DuckDBPyConnection | None = None
    ctx: datafusion.SessionContext | None = None
    format: str = "mqtt"

    def model_post_init(self, __context):
        if isinstance(self.payload, bytes):
            self.payload = orjson.loads(self.payload)

    def to_pyarrow_table(self) -> pa.Table:
        try:
            return pa.Table.from_pydict(self.payload)
        except pa.ArrowInvalid:
            return pa.Table.from_pylist([self.payload])

    def to_pandas(self) -> pd.DataFrame:
        try:
            return pd.DataFrame(self.payload)
        except ValueError:
            return pd.DataFrame([self.payload])

    def _to_polars_dataframe(self) -> pl.DataFrame:
        try:
            return pl.DataFrame(self.payload)
        except pl.exceptions.ShapeError:
            return pl.DataFrame([self.payload])

    def _to_polars_lazyframe(self) -> pl.LazyFrame:
        try:
            return pl.LazyFrame(self.payload)
        except pl.exceptions.ShapeError:
            return pl.LazyFrame([self.payload])

    def to_polars(self, lazy: bool = False) -> pl.DataFrame | pl.LazyFrame:
        if lazy:
            return self._to_polars_lazyframe()
        else:
            return self._to_polars_dataframe()

    def to_duckdb_relation(self, conn: duckdb.DuckDBPyConnection | None = None):
        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn
        return self.conn.from_arrow(self.to_pyarrow_table())

    def to_pyarrow_dataset(self, **kwargs) -> pds.Dataset:
        return pds.dataset(self.to_pyarrow_table(), **kwargs)

    def register_in_duckdb(
        self,
        conn: duckdb.DuckDBPyConnection | None = None,
        name: str | None = None,
    ):
        if name is None:
            name = f"mqtt:{self.topic}"

        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        self.conn.register(name, self.to_pyarrow_table())

    def register_in_datafusion(
        self,
        ctx: datafusion.SessionContext | None = None,
        name: str | None = None,
    ) -> None:
        if name is None:
            name = f"mqtt:{self.topic}"

        if self.ctx is None:
            if ctx is None:
                ctx = datafusion.SessionContext()
            self.ctx = ctx

        ctx.register(name, [self.to_pyarrow_table()])

        return ctx

    def filter(self, filter_expr: str | pl.Expr) -> pl.DataFrame | pl.LazyFrame:
        self._data = self.to_polars()

        pl_schema = (
            self._data.schema
            if isinstance(self._data, pl.DataFrame)
            else self._data.collect_schema()
        )
        filter_expr = (
            sql2polars_filter(filter_expr, pl_schema)
            if isinstance(filter_expr, str)
            else filter_expr
        )
        return self._data.filter(filter_expr)
