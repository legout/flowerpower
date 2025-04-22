import msgspec
from munch import munchify

from .. import BaseConfig


class TrackerConfig(BaseConfig):
    project_id: int | None = msgspec.field(default=None)
    dag_name: str | None = msgspec.field(default=None)
    tags: dict = msgspec.field(default_factory=dict)

    def __post_init__(self):
        self.tags = munchify(self.tags)

class MLFlowConfig(BaseConfig):
    experiment_name: str | None = msgspec.field(default=None)
    experiment_tags: dict | None = msgspec.field(default_factory=dict)
    experiment_description: str | None = msgspec.field(default=None)
    run_id: str | None = msgspec.field(default=None)
    run_name: str | None = msgspec.field(default=None)
    run_tags: dict | None = msgspec.field(default_factory=dict)
    run_description: str | None = msgspec.field(default=None)

    def __post_init__(self):
        if isinstance(self.experiment_tags, dict):
            self.experiment_tags = munchify(self.experiment_tags)
        if isinstance(self.run_tags, dict):
            self.run_tags = munchify(self.run_tags)



class AdapterConfig(BaseConfig):
    tracker: TrackerConfig = msgspec.field(default_factory=TrackerConfig)
    mlflow: MLFlowConfig = msgspec.field(default_factory=MLFlowConfig)

    def __post_init__(self):
        if self.tracker.project_id is not None:
            self.mlflow.experiment_name = f"flowerpower_project_{self.tracker.project_id}"
        if self.tracker.dag_name is not None:
            self.mlflow.run_name = self.tracker.dag_name
           
