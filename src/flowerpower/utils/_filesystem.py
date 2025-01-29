import base64
import datetime as dt
import inspect
import os
import posixpath
import urllib
import uuid
from pathlib import Path
from typing import Generator

import fsspec
import orjson
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pds
import pyarrow.parquet as pq
import requests
from fsspec import filesystem
from fsspec.implementations.cache_mapper import AbstractCacheMapper
from fsspec.implementations.cached import SimpleCacheFileSystem
from fsspec.implementations.dirfs import DirFileSystem
from fsspec.implementations.memory import MemoryFile
from fsspec.spec import AbstractFileSystem
from fsspec.utils import infer_storage_options
from loguru import logger

from .misc import convert_large_types_to_standard, run_parallel
from .polars import pl
from .storage_options import (
    AwsStorageOptions,
    AzureStorageOptions,
    GcsStorageOptions,
    GitHubStorageOptions,
    GitLabStorageOptions,
    get_storage_options,
)


class FileNameCacheMapper(AbstractCacheMapper):
    def __init__(self, directory):
        self.directory = directory

    def __call__(self, path: str) -> str:
        os.makedirs(
            posixpath.dirname(posixpath.join(self.directory, path)), exist_ok=True
        )
        return path


class MonitoredSimpleCacheFileSystem(SimpleCacheFileSystem):
    def __init__(self, **kwargs):
        # kwargs["cache_storage"] = posixpath.join(
        #    kwargs.get("cache_storage"), kwargs.get("fs").protocol[0]
        # )
        self._verbose = kwargs.get("verbose", False)
        super().__init__(**kwargs)
        self._mapper = FileNameCacheMapper(kwargs.get("cache_storage"))

    def _check_file(self, path):
        self._check_cache()
        cache_path = self._mapper(path)
        for storage in self.storage:
            fn = posixpath.join(storage, cache_path)
            if posixpath.exists(fn):
                return fn
            if self._verbose:
                logger.info(f"Downloading {self.protocol[0]}://{path}")

    # def glob(self, path):
    #    return [self._strip_protocol(path)]

    def size(self, path):
        cached_file = self._check_file(self._strip_protocol(path))
        if cached_file is None:
            return self.fs.size(path)
        else:
            return posixpath.getsize(cached_file)

    def sync(self, reload: bool = False):
        if reload:
            self.clear_cache()
        content = self.glob("**/*")
        [self.open(f).close() for f in content if self.isfile(f)]

    def __getattribute__(self, item):
        if item in {
            # new items
            "size",
            "glob",
            "sync",
            # previous
            "load_cache",
            "_open",
            "save_cache",
            "close_and_update",
            "__init__",
            "__getattribute__",
            "__reduce__",
            "_make_local_details",
            "open",
            "cat",
            "cat_file",
            "cat_ranges",
            "get",
            "read_block",
            "tail",
            "head",
            "info",
            "ls",
            "exists",
            "isfile",
            "isdir",
            "_check_file",
            "_check_cache",
            "_mkcache",
            "clear_cache",
            "clear_expired_cache",
            "pop_from_cache",
            "local_file",
            "_paths_from_path",
            "get_mapper",
            "open_many",
            "commit_many",
            "hash_name",
            "__hash__",
            "__eq__",
            "to_json",
            "to_dict",
            "cache_size",
            "pipe_file",
            "pipe",
            "start_transaction",
            "end_transaction",
        }:
            # all the methods defined in this class. Note `open` here, since
            # it calls `_open`, but is actually in superclass
            return lambda *args, **kw: getattr(type(self), item).__get__(self)(
                *args, **kw
            )
        if item in ["__reduce_ex__"]:
            raise AttributeError
        if item in ["transaction"]:
            # property
            return type(self).transaction.__get__(self)
        if item in ["_cache", "transaction_type"]:
            # class attributes
            return getattr(type(self), item)
        if item == "__class__":
            return type(self)
        d = object.__getattribute__(self, "__dict__")
        fs = d.get("fs", None)  # fs is not immediately defined
        if item in d:
            return d[item]
        elif fs is not None:
            if item in fs.__dict__:
                # attribute of instance
                return fs.__dict__[item]
            # attributed belonging to the target filesystem
            cls = type(fs)
            m = getattr(cls, item)
            if (inspect.isfunction(m) or inspect.isdatadescriptor(m)) and (
                not hasattr(m, "__self__") or m.__self__ is None
            ):
                # instance method
                return m.__get__(fs, cls)
            return m  # class method or attribute
        else:
            # attributes of the superclass, while target is being set up
            return super().__getattribute__(item)


class GitLabFileSystem(AbstractFileSystem):
    def __init__(
        self,
        project_name: str | None = None,
        project_id: str | None = None,
        access_token: str | None = None,
        branch: str = "main",
        base_url: str = "https://gitlab.com",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.project_name = project_name
        self.project_id = project_id
        self.access_token = access_token
        self.branch = branch
        self.base_url = base_url.rstrip("/")
        self._validate_init()
        if not self.project_id:
            self.project_id = self._get_project_id()

    def _validate_init(self):
        if not self.project_id and not self.project_name:
            raise ValueError("Either 'project_id' or 'project_name' must be provided")

    def _get_project_id(self):
        url = f"{self.base_url}/api/v4/projects"
        headers = {"PRIVATE-TOKEN": self.access_token}
        params = {"search": self.project_name}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            projects = response.json()
            for project in projects:
                if project["name"] == self.project_name:
                    return project["id"]
            raise ValueError(f"Project '{self.project_name}' not found")
        else:
            response.raise_for_status()

    def _open(self, path, mode="rb", **kwargs):
        if mode != "rb":
            raise NotImplementedError("Only read mode is supported")

        url = (
            f"{self.base_url}/api/v4/projects/{self.project_id}/repository/files/"
            f"{urllib.parse.quote_plus(path)}?ref={self.branch}"
        )
        headers = {"PRIVATE-TOKEN": self.access_token}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            file_content = base64.b64decode(response.json()["content"])
            return MemoryFile(None, None, file_content)
        else:
            response.raise_for_status()

    def _ls(self, path, detail=False, **kwargs):
        url = f"{self.base_url}/api/v4/projects/{self.project_id}/repository/tree?path={path}&ref={self.branch}"
        headers = {"PRIVATE-TOKEN": self.access_token}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            files = response.json()
            if detail:
                return files
            else:
                return [file["name"] for file in files]
        else:
            response.raise_for_status()


try:
    fsspec.register_implementation("gitlab", GitLabFileSystem)
except ValueError as e:
    _ = e


# Original ls Methode speichern
dirfs_ls_o = DirFileSystem.ls
mscf_ls_o = MonitoredSimpleCacheFileSystem.ls


# Neue ls Methode definieren
def dir_ls_p(self, path, detail=False, **kwargs):
    return dirfs_ls_o(self, path, detail=detail, **kwargs)


def mscf_ls_p(self, path, detail=False, **kwargs):
    return mscf_ls_o(self, path, detail=detail, **kwargs)


def read_json_file(
    path, self, include_file_path: bool = False, jsonlines: bool = False
) -> dict | list[dict]:
    with self.open(path) as f:
        if jsonlines:
            data = [orjson.loads(line) for line in f.readlines()]
        else:
            data = orjson.loads(f.read())
    if include_file_path:
        return {path: data}
    return data


def _read_json(
    self,
    path: str | list[str],
    include_file_path: bool = False,
    use_threads: bool = True,
    jsonlines: bool = False,
    as_dataframe: bool = True,
    concat: bool = True,
    verbose: bool = False,
    **kwargs,
) -> dict | list[dict] | pl.DataFrame | list[pl.DataFrame]:
    """
    Read a JSON file or a list of JSON files.

    Args:
        path: (str | list[str]) Path to the JSON file(s).
        include_file_path: (bool, optional) If True, return a dictionary with the file path as key.
            Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        jsonlines: (bool, optional) If True, read JSON lines. Defaults to False.
        as_dataframe: (bool, optional) If True, return a DataFrame. Defaults to True.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (dict | list[dict] | pl.DataFrame | list[pl.DataFrame]):
            Dictionary, list of dictionaries, DataFrame or list of DataFrames.
    """
    if isinstance(path, str):
        if "**" in path:
            path = self.glob(path)
        else:
            if ".json" not in posixpath.basename(path):
                path = posixpath.join(path, "**/*.jsonl" if jsonlines else "**/*.json")
                path = self.glob(path)

    if isinstance(path, list):
        if use_threads:
            data = run_parallel(
                read_json_file,
                path,
                self=self,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        data = [
            read_json_file(
                path=p,
                self=self,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
            )
            for p in path
        ]
    data = read_json_file(
        path=path, self=self, include_file_path=include_file_path, jsonlines=jsonlines
    )
    if as_dataframe:
        if not include_file_path:
            data = pl.DataFrame(data)
        else:
            data = pl.DataFrame(list(data.values())[0]).with_columns(
                pl.lit(list(data.keys())[0]).alias("file_path")
            )
        if concat:
            return pl.concat(data, how="diagonal_relaxed")
    return data


def _read_json_batches(
    self,
    path: str | list[str],
    num_batches: int = 1,
    include_file_path: bool = False,
    jsonlines: bool = False,
    as_dataframe: bool = True,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> Generator[dict | list[dict] | pl.DataFrame | list[pl.DataFrame], None, None]:
    """
    Read JSON files in batches with optional parallel processing within batches.

    Args:
        path: (str | list[str]) Path to the JSON file(s).
        num_batches: (int) Number of files per batch. Defaults to 1.
        include_file_path: (bool) If True, return with file path as key.
        jsonlines: (bool) If True, read JSON lines. Defaults to False.
        as_dataframe: (bool) If True, return DataFrame. Defaults to True.
        concat: (bool) If True, concatenate batch DataFrames. Defaults to True.
        use_threads: (bool) If True, use parallel processing within batches.
        verbose: (bool) If True, print verbose output.
        **kwargs: Additional keyword arguments.

    Yields:
        Data from num_batches files as dict/DataFrame based on parameters.
    """
    # Handle path resolution
    if isinstance(path, str):
        if "**" in path:
            path = self.glob(path)
        else:
            if ".json" not in posixpath.basename(path):
                path = posixpath.join(path, "**/*.jsonl" if jsonlines else "**/*.json")
                path = self.glob(path)

    if isinstance(path, str):
        path = [path]

    # Process files in batches
    for i in range(0, len(path), num_batches):
        batch_paths = path[i : i + num_batches]

        # Read batch with optional parallelization
        if use_threads and len(batch_paths) > 1:
            batch_data = run_parallel(
                read_json_file,
                batch_paths,
                self=self,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        else:
            batch_data = [
                read_json_file(
                    path=p,
                    self=self,
                    include_file_path=include_file_path,
                    jsonlines=jsonlines,
                )
                for p in batch_paths
            ]

        if as_dataframe:
            if not include_file_path:
                batch_dfs = [pl.DataFrame(d) for d in batch_data]
            else:
                batch_dfs = [
                    pl.DataFrame(list(d.values())[0]).with_columns(
                        pl.lit(list(d.keys())[0]).alias("file_path")
                    )
                    for d in batch_data
                ]

            if concat and len(batch_dfs) > 1:
                yield pl.concat(batch_dfs, how="diagonal_relaxed")
            else:
                yield batch_dfs
        else:
            yield batch_data


def read_json(
    self,
    path: str | list[str],
    num_batches: int | None = None,
    include_file_path: bool = False,
    jsonlines: bool = False,
    as_dataframe: bool = True,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> (
    dict
    | list[dict]
    | pl.DataFrame
    | list[pl.DataFrame]
    | Generator[dict | list[dict] | pl.DataFrame | list[pl.DataFrame], None, None]
):
    """
    Read a JSON file or a list of JSON files. Optionally read in batches,
    returning a generator that sequentially yields data for specified number of files.

    Args:
        path: (str | list[str]) Path to the JSON file(s).
        num_batches: (int, optional) Number of files to process in each batch. Defaults to 1.
        include_file_path: (bool) If True, return with file path as key.
        jsonlines: (bool) If True, read JSON lines. Defaults to False.
        as_dataframe: (bool) If True, return DataFrame. Defaults to True.
        concat: (bool) If True, concatenate the DataFrames. Defaults to True.
        use_threads: (bool) If True, use parallel processing within batches. Defaults to True.
        verbose: (bool) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (dict | list[dict] | pl.DataFrame | list[pl.DataFrame]:
            Dictionary, list of dictionaries, DataFrame, list of DataFrames
    Yields:
        (dict | list[dict] | pl.DataFrame | list[pl.DataFrame]:
            Dictionary, list of dictionaries, DataFrame, list of DataFrames
    """
    if num_batches is not None:
        yield from _read_json_batches(
            self=self,
            path=path,
            num_batches=num_batches,
            include_file_path=include_file_path,
            jsonlines=jsonlines,
            as_dataframe=as_dataframe,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            **kwargs,
        )
    return _read_json(
        self=self,
        path=path,
        include_file_path=include_file_path,
        jsonlines=jsonlines,
        as_dataframe=as_dataframe,
        concat=concat,
        use_threads=use_threads,
        verbose=verbose,
        **kwargs,
    )


def read_csv_file(
    path, self, include_file_path: bool = False, **kwargs
) -> pl.DataFrame:
    with self.open(path) as f:
        df = pl.read_csv(f, **kwargs)
    if include_file_path:
        return df.with_columns(pl.lit(path).alias("file_path"))
    return df


def _read_csv(
    self,
    path: str | list[str],
    include_file_path: bool = False,
    use_threads: bool = True,
    concat: bool = True,
    verbose: bool = False,
    **kwargs,
) -> pl.DataFrame | list[pl.DataFrame]:
    """
    Read a CSV file or a list of CSV files into a polars DataFrame.

    Args:
        path: (str | list[str]) Path to the CSV file(s).
        include_file_path: (bool, optional) If True, return a DataFrame with a 'file_path' column.
            Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (pl.DataFrame | list[pl.DataFrame]): Polars DataFrame or list of DataFrames.
    """
    if isinstance(path, str):
        if "**" in path:
            path = self.glob(path)
        else:
            if ".csv" not in posixpath.basename(path):
                path = posixpath.join(path, "**/*.csv")
                path = self.glob(path)

    if isinstance(path, list):
        if use_threads:
            dfs = run_parallel(
                read_csv_file,
                path,
                self=self,
                include_file_path=include_file_path,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        dfs = [
            read_csv_file(p, self=self, include_file_path=include_file_path, **kwargs)
            for p in path
        ]
    dfs = read_csv_file(
        path=path, self=self, include_file_path=include_file_path, **kwargs
    )
    if concat:
        return pl.concat(dfs, how="diagonal_relaxed")
    return dfs


def _read_csv_batches(
    self,
    path: str | list[str],
    num_batches: int = 1,
    include_file_path: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> Generator[pl.DataFrame, None, None]:
    """
    Read CSV files in batches with optional parallel processing within batches.

    Args:
        path: (str | list[str]) Path to the CSV file(s).
        num_batches: (int) Number of files per batch. Defaults to 1.
        include_file_path: (bool) If True, include file_path column.
        concat: (bool) If True, concatenate batch DataFrames.
        use_threads: (bool) If True, use parallel processing within batches.
        verbose: (bool) If True, print verbose output.
        **kwargs: Additional keyword arguments.

    Yields:
        pl.DataFrame: DataFrame containing data from num_batches files.
    """
    # Handle path resolution
    if isinstance(path, str):
        if "**" in path:
            path = self.glob(path)
        else:
            if ".csv" not in posixpath.basename(path):
                path = posixpath.join(path, "**/*.csv")
                path = self.glob(path)

    # Ensure path is a list
    if isinstance(path, str):
        path = [path]

    # Process files in batches
    for i in range(0, len(path), num_batches):
        batch_paths = path[i : i + num_batches]

        # Read batch with optional parallelization
        if use_threads and len(batch_paths) > 1:
            batch_dfs = run_parallel(
                read_csv_file,
                batch_paths,
                self=self,
                include_file_path=include_file_path,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        else:
            batch_dfs = [
                read_csv_file(
                    p, self=self, include_file_path=include_file_path, **kwargs
                )
                for p in batch_paths
            ]

        if concat and len(batch_dfs) > 1:
            yield pl.concat(batch_dfs, how="diagonal_relaxed")
        else:
            yield batch_dfs


def read_csv(
    self,
    path: str | list[str],
    num_batches: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> (
    pl.DataFrame
    | list[pl.DataFrame]
    | Generator[pl.DataFrame | list[pl.DataFrame], None, None]
):
    """
    Read a CSV file or a list of CSV files. Optionally read in batches,
    returning a generator that sequentially yields data for specified number of files.

    Args:
        path: (str | list[str]) Path to the CSV file(s).
        num_batches: (int, optional) Number of files to process in each batch. Defaults to 1.
        include_file_path: (bool, optional) If True, include 'file_path' column.
        concat: (bool, optional) If True, concatenate the batch DataFrames. Defaults to True.
        use_threads: (bool, optional) If True, use parallel processing within batches. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        pl.DataFrame | list[pl.DataFrame]:
            DataFrame or list or DataFrames containing data from num_batches files.

    Yields:
        pl.DataFrame | list[pl.DataFrame]:
            DataFrame or list of DataFrames containing data from num_batches files.
    """
    if num_batches is not None:
        yield from _read_csv_batches(
            self=self,
            path=path,
            num_batches=num_batches,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            **kwargs,
        )
    return _read_csv(
        self=self,
        path=path,
        include_file_path=include_file_path,
        concat=concat,
        use_threads=use_threads,
        verbose=verbose,
        **kwargs,
    )


def read_parquet_file(
    path, self, include_file_path: bool = False, **kwargs
) -> pa.Table:
    table = pq.read_table(path, filesystem=self, **kwargs)
    if include_file_path:
        return table.add_column(0, "file_path", pl.Series([path] * table.num_rows))
    return table


def _read_parquet(
    self,
    path,
    include_file_path: bool = False,
    use_threads: bool = True,
    concat: bool = True,
    verbose: bool = False,
    **kwargs,
) -> pa.Table | list[pa.Table]:
    """
    Read a Parquet file or a list of Parquet files into a pyarrow Table.

    Args:
        path: (str | list[str]) Path to the Parquet file(s).
        include_file_path: (bool, optional) If True, return a Table with a 'file_path' column.
            Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        concat: (bool, optional) If True, concatenate the Tables. Defaults to True.
        **kwargs: Additional keyword arguments.

    Returns:
        (pa.Table | list[pa.Table]): Pyarrow Table or list of Pyarrow Tables.
    """
    if not include_file_path and concat:
        return pq.read_table(path, filesystem=self, **kwargs)
    else:
        if isinstance(path, str):
            if "**" in path:
                path = self.glob(path)
            else:
                if ".parquet" not in posixpath.basename(path):
                    path = posixpath.join(path, "**/*.parquet")
                    path = self.glob(path)

        if isinstance(path, list):
            if use_threads:
                table = run_parallel(
                    read_parquet_file,
                    path,
                    self=self,
                    include_file_path=include_file_path,
                    n_jobs=-1,
                    backend="threading",
                    verbose=verbose,
                    **kwargs,
                )
            table = [
                read_parquet_file(
                    p, self=self, include_file_path=include_file_path, **kwargs
                )
                for p in path
            ]

    table = read_parquet_file(
        path=path, self=self, include_file_path=include_file_path, **kwargs
    )
    if concat:
        return pa.concat_tables(table, promote_options="permissive")
    return table


def _read_parquet_batches(
    self,
    path: str | list[str],
    num_batches: int = 1,
    include_file_path: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> Generator[pa.Table, None, None]:
    """
    Read Parquet files in batches with optional parallel processing within batches.

    Args:
        path: (str | list[str]) Path to the Parquet file(s).
        num_batches: (int) Number of files per batch. Defaults to 1.
        include_file_path: (bool) If True, include file_path column.
        concat: (bool) If True, concatenate batch tables.
        use_threads: (bool) If True, use parallel processing within batches.
        verbose: (bool) If True, print verbose output.
        **kwargs: Additional keyword arguments.

    Yields:
        pa.Table: PyArrow Table containing data from num_batches files.
    """

    # Handle path resolution
    if isinstance(path, str):
        if "**" in path:
            path = self.glob(path)
        else:
            if ".parquet" not in posixpath.basename(path):
                path = posixpath.join(path, "**/*.parquet")
                path = self.glob(path)

    if isinstance(path, str):
        path = [path]

    # Process files in batches
    for i in range(0, len(path), num_batches):
        batch_paths = path[i : i + num_batches]

        # Read batch of files with optional parallelization
        if use_threads and len(batch_paths) > 1:
            batch_tables = run_parallel(
                read_parquet_file,
                batch_paths,
                self=self,
                include_file_path=include_file_path,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        else:
            batch_tables = [
                read_parquet_file(
                    p, self=self, include_file_path=include_file_path, **kwargs
                )
                for p in batch_paths
            ]

        if concat and len(batch_tables) > 1:
            yield pa.concat_tables(batch_tables, promote_options="permissive")
        else:
            yield batch_tables


def read_parquet(
    self,
    path: str | list[str],
    num_batches: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> pa.Table | list[pa.Table] | Generator[pa.Table | list[pa.Table], None, None]:
    """
    Read a Parquet file or a list of Parquet files. Optionally read in batches,
    returning a generator that sequentially yields data for specified number of files.

    Args:
        path: (str | list[str]) Path to the Parquet file(s).
        num_batches: (int, optional) Number of files to process in each batch. Defaults to 1.
        include_file_path: (bool, optional) If True, include 'file_path' column.
        concat: (bool, optional) If True, concatenate the batch Tables. Defaults to True.
        use_threads: (bool, optional) If True, use parallel processing within batches. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        pa.Table | list[pa.Table]:
            PyArrow Table or list of PyArrow Tables containing data from num_batches files.

    Yields:
        pa.Table | list[pa.Table]: PyArrow Table or list of PyArrow Tables containing data from num_batches files.
    """
    if num_batches is not None:
        yield from _read_parquet_batches(
            self=self,
            path=path,
            num_batches=num_batches,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            **kwargs,
        )
    return _read_parquet(
        self=self,
        path=path,
        include_file_path=include_file_path,
        concat=concat,
        use_threads=use_threads,
        verbose=verbose,
        **kwargs,
    )


def read_files(
    self,
    path: str | list[str],
    format: str,
    num_batches: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    jsonlines: bool = False,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> (
    pl.DataFrame
    | pa.Table
    | list[pl.DataFrame]
    | list[pa.Table]
    | Generator[
        pl.DataFrame | pa.Table | list[pa.Table] | list[pl.DataFrame], None, None
    ]
):
    """
    Read a file or a list of files of the given format.

    Args:
        path: (str | list[str]) Path to the file(s).
        format: (str) Format of the file.
        num_batches: (int, optional) Number of files to process in each batch. Defaults to None.
        include_file_path: (bool, optional) If True, return a DataFrame with a 'file_path' column.
            Defaults to False.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        jsonlines: (bool, optional) If True, read JSON lines. Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (pl.DataFrame | pa.Table | list[pl.DataFrame] | list[pa.Table]):
            Polars DataFrame, Pyarrow Table or list of DataFrames, LazyFrames or Tables.

    Yields:
        (pl.DataFrame | pa.Table):
            Polars DataFrame, Pyarrow Table or list of DataFrames, LazyFrames or Tables.
    """
    if format == "json":
        if num_batches is not None:
            yield from read_json(
                self=self,
                path=path,
                num_batches=num_batches,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
                concat=concat,
                use_threads=use_threads,
                verbose=verbose,
                **kwargs,
            )
        return read_json(
            self,
            path,
            include_file_path=include_file_path,
            jsonlines=jsonlines,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            **kwargs,
        )
    elif format == "csv":
        if num_batches is not None:
            yield from read_csv(
                self=self,
                path=path,
                num_batches=num_batches,
                include_file_path=include_file_path,
                concat=concat,
                use_threads=use_threads,
                verbose=verbose,
                **kwargs,
            )
        return read_csv(
            self,
            path,
            include_file_path=include_file_path,
            use_threads=use_threads,
            concat=concat,
            verbose=verbose,
            **kwargs,
        )
    elif format == "parquet":
        if num_batches is not None:
            yield from read_parquet(
                self=self,
                path=path,
                num_batches=num_batches,
                include_file_path=include_file_path,
                concat=concat,
                use_threads=use_threads,
                verbose=verbose,
                **kwargs,
            )
        return read_parquet(
            self,
            path,
            include_file_path=include_file_path,
            use_threads=use_threads,
            concat=concat,
            verbose=verbose,
            **kwargs,
        )


def pyarrow_dataset(
    self,
    path: str,
    format="parquet",
    schema: pa.Schema | None = None,
    partitioning: str | list[str] | pds.Partitioning = None,
    **kwargs,
) -> pds.Dataset:
    """
    Create a pyarrow dataset.

    Args:
        path: (str) Path to the dataset.
        format: (str, optional) Format of the dataset. Defaults to 'parquet'.
        schema: (pa.Schema, optional) Schema of the dataset. Defaults to None.
        partitioning: (str | list[str] | pds.Partitioning, optional) Partitioning of the dataset.
            Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        (pds.Dataset): Pyarrow dataset.
    """
    return pds.dataset(
        path,
        filesystem=self,
        partitioning=partitioning,
        schema=schema,
        format=format,
        **kwargs,
    )


def pyarrow_parquet_dataset(
    self,
    path: str,
    schema: pa.Schema | None = None,
    partitioning: str | list[str] | pds.Partitioning = None,
    **kwargs,
) -> pds.Dataset:
    """
    Create a pyarrow dataset from a parquet_metadata file.

    Args:
        path: (str) Path to the dataset.
        schema: (pa.Schema, optional) Schema of the dataset. Defaults to None.
        partitioning: (str | list[str] | pds.Partitioning, optional) Partitioning of the dataset.
            Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        (pds.Dataset): Pyarrow dataset.
    """
    if not self.is_file(path):
        path = posixpath.join(path, "_metadata")
    return pds.dataset(
        path,
        filesystem=self,
        partitioning=partitioning,
        schema=schema,
        **kwargs,
    )


def write_parquet(
    self,
    data: pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame,
    path: str,
    schema: pa.Schema | None = None,
    **kwargs,
) -> pq.FileMetaData:
    """
    Write a DataFrame to a Parquet file.

    Args:
        data: (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame) Data to write.
        path: (str) Path to write the data.
        schema: (pa.Schema, optional) Schema of the data. Defaults to None.
        **kwargs: Additional keyword arguments for `pq.write_table`.

    Returns:
        (pq.FileMetaData): Parquet file metadata.
    """
    if isinstance(data, pl.LazyFrame):
        data = data.collect()
    if isinstance(data, pl.DataFrame):
        data = data.to_arrow()
        data = data.cast(convert_large_types_to_standard(data.schema))
    elif isinstance(data, pd.DataFrame):
        data = pa.Table.from_pandas(data, preserve_index=False)

    if schema is not None:
        data = data.cast(schema)
    metadata = []
    pq.write_table(data, path, filesystem=self, metadata_collector=metadata, **kwargs)
    metadata = metadata[0]
    metadata.set_file_path(path)
    return metadata


def write_json(
    self,
    data: dict | pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame,
    path: str,
    append: bool = False,
) -> None:
    """
    Write a dictionary, DataFrame or Table to a JSON file.

    Args:
        data: (dict | pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame) Data to write.
        path: (str) Path to write the data.
        append: (bool, optional) If True, append to the file. Defaults to False.

    Returns:
        None
    """
    if isinstance(data, pl.LazyFrame):
        data = data.collect()
    if isinstance(data, pl.DataFrame):
        data = data.to_arrow()
        data = data.cast(convert_large_types_to_standard(data.schema)).to_pydict()
    elif isinstance(data, pd.DataFrame):
        data = pa.Table.from_pandas(data, preserve_index=False).to_pydict()
    elif isinstance(data, pa.Table):
        data = data.to_pydict()
    if append:
        with self.open(path, "ab") as f:
            f.write(orjson.dumps(data))
            f.write(b"\n")
    else:
        with self.open(path, "wb") as f:
            f.write(orjson.dumps(data))


def write_csv(
    self,
    data: pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame,
    path: str,
    **kwargs,
) -> None:
    """
    Write a DataFrame to a CSV file.

    Args:
        data: (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame) Data to write.
        path: (str) Path to write the data.
        **kwargs: Additional keyword arguments for `pl.DataFrame.write_csv`.

    Returns:
        None
    """
    if isinstance(data, pl.LazyFrame):
        data = data.collect()
    if isinstance(data, pa.Table):
        data = pl.from_arrow(data)
    elif isinstance(data, pd.DataFrame):
        data = pl.from_pandas(data)

    with self.open(path, "w") as f:
        data.write_csv(f, **kwargs)


def write_file(
    self,
    data: pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame,
    path: str,
    format: str,
    **kwargs,
) -> None:
    """
    Write a DataFrame to a file in the given format.

    Args:
        data: (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame) Data to write.
        path (str): Path to write the data.
        format (str): Format of the file.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if format == "json":
        write_json(self, data, path, **kwargs)
    elif format == "csv":
        write_csv(self, data, path, **kwargs)
    elif format == "parquet":
        write_parquet(self, data, path, **kwargs)


def write_pyarrow_dataset(
    self,
    data: (
        pl.DataFrame
        | pa.Table
        | pa.RecordBatch
        | pa.RecordBatchReader
        | pd.DataFrame
        | list[pl.DataFrame]
        | list[pa.Table]
        | list[pa.RecordBatch]
        | list[pa.RecordBatchReader]
        | list[pd.DataFrame]
    ),
    path: str,
    basename: str | None = None,
    schema: pa.Schema | None = None,
    partition_by: str | list[str] | pds.Partitioning | None = None,
    partitioning_flavor: str = "hive",
    mode: str = "append",
    format: str | None = "parquet",
    compression: str = "zstd",
    **kwargs,
) -> list[pq.FileMetaData] | None:
    """
    Write a tabluar data to a PyArrow dataset.

    Args:
        data: (pl.DataFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader |
            pd.DataFrame | list[pl.DataFrame] | list[pa.Table] | list[pa.RecordBatch] |
            list[pa.RecordBatchReader] | list[pd.DataFrame]) Data to write.
        path: (str) Path to write the data.
        basename: (str, optional) Basename of the files. Defaults to None.
        schema: (pa.Schema, optional) Schema of the data. Defaults to None.
        partition_by: (str | list[str] | pds.Partitioning, optional) Partitioning of the data.
            Defaults to None.
        partitioning_flavor: (str, optional) Partitioning flavor. Defaults to 'hive'.
        mode: (str, optional) Write mode. Defaults to 'append'.
        format: (str, optional) Format of the data. Defaults to 'parquet'.
        compression: (str, optional) Compression algorithm. Defaults to 'zstd'.
        **kwargs: Additional keyword arguments for `pds.write_dataset`.

    Returns:
        (list[pq.FileMetaData] | None): List of Parquet file metadata or None.
    """
    if not isinstance(data, list):
        data = [data]

    if isinstance(data[0], pl.DataFrame):
        data = [dd.to_arrow() for dd in data]
        data = [dd.cast(convert_large_types_to_standard(dd.schema)) for dd in data]

    elif isinstance(data[0], pd.DataFrame):
        data = [pa.Table.from_pandas(dd, preserve_index=False) for dd in data]

    if mode == "delete_matching":
        existing_data_behavior = "delete_matching"
    elif mode == "append":
        existing_data_behavior = "overwrite_or_ignore"
    elif mode == "overwrite":
        self.rm(path, recursive=True)
        existing_data_behavior = "overwrite_or_ignore"
    else:
        existing_data_behavior = mode

    if basename is None:
        basename_template = (
            "data-"
            f"{dt.datetime.now().strftime('%Y%m%d_%H%M%S%f')[:-3]}-{uuid.uuid4().hex[:16]}-{{i}}.parquet"
        )
    else:
        basename_template = f"{basename}-{{i}}.parquet"

    file_options = pds.ParquetFileFormat().make_write_options(compression=compression)

    create_dir: bool = (False,)

    if hasattr(self, "fs"):
        if "local" in self.fs.protocol:
            create_dir = True
    else:
        if "local" in self.protocol:
            create_dir = True

    if format == "parquet":
        metadata = []

        def file_visitor(written_file):
            file_metadata = written_file.metadata
            file_metadata.set_file_path(written_file.path)
            metadata.append(file_metadata)

    pds.write_dataset(
        data=data,
        base_dir=path,
        basename_template=basename_template,
        partitioning=partition_by,
        partitioning_flavor=partitioning_flavor,
        filesystem=self,
        existing_data_behavior=existing_data_behavior,
        schema=schema,
        format=format,
        create_dir=create_dir,
        file_options=file_options,
        file_visitor=file_visitor if format == "parquet" else None,
        **kwargs,
    )
    if format == "parquet":
        return metadata


# patchen
DirFileSystem.ls = dir_ls_p
MonitoredSimpleCacheFileSystem.ls = mscf_ls_p
AbstractFileSystem.read_json_file = read_json_file
AbstractFileSystem.read_json = read_json
AbstractFileSystem.read_csv_file = read_csv_file
AbstractFileSystem.read_csv = read_csv
AbstractFileSystem.read_parquet_file = read_parquet_file
AbstractFileSystem.read_parquet = read_parquet
AbstractFileSystem.read_files = read_files
AbstractFileSystem.pyarrow_dataset = pyarrow_dataset
AbstractFileSystem.pyarrow_parquet_dataset = pyarrow_parquet_dataset
AbstractFileSystem.write_parquet = write_parquet
AbstractFileSystem.write_json = write_json
AbstractFileSystem.write_csv = write_csv
AbstractFileSystem.write_pyarrow_dataset = write_pyarrow_dataset


def get_filesystem(
    path: str | None = None,
    storage_options: (
        AwsStorageOptions
        | GitHubStorageOptions
        | GitLabStorageOptions
        | GcsStorageOptions
        | AzureStorageOptions
        | dict[str, str]
        | None
    ) = None,
    dirfs: bool = True,
    cached: bool = False,
    cache_storage: str | None = None,
    **storage_options_kwargs,
) -> AbstractFileSystem:
    """
    Get a filesystem based on the given path.

    Args:
        path: (str, optional) Path to the filesystem. Defaults to None.
        storage_options: (AwsStorageOptions | GitHubStorageOptions | GitLabStorageOptions |
            GcsStorageOptions | AzureStorageOptions | dict[str, str], optional) Storage options.
            Defaults to None.
        dirfs: (bool, optional) If True, return a DirFileSystem. Defaults to True.
        cached: (bool, optional) If True, use a cached filesystem. Defaults to False.
        cache_storage: (str, optional) Path to the cache storage. Defaults to None.
        **storage_options_kwargs: Additional keyword arguments for the storage options.

    """
    pp = infer_storage_options(path)
    protocol = pp.get("protocol")
    path = pp.get("host", "") + pp.get("path", "")

    if protocol == "file" or protocol == "local":
        fs = filesystem(protocol)
        fs.is_cache_fs = False
        if dirfs:
            fs = DirFileSystem(path=path, fs=fs)
            fs.is_cache_fs = False
        return fs

    if storage_options is None:
        storage_options = get_storage_options(protocol, **storage_options_kwargs)

    fs = storage_options.to_filesystem()
    fs.is_cache_fs = False
    if dirfs:
        fs = DirFileSystem(path=path, fs=fs)
        fs.is_cache_fs = False
    if cached:
        if cache_storage is None:
            cache_storage = (Path.cwd() / path).as_posix()
        fs = MonitoredSimpleCacheFileSystem(fs=fs, cache_storage=cache_storage)
        fs.is_cache_fs = True

    return fs
