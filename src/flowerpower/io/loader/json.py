import duckdb
import pandas as pd
from ...helpers.polars import pl

from hamilton.function_modifiers import dataloader
from ..utils import get_dataframe_metadata, get_duckdb_metadata
from ...helpers.filesystem import get_filesytem
from ...helpers.storage_options import (
    AwsStorageOptions,
    GcsStorageOptions,
    AzureStorageOptions,
    GitHubStorageOptions,
    GitLabStorageOptions,
)
from fsspec import AbstractFileSystem


@dataloader()
def load_json_as_pandas_dataframe(
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
    jsonlines: bool = False,
    **kwargs,
) -> tuple[pd.DataFrame, dict]:
    """
    Load a JSON file(s) into a pandas DataFrame.

    Args:
        path: (str | list[str]) Path(s) to the JSON file(s).
        storage_options: (dict, optional) Optional storage options. Defaults to None.
        fs: (AbstractFileSystem, optional) Optional filesystem. Defaults to None.
        filename: (bool, optional) Whether to load the filename as a column. Defaults to False.
        jsonlines: (bool, optional) Whether the file is in jsonlines format. Defaults to False.
        **kwargs: Additional keyword arguments to pass to `fs.read_json_dataset`.

    Returns:
        tuple[pd.DataFrame, dict]: A tuple containing the DataFrame and metadata.
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    df = fs.read_json_dataset(
        path, concat=True, filename=filename, jsonlines=jsonlines, **kwargs
    ).to_pandas()
    metadata = get_dataframe_metadata(df, path, format="json", fs=fs, **kwargs)
    return df, metadata


@dataloader()
def load_json_as_polars_dataframe(
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
    jsonlines: bool = False,
    **kwargs,
) -> tuple[pl.DataFrame, dict]:
    """
    Load a JSON file(s) into a polars DataFrame.

    Args:
        path: (str | list[str]) Path(s) to the JSON file(s).
        storage_options: (dict, optional) Optional storage options. Defaults to None.
        fs: (AbstractFileSystem, optional) Optional filesystem. Defaults to None.
        filename: (bool, optional) Whether to load the filename as a column. Defaults to False.
        jsonlines: (bool, optional) Whether the file is in jsonlines format. Defaults to False.
        **kwargs: Additional keyword arguments to pass to `fs.read_json_dataset`.

    Returns:
        tuple[pl.DataFrame, dict]: A tuple containing the DataFrame and metadata.
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    df = fs.read_json_dataset(
        path, concat=True, filename=filename, jsonlines=jsonlines, **kwargs
    )
    metadata = get_dataframe_metadata(df, path, format="json", fs=fs, **kwargs)
    return df, metadata


@dataloader()
def load_json_as_polars_lazyframe(
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
    jsonlines: bool = False,
    **kwargs,
) -> tuple[pl.LazyFrame, dict]:
    """
    Load a JSON file(s) into a polars LazyFrame.

    Args:
        path: (str | list[str]) Path(s) to the JSON file(s).
        storage_options: (dict, optional) Optional storage options. Defaults to None.
        fs: (AbstractFileSystem, optional) Optional filesystem. Defaults to None.
        filename: (bool, optional) Whether to load the filename as a column. Defaults to False.
        jsonlines: (bool, optional) Whether the file is in jsonlines format. Defaults to False.
        **kwargs: Additional keyword arguments to pass to `fs.read_json_dataset`.

    Returns:
        tuple[pl.LazyFrame, dict]: A tuple containing the DataFrame and metadata.
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    df = fs.read_json_dataset(
        path, concat=True, filename=filename, jsonlines=jsonlines, **kwargs
    )
    metadata = get_dataframe_metadata(df, path, format="json", fs=fs, **kwargs)
    return df.lazy(), metadata


@dataloader()
def load_json_as_duckdb_relation(
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
    include_shape_metadata: bool = False,
    include_num_files_metadata: bool = False,
    **kwargs,
) -> tuple[duckdb.DuckDBPyRelation, dict]:
    """
    Load a JSON file(s) into a DuckDB relation.

    Args:
        path: (str |list[str]) Path(s) to the JSON file(s). Use wildcards ('**/*.json') to load multiple files.
        storage_options: (dict) Optional storage options.
        fs: (AbstractFileSystem) Optional filesystem.
        conn: (DuckDBPyConnection) Optional DuckDB connection.
        include_shape_metadata: (bool) Whether to include shape metadata.
        include_num_files_metadata: (bool) Whether to include number of files metadata.
        **kwargs: Additional keyword arguments to pass to `duckdb.read_json`.

    Returns:
        tuple[duckdb.DuckDBPyRelation, dict]: A tuple containing the relation and metadata
    """
    if fs is None:
        fs = get_filesytem(path, storage_options)
    if conn is None:
        conn = duckdb.connect()

    conn.register_filesystem(fs)

    rel = conn.read_json(path, **kwargs)
    metadata = get_duckdb_metadata(
        rel,
        path,
        format="json",
        fs=fs,
        include_shape=include_shape_metadata,
        include_num_files=include_num_files_metadata**kwargs,
    )
    return rel, metadata
