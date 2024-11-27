import datetime as dt

import datafusion as dtf
import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pds
from deltalake import DeltaTable
from hamilton.function_modifiers import dataloader

from ...utils.polars import pl
from ..utils import get_dataframe_metadata, get_delta_metadata


@dataloader()
def load(
    path: str, storage_options: dict[str, str] | None = None, **kwargs
) -> tuple[DeltaTable, dict]:
    dtable = DeltaTable(path, storage_options=storage_options, **kwargs)
    metadata = get_delta_metadata(dtable, path, **kwargs)

    return dtable, metadata


@dataloader()
def load_pyarrow_table(
    path: str, storage_options: dict[str, str] | None = None, **kwargs
) -> tuple[pa.Table, dict]:
    dtable, metadata = load(path, storage_options=storage_options, **kwargs)
    table = dtable.to_pyarrow_table()
    metadata["num_rows"] = table.num_rows
    return table, metadata


@dataloader()
def load_pyarrow_dataset(
    path: str, storage_options: dict[str, str] | None = None, **kwargs
) -> dict[pds.Dataset, dict]:
    dtable, metadata = load(path, storage_options=storage_options, **kwargs)
    ds = dtable.to_pyarrow_dataset()
    return ds, metadata


@dataloader()
def load_pandas_dataframe(
    path: str, storage_options: dict[str, str] | None = None, **kwargs
) -> tuple[pd.DataFrame, dict]:
    dtable, metadata = load(path, storage_options=storage_options, **kwargs)
    df = dtable.to_pandas()
    metadata["num_rows"] = df.shape[0]
    return df, metadata


@dataloader()
def load_polars_dataframe(
    path: str, storage_options: dict[str, str] | None = None, **kwargs
) -> tuple[pl.DataFrame, dict]:
    df = pl.read_delta(path, storage_options=storage_options, **kwargs)
    metadata = get_dataframe_metadata(df, path, **kwargs)

    return df, metadata


@dataloader()
def load_polars_lazyframe(
    path: str, storage_options: dict[str, str] | None = None, **kwargs
) -> pl.LazyFrame:
    df = pl.scan_delta(path, storage_options=storage_options, **kwargs)
    df_schema = df.collect_schema.to_python()
    metadata = {
        "path": path,
        "format": "delta",
        "timestamp": dt.datetime.now().timestamp(),
        "schema": df_schema,
        "partition_columns": None,
        "num_columns": len(df_schema),
        "num_rows": None,
        "name": None,
        "description": None,
        "id": None,
    }
    return df, metadata


@dataloader()
def load_duckdb_relation(
    path: str,
    storage_options: dict[str, str] | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
    **kwargs,
) -> tuple[duckdb.DuckDBPyRelation, dict]:
    ds, metadata = load_pyarrow_dataset(path, storage_options=storage_options, **kwargs)
    if conn is None:
        conn = duckdb.connect()

    table = conn.from_arrow(ds)

    return table, metadata


@dataloader()
def register_delta_in_duckdb(
    path: str,
    storage_options: dict[str, str] | None = None,
    name: str | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
    lazy: bool = True,
    **kwargs,
) -> tuple[duckdb.DuckDBPyConnection, dict]:
    if name is None:
        name = "delta_table"
    table, metadata = load_pyarrow_dataset(
        path, storage_options=storage_options, conn=conn, name=name, **kwargs
    )
    if not lazy:
        table = table.to_table()
    if conn is None:
        conn = duckdb.connect()
    conn.register(name, table)
    return conn, metadata


@dataloader()
def register_delta_in_datafusion(
    path: str,
    storage_options: dict[str, str] | None = None,
    name: str | None = None,
    ctx: dtf.SessionContext | None = None,
    lazy: bool = True,
    **kwargs,
) -> tuple[dtf.SessionContext, dict]:
    if name is None:
        name = "delta_table"
    table, metadata = (
        load_pyarrow_dataset(
            path, storage_options=storage_options, name=name, **kwargs
        ),
    )

    if ctx is None:
        ctx = dtf.SessionContext()

    if not lazy:
        ctx.register_record_batches(name, [table.to_batches()])
    else:
        ctx.register_dataset(name, table)

    return ctx, metadata
