import datetime as dt
import importlib

import duckdb
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.dataset as pds
from deltalake import DeltaTable
from fsspec import AbstractFileSystem

from .fs.ext import path_to_glob

# Helper to filter out None values from metadata dicts
def _filter_metadata(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}

def get_serializable_schema(
    data: (
        pd.DataFrame
        | pl.DataFrame
        | pl.LazyFrame
        | duckdb.DuckDBPyRelation
        | pa.Table
        | pa.Schema
        | pa.RecordBatch
        | pa.RecordBatchReader
        | pds.Dataset
    ),
) -> dict[str, str]:
    """
    Convert DataFrame or similar object dtypes to a serializable dictionary.
    """
    if isinstance(data, pd.DataFrame):
        return {col: str(dtype) for col, dtype in data.dtypes.items()}
    if isinstance(data, pl.DataFrame):
        return data.schema.to_python()
    if isinstance(data, pl.LazyFrame):
        return data.collect_schema().to_python()
    if isinstance(data, duckdb.DuckDBPyRelation):
        return dict(zip(data.columns, map(str, data.types)))
    if isinstance(data, (pa.Table, pa.RecordBatch, pa.RecordBatchReader, pds.Dataset)):
        return dict(zip(data.schema.names, map(str, data.schema.types)))
    if isinstance(data, pa.Schema):
        return dict(zip(data.names, map(str, data.types)))
    # Fallback: try to treat as dict-like
    if hasattr(data, "items"):
        return {k: str(v) for k, v in data.items()}
    return {}

def get_dataframe_metadata(
    df: (
        pd.DataFrame
        | pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | pa.RecordBatch
        | pa.RecordBatchReader
        | list[
            pd.DataFrame
            | pl.DataFrame
            | pl.LazyFrame
            | pa.Table
            | pa.RecordBatch
            | pa.RecordBatchReader
        ]
    ),
    path: str | list[str] | None = None,
    format: str | None = None,
    topic: str | None = None,
    num_files: int | None = None,
    partition_columns: list[str] | None = None,
    fs: AbstractFileSystem | None = None,
    **kwargs,
) -> dict:
    """
    Get metadata for a DataFrame or list of DataFrames.
    """
    if isinstance(df, list):
        schema = get_serializable_schema(df[0])
        num_rows = sum(getattr(df_, "shape", [None])[0] or 0 for df_ in df)
    else:
        schema = get_serializable_schema(df)
        num_rows = getattr(df, "shape", [None])[0] if hasattr(df, "shape") else None

    if path is not None and num_files is None:
        if isinstance(path, list):
            num_files = len(path)
        else:
            path_ = path_to_glob(path=path, format=format)
            num_files = len(fs.glob(path_)) if fs is not None else None

    if partition_columns is not None:
        schema = {k: v for k, v in schema.items() if k not in partition_columns}

    metadata = {
        "path": path,
        "topic": topic,
        "format": format,
        "timestamp": int(dt.datetime.now().timestamp() * 1000),
        "schema": schema,
        "partition_columns": partition_columns,
        "num_columns": len(schema),
        "num_rows": num_rows,
        "num_files": num_files,
        "name": kwargs.get("name"),
        "description": kwargs.get("description"),
        "id": kwargs.get("id"),
    }
    return _filter_metadata(metadata)


def get_duckdb_metadata(
    rel: duckdb.DuckDBPyRelation,
    path: str,
    format: str,
    fs: AbstractFileSystem | None = None,
    include_shape: bool = False,
    include_num_files: bool = False,
    partition_columns: list[str] | None = None,
    **kwargs,
) -> dict:
    """
    Get metadata for a DuckDBPyRelation.
    """
    schema = get_serializable_schema(rel)
    shape = rel.shape if include_shape else None
    if partition_columns is not None:
        schema = {k: v for k, v in schema.items() if k not in partition_columns}

    metadata = {
        "path": path,
        "format": format,
        "timestamp": dt.datetime.now().timestamp(),
        "schema": schema,
        "partition_columns": partition_columns,
        "num_columns": shape[1] if shape else None,
        "num_rows": shape[0] if shape else None,
        "num_files": len(fs.glob(path)) if (include_num_files and fs is not None) else None,
        "name": kwargs.get("name"),
        "description": kwargs.get("description"),
        "id": kwargs.get("id"),
    }
    return _filter_metadata(metadata)


def get_pyarrow_dataset_metadata(
    ds: pds.Dataset,
    path: str,
    format: str,
    **kwargs,
) -> dict:
    schema = get_serializable_schema(ds.schema)
    metadata = {
        "path": path,
        "format": format,
        "timestamp": dt.datetime.now().timestamp(),
        "schema": schema,
        "partition_columns": ds.partitioning.schema.names if getattr(ds, "partitioning", None) else None,
        "num_columns": len(ds.schema),
        "num_rows": None,
        "num_files": len(ds.files),
        "name": kwargs.get("name"),
        "description": kwargs.get("description"),
        "id": kwargs.get("id"),
    }
    return _filter_metadata(metadata)


def get_delta_metadata(
    dtable: DeltaTable,
    path: str,
    **kwargs,
) -> dict:
    dt_meta = dtable.metadata()
    dt_schema = dtable.schema().to_pyarrow()
    metadata = {
        "path": path,
        "format": "delta",
        "timestamp": dt.datetime.now().timestamp(),
        "schema": dict(zip(dt_schema.names, map(str, dt_schema.types))),
        "partition_columns": getattr(dt_meta, "partition_columns", None),
        "num_columns": len(dt_schema),
        "num_files": len(dtable.files()),
        "name": getattr(dt_meta, "name", None) or kwargs.get("name"),
        "description": getattr(dt_meta, "description", None) or kwargs.get("description"),
        "id": getattr(dt_meta, "id", None) or kwargs.get("id"),
    }
    return _filter_metadata(metadata)


if importlib.util.find_spec("orjson"):
    import orjson

    def get_mqtt_metadata(
        payload: bytes | dict[str, any],
        topic: str | None = None,
        **kwargs,
    ) -> dict:
        if isinstance(payload, bytes):
            payload = orjson.loads(payload)
        schema = get_serializable_schema(payload)
        metadata = {
            "topic": topic,
            "format": "mqtt",
            "timestamp": dt.datetime.now().timestamp(),
            "schema": schema,
            "num_columns": len(schema),
            "num_rows": len(payload),
            "name": kwargs.get("name"),
            "description": kwargs.get("description"),
            "id": kwargs.get("id"),
        }
        return _filter_metadata(metadata)
else:
    def get_mqtt_metadata(*args, **kwargs):
        raise ImportError("orjson not installed")
