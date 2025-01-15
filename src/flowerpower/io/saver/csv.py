from ..base import BaseDatasetWriter, BaseFileWriter


class CSVFileWriter(BaseFileWriter):
    """CSV file writer.

    This class is responsible for writing dataframes to CSV files.

    Examples:
        ```python
        writer = CSVFileWriter(df, "data.csv")
        writer.write()
        ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "csv"


class CSVDatasetWriter(BaseDatasetWriter):
    """CSV dataset writer.

    This class is responsible for writing dataframes to CSV dataset.

    Examples:
        ```python
        writer = CSVDatasetWriter(df, "csv_data/")
        writer.write()
        ```

    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "csv"
