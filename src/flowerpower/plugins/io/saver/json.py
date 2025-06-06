from msgspec import field

from ..base import BaseFileWriter


# @attrs.define
class JsonFileWriter(BaseFileWriter, gc=False):
    """JSON file writer.

    This class is responsible for writing dataframes to JSON files.

    Examples:
        ```python
        writer = JsonFileWriter(df, "data.json")
        writer.write()
        ```
    """

    format: str = field(default="json")


# @attrs.define
class JsonDatasetWriter(BaseFileWriter, gc=False):
    """JSON dataset writer.

    This class is responsible for writing dataframes to JSON dataset.

    Examples:
        ```python
        writer = JsonDatasetWriter([df1, df2], "json_data/")
        writer.write()
        ```

    """

    format: str = field(default="json")
