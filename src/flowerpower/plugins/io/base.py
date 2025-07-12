import importlib
import os
import posixpath
from typing import Any, Generator

if importlib.util.find_spec("datafusion"):
    import datafusion
else:
    raise ImportError("To use this module, please install `flowerpower[io]`.")
import sqlite3

import duckdb
import msgspec
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pds
from fsspec import AbstractFileSystem
from msgspec import field
from pydala.dataset import ParquetDataset
from sqlalchemy import create_engine, text

from ...fs import get_filesystem
from ...fs.ext import _dict_to_dataframe, path_to_glob
from ...fs.storage_options import (AwsStorageOptions, AzureStorageOptions,
                                   GcsStorageOptions, GitHubStorageOptions,
                                   GitLabStorageOptions, StorageOptions)
from ...utils.misc import convert_large_types_to_standard, to_pyarrow_table
from .helpers.polars import pl
from .helpers.pyarrow import opt_dtype
from .helpers.sql import sql2polars_filter, sql2pyarrow_filter
from .metadata import get_dataframe_metadata, get_pyarrow_dataset_metadata


# @attrs.define # Removed
class BaseFileIO(msgspec.Struct, gc=False):
    """
    Base class for file I/O operations supporting various storage backends.
    This class provides a foundation for file operations across different storage systems
    including AWS S3, Google Cloud Storage, Azure Blob Storage, GitHub, and GitLab.

    Args:
        path (str | list[str]): Path or list of paths to file(s).
        storage_options (AwsStorageOptions | GcsStorageOptions | AzureStorageOptions |
                             GitHubStorageOptions | GitLabStorageOptions | dict[str, Any] |  None, optional):
            Storage-specific options for accessing remote filesystems.
        fs (AbstractFileSystem, optional): Filesystem instance for handling file operations.
        format (str, optional): File format extension (without dot).

    Notes:
        ```python
        file_io = BaseFileIO(
            path="s3://bucket/path/to/files",
            storage_options=AwsStorageOptions(
                key="access_key",
                secret="secret_key"
        files = file_io.list_files()
        ```
    Notes:
        - Supports multiple cloud storage backends through different storage options
        - Automatically handles filesystem initialization based on path protocol
        - Supports both single path and multiple path inputs
        - Can read credentials from environment variables when using from_env() methods

    """

    path: str | list[str]
    storage_options: (
        StorageOptions
        | AwsStorageOptions
        | AzureStorageOptions
        | GcsStorageOptions
        | GitLabStorageOptions
        | GitHubStorageOptions
        | dict[str, Any]
        | None
    ) = field(default=None)
    fs: AbstractFileSystem | None = field(default=None)
    format: str | None = None
    # _base_path: str | list[str] | None = field(default=None)
    # _full_path: str | list[str] | None = field(default=None)
    # _rel_path: str | list[str] | None = field(default=None)
    # _glob_path
    _metadata: dict[str, Any] | None = field(default=None)

    def __post_init__(self):
        # self._base_path = self.path if isinstance(self.path, str) else os.path.commonpath(self.path)

        # if self.fs is None:
        self.fs = get_filesystem(
            path=self._base_path,
            storage_options=self.storage_options,
            fs=self.fs,
            dirfs=True,
        )

        self.storage_options = (
            self.storage_options or self.fs.storage_options
            if self.protocol != "dir"
            else self.fs.fs.storage_options
        )

    @property
    def protocol(self):
        """Get the protocol of the filesystem."""
        protocol = (
            self.fs.protocol if self.fs.protocol != "dir" else self.fs.fs.protocol
        )
        if isinstance(protocol, list | tuple):
            protocol = protocol[0]
        return protocol

    @property
    def _base_path(self) -> str:
        """Get the base path for the filesystem."""
        return (
            self.path if isinstance(self.path, str) else os.path.commonpath(self.path)
        )

    @property
    def _path(self) -> str | list[str]:
        if self.fs.protocol == "dir":
            if isinstance(self.path, list):
                return [
                    p.replace(self._base_path.lstrip("/"), "").lstrip("/")
                    for p in self.path
                ]
            else:
                return self.path.replace(self._base_path.lstrip("/"), "").lstrip("/")
        return self.path

    @property
    def _glob_path(self) -> str | list[str]:
        if isinstance(self._path, list):
            return self._path
        return path_to_glob(self._path, self.format)

    @property
    def _root_path(self) -> str:
        if self.fs.protocol == "dir":
            return self._base_path.replace(self.fs.path, "")
        return self._base_path

    def list_files(self) -> list[str]:
        if isinstance(self._path, list):
            return self._path

        return self.fs.glob(self._glob_path)


# @attrs.define # Removed
class BaseFileReader(BaseFileIO, gc=False):
    """
    Base class for file loading operations supporting various file formats.
    This class provides a foundation for file loading operations across different file formats
    including CSV, Parquet, JSON, Arrow, and IPC.

    Args:
        path (str | list[str]): Path or list of paths to file(s).
        format (str, optional): File format extension (without dot).
        fs (AbstractFileSystem, optional): Filesystem instance for handling file operations.
        include_file_path (bool, optional): Include file path in the output DataFrame.
        concat (bool, optional): Concatenate multiple files into a single DataFrame.
        conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
        ctx (datafusion.SessionContext, optional): DataFusion session context instance.

    Examples:
        ```python
        file_loader = BaseFileReader(
            path="s3://bucket/path/to/files",
            format="csv",
            include_file_path=True,
            concat=True,
            conn=duckdb.connect(),
            ctx=datafusion.SessionContext()
        data = file_loader.to_polars()
        ```
    Notes:
        - Supports multiple file formats including CSV, Parquet, JSON, Arrow, and IPC
        - Automatically handles filesystem initialization based on path protocol
        - Supports both single path and multiple path inputs
        - Supports loading data into DuckDB and DataFusion for SQL operations

    """

    include_file_path: bool = field(default=False)
    concat: bool = field(default=True)
    batch_size: int | None = field(default=None)
    opt_dtypes: bool = field(default=False)
    use_threads: bool = field(default=True)
    conn: duckdb.DuckDBPyConnection | None = field(default=None)
    ctx: datafusion.SessionContext | None = field(default=None)
    jsonlines: bool | None = field(default=None)
    partitioning: str | list[str] | pds.Partitioning | None = field(default=None)
    verbose: bool | None = field(default=None)
    _data: Any | None = field(default=None)

    def _load(
        self,
        metadata: bool = False,
        reload: bool = False,
        batch_size: int | None = None,
        include_file_path: bool = False,
        concat: bool | None = None,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ):
        if batch_size is not None:
            if self.batch_size != batch_size:
                reload = True
            self.batch_size = batch_size

        if include_file_path is not None:
            if self.include_file_path != include_file_path:
                reload = True
                self.include_file_path = include_file_path

        if concat is not None:
            if self.concat != concat:
                reload = True
                self.concat = concat

        if use_threads is not None:
            if self.use_threads != use_threads:
                reload = True
                self.use_threads = use_threads

        if verbose is not None:
            if self.verbose != verbose:
                reload = True
                self.verbose = verbose

        if opt_dtypes is not None:
            if self.opt_dtypes != opt_dtypes:
                reload = True
                self.opt_dtypes = opt_dtypes

        if "partitioning" in kwargs:
            if self.partitioning != kwargs["partitioning"]:
                reload = True
                self.partitioning = kwargs.pop("partitioning")

        if not hasattr(self, "_data") or self._data is None or reload:
            self._data = self.fs.read_files(
                path=self._glob_path,
                format=self.format,
                include_file_path=True if metadata or self.include_file_path else False,
                concat=self.concat,
                jsonlines=self.jsonlines or None,
                batch_size=self.batch_size,
                partitioning=self.partitioning,
                opt_dtypes=self.opt_dtypes,
                verbose=self.verbose,
                use_threads=self.use_threads,
                **kwargs,
            )
            if metadata:
                if isinstance(self._data, tuple | list):
                    self._metadata = [
                        get_dataframe_metadata(
                            df=df,
                            path=self.path,
                            format=self.format,
                            num_files=pl.from_arrow(df.select(["file_path"])).select(
                                pl.n_unique("file_path")
                            )[0, 0]
                            if isinstance(df, pa.Table)
                            else df.select(pl.n_unique("file_path"))[0, 0],
                        )
                        for df in self._data
                    ]
                    if not self.include_file_path:
                        self._data = [df.drop("file_path") for df in self._data]

                elif isinstance(self._data, pa.Table):
                    self._metadata = get_dataframe_metadata(
                        df=self._data,
                        path=self.path,
                        format=self.format,
                        num_files=pl.from_arrow(
                            self._data.select(pl.n_unique("file_path"))
                        )[0, 0],
                    )
                    if not self.include_file_path:
                        self._data = self._data.drop("file_path")

                elif isinstance(self._data, pl.DataFrame | pl.LazyFrame):
                    self._metadata = get_dataframe_metadata(
                        df=self._data,
                        path=self.path,
                        format=self.format,
                        num_files=self._data.select(pl.n_unique("file_path"))[0, 0]
                        if isinstance(self._data, pl.DataFrame)
                        else self._data.select(pl.n_unique("file_path")).collect()[
                            0, 0
                        ],
                    )

                    if not self.include_file_path:
                        self._data = self._data.drop("file_path")
                else:
                    metadata = {}
            else:
                self._metadata = {}

    def to_pandas(
        self,
        metadata: bool = False,
        reload: bool = False,
        include_file_path: bool = False,
        concat: bool | None = None,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> (
        tuple[pd.DataFrame | list[pd.DataFrame], dict[str, Any]]
        | pd.DataFrame
        | list[pd.DataFrame]
    ):
        """Convert data to Pandas DataFrame(s).

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            concat (bool, optional): Concatenate multiple files into a single DataFrame. Default is True.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            tuple[pd.DataFrame | list[pd.DataFrame], dict[str, Any]] | pd.DataFrame | list[pd.DataFrame]: Pandas
                DataFrame or list of DataFrames and optional metadata.
        """
        kwargs.pop("batch_size", None)
        self._load(
            reload=reload,
            metadata=metadata,
            batch_size=None,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
        if isinstance(self._data, list):
            df = [
                df if isinstance(df, pd.DataFrame) else df.to_pandas()
                for df in self._data
            ]
            df = pd.concat(df) if self.concat else df
        else:
            df = (
                self._data
                if isinstance(self._data, pd.DataFrame)
                else self._data.to_pandas()
            )
        if metadata:
            # metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, self._metadata
        return df

    def iter_pandas(
        self,
        reload: bool = False,
        batch_size: int | None = None,
        include_file_path: bool = False,
        concat: bool | None = None,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> Generator[pd.DataFrame, None, None]:
        """Iterate over Pandas DataFrames.

        Args:
            batch_size (int, optional): Batch size for iteration. Default is 1.
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            concat (bool, optional): Concatenate multiple files into a single DataFrame. Default is True.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            Generator[pd.DataFrame, None, None]: Generator of Pandas DataFrames.
        """
        batch_size = batch_size or self.batch_size or 1

        self._load(
            reload=reload,
            batch_size=batch_size,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )

        if isinstance(self._data, list | Generator):
            for df in self._data:
                yield df if isinstance(df, pd.DataFrame) else df.to_pandas()
        else:
            yield (
                self._data
                if isinstance(self._data, pd.DataFrame)
                else self._data.to_pandas()
            )

    def _to_polars_dataframe(
        self,
        metadata: bool = False,
        reload: bool = False,
        include_file_path: bool = False,
        concat: bool | None = None,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> (
        tuple[pl.DataFrame | list[pl.DataFrame], dict[str, Any]]
        | pl.DataFrame
        | list[pl.DataFrame]
    ):
        """Convert data to Polars DataFrame(s).

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            concat (bool, optional): Concatenate multiple files into a single DataFrame. Default is True.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            tuple[pl.DataFrame | list[pl.DataFrame], dict[str, Any]] | pl.DataFrame | list[pl.DataFrame]: Polars
                DataFrame or list of DataFrames and optional metadata.
        """
        kwargs.pop("batch_size", None)

        self._load(
            metadata=metadata,
            reload=reload,
            batch_size=None,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
        if isinstance(self._data, list):
            df = [
                df if isinstance(self._data, pl.DataFrame) else pl.from_arrow(df)
                for df in self._data
            ]
            df = pl.concat(df) if self.concat else df
        else:
            df = (
                self._data
                if isinstance(self._data, pl.DataFrame)
                else pl.from_arrow(self._data)
            )
        if metadata:
            # metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, self._metadata
        return df

    def _iter_polars_dataframe(
        self,
        reload: bool = False,
        batch_size: int | None = None,
        include_file_path: bool = False,
        concat: bool | None = None,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> Generator[pl.DataFrame, None, None]:
        """Iterate over Polars DataFrames.

        Args:
            batch_size (int, optional): Batch size for iteration. Default is 1.
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            concat (bool, optional): Concatenate multiple files into a single DataFrame. Default is True.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            Generator[pl.DataFrame, None, None]: Generator of Polars DataFrames.
        """
        batch_size = batch_size or self.batch_size or 1

        self._load(
            reload=reload,
            batch_size=batch_size,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
        if isinstance(self._data, list | Generator):
            for df in self._data:
                yield df if isinstance(df, pl.DataFrame) else pl.from_arrow(df)
        else:
            yield (
                self._data
                if isinstance(self._data, pl.DataFrame)
                else pl.from_arrow(self._data)
            )

    def _to_polars_lazyframe(
        self,
        metadata: bool = False,
        reload: bool = False,
        include_file_path: bool = False,
        concat: bool | None = None,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> (
        tuple[pl.LazyFrame | list[pl.LazyFrame], dict[str, Any]]
        | pl.LazyFrame
        | list[pl.LazyFrame]
    ):
        """Convert data to Polars LazyFrame(s).

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            concat (bool, optional): Concatenate multiple files into a single DataFrame. Default is True.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            tuple[pl.LazyFrame | list[pl.LazyFrame], dict[str, Any]] | pl.LazyFrame | list[pl.LazyFrame]: Polars
                LazyFrame or list of LazyFrames and optional metadata.
        """
        kwargs.pop("batch_size", None)

        self._load(
            metadata=metadata,
            reload=reload,
            batch_size=None,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
        if not self.concat:
            df = [df.lazy() for df in self._to_polars_dataframe()]

        else:
            df = self._to_polars_dataframe().lazy()
        if metadata:
            # metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, self._metadata
        return df

    def _iter_polars_lazyframe(
        self,
        reload: bool = False,
        batch_size: int | None = None,
        include_file_path: bool = False,
        concat: bool | None = None,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> Generator[pl.LazyFrame, None, None]:
        """Iterate over Polars LazyFrames.

        Args:
            batch_size (int, optional): Batch size for iteration. Default is 1.
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            concat (bool, optional): Concatenate multiple files into a single DataFrame. Default is True.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            Generator[pl.LazyFrame, None, None]: Generator of Polars LazyFrames.
        """
        batch_size = batch_size or self.batch_size or 1

        self._load(
            reload=reload,
            batch_size=batch_size,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
        if isinstance(self._data, list | Generator):
            for df in self._data:
                yield (
                    df.lazy()
                    if isinstance(df, pl.DataFrame)
                    else pl.from_arrow(df).lazy()
                )
        else:
            yield (
                self._data.lazy()
                if isinstance(self._data, pl.DataFrame)
                else pl.from_arrow(self._data).lazy()
            )

    def to_polars(
        self,
        lazy: bool = False,
        metadata: bool = False,
        reload: bool = False,
        include_file_path: bool = False,
        concat: bool | None = None,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> (
        pl.DataFrame
        | pl.LazyFrame
        | list[pl.DataFrame]
        | list[pl.LazyFrame]
        | tuple[
            pl.DataFrame | pl.LazyFrame | list[pl.DataFrame] | list[pl.LazyFrame],
            dict[str, Any],
        ]
    ):
        """Convert data to Polars DataFrame or LazyFrame.

        Args:
            lazy (bool, optional): Return a LazyFrame if True, else a DataFrame.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            batch_size (int, optional): Batch size for iteration. Default is 1.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            concat (bool, optional): Concatenate multiple files into a single DataFrame. Default is True.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            pl.DataFrame | pl.LazyFrame | list[pl.DataFrame] | list[pl.LazyFrame] | tuple[pl.DataFrame | pl.LazyFrame
                | list[pl.DataFrame] | list[pl.LazyFrame], dict[str, Any]]: Polars DataFrame or LazyFrame and optional
                metadata.
        """
        kwargs.pop("batch_size", None)
        if lazy:
            return self._to_polars_lazyframe(
                metadata=metadata,
                reload=reload,
                batch_size=None,
                include_file_path=include_file_path,
                concat=concat,
                use_threads=use_threads,
                verbose=verbose,
                opt_dtypes=opt_dtypes,
                **kwargs,
            )
        return self._to_polars_dataframe(
            metadata=metadata,
            reload=reload,
            batch_size=None,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )

    def iter_polars(
        self,
        lazy: bool = False,
        reload: bool = False,
        batch_size: int | None = None,
        include_file_path: bool = False,
        concat: bool | None = None,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> Generator[pl.DataFrame | pl.LazyFrame, None, None]:
        """Iterate over Polars DataFrames or LazyFrames.

        Args:
            lazy (bool, optional): Return a LazyFrame if True, else a DataFrame. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            batch_size (int, optional): Batch size for iteration. Default is 1.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            concat (bool, optional): Concatenate multiple files into a single DataFrame. Default is True.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            Generator[pl.DataFrame | pl.LazyFrame, None, None]: Generator of Polars DataFrames or LazyFrames.
        """
        if lazy:
            yield from self._iter_polars_lazyframe(
                reload=reload,
                batch_size=batch_size,
                include_file_path=include_file_path,
                concat=concat,
                use_threads=use_threads,
                verbose=verbose,
                opt_dtypes=opt_dtypes,
                **kwargs,
            )
        yield from self._iter_polars_dataframe(
            reload=reload,
            batch_size=batch_size,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )

    def to_pyarrow_table(
        self,
        metadata: bool = False,
        reload: bool = False,
        include_file_path: bool = False,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> pa.Table | list[pa.Table] | tuple[pa.Table | list[pa.Table], dict[str, Any]]:
        """Convert data to PyArrow Table(s).

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            pa.Table | list[pa.Table] | tuple[pa.Table | list[pa.Table], dict[str, Any]]: PyArrow Table or list of
                Tables and optional metadata.
        """
        kwargs.pop("batch_size", None)
        self._load(
            reload=reload,
            metadata=metadata,
            batch_size=None,
            include_file_path=include_file_path,
            concat=None,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
        if isinstance(self._data, list):
            df = [
                df.to_arrow(**kwargs) if isinstance(df, pl.DataFrame) else df
                for df in self._data
            ]
            df = pa.concat_tables(df) if self.concat else df
        else:
            df = (
                self._data.to_arrow(**kwargs)
                if isinstance(self._data, pl.DataFrame)
                else self._data
            )
        if metadata:
            # metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, self._metadata
        return df

    def iter_pyarrow_table(
        self,
        reload: bool = False,
        batch_size: int | None = None,
        include_file_path: bool = False,
        concat: bool | None = None,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> Generator[pa.Table, None, None]:
        """Iterate over PyArrow Tables.

        Args:
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            concat (bool, optional): Concatenate multiple files into a single Table. Default is True.
            batch_size (int, optional): Batch size for iteration. Default is 1.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            Generator[pa.Table, None, None]: Generator of PyArrow Tables.
        """
        batch_size = batch_size or self.batch_size or 1

        self._load(
            reload=reload,
            batch_size=batch_size,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
        if isinstance(self._data, list | Generator):
            for df in self._data:
                yield df.to_arrow(**kwargs) if isinstance(df, pl.DataFrame) else df
        else:
            yield (
                self._data.to_arrow(**kwargs)
                if isinstance(self._data, pl.DataFrame)
                else self._data
            )

    def to_duckdb_relation(
        self,
        conn: duckdb.DuckDBPyConnection | None = None,
        metadata: bool = False,
        reload: bool = False,
        include_file_path: bool = False,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> duckdb.DuckDBPyRelation | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]:
        """Convert data to DuckDB relation.

        Args:
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyRelation | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]: DuckDB relation and optional
                metadata.
        """
        kwargs.pop("batch_size", None)
        if self._conn is None:
            if conn is None:
                conn = duckdb.connect()
            self._conn = conn

        if metadata:
            return self._conn.from_arrow(
                self.to_pyarrow_table(
                    metadata=metadata,
                    reload=reload,
                    batch_size=None,
                    include_file_path=include_file_path,
                    se_threads=use_threads,
                    verbose=verbose,
                    opt_dtypes=opt_dtypes,
                    **kwargs,
                ),
            ), self._metadata
        return self._conn.from_arrow(
            self.to_pyarrow_table(
                reload=reload,
                batch_size=None,
                include_file_path=include_file_path,
                use_threads=use_threads,
                verbose=verbose,
                opt_dtypes=opt_dtypes,
                **kwargs,
            )
        )

    def register_in_duckdb(
        self,
        conn: duckdb.DuckDBPyConnection,
        name: str | None = None,
        metadata: bool = False,
        reload: bool = False,
        include_file_path: bool = False,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]:
        """Register data in DuckDB.

        Args:
            conn (duckdb.DuckDBPyConnection): DuckDB connection instance.
            name (str, optional): Name for the DuckDB table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]: DuckDB connection instance
                or DuckDB connection instance and optional metadata.
        """
        kwargs.pop("batch_size", None)
        if name is None:
            name = f"{self.format}:{self.path}"

        if self._conn is None:
            if conn is None:
                conn = duckdb.connect()
            self._conn = conn

        self._conn.register(
            name,
            self.to_pyarrow_table(
                metadata=metadata,
                reload=reload,
                include_file_path=include_file_path,
                use_threads=use_threads,
                verbose=verbose,
                opt_dtypes=opt_dtypes,
                **kwargs,
            ),
        )
        if metadata:
            return self._conn, self._metadata
        return self._conn

    def to_duckdb(
        self,
        as_relation: bool = True,
        conn: duckdb.DuckDBPyConnection | None = None,
        name: str | None = None,
        metadata: bool = False,
        reload: bool = False,
        include_file_path: bool = False,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> (
        duckdb.DuckDBPyRelation
        | duckdb.DuckDBPyConnection
        | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]
        | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]
    ):
        """Convert data to DuckDB relation or register in DuckDB.

        Args:
            as_relation (bool, optional): Return a DuckDB relation if True, else register in DuckDB. Default is True.
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            name (str, optional): Name for the DuckDB table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            include_file_path (bool, optional): Include file path in the output. Default is False.
            use_threads (bool, optional): Use threads for reading data. Default is True.
            verbose (bool, optional): Verbose output. Default is None.
            opt_dtypes (bool, optional): Optimize data types. Default is True.
            **kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyRelation | duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyRelation, dict[str, Any]] |
                tuple[duckdb.DuckDBPyConnection, dict[str, Any]]: DuckDB relation or connection instance
                or DuckDB relation or connection instance and optional metadata.

        """
        kwargs.pop("batch_size", None)
        if as_relation:
            return self.to_duckdb_relation(
                conn=conn,
                metadata=metadata,
                reload=reload,
                include_file_path=include_file_path,
                use_threads=use_threads,
                verbose=verbose,
                opt_dtypes=opt_dtypes,
                **kwargs,
            )
        return self.register_in_duckdb(
            conn=conn,
            name=name,
            metadata=metadata,
            reload=reload,
            include_file_path=include_file_path,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )

    def register_in_datafusion(
        self,
        ctx: datafusion.SessionContext,
        name: str | None = None,
        metadata: bool = False,
        reload: bool = False,
        include_file_path: bool = False,
        use_threads: bool | None = None,
        verbose: bool | None = None,
        opt_dtypes: bool | None = None,
        **kwargs,
    ) -> datafusion.SessionContext | tuple[datafusion.SessionContext, dict[str, Any]]:
        """Register data in DataFusion.

        Args:
            ctx (datafusion.SessionContext): DataFusion session context instance.
            name (str, optional): Name for the DataFusion table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        kwargs.pop("batch_size", None)
        if name is None:
            name = f"{self.format}:{self.path}"

        if self._ctx is None:
            if ctx is None:
                ctx = datafusion.SessionContext()
            self._ctx = ctx

        self._ctx.register_record_batches(
            name,
            [
                self.to_pyarrow_table(
                    reload=reload,
                    include_file_path=include_file_path,
                    use_threads=use_threads,
                    opt_dtypes=opt_dtypes,
                    verbose=verbose,
                    **kwargs,
                ).to_batches()
            ],
        )
        if metadata:
            return self._ctx, self._metadata
        return self._ctx

    def filter(
        self, filter_expr: str | pl.Expr | pa.compute.Expression
    ) -> (
        pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | list[pl.DataFrame]
        | list[pl.LazyFrame]
        | list[pa.Table]
    ):
        """Filter data based on a filter expression.

        Args:
            filter_expr (str | pl.Expr | pa.compute.Expression): Filter expression. Can be a SQL expression, Polars
                expression, or PyArrow compute expression.

        Returns:
            pl.DataFrame | pl.LazyFrame | pa.Table | list[pl.DataFrame] | list[pl.LazyFrame]
                | list[pa.Table]: Filtered data.
        """
        if isinstance(self._data, pl.DataFrame | pl.LazyFrame):
            pl_schema = (
                self._data.schema
                if isinstance(self._data, pl.DataFrame)
                else self._data.collect_schema()
            )
            filter_expr = (
                sql2polars_filter(filter_expr, pl_schema)
                if isinstance(filter_expr, str)
                else filter_expr
            )
            return self._data.filter(filter_expr)

        elif isinstance(self._data, pa.Table):
            pa_schema = self._data.schema
            filter_expr = (
                sql2pyarrow_filter(filter_expr, pa_schema)
                if isinstance(filter_expr, str)
                else filter_expr
            )
            return self._data.filter(filter_expr)

        if isinstance(self._data, str):
            if isinstance(self._data[0], pl.DataFrame | pl.LazyFrame):
                pl_schema = (
                    self._data.schema
                    if isinstance(self._data[0], pl.DataFrame)
                    else self._data[0].collect_schema()
                )
                filter_expr = (
                    sql2polars_filter(filter_expr, pl_schema)
                    if isinstance(filter_expr, str)
                    else filter_expr
                )
                return [d.filter(filter_expr) for d in self._data]
            elif isinstance(self._data[0], pa.Table):
                pa_schema = self._data[0].schema
                filter_expr = (
                    sql2pyarrow_filter(filter_expr, pa_schema)
                    if isinstance(filter_expr, str)
                    else filter_expr
                )
                return [d.filter(filter_expr) for d in self._data]

    @property
    def metadata(self):
        if not hasattr(self, "_metadata"):
            self._load()
        return self._metadata


# @attrs.define # Removed
class BaseDatasetReader(BaseFileReader, gc=False):
    """
    Base class for dataset loading operations supporting various file formats.
    This class provides a foundation for dataset loading operations across different file formats
    including CSV, Parquet, JSON, Arrow, and IPC.

    Args:
        path (str | list[str]): Path or list of paths to file(s).
        format (str, optional): File format extension (without dot).
        fs (AbstractFileSystem, optional): Filesystem instance for handling file operations.
        include_file_path (bool, optional): Include file path in the output DataFrame.
        concat (bool, optional): Concatenate multiple files into a single DataFrame.
        conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
        ctx (datafusion.SessionContext, optional): DataFusion session context instance.
        schema (pa.Schema, optional): PyArrow schema for the dataset.
        partitioning (str | list[str] | pds.Partitioning, optional): Dataset partitioning scheme.

        Examples:
        ```python
        dataset_loader = BaseDatasetReader(
            path="s3://bucket/path/to/files",
            format="csv",
            include_file_path=True,
            concat=True,
            conn=duckdb.connect(),
            ctx=datafusion.SessionContext(),
            schema=pa.schema([
                pa.field("column1", pa.int64()),
                pa.field("column2", pa.string())
            ]),
            partitioning="hive"
        )
        data = dataset_loader.to_polars()
        ```
    Notes:
        - Supports multiple file formats including CSV, Parquet, JSON, Arrow, and IPC
        - Automatically handles filesystem initialization based on path protocol
        - Supports both single path and multiple path inputs
        - Supports loading data into DuckDB and DataFusion for SQL operations
        - Supports custom schema and partitioning for datasets

    """

    schema_: pa.Schema | None = field(default=None)
    _dataset: pds.Dataset | None = field(default=None)
    _pydala_dataset: Any | None = field(default=None)

    def to_pyarrow_dataset(
        self,
        metadata: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> pds.Dataset | tuple[pds.Dataset, dict[str, Any]]:
        """
        Convert data to PyArrow Dataset.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            pds.Dataset: PyArrow Dataset.
        """
        if self._dataset is not None and not reload:
            if metadata:
                return self._dataset, self._metadata
            return self._dataset

        if self.format == ["csv", "arrow", "ipc"]:
            self._dataset = self.fs.pyarrow_dataset(
                self._path,
                format=self.format,
                schema=self.schema_,
                partitioning=self.partitioning,
                **kwargs,
            )
            self._metadata = get_pyarrow_dataset_metadata(
                self._dataset, path=self.path, format=self.format
            )
        elif self.format == "parquet":
            if self.fs.exists(posixpath.join(self._root_path, "_metadata")):
                self._dataset = self.fs.parquet_dataset(
                    posixpath.join(self._root_path, "_metadata"),
                    schema=self.schema_,
                    partitioning=self.partitioning,
                    **kwargs,
                )
            else:
                self._dataset = self.fs.pyarrow_dataset(
                    self._path,
                    format=self.format,
                    schema=self.schema_,
                    partitioning=self.partitioning,
                    **kwargs,
                )
            self._metadata = get_pyarrow_dataset_metadata(
                self._dataset, path=self.path, format=self.format
            )
        else:
            raise ValueError(f"Unsupported format: {self.format}")
        if metadata:
            return self._dataset, self._metadata
        return self._dataset

    def to_pandas(
        self, metadata: bool = False, reload: bool = False, **kwargs
    ) -> pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]:
        """
        Convert data to Pandas DataFrame.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.

        Returns:
            pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]: Pandas DataFrame and optional metadata.
        """
        self.to_pyarrow_dataset(reload=reload, **kwargs)
        df = self._dataset.to_table().to_pandas()
        if metadata:
            metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, metadata
        return df

    def _to_polars_dataframe(
        self, metadata: bool = False, reload: bool = False, **kwargs
    ) -> pl.DataFrame | tuple[pl.DataFrame, dict[str, Any]]:
        self.to_pyarrow_dataset(reload=reload, **kwargs)
        df = pl.from_arrow(self._dataset.to_table())
        if metadata:
            metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, metadata
        return df

    def _to_polars_lazyframe(
        self, metadata: bool = False, reload: bool = False, **kwargs
    ) -> pl.LazyFrame | tuple[pl.LazyFrame, dict[str, Any]]:
        self.to_pyarrow_dataset(reload=reload, **kwargs)
        df = pl.scan_pyarrow_dataset(self._dataset)
        if metadata:
            metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, metadata
        return df

    def to_polars(
        self, lazy: bool = True, metadata: bool = False, reload: bool = False, **kwargs
    ) -> (
        pl.DataFrame | pl.LazyFrame | tuple[pl.DataFrame | pl.LazyFrame, dict[str, Any]]
    ):
        """
        Convert data to Polars DataFrame or LazyFrame.

        Args:
            lazy (bool, optional): Return a LazyFrame if True, else a DataFrame.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            pl.DataFrame | pl.LazyFrame | tuple[pl.DataFrame | pl.LazyFrame, dict[str, Any]]: Polars DataFrame or
                LazyFrame and optional metadata.
        """
        df = (
            self._to_polars_lazyframe(reload=reload, **kwargs)
            if lazy
            else self._to_polars_dataframe(reload=reload, **kwargs)
        )
        if metadata:
            metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, metadata
        return df

    def to_pyarrow_table(
        self, metadata: bool = False, reload: bool = False, **kwargs
    ) -> pa.Table | tuple[pa.Table, dict]:
        """Convert data to PyArrow Table.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            pa.Table | tuple[pa.Table, dict]: PyArrow Table and optional metadata.
        """
        self.to_pyarrow_dataset(reload=reload, **kwargs)
        df = self._dataset.to_table()
        if metadata:
            metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, metadata
        return df

    def to_pydala_dataset(
        self, metadata: bool = False, reload: bool = False, **kwargs
    ) -> ParquetDataset | tuple[ParquetDataset, dict[str, Any]]:  # type: ignore
        """Convert data to Pydala ParquetDataset.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.

        Returns:
            ParquetDataset: Pydala ParquetDataset.
        """
        if ParquetDataset is None:
            raise ImportError("pydala is not installed.")
        if not hasattr(self, "_pydala_dataset") or reload:
            if not hasattr(self, "conn"):
                self._conn = duckdb.connect()
            self._pydala_dataset = self.fs.pydala_dataset(
                self._path,
                partitioning=self.partitioning,
                ddb_con=self._conn,
                **kwargs,
            )
            self._pydala_dataset.load(update_metadata=True)
            self._metadata = get_pyarrow_dataset_metadata(
                self._pydala_dataset._arrow_dataset, path=self.path, format=self.format
            )
        if metadata:
            return self._pydala_dataset, self._metadata
        return self._pydala_dataset

    def to_duckdb_relation(
        self,
        conn: duckdb.DuckDBPyConnection | None = None,
        metadata: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> duckdb.DuckDBPyRelation | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]:
        """Convert data to DuckDB relation.

        Args:
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            duckdb.DuckDBPyRelation | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]: DuckDB relation and optional
                metadata.
        """
        if self._conn is None:
            if conn is None:
                conn = duckdb.connect()
            self._conn = conn

        self.to_pyarrow_dataset(reload=reload, **kwargs)
        if metadata:
            return self._conn.from_arrow(self._dataset), self._metadata
        return self._conn.from_arrow(self._dataset)

    def register_in_duckdb(
        self,
        conn: duckdb.DuckDBPyConnection | None = None,
        name: str | None = None,
        metadata: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]:
        """Register data in DuckDB.

        Args:
            conn (duckdb.DuckDBPyConnection): DuckDB connection instance.
            name (str, optional): Name for the DuckDB table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]: DuckDB connection instance
                or DuckDB connection instance and optional metadata.
        """
        if name is None:
            name = f"{self.format}:{self.path}"

        if self._conn is None:
            if conn is None:
                conn = duckdb.connect()
            self._conn = conn

        self._conn.register(name, self._dataset)
        if metadata:
            return self._conn, self._metadata
        return self._conn

    def to_duckdb(
        self,
        as_relation: bool = True,
        conn: duckdb.DuckDBPyConnection | None = None,
        name: str | None = None,
        metadata: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> (
        duckdb.DuckDBPyRelation
        | duckdb.DuckDBPyConnection
        | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]
        | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]
    ):
        """Convert data to DuckDB relation or register in DuckDB.

        Args:
            as_relation (bool, optional): Return a DuckDB relation if True, else register in DuckDB. Default is True.
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            name (str, optional): Name for the DuckDB table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyRelation | duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyRelation, dict[str, Any]] |
                tuple[duckdb.DuckDBPyConnection, dict[str, Any]]: DuckDB relation or connection instance
                or DuckDB relation or connection instance and optional metadata.

        """
        if as_relation:
            return self.to_duckdb_relation(
                conn=conn, metadata=metadata, reload=reload, **kwargs
            )
        return self.register_in_duckdb(
            conn=conn, name=name, metadata=metadata, reload=reload, **kwargs
        )

    def register_in_datafusion(
        self,
        ctx: datafusion.SessionContext,
        name: str | None = None,
        metadata: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> datafusion.SessionContext | tuple[datafusion.SessionContext, dict[str, Any]]:
        """Register data in DataFusion.

        Args:
            ctx (datafusion.SessionContext): DataFusion session context instance.
            name (str, optional): Name for the DataFusion table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        if name is None:
            name = f"{self.format}:{self.path}"

        if self._ctx is None:
            if ctx is None:
                ctx = datafusion.SessionContext()
            self._ctx = ctx

        self._ctx.register_record_batches(name, [self.to_pyarrow_table().to_batches()])

    def filter(
        self, filter_expr: str | pl.Expr | pa.compute.Expression
    ) -> (
        pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | list[pl.DataFrame]
        | list[pl.LazyFrame]
        | list[pa.Table]
    ):
        """Filter data based on a filter expression.

        Args:
            filter_expr (str | pl.Expr | pa.compute.Expression): Filter expression. Can be a SQL expression, Polars
                expression, or PyArrow compute expression.

        Returns:
            pl.DataFrame | pl.LazyFrame | pa.Table | list[pl.DataFrame] | list[pl.LazyFrame]
                | list[pa.Table]: Filtered data.
        """
        if isinstance(self._data, pl.DataFrame | pl.LazyFrame):
            pl_schema = (
                self._data.schema
                if isinstance(self._data, pl.DataFrame)
                else self._data.collect_schema()
            )
            filter_expr = (
                sql2polars_filter(filter_expr, pl_schema)
                if isinstance(filter_expr, str)
                else filter_expr
            )
            return self._data.filter(filter_expr)

        elif isinstance(self._data, pa.Table):
            pa_schema = self._data.schema
            filter_expr = (
                sql2pyarrow_filter(filter_expr, pa_schema)
                if isinstance(filter_expr, str)
                else filter_expr
            )
            return self._data.filter(filter_expr)

        if isinstance(self._data, str):
            if isinstance(self._data[0], pl.DataFrame | pl.LazyFrame):
                pl_schema = (
                    self._data.schema
                    if isinstance(self._data[0], pl.DataFrame)
                    else self._data[0].collect_schema()
                )
                filter_expr = (
                    sql2polars_filter(filter_expr, pl_schema)
                    if isinstance(filter_expr, str)
                    else filter_expr
                )
                return [d.filter(filter_expr) for d in self._data]
            elif isinstance(self._data[0], pa.Table):
                pa_schema = self._data[0].schema
                filter_expr = (
                    sql2pyarrow_filter(filter_expr, pa_schema)
                    if isinstance(filter_expr, str)
                    else filter_expr
                )
                return [d.filter(filter_expr) for d in self._data]

    @property
    def metadata(self):
        if not hasattr(self, "_metadata"):
            self._load()
        return self._metadata


# @attrs.define # Removed
class BaseFileWriter(BaseFileIO, gc=False):
    """
    Base class for file writing operations supporting various storage backends.
    This class provides a foundation for file writing operations across different storage systems
    including AWS S3, Google Cloud Storage, Azure Blob Storage, GitHub, and GitLab.

    Args:
        path (str | list[str]): Path or list of paths to file(s).
        storage_options (AwsStorageOptions | GcsStorageOptions | AzureStorageOptions |
                             GitHubStorageOptions | GitLabStorageOptions | dict[str, Any] |  None, optional):
                             Storage-specific options for accessing remote filesystems.
        fs (AbstractFileSystem, optional): Filesystem instance for handling file operations.
        format (str, optional): File format extension (without dot).
        basename (str, optional): Basename for the output file(s).
        concat (bool, optional): Concatenate multiple files into a single DataFrame.
        mode (str, optional): Write mode (append, overwrite, delete_matching, error_if_exists).
        unique (bool | list[str] | str, optional): Unique columns for deduplication.

    Examples:
        ```python
        file_writer = BaseFileWriter(
            path="s3://bucket/path/to/files",
            storage_options=AwsStorageOptions(
                key="access_key",
                secret="secret_key"),
            format="csv",
            basename="output",
            concat=True,
            mode="append",
            unique=True
        )
        file_writer.write(data=df)
        ```

    Notes:
        - Supports multiple cloud storage backends through different storage options
        - Automatically handles filesystem initialization based on path protocol
        - Supports both single path and multiple path inputs
        - Supports writing data to cloud storage with various write modes
    """

    basename: str | None = field(default=None)
    concat: bool = field(default=False)
    mode: str = field(default="append")
    unique: bool | list[str] | str = field(default=False)

    def write(
        self,
        data: (
            pl.DataFrame
            | pl.LazyFrame
            | pa.Table
            | pd.DataFrame
            | dict[str, Any]
            | list[
                pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict[str, Any]
            ]
        ),
        basename: str | None = None,
        concat: bool | None = None,
        unique: bool | list[str] | str | None = None,
        mode: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Write data to file.

        Args:
            data (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict[str, Any] | list[pl.DataFrame |
                pl.LazyFrame | pa.Table | pd.DataFrame | dict[str, Any]] | None, optional): Data to write.
            basename (str, optional): Basename for the output file(s).
            concat (bool, optional): Concatenate multiple files into a single DataFrame.
            unique (bool | list[str] | str, optional): Unique columns for deduplication.
            mode (str, optional): Write mode (append, overwrite, delete_matching, error_if_exists).
            **kwargs: Additional keyword arguments.

        Returns:
            dict[str, Any]: Metadata for the written data
        """
        if isinstance(data, list):
            if isinstance(data[0], dict):
                data = _dict_to_dataframe(data)
        if isinstance(data, dict):
            data = _dict_to_dataframe(data)

        self._metadata = get_dataframe_metadata(
            df=data, path=self.path, format=self.format
        )

        self.fs.write_files(
            data=data,  # if data is not None else self.data,
            path=self._path,
            basename=basename or self.basename,
            concat=concat or self.concat,
            unique=unique or self.unique,
            mode=mode or self.mode,
            **kwargs,
        )
        return self._metadata

    @property
    def metadata(self):
        if not hasattr(self, "_metadata"):
            return {}
        return self._metadata


# @attrs.define # Removed
class BaseDatasetWriter(BaseFileWriter, gc=False):
    """
    Base class for dataset writing operations supporting various file formats.
    This class provides a foundation for dataset writing operations across different file formats
    including CSV, Parquet, JSON, Arrow, and IPC.

    Args:
        path (str | list[str]): Path or list of paths to file(s).
        format (str, optional): File format extension (without dot).
        storage_options (AwsStorageOptions | GcsStorageOptions | AzureStorageOptions |
                                GitHubStorageOptions | GitLabStorageOptions | dict[str, Any] |  None, optional):
            Storage-specific options for accessing remote filesystems.
        fs (AbstractFileSystem, optional): Filesystem instance for handling file operations.
        basename (str, optional): Basename for the output file(s).
        schema (pa.Schema, optional): PyArrow schema for the dataset.
        partition_by (str | list[str] | pds.Partitioning, optional): Dataset partitioning scheme.
        partitioning_flavor (str, optional): Partitioning flavor for the dataset.
        compression (str, optional): Compression codec for the dataset.
        row_group_size (int, optional): Row group size for the dataset.
        max_rows_per_file (int, optional): Maximum number of rows per file.
        concat (bool, optional): Concatenate multiple files into a single DataFrame.
        unique (bool | list[str] | str, optional): Unique columns for deduplication.
        mode (str, optional): Write mode (append, overwrite, delete_matching, error_if_exists).
        is_pydala_dataset (bool, optional): Write data as a Pydala ParquetDataset.

    Examples:
        ```python
        dataset_writer = BaseDatasetWriter(
            path="s3://bucket/path/to/files",
            format="parquet",
            storage_options=AwsStorageOptions(
                key="access_key",
                secret="secret_key"),
            basename="output",
            schema=pa.schema([
                pa.field("column1", pa.int64()),
                pa.field("column2", pa.string())
            ]),
            partition_by="column1",
            partitioning_flavor="hive",
            compression="zstd",
            row_group_size=250_000,
            max_rows_per_file=2_500_000,
            concat=True,
            unique=True,
            mode="append",
            is_pydala_dataset=False
        )
        dataset_writer.write(data=df)
        ```
    Notes:
        - Supports multiple file formats including CSV, Parquet, JSON, Arrow, and IPC
        - Automatically handles filesystem initialization based on path protocol
        - Supports both single path and multiple path inputs
        - Supports writing data to cloud storage with various write modes
        - Supports writing data as a Pydala ParquetDataset
    """

    # basename, concat, unique, mode are inherited from BaseFileWriter
    schema_: pa.Schema | None = None
    partition_by: str | list[str] | pds.Partitioning | None = None
    partitioning_flavor: str | None = None
    compression: str = "zstd"
    row_group_size: int | None = 250_000
    max_rows_per_file: int | None = 2_500_000
    is_pydala_dataset: bool = False

    def write(
        self,
        data: (
            pl.DataFrame
            | pl.LazyFrame
            | pa.Table
            | pa.RecordBatch
            | pa.RecordBatchReader
            | pd.DataFrame
            | dict[str, Any]
            | list[
                pl.DataFrame
                | pl.LazyFrame
                | pa.Table
                | pa.RecordBatch
                | pa.RecordBatchReader
                | pd.DataFrame
                | dict[str, Any]
            ]
        ),
        concat: bool | None = None,
        unique: bool | list[str] | str | None = None,
        mode: str | None = None,
        delta_subset: str | None = None,
        alter_schema: bool = False,
        update_metadata: bool = True,
        timestamp_column: str | None = None,
        verbose: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Write data to dataset.

        Args:
            data (pl.DataFrame | pl.LazyFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader | pd.DataFrame |
                dict[str, Any] | list[pl.DataFrame | pl.LazyFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader |
                pd.DataFrame | dict[str, Any]] | None, optional): Data to write.
            unique (bool | list[str] | str, optional): Unique columns for deduplication.
            delta_subset (str | None, optional): Delta subset for incremental updates.
            alter_schema (bool, optional): Alter schema for compatibility.
            update_metadata (bool, optional): Update metadata.
            timestamp_column (str | None, optional): Timestamp column for updates.
            verbose (bool, optional): Verbose output.
            **kwargs: Additional keyword arguments.

        Returns:
            dict[str, Any]: Metadata of the written data.
        """
        basename = kwargs.pop("basename", self.basename)
        schema = kwargs.pop("schema", self.schema_)
        partition_by = kwargs.pop("partition_by", self.partition_by)
        partitioning_flavor = kwargs.pop(
            "partitioning_flavor", self.partitioning_flavor
        )
        compression = kwargs.pop("compression", self.compression)
        row_group_size = kwargs.pop("row_group_size", self.row_group_size)
        max_rows_per_file = kwargs.pop("max_rows_per_file", self.max_rows_per_file)

        if isinstance(data, list):
            if isinstance(data[0], dict):
                data = _dict_to_dataframe(data)
        if isinstance(data, dict):
            data = _dict_to_dataframe(data)

        self._metadata = get_dataframe_metadata(
            df=data, path=self.path, format=self.format
        )

        if not self.is_pydala_dataset:
            self.fs.write_pyarrow_dataset(
                data=data,  # if data is not None else self.data,
                path=self._path,
                basename=basename or self.basename,
                schema=schema or self.schema_,
                partition_by=partition_by or self.partition_by,
                partitioning_flavor=partitioning_flavor or self.partitioning_flavor,
                format=self.format,
                compression=compression or self.compression,
                row_group_size=row_group_size or self.row_group_size,
                max_rows_per_file=max_rows_per_file or self.max_rows_per_file,
                concat=concat or self.concat,
                unique=unique or self.unique,
                mode=mode or self.mode,
                **kwargs,
            )
        else:
            self.fs.write_pydala_dataset(
                data=data,  # if data is not None else self.data,
                path=self._path,
                mode=mode or self.mode,
                basename=basename or self.basename,
                schema=schema or self.schema_,
                partition_by=partition_by or self.partition_by,
                compression=compression or self.compression,
                row_group_size=row_group_size or self.row_group_size,
                max_rows_per_file=max_rows_per_file or self.max_rows_per_file,
                concat=concat or self.concat,
                unique=unique or self.unique,
                delta_subset=delta_subset,
                alter_schema=alter_schema,
                update_metadata=update_metadata,
                timestamp_column=timestamp_column,
                verbose=verbose,
                **kwargs,
            )
        return self._metadata

    @property
    def metadata(self):
        if not hasattr(self, "_metadata"):
            return {}
        return self._metadata


# @attrs.define # Removed
class BaseDatabaseIO(msgspec.Struct, gc=False):
    """
    Base class for database read/write operations supporting various database systems.
    This class provides a foundation for database read/write operations across different database systems
    including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle.

    Args:
        type_ (str): Database type (sqlite, duckdb, postgres, mysql, mssql, oracle).
        table_name (str): Table name in the database.
        path (str | None, optional): File path for SQLite or DuckDB databases.
        connection_string (str | None, optional): Connection string for SQLAlchemy-based databases.
        username (str | None, optional): Username for the database.
        password (str | None, optional): Password for the database.
        server (str | None, optional): Server address for the database.
        port (str | None, optional): Port number for the database.
        database (str | None, optional): Database name.

    Examples:
        ```python
        db_reader = BaseDatabaseIO(
            type_="sqlite",
            table_name="table_name",
            path="path/to/database.db"
        )
        data = db_reader.read()
        ```

    Notes:
        - Supports multiple database systems including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle
        - Automatically handles database initialization based on connection parameters
        - Supports reading data from databases into DataFrames
        - Supports writing data to databases from DataFrames
    """

    type_: str
    table_name: str = field(default="")
    path: str | None = field(default=None)
    username: str | None = field(default=None)
    password: str | None = field(default=None)
    server: str | None = field(default=None)
    port: str | int | None = field(default=None)
    database: str | None = field(default=None)
    ssl: bool = field(default=False)
    connection_string: str | None = field(default=None)
    _metadata: dict[str, Any] = field(default_factory=dict)
    _data: pa.Table | pl.DataFrame | pl.LazyFrame | pd.DataFrame | None = field(
        default=None
    )
    _conn: duckdb.DuckDBPyConnection | None = field(default=None)
    _ctx: datafusion.SessionContext | None = field(default=None)

    def __post_init__(self):  # Renamed from __attrs_post_init__
        db = self.type_.lower()
        if (
            db in ["postgres", "mysql", "mssql", "oracle"]
            and not self.connection_string
        ):
            if not all([
                self.username,
                self.password,
                self.server,
                self.port,
                self.database,
            ]):
                raise ValueError(
                    f"{self.type_} requires connection_string or username, password, server, port, and table_name "
                    "to build it."
                )
            if db == "postgres":
                ssl_mode = "?sslmode=require" if self.ssl else ""
                self.connection_string = (
                    f"postgresql://{self.username}:{self.password}@{self.server}:{self.port}/"
                    f"{self.database}{ssl_mode}"
                )
            elif db == "mysql":
                ssl_mode = "?ssl=true" if self.ssl else ""
                self.connection_string = (
                    f"mysql+pymysql://{self.username}:{self.password}@{self.server}:{self.port}/"
                    f"{self.database}{ssl_mode}"
                )
            elif db == "mssql":
                ssl_mode = ";Encrypt=yes;TrustServerCertificate=yes" if self.ssl else ""
                self.connection_string = (
                    f"mssql+pyodbc://{self.username}:{self.password}@{self.server}:{self.port}/"
                    f"{self.database}?driver=ODBC+Driver+17+for+SQL+Server{ssl_mode}"
                )
            elif db == "oracle":
                ssl_mode = "?ssl=true" if self.ssl else ""
                self.connection_string = (
                    f"oracle+cx_oracle://{self.username}:{self.password}@{self.server}:{self.port}/"
                    f"{self.database}{ssl_mode}"
                )
        if db in ["sqlite", "sqlite3"]:
            if not self.path:
                raise ValueError("SQLite requires a file path.")
            self.connection_string = f"sqlite:///{self.path}"
        elif db == "duckdb":
            if not self.path:
                raise ValueError("DuckDB requires a file path.")
            self.connection_string = self.path

    def execute(self, query: str, cursor: bool = True, **query_kwargs):
        """Execute a SQL query.

        Args:
            query (str): SQL query.
            cursor (bool, optional): Use cursor for execution. Default is True.
            **query_kwargs: Additional keyword arguments.
        """
        query = query.format(**query_kwargs)
        if self.type_ == "sqlite" or self.type_ == "duckdb":
            with self.connect() as conn:
                if cursor:
                    cur = conn.cursor()
                    res = cur.execute(query)

                else:
                    res = conn.execute(query)

                conn.commit()
                return res

        with self.connect() as conn:
            cur = conn.cursor()
            res = cur.execute(text(query))
            conn.commit()
            return res

    def _to_pandas(
        self,
        data: pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | pa.RecordBatch
        | pa.RecordBatchReader
        | pd.DataFrame
        | dict[str, Any],
    ) -> pd.DataFrame | list[pd.DataFrame]:
        # convert data to pandas DataFrame if needed
        if isinstance(data, pl.DataFrame):
            return data.to_pandas()
        elif isinstance(data, pa.Table):
            return data.to_pandas()
        elif isinstance(data, pl.LazyFrame):
            return data.collect().to_pandas()
        elif isinstance(data, pa.RecordBatch):
            return pa.Table.from_batches([self.data]).to_pandas()
        elif isinstance(data, pa.RecordBatchReader):
            return data.read_all().to_pandas()
        elif isinstance(data, dict):
            return pd.DataFrame(data)
        return data

    def create_engine(self):
        return create_engine(self.connection_string)

    def connect(self):
        if self.type_ == "sqlite":
            conn = sqlite3.connect(self.path)
            # Activate WAL mode:
            conn.execute("PRAGMA journal_mode=WAL;")
            return conn
        if self.type_ == "duckdb":
            return duckdb.connect(database=self.path)
        return self.create_engine().connect()


# @attrs.define # Removed
class BaseDatabaseWriter(BaseDatabaseIO, gc=False):
    """
    Base class for database writing operations supporting various database systems.
    This class provides a foundation for database writing operations across different database systems
    including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle.

    Args:
        type_ (str): Database type (sqlite, duckdb, postgres, mysql, mssql, oracle).
        table_name (str): Table name in the database.
        path (str | None, optional): File path for SQLite or DuckDB databases.
        connection_string (str | None, optional): Connection string for SQLAlchemy-based databases.
        username (str | None, optional): Username for the database.
        password (str | None, optional): Password for the database.
        server (str | None, optional): Server address for the database.
        port (str | None, optional): Port number for the database.
        database (str | None, optional): Database name.
        mode (str, optional): Write mode (append, replace, fail).
        concat (bool, optional): Concatenate multiple files into a single DataFrame.
        unique (bool | list[str] | str, optional): Unique columns for deduplication.

    Examples:
        ```python
        db_writer = BaseDatabaseWriter(
            type_="sqlite",
            table_name="table_name",
            path="path/to/database.db"
        )
        db_writer.write(data=df)
        ```

    Notes:
        - Supports multiple database systems including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle
        - Automatically handles database initialization based on connection parameters
        - Supports writing data to databases from DataFrames
    """

    mode: str = field(default="append")  # append, replace, fail
    concat: bool = field(default=False)
    unique: bool | list[str] | str = field(default=False)

    def _write_sqlite(
        self,
        data: pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | pa.RecordBatch
        | pa.RecordBatchReader
        | pd.DataFrame
        | dict[str, Any]
        | list[pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict[str, Any]],
        mode: str | None = None,
        concat: bool | None = None,
        unique: bool | list[str] | str | None = None,
    ) -> dict[str, Any]:
        if not self.path:
            raise ValueError("SQLite requires a file path.")

        data = to_pyarrow_table(
            data, unique=unique or self.unique, concat=concat or self.concat
        )
        if not isinstance(data, list):
            data = [data]

        with sqlite3.connect(self.path) as conn:
            # Activate WAL mode:
            conn.execute("PRAGMA journal_mode=WAL;")

        self._metadata = get_dataframe_metadata(
            df=data, path=self.connection_string, format=self.type_
        )

        for n, _data in enumerate(data):
            df = self._to_pandas(_data)
            df.to_sql(self.table_name, conn, if_exists=mode or self.mode, index=False)

        return self._metadata

    def _write_duckdb(
        self,
        data: pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | pa.RecordBatch
        | pa.RecordBatchReader
        | pd.DataFrame
        | dict[str, Any]
        | list[pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict[str, Any]],
        mode: str | None = None,
        concat: bool | None = None,
        unique: bool | list[str] | str | None = None,
    ) -> dict[str, Any]:
        if not self.path:
            raise ValueError("DuckDB requires a file path.")

        data = to_pyarrow_table(
            data, unique=unique or self.unique, concat=concat or self.concat
        )
        if not isinstance(data, list):
            data = [data]

        self._metadata = get_dataframe_metadata(
            df=data, path=self.connection_string, format=self.type_
        )

        with duckdb.connect(database=self.path) as conn:
            mode = mode or self.mode
            for _data in data:
                conn.register(f"temp_{self.table_name}", _data)
                if mode == "append":
                    conn.execute(
                        f"CREATE TABLE IF NOT EXISTS {self.table_name} AS SELECT * FROM temp_{self.table_name} LIMIT 0;"
                    )
                    conn.execute(
                        f"INSERT INTO {self.table_name} SELECT * FROM temp_{self.table_name};"
                    )
                elif mode == "replace":
                    conn.execute(
                        f"CREATE OR REPLACE TABLE {self.table_name} AS SELECT * FROM temp_{self.table_name};"
                    )
                elif mode == "fail":
                    try:
                        conn.execute(
                            f"CREATE TABLE {self.table_name} AS SELECT * FROM temp_{self.table_name};"
                        )
                    except Exception as e:
                        raise e

                conn.execute(
                    f"DROP TABLE temp_{self.table_name};"
                )  # Fixed: TABLE not VIEW

        return self._metadata

    def _write_sqlalchemy(
        self,
        data: pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | pa.RecordBatch
        | pa.RecordBatchReader
        | pd.DataFrame
        | dict[str, Any]
        | list[pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict[str, Any]],
        mode: str | None = None,
        concat: bool | None = None,
        unique: bool | list[str] | str | None = None,
    ) -> dict[str, Any]:
        if not self.connection_string:
            raise ValueError(f"{self.type_} requires a connection string.")

        data = to_pyarrow_table(
            data, unique=unique or self.unique, concat=concat or self.concat
        )
        if not isinstance(data, list):
            data = [data]

        self._metadata = get_dataframe_metadata(
            df=data, path=self.connection_string, format=self.type_
        )

        engine = create_engine(self.connection_string)
        for _data in data:
            df = self._to_pandas(_data)
            df.to_sql(self.table_name, engine, if_exists=mode or self.mode, index=False)
        engine.dispose()

        return self._metadata

    def write(
        self,
        data: pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | pa.RecordBatch
        | pa.RecordBatchReader
        | pd.DataFrame
        | dict[str, Any]
        | list[pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict[str, Any]],
        mode: str | None = None,
        concat: bool | None = None,
        unique: bool | list[str] | str | None = None,
    ) -> dict[str, Any]:
        """
        Write data to database.

        Args:
            data (pl.DataFrame | pl.LazyFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader | pd.DataFrame |
                dict[str, Any] | list[pl.DataFrame | pl.LazyFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader |
                pd.DataFrame | dict[str, Any]], optional): Data to write.
            mode (str, optional): Write mode (append, replace, fail).
            concat (bool, optional): Concatenate multiple files into a single DataFrame.
            unique (bool | list[str] | str, optional): Unique columns for deduplication.

        Returns:
            dict[str, Any]: Metadata of the written data
        """
        db = self.type_.lower()
        if db == "sqlite":
            return self._write_sqlite(
                data=data, mode=mode, concat=concat, unique=unique
            )
        elif db == "duckdb":
            return self._write_duckdb(
                data=data, mode=mode, concat=concat, unique=unique
            )
        elif db in ["postgres", "mysql", "mssql", "oracle"]:
            return self._write_sqlalchemy(
                data=data, mode=mode, concat=concat, unique=unique
            )
        else:
            raise ValueError(f"Unsupported database type: {self.type_}")

    @property
    def metadata(self):
        if not hasattr(self, "_metadata"):
            return {}
        return self._metadata


# @attrs.define # Removed
class BaseDatabaseReader(BaseDatabaseIO, gc=False):
    """
    Base class for database read operations supporting various database systems.
    This class provides a foundation for database read operations across different database systems
    including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle.

    Args:
        type_ (str): Database type (sqlite, duckdb, postgres, mysql, mssql, oracle).
        table_name (str): Table name in the database.
        path (str | None, optional): File path for SQLite or DuckDB databases.
        connection_string (str | None, optional): Connection string for SQLAlchemy-based databases.
        username (str | None, optional): Username for the database.
        password (str | None, optional): Password for the database.
        server (str | None, optional): Server address for the database.
        port (str | None, optional): Port number for the database.
        database (str | None, optional): Database name.
        query (str | None, optional): SQL query to execute.

    Examples:
        ```python
        db_reader = BaseDatabaseReader(
            type_="sqlite",
            table_name="table_name",
            path="path/to/database.db"
        )
        data = db_reader.read()
        ```
    Notes:
        - Supports multiple database systems including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle
        - Automatically handles database initialization based on connection parameters
        - Supports reading data from databases into DataFrames
    """

    query: str | None = None

    def __post_init__(self):  # Renamed from __attrs_post_init__
        super().__post_init__()  # Call super's post_init if BaseDatabaseIO has one and it's needed
        if self.connection_string is not None:
            if "+" in self.connection_string:
                self.connection_string = (
                    f"{self.connection_string.split('+')[0]}://"
                    f"{self.connection_string.split('://')[1]}"
                )

    def _load(self, query: str | None = None, reload: bool = False, **kwargs) -> None:
        """Load data from database.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        if query is None:
            query = f"SELECT * FROM {self.table_name}"
        else:
            query = query.replace("table", self.table_name)

        if "engine" in kwargs:
            engine = kwargs.pop("engine", "adbc")
        else:
            engine = "adbc"

        if query != self.query:
            reload = True

        self.query = query

        if self.type_ == "duckdb":
            if not self.path:
                raise ValueError("DuckDB requires a file path.")

            if not hasattr(self, "_data") or self._data is None or reload:
                with duckdb.connect(database=self.path) as conn:
                    self._data = conn.execute(query).arrow()

        else:
            if not self.connection_string:
                raise ValueError(f"{self.type_} requires a connection string.")
            if not hasattr(self, "_data") or self._data is None or reload:
                if engine == "connectorx":
                    cs = self.connection_string.replace("///", "//")
                else:
                    cs = self.connection_string
                data = (
                    pl.read_database_uri(
                        query=query,
                        uri=cs,
                        engine=engine,
                        **kwargs,
                    )
                ).to_arrow()
                self._data = data.cast(convert_large_types_to_standard(data.schema))

        self._metadata = get_dataframe_metadata(
            self._data, path=self.connection_string, format=self.type_
        )

    def to_polars(
        self,
        query: str | None = None,
        reload: bool = False,
        metadata: bool = False,
        **kwargs,
    ) -> pl.DataFrame | tuple[pl.DataFrame, dict[str, Any]]:
        """Convert data to Polars DataFrame.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            pl.DataFrame | tuple[pl.DataFrame, dict[str, Any]]: Polars DataFrame or tuple of DataFrame and metadata.
        """
        self._load(query=query, reload=reload, **kwargs)
        df = pl.from_arrow(self._data)
        if metadata:
            return df, self.metadata
        return df

    def to_pandas(
        self,
        query: str | None = None,
        reload: bool = False,
        metadata: bool = False,
        **kwargs,
    ) -> pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]:
        """Convert data to Pandas DataFrame.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]: Pandas DataFrame or tuple of DataFrame and metadata.
        """
        self._load(query=query, reload=reload, **kwargs)
        df = self._data.to_pandas()
        if metadata:
            return df, self.metadata
        return df

    def to_pyarrow_table(
        self,
        query: str | None = None,
        reload: bool = False,
        metadata: bool = False,
        **kwargs,
    ) -> pa.Table:
        """Convert data to PyArrow Table.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            pa.Table | tuple[pa.Table, dict[str, Any]]: PyArrow Table or tuple of Table and metadata.
        """
        self._load(query=query, reload=reload, **kwargs)
        if metadata:
            return self._data, self.metadata
        return self._data

    def to_duckdb_relation(
        self,
        query: str | None = None,
        reload: bool = False,
        metadata: bool = False,
        conn: duckdb.DuckDBPyConnection | None = None,
        **kwargs,
    ) -> duckdb.DuckDBPyRelation | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]:
        """Convert data to DuckDB relation.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyRelation: DuckDB relation.
        """
        self._load(query=query, reload=reload, **kwargs)
        if self._conn is None:
            if conn is None:
                conn = duckdb.connect()
            self._conn = conn
        if metadata:
            return self._conn.from_arrow(self._data), self.metadata
        return self._conn.from_arrow(self._data)

    def register_in_duckdb(
        self,
        query: str | None = None,
        reload: bool = False,
        conn: duckdb.DuckDBPyConnection | None = None,
        name: str | None = None,
        **kwargs,
    ) -> None:
        """Register data in DuckDB.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            name (str, optional): Name of the relation.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        if name is None:
            name = f"{self.type_}:{self.table_name}"

        if self._conn is None:
            if conn is None:
                conn = duckdb.connect()
            self._conn = conn

        self._load(query=query, reload=reload, **kwargs)
        self._conn.register(name, self._data)

    def register_in_datafusion(
        self,
        query: str | None = None,
        reload: bool = False,
        ctx: datafusion.SessionContext | None = None,
        name: str | None = None,
        **kwargs,
    ) -> None:
        """Register data in DataFusion.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            ctx (datafusion.SessionContext, optional): DataFusion session context instance.
            name (str, optional): Name of the relation.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        if name is None:
            name = f"{self.type_}:{self.table_name}"

        if self._ctx is None:
            if ctx is None:
                ctx = datafusion.SessionContext()
            self._ctx = ctx

        self._load(query=query, reload=reload, **kwargs)

        self._ctx.register_record_batches(name, [self.to_pyarrow_table().to_batches()])

    @property
    def metadata(self):
        if not hasattr(self, "_metadata"):
            self._load()
        return self._metadata

    def metadata(self):
        if not hasattr(self, "_metadata"):
            self._load()
        return self._metadata
