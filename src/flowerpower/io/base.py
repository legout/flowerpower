import os
from typing import Any, Generator

import datafusion
import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pds
from fsspec import AbstractFileSystem
from fsspec.utils import get_protocol
from pydantic import BaseModel, ConfigDict

from ..filesystem import get_filesystem
from ..utils.polars import pl
from ..utils.sql import sql2polars_filter, sql2pyarrow_filter
from ..utils.storage_options import (
    # AwsStorageOptions,
    # AzureStorageOptions,
    # GcsStorageOptions,
    # GitHubStorageOptions,
    # GitLabStorageOptions,
    StorageOptions,
)
import importlib

if importlib.util.find_spec("pydala"):
    from pydala.dataset import ParquetDataset
else:
    ParquetDataset = None


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
    storage_options: StorageOptions | dict[str, Any] | None = None
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

        if self.fs is None:
            self.fs = get_filesystem(
                path=self.path if isinstance(self.path, str) else self.path[0],
                storage_options=self.storage_options,
                fs=self.fs,
                dirfs=True,
            )

        if isinstance(self.path, str):
            self.path = (
                self.path.replace(self.storage_options.protocol, "")
                .lstrip("://")
                .replace(f"**/*.{self.format}", "")
                .replace("**", "")
                .replace("*", "")
                .rstrip("//")
                .rstrip("/")
            )

    @property
    def _path(self):
        if self.fs.protocol == "dir":
            if isinstance(self.path, list):
                return [p.lstrip(self.fs.path).lstrip("/") for p in self.path]
            else:
                return self.path.lstrip(self.fs.path).lstrip("/")
        return self.path

    @property
    def _glob_path(self):
        if isinstance(self._path, list):
            return
        else:
            if self.format is not None:
                if f"**/*.{self.format}" in self._path:
                    return self._path
                else:
                    return f"{self._path}/**/*.{self.format}".lstrip("/")
            else:
                if "**" in self._path:
                    return self._path
                else:
                    return f"{self._path}/**".lstrip("/")

    def list_files(self):
        if isinstance(self._path, list):
            return self._path

        return self.fs.glob(self._glob_path)


class BaseFileLoader(BaseFileIO):
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
        file_loader = BaseFileLoader(
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

    def load(self, **kwargs):
        self.include_file_path = kwargs.pop("include_file_path", self.include_file_path)
        self.concat = kwargs.pop("concat", self.concat)
        self.batch_size = kwargs.pop("batch_size", self.batch_size)

        if not hasattr(self, "_data") or self._data is None:
            self._data = self.fs.read_files(
                path=self._glob_path,
                format=self.format,
                include_file_path=self.include_file_path,
                concat=self.concat,
                jsonlines=self.jsonlines or None,
                batch_size=self.batch_size,
                **kwargs,
            )

        else:
            reload = kwargs.pop("reload", False)
            if self.include_file_path and not "file_path" not in self._data.columns:
                reload = True
            if isinstance(self._data, pl.DataFrame | pa.Table) and not self.concat:
                reload = True
            if isinstance(self._data, Generator):
                reload = True

            if reload:
                self._data = self.fs.read_files(
                    path=self._glob_path,
                    format=self.format,
                    include_file_path=self.include_file_path,
                    concat=self.concat,
                    jsonlines=self.jsonlines or None,
                    batch_size=self.batch_size,
                    **kwargs,
                )

    def to_pandas(self, **kwargs) -> pd.DataFrame | list[pd.DataFrame]:
        """Convert data to Pandas DataFrame(s).

        Returns:
            pd.DataFrame | list[pd.DataFrame]: Pandas DataFrame or list of DataFrames.
        """
        self.load(**kwargs)

    def iter_pandas(
        self, batch_size: int = 1, **kwargs
    ) -> Generator[pd.DataFrame, None, None]:
        """Iterate over Pandas DataFrames.

        Returns:
            Generator[pd.DataFrame, None, None]: Generator of Pandas DataFrames.
        """
        self.load(batch_size=batch_size, **kwargs)
        if isinstance(self._data, list | Generator):
            for df in self._data:
                yield df if isinstance(df, pd.DataFrame) else df.to_pandas()
        else:
            yield (
                self._data
                if isinstance(self._data, pd.DataFrame)
                else self._data.to_pandas()
            )

    def _to_polars_dataframe(self, **kwargs) -> pl.DataFrame | list[pl.DataFrame]:
        """Convert data to Polars DataFrame(s).

        Returns:
            pl.DataFrame | list[pl.DataFrame]: Polars DataFrame or list of DataFrames.
        """
        self.load(**kwargs)
        if isinstance(self._data, list):
            df = [
                df if isinstance(self._data, pl.DataFrame) else pl.from_arrow(df)
                for df in self._data
            ]
            return pl.concat(df) if self.concat else df
        return (
            self._data
            if isinstance(self._data, pl.DataFrame)
            else pl.from_arrow(self._data)
        )

    def _iter_polars_dataframe(
        self, batch_size: int = 1, **kwargs
    ) -> Generator[pl.DataFrame, None, None]:
        """Iterate over Polars DataFrames.

        Returns:
            Generator[pl.DataFrame, None, None]: Generator of Polars DataFrames.
        """
        self.load(batch_size=batch_size, **kwargs)
        if isinstance(self._data, list | Generator):
            for df in self._data:
                yield df if isinstance(df, pl.DataFrame) else pl.from_arrow(df)
        else:
            yield (
                self._data
                if isinstance(self._data, pl.DataFrame)
                else pl.from_arrow(self._data)
            )

    def _to_polars_lazyframe(self, **kwargs) -> pl.LazyFrame | list[pl.LazyFrame]:
        """Convert data to Polars LazyFrame(s).

        Returns:
            pl.LazyFrame | list[pl.LazyFrame]: Polars LazyFrame or list of LazyFrames.
        """
        self.load(**kwargs)
        if not self.concat:
            return [df.lazy() for df in self._to_polars_dataframe()]
        return self._to_polars_dataframe.lazy()

    def _iter_polars_lazyframe(
        self, batch_size: int = 1, **kwargs
    ) -> Generator[pl.LazyFrame, None, None]:
        """Iterate over Polars LazyFrames.

        Returns:
            Generator[pl.LazyFrame, None, None]: Generator of Polars LazyFrames.
        """
        self.load(batch_size=batch_size, **kwargs)
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
        **kwargs,
    ) -> pl.DataFrame | pl.LazyFrame | list[pl.DataFrame] | list[pl.LazyFrame]:
        """Convert data to Polars DataFrame or LazyFrame.

        Args:
            lazy (bool, optional): Return a LazyFrame if True, else a DataFrame.

        Returns:
            pl.DataFrame | pl.LazyFrame | list[pl.DataFrame] | list[pl.LazyFrame]: Polars DataFrame or LazyFrame.

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

    def to_pyarrow_table(self, **kwargs) -> pa.Table | list[pa.Table]:
        """Convert data to PyArrow Table(s).

        Returns:
            pa.Table | list[pa.Table]: PyArrow Table or list of Tables.
        """
        self.load(**kwargs)
        if isinstance(self._data, list):
            df = [
                df.to_arrow(**kwargs) if isinstance(df, pl.DataFrame) else df
                for df in self._data
            ]
            return pa.concat_tables(df) if self.concat else df
        return (
            self._data.to_arrow(**kwargs)
            if isinstance(self._data, pl.DataFrame)
            else self._data
        )

    def iter_pyarrow_table(
        self, batch_size: int = 1, **kwargs
    ) -> Generator[pa.Table, None, None]:
        """Iterate over PyArrow Tables.

        Returns:
            Generator[pa.Table, None, None]: Generator of PyArrow Tables.
        """
        self.load(batch_size=batch_size, **kwargs)
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
        self, conn: duckdb.DuckDBPyConnection | None = None, **kwargs
    ) -> duckdb.DuckDBPyRelation:
        """Convert data to DuckDB relation.

        Args:
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.

        Returns:

            duckdb.DuckDBPyRelation: DuckDB relation.
        """
        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        if hasattr(self, "_data"):
            return self.conn.from_arrow(self.to_pyarrow_table(concat=True))

        else:
            return self.conn.read_csv(self._glob_path, **kwargs)

    def register_in_duckdb(
        self, conn: duckdb.DuckDBPyConnection, name: str | None = None, **kwargs
    ) -> None:
        """Register data in DuckDB.

        Args:
            conn (duckdb.DuckDBPyConnection): DuckDB connection instance.

        Returns:
            None
        """
        if name is None:
            name = f"{self.format}:{self.path}"

        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        if hasattr(self, "_data"):
            self.conn.register(name, self.to_pyarrow_table(concat=True))
        else:
            self.conn.register(name, self.to_duckdb_relation(self.conn, **kwargs))

    def register_in_datafusion(
        self, ctx: datafusion.SessionContext, name: str | None = None, **kwargs
    ) -> None:
        """Register data in DataFusion.

        Args:
            ctx (datafusion.SessionContext): DataFusion session context instance.

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
            name, [self.to_pyarrow_table(concat=True).to_batches()]
        )
        # return ctx

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
            filter_expr (str | pl.Expr | pa.compute.Expression): Filter expression.

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


class BaseDatasetLoader(BaseFileLoader):
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
        dataset_loader = BaseDatasetLoader(
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
        **kwargs,
    ) -> pds.Dataset:
        """
        Convert data to PyArrow Dataset.

        Returns:
            pds.Dataset: PyArrow Dataset.
        """
        if self.format == ["csv", "arrow", "ipc"]:
            self._dataset = self.fs.pyarrow_dataset(
                self._path,
                format=self.format,
                schema=self.schema_,
                partitioning=self.partitioning,
                **kwargs,
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
        else:
            self._dataset = pds.dataset(
                self.to_pyarrow_table(**kwargs), schema=self.schema_
            )
        return self._dataset

    def to_pandas(self, **kwargs) -> pd.DataFrame:
        """
        Convert data to Pandas DataFrame.

        Returns:
            pd.DataFrame: Pandas DataFrame.
        """
        if not hasattr(self, "_dataset"):
            self.to_pyarrow_dataset(**kwargs)
        return self._dataset.to_table().to_pandas()

    def _to_polars_dataframe(self, **kwargs) -> pl.DataFrame:
        if not hasattr(self, "_dataset"):
            self.to_pyarrow_dataset(**kwargs)
        return pl.from_arrow(self._dataset.to_table())

    def _to_polars_lazyframe(self, **kwargs) -> pl.LazyFrame:
        if not hasattr(self, "_dataset"):
            self.to_pyarrow_dataset(**kwargs)
        return pl.scan_pyarrow_dataset(self._dataset)

    def to_polars(self, lazy: bool = True, **kwargs) -> pl.DataFrame | pl.LazyFrame:
        """
        Convert data to Polars DataFrame or LazyFrame.

        Args:
            lazy (bool, optional): Return a LazyFrame if True, else a DataFrame.

        Returns:
            pl.DataFrame | pl.LazyFrame: Polars DataFrame or LazyFrame.
        """
        return (
            self._to_polars_lazyframe(**kwargs)
            if lazy
            else self._to_polars_dataframe(**kwargs)
        )

    def to_pyarrow_table(self, **kwargs) -> pa.Table:
        """Convert data to PyArrow Table.

        Returns:
            pa.Table: PyArrow Table.
        """
        if not hasattr(self, "_dataset"):
            self.to_pyarrow_dataset(**kwargs)
        return self._dataset.to_table()

    def to_pydala_dataset(self, **kwargs) -> ParquetDataset:
        if ParquetDataset is None:
            raise ImportError("pydala is not installed.")
        if not hasattr(self, "_pydala_dataset"):
            if not hasattr(self, "conn"):
                self.conn = duckdb.connect()
            self._pydala_dataset = self.fs.pydala_dataset(
                self._path,
                partitioning=self.partitioning,
                ddb_con=self.conn,
                **kwargs,
            )
        return self._pydala_dataset

    def to_duckdb_relation(
        self, conn: duckdb.DuckDBPyConnection | None = None, **kwargs
    ) -> duckdb.DuckDBPyRelation:
        """Convert data to DuckDB relation.

        Args:
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.

        Returns:
            duckdb.DuckDBPyRelation: DuckDB relation.
        """
        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        if not hasattr(self, "_dataset"):
            self.to_pyarrow_dataset(**kwargs)

        return self.conn.from_arrow(self._dataset)

    def register_in_duckdb(
        self, conn: duckdb.DuckDBPyConnection, name: str | None = None, **kwargs
    ) -> None:
        """Register data in DuckDB.

        Args:
            conn (duckdb.DuckDBPyConnection): DuckDB connection instance.

        Returns:
            None
        """
        if name is None:
            name = f"{self.format}:{self.path}"

        if self.conn is None:
            if conn is None:
                conn = duckdb.connect()
            self.conn = conn

        if not hasattr(self, "_dataset"):
            self.to_pyarrow_dataset(**kwargs)

        self.conn.register(name, self._dataset)
        # return conn

    def register_in_datafusion(
        self, ctx: datafusion.SessionContext, name: str | None = None, **kwargs
    ) -> None:
        """Register data in DataFusion.

        Args:
            ctx (datafusion.SessionContext): DataFusion session context instance.

        Returns:
            None
        """
        if name is None:
            name = f"{self.format}:{self.path}"

        if self.ctx is None:
            if ctx is None:
                ctx = datafusion.SessionContext()
            self.ctx = ctx

        if not hasattr(self, "_dataset"):
            self.to_pyarrow_dataset(**kwargs)

        self.ctx.register_dataset(name, self._dataset)
        # return self.tx

    def filter(self, filter_exp: str | pa.compute.Expression) -> pds.Dataset:
        if not hasattr(self, "_dataset"):
            self.to_pyarrow_dataset()
        if isinstance(filter_exp, str):
            filter_exp = sql2pyarrow_filter(filter_exp, self._dataset.schema)
        return self._dataset.filter(filter_exp)


class BaseFileWriter(BaseFileIO):
    data: (
        pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | pd.DataFrame
        | dict[str, Any]
        | list[pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict[str, Any]]
    ) | None = None
    basename: str | None = None
    concat: bool = False
    mode: str = "append"  # append, overwrite, delete_matching, error_if_exists

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
        ) | None = None,
        basename: str | None = None,
        concat: bool = False,
        mode: str = "append",
        **kwargs,
    ):

        self.fs.write_files(
            data=data or self.data,
            basename=basename or self.basename,
            concat=concat or self.concat,
            mode=mode or self.mode,
            **kwargs,
        )


class BaseDatasetWriter(BaseFileWriter):
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
    ) | None = None
    basename: str | None = None
    schema_: pa.Schema | None = None
    partition_by: str | list[str] | pds.Partitioning | None = None
    partitioning_flavor: str | None = None
    compression: str = "zstd"
    row_group_size: int | None = 250_000
    max_rows_per_file: int | None = 2_500_000
    concat: bool = False
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
        ) | None = None,
        unique: bool | list[str] | str = False,
        delta_subset: str | None = None,
        alter_schema: bool = False,
        update_metadata: bool = True,
        timestamp_column: str | None = None,
        verbose: bool = False,
        **kwargs,
    ):
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
        concat = kwargs.pop("concat", self.concat)
        mode = kwargs.pop("mode", self.mode)

        if not self.is_pydala_dataset:
            self.fs.write_pyarrow_dataset(
                data=data or self.data,
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
                mode=mode or self.mode,
                **kwargs,
            )
        else:
            self.fs.write_pydala_dataset(
                data=data or self.data,
                path=self._path,
                mode=mode,
                basename=basename or self.basename,
                schema=schema or self.schema_,
                partition_flavor=partitioning_flavor or self.partitioning_flavor,
                partition_by=partition_by or self.partition_by,
                compression=compression or self.compression,
                row_group_size=row_group_size or self.row_group_size,
                max_rows_per_file=max_rows_per_file or self.max_rows_per_file,
                concat=concat or self.concat,
                unique=unique,
                delta_subset=delta_subset,
                alter_schema=alter_schema,
                update_metadata=update_metadata,
                timestamp_column=timestamp_column,
                verbose=verbose,
                **kwargs,
            )
