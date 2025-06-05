import attrs

from ..base import BaseDatasetReader, BaseFileReader


@attrs.define
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

    format: str = attrs.field(default="csv", init=False)


@attrs.define
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

    format: str = attrs.field(default="csv", init=False)
