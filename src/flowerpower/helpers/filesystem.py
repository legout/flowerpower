import base64
import inspect
import os
import orjson
import urllib
from pathlib import Path

import fsspec
import requests
from fsspec import url_to_fs
from fsspec.implementations.cache_mapper import AbstractCacheMapper
from fsspec.implementations.cached import SimpleCacheFileSystem
from fsspec.implementations.dirfs import DirFileSystem
from fsspec.implementations.memory import MemoryFile
from fsspec.spec import AbstractFileSystem
from loguru import logger

from .storage_options import (
    AwsStorageOptions,
    GitHubStorageOptions,
    GitLabStorageOptions,
    GcsStorageOptions,
    AzureStorageOptions,
)
from .misc import run_parallel
from .polars import pl
from .misc import convert_large_types_to_standard
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.dataset as pds
import datetime as dt
import pandas as pd
import uuid


class FileNameCacheMapper(AbstractCacheMapper):
    def __init__(self, directory):
        self.directory = directory

    def __call__(self, path: str) -> str:
        os.makedirs(os.path.dirname(os.path.join(self.directory, path)), exist_ok=True)
        return path


class MonitoredSimpleCacheFileSystem(SimpleCacheFileSystem):
    def __init__(self, **kwargs):
        # kwargs["cache_storage"] = os.path.join(
        #    kwargs.get("cache_storage"), kwargs.get("fs").protocol[0]
        # )
        self._verbose = kwargs.get("verbose", False)
        super().__init__(**kwargs)
        self._mapper = FileNameCacheMapper(kwargs.get("cache_storage"))

    def _check_file(self, path):
        self._check_cache()
        cache_path = self._mapper(path)
        for storage in self.storage:
            fn = os.path.join(storage, cache_path)
            if os.path.exists(fn):
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
            return os.path.getsize(cached_file)

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


def _read_json(
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


def read_json(
    self,
    path: str | list[str],
    include_file_path: bool = False,
    use_threads: bool = True,
    jsonlines: bool = False,
    **kwargs,
) -> dict | list[dict]:
    """
    Read a JSON file or a list of JSON files.

    Args:
        path: (str | list[str]) Path to the JSON file(s).
        include_file_path: (bool, optional) If True, return a dictionary with the file path as key.
            Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        jsonlines: (bool, optional) If True, read JSON lines. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (dict | list[dict]): JSON data or list of JSON data.
    """
    if isinstance(path, str):
        if "*" in path:
            path = self.glob(path)
        else:
            if ".json" not in os.path.basename(path):
                path = os.path.join(path, "**/*.jsonl" if jsonlines else "**/*.json")
                path = self.glob(path)

    if isinstance(path, list):
        if use_threads:
            return run_parallel(
                _read_json,
                path,
                self=self,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
                n_jobs=-1,
                backend="threading",
                **kwargs,
            )
        return [
            _read_json(
                path=p,
                self=self,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
            )
            for p in path
        ]
    return _read_json(
        path=path, self=self, include_file_path=include_file_path, jsonlines=jsonlines
    )


def read_json_dataset(
    self,
    path: str | list[str],
    include_file_path: bool = False,
    jsonlines: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    **kwargs,
) -> list[pl.DataFrame] | pl.DataFrame:
    """
    Read a JSON file or a list of JSON files into a polars DataFrame.

    Args:
        path: (str | list[str]) Path to the JSON file(s).
        include_file_path: (bool, optional) If True, return a dictionary with the file path as key.
            Defaults to False.
        jsonlines: (bool, optional) If True, read JSON lines. Defaults to False.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        **kwargs: Additional keyword arguments.

    Returns:
        (pl.DataFrame | list[pl.DataFrame]): Polars DataFrame or list of DataFrames.
    """
    data = read_json(
        self=self,
        path=path,
        include_file_path=include_file_path,
        jsonlines=jsonlines,
        use_threads=use_threads,
        **kwargs,
    )
    if not include_file_path:
        data = [pl.DataFrame(d) for d in data]
    else:
        data = [
            pl.DataFrame(list(d.values())[0]).with_columns(
                pl.lit(list(d.keys())[0]).alias("file_path")
            )
            for d in data
        ]
    if concat:
        return pl.concat(data, how="diagonal_relaxed")
    return data


def _read_csv(path, self, include_file_path: bool = False, **kwargs) -> pl.DataFrame:
    with self.open(path) as f:
        df = pl.read_csv(f, **kwargs)
    if include_file_path:
        return df.with_columns(pl.lit(path).alias("file_path"))
    return df


def read_csv(
    self,
    path: str | list[str],
    include_file_path: bool = False,
    use_threads: bool = True,
    concat: bool = True,
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
        **kwargs: Additional keyword arguments.

    Returns:
        (pl.DataFrame | list[pl.DataFrame]): Polars DataFrame or list of DataFrames.
    """
    if isinstance(path, str):
        if "*" in path:
            path = self.glob(path)
        else:
            if ".csv" not in os.path.basename(path):
                path = os.path.join(path, "**/*.csv")
                path = self.glob(path)

    if isinstance(path, list):
        if use_threads:
            dfs = run_parallel(
                _read_csv,
                path,
                self=self,
                include_file_path=include_file_path,
                n_jobs=-1,
                backend="threading",
                **kwargs,
            )
        dfs = [
            _read_csv(p, self=self, include_file_path=include_file_path, **kwargs)
            for p in path
        ]
    dfs = _read_csv(path=path, self=self, include_file_path=include_file_path, **kwargs)
    if concat:
        return pl.concat(dfs, how="diagonal_relaxed")
    return dfs


def _read_parquet(path, self, include_file_path: bool = False, **kwargs) -> pa.Table:
    table = pq.read_table(path, filesystem=self, **kwargs)
    if include_file_path:
        return table.add_column(0, "file_path", pl.Series([path] * table.num_rows))
    return table


def read_parquet(
    self,
    path,
    include_file_path: bool = False,
    use_threads: bool = True,
    concat: bool = True,
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
            if "*" in path:
                path = self.glob(path)
            else:
                if ".parquet" not in os.path.basename(path):
                    path = os.path.join(path, "**/*.parquet")
                    path = self.glob(path)

        if isinstance(path, list):
            if use_threads:
                table = run_parallel(
                    _read_parquet,
                    path,
                    self=self,
                    include_file_path=include_file_path,
                    n_jobs=-1,
                    backend="threading",
                    **kwargs,
                )
            table = [
                _read_parquet(
                    p, self=self, include_file_path=include_file_path, **kwargs
                )
                for p in path
            ]

    table = _read_parquet(
        path=path, self=self, include_file_path=include_file_path, **kwargs
    )
    if concat:
        return pa.concat_tables(table, promote_options="permissive")
    return table


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
        path = os.path.join(path, "_metadata")
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

    if hasattr(self._filesystem, "fs"):
        if "local" in self._filesystem.fs.protocol:
            create_dir = True
    else:
        if "local" in self._filesystem.protocol:
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
AbstractFileSystem.read_json = read_json
AbstractFileSystem.read_json_dataset = read_json_dataset
AbstractFileSystem.read_csv = read_csv
AbstractFileSystem.read_parquet = read_parquet
AbstractFileSystem.pyarrow_dataset = pyarrow_dataset
AbstractFileSystem.pyarrow_parquet_dataset = pyarrow_parquet_dataset
AbstractFileSystem.write_parquet = write_parquet
AbstractFileSystem.write_json = write_json
AbstractFileSystem.write_csv = write_csv
AbstractFileSystem.write_pyarrow_dataset = write_pyarrow_dataset


def get_filesystem(
    path: str | None = None,
    cached: bool = True,
    cache_storage: str | None = None,
    storage_options: (
        AwsStorageOptions
        | GitHubStorageOptions
        | GitLabStorageOptions
        | GcsStorageOptions
        | AzureStorageOptions
        | dict[str, str]
        | None
    ) = None,
    **storage_options_kwargs,
) -> DirFileSystem:
    if storage_options is None:
        if storage_options_kwargs:
            storage_options = storage_options_kwargs
        else:
            storage_options = {}
    else:
        if hasattr(storage_options, "to_fsspec_kwargs"):
            storage_options = storage_options.to_fsspec_kwargs()
        else:
            storage_options = storage_options.to_dict()

    if path is None:
        path = "file://."
    fs, path = url_to_fs(path, **storage_options)

    if fs.protocol[0] == "file" or fs.protocol[0] == "local":
        fs = DirFileSystem(path=path, fs=fs)
        fs.is_cache_fs = False
        return fs

    # temp_dir = tempfile.TemporaryDirectory()
    fs = DirFileSystem(path=path, fs=fs)

    if cached:
        if cache_storage is None:
            cache_storage = (Path.cwd() / path).as_posix()
        fs = MonitoredSimpleCacheFileSystem(fs=fs, cache_storage=cache_storage)
        fs.is_cache_fs = True
    else:
        fs.is_cache_fs = False
    return fs
