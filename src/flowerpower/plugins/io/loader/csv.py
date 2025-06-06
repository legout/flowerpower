from msgspec import field

from ..base import BaseDatasetReader, BaseFileReader


# @attrs.define
class CSVFileReader(BaseFileReader, gc=False):
    """CSV file loader.

    This class is responsible for loading CSV files into several dataframe formats,
    duckdb and datafusion.

    Examples:
        ```python
        loader = CSVFileReader("data.csv")
        df = loader.to_pandas()
    ```
    """

    format: str = field(default="csv")


# @attrs.define
class CSVDatasetReader(BaseDatasetReader, gc=False):
    """CSV dataset loader.

    This class is responsible for loading CSV files into several dataframe formats,
    duckdb and datafusion.

    Examples:
        ```python
        loader = CSVDatasetReader("csv_data/")
        df = loader.to_pandas()
        ```
    """

    format: str = field(default="csv")
