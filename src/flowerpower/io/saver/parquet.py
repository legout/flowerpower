from ..base import BaseDatasetWriter, BaseFileWriter


class ParquetFileWriter(BaseFileWriter):
    """CSV file writer.

    This class is responsible for writing dataframes to CSV files.

    Examples:
        ```python
        writer = CSVFileWriter(df, "data.csv")
        writer.write()
        ```
    """

    format: str = "parquet"

    def model_post_init(self, __context):
        super().model_post_init(__context)


class ParquetDatasetWriter(BaseDatasetWriter):
    """CSV dataset writer.

    This class is responsible for writing dataframes to CSV dataset.

    Examples:
        ```python
        writer = CSVDatasetWriter(df, "csv_data/")
        writer.write()
        ```

    """

    format: str = "parquet"

    def model_post_init(self, __context):
        super().model_post_init(__context)
