# import datetime as dt


import datetime

import pyarrow as pa
import pyarrow.dataset as pds
from deltalake import DeltaTable, table
from deltalake.exceptions import TableNotFoundError
from deltalake.transaction import CommitProperties, PostCommitHookProperties
from deltalake.writer import WriterProperties
from loguru import logger
from msgspec import field
from sherlock import RedisLock

from ..base import BaseDatasetReader
from ..metadata import (get_dataframe_metadata, get_delta_metadata,
                        get_pyarrow_dataset_metadata)


# @attrs.define
class DeltaTableReader(BaseDatasetReader, gc=False):
    """Delta table loader.

    This class is responsible for loading Delta tables into several dataframe formats,
    duckdb and datafusion.

    """

    delta_table: DeltaTable | None = None
    with_lock: bool = False
    redis: str | None = None
    format: str = field(default="delta")

    def __post_init__(self):
        super().__post_init__()

        self._init_dt()
        if self.with_lock and self.redis is None:
            raise ValueError("Redis connection is required when using locks.")

    def _init_dt(self):
        try:
            self.delta_table = DeltaTable(
                self._base_path,
                storage_options=self.storage_options.to_object_store_kwargs(),
            )
        except TableNotFoundError:
            logger.warning(f"Table {self._base_path} not found.")
            self.delta_table = None

    @property
    def dt(self) -> DeltaTable:
        return self.delta_table

    def _load(self, reload: bool = False):
        self.to_pyarrow_table(reload=reload)

    def to_pyarrow_dataset(
        self, metadata: bool = False, reload: bool = False
    ) -> pds.Dataset | tuple[pds.Dataset, dict[str, any]]:
        """Converts the DeltaTable to a PyArrow Dataset.

        Args:
            metadata (bool, optional): Whether to include metadata. Defaults to False.
            reload (bool, optional): Whether to reload the dataset. Defaults to False.

        Returns:
            pds.Dataset | tuple[pds.Dataset, dict[str, any]]: PyArrow Dataset or tuple of PyArrow Dataset and metadata.
        """
        if self.delta_table is None:
            self._init_dt()
            if self.delta_table is None:
                return None

        if reload or not hasattr(self, "_dataset"):
            self._dataset = self.delta_table.to_pyarrow_dataset()
        if metadata:
            metadata = get_pyarrow_dataset_metadata(
                self._dataset, self._base_path, "parquet"
            )
            return self._dataset, metadata
        return self._dataset

    def to_pyarrow_table(
        self, metadata: bool = False, reload: bool = False
    ) -> pa.Table | tuple[pa.Table, dict[str, any]]:
        """Converts the DeltaTable to a PyArrow Table.

        Args:
            metadata (bool, optional): Whether to include metadata. Defaults to False.
            reload (bool, optional): Whether to reload the table. Defaults to False.

        Returns:
            pa.Table | tuple[pa.Table, dict[str, any]]: PyArrow Table or tuple of PyArrow Table and metadata.
        """
        if self.delta_table is None:
            self._init_dt()
            if self.delta_table is None:
                return None

        if reload or not hasattr(self, "_data"):
            self._data = self.delta_table.to_pyarrow_table()
        if metadata:
            metadata = get_dataframe_metadata(table, self._base_path, "parquet")
            return self._data, metadata
        return self._data

    def compact(
        self,
        partition_filters: list[tuple[str, str, any]] | None = None,
        target_size: int = None,
        max_concurrent_tasks: int = None,
        min_commit_interval: int | datetime.timedelta | None = None,
        writer_properties: WriterProperties = None,
        custom_metadata: dict[str, str] | None = None,
        post_commithook_properties: PostCommitHookProperties | None = None,
        commit_properties: CommitProperties | None = None,
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
                lock_name=self._base_path,
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
        writer_properties: WriterProperties = None,
        custom_metadata: dict[str, str] | None = None,
        post_commithook_properties: PostCommitHookProperties | None = None,
        commit_properties: CommitProperties | None = None,
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
                lock_name=self._base_path,
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
            self._metadata = get_delta_metadata(self.delta_table, self._base_path)
        return self._metadata
        if not hasattr(self, "_metadata"):
            self._metadata = get_delta_metadata(self.delta_table, self._base_path)
        return self._metadata
