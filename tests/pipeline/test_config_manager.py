from unittest.mock import MagicMock, patch

from flowerpower.pipeline.config_manager import PipelineConfigManager


@patch("flowerpower.pipeline.config_manager.ProjectConfig.load")
@patch("flowerpower.pipeline.config_manager.add_modules_path")
def test_load_project_config_uses_configured_pipelines_dir(
    mock_add_modules_path: MagicMock,
    mock_project_load: MagicMock,
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
    mock_add_modules_path.assert_called_once_with(fs, "flows", "/project")


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
