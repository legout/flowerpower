# import datetime as dt


import pyarrow as pa
import pyarrow.dataset as pds
from deltalake import DeltaTable, table
import datetime
from sherlock import RedisLock
from ..base import BaseDatasetLoader

# from hamilton.function_modifiers import dataloader


# from ..utils import get_dataframe_metadata, get_delta_metadata


class DeltaTableLoader(BaseDatasetLoader):
    """Delta table loader.

    This class is responsible for loading Delta tables into several dataframe formats,
    duckdb and datafusion.

    """

    delta_table: DeltaTable | None = None
    with_lock: bool = False
    redis: str | None = None

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "delta"

        self.delta_table = DeltaTable(
            self._raw_path,
            storage_options=self.storage_options.to_object_store_kwargs(),
        )
        if self.with_lock and self.redis is None:
            raise ValueError("Redis connection is required when using locks.")

    @property
    def dt(self) -> DeltaTable:
        return self.delta_table

    def to_pyarrow_dataset(self) -> pds.Dataset:
        """Converts the DeltaTable to a PyArrow Dataset."""
        return self.delta_table.to_pyarrow_dataset()

    def to_pyarrow_table(self) -> pa.Table:
        """Converts the DeltaTable to a PyArrow Table."""
        return self.delta_table.to_pyarrow_table()

    def compact(
        self,
        partition_filters: list[tuple[str, str, any]] | None = None,
        target_size: int = None,
        max_concurrent_tasks: int = None,
        min_commit_interval: int | datetime.timedelta | None = None,
        writer_properties: table.WriterProperties = None,
        custom_metadata: dict[str, str] | None = None,
        post_commithook_properties: table.PostCommitHookProperties | None = None,
        commit_properties: table.CommitProperties | None = None,
    ) -> dict[str, any]:
        def _compact():
            self.delta_table.compact(
                partition_filters=partition_filters,
                target_size=target_size,
                max_concurrent_tasks=max_concurrent_tasks,
                min_commit_interval=min_commit_interval,
                writer_properties=writer_properties,
                custom_metadata=custom_metadata,
                post_commithook_properties=post_commithook_properties,
                commit_properties=commit_properties,
            )

        if self.with_lock:
            with RedisLock(
                lock_name=self._raw_path,
                namespace="flowerpower",
                client=self.redis,
                expire=10,
                timeout=5,
                retry_interval=0.1,
            ):
                _compact()
        else:
            _compact()

    def z_order(
        self,
        columns: list[str],
        partition_filters: list[tuple[str, str, any]] | None = None,
        target_size: int = None,
        max_concurrent_tasks: int = None,
        min_commit_interval: int | datetime.timedelta | None = None,
        writer_properties: table.WriterProperties = None,
        custom_metadata: dict[str, str] | None = None,
        post_commithook_properties: table.PostCommitHookProperties | None = None,
        commit_properties: table.CommitProperties | None = None,
    ) -> dict[str, any]:
        def _z_order():
            self.delta_table.z_order(
                columns=columns,
                partition_filters=partition_filters,
                target_size=target_size,
                max_concurrent_tasks=max_concurrent_tasks,
                min_commit_interval=min_commit_interval,
                writer_properties=writer_properties,
                custom_metadata=custom_metadata,
                post_commithook_properties=post_commithook_properties,
                commit_properties=commit_properties,
            )

        if self.with_lock:
            with RedisLock(
                lock_name=self._raw_path,
                namespace="flowerpower",
                client=self.redis,
                expire=10,
                timeout=5,
                retry_interval=0.1,
            ):
                _z_order()
        else:
            _z_order()

    # def to_polars(self, lazy: bool = True) -> pl.DataFrame | pl.LazyFrame:
    #     """Converts the DeltaTable to a Polars DataFrame."""
    #     if lazy:
    #         return pl.scan_pyarrow_dataset(self.to_pyarrow_dataset())

    #     return pl.from_arrow(self.to_pyarrow_table())

    # def to_pandas(self) -> pd.DataFrame:
    #     """Converts the DeltaTable to a Pandas DataFrame."""
    #     return self.to_pyrrow_table().to_pandas()

    # def to_duckdb_relation(
    #     self, conn: duckdb.DuckDBPyConnection | None = None, lazy: bool = True
    # ) -> duckdb.DuckDBPyRelation:
    #     """Converts the DeltaTable to a DuckDB relation."""
    #     if conn is None:
    #         conn = duckdb.connect()
    #     if lazy:
    #         return conn.from_arrow(self.to_pyarrow_dataset())
    #     return conn.from_arrow(self.to_pyarrow_table())

    # def register_in_duckdb(
    #     self,
    #     conn: duckdb.DuckDBPyConnection | None = None,
    #     name: str | None = None,
    #     lazy: bool = True,
    # ) -> duckdb.DuckDBPyConnection:
    #     """Registers the DeltaTable in a DuckDB connection."""
    #     if name is None:
    #         name = f"{self.format}:{self.path}"
    #     if conn is None:
    #         conn = duckdb.connect()
    #     table = self.to_duckdb_relation(conn=conn, lazy=lazy)
    #     conn.register(name, table)
    #     return conn

    # def register_in_datafusion(
    #     self,
    #     ctx: dtf.SessionContext | None = None,
    #     name: str | None = None,
    #     lazy: bool = True,
    # ) -> dtf.SessionContext:
    #     """Registers the DeltaTable in a DataFusion context."""
    #     if name is None:
    #         name = f"{self.format}:{self.path}"
    #     if ctx is None:
    #         ctx = dtf.SessionContext()
    #     if lazy:
    #         ctx.register_dataset(name, self.to_pyarrow_dataset())
    #     else:
    #         ctx.register_record_batches(name, [self.to_pyarrow_table().to_batches()])
    #         # table = table.to_table()
    #     # ctx.register_dataset(name, table)
    #     return ctx
