from deltalake.writer import WriterProperties, write_deltalake
from deltalake.table import ColumnProperties, PostCommitHookProperties, CommitProperties
import pyarrow as pa
import polars as pl
import pandas as pd
from typing import Any
from ..utils.misc import _dict_to_dataframe


class DeltaTableWriter:
    """Delta table writer.

    This class is responsible for writing dataframes to Delta tables.

    Examples:
        ```python
        writer = DeltaTableWriter("data/")
        writer.write(df)
        ```
    """

    def __init__(
        self,
        path: str | list[str] | None = None,
        schema: pa.Schema | None = None,
        partition_by: list[str] | str | None = None,
        storage_options: dict[str, str] | None = None,
        description: str | None = None,
    ):
        self.path = path
        self.schema = schema
        self.partition_by = partition_by
        self.storage_options = storage_options
        self.description = description
        self.format = "delta"

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
        mode: str = "append",  # "overwrite" | "append" | "error | "ignore"
        schema_mode: str | None = None,  # "merge" | "overwrite"
        partition_filters: list[tuple[str, str, Any]] | None = None,
        predicate: str | None = None,
        target_file_size: int | None = None,
        large_dtypes: bool = False,
        custom_metadata: dict[str, Any] | None = None,
        post_commithook_properties: PostCommitHookProperties | None = None,
        commit_properties: CommitProperties | None = None,
        # writerproperties
        data_page_size_limit: int | None = None,
        dictionary_page_size_limit: int | None = None,
        data_page_row_count_limit: int | None = None,
        write_batch_size: int | None = None,
        max_row_group_size: int | None = None,
        compression: str | None = "ZSTD",
        compression_level: int | None = None,
        statistics_truncate_length: int | None = None,
        default_column_properties: ColumnProperties | None = None,
        column_properties: dict[str, ColumnProperties] | None = None,
    ):
        if isinstance(data, dict):
            data = _dict_to_dataframe(data)
        if not isinstance(data, list):
            data = [data]
        if isinstance(data[0], dict):
            data = [_dict_to_dataframe(d) for d in data]
        if isinstance(data[0], pa.LazyFrame):
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

        writer_properties = WriterProperties(
            data_page_size_limit=data_page_size_limit,
            dictionary_page_size_limit=dictionary_page_size_limit,
            data_page_row_count_limit=data_page_row_count_limit,
            write_batch_size=write_batch_size,
            max_row_group_size=max_row_group_size,
            compression=compression,
            compression_level=compression_level,
            statistics_truncate_length=statistics_truncate_length,
            default_column_properties=default_column_properties,
            column_properties=column_properties,
        )
        write_deltalake(
            self.path,
            data,
            mode=mode,
            schema=self.schema,
            partition_by=self.partition_by,
            storage_options=self.storage_options,
            description=self.description,
            schema_mode=schema_mode,
            partition_filters=partition_filters,
            predicate=predicate,
            target_file_size=target_file_size,
            large_dtypes=large_dtypes,
            custom_metadata=custom_metadata,
            post_commithook_properties=post_commithook_properties,
            commit_properties=commit_properties,
            writer_properties=writer_properties,
        )