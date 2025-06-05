import attrs

from ..base import BaseDatasetReader


@attrs.define
class PydalaDatasetReader(BaseDatasetReader):
    """Pydala dataset loader.

    This class is responsible for loading dataframes from Pydala dataset.

    Examples:
        ```python
        loader = PydalaDatasetReader("pydala_data/")
        df = loader.load()
        ```
    """

    format: str = attrs.field(default="parquet", init=False)
