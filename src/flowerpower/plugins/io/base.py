import importlib
import posixpath
from typing import Any, Generator

import datafusion
import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pds
from fsspec import AbstractFileSystem
from fsspec.utils import get_protocol
from pydantic import BaseModel, ConfigDict

from ..fs import get_filesystem
from ..fs.ext import _dict_to_dataframe, path_to_glob
from ..fs.storage_options import (AwsStorageOptions, AzureStorageOptions,
                                  GcsStorageOptions, GitHubStorageOptions,
                                  GitLabStorageOptions, StorageOptions)
from ..utils.misc import convert_large_types_to_standard, to_pyarrow_table
from ..utils.polars import pl
from ..utils.sql import sql2polars_filter, sql2pyarrow_filter
from .metadata import get_dataframe_metadata, get_pyarrow_dataset_metadata

if importlib.util.find_spec("pydala"):
    from pydala.dataset import ParquetDataset
else:
    ParquetDataset = None
import sqlite3

if importlib.util.find_spec("sqlalchemy"):
    from sqlalchemy import create_engine, text
else:
    create_engine = None
    text = None


class BaseFileIO(BaseModel):
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

    model_config = ConfigDict(arbitrary_types_allowed=True)
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
    ) = None
    fs: AbstractFileSystem | None = None
    format: str | None = None

    def model_post_init(self, __context):
        self._raw_path = self.path
        if isinstance(self.storage_options, dict):
            if "protocol" not in self.storage_options:
                self.storage_options["protocol"] = get_protocol(self.path)
            self.storage_options = StorageOptions(
                **self.storage_options
            ).storage_options
        if isinstance(self.storage_options, StorageOptions):
            self.storage_options = self.storage_options.storage_options

        if self.fs is None:
            self.fs = get_filesystem(
                path=self.path if isinstance(self.path, str) else self.path[0],
                storage_options=self.storage_options,
                fs=self.fs,
                dirfs=True,
            )

        if hasattr(self.storage_options, "protocol"):
            protocol = self.storage_options.protocol
        else:
            protocol = self.fs.protocol
            if protocol == "dir":
                protocol = (
                    self.fs.fs.protocol
                    if isinstance(self.fs.fs.protocol, str)
                    else self.fs.fs.protocol[0]
                )
            if isinstance(protocol, list | tuple):
                protocol = protocol[0]

        if isinstance(self.path, str):
            self.path = (
                self.path.replace(protocol + "://", "")
                .replace(f"**/*.{self.format}", "")
                .replace("**", "")
                .replace("*", "")
                .rstrip("/")
            )

    @property
    def _path(self):
        if self.fs.protocol == "dir":
            if isinstance(self.path, list):
                return [
                    p.replace(self.fs.path.lstrip("/"), "").lstrip("/")
                    for p in self.path
                ]
            else:
                return self.path.replace(self.fs.path.lstrip("/"), "").lstrip("/")
        return self.path

    @property
    def _glob_path(self):
        return path_to_glob(self._path, self.format)

    def list_files(self):
        if isinstance(self._path, list):
            return self._path

        return self.fs.glob(self._glob_path)


class BaseFileReader(BaseFileIO):
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

    include_file_path: bool = False
    concat: bool = True
    batch_size: int | None = None
    conn: duckdb.DuckDBPyConnection | None = None
    ctx: datafusion.SessionContext | None = None
    jsonlines: bool | None = None
    partitioning: str | list[str] | pds.Partitioning | None = None

    def _load(self, reload: bool = False, **kwargs):
        if "include_file_path" in kwargs:
            if self.include_file_path != kwargs["include_file_path"]:
                reload = True
                self.include_file_path = kwargs.pop("include_file_path")
            else:
                kwargs.pop("include_file_path")

        if "concat" in kwargs:
            if self.concat != kwargs["concat"]:
                reload = True
                self.concat = kwargs.pop("concat")
            else:
                kwargs.pop("concat")

        if "batch_size" in kwargs:
            if self.batch_size != kwargs["batch_size"]:
                reload = True
                self.batch_size = kwargs.pop("batch_size")
            else:
                kwargs.pop("batch_size")

        if "partitioning" in kwargs:
            if self.partitioning != kwargs["partitioning"]:
                reload = True
                self.partitioning = kwargs.pop("partitioning")
            else:
                kwargs.pop("partitioning")

        if not hasattr(self, "_data") or self._data is None or reload:
            self._data = self.fs.read_files(
                path=self._glob_path,
                format=self.format,
                include_file_path=True,
                concat=self.concat,
                jsonlines=self.jsonlines or None,
                batch_size=self.batch_size,
                partitioning=self.partitioning,
                **kwargs,
            )
            if not isinstance(self._data, Generator):
                self._metadata = get_dataframe_metadata(
                    df=self._data,
                    path=self.path,
                    format=self.format,
                    num_files=pl.from_arrow(self._data.select(["file_path"])).select(
                        pl.n_unique("file_path")
                    )[0, 0],
                )
                if not self.include_file_path:
                    self._data = self._data.drop("file_path")
            else:
                self._metadata = {}

    def to_pandas(
        self, metadata: bool = False, reload: bool = False, **kwargs
    ) -> (
        tuple[pd.DataFrame | list[pd.DataFrame], dict[str, Any]]
        | pd.DataFrame
        | list[pd.DataFrame]
    ):
        """Convert data to Pandas DataFrame(s).

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            tuple[pd.DataFrame | list[pd.DataFrame], dict[str, Any]] | pd.DataFrame | list[pd.DataFrame]: Pandas
                DataFrame or list of DataFrames and optional metadata.
        """
        self._load(reload=reload, **kwargs)
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
            metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, metadata
        return df

    def iter_pandas(
        self, batch_size: int = 1, reload: bool = False, **kwargs
    ) -> Generator[pd.DataFrame, None, None]:
        """Iterate over Pandas DataFrames.

        Args:
            batch_size (int, optional): Batch size for iteration. Default is 1.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            Generator[pd.DataFrame, None, None]: Generator of Pandas DataFrames.
        """
        self._load(batch_size=batch_size, reload=reload, **kwargs)
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
        self, metadata: bool = False, reload: bool = False, **kwargs
    ) -> (
        tuple[pl.DataFrame | list[pl.DataFrame], dict[str, Any]]
        | pl.DataFrame
        | list[pl.DataFrame]
    ):
        self._load(reload=reload, **kwargs)
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
            metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, metadata
        return df

    def _iter_polars_dataframe(
        self, batch_size: int = 1, reload: bool = False, **kwargs
    ) -> Generator[pl.DataFrame, None, None]:
        """Iterate over Polars DataFrames.

        Returns:
            Generator[pl.DataFrame, None, None]: Generator of Polars DataFrames.
        """
        self._load(batch_size=batch_size, reload=reload, **kwargs)
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
        self, metadata: bool = False, reload: bool = False, **kwargs
    ) -> (
        tuple[pl.LazyFrame | list[pl.LazyFrame], dict[str, Any]]
        | pl.LazyFrame
        | list[pl.LazyFrame]
    ):
        self._load(reload=reload, **kwargs)
        if not self.concat:
            df = [df.lazy() for df in self._to_polars_dataframe()]

        else:
            df = self._to_polars_dataframe.lazy()
        if metadata:
            metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, metadata
        return df

    def _iter_polars_lazyframe(
        self, batch_size: int = 1, reload: bool = False, **kwargs
    ) -> Generator[pl.LazyFrame, None, None]:
        """Iterate over Polars LazyFrames.

        Args:
            batch_size (int, optional): Batch size for iteration. Default is 1.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            Generator[pl.LazyFrame, None, None]: Generator of Polars LazyFrames.
        """
        self._load(batch_size=batch_size, reload=reload, **kwargs)
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

        Returns:
            pl.DataFrame | pl.LazyFrame | list[pl.DataFrame] | list[pl.LazyFrame] | tuple[pl.DataFrame | pl.LazyFrame
                | list[pl.DataFrame] | list[pl.LazyFrame], dict[str, Any]]: Polars DataFrame or LazyFrame and optional
                metadata.
        """
        if lazy:
            return self._to_polars_lazyframe(**kwargs)
        return self._to_polars_dataframe(**kwargs)

    def iter_polars(
        self,
        lazy: bool = False,
        batch_size: int = 1,
        **kwargs,
    ) -> Generator[pl.DataFrame | pl.LazyFrame, None, None]:
        if lazy:
            yield from self._iter_polars_lazyframe(batch_size=batch_size, **kwargs)
        yield from self._iter_polars_dataframe(batch_size=batch_size, **kwargs)

    def to_pyarrow_table(
        self, metadata: bool = False, reload: bool = False, **kwargs
    ) -> pa.Table | list[pa.Table] | tuple[pa.Table | list[pa.Table], dict[str, Any]]:
        """Convert data to PyArrow Table(s).

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            pa.Table | list[pa.Table] | tuple[pa.Table | list[pa.Table], dict[str, Any]]: PyArrow Table or list of
                Tables and optional metadata.
        """
        self._load(reload=reload, **kwargs)
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
            metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
            return df, metadata
        return df

    def iter_pyarrow_table(
        self, batch_size: int = 1, reload: bool = False, **kwargs
    ) -> Generator[pa.Table, None, None]:
        """Iterate over PyArrow Tables.

        Returns:
            Generator[pa.Table, None, None]: Generator of PyArrow Tables.
        """
        self._load(batch_size=batch_size, reload=reload, **kwargs)
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
        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        if metadata:
            return self.conn.from_arrow(
                self.to_pyarrow_table(concat=True, reload=reload, **kwargs),
            ), self._metadata
        return self.conn.from_arrow(
            self.to_pyarrow_table(concat=True, reload=reload, **kwargs)
        )

    def register_in_duckdb(
        self,
        conn: duckdb.DuckDBPyConnection,
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

        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        self.conn.register(
            name, self.to_pyarrow_table(concat=True, reload=reload, **kwargs)
        )
        if metadata:
            return self.conn, self._metadata
        return self.conn

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

        if self.ctx is None:
            if ctx is None:
                ctx = datafusion.SessionContext()
            self.ctx = ctx

        self.ctx.register_record_batches(
            name,
            [self.to_pyarrow_table(concat=True, reload=reload, **kwargs).to_batches()],
        )
        if metadata:
            return self.ctx, self._metadata
        return ctx

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


class BaseDatasetReader(BaseFileReader):
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

    schema_: pa.Schema | None = None
    partitioning: str | list[str] | pds.Partitioning | None = None

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
        if hasattr(self, "_dataset") and not reload:
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
            if self.fs.exists(posixpath.join(self._path, "_metadata")):
                self._dataset = self.fs.parquet_dataset(
                    self._path,
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
                self.conn = duckdb.connect()
            self._pydala_dataset = self.fs.pydala_dataset(
                self._path,
                partitioning=self.partitioning,
                ddb_con=self.conn,
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
        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        self.to_pyarrow_dataset(reload=reload, **kwargs)
        if metadata:
            return self.conn.from_arrow(self._dataset), self._metadata
        return self.conn.from_arrow(self._dataset)

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
            **kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]: DuckDB connection instance
                or DuckDB connection instance and optional metadata.
        """
        if name is None:
            name = f"{self.format}:{self.path}"

        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        self.to_pyarrow_dataset(reload=reload, **kwargs)

        self.conn.register(name, self._dataset)
        if metadata:
            return self.conn, self._metadata
        return self.conn

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
            **kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyRelation | duckdb.DuckDBPyConnection: DuckDB relation or connection instance.
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
            **kwargs: Additional keyword arguments.

        Returns:
            datafusion.SessionContext | tuple[datafusion.SessionContext, dict[str, Any]]: DataFusion session
                context or instance and optional metadata.
        """
        if name is None:
            name = f"{self.format}:{self.path}"

        if self.ctx is None:
            if ctx is None:
                ctx = datafusion.SessionContext()
            self.ctx = ctx

        self.to_pyarrow_dataset(reload=reload, **kwargs)

        self.ctx.register_dataset(name, self._dataset)

        if metadata:
            return self.ctx, self._metadata

        return self.ctx

    def filter(self, filter_exp: str | pa.compute.Expression) -> pds.Dataset:
        """
        Filter data based on a filter expression.

        Args:
            filter_exp (str | pa.compute.Expression): Filter expression. Can be a SQL expression or
                PyArrow compute expression.

        Returns:
            pds.Dataset: Filtered dataset.

        """
        if not hasattr(self, "_dataset"):
            self.to_pyarrow_dataset()
        if isinstance(filter_exp, str):
            filter_exp = sql2pyarrow_filter(filter_exp, self._dataset.schema)
        return self._dataset.filter(filter_exp)

    @property
    def metadata(self):
        if not hasattr(self, "_metadata"):
            self.to_pyarrow_dataset()
        return self._metadata


class BaseFileWriter(BaseFileIO):
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

    basename: str | None = None
    concat: bool = False
    mode: str = "append"  # append, overwrite, delete_matching, error_if_exists
    unique: bool | list[str] | str = False

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


class BaseDatasetWriter(BaseFileWriter):
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

    basename: str | None = None
    schema_: pa.Schema | None = None
    partition_by: str | list[str] | pds.Partitioning | None = None
    partitioning_flavor: str | None = None
    compression: str = "zstd"
    row_group_size: int | None = 250_000
    max_rows_per_file: int | None = 2_500_000
    concat: bool = False
    unique: bool | list[str] | str = False
    mode: str = "append"  # append, overwrite, delete_matching, error_if_exists
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
                partition_flavor=partitioning_flavor or self.partitioning_flavor,
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


class BaseDatabaseIO(BaseModel):
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
        mode (str, optional): Write mode (append, replace, fail).

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

    type_: str  # "sqlite", "duckdb", "postgres", "mysql", "mssql", or "oracle"
    table_name: str
    path: str | None = None  # For sqlite or duckdb file paths
    connection_string: str | None = None  # For SQLAlchemy-based databases
    username: str | None = None
    password: str | None = None
    server: str | None = None
    port: str | int | None = None
    database: str | None = None
    ssl: bool = False

    def model_post_init(self, __context):
        db = self.type_.lower()
        if (
            db in ["postgres", "mysql", "mssql", "oracle"]
            and not self.connection_string
        ):
            if not all(
                [
                    self.username,
                    self.password,
                    self.server,
                    self.port,
                    self.database,
                ]
            ):
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


class BaseDatabaseWriter(BaseDatabaseIO):
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

    mode: str = "append"  # append, replace, fail
    concat: bool = False
    unique: bool | list[str] | str = False

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

        conn = sqlite3.connect(self.path)
        # Activate WAL mode:
        conn.execute("PRAGMA journal_mode=WAL;")

        self._metadata = get_dataframe_metadata(
            df=data, path=self.connection_string, format=self.type_
        )

        for n, _data in enumerate(data):
            df = self._to_pandas(_data)
            df.to_sql(self.table_name, conn, if_exists=mode or self.mode, index=False)

        conn.close()
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

        conn = duckdb.connect(database=self.path)
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

            conn.execute(f"DROP TABLE temp_{self.table_name};")

        conn.close()
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
                pd.DataFrame | dict[str, Any]] | None, optional): Data to write.
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


class BaseDatabaseReader(BaseDatabaseIO):
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

    def model_post_init(self, __context):
        super().model_post_init(__context)
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
                conn = duckdb.connect(database=self.path)
                self._data = conn.execute(query).arrow()
                conn.close()

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
        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn
        if metadata:
            return self.conn.from_arrow(self._data), self.metadata
        return self.conn.from_arrow(self._data)

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

        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        self._load(query=query, reload=reload, **kwargs)
        self.conn.register(name, self._data)

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

        if self.ctx is None:
            if ctx is None:
                ctx = datafusion.SessionContext()
            self.ctx = ctx

        self._load(query=query, reload=reload, **kwargs)

        self.ctx.register_record_batches(name, [self.to_pyarrow_table().to_batches()])

    @property
    def metadata(self):
        if not hasattr(self, "_metadata"):
            self._load()
        return self._metadata
