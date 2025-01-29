# import datetime as dt

import datafusion as dtf
import duckdb

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pds
from deltalake import DeltaTable

# from hamilton.function_modifiers import dataloader

from ...utils.polars import pl
from ..base import BaseFileIO

# from ..utils import get_dataframe_metadata, get_delta_metadata


class DeltaTableLoader(BaseFileIO):
    """Delta table loader.

    This class is responsible for loading Delta tables into several dataframe formats,
    duckdb and datafusion.

    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "delta"

        self.delta_table = DeltaTable(
            self._raw_path,
            storage_options=self.storage_options.to_object_store_kwargs(),
        )

    @property
    def dt(self) -> DeltaTable:
        return self.delta_table

    def to_pyarrow_dataset(self) -> pds.Dataset:
        """Converts the DeltaTable to a PyArrow Dataset."""
        self.delta_table.to_pyarrow_dataset()

    def to_pyrrow_table(self) -> pa.Table:
        """Converts the DeltaTable to a PyArrow Table."""
        self.delta_table.to_pyarrow_table()

    def to_polars(self, lazy: bool = True) -> pl.DataFrame | pl.LazyFrame:
        """Converts the DeltaTable to a Polars DataFrame."""
        if lazy:
            return pl.scan_pyarrow_dataset(self.to_pyarrow_dataset())

        return pl.from_arrow(self.to_pyarrow_table())

    def to_pandas(self) -> pd.DataFrame:
        """Converts the DeltaTable to a Pandas DataFrame."""
        return self.to_pyrrow_table().to_pandas()

    def to_duckdb_relation(
        self, conn: duckdb.DuckDBPyConnection | None = None, lazy: bool = True
    ) -> duckdb.DuckDBPyRelation:
        """Converts the DeltaTable to a DuckDB relation."""
        if conn is None:
            conn = duckdb.connect()
        if lazy:
            return conn.from_arrow(self.to_pyarrow_dataset())
        return conn.from_arrow(self.to_pyarrow_table())

    def register_in_duckdb(
        self,
        conn: duckdb.DuckDBPyConnection | None = None,
        name: str | None = None,
        lazy: bool = True,
    ) -> duckdb.DuckDBPyConnection:
        """Registers the DeltaTable in a DuckDB connection."""
        if name is None:
            name = f"{self.format}:{self.path}"
        if conn is None:
            conn = duckdb.connect()
        table = self.to_duckdb_relation(conn=conn, lazy=lazy)
        conn.register(name, table)
        return conn

    def register_in_datafusion(
        self,
        ctx: dtf.SessionContext | None = None,
        name: str | None = None,
        lazy: bool = True,
    ) -> dtf.SessionContext:
        """Registers the DeltaTable in a DataFusion context."""
        if name is None:
            name = f"{self.format}:{self.path}"
        if ctx is None:
            ctx = dtf.SessionContext()
        if lazy:
            ctx.register_dataset(name, self.to_pyarrow_dataset())
        else:
            ctx.register_record_batches(name, [self.to_pyarrow_table().to_batches()])
            # table = table.to_table()
        # ctx.register_dataset(name, table)
        return ctx
