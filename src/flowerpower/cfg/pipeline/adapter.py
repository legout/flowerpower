import msgspec
from munch import munchify

from ... import settings
from ..base import BaseConfig


class HamiltonTracerConfig(BaseConfig):
    project_id: int | None = msgspec.field(default=None)
    dag_name: str | None = msgspec.field(default=None)
    tags: dict = msgspec.field(default_factory=dict)
    capture_data_statistics: bool = msgspec.field(
        default=settings.HAMILTON_CAPTURE_DATA_STATISTICS
    )
    max_list_length_capture: int = msgspec.field(
        default=settings.HAMILTON_MAX_LIST_LENGTH_CAPTURE
    )
    max_dict_length_capture: int = msgspec.field(
        default=settings.HAMILTON_MAX_DICT_LENGTH_CAPTURE
    )

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


# class OpenLineageConfig(BaseConfig):
#     namespace : str | None = msgspec.field(default=None)
#     job_name : str | None = msgspec.field(default=None)


class AdapterConfig(BaseConfig):
    hamilton_tracker: HamiltonTracerConfig = msgspec.field(
        default_factory=HamiltonTracerConfig
    )
    mlflow: MLFlowConfig = msgspec.field(default_factory=MLFlowConfig)
    # openlineage: OpenLineageConfig | dict = msgspec.field(default_factory=OpenLineageConfig)

    def __post_init__(self):
        if isinstance(self.hamilton_tracker, dict):
            self.hamilton_tracker = HamiltonTracerConfig.from_dict(
                self.hamilton_tracker
            )
        if isinstance(self.mlflow, dict):
            self.mlflow = MLFlowConfig.from_dict(self.mlflow)
        if self.hamilton_tracker.project_id is not None:
            self.mlflow.experiment_name = (
                f"flowerpower_project_{self.hamilton_tracker.project_id}"
            )
        if self.hamilton_tracker.dag_name is not None:
            self.mlflow.run_name = self.hamilton_tracker.dag_name
