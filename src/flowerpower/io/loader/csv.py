import duckdb
import pandas as pd
import datafusion as dtf

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
def load_pandas_dataframe(
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
    include_file_path: bool = False,
    **kwargs,
) -> tuple[pd.DataFrame, dict]:
    """
    Load a CSV file(s) into a pandas DataFrame.

    Args:
        path: (str | list[str]) Path(s) to the CSV file(s).
        storage_options: (dict, optional) Optional storage options. Defaults to None.
        fs: (AbstractFileSystem, optional) Optional filesystem. Defaults to None.
        include_file_path: (bool, optional) Whether to load the file path as a column. Defaults to False.
        **kwargs: Additional keyword arguments to pass to `fs.read_csv`.

    Returns:
        tuple[pd.DataFrame, dict]: A tuple containing the DataFrame and metadata.
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    df = fs.read_csv(
        path, concat=True, include_file_path=include_file_path, **kwargs
    ).to_pandas()
    metadata = get_dataframe_metadata(df, path, format="csv", fs=fs, **kwargs)
    return df, metadata


@dataloader()
def load_polars_dataframe(
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
    include_file_path: bool = False,
    **kwargs,
) -> tuple[pl.DataFrame, dict]:
    """
    Load a CSV file(s) into a polars DataFrame.

    Args:
        path: (str | list[str]) Path(s) to the CSV file(s).
        storage_options: (dict, optional) Optional storage options. Defaults to None.
        fs: (AbstractFileSystem, optional) Optional filesystem. Defaults to None.
        include_file_path: (bool, optional) Whether to load the file path as a column. Defaults to False.
        **kwargs: Additional keyword arguments to pass to `fs.read_csv`.

    Returns:
        tuple[pl.DataFrame, dict]: A tuple containing the DataFrame and metadata.
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    df = fs.read_csv(path, concat=True, include_file_path=include_file_path, **kwargs)
    metadata = get_dataframe_metadata(df, path, format="csv", fs=fs, **kwargs)
    return df, metadata


@dataloader()
def load_polars_lazyframe(
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
    include_file_path: bool = False,
    **kwargs,
) -> tuple[pl.LazyFrame, dict]:
    """
    Load a CSV file(s) into a polars LazyFrame.

    Args:
        path: (str | list[str]) Path(s) to the CSV file(s).
        storage_options: (dict, optional) Optional storage options. Defaults to None.
        fs: (AbstractFileSystem, optional) Optional filesystem. Defaults to None.
        include_file_path: (bool, optional) Whether to load the file path as a column. Defaults to False.
        **kwargs: Additional keyword arguments to pass to `pd.read_csv`.

    Returns:
        tuple[pl.LazyFrame, dict]: A tuple containing the DataFrame and metadata.
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    df = fs.read_csv(path, concat=True, include_file_path=include_file_path, **kwargs)
    metadata = get_dataframe_metadata(df, path, format="csv", fs=fs, **kwargs)
    return df.lazy(), metadata


@dataloader()
def load_duckdb_relation(
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
    Load a CSV file into a DuckDB relation.

    Args:
        path: (str |list[str]) Path(s) to the CSV file(s). Use wildcards ('**/*.csv') to load multiple files.
        storage_options: (dict) Optional storage options.
        fs: (AbstractFileSystem) Optional filesystem.
        conn: (DuckDBPyConnection) Optional DuckDB connection.
        shape_metadata: (bool) Whether to include shape metadata.
        num_files_metadata: (bool) Whether to include the number of files metadata.
        **kwargs: Additional keyword arguments to pass to `duckdb.read_csv`.

    Returns:
        tuple[duckdb.DuckDBPyRelation, dict]: A tuple containing the relation and metadata
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    if conn is None:
        conn = duckdb.connect()

    conn.register_filesystem(fs)

    rel = conn.read_csv(path, **kwargs)
    metadata = get_duckdb_metadata(
        rel,
        path,
        format="csv",
        fs=fs,
        shape=shape_metadata,
        num_files=num_files_metadata,
        **kwargs,
    )
    return rel, metadata


@dataloader(
    name="csv_load_pyarrow_dataset",
    description="Register a PyArrow dataset in a DuckDB Connection.",
)
def load_pyarrow_dataset(
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
    Load a CSV file(s) into a PyArrow dataset.

    Args:
        path: (str) Path to the CSV file(s).
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
        path, schema=schema, partitioning=partitioning, format="csv", **kwargs
    )
    metadata = get_pyarrow_dataset_metadata(ds, path, format="csv", fs=fs, **kwargs)

    return ds, metadata


@dataloader(
    name="csv_register_in_duckdb",
    description="Register a PyArrow dataset in a DuckDB Connection.",
)
def register_in_duckdb(
    path: str | list[str],
    name: str | None = None,
    schema: pa.Schema | None = None,
    partitioning: str | list[str] | None = None,
    storage_options: dict[str, str] | None = None,
    include_file_path: bool = False,
    conn: duckdb.DuckDBPyConnection | None = None,
    lazy: bool = True,
    **kwargs,
) -> tuple[duckdb.DuckDBPyConnection, dict]:
    if name is None:
        name = "csv_pyarrow_dataset"

    table, metadata = load_pyarrow_dataset(
        path,
        schema=schema,
        partitioning=partitioning,
        storage_options=storage_options,
        include_file_path=include_file_path,
        name=name,
        **kwargs,
    )
    if not lazy:
        table = table.to_table()
    if conn is None:
        conn = duckdb.connect()
    conn.register(name, table)
    return conn, metadata


@dataloader(
    name="csv_register_in_datafusion",
    description="Register a PyArrow dataset in a Datafussion SessionContext.",
)
def register_in_datafusion(
    path: str | list[str],
    name: str | None = None,
    schema: pa.Schema | None = None,
    partitioning: str | list[str] | None = None,
    storage_options: dict[str, str] | None = None,
    ctx: dtf.SessionContext | None = None,
    lazy: bool = True,
    **kwargs,
) -> tuple[dtf.SessionContext, dict]:
    if name is None:
        name = "csv_pyarrow_dataset"
    table, metadata = (
        load_pyarrow_dataset(
            path,
            storage_options=storage_options,
            schema=schema,
            partitioning=partitioning,
            name=name,
            **kwargs,
        ),
    )

    if ctx is None:
        ctx = dtf.SessionContext()

    if not lazy:

        ctx.register_record_batches(name, [table.to_batches()])
    else:
        ctx.register_dataset(name, table)

    return ctx, metadata
