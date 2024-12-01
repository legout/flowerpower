import os
from typing import Any

import datafusion
import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pds
from fsspec import AbstractFileSystem
from fsspec.utils import get_protocol
from pydantic import BaseModel, ConfigDict, Field

from ..utils.filesystem import get_filesystem
from ..utils.polars import pl
from ..utils.sql import sql2polars_filter, sql2pyarrow_filter
from ..utils.storage_options import (
    AwsStorageOptions,
    AzureStorageOptions,
    GcsStorageOptions,
    GitHubStorageOptions,
    GitLabStorageOptions,
)


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
        AwsStorageOptions
        | GcsStorageOptions
        | AzureStorageOptions
        | GitHubStorageOptions
        | GitLabStorageOptions
        | dict[str, Any]
        | None
    ) = None
    fs: AbstractFileSystem | None = Field(default=None)
    format: str | None = None

    def model_post_init(self, __context):
        # self._update_storage_options_from_env()
        if isinstance(self.path, str):
            self.path = (
                self.path.replace(f"**/*.{format}", "")
                .replace("**", "")
                .replace("*", "")
                .rstrip("//")
                .rstrip("/")
            )

        self._update_fs()

    def _update_storage_options_from_aws_credentials(
        self,
        profile: str = "default",
        allow_invalid_certificates: bool = False,
        allow_http: bool = False,
    ) -> AwsStorageOptions:
        if isinstance(self.storage_options, AwsStorageOptions):
            self.storage_options = self.storage_options.to_aws_credentials(
                profile=profile,
                allow_invalid_certificates=allow_invalid_certificates,
                allow_http=allow_http,
            )
        self._update_fs()

    def _update_storage_options_from_env(
        self,
    ):
        protocol = get_protocol(self.path)
        if protocol == "s3":
            self.storage_options = AwsStorageOptions.from_env()
        elif protocol == "gs" or protocol == "gcs":
            self.storage_options = GcsStorageOptions.from_env()
        elif protocol == "az" or protocol == "abfs":
            self.storage_options = AzureStorageOptions.from_env()
        elif protocol == "github":
            self.storage_options = GitHubStorageOptions.from_env()
        elif protocol == "gitlab":
            self.storage_options = GitLabStorageOptions.from_env()
        self._update_fs()

    def _update_storage_options(self, **kwargs):
        self.storage_options = self.storage_options.model_copy(update=kwargs)
        self._update_fs()

    def _update_fs(self):
        self.fs = get_filesystem(
            self.path if isinstance(self.path, str) else self.path[0],
            self.storage_options,
            dirfs=False,
        )

    def _glob_path(self):
        if isinstance(self.path, list):
            return
        else:
            if self.format is not None:
                if f"**/*.{format}" in self.path:
                    return self.path
                else:
                    return f"{self.path}/**/*.{format}"
            else:
                if "**" in self.path:
                    return self.path
                else:
                    return f"{self.path}/**"

    def list_files(self):
        if isinstance(self.path, list):
            return self.path

        glob_path = self._glob_path()
        return self.fs.glob(glob_path)


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
    conn: duckdb.DuckDBPyConnection | None = None
    ctx: datafusion.SessionContext | None = None

    def _load(self, **kwargs):
        if "include_file_path" not in kwargs:
            self.include_file_path = kwargs.get(
                "include_file_path", self.include_file_path
            )
        if "concat" not in kwargs:
            self.concat = kwargs.get("concat", self.concat)

        if not hasattr(self, "_data"):
            self._data = self.fs.read_files(
                self._glob_path,
                self.format,
                include_file_path=self.include_file_path,
                concat=self.concat,
                jsonlines=self.jsonlines or None,
                **kwargs,
            )
        else:
            reload = False
            if self.include_file_path and not "file_path" not in self._data.columns:
                reload = True
            if isinstance(self._data, pl.DataFrame) and not self.concat:
                reload = True
            if isinstance(self._data, list) and self.concat:
                self._data = pl.concat(self._data, how="diagonal_relaxed")
            if reload:
                self._load(
                    include_file_path=self.include_file_path,
                    concat=self.concat,
                    jsonlines=self.jsonlines or None,
                    **kwargs,
                )

    def to_pandas(self, **kwargs) -> pd.DataFrame | list[pd.DataFrame]:
        """Convert data to Pandas DataFrame(s).

        Returns:
            pd.DataFrame | list[pd.DataFrame]: Pandas DataFrame or list of DataFrames.
        """
        self._load(**kwargs)
        if not self.concat:
            return [df.to_pandas() for df in self._data]
        return self._data.to_pandas()

    def _to_polars_dataframe(self, **kwargs) -> pl.DataFrame | list[pl.DataFrame]:
        """Convert data to Polars DataFrame(s).

        Returns:
            pl.DataFrame | list[pl.DataFrame]: Polars DataFrame or list of DataFrames.
        """
        self._load(self, **kwargs)
        if not self.concat:
            return [
                df if isinstance(self._data, pl.DataFrame) else pl.from_arrow(df)
                for df in self._data
            ]
        return (
            self._data
            if isinstance(self._data, pl.DataFrame)
            else pl.from_arrow(self._data)
        )

    def _to_polars_lazyframe(self, **kwargs) -> pl.LazyFrame | list[pl.LazyFrame]:
        """Convert data to Polars LazyFrame(s).

        Returns:
            pl.LazyFrame | list[pl.LazyFrame]: Polars LazyFrame or list of LazyFrames.
        """
        self._load(**kwargs)
        if not self.concat:
            return [df.lazy() for df in self._to_polars_dataframe()]
        return self._to_polars_dataframe.lazy()

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

    def to_pyarrow_table(self, **kwargs) -> pa.Table | list[pa.Table]:
        """Convert data to PyArrow Table(s).

        Returns:
            pa.Table | list[pa.Table]: PyArrow Table or list of Tables.
        """
        self._load(**kwargs)
        if not self.concat:
            return [
                df.to_arrow(**kwargs) if isinstance(df, pl.DataFrame) else df
                for df in self._data
            ]
        return (
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
            pl.DataFrame | pl.LazyFrame | pa.Table | list[pl.DataFrame] | list[pl.LazyFrame] | list[pa.Table]: Filtered data.
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
            partitioning="column1"
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

    _schema: pa.Schema | None = None
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
                self.path,
                format=self.format,
                schema=self._schema,
                partitioning=self.partitioning,
                **kwargs,
            )
        elif self.format == "parquet":
            if self.fs.exists(os.path.join(self.path, "_metadata")):
                self._dataset = self.fs.parquet_dataset(
                    self.path,
                    schema=self._schema,
                    partitioning=self.partitioning,
                    **kwargs,
                )
            else:
                self._dataset = self.fs.pyarrow_dataset(
                    self.path,
                    format=self.format,
                    schema=self._schema,
                    partitioning=self.partitioning,
                    **kwargs,
                )
        else:
            self._dataset = pds.dataset(
                self.to_pyarrow_table(**kwargs), schema=self._schema
            )

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
        | list[pl.DataFrame]
        | list[pl.LazyFrame]
        | list[pa.Table]
        | list[pd.DataFrame]
    )
    mode: str = "append"

    def model_post_init(self, __context):
        if isinstance(self.data, list) and self.concat:
            if isinstance(self.data[0], pl.DataFrame | pl.LazyFrame):
                self.data = pl.concat(self.data, how="diagonal_relaxed")
            elif isinstance(self.data[0], pa.Table):
                self.data = pa.concat_tables(self.data, promote_options="permissive")
            elif isinstance(self.data[0], pd.DataFrame):
                self.data = pd.concat(self.data)
        self._gen_paths()

    def _gen_paths(self):
        if isinstance(self.path, str) and isinstance(self.data, list):
            if self.path.endswith(self.format):
                self.path = [
                    f"{self.path}-{i}.{self.format}" for i in range(len(self.data))
                ]

    def write(self, data, **kwargs):
        self.fs.write
