# import datetime as dt


import pyarrow as pa
import pyarrow.dataset as pds
from deltalake import DeltaTable, table
from deltalake.exceptions import TableNotFoundError
import datetime
from sherlock import RedisLock
from ..base import BaseDatasetReader
from ..metadata import (
    get_delta_metadata,
    get_dataframe_metadata,
    get_pyarrow_dataset_metadata,
)

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
        try:
            self.delta_table = DeltaTable(
                self._raw_path,
                storage_options=self.storage_options.to_object_store_kwargs(),
            )
        except TableNotFoundError:
            raise ValueError(f"Table {self._raw_path} not found.")
        if self.with_lock and self.redis is None:
            raise ValueError("Redis connection is required when using locks.")

    @property
    def dt(self) -> DeltaTable:
        return self.delta_table

    def to_pyarrow_dataset(
        self, metadata: bool = False
    ) -> pds.Dataset | tuple[pds.Dataset, dict[str, any]]:
        """Converts the DeltaTable to a PyArrow Dataset.

        Args:
            metadata (bool, optional): Whether to include metadata. Defaults to False.

        Returns:
            pds.Dataset | tuple[pds.Dataset, dict[str, any]]: PyArrow Dataset or tuple of PyArrow Dataset and metadata.
        """
        self._dataset = self.delta_table.to_pyarrow_dataset()
        if metadata:
            metadata = get_pyarrow_dataset_metadata(
                self._dataset, self._raw_path, "parquet"
            )
            return self._dataset, metadata
        return self._dataset

    def to_pyarrow_table(
        self, metadata: bool = False
    ) -> pa.Table | tuple[pa.Table, dict[str, any]]:
        """Converts the DeltaTable to a PyArrow Table.

        Args:
            metadata (bool, optional): Whether to include metadata. Defaults to False.

        Returns:
            pa.Table | tuple[pa.Table, dict[str, any]]: PyArrow Table or tuple of PyArrow Table and metadata.
        """
        table = self.delta_table.to_pyarrow_table()
        if metadata:
            metadata = get_dataframe_metadata(table, self._raw_path, "parquet")
            return table, metadata
        return table

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

    @property
    def metadata(self) -> dict:
        if not hasattr(self, "_metadata"):
            self._metadata = get_delta_metadata(self.delta_table, self._raw_path)
        return self._metadata
