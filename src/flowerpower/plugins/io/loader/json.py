from msgspec import field

from ..base import BaseFileReader


# @attrs.define
class JsonFileReader(BaseFileReader, gc=False):
    """
    JSON file loader.

    This class is responsible for loading dataframes from JSON files.

    Examples:
        ```python
        loader = JsonFileReader("data.json")
        df = loader.load()
        ```
    """

    format: str = field(default="json")


# @attrs.define
class JsonDatasetReader(BaseFileReader, gc=False):
    """
    JSON dataset loader.

    This class is responsible for loading dataframes from JSON dataset.

    Examples:
        ```python
        loader = JsonDatasetReader("json_data/")
        df = loader.load()
        ```
    """

    format: str = field(default="json")
