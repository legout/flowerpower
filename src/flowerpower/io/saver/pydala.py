from ..base import BaseDatasetWriter


class PydalaDatasetWriter(BaseDatasetWriter):
    """Writer for Pydala dataset.

    This class is responsible for writing dataframes to Pydala dataset.

    Examples:
        ```python
        writer = PydalaDatasetWriter(path="pydala_data/")
        writer.write(df)
        ```
    """

    format: str = "parquet"
    is_pydala_dataset: bool = True

    def model_post_init(self, __context):
        super().model_post_init(__context)
