from ..base import BaseDatasetReader, BaseFileReader


class ParquetFileReader(BaseFileReader):
    """Parquet file loader.

    This class is responsible for loading dataframes from Parquet files.

    Examples:
        ```python
        loader = ParquetFileReader("data.parquet")
        df = loader.load()
        ```
    """

    format: str = "parquet"

    def model_post_init(self, __context):
        super().model_post_init(__context)


class ParquetDatasetReader(BaseDatasetReader):
    """Parquet dataset loader.

    This class is responsible for loading dataframes from Parquet dataset.

    Examples:
        ```python
        loader = ParquetDatasetReader("parquet_data/")
        df = loader.load()
        ```
    """

    format: str = "parquet"

    def model_post_init(self, __context):
        super().model_post_init(__context)
