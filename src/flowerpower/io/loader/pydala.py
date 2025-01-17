from ..base import BaseDatasetLoader


class PydalaDatasetLoader(BaseDatasetLoader):
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.format = "parquet"

    def load(self, **kwargs):
        return self.to_pydala_dataset(**kwargs)
