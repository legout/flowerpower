import attrs

from ..base import BaseDatasetWriter


@attrs.define
class PydalaDatasetWriter(BaseDatasetWriter):
    """Writer for Pydala dataset.

    This class is responsible for writing dataframes to Pydala dataset.

    Examples:
        ```python
        writer = PydalaDatasetWriter(path="pydala_data/")
        writer.write(df)
        ```
    """

    format: str = attrs.field(default="parquet", init=False)
    is_pydala_dataset: bool = attrs.field(default=True, init=False)
