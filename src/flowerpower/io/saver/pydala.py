from ..base import BaseDatasetWriter


class PydalaDatasetWriter(BaseDatasetWriter):
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "parquet"
        self.is_pydala_dataset = True
