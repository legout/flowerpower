import duckdb
import pandas as pd
from ...helpers.polars import pl

from hamilton.function_modifiers import dataloader
from ..utils import (
    get_dataframe_metadata,
    get_duckdb_metadata,
    get_pyarrow_dataset_metadata,
)

from ...helpers.filesystem import get_filesytem
from ...helpers.storage_options import (
    AwsStorageOptions,
    GcsStorageOptions,
    AzureStorageOptions,
    GitHubStorageOptions,
    GitLabStorageOptions,
)
from fsspec import AbstractFileSystem
import pyarrow.dataset as pds
import pyarrow as pa


@dataloader()
def load_parquet_as_pandas_dataframe(
    path: str | list[str],
    storage_options: (
        AwsStorageOptions
        | GcsStorageOptions
        | AzureStorageOptions
        | GitHubStorageOptions
        | GitLabStorageOptions
        | dict[str, str]
        | None
    ) = None,
    fs: AbstractFileSystem | None = None,
    filename: bool = False,
    **kwargs,
) -> tuple[pd.DataFrame, dict]:
    """
    Load a Parquet file(s) into a pandas DataFrame.

    Args:
        path: (str | list[str]) Path(s) to the Parquet file(s).
        storage_options: (dict, optional) Optional storage options. Defaults to None.
        fs: (AbstractFileSystem, optional) Optional filesystem. Defaults to None.
        filename: (bool, optional) Whether to load the filename as a column. Defaults to False.
        **kwargs: Additional keyword arguments to pass to `fs.read_parquet`.

    Returns:
        tuple[pd.DataFrame, dict]: A tuple containing the DataFrame and metadata.
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    df = fs.read_parquet(path, concat=True, filename=filename, **kwargs).to_pandas()
    metadata = get_dataframe_metadata(df, path, format="parquet", fs=fs, **kwargs)
    return df, metadata


@dataloader()
def load_parquet_as_polars_dataframe(
    path: str | list[str],
    storage_options: (
        AwsStorageOptions
        | GcsStorageOptions
        | AzureStorageOptions
        | GitHubStorageOptions
        | GitLabStorageOptions
        | dict[str, str]
        | None
    ) = None,
    fs: AbstractFileSystem | None = None,
    filename: bool = False,
    **kwargs,
) -> tuple[pl.DataFrame, dict]:
    """
    Load a Parquet file(s) into a polars DataFrame.

    Args:
        path: (str | list[str]) Path(s) to the Parquet file(s).
        storage_options: (dict, optional) Optional storage options. Defaults to None.
        fs: (AbstractFileSystem, optional) Optional filesystem. Defaults to None.
        filename: (bool, optional) Whether to load the filename as a column. Defaults to False.
        **kwargs: Additional keyword arguments to pass to `fs.read_parquet`.

    Returns:
        tuple[pl.DataFrame, dict]: A tuple containing the DataFrame and metadata.
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    df = fs.read_parquet_dataset(path, concat=True, filename=filename, **kwargs)
    metadata = get_dataframe_metadata(df, path, format="parquet", fs=fs, **kwargs)
    return df, metadata


@dataloader()
def load_parquet_as_polars_lazyframe(
    path: str | list[str],
    storage_options: (
        AwsStorageOptions
        | GcsStorageOptions
        | AzureStorageOptions
        | GitHubStorageOptions
        | GitLabStorageOptions
        | dict[str, str]
        | None
    ) = None,
    fs: AbstractFileSystem | None = None,
    filename: bool = False,
    **kwargs,
) -> tuple[pl.LazyFrame, dict]:
    """
    Load a Parquet file(s) into a polars LazyFrame.

    Args:
        path: (str | list[str]) Path(s) to the Parquet file(s).
        storage_options: (dict, optional) Optional storage options. Defaults to None.
        fs: (AbstractFileSystem, optional) Optional filesystem. Defaults to None.
        filename: (bool, optional) Whether to load the filename as a column. Defaults to False.
        **kwargs: Additional keyword arguments to pass to `pd.read_parquet`.

    Returns:
        tuple[pl.LazyFrame, dict]: A tuple containing the DataFrame and metadata.
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    df = fs.read_parquet_dataset(path, concat=True, filename=filename, **kwargs)
    metadata = get_dataframe_metadata(df, path, format="parquet", fs=fs, **kwargs)
    return df.lazy(), metadata


@dataloader()
def load_parquet_as_duckdb_relation(
    path: str,
    storage_options: (
        AwsStorageOptions
        | GcsStorageOptions
        | AzureStorageOptions
        | GitHubStorageOptions
        | GitLabStorageOptions
        | dict[str, str]
        | None
    ) = None,
    fs: AbstractFileSystem | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
    shape_metadata: bool = False,
    num_files_metadata: bool = True,
    **kwargs,
) -> tuple[duckdb.DuckDBPyRelation, dict]:
    """
    Load a Parquet file into a DuckDB relation.

    Args:
        path: (str |list[str]) Path(s) to the Parquet file(s). Use wildcards ('**/*.parquet') to load multiple files.
        storage_options: (dict) Optional storage options.
        fs: (AbstractFileSystem) Optional filesystem.
        conn: (DuckDBPyConnection) Optional DuckDB connection.
        shape_metadata: (bool) Whether to include shape metadata.
        num_files_metadata: (bool) Whether to include the number of files metadata.
        **kwargs: Additional keyword arguments to pass to `duckdb.read_parquet`.

    Returns:
        tuple[duckdb.DuckDBPyRelation, dict]: A tuple containing the relation and metadata
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    if conn is None:
        conn = duckdb.connect()

    conn.register_filesystem(fs)

    rel = conn.read_parquet(path, **kwargs)
    metadata = get_duckdb_metadata(
        rel,
        path,
        format="parquet",
        fs=fs,
        shape=shape_metadata,
        num_files=num_files_metadata,
        **kwargs,
    )
    return rel, metadata


@dataloader()
def load_parquet_as_pyarrow_dataset(
    path: str,
    storage_options: (
        AwsStorageOptions
        | GcsStorageOptions
        | AzureStorageOptions
        | GitHubStorageOptions
        | GitLabStorageOptions
        | dict[str, str]
        | None
    ) = None,
    fs: AbstractFileSystem | None = None,
    schema: pa.Schema | None = None,
    partitioning: str | list[str] | None = None,
    **kwargs,
) -> tuple[pds.Dataset, dict]:
    """
    Load a Parquet file(s) into a PyArrow dataset.

    Args:
        path: (str) Path to the Parquet file(s).
        storage_options: (dict) Optional storage options.
        fs: (AbstractFileSystem) Optional filesystem.
        schema: (pa.Schema) Optional schema.
        partitioning: (str | list[str]) Optional partitioning.
        **kwargs: Additional keyword arguments to pass to `pds.dataset`.

    Returns:
        tuple[pds.Dataset, dict]: A tuple containing the dataset and metadata.
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    ds = fs.pyarrow_dataset(
        path, schema=schema, partitioning=partitioning, format="parquet", **kwargs
    )
    metadata = get_pyarrow_dataset_metadata(ds, path, format="parquet", fs=fs, **kwargs)

    return ds, metadata
