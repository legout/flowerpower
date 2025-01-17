from ..base import BaseDatasetLoader, BaseFileLoader


class ParquetFileLoader(BaseFileLoader):
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "parquet"

    def load(self, **kwargs):
        return self.to_pyarrow_table(**kwargs)


class ParquetDatasetLoader(BaseDatasetLoader):
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "parquet"

    def load(self, **kwargs):
        return self.to_pyarrow_dataset(**kwargs)
