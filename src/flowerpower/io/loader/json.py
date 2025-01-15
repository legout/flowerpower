from ..base import BaseFileLoader


class JsonFileLoader(BaseFileLoader):
    """
    JSON file loader.

    This class is responsible for loading dataframes from JSON files.

    Examples:
        ```python
        loader = JsonFileLoader("data.json")
        df = loader.load()
        ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "json"


class JsonDatasetLoader(BaseFileLoader):
    """
    JSON dataset loader.

    This class is responsible for loading dataframes from JSON dataset.

    Examples:
        ```python
        loader = JsonDatasetLoader("json_data/")
        df = loader.load()
        ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "json"
