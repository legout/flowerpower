from ..base import BaseFileWriter


class JsonFileWriter(BaseFileWriter):
    """CSV file writer.

    This class is responsible for writing dataframes to CSV files.

    Examples:
        ```python
        writer = CSVFileWriter(df, "data.csv")
        writer.write()
        ```
    """

    format: str = "json"

    def model_post_init(self, __context):
        super().model_post_init(__context)


class JsonDatasetWriter(BaseFileWriter):
    """CSV dataset writer.

    This class is responsible for writing dataframes to CSV dataset.

    Examples:
        ```python
        writer = CSVDatasetWriter([df1, df2], "csv_data/")
        writer.write()
        ```

    """

    format: str = "json"

    def model_post_init(self, __context):
        super().model_post_init(__context)
