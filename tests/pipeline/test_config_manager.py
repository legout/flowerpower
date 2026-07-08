from unittest.mock import MagicMock, patch

from fsspeckit import filesystem

from flowerpower.cfg import Config, PipelineConfig
from flowerpower.pipeline.config_manager import PipelineConfigManager
from flowerpower.pipeline.registry import PipelineRegistry


@patch("flowerpower.pipeline.config_manager.apply_env_overlays")
@patch("flowerpower.pipeline.config_manager.ProjectConfig.load")
def test_load_project_config_uses_configured_dirs(
    mock_project_load: MagicMock,
    mock_apply_overlays: MagicMock,
) -> None:
    fs = MagicMock()
    mock_project_load.return_value = MagicMock()

    manager = PipelineConfigManager(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="conf",
        pipelines_dir="flows",
    )

    manager.load_project_config()

    mock_project_load.assert_called_once_with(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="conf",
    )
    mock_apply_overlays.assert_called_once()


@patch("flowerpower.pipeline.config_manager.ProjectConfig.load")
@patch("flowerpower.pipeline.config_manager.PipelineConfig.load")
def test_load_pipeline_config_uses_configured_dirs(
    mock_pipeline_load: MagicMock,
    mock_project_load: MagicMock,
) -> None:
    fs = MagicMock()
    mock_project_load.return_value = MagicMock()
    mock_pipeline_load.return_value = MagicMock()

    manager = PipelineConfigManager(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )

    manager.load_pipeline_config("demo")

    mock_pipeline_load.assert_called_once_with(
        base_dir="/project",
        name="demo",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )


@patch("flowerpower.pipeline.config_manager.ProjectConfig.load")
@patch("flowerpower.pipeline.config_manager.PipelineConfig.load")
def test_load_pipeline_config_strips_surrounding_whitespace(
    mock_pipeline_load: MagicMock,
    mock_project_load: MagicMock,
) -> None:
    fs = MagicMock()
    mock_project_load.return_value = MagicMock()
    mock_pipeline_load.return_value = MagicMock()

    manager = PipelineConfigManager(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )

    manager.load_pipeline_config("  demo  ")

    mock_pipeline_load.assert_called_once_with(
        base_dir="/project",
        name="demo",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )


@patch("flowerpower.pipeline.config_manager.ProjectConfig.load")
def test_load_project_config_is_stateless_and_passes_name_through(
    mock_project_load: MagicMock,
) -> None:
    """Stateless loader reads from disk on every call, passing the fallback
    name through when no project config file exists."""
    fs = MagicMock()
    fs.exists.return_value = False
    mock_project_load.side_effect = [MagicMock(name="first"), MagicMock(name="second")]

    manager = PipelineConfigManager(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )

    manager.load_project_config(name="first")
    manager.load_project_config(name="second")

    assert mock_project_load.call_count == 2
    assert mock_project_load.call_args_list[0].kwargs["name"] == "first"
    assert mock_project_load.call_args_list[1].kwargs["name"] == "second"


@patch("flowerpower.pipeline.config_manager.ProjectConfig.load")
def test_load_project_config_ignores_fallback_name_when_project_file_exists(
    mock_project_load: MagicMock,
) -> None:
    fs = MagicMock()
    fs.exists.return_value = True
    mock_project_load.return_value = MagicMock()

    manager = PipelineConfigManager(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )

    manager.load_project_config(name="first")
    manager.load_project_config(name="second")

    assert mock_project_load.call_count == 2
    mock_project_load.assert_called_with(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
    )


@patch("flowerpower.pipeline.config_manager.ProjectConfig.load")
def test_load_project_config_treats_project_yaml_as_existing_config(
    mock_project_load: MagicMock,
) -> None:
    fs = MagicMock()
    fs.exists.side_effect = lambda path: path == "settings/project.yaml"
    mock_project_load.return_value = MagicMock()

    manager = PipelineConfigManager(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )

    manager.load_project_config(name="first")
    manager.load_project_config(name="second")

    assert mock_project_load.call_count == 2
    mock_project_load.assert_called_with(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
    )


def test_config_loading_produces_identical_results_across_entry_points(
    monkeypatch, temp_project_dir
):
    """All entry points (Config.load, PipelineConfigManager, PipelineRegistry)
    apply env overlays consistently and yield identical PipelineConfig results.
    Direct PipelineConfig.load() returns the base config without overlays.
    """
    # Create project config
    project_path = temp_project_dir / "conf" / "project.yml"
    project_path.parent.mkdir(parents=True)
    project_path.write_text("name: test-project\n")

    # Create pipeline config
    pipeline_path = temp_project_dir / "conf" / "pipelines" / "test_pipeline.yml"
    pipeline_path.parent.mkdir(parents=True)
    pipeline_path.write_text("run:\n  log_level: INFO\n")

    # Set env overlay
    monkeypatch.setenv("FP_PIPELINE__RUN__LOG_LEVEL", "DEBUG")

    # Use a consistent dirfs filesystem rooted at the temp directory
    fs = filesystem(str(temp_project_dir), cached=False, dirfs=True)

    # Entry point 1: Config.load()
    cfg = Config.load(
        base_dir=str(temp_project_dir),
        pipeline_name="test-pipeline",
        fs=fs,
    )
    result_config_load = cfg.pipeline.to_dict()

    # Entry point 2: PipelineConfigManager
    manager = PipelineConfigManager(
        base_dir=str(temp_project_dir),
        fs=fs,
        storage_options={},
    )
    result_manager = manager.load_pipeline_config("test-pipeline").to_dict()

    # Entry point 3: PipelineRegistry
    registry = PipelineRegistry.from_filesystem(
        base_dir=str(temp_project_dir),
        fs=fs,
    )
    result_registry = registry.load_config("test-pipeline").to_dict()

    # All three entry points should produce identical results
    assert result_config_load == result_manager == result_registry
    assert result_config_load["run"]["log_level"] == "DEBUG"

    # Direct PipelineConfig.load() should NOT have env overlay applied
    direct = PipelineConfig.load(
        base_dir=str(temp_project_dir), name="test-pipeline", fs=fs
    )
    result_direct = direct.to_dict()
    assert result_direct["run"]["log_level"] == "INFO"
