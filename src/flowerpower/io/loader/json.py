from ..base import BaseFileReader


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

    format: str = "json"

    def model_post_init(self, __context):
        super().model_post_init(__context)


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

    format: str = "json"

    def model_post_init(self, __context):
        super().model_post_init(__context)
