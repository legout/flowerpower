from unittest.mock import MagicMock, patch

from flowerpower.cfg import Config
from flowerpower.cfg.pipeline import PipelineConfig
from flowerpower.cfg.project import ProjectConfig
from flowerpower.flowerpower import FlowerPowerProject
from flowerpower.pipeline.config_manager import PipelineConfigManager
from flowerpower.pipeline.manager import PipelineManager
from flowerpower.pipeline.registry import PipelineRegistry
from flowerpower.pipeline.visualizer import PipelineVisualizer


def test_project_config_load_uses_config_dir_constant() -> None:
    fs = MagicMock()
    fs.exists.side_effect = lambda path: path == "settings/project.yml"

    with patch("flowerpower.cfg.project.CONFIG_DIR", "settings"):
        with patch.object(ProjectConfig, "from_yaml", return_value=ProjectConfig(name="demo")) as mock_from_yaml:
            ProjectConfig.load(fs=fs)

    mock_from_yaml.assert_called_once_with(path="settings/project.yml", fs=fs)


def test_project_config_default_hooks_dir_resolves_at_runtime() -> None:
    with patch("flowerpower.cfg.project.HOOKS_DIR", "dynamic_hooks"):
        cfg = ProjectConfig(name="demo")

    assert cfg.hooks_dir == "dynamic_hooks"


def test_project_config_allows_empty_config_dir_override() -> None:
    fs = MagicMock()
    fs.exists.side_effect = lambda path: path == "project.yml"

    with patch.object(ProjectConfig, "from_yaml", return_value=ProjectConfig(name="demo")) as mock_from_yaml:
        ProjectConfig.load(fs=fs, cfg_dir="")

    mock_from_yaml.assert_called_once_with(path="project.yml", fs=fs)


def test_pipeline_config_paths_use_config_and_pipelines_constants() -> None:
    fs = MagicMock()
    fs.exists.side_effect = lambda path: path == "settings/flows/my_pipeline.yml"

    with patch("flowerpower.cfg.pipeline.CONFIG_DIR", "settings"):
        with patch("flowerpower.cfg.pipeline.PIPELINES_DIR", "flows"):
            with patch.object(PipelineConfig, "from_yaml", return_value=PipelineConfig(name="my-pipeline")) as mock_from_yaml:
                PipelineConfig.load(name="my-pipeline", fs=fs)

            with patch.object(PipelineConfig, "to_yaml") as mock_to_yaml:
                cfg = PipelineConfig(name="my-pipeline")
                cfg.save(fs=fs)

    mock_from_yaml.assert_called_once_with(
        name="my-pipeline",
        path="settings/flows/my_pipeline.yml",
        fs=fs,
    )
    fs.makedirs.assert_called_with("settings/flows", exist_ok=True)
    mock_to_yaml.assert_called_once_with(path="settings/flows/my_pipeline.yml", fs=fs)


def test_pipeline_config_allows_empty_directory_overrides() -> None:
    fs = MagicMock()
    fs.exists.side_effect = lambda path: path == "flows/my_pipeline.yml"

    with patch.object(PipelineConfig, "from_yaml", return_value=PipelineConfig(name="my-pipeline")) as mock_from_yaml:
        PipelineConfig.load(name="my-pipeline", fs=fs, cfg_dir="", pipelines_dir="flows")

    mock_from_yaml.assert_called_once_with(
        name="my-pipeline",
        path="flows/my_pipeline.yml",
        fs=fs,
    )


def test_combined_config_save_uses_config_dir_constants() -> None:
    fs = MagicMock()
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        fs=fs,
    )

    with patch("flowerpower.cfg.CONFIG_DIR", "settings"):
        with patch("flowerpower.cfg.PIPELINES_DIR", "flows"):
            with patch.object(PipelineConfig, "to_yaml") as mock_pipeline_to_yaml:
                with patch.object(ProjectConfig, "to_yaml") as mock_project_to_yaml:
                    cfg.save(project=True, pipeline=True, fs=fs)

    mock_pipeline_to_yaml.assert_called_once_with(path="settings/flows/my_pipeline.yml", fs=fs)
    mock_project_to_yaml.assert_called_once_with("settings/project.yml", fs)
    fs.makedirs.assert_any_call("settings/flows", exist_ok=True)


def test_combined_config_save_creates_nested_config_pipeline_directory() -> None:
    fs = MagicMock()
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        fs=fs,
    )

    with patch.object(PipelineConfig, "to_yaml"):
        cfg.save(project=False, pipeline=True, fs=fs)

    fs.makedirs.assert_any_call("conf/pipelines", exist_ok=True)


def test_combined_config_save_formats_dotted_pipeline_paths() -> None:
    fs = MagicMock()
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="group.my-pipeline"),
        fs=fs,
    )

    with patch.object(PipelineConfig, "to_yaml") as mock_pipeline_to_yaml:
        cfg.save(project=False, pipeline=True, fs=fs)

    mock_pipeline_to_yaml.assert_called_once_with(
        path="conf/pipelines/group/my_pipeline.yml",
        fs=fs,
    )
    fs.makedirs.assert_any_call("conf/pipelines/group", exist_ok=True)


def test_combined_config_save_requires_pipeline_name() -> None:
    fs = MagicMock()
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name=None),
        fs=fs,
    )

    with patch.object(PipelineConfig, "to_yaml") as mock_pipeline_to_yaml:
        try:
            cfg.save(project=False, pipeline=True, fs=fs)
        except ValueError as exc:
            assert "Pipeline name is not set" in str(exc)
        else:
            raise AssertionError("Expected ValueError when pipeline name is missing")

    mock_pipeline_to_yaml.assert_not_called()


def test_combined_config_save_rejects_invalid_pipeline_name() -> None:
    fs = MagicMock()
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="valid-name"),
        fs=fs,
    )
    cfg.pipeline.name = "bad name"

    with patch.object(PipelineConfig, "to_yaml") as mock_pipeline_to_yaml:
        try:
            cfg.save(project=False, pipeline=True, fs=fs)
        except Exception as exc:
            assert "Invalid pipeline name" in str(exc)
        else:
            raise AssertionError("Expected invalid pipeline name to be rejected")

    mock_pipeline_to_yaml.assert_not_called()


def test_combined_config_save_defaults_base_dir_when_missing() -> None:
    cfg = Config(
        base_dir=None,
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        fs=None,
    )

    fake_fs = MagicMock()
    fake_fs.exists.return_value = True

    with patch.object(Config, "_get_cached_filesystem", return_value=fake_fs) as mock_get_fs:
        with patch.object(PipelineConfig, "to_yaml"):
            cfg.save(project=False, pipeline=True, fs=None)

    mock_get_fs.assert_called_once()
    assert mock_get_fs.call_args.args[0] == "."


def test_project_structure_uses_pipeline_dir_setting() -> None:
    fs = MagicMock()

    with patch("flowerpower.flowerpower.settings.CONFIG_DIR", "settings"):
        with patch("flowerpower.flowerpower.settings.PIPELINES_DIR", "flows"):
            FlowerPowerProject._create_project_structure(fs, "custom_hooks")

    fs.makedirs.assert_any_call("settings/flows", exist_ok=True)
    fs.makedirs.assert_any_call("flows", exist_ok=True)
    fs.makedirs.assert_any_call("custom_hooks", exist_ok=True)


def test_config_accepts_none_storage_options() -> None:
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        storage_options=None,
    )

    assert cfg.storage_options == {}


def test_pipeline_registry_uses_configured_pipeline_dir_for_name_resolution() -> None:
    registry = PipelineRegistry(
        project_cfg=ProjectConfig(name="demo"),
        fs=MagicMock(),
        cfg_dir="settings",
        pipelines_dir="flows",
    )

    assert registry._pipeline_name_from_path("flows/group/example.py") == "group.example"


def test_pipeline_manager_resolves_config_dirs_at_runtime() -> None:
    fs = MagicMock()

    with patch("flowerpower.pipeline.manager.CONFIG_DIR", "settings"):
        with patch("flowerpower.pipeline.manager.PIPELINES_DIR", "flows"):
            with patch.object(PipelineManager, "_initialize_managers"):
                with patch.object(PipelineManager, "_ensure_directories_exist"):
                    with patch("flowerpower.pipeline.manager.add_modules_path"):
                        manager = PipelineManager(base_dir=".", fs=fs)

    assert manager._cfg_dir == "settings"
    assert manager._pipelines_dir == "flows"


def test_pipeline_support_classes_resolve_config_dirs_at_runtime() -> None:
    fs = MagicMock()
    project_cfg = ProjectConfig(name="demo")

    with patch("flowerpower.pipeline.config_manager.CONFIG_DIR", "settings"):
        with patch("flowerpower.pipeline.config_manager.PIPELINES_DIR", "flows"):
            manager = PipelineConfigManager(
                base_dir=".",
                fs=fs,
                storage_options={},
            )

    assert manager._cfg_dir == "settings"
    assert manager._pipelines_dir == "flows"

    with patch("flowerpower.pipeline.registry.CONFIG_DIR", "settings"):
        with patch("flowerpower.pipeline.registry.PIPELINES_DIR", "flows"):
            registry = PipelineRegistry(project_cfg=project_cfg, fs=fs)

    assert registry._cfg_dir == "settings"
    assert registry._pipelines_dir == "flows"

    with patch("flowerpower.pipeline.visualizer.CONFIG_DIR", "settings"):
        with patch("flowerpower.pipeline.visualizer.PIPELINES_DIR", "flows"):
            visualizer = PipelineVisualizer(project_cfg=project_cfg, fs=fs)

    assert visualizer._cfg_dir == "settings"
    assert visualizer._pipelines_dir == "flows"
