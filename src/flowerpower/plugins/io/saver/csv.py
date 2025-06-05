import attrs

from ..base import BaseDatasetWriter, BaseFileWriter


@attrs.define
class CSVFileWriter(BaseFileWriter):
    """CSV file writer.

    This class is responsible for writing dataframes to CSV files.

    Examples:
        ```python
        writer = CSVFileWriter(df, "data.csv")
        writer.write()
        ```
    """

    format: str = attrs.field(default="csv", init=False)


@attrs.define
class CSVDatasetWriter(BaseDatasetWriter):
    """CSV dataset writer.

    This class is responsible for writing dataframes to CSV dataset.

    Examples:
        ```python
        writer = CSVDatasetWriter(df, "csv_data/")
        writer.write()
        ```

    """

    format: str = attrs.field(default="csv", init=False)
