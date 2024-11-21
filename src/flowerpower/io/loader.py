import pathlib
from dataclasses import dataclass
from typing import Any, Collection, Iterable, Type

import datafusion as df
import duckdb as ddb
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.dataset as pds
from deltalake import ArrowStreamExportable, DeltaTable, write_deltalake_table
from hamilton.io import utils
from hamilton.io.data_adapters import DataLoader, DataSaver


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
