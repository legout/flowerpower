import attrs

from ..base import BaseDatasetReader, BaseFileReader


@attrs.define
class ParquetFileReader(BaseFileReader):
    """Parquet file loader.

    This class is responsible for loading dataframes from Parquet files.

    Examples:
        ```python
        loader = ParquetFileReader("data.parquet")
        df = loader.load()
        ```
    """

    format: str = attrs.field(default="parquet", init=False)


@attrs.define
class ParquetDatasetReader(BaseDatasetReader):
    """Parquet dataset loader.

    This class is responsible for loading dataframes from Parquet dataset.

    Examples:
        ```python
        loader = ParquetDatasetReader("parquet_data/")
        df = loader.load()
        ```
    """

    format: str = attrs.field(default="parquet", init=False)
