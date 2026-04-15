from unittest.mock import MagicMock, patch

from flowerpower.pipeline.config_manager import PipelineConfigManager


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

    manager.load_project_config(reload=True)

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

    manager.load_pipeline_config("demo", reload=True)

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

    manager.load_pipeline_config("  demo  ", reload=True)

    mock_pipeline_load.assert_called_once_with(
        base_dir="/project",
        name="demo",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )


@patch("flowerpower.pipeline.config_manager.ProjectConfig.load")
def test_load_project_config_reloads_when_requested_name_changes(
    mock_project_load: MagicMock,
) -> None:
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

    mock_project_load.assert_called_once_with(
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

    mock_project_load.assert_called_once_with(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
    )
