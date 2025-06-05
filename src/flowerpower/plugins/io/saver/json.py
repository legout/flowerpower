import attrs

from ..base import BaseFileWriter


@attrs.define
class JsonFileWriter(BaseFileWriter):
    """JSON file writer.

    This class is responsible for writing dataframes to JSON files.

    Examples:
        ```python
        writer = JsonFileWriter(df, "data.json")
        writer.write()
        ```
    """

    format: str = attrs.field(default="json", init=False)


@attrs.define
class JsonDatasetWriter(BaseFileWriter):
    """JSON dataset writer.

    This class is responsible for writing dataframes to JSON dataset.

    Examples:
        ```python
        writer = JsonDatasetWriter([df1, df2], "json_data/")
        writer.write()
        ```

    """

    format: str = attrs.field(default="json", init=False)
