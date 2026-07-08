import datetime as dt
import posixpath  # Important for consistent path joining as used in registry.py
import tempfile
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import pytest
import yaml
from fsspeckit import (
    AbstractFileSystem,  # For type hinting mocks
    filesystem,
)

from flowerpower.cfg import PipelineConfig, ProjectConfig
from flowerpower.pipeline.config_manager import PipelineConfigManager
from flowerpower.pipeline.registry import CachedPipelineData, HookType, PipelineRegistry
from flowerpower.utils.security import SecurityError
from flowerpower.utils.templates import HOOK_TEMPLATE__MQTT_BUILD_CONFIG

# --- Fixtures ---


@pytest.fixture
def mock_fs(mocker):
    """Fixture for a mocked AbstractFileSystem."""
    fs = mocker.MagicMock(spec=AbstractFileSystem)
    fs.exists = mocker.MagicMock(
        return_value=True
    )  # Default to True for paths that should exist
    fs.open = mocker.mock_open()  # General mock for open
    fs.makedirs = mocker.MagicMock()
    fs.rm = mocker.MagicMock()
    fs.glob = mocker.MagicMock(return_value=[])
    fs.ls = mocker.MagicMock(return_value=[])
    fs.modified = mocker.MagicMock(return_value=dt.datetime.now())
    fs.size = mocker.MagicMock(return_value=1024)
    fs.cat = mocker.MagicMock(return_value=b"")  # Returns bytes
    return fs


@pytest.fixture
def mock_project_cfg(mocker):
    """Fixture for a mocked ProjectConfig."""
    cfg = mocker.MagicMock(spec=ProjectConfig)
    cfg.name = "test_project"
    cfg.hooks_dir = "hooks"
    # Other attributes will be set by the registry or can be mocked as needed
    cfg.to_dict = mocker.MagicMock(
        return_value={"name": "test_project", "version": "0.1"}
    )
    return cfg


@pytest.fixture
def mock_pipeline_cfg_instance(mocker):
    """Fixture for a mocked PipelineConfig instance."""
    from flowerpower.cfg import PipelineConfig

    cfg_instance = mocker.MagicMock(spec=PipelineConfig)
    cfg_instance.name = "test_pipeline"
    cfg_instance.version = "1.0"
    cfg_instance.to_dict = mocker.MagicMock(
        return_value={"name": "test_pipeline", "version": "1.0"}
    )
    return cfg_instance


@pytest.fixture
def registry(mock_project_cfg, mock_fs):
    """Fixture for PipelineRegistry instance."""
    return PipelineRegistry(
        project_cfg=mock_project_cfg,
        fs=mock_fs,
    )


# --- Test Cases ---


class TestPipelineRegistry:
    def test_initialization(self, registry, mock_project_cfg, mock_fs):
        assert registry.project_cfg == mock_project_cfg
        assert registry._fs == mock_fs
        assert registry._cfg_dir == "conf"
        assert registry._pipelines_dir == "pipelines"
        assert registry._presenter is not None

    def test_new_delegates_to_pipeline_creator(self, registry, mocker):
        creator = mocker.MagicMock()
        mocker.patch.object(registry, "_creator", return_value=creator)

        registry.new("demo-pipeline", overwrite=True)

        creator.new.assert_called_once_with(name="demo-pipeline", overwrite=True)

    def test_delete_delegates_to_pipeline_creator(self, registry, mocker):
        creator = mocker.MagicMock()
        mocker.patch.object(registry, "_creator", return_value=creator)

        registry.delete("demo-pipeline", cfg=False, module=True)

        creator.delete.assert_called_once_with(
            name="demo-pipeline", cfg=False, module=True
        )

    def test_create_pipeline_alias_delegates_to_new(self, registry, mocker):
        mock_new = mocker.patch.object(registry, "new")

        registry.create_pipeline("demo-pipeline", overwrite=True)

        mock_new.assert_called_once_with(name="demo-pipeline", overwrite=True)

    def test_delete_pipeline_alias_delegates_to_delete(self, registry, mocker):
        mock_delete = mocker.patch.object(registry, "delete")

        registry.delete_pipeline("demo-pipeline", cfg=False, module=True)

        mock_delete.assert_called_once_with(
            name="demo-pipeline", cfg=False, module=True
        )

    # --- Tests for _get_files() and _get_names() ---
    def test_get_files_and_names(self, registry, mock_fs):
        mock_fs.glob.return_value = [
            posixpath.join(registry._pipelines_dir, "pipe1.py"),
            posixpath.join(registry._pipelines_dir, "pipe2.py"),
        ]

        files = registry._get_files()
        assert len(files) == 2
        assert posixpath.join(registry._pipelines_dir, "pipe1.py") in files

        names = registry._get_names()
        assert sorted(names) == sorted(["pipe1", "pipe2"])

    def test_get_names_discovers_nested_modules(self, registry, mock_fs):
        mock_fs.glob.side_effect = [
            [posixpath.join(registry._pipelines_dir, "top_level.py")],
            [posixpath.join(registry._pipelines_dir, "group", "nested_pipe.py")],
        ]

        assert registry._get_names() == ["group.nested_pipe", "top_level"]

    def test_get_names_prefers_stored_pipeline_name(self, registry, mock_fs):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)
            pipelines_dir = Path(tmpdir) / "pipelines" / "group"
            config_dir = Path(tmpdir) / "conf" / "pipelines" / "group"
            pipelines_dir.mkdir(parents=True)
            config_dir.mkdir(parents=True)
            (pipelines_dir / "my_pipeline.py").write_text("def x():\n    return 1\n")
            with (config_dir / "my_pipeline.yml").open("w") as fh:
                yaml.safe_dump({"name": "group.my-pipeline"}, fh)

            registry = PipelineRegistry(
                project_cfg=ProjectConfig(name="demo"),
                fs=fs,
            )

            assert registry._get_names() == ["group.my-pipeline"]

    def test_read_stored_pipeline_name_skips_probe_errors(self, registry, mock_fs):
        def exists(path: str) -> bool:
            if path == "conf/pipelines/group/my_pipeline.yml":
                raise PermissionError("denied")
            return path == "conf/group/my_pipeline.yml"

        mock_fs.exists.side_effect = exists
        mock_fs.open = MagicMock()
        mock_fs.open.return_value.__enter__.return_value = "name: group.my-pipeline\n"

        assert registry._read_stored_pipeline_name("group/my_pipeline") == "group.my-pipeline"

    def test_get_files_fs_error(self, registry, mock_fs, mocker):
        mock_fs.glob.side_effect = Exception("FS error")
        mock_logger_error = mocker.patch("flowerpower.pipeline.catalog.logger.error")

        assert registry._get_files() == []
        mock_logger_error.assert_called_once()

    def test_get_files_ignores_unsupported_recursive_glob(self, registry, mock_fs):
        mock_fs.glob.side_effect = [
            [posixpath.join(registry._pipelines_dir, "top_level.py")],
            NotImplementedError("recursive glob unsupported"),
        ]

        assert registry._get_files() == [
            posixpath.join(registry._pipelines_dir, "top_level.py")
        ]

    # --- Tests for get_summary() method ---
    @patch("flowerpower.pipeline.config_manager.PipelineConfig")  # Mock the class itself
    def test_get_summary_single_pipeline(
        self,
        MockPipelineConfig,
        registry,
        mock_fs,
        mock_project_cfg,
        mock_pipeline_cfg_instance,
    ):
        pipeline_name = "summary_pipe"

        # Setup mocks for this test
        mock_fs.glob.return_value = [
            posixpath.join(registry._pipelines_dir, f"{pipeline_name}.py")
        ]  # for _get_names
        MockPipelineConfig.load.return_value = (
            mock_pipeline_cfg_instance  # For PipelineConfig.load call
        )
        mock_fs.cat.return_value = b"pipeline_code_content"
        mock_project_cfg.to_dict.return_value = {"project_data": "value"}

        summary = registry.get_summary(
            name=pipeline_name, cfg=True, code=True, project=True
        )

        assert "project" in summary
        assert summary["project"] == {"project_data": "value"}
        assert pipeline_name in summary["pipelines"]
        assert (
            summary["pipelines"][pipeline_name]["cfg"]
            == mock_pipeline_cfg_instance.to_dict()
        )
        assert summary["pipelines"][pipeline_name]["module"] == "pipeline_code_content"

        MockPipelineConfig.load.assert_called_once_with(name=pipeline_name, fs=mock_fs, base_dir=".", storage_options={}, cfg_dir="conf", pipelines_dir="pipelines")
        mock_fs.cat.assert_called_once_with(
            posixpath.join(registry._pipelines_dir, f"{pipeline_name}.py")
        )

    @patch("flowerpower.pipeline.config_manager.PipelineConfig")
    def test_get_summary_uses_formatted_module_path_for_dotted_pipeline(
        self,
        MockPipelineConfig,
        registry,
        mock_fs,
        mock_pipeline_cfg_instance,
    ):
        pipeline_name = "group.my-pipeline"
        MockPipelineConfig.load.return_value = mock_pipeline_cfg_instance
        mock_fs.cat.return_value = b"pipeline_code_content"

        registry.get_summary(name=pipeline_name, cfg=True, code=True, project=False)

        mock_fs.cat.assert_called_once_with(
            posixpath.join(registry._pipelines_dir, "group", "my_pipeline.py")
        )

    def test_load_module_supports_nested_pipeline_package_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)
            root = Path(tmpdir)

            (root / "pkg" / "flows" / "group").mkdir(parents=True)
            (root / "pkg" / "__init__.py").write_text("")
            (root / "pkg" / "flows" / "__init__.py").write_text("")
            (root / "pkg" / "flows" / "group" / "__init__.py").write_text("")
            (root / "pkg" / "flows" / "group" / "my_pipeline.py").write_text(
                "VALUE = 1\n"
            )

            (root / "conf" / "pkg" / "flows" / "group").mkdir(parents=True)
            with (root / "conf" / "project.yml").open("w") as fh:
                yaml.safe_dump({"name": "demo"}, fh)
            with (root / "conf" / "pkg" / "flows" / "group" / "my_pipeline.yml").open(
                "w"
            ) as fh:
                yaml.safe_dump({"name": "group.my-pipeline"}, fh)

            registry = PipelineRegistry(
                project_cfg=ProjectConfig(name="demo"),
                fs=fs,
                base_dir=tmpdir,
                cfg_dir="conf",
                pipelines_dir="pkg/flows",
            )

            module = registry.load_module("group.my-pipeline")

            assert module.__name__ == "pkg.flows.group.my_pipeline"
            assert module.VALUE == 1

    def test_from_filesystem_supports_custom_configured_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)
            root = Path(tmpdir)

            (root / "settings" / "flows").mkdir(parents=True)
            (root / "flows").mkdir(parents=True)
            (root / "settings" / "project.yml").write_text("name: demo\n")
            (root / "settings" / "flows" / "pipe.yml").write_text(
                "name: pipe\nrun:\n  log_level: INFO\n"
            )
            (root / "flows" / "pipe.py").write_text("def x():\n    return 1\n")

            registry = PipelineRegistry.from_filesystem(
                base_dir=tmpdir,
                fs=fs,
                cfg_dir="settings",
                pipelines_dir="flows",
            )

            assert registry.project_cfg.name == "demo"
            assert registry.pipelines == ["pipe"]
            assert registry.load_config("pipe").run.log_level == "INFO"

    @patch("flowerpower.pipeline.config_manager.PipelineConfig")
    def test_get_summary_all_pipelines(
        self,
        MockPipelineConfig,
        registry,
        mock_fs,
        mock_project_cfg,
        mock_pipeline_cfg_instance,
    ):
        # Similar to single, but _get_names will return multiple, and loop will run
        mock_fs.glob.return_value = [
            posixpath.join(registry._pipelines_dir, "pipe1.py"),
            posixpath.join(registry._pipelines_dir, "pipe2.py"),
        ]
        # Make load return different cfgs if needed, or same for simplicity if only names matter for distinction
        mock_config1 = MagicMock(spec=PipelineConfig)
        mock_config1.name = "pipe1"
        mock_config1.to_dict.return_value = {"name": "pipe1"}
        mock_config2 = MagicMock(spec=PipelineConfig)
        mock_config2.name = "pipe2"
        mock_config2.to_dict.return_value = {"name": "pipe2"}
        MockPipelineConfig.load.side_effect = (
            lambda name, fs, **kwargs: mock_config1 if name == "pipe1" else mock_config2
        )

        mock_fs.cat.side_effect = lambda path: b"code_for_" + bytes(
            posixpath.basename(path).split(".")[0], "utf-8"
        )

        summary = registry.get_summary(
            cfg=True, code=True, project=False
        )  # No project details

        assert "project" not in summary
        assert "pipe1" in summary["pipelines"]
        assert summary["pipelines"]["pipe1"]["cfg"] == {"name": "pipe1"}
        assert summary["pipelines"]["pipe1"]["module"] == "code_for_pipe1"
        assert "pipe2" in summary["pipelines"]
        assert summary["pipelines"]["pipe2"]["cfg"] == {"name": "pipe2"}
        assert summary["pipelines"]["pipe2"]["module"] == "code_for_pipe2"

    # --- Tests for pipeline discovery helpers ---
    def test_list_pipeline_info_and_all_pipelines(self, registry, mock_fs):
        file_infos = [
            {
                "name": "p1",
                "path": posixpath.join(registry._pipelines_dir, "p1.py"),
                "mod_time": "t1",
                "size": "s1",
            },
            {
                "name": "p2",
                "path": posixpath.join(registry._pipelines_dir, "p2.py"),
                "mod_time": "t2",
                "size": "s2",
            },
        ]

        # Mock fs.glob to return the paths for which metadata will be fetched
        mock_fs.glob.side_effect = [[info["path"] for info in file_infos], []]

        # Mock fs.modified and fs.size to return corresponding values
        def mock_modified_side_effect(path):
            if path.endswith("p1.py"):
                return dt.datetime.strptime("2023-01-01 10:00:00", "%Y-%m-%d %H:%M:%S")
            if path.endswith("p2.py"):
                return dt.datetime.strptime("2023-01-02 11:00:00", "%Y-%m-%d %H:%M:%S")
            return dt.datetime.now()

        def mock_size_side_effect(path):
            if path.endswith("p1.py"):
                return 1000
            if path.endswith("p2.py"):
                return 2000
            return 0

        mock_fs.modified.side_effect = mock_modified_side_effect
        mock_fs.size.side_effect = mock_size_side_effect

        result = registry.list_pipeline_info()

        assert len(result) == 2
        assert any(item["name"] == "p1" and item["size"] == "1.0 KB" for item in result)
        assert any(item["name"] == "p2" and item["size"] == "2.0 KB" for item in result)

    def test_list_pipelines_returns_names_only(self, registry, mock_fs):
        mock_fs.glob.side_effect = [
            [posixpath.join(registry._pipelines_dir, "pipe1.py")],
            [posixpath.join(registry._pipelines_dir, "group", "pipe2.py")],
        ]

        assert registry.list_pipelines() == ["group.pipe2", "pipe1"]

    def test_pipelines_property_returns_names_only(self, registry, mock_fs):
        mock_fs.glob.side_effect = [
            [posixpath.join(registry._pipelines_dir, "pipe1.py")],
            [posixpath.join(registry._pipelines_dir, "group", "pipe2.py")],
        ]

        assert registry.pipelines == ["group.pipe2", "pipe1"]

    def test_get_pipeline_ignores_partial_cache_entries(self, registry, mocker):
        partial_cfg = MagicMock(spec=PipelineConfig)
        partial_module = object()
        registry._pipeline_data_cache["demo"] = mocker.MagicMock(
            pipeline=None,
            config=partial_cfg,
            module=partial_module,
        )

        created_pipeline = MagicMock()
        mock_pipeline_cls = mocker.patch("flowerpower.pipeline.pipeline.Pipeline", return_value=created_pipeline)

        result = registry.get_pipeline("demo", project_context=MagicMock(), reload=False)

        assert result is created_pipeline
        mock_pipeline_cls.assert_called_once_with(
            name="demo",
            config=partial_cfg,
            module=partial_module,
            project_context=ANY,
        )

    def test_load_config_reload_invalidates_cached_pipeline(self, registry, mocker):
        old_pipeline = MagicMock()
        old_config = MagicMock(spec=PipelineConfig)
        old_module = object()
        new_config = MagicMock(spec=PipelineConfig)

        registry._pipeline_data_cache["demo"] = mocker.MagicMock(
            pipeline=old_pipeline,
            config=old_config,
            module=old_module,
        )
        registry._config_manager.load_pipeline_config = mocker.MagicMock(
            return_value=new_config
        )

        result = registry.load_config("demo", reload=True)

        assert result is new_config
        assert registry._pipeline_data_cache["demo"].config is new_config
        assert registry._pipeline_data_cache["demo"].module is None
        assert registry._pipeline_data_cache["demo"].pipeline is None

    def test_load_module_reload_invalidates_cached_pipeline(self, registry, mocker):
        old_pipeline = MagicMock()
        old_config = MagicMock(spec=PipelineConfig)
        old_module = object()
        new_module = object()

        registry._pipeline_data_cache["demo"] = mocker.MagicMock(
            pipeline=old_pipeline,
            config=old_config,
            module=old_module,
        )
        mocker.patch(
            "flowerpower.pipeline.module_resolver.load_module",
            return_value=new_module,
        )

        result = registry.load_module("demo", reload=True)

        assert result is new_module
        assert registry._pipeline_data_cache["demo"].config is old_config
        assert registry._pipeline_data_cache["demo"].module is new_module
        assert registry._pipeline_data_cache["demo"].pipeline is None

    def test_load_config_reload_syncs_registry_project_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)
            conf = Path(tmpdir) / "conf"
            conf.mkdir()
            with (conf / "project.yml").open("w") as fh:
                yaml.safe_dump({"name": "demo", "hooks_dir": "hooks"}, fh)
            pipelines = conf / "pipelines"
            pipelines.mkdir()
            with (pipelines / "my_pipeline.yml").open("w") as fh:
                yaml.safe_dump({"run": {"log_level": "INFO"}}, fh)

            manager = PipelineConfigManager(base_dir=tmpdir, fs=fs, storage_options={})
            manager.load_project_config()
            registry = PipelineRegistry(
                project_cfg=manager.project_config,
                fs=fs,
                base_dir=tmpdir,
                config_manager=manager,
            )

            with (conf / "project.yml").open("w") as fh:
                yaml.safe_dump({"name": "updated-demo", "hooks_dir": "custom_hooks"}, fh)

            registry.load_config("my-pipeline", reload=True)

            assert registry.project_cfg.name == "updated-demo"
            assert registry._hooks_dir == "custom_hooks"
            assert registry.get_summary(cfg=False, code=False, project=True)["project"]["name"] == "updated-demo"

    def test_load_config_cached_return_syncs_registry_project_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)
            conf = Path(tmpdir) / "conf"
            conf.mkdir()
            with (conf / "project.yml").open("w") as fh:
                yaml.safe_dump({"name": "demo", "hooks_dir": "hooks"}, fh)
            pipelines = conf / "pipelines"
            pipelines.mkdir()
            with (pipelines / "my_pipeline.yml").open("w") as fh:
                yaml.safe_dump({"run": {"log_level": "INFO"}}, fh)

            manager = PipelineConfigManager(base_dir=tmpdir, fs=fs, storage_options={})
            manager.load_project_config()
            registry = PipelineRegistry(
                project_cfg=manager.project_config,
                fs=fs,
                base_dir=tmpdir,
                config_manager=manager,
            )

            registry.load_config("my-pipeline")

            with (conf / "project.yml").open("w") as fh:
                yaml.safe_dump({"name": "updated-demo", "hooks_dir": "custom_hooks"}, fh)
            manager.load_project_config(reload=True)

            registry.load_config("my-pipeline", reload=False)

            assert registry.project_cfg.name == "updated-demo"
            assert registry._hooks_dir == "custom_hooks"

    def test_get_pipeline_cached_return_syncs_registry_project_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)
            conf = Path(tmpdir) / "conf"
            conf.mkdir()
            with (conf / "project.yml").open("w") as fh:
                yaml.safe_dump({"name": "demo", "hooks_dir": "hooks"}, fh)

            manager = PipelineConfigManager(base_dir=tmpdir, fs=fs, storage_options={})
            manager.load_project_config()
            registry = PipelineRegistry(
                project_cfg=manager.project_config,
                fs=fs,
                base_dir=tmpdir,
                config_manager=manager,
            )
            registry._pipeline_data_cache["demo"] = CachedPipelineData(
                pipeline=MagicMock(),
                config=MagicMock(spec=PipelineConfig),
                module=object(),
            )

            with (conf / "project.yml").open("w") as fh:
                yaml.safe_dump({"name": "updated-demo", "hooks_dir": "custom_hooks"}, fh)
            manager.load_project_config(reload=True)

            registry.get_pipeline("demo", project_context=MagicMock(), reload=False)

            assert registry.project_cfg.name == "updated-demo"
            assert registry._hooks_dir == "custom_hooks"

    def test_list_pipelines_empty_dir(self, registry, mock_fs, mocker):
        mock_fs.ls.return_value = []
        mock_rich_print = mocker.patch("flowerpower.pipeline.presenter.rich.print")

        assert registry.list_pipelines() == []

        registry.show_pipelines()  # Test the print path
        mock_rich_print.assert_called_with("[yellow]No pipelines found[/yellow]")

    # --- Tests for add_hook() method ---
    def test_add_hook_success(self, registry, mock_fs):
        pipeline_name = "hooked_pipeline"
        hook_type = HookType.MQTT_BUILD_CONFIG
        function_name = "custom_mqtt_build_config"

        # Simulate hook file does not exist initially for makedirs check
        mock_fs.exists.return_value = False

        registry.add_hook(
            name=pipeline_name, type=hook_type, function_name=function_name
        )

        expected_hook_file_path = f"hooks/{pipeline_name}/hook.py"
        expected_content = HOOK_TEMPLATE__MQTT_BUILD_CONFIG.format(
            function_name=function_name
        )

        mock_fs.makedirs.assert_called_once_with(
            posixpath.dirname(expected_hook_file_path), exist_ok=True
        )
        mock_fs.open.assert_called_once_with(expected_hook_file_path, "a")

        # Check content written - fs.open is a mock_open instance
        handle = mock_fs.open()
        handle.write.assert_called_once_with(expected_content)

    def test_add_hook_default_function_name(self, registry, mock_fs):
        pipeline_name = "hooked_pipeline_default_func"
        hook_type = HookType.MQTT_BUILD_CONFIG

        mock_fs.exists.return_value = False
        registry.add_hook(name=pipeline_name, type=hook_type)  # No function_name

        default_func_name = hook_type.default_function_name()
        expected_content = HOOK_TEMPLATE__MQTT_BUILD_CONFIG.format(
            function_name=default_func_name
        )

        handle = mock_fs.open()
        handle.write.assert_called_once_with(expected_content)

    def test_add_hook_custom_to_file(self, registry, mock_fs):
        pipeline_name = "hooked_pipeline_custom_file"
        hook_type = HookType.MQTT_BUILD_CONFIG
        custom_file_path = "custom_hooks/my_mqtt.py"

        mock_fs.exists.return_value = False
        registry.add_hook(name=pipeline_name, type=hook_type, to=custom_file_path)

        expected_hook_file_path = f"hooks/{pipeline_name}/{custom_file_path}"
        default_func_name = hook_type.default_function_name()
        expected_content = HOOK_TEMPLATE__MQTT_BUILD_CONFIG.format(
            function_name=default_func_name
        )

        mock_fs.makedirs.assert_called_once_with(
            posixpath.dirname(expected_hook_file_path), exist_ok=True
        )
        mock_fs.open.assert_called_once_with(expected_hook_file_path, "a")
        handle = mock_fs.open()
        handle.write.assert_called_once_with(expected_content)

    def test_add_hook_uses_project_configured_hooks_dir(self, mock_fs):
        registry = PipelineRegistry(
            project_cfg=ProjectConfig(name="demo", hooks_dir="custom_hooks"),
            fs=mock_fs,
        )

        mock_fs.exists.return_value = False

        registry.add_hook(name="hooked_pipeline", type=HookType.MQTT_BUILD_CONFIG)

        mock_fs.open.assert_called_once_with(
            "custom_hooks/hooked_pipeline/hook.py",
            "a",
        )

    def test_add_hook_rejects_path_traversal(self, registry):
        with pytest.raises(SecurityError):
            registry.add_hook(
                name="safe_pipeline",
                type=HookType.MQTT_BUILD_CONFIG,
                to="../escape.py",
            )
