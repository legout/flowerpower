from ..base import BaseDatasetLoader, BaseFileLoader


class CSVFileLoader(BaseFileLoader):
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "csv"


class CSVDatasetLoader(BaseDatasetLoader):
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "csv"
