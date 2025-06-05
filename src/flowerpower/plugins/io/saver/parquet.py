import attrs

from ..base import BaseDatasetWriter, BaseFileWriter


@attrs.define
class ParquetFileWriter(BaseFileWriter):
    """Parquet file writer.

    This class is responsible for writing dataframes to Parquet files.

    Examples:
        ```python
        writer = ParquetFileWriter(df, "data.parquet")
        writer.write()
        ```
    """

    format: str = attrs.field(default="parquet", init=False)


@attrs.define
class ParquetDatasetWriter(BaseDatasetWriter):
    """Parquet dataset writer.

    This class is responsible for writing dataframes to Parquet dataset.

    Examples:
        ```python
        writer = ParquetDatasetWriter(df, "parquet_data/")
        writer.write()
        ```

    """

    format: str = attrs.field(default="parquet", init=False)
