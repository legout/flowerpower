from dataclasses import dataclass, field
from typing import Any

import datafusion
import duckdb
import orjson
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.dataset as pds

from ...utils.sql import sql2polars_filter
from ..metadata import get_dataframe_metadata, get_duckdb_metadata


@dataclass
class PayloadReader:
    """
    MQTT Payload loader.

    Converts MQTT message payloads (bytes or dict) into DataFrames (pandas, polars, pyarrow).
    Supports registering data in DuckDB and DataFusion contexts, and filtering with SQL or polars expressions.
    """

    payload: bytes | dict[str, Any]
    topic: str | None = None
    conn: duckdb.DuckDBPyConnection | None = None
    ctx: datafusion.SessionContext | None = None
    format: str = "mqtt"
    _metadata: dict[str, Any] = field(init=False, default_factory=dict)

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
        """Convert data to pyarrow Table.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.

        Returns:
            pa.Table | tuple[pa.Table, dict[str, Any]]: PyArrow Table or tuple of Table and metadata.
        """
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
        """Convert data to pandas DataFrame.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.

        Returns:
            pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]: Pandas DataFrame or tuple of DataFrame and metadata.
        """
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
        """Convert data to polars DataFrame."""
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
        """Convert data to polars LazyFrame."""
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
        """Convert data to polars DataFrame or LazyFrame.

        Args:
            lazy (bool, optional): If True, return a LazyFrame. Default is False.
            metadata (bool, optional): Include metadata in the output. Default is False.

        Returns:
            pl.DataFrame | pl.LazyFrame | tuple[pl.DataFrame | pl.LazyFrame, dict[str, Any]]:
                Polars DataFrame or LazyFrame or tuple of DataFrame/LazyFrame and metadata.
        """
        if lazy:
            return self._to_polars_lazyframe(metadata=metadata)
        else:
            return self._to_polars_dataframe(metadata=metadata)

    def to_duckdb_relation(
        self, conn: duckdb.DuckDBPyConnection | None = None, metadata: bool = False
    ) -> duckdb.DuckDBPyRelation | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]:
        """Convert data to DuckDB relation.
        
        Args:
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            metadata (bool, optional): Include metadata in the output. Default is False.
        
        Returns:
            duckdb.DuckDBPyRelation | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]: DuckDB relation
                or DuckDB relation and optional metadata.
        """
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
        """Convert data to pyarrow Dataset.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments for pyarrow dataset.
        
        Returns:
            pds.Dataset | tuple[pds.Dataset, dict[str, Any]]: PyArrow Dataset or tuple of Dataset and metadata.
        """
        if metadata:
            t, self._metadata = self.to_pyarrow_table(metadata=True)
            return pds.dataset(t, **kwargs), self._metadata
        return pds.dataset(self.to_pyarrow_table(), **kwargs)

    def register_in_duckdb(
        self,
        conn: duckdb.DuckDBPyConnection,
        name: str | None = None,
        metadata: bool = False,
        **kwargs,
    ) -> duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]:
        """Register data in DuckDB.

        Args:
            conn (duckdb.DuckDBPyConnection): DuckDB connection instance.
            name (str, optional): Name for the DuckDB table.
            metadata (bool, optional): Include metadata in the output. Default is False.

        Returns:
            duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]: DuckDB connection instance
                or DuckDB connection instance and optional metadata.
        """
        if name is None:
            name = f"{self.format}:{self.topic}"

        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        self.conn.register(
            name, self.to_pyarrow_table( **kwargs)
        )
        if metadata:
            return self.conn, self._metadata
        return self.conn

    def to_duckdb(
        self,
        as_relation: bool = True,
        conn: duckdb.DuckDBPyConnection | None = None,
        name: str | None = None,
        metadata: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> (
        duckdb.DuckDBPyRelation
        | duckdb.DuckDBPyConnection
        | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]
        | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]
    ):
        """Convert data to DuckDB relation or register in DuckDB.

        Args:
            as_relation (bool, optional): Return a DuckDB relation if True, else register in DuckDB. Default is True.
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            name (str, optional): Name for the DuckDB table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyRelation | duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyRelation, dict[str, Any]] |
                tuple[duckdb.DuckDBPyConnection, dict[str, Any]]: DuckDB relation or connection instance
                or DuckDB relation or connection instance and optional metadata.

        """
        if as_relation:
            return self.to_duckdb_relation(
                conn=conn,  **kwargs
            )
        return self.register_in_duckdb(
            conn=conn, name=name, **kwargs
        )

    def register_in_datafusion(
        self,
        ctx: datafusion.SessionContext,
        name: str | None = None,
        metadata: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> datafusion.SessionContext | tuple[datafusion.SessionContext, dict[str, Any]]:
        """Register data in DataFusion.

        Args:
            ctx (datafusion.SessionContext): DataFusion session context instance.
            name (str, optional): Name for the DataFusion table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        if name is None:
            name = f"{self.format}:{self.topic}"

        if self.ctx is None:
            if ctx is None:
                ctx = datafusion.SessionContext()
            self.ctx = ctx

        table = self.to_pyarrow_table(metadata=False, **kwargs)
        
        self.ctx.register_record_batches(
            name,
            [table.to_batches()],
        )
        if metadata:
            return self.ctx, self._metadata
        return ctx

    def filter(self, filter_expr: str | pl.Expr) -> pl.DataFrame | pl.LazyFrame:
        """
        Filter the payload data using a SQL expression string or polars expression.

        Args:
            filter_expr: SQL WHERE clause string or polars expression.

        Returns:
            Filtered polars DataFrame or LazyFrame.
        """
        data = self.to_polars()
        if isinstance(data, tuple):
            data = data[0]
        self._data = data

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
