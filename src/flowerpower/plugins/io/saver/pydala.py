from msgspec import field

from ..base import BaseDatasetWriter


# @attrs.define
class PydalaDatasetWriter(BaseDatasetWriter, gc=False):
    """Writer for Pydala dataset.

    This class is responsible for writing dataframes to Pydala dataset.

    Examples:
        ```python
        writer = PydalaDatasetWriter(path="pydala_data/")
        writer.write(df)
        ```
    """

    format: str = field(default="parquet")
    is_pydala_dataset: bool = field(default=True)
