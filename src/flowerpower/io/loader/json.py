from ..base import BaseDatasetLoader, BaseFileLoader


class ParquetFileLoader(BaseFileLoader):
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "json"


class ParquetDatasetLoader(BaseDatasetLoader):
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "json"
