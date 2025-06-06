from msgspec import field

from ..base import BaseDatasetWriter, BaseFileWriter


# @attrs.define
class ParquetFileWriter(BaseFileWriter, gc=False):
    """Parquet file writer.

    This class is responsible for writing dataframes to Parquet files.

    Examples:
        ```python
        writer = ParquetFileWriter(df, "data.parquet")
        writer.write()
        ```
    """

    format: str = field(default="parquet")


# @attrs.define
class ParquetDatasetWriter(BaseDatasetWriter, gc=False):
    """Parquet dataset writer.

    This class is responsible for writing dataframes to Parquet dataset.

    Examples:
        ```python
        writer = ParquetDatasetWriter(df, "parquet_data/")
        writer.write()
        ```

    """

    format: str = field(default="parquet")
