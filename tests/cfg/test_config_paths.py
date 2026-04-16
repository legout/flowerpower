import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from fsspeckit import BaseStorageOptions, filesystem

from flowerpower.cfg import Config
from flowerpower.cfg.exceptions import ConfigLoadError, ConfigSaveError
from flowerpower.cfg.pipeline import PipelineConfig
from flowerpower.cfg.pipeline.builder import RunConfigBuilder as LegacyRunConfigBuilder
from flowerpower.cfg.project import ProjectConfig
from flowerpower.flowerpower import FlowerPowerProject
from flowerpower.pipeline.config_manager import PipelineConfigManager
from flowerpower.pipeline.manager import PipelineManager
from flowerpower.pipeline.registry import PipelineRegistry
from flowerpower.utils.security import SecurityError


def test_project_config_load_uses_config_dir_constant() -> None:
    fs = MagicMock()
    fs.exists.side_effect = lambda path: path == "settings/project.yml"

    with patch("flowerpower.cfg.project.CONFIG_DIR", "settings"):
        with patch.object(ProjectConfig, "from_yaml", return_value=ProjectConfig(name="demo")) as mock_from_yaml:
            ProjectConfig.load(fs=fs)

    mock_from_yaml.assert_called_once_with(path="settings/project.yml", fs=fs)


def test_project_config_rejects_absolute_yaml_paths() -> None:
    fs = MagicMock()
    absolute_path = str(Path(tempfile.gettempdir()) / "project.yml")

    with pytest.raises(ConfigLoadError, match="Path validation failed"):
        ProjectConfig.from_yaml(absolute_path, fs=fs)


def test_project_config_allows_empty_config_dir_override() -> None:
    fs = MagicMock()
    fs.exists.side_effect = lambda path: path == "project.yml"

    with patch.object(ProjectConfig, "from_yaml", return_value=ProjectConfig(name="demo")) as mock_from_yaml:
        ProjectConfig.load(fs=fs, cfg_dir="")

    mock_from_yaml.assert_called_once_with(path="project.yml", fs=fs)


def test_project_config_load_prefers_existing_yaml_extension() -> None:
    fs = MagicMock()
    fs.exists.side_effect = lambda path: path == "settings/project.yaml"

    with patch.object(
        ProjectConfig,
        "from_yaml",
        return_value=ProjectConfig(name="demo"),
    ) as mock_from_yaml:
        ProjectConfig.load(fs=fs, cfg_dir="settings")

    mock_from_yaml.assert_called_once_with(path="settings/project.yaml", fs=fs)


def test_project_config_save_and_load_preserves_hooks_dir() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        cfg = ProjectConfig(name="demo", hooks_dir="custom_hooks")

        cfg.save(fs=fs)

        loaded = ProjectConfig.load(fs=fs)

        assert loaded.hooks_dir == "custom_hooks"


def test_project_config_save_uses_canonical_root_relative_path() -> None:
    fs = MagicMock()
    cfg = ProjectConfig(name="demo")

    with patch.object(ProjectConfig, "to_yaml") as mock_to_yaml:
        cfg.save(fs=fs, cfg_dir="")

    mock_to_yaml.assert_called_once_with(path="project.yml", fs=fs)


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


def test_pipeline_config_dotted_name_round_trip() -> None:
    """Verify that a dotted pipeline name like group.my-pipeline round-trips
    through save and load using the shared path formatter (dots → slashes)."""
    fs = MagicMock()
    fs.exists.side_effect = lambda path: path == "conf/pipelines/group/my_pipeline.yml"

    with patch.object(PipelineConfig, "from_yaml", return_value=PipelineConfig(name="group.my-pipeline")) as mock_from_yaml:
        PipelineConfig.load(name="group.my-pipeline", fs=fs)

    mock_from_yaml.assert_called_once_with(
        name="group.my-pipeline",
        path="conf/pipelines/group/my_pipeline.yml",
        fs=fs,
    )


def test_pipeline_config_load_prefers_stored_name_from_yaml() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        conf = Path(tmpdir) / "conf" / "pipelines"
        (conf / "group").mkdir(parents=True)
        with (conf / "group" / "my_pipeline.yml").open("w") as fh:
            yaml.safe_dump({"name": "group.my-pipeline", "run": {"log_level": "INFO"}}, fh)

        cfg = PipelineConfig.load(
            name="group.my_pipeline",
            fs=fs,
        )

        assert cfg.name == "group.my-pipeline"


def test_pipeline_config_load_skips_probe_errors_and_uses_fallback_path() -> None:
    fs = MagicMock()

    def exists(path: str) -> bool:
        if path == "conf/pipelines/my_pipeline.yml":
            raise PermissionError("denied")
        return path == "conf/my_pipeline.yml"

    fs.exists.side_effect = exists

    with patch.object(
        PipelineConfig,
        "from_yaml",
        return_value=PipelineConfig(name="my-pipeline"),
    ) as mock_from_yaml:
        cfg = PipelineConfig.load(name="my-pipeline", fs=fs)

    assert cfg.name == "my-pipeline"
    mock_from_yaml.assert_called_once_with(
        name="my-pipeline",
        path="conf/my_pipeline.yml",
        fs=fs,
    )


def test_pipeline_config_save_persists_original_name() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        cfg = PipelineConfig(name="group.my-pipeline")

        cfg.save(fs=fs)

        saved = yaml.safe_load((Path(tmpdir) / "conf" / "pipelines" / "group" / "my_pipeline.yml").read_text())
        assert saved["name"] == "group.my-pipeline"


def test_pipeline_config_save_uses_canonical_root_relative_path() -> None:
    fs = MagicMock()
    cfg = PipelineConfig(name="root-pipeline")

    with patch.object(PipelineConfig, "to_yaml") as mock_to_yaml:
        cfg.save(fs=fs, cfg_dir="", pipelines_dir="")

    mock_to_yaml.assert_called_once_with(path="root_pipeline.yml", fs=fs)


def test_pipeline_config_to_yaml_supports_root_relative_paths() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        cfg = PipelineConfig(name="root-pipeline")

        cfg.to_yaml("root_pipeline.yml", fs=fs)

        assert (Path(tmpdir) / "root_pipeline.yml").exists()


def test_pipeline_config_rejects_absolute_yaml_paths() -> None:
    fs = MagicMock()
    cfg = PipelineConfig(name="root-pipeline")
    absolute_path = str(Path(tempfile.gettempdir()) / "root_pipeline.yml")

    with pytest.raises(ConfigSaveError, match="Path validation failed"):
        cfg.to_yaml(absolute_path, fs=fs)


def test_pipeline_config_rejects_traversal_directory_overrides() -> None:
    fs = MagicMock()

    with pytest.raises(SecurityError):
        PipelineConfig.load(
            name="my-pipeline",
            fs=fs,
            cfg_dir="../evil",
            pipelines_dir="flows",
        )


def test_pipeline_config_update_preserves_scalar_fields_and_syncs_h_params() -> None:
    cfg = PipelineConfig(name="old-name", params={"foo": 1})

    cfg.update(
        {
            "name": "new-name",
            "run": {"log_level": "DEBUG"},
            "params": {"bar": 2},
        }
    )

    assert cfg.name == "new-name"
    assert cfg.run.log_level == "DEBUG"
    assert cfg.params == {"foo": 1, "bar": 2}
    assert "bar" in cfg.h_params


def test_pipeline_config_load_passes_storage_options_to_cached_filesystem() -> None:
    fake_fs = MagicMock()
    fake_fs.exists.return_value = False
    PipelineConfig._filesystem_cache.clear()

    try:
        with patch("flowerpower.cfg.base.filesystem", return_value=fake_fs) as mock_filesystem:
            PipelineConfig.load(
                base_dir="s3://bucket/project",
                name="demo",
                storage_options={"anon": True},
            )
    finally:
        PipelineConfig._filesystem_cache.clear()

    mock_filesystem.assert_called_once_with(
        "s3://bucket/project",
        storage_options={"anon": True},
        cached=True,
        dirfs=True,
    )


def test_combined_config_accepts_base_storage_options() -> None:
    class DummyStorageOptions(BaseStorageOptions):
        endpoint: str | None = None

    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        storage_options=DummyStorageOptions(
            protocol="s3", endpoint="https://example.invalid"
        ),
    )

    assert dict(cfg.storage_options) == {
        "protocol": "s3",
        "endpoint": "https://example.invalid",
    }


def test_pipeline_config_load_preserves_protocol_from_base_storage_options() -> None:
    class DummyStorageOptions(BaseStorageOptions):
        endpoint: str | None = None

    fake_fs = MagicMock()
    fake_fs.exists.return_value = False
    PipelineConfig._filesystem_cache.clear()

    try:
        with patch("flowerpower.cfg.base.filesystem", return_value=fake_fs) as mock_filesystem:
            PipelineConfig.load(
                base_dir="bucket/project",
                name="demo",
                storage_options=DummyStorageOptions(
                    protocol="s3", endpoint="https://example.invalid"
                ),
            )
    finally:
        PipelineConfig._filesystem_cache.clear()

    mock_filesystem.assert_called_once_with(
        "bucket/project",
        storage_options={
            "protocol": "s3",
            "endpoint": "https://example.invalid",
        },
        cached=True,
        dirfs=True,
    )


def test_cached_filesystem_cache_is_bounded() -> None:
    PipelineConfig._filesystem_cache.clear()
    maxsize = PipelineConfig._filesystem_cache_maxsize

    try:
        with patch("flowerpower.cfg.base.filesystem", side_effect=lambda *args, **kwargs: MagicMock()) as mock_filesystem:
            for idx in range(maxsize + 1):
                PipelineConfig._get_cached_filesystem(f"project-{idx}")
    finally:
        cache_keys = list(PipelineConfig._filesystem_cache.keys())
        PipelineConfig._filesystem_cache.clear()

    assert len(cache_keys) == maxsize
    assert ("project-0", "{}") not in cache_keys
    assert (f"project-{maxsize}", "{}") in cache_keys
    assert mock_filesystem.call_count == maxsize + 1



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
    mock_project_to_yaml.assert_called_once_with(path="settings/project.yml", fs=fs)


def test_combined_config_save_preserves_custom_directories_by_default() -> None:
    fs = MagicMock()
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        fs=fs,
        cfg_dir="settings",
        pipelines_dir="flows",
    )

    with patch.object(PipelineConfig, "to_yaml") as mock_pipeline_to_yaml:
        with patch.object(ProjectConfig, "to_yaml") as mock_project_to_yaml:
            cfg.save(project=True, pipeline=True, fs=fs)

    mock_pipeline_to_yaml.assert_called_once_with(
        path="settings/flows/my_pipeline.yml",
        fs=fs,
    )
    mock_project_to_yaml.assert_called_once_with(path="settings/project.yml", fs=fs)


def test_combined_config_save_preserves_empty_config_dir_override_by_default() -> None:
    fs = MagicMock()
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        fs=fs,
        cfg_dir="",
        pipelines_dir="flows",
    )

    with patch.object(PipelineConfig, "to_yaml") as mock_pipeline_to_yaml:
        cfg.save(project=False, pipeline=True, fs=fs)

    mock_pipeline_to_yaml.assert_called_once_with(
        path="flows/my_pipeline.yml",
        fs=fs,
    )


def test_combined_config_save_uses_canonical_root_relative_pipeline_path() -> None:
    fs = MagicMock()
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        fs=fs,
        cfg_dir="",
        pipelines_dir="",
    )

    with patch.object(PipelineConfig, "to_yaml") as mock_pipeline_to_yaml:
        cfg.save(project=False, pipeline=True, fs=fs)

    mock_pipeline_to_yaml.assert_called_once_with(
        path="my_pipeline.yml",
        fs=fs,
    )


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


def test_combined_config_save_creates_pipeline_directories_via_pipeline_to_yaml() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        cfg = Config(
            base_dir=tmpdir,
            project=ProjectConfig(name="demo"),
            pipeline=PipelineConfig(name="group.my-pipeline"),
            fs=fs,
        )

        cfg.save(project=False, pipeline=True, fs=fs)

        assert (Path(tmpdir) / "conf" / "pipelines" / "group" / "my_pipeline.yml").exists()


def test_combined_config_save_creates_project_directory() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        cfg = Config(
            base_dir=tmpdir,
            project=ProjectConfig(name="demo"),
            pipeline=PipelineConfig(name="group.my-pipeline"),
            fs=fs,
        )

        cfg.save(project=True, pipeline=False, fs=fs)

        assert (Path(tmpdir) / "conf" / "project.yml").exists()


def test_combined_config_save_requires_pipeline_name() -> None:
    fs = MagicMock()
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name=None),
        fs=fs,
    )

    with patch.object(PipelineConfig, "to_yaml") as mock_pipeline_to_yaml:
        with pytest.raises(ValueError, match="Pipeline name is not set"):
            cfg.save(project=False, pipeline=True, fs=fs)

    mock_pipeline_to_yaml.assert_not_called()


def test_combined_config_save_rejects_invalid_pipeline_name() -> None:
    fs = MagicMock()
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="valid-name"),
        fs=fs,
    )
    # Use a name with actual path traversal characters
    cfg.pipeline.name = "bad/name"

    with patch.object(PipelineConfig, "to_yaml") as mock_pipeline_to_yaml:
        try:
            cfg.save(project=False, pipeline=True, fs=fs)
        except Exception as exc:
            assert "invalid characters" in str(exc).lower() or "path traversal" in str(exc).lower()
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
    # base_dir remains None (no implicit default in Config.save)
    assert mock_get_fs.call_args[0][0] is None


def test_combined_config_save_reuses_instance_storage_options() -> None:
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        fs=None,
        storage_options={"anon": True},
    )

    fake_fs = MagicMock()

    with patch.object(Config, "_get_cached_filesystem", return_value=fake_fs) as mock_get_fs:
        with patch.object(PipelineConfig, "to_yaml"):
            cfg.save(project=False, pipeline=True, fs=None)

    mock_get_fs.assert_called_once()
    assert mock_get_fs.call_args[0][0] == "."
    assert dict(mock_get_fs.call_args[0][1]) == {"anon": True}


def test_combined_config_save_uses_explicit_fs_when_self_fs_missing() -> None:
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        fs=None,
    )
    explicit_fs = MagicMock()

    with patch.object(PipelineConfig, "to_yaml") as mock_pipeline_to_yaml:
        cfg.save(project=False, pipeline=True, fs=explicit_fs)

    mock_pipeline_to_yaml.assert_called_once_with(
        path="conf/pipelines/my_pipeline.yml",
        fs=explicit_fs,
    )


def test_config_accepts_none_storage_options() -> None:
    cfg = Config(
        base_dir=".",
        project=ProjectConfig(name="demo"),
        pipeline=PipelineConfig(name="my-pipeline"),
        storage_options=None,
    )

    assert cfg.storage_options == {}


def test_project_structure_uses_pipeline_dir_setting() -> None:
    fs = MagicMock()

    with patch("flowerpower.flowerpower.settings.CONFIG_DIR", "settings"):
        with patch("flowerpower.flowerpower.settings.PIPELINES_DIR", "flows"):
            FlowerPowerProject._create_project_structure(fs, "custom_hooks")

    fs.makedirs.assert_any_call("settings/flows", exist_ok=True)
    fs.makedirs.assert_any_call("flows", exist_ok=True)
    fs.makedirs.assert_any_call("custom_hooks", exist_ok=True)


def test_pipeline_manager_resolves_config_dirs_at_runtime() -> None:
    fs = MagicMock()

    with patch.object(PipelineManager, "_initialize_managers"):
        with patch.object(PipelineManager, "_ensure_directories_exist"):
            with patch("flowerpower.pipeline.registry.add_modules_path"):
                manager = PipelineManager(base_dir=".", fs=fs, cfg_dir="settings", pipelines_dir="flows")

    assert manager._cfg_dir == "settings"
    assert manager._pipelines_dir == "flows"


def test_pipeline_manager_allows_empty_config_dir() -> None:
    fs = MagicMock()

    with patch.object(PipelineManager, "_initialize_managers"):
        with patch("flowerpower.pipeline.registry.add_modules_path"):
            manager = PipelineManager(base_dir=".", fs=fs, cfg_dir="", pipelines_dir="flows")

    fs.makedirs.assert_any_call(".", exist_ok=True)
    fs.makedirs.assert_any_call("flows", exist_ok=True)
    assert manager._cfg_dir == ""


def test_pipeline_manager_rejects_traversal_config_dirs() -> None:
    fs = MagicMock()

    with pytest.raises(SecurityError):
        PipelineManager(base_dir=".", fs=fs, cfg_dir="../evil", pipelines_dir="flows")


def test_pipeline_support_classes_resolve_config_dirs_at_runtime() -> None:
    fs = MagicMock()
    project_cfg = ProjectConfig(name="demo")

    manager = PipelineConfigManager(
        base_dir=".",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )
    assert manager._cfg_dir == "settings"
    assert manager._pipelines_dir == "flows"

    registry = PipelineRegistry(project_cfg=project_cfg, fs=fs, cfg_dir="settings", pipelines_dir="flows")
    assert registry._cfg_dir == "settings"
    assert registry._pipelines_dir == "flows"


def test_pipeline_registry_prefers_config_manager_dirs_when_provided() -> None:
    fs = MagicMock()
    project_cfg = ProjectConfig(name="demo")

    manager = PipelineConfigManager(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )

    registry = PipelineRegistry(
        project_cfg=project_cfg,
        fs=fs,
        base_dir=".",
        config_manager=manager,
    )

    assert registry._base_dir == "/project"
    assert registry._cfg_dir == "settings"
    assert registry._pipelines_dir == "flows"


def test_pipeline_support_classes_default_none_config_dirs_to_constants() -> None:
    fs = MagicMock()
    project_cfg = ProjectConfig(name="demo")

    manager_cfg = PipelineConfigManager(
        base_dir=".",
        fs=fs,
        storage_options={},
        cfg_dir=None,
        pipelines_dir=None,
    )
    assert manager_cfg._cfg_dir == "conf"
    assert manager_cfg._pipelines_dir == "pipelines"

    with patch.object(PipelineManager, "_initialize_managers"):
        with patch.object(PipelineManager, "_ensure_directories_exist"):
            with patch("flowerpower.pipeline.registry.add_modules_path"):
                manager = PipelineManager(base_dir=".", fs=fs, cfg_dir=None, pipelines_dir=None)

    assert manager._cfg_dir == "conf"
    assert manager._pipelines_dir == "pipelines"

    registry = PipelineRegistry(project_cfg=project_cfg, fs=fs, cfg_dir=None, pipelines_dir=None)
    assert registry._cfg_dir == "conf"
    assert registry._pipelines_dir == "pipelines"


def test_config_loading_produces_identical_results_across_entry_points() -> None:
    """Verify that Config.load, PipelineConfigManager, and PipelineRegistry
    produce the same pipeline config (including env overlays) for the same
    on-disk YAML.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        conf = Path(tmpdir) / "conf"
        conf.mkdir()
        with (conf / "project.yml").open("w") as fh:
            yaml.safe_dump({"name": "demo"}, fh)
        pipelines = conf / "pipelines"
        pipelines.mkdir()
        with (pipelines / "my_pipeline.yml").open("w") as fh:
            yaml.safe_dump({"run": {"log_level": "INFO"}}, fh)

        with patch.dict("os.environ", {"FP_PIPELINE__RUN__LOG_LEVEL": "WARNING"}):
            # Entry point 1: Config.load
            combined = Config.load(base_dir=tmpdir, pipeline_name="my-pipeline", fs=fs)
            cfg_combined = combined.pipeline

            # Entry point 2: PipelineConfigManager
            manager = PipelineConfigManager(base_dir=tmpdir, fs=fs, storage_options={})
            cfg_manager = manager.load_pipeline_config("my-pipeline")

            # Entry point 3: PipelineRegistry with manager
            registry = PipelineRegistry(
                project_cfg=manager.project_config,
                fs=fs,
                base_dir=tmpdir,
                config_manager=manager,
            )
            cfg_registry = registry.load_config("my-pipeline")

        assert cfg_combined.run.log_level == "WARNING"
        assert cfg_manager.run.log_level == "WARNING"
        assert cfg_registry.run.log_level == "WARNING"
        assert cfg_combined.to_dict() == cfg_manager.to_dict() == cfg_registry.to_dict()


def test_config_load_parses_env_overlays_once_via_config_manager() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        conf = Path(tmpdir) / "conf"
        conf.mkdir()
        with (conf / "project.yml").open("w") as fh:
            yaml.safe_dump({"name": "demo"}, fh)
        pipelines = conf / "pipelines"
        pipelines.mkdir()
        with (pipelines / "my_pipeline.yml").open("w") as fh:
            yaml.safe_dump({"run": {"log_level": "INFO"}}, fh)

        call_count = 0

        def count_and_return(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1
            return {"pipeline": {"run": {"log_level": "WARNING"}}}

        with patch(
            "flowerpower.utils.env.parse_env_overrides",
            side_effect=count_and_return,
        ):
            combined = Config.load(base_dir=tmpdir, pipeline_name="my-pipeline", fs=fs)

        assert call_count == 1
        assert combined.pipeline.run.log_level == "WARNING"


def test_pipeline_registry_from_filesystem_applies_env_overlays() -> None:
    """Verify that PipelineRegistry.from_filesystem() applies env overlays
    consistently with other config loading entry points.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        conf = Path(tmpdir) / "conf"
        conf.mkdir()
        with (conf / "project.yml").open("w") as fh:
            yaml.safe_dump({"name": "demo"}, fh)
        pipelines = conf / "pipelines"
        pipelines.mkdir()
        with (pipelines / "my_pipeline.yml").open("w") as fh:
            yaml.safe_dump({"run": {"log_level": "INFO"}}, fh)

        with patch.dict("os.environ", {"FP_PIPELINE__RUN__LOG_LEVEL": "WARNING"}):
            registry = PipelineRegistry.from_filesystem(base_dir=tmpdir, fs=fs)
            cfg_registry = registry.load_config("my-pipeline")

        assert cfg_registry.run.log_level == "WARNING"


def test_config_load_without_pipeline_name_still_applies_pipeline_env_overlays() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        conf = Path(tmpdir) / "conf"
        conf.mkdir()
        with (conf / "project.yml").open("w") as fh:
            yaml.safe_dump({"name": "demo"}, fh)

        with patch.dict("os.environ", {"FP_PIPELINE__RUN__LOG_LEVEL": "WARNING"}):
            combined = Config.load(base_dir=tmpdir, fs=fs)

        assert combined.pipeline.run.log_level == "WARNING"


def test_config_load_preserves_explicit_project_name_when_project_file_is_missing() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)

        combined = Config.load(
            base_dir=tmpdir,
            name="demo-project",
            pipeline_name="my-pipeline",
            fs=fs,
        )

        assert combined.project.name == "demo-project"


def test_legacy_run_config_builder_uses_canonical_env_overlay_path() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        conf = Path(tmpdir) / "conf"
        conf.mkdir()
        with (conf / "project.yml").open("w") as fh:
            yaml.safe_dump({"name": "demo"}, fh)
        pipelines = conf / "pipelines"
        pipelines.mkdir()
        with (pipelines / "my_pipeline.yml").open("w") as fh:
            yaml.safe_dump({"run": {"log_level": "INFO"}}, fh)

        with patch.dict("os.environ", {"FP_PIPELINE__RUN__LOG_LEVEL": "WARNING"}):
            with pytest.deprecated_call():
                builder = LegacyRunConfigBuilder(
                    pipeline_name="my-pipeline",
                    base_dir=tmpdir,
                    fs=fs,
                )

        assert builder.build().log_level == "WARNING"


def test_legacy_run_config_builder_surfaces_invalid_pipeline_config() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        conf = Path(tmpdir) / "conf" / "pipelines"
        conf.mkdir(parents=True)
        with (Path(tmpdir) / "conf" / "project.yml").open("w") as fh:
            yaml.safe_dump({"name": "demo"}, fh)
        (conf / "my_pipeline.yml").write_text("run: [not-a-mapping]\n")

        with pytest.deprecated_call():
            with pytest.raises(ConfigLoadError):
                LegacyRunConfigBuilder(
                    pipeline_name="my-pipeline",
                    base_dir=tmpdir,
                    fs=fs,
                )
