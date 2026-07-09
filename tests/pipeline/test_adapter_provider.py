from unittest.mock import MagicMock, patch

from flowerpower.cfg.pipeline import PipelineConfig
from flowerpower.cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from flowerpower.cfg.pipeline.run import RunConfig, WithAdapterConfig
from flowerpower.cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from flowerpower.pipeline.adapter_provider import AdapterProvider, ResolvedAdapterSet


def test_adapter_provider_resolves_project_pipeline_and_run_precedence():
    provider = AdapterProvider()
    pipeline_config = PipelineConfig(
        name="pipe",
        adapter=PipelineAdapterConfig.from_dict(
            {"hamilton_tracker": {"project_id": 100, "tags": {"source": "pipeline"}}}
        ),
        run=RunConfig(),
    )
    project_adapter = ProjectAdapterConfig.from_dict(
        {"hamilton_tracker": {"api_key": "project-key", "username": "project-user"}}
    )
    run_config = RunConfig(
        with_adapter=WithAdapterConfig(hamilton_tracker=False),
        pipeline_adapter_cfg=PipelineAdapterConfig.from_dict(
            {"hamilton_tracker": {"tags": {"source": "run"}}}
        ),
        project_adapter_cfg=ProjectAdapterConfig.from_dict(
            {"hamilton_tracker": {"username": "run-user"}}
        ),
    )

    adapter_set = provider.resolve(run_config, pipeline_config, project_adapter)

    assert isinstance(adapter_set, ResolvedAdapterSet)
    assert adapter_set.with_adapter_cfg.hamilton_tracker is False
    assert adapter_set.pipeline_adapter_cfg.hamilton_tracker.project_id == 100
    assert adapter_set.pipeline_adapter_cfg.hamilton_tracker.tags == {"source": "run"}
    assert adapter_set.project_adapter_cfg.hamilton_tracker.api_key == "project-key"
    assert adapter_set.project_adapter_cfg.hamilton_tracker.username == "run-user"
    assert run_config.pipeline_adapter_cfg is adapter_set.pipeline_adapter_cfg
    assert run_config.project_adapter_cfg is adapter_set.project_adapter_cfg


def test_adapter_provider_respects_explicit_none_adapter_overrides():
    provider = AdapterProvider()
    pipeline_config = PipelineConfig(
        name="pipe",
        adapter=PipelineAdapterConfig.from_dict({"hamilton_tracker": {"project_id": 100}}),
        run=RunConfig(),
    )
    project_adapter = ProjectAdapterConfig.from_dict(
        {"hamilton_tracker": {"api_key": "project-key", "username": "project-user"}}
    )
    run_config = RunConfig(
        pipeline_adapter_cfg=None,
        project_adapter_cfg=None,
        explicit_overrides={"pipeline_adapter_cfg", "project_adapter_cfg"},
    )

    adapter_set = provider.resolve(run_config, pipeline_config, project_adapter)

    assert adapter_set.pipeline_adapter_cfg.hamilton_tracker.project_id is None
    assert adapter_set.project_adapter_cfg.hamilton_tracker.api_key is None
    assert adapter_set.project_adapter_cfg.hamilton_tracker.username is None


def test_adapter_provider_constructs_builtin_adapters_without_live_services():
    tracker_adapter = MagicMock(name="HamiltonTracker")
    mlflow_adapter = MagicMock(name="MLFlowTracker")
    provider = AdapterProvider()
    run_config = RunConfig(with_adapter=WithAdapterConfig(hamilton_tracker=True, mlflow=True))

    with patch(
        "flowerpower.utils.adapter.AdapterManager._create_hamilton_tracker",
        return_value=tracker_adapter,
    ) as mock_tracker, patch(
        "flowerpower.utils.adapter.AdapterManager._create_mlflow_adapter",
        return_value=mlflow_adapter,
    ) as mock_mlflow:
        adapter_set = provider.resolve(
            run_config,
            PipelineConfig(name="pipe", run=RunConfig()),
            ProjectAdapterConfig(),
        )

    assert adapter_set.runtime_adapters == [tracker_adapter, mlflow_adapter]
    mock_tracker.assert_called_once()
    mock_mlflow.assert_called_once()


def test_adapter_provider_preserves_custom_adapter_passthrough():
    custom_adapter = MagicMock(name="custom_adapter")
    provider = AdapterProvider()
    run_config = RunConfig(
        with_adapter=WithAdapterConfig(hamilton_tracker=False, mlflow=False),
        adapter={"custom": custom_adapter},
    )

    adapter_set = provider.resolve(
        run_config,
        PipelineConfig(name="pipe", run=RunConfig()),
        ProjectAdapterConfig(),
    )

    assert adapter_set.runtime_adapters == [custom_adapter]


def test_adapter_provider_carries_ray_shutdown_policy_in_project_config():
    provider = AdapterProvider()
    run_config = RunConfig()
    project_adapter = ProjectAdapterConfig.from_dict(
        {"ray": {"shutdown_ray_on_completion": True}}
    )

    adapter_set = provider.resolve(
        run_config,
        PipelineConfig(name="pipe", run=RunConfig()),
        project_adapter,
    )

    assert adapter_set.project_adapter_cfg.ray.shutdown_ray_on_completion is True
