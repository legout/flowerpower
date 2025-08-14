from typing import Any

import pandas as pd
import polars as pl
import pyarrow as pa
from deltalake.transaction import CommitProperties, PostCommitHookProperties
from deltalake.writer import (ColumnProperties, WriterProperties,
                              write_deltalake)
from msgspec import field
from redis import Redis, StrictRedis
from sherlock import RedisLock

from ....utils.misc import _dict_to_dataframe
from ..base import BaseDatasetWriter
from ..metadata import get_dataframe_metadata


# @attrs.define
class DeltaTableWriter(BaseDatasetWriter, gc=False):
    """Delta table writer.

    This class is responsible for writing dataframes to Delta tables.

    Examples:
        ```python
        writer = DeltaTableWriter("data/")
        writer.write(df)
        ```
    """

    description: str | None = None
    with_lock: bool = False
    redis: StrictRedis | Redis | None = None
    format: str = field(default="delta")

    def __post_init__(self):
        super().__post_init__()
        if self.with_lock and self.redis is None:
            raise ValueError("Redis connection is required when using locks.")

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
        )
        | None = None,
        mode: str = "append",  # "overwrite" | "append" | "error | "ignore"
        # schema: pa.Schema | None = None,
        schema_mode: str | None = None,  # "merge" | "overwrite"
        partition_by: list[str] | None = None,
        # partition_filters: list[tuple[str, str, Any]] | None = None,
        predicate: str | None = None,
        target_file_size: int | None = None,
        # large_dtypes: bool = False,
        # custom_metadata: dict[str, Any] | None = None,
        post_commithook_properties: PostCommitHookProperties | None = None,
        commit_properties: CommitProperties | None = None,
        # writerproperties
        data_page_size_limit: int | None = None,
        dictionary_page_size_limit: int | None = None,
        data_page_row_count_limit: int | None = None,
        write_batch_size: int | None = None,
        max_row_group_size: int | None = None,
        compression: str | None = None,
        compression_level: int | None = None,
        statistics_truncate_length: int | None = None,
        default_column_properties: ColumnProperties | None = None,
        column_properties: dict[str, ColumnProperties] | None = None,
    ) -> dict[str, Any]:
        """
        Write data to a Delta table.

        Args:
            data: Data to write
            mode: Write mode
            schema: Schema of the data
            schema_mode: Schema mode
            partition_by: Columns to partition by
            partition_filters: Filters to apply to the partitions
            predicate: Predicate to apply to the data
            target_file_size: Target file size
            large_dtypes: Whether to use large dtypes
            custom_metadata: Custom metadata
            post_commithook_properties: Post-commit hook properties
            commit_properties: Commit properties
            data_page_size_limit: Data page size limit
            dictionary_page_size_limit: Dictionary page size limit
            data_page_row_count_limit: Data page row count limit
            write_batch_size: Write batch size
            max_row_group_size: Maximum row group size
            compression: Compression method
            compression_level: Compression level
            statistics_truncate_length: Statistics truncate length
            default_column_properties: Default column properties
            column_properties: Column properties

        Returns:
            Metadata
        """
        if data is None:
            data = self.data
        if isinstance(data, dict):
            data = _dict_to_dataframe(data)
        if not isinstance(data, list):
            data = [data]
        if isinstance(data[0], dict):
            data = [_dict_to_dataframe(d) for d in data]
        if isinstance(data[0], pl.LazyFrame):
            data = [d.collect() for d in data]
        if isinstance(data[0], pl.DataFrame):
            data = pl.concat(data, how="diagonal_relaxed").to_arrow()
        if isinstance(data[0], pd.DataFrame):
            data = pa.concat_tables(
                [pa.Table.from_pandas(d, preserve_index=False) for d in data],
                promote_options="permissive",
            )
        if isinstance(data[0], pa.RecordBatch | pa.RecordBatchReader):
            data = pa.Table.from_batches(data)
        if isinstance(data[0], pa.Table):
            data = pa.concat_tables(data, promote_options="permissive")

        metadata = get_dataframe_metadata(
            data, path=self._base_path, format=self.format
        )

        writer_properties = WriterProperties(
            data_page_size_limit=data_page_size_limit,
            dictionary_page_size_limit=dictionary_page_size_limit,
            data_page_row_count_limit=data_page_row_count_limit,
            write_batch_size=write_batch_size,
            max_row_group_size=max_row_group_size or self.row_group_size,
            compression=compression or self.compression.upper(),
            compression_level=compression_level,
            statistics_truncate_length=statistics_truncate_length,
            default_column_properties=default_column_properties,
            column_properties=column_properties,
        )

        def _write():
            write_deltalake(
                self._base_path,
                data,
                mode=mode,
                # schema=schema or self.schema_,
                partition_by=partition_by or self.partition_by,
                storage_options=self.storage_options.to_object_store_kwargs(),
                description=self.description,
                schema_mode=schema_mode,
                # partition_filters=partition_filters,
                predicate=predicate,
                target_file_size=target_file_size,
                # large_dtypes=large_dtypes,
                # custom_metadata=custom_metadata,
                post_commithook_properties=post_commithook_properties,
                commit_properties=commit_properties,
                writer_properties=writer_properties,
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
                _write()
        else:
            _write()
        return metadata
