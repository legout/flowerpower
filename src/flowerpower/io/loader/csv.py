from ..base import BaseDatasetLoader, BaseFileLoader


class CSVFileLoader(BaseFileLoader):
    """CSV file loader.

    This class is responsible for loading CSV files into several dataframe formats,
    duckdb and datafusion.

    Examples:
        ```python
        loader = CSVFileLoader("data.csv")
        df = loader.to_pandas()
    ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "csv"


class CSVDatasetLoader(BaseDatasetLoader):
    """CSV dataset loader.

    This class is responsible for loading CSV files into several dataframe formats,
    duckdb and datafusion.

    Examples:
        ```python
        loader = CSVDatasetLoader("csv_data/")
        df = loader.to_pandas()
        ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "csv"
