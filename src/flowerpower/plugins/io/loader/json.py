import attrs

from ..base import BaseFileReader


@attrs.define
class JsonFileReader(BaseFileReader):
    """
    JSON file loader.

    This class is responsible for loading dataframes from JSON files.

    Examples:
        ```python
        loader = JsonFileReader("data.json")
        df = loader.load()
        ```
    """

    format: str = attrs.field(default="json", init=False)


@attrs.define
class JsonDatasetReader(BaseFileReader):
    """
    JSON dataset loader.

    This class is responsible for loading dataframes from JSON dataset.

    Examples:
        ```python
        loader = JsonDatasetReader("json_data/")
        df = loader.load()
        ```
    """

    format: str = attrs.field(default="json", init=False)
