import datetime as dt

import duckdb
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.dataset as pds
from deltalake import DeltaTable
from fsspec import AbstractFileSystem
import importlib


def get_serializable_schema(
    data: (
        pd.DataFrame
        | pl.DataFrame
        | pl.LazyFrame
        | duckdb.DuckDBPyRelation
        | pa.Table
        | pa.Schema
    ),
) -> dict[str, str]:
    """
    Convert DataFrame dtypes to a serializable dictionary.

    Args:
        data:  DataFrame

    Returns:
        dict mapping column names to dtype strings
    """
    if isinstance(data, pd.DataFrame):
        return {col: str(dtype) for col, dtype in data.dtypes.items()}
    elif isinstance(data, pl.DataFrame):
        return data.schema.to_python()
    elif isinstance(data, pl.LazyFrame):
        return data.collect_schema().to_python()
    elif isinstance(data, duckdb.DuckDBPyRelation):
        return dict(zip(data.columns, [str(dtype) for dtype in data.types]))
    elif isinstance(
        data, pa.Table | pa.RecordBatch | pa.RecordBatchReader | pds.Dataset
    ):
        return dict(zip(data.schema.names, [str(dtype) for dtype in data.schema.types]))
    elif isinstance(data, pa.Schema):
        return dict(zip(data.names, [str(dtype) for dtype in data.types]))


def get_dataframe_metadata(
    df: pd.DataFrame | pl.DataFrame | pl.LazyFrame | pa.Table,
    path: str | list[str],
    format: str,
    topic: str | None = None,
    fs: AbstractFileSystem | None = None,
    **kwargs,
) -> dict:
    """
    Get metadata for a DataFrame.

    Args:
        df: DataFrame
        path: Path to the file(s) that the DataFrame was loaded from
        fs: Optional filesystem
        kwargs: Additional metadata fields

    Returns:
        dict: DataFrame metadata
    """
    schema = get_serializable_schema(df)

    if path is not None:
        if isinstance(path, list):
            num_files = len(path)
        else:
            if "*" in path:
                if fs is None:
                    num_files = None
                else:
                    num_files = len(fs.glob(path))
            else:
                num_files = 1
    else:
        num_files = None

    metadata = {
        "path": path,
        "topic": topic,
        "format": format,
        "timestamp": dt.datetime.now().timestamp(),
        "schema": schema,
        # "partition_columns": None,
        "num_columns": len(schema),
        "num_rows": df.shape[0] if hasattr(df, "shape") else None,
        "num_files": num_files,
        "name": kwargs.get("name", None),
        "description": kwargs.get("description", None),
        "id": kwargs.get("id", None),
    }
    return {k: v for k, v in metadata.items() if v is not None}


def get_duckdb_metadata(
    rel: duckdb.DuckDBPyRelation,
    path: str,
    format: str,
    fs: AbstractFileSystem | None = None,
    include_shape: bool = False,
    include_num_files: bool = False,
    **kwargs,
) -> dict:
    """
    Get metadata for a DuckDBPyRelation.

    Args:
        rel: DuckDBPyRelation
        path: Path to the file(s) that the DuckDBPyRelation was loaded from
        fs: Filesystem
        include_shape: Include shape in metadata
        include_num_files: Include number of files in metadata
        kwargs: Additional metadata fields

    Returns:
        dict: DuckDBPyRelation metadata
    """

    schema = get_serializable_schema(rel)
    if include_shape:
        shape = rel.shape
    else:
        shape = None

    metadata = {
        "path": path,
        "format": format,
        "timestamp": dt.datetime.now().timestamp(),
        "schema": schema,
        "num_columns": shape[1] if shape else None,
        "num_rows": shape[0] if shape else None,
        "num_files": len(fs.glob(path)) if include_num_files else None,
        "name": kwargs.get("name", None),
        "description": kwargs.get("description", None),
        "id": kwargs.get("id", None),
    }
    return {k: v for k, v in metadata.items() if v is not None}


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
        "partition_columns": ds.partitioning.schema.names if ds.partitioning else None,
        "num_columns": len(ds.schema),
        "num_rows": None,
        "num_files": len(ds.files),
        "name": kwargs.get("name", None),
        "description": kwargs.get("description", None),
        "id": kwargs.get("id", None),
    }
    return metadata


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
        "schema": dict(zip(dt_schema.names, [str(x) for x in dt_schema.types])),
        "partition_columns": dt_meta.partition_columns,
        "num_columns": len(dt_schema),
        "num_rows": None,
        "num_files": len(dtable.files()),
        "name": dt_meta.name or kwargs.get("name", None),
        "description": dt_meta.description or kwargs.get("description", None),
        "id": dt_meta.metadata().id or kwargs.get("id", None),
    }

    return {k: v for k, v in metadata.items() if v is not None}


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
            "name": kwargs.get("name", None),
            "description": kwargs.get("description", None),
            "id": kwargs.get("id", None),
        }
        return metadata

else:

    def get_mqtt_metadata(*args, **kwargs):
        raise ImportError("orjson not installed")
