from typing import Any

import datafusion
import duckdb
import msgspec
import orjson
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.dataset as pds

from ..helpers.sql import sql2polars_filter
from ..metadata import get_dataframe_metadata, get_duckdb_metadata


class PayloadReader(msgspec.Struct):
    payload: bytes | dict[str, Any]
    topic: str | None = None
    conn: duckdb.DuckDBPyConnection | None = None
    ctx: datafusion.SessionContext | None = None
    format: str = "mqtt"

    def __post_init__(self):
        if isinstance(self.payload, bytes):
            self.payload = orjson.loads(self.payload)

        self._metadata = {
            "format": self.format,
            "timestamp": pd.Timestamp.now(),
            "topic": self.topic,
        }

    def to_pyarrow_table(
        self, metadata: bool = False
    ) -> pa.Table | tuple[pa.Table, dict[str, Any]]:
        try:
            df = pa.Table.from_pydict(self.payload)
        except pa.ArrowInvalid:
            df = pa.Table.from_pylist([self.payload])
        if metadata:
            self._metadata = get_dataframe_metadata(df, **self._metadata)
            return df, self._metadata
        return df

    def to_pandas(
        self, metadata: bool = False
    ) -> pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]:
        try:
            df = pd.DataFrame(self.payload)
        except ValueError:
            df = pd.DataFrame([self.payload])
        if metadata:
            self._metadata = get_dataframe_metadata(df, **self._metadata)
            return df, self._metadata
        return df

    def _to_polars_dataframe(
        self, metadata: bool = False
    ) -> pl.DataFrame | tuple[pl.DataFrame, dict[str, Any]]:
        try:
            df = pl.DataFrame(self.payload)
        except pl.exceptions.ShapeError:
            df = pl.DataFrame([self.payload])
        if metadata:
            self._metadata = get_dataframe_metadata(df, **self._metadata)
            return df, self._metadata
        return df

    def _to_polars_lazyframe(
        self, metadata: bool = False
    ) -> pl.LazyFrame | tuple[pl.LazyFrame, dict[str, Any]]:
        try:
            df = pl.LazyFrame(self.payload)
        except pl.exceptions.ShapeError:
            df = pl.LazyFrame([self.payload])
        if metadata:
            self._metadata = get_dataframe_metadata(df, **self._metadata)
            return df, self._metadata
        return df

    def to_polars(
        self, lazy: bool = False, metadata: bool = False
    ) -> (
        pl.DataFrame | pl.LazyFrame | tuple[pl.DataFrame | pl.LazyFrame, dict[str, Any]]
    ):
        if lazy:
            return self._to_polars_lazyframe(metadata=metadata)
        else:
            return self._to_polars_dataframe(metadata=metadata)

    def to_duckdb_relation(
        self, conn: duckdb.DuckDBPyConnection | None = None, metadata: bool = False
    ) -> duckdb.DuckDBPyRelation | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]:
        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn
        rel = self.conn.from_arrow(self.to_pyarrow_table())
        if metadata:
            self._metadata = get_duckdb_metadata(rel, **self._metadata)
            return rel, self._metadata
        return rel

    def to_pyarrow_dataset(
        self, metadata: bool = False, **kwargs
    ) -> pds.Dataset | tuple[pds.Dataset, dict[str, Any]]:
        if metadata:
            t, self._metadata = self.to_pyarrow_table(metadata=True)
            return pds.dataset(t, **kwargs), self._metadata
        return pds.dataset(self.to_pyarrow_table(), **kwargs)

    def register_in_duckdb(
        self,
        conn: duckdb.DuckDBPyConnection | None = None,
        name: str | None = None,
    ) -> duckdb.DuckDBPyConnection:
        if name is None:
            name = f"mqtt:{self.topic}"

        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        self.conn.register(name, self.to_pyarrow_table())
        return self.conn

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

        self.ctx.register(name, [self.to_pyarrow_table()])

        return self.ctx

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
        return self._data.filter(filter_expr)
