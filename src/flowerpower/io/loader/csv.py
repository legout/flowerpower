from ..base import BaseDatasetReader, BaseFileReader


class CSVFileReader(BaseFileReader):
    """CSV file loader.

    This class is responsible for loading CSV files into several dataframe formats,
    duckdb and datafusion.

    Examples:
        ```python
        loader = CSVFileReader("data.csv")
        df = loader.to_pandas()
    ```
    """

    format: str = "csv"

    def model_post_init(self, __context):
        super().model_post_init(__context)


class CSVDatasetReader(BaseDatasetReader):
    """CSV dataset loader.

    This class is responsible for loading CSV files into several dataframe formats,
    duckdb and datafusion.

    Examples:
        ```python
        loader = CSVDatasetReader("csv_data/")
        df = loader.to_pandas()
        ```
    """

    format: str = "csv"

    def model_post_init(self, __context):
        super().model_post_init(__context)
