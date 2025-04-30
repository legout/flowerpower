from ..base import BaseDatasetReader


class PydalaDatasetReader(BaseDatasetReader):
    """Pydala dataset loader.

    This class is responsible for loading dataframes from Pydala dataset.

    Examples:
        ```python
        loader = PydalaDatasetReader("pydala_data/")
        df = loader.load()
        ```
    """

    format: str = "parquet"

    def model_post_init(self, __context):
        super().model_post_init(__context)
