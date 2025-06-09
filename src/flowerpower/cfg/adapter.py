import msgspec
from .. import settings
from .base import BaseConfig
from munch import munchify
from .project.adapter import (
    HamiltonTrackerConfig as ProjectHamiltonTrackerConfig,
    MLFlowConfig as ProjectMLFlowConfig,
    RayConfig,
    OpenTelemetryConfig,
)
from .pipeline.adapter import (
    HamiltonTracerConfig as PipelineHamiltonTracerConfig,
    MLFlowConfig as PipelineMLFlowConfig,
)


class HamiltonTrackerConfig(BaseConfig):
    username: str | None = msgspec.field(default=None)
    api_url: str = msgspec.field(default=settings.HAMILTON_API_URL)
    ui_url: str = msgspec.field(default=settings.HAMILTON_UI_URL)
    api_key: str | None = msgspec.field(default=None)
    verify: bool = msgspec.field(default=False)
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
    tracking_uri: str | None = msgspec.field(default=None)
    registry_uri: str | None = msgspec.field(default=None)
    artifact_location: str | None = msgspec.field(default=None)
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
    hamilton_tracker: HamiltonTrackerConfig = msgspec.field(
        default_factory=HamiltonTrackerConfig
    )
    mlflow: MLFlowConfig = msgspec.field(default_factory=MLFlowConfig)

    ray: RayConfig = msgspec.field(default_factory=RayConfig)
    opentelemetry: OpenTelemetryConfig = msgspec.field(
        default_factory=OpenTelemetryConfig
    )

    @classmethod
    def from_adapters(
        cls,
        project_hamilton_tracker_cfg: ProjectHamiltonTrackerConfig,
        pipeline_hamilton_tracker_cfg: PipelineHamiltonTracerConfig,
        project_mlflow_cfg: ProjectMLFlowConfig,
        pipeline_mlflow_cfg: PipelineMLFlowConfig,
        ray_cfg: RayConfig,
        opentelemetry_cfg: OpenTelemetryConfig,
    ) -> "AdapterConfig":
        return cls(
            hamilton_tracker=HamiltonTrackerConfig.from_dict(
                **{**project_hamilton_tracker_cfg, **pipeline_hamilton_tracker_cfg}
            ),
            mlflow=MLFlowConfig.from_dict(
                **{**project_mlflow_cfg, **pipeline_mlflow_cfg}
            ),
            ray=ray_cfg
            if isinstance(ray_cfg, RayConfig)
            else RayConfig.from_dict(ray_cfg),
            opentelemetry=opentelemetry_cfg
            if isinstance(opentelemetry_cfg, OpenTelemetryConfig)
            else OpenTelemetryConfig.from_dict(opentelemetry_cfg),
        )
