# import datetime as dt


import pyarrow as pa
import pyarrow.dataset as pds
from deltalake import DeltaTable, table
import datetime
from sherlock import RedisLock
from ..base import BaseDatasetReader

# from hamilton.function_modifiers import dataloader


# from ..utils import get_dataframe_metadata, get_delta_metadata


class DeltaTableReader(BaseDatasetReader):
    """Delta table loader.

    This class is responsible for loading Delta tables into several dataframe formats,
    duckdb and datafusion.

    """

    delta_table: DeltaTable | None = None
    with_lock: bool = False
    redis: str | None = None
    format: str = "delta"

    def model_post_init(self, __context):
        super().model_post_init(__context)

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
