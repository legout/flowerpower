from dataclasses import dataclass
from hamilton.io.data_adapters import DataLoader, DataSaver
from hamilton.io import utils
import pathlib
from typing import Collection, Type, Any, Iterable
from deltalake import DeltaTable, write_deltalake_table, ArrowStreamExportable
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pds
import polars as pl
import duckdb as ddb
import datafusion as df


def load_delta_table(
    path: str, storage_options: dict[str, str], **kwargs
) -> DeltaTable:
    return DeltaTable(path, storage_options=storage_options, **kwargs)


def load_pyarrow_table_from_delta(
    path: str, storage_options: dict[str, str], **kwargs
) -> pa.Table:
    return load_delta_table(
        path, storage_options=storage_options, **kwargs
    ).to_pyarrow_table()


def load_pyarrow_dataset_from_delta(
    path: str, storage_options: dict[str, str], **kwargs
) -> pds.Dataset:
    return load_delta_table(
        path, storage_options=storage_options, **kwargs
    ).to_pyarrow_dataset()


def load_pandas_dataframe_from_delta(
    path: str, storage_options: dict[str, str], **kwargs
) -> pd.DataFrame:
    return load_pyarrow_table_from_delta(
        path, storage_options=storage_options, **kwargs
    ).to_pandas()


def load_polars_dataframe_from_delta(
    path: str, storage_options: dict[str, str], **kwargs
) -> pl.DataFrame:
    return pl.from_arrow(
        load_pyarrow_table_from_delta(path, storage_options=storage_options, **kwargs)
    )


def load_polars_lazyframe_from_delta(
    path: str, storage_options: dict[str, str], **kwargs
) -> pl.LazyFrame:
    return pl.scan_pyarrow_dataset(
        load_pyarrow_dataset_from_delta(path, storage_options=storage_options, **kwargs)
    )


def load_duckdb_table_from_delta(
    path: str, storage_options: dict[str, str], **kwargs
) -> ddb.DataFrame:
    return ddb.from_arrow(
        load_pyarrow_dataset_from_delta(path, storage_options=storage_options, **kwargs)
    )


def load_datafusion_ctx_from_delta(
    path: str, storage_options: dict[str, str], name="delta_table", **kwargs
) -> df.SessionContext:
    ctx = df.SessionContext()
    return ctx.register_dataset(
        name,
        load_pyarrow_dataset_from_delta(
            path, storage_options=storage_options, **kwargs
        ),
    )
