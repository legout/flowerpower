import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open, call
import datetime as dt
import posixpath # Important for consistent path joining as used in registry.py

from flowerpower.pipeline.registry import PipelineRegistry, HookType
from flowerpower.cfg import ProjectConfig, PipelineConfig # Actual config classes
from flowerpower.fs import AbstractFileSystem # For type hinting mocks
from flowerpower.utils.templates import PIPELINE_PY_TEMPLATE, HOOK_TEMPLATE__MQTT_BUILD_CONFIG

# --- Fixtures ---

@pytest.fixture
def mock_fs(mocker):
    """Fixture for a mocked AbstractFileSystem."""
    fs = mocker.MagicMock(spec=AbstractFileSystem)
    fs.exists = mocker.MagicMock(return_value=True) # Default to True for paths that should exist
    fs.open = mocker.mock_open() # General mock for open
    fs.makedirs = mocker.MagicMock()
    fs.rm = mocker.MagicMock()
    fs.glob = mocker.MagicMock(return_value=[])
    fs.ls = mocker.MagicMock(return_value=[])
    fs.modified = mocker.MagicMock(return_value=dt.datetime.now())
    fs.size = mocker.MagicMock(return_value=1024)
    fs.cat = mocker.MagicMock(return_value=b"") # Returns bytes
    return fs

@pytest.fixture
def mock_project_cfg(mocker):
    """Fixture for a mocked ProjectConfig."""
    cfg = mocker.MagicMock(spec=ProjectConfig)
    cfg.name = "test_project"
    # Other attributes will be set by the registry or can be mocked as needed
    cfg.to_dict = mocker.MagicMock(return_value={"name": "test_project", "version": "0.1"})
    return cfg

@pytest.fixture
def mock_pipeline_cfg_instance(mocker):
    """Fixture for a mocked PipelineConfig instance."""
    cfg_instance = mocker.MagicMock(spec=PipelineConfig)
    cfg_instance.name = "test_pipeline"
    cfg_instance.version = "1.0"
    cfg_instance.to_dict = mocker.MagicMock(return_value={"name": "test_pipeline", "version": "1.0"})
    # Mock the save method as it's called in registry.new
    cfg_instance.save = mocker.MagicMock()
    return cfg_instance

@pytest.fixture
def registry(mock_project_cfg, mock_fs):
    """Fixture for PipelineRegistry instance."""
    # Define cfg_dir and pipelines_dir as they are passed to registry constructor
    cfg_dir = "project/conf"
    pipelines_dir = "project/pipelines"
    return PipelineRegistry(
        project_cfg=mock_project_cfg,
        fs=mock_fs,
        cfg_dir=cfg_dir,
        pipelines_dir=pipelines_dir
    )

# --- Test Cases ---

class TestPipelineRegistry:

    def test_initialization(self, registry, mock_project_cfg, mock_fs):
        assert registry.project_cfg == mock_project_cfg
        assert registry._fs == mock_fs
        assert registry._cfg_dir == "project/conf"
        assert registry._pipelines_dir == "project/pipelines"
        assert registry._console is not None

    # --- Tests for new() method ---
    def test_new_pipeline_success(self, registry, mock_fs, mock_pipeline_cfg_instance, mocker):
        pipeline_name = "my_new_pipeline"
        formatted_name = "my_new_pipeline" # Assumes no . or -
        
        # Mock fs.exists to return False for new files initially
        mock_fs.exists.side_effect = lambda p: not (
            p.endswith(f"{formatted_name}.py") or p.endswith(f"{formatted_name}.yml")
        ) if "project/" in p else True # Keep other paths (like base dirs) existing

        # Patch PipelineConfig class to return our mock instance when called like a constructor
        # or when its .save method is used by an instance.
        # Since registry.new creates a PipelineConfig(name=name) then calls save on it.
        mocker.patch("flowerpower.pipeline.registry.PipelineConfig", return_value=mock_pipeline_cfg_instance)

        registry.new(pipeline_name)

        # Check directory creation for the new files
        expected_pipeline_file = posixpath.join(registry._pipelines_dir, f"{formatted_name}.py")
        expected_cfg_file = posixpath.join(registry._cfg_dir, "pipelines", f"{formatted_name}.yml")
        
        mock_fs.makedirs.assert_any_call(posixpath.dirname(expected_pipeline_file), exist_ok=True)
        mock_fs.makedirs.assert_any_call(posixpath.dirname(expected_cfg_file), exist_ok=True)

        # Check file writes
        mock_fs.open.assert_any_call(expected_pipeline_file, "w")
        
        # Check PipelineConfig instantiation and save
        # PipelineConfig(name=pipeline_name) is called, then new_pipeline_cfg.save(fs=mock_fs)
        from flowerpower.pipeline.registry import PipelineConfig as ActualPipelineConfig # get the class for constructor check
        ActualPipelineConfig.assert_called_once_with(name=pipeline_name)
        mock_pipeline_cfg_instance.save.assert_called_once_with(fs=mock_fs)


    def test_new_pipeline_base_dirs_do_not_exist(self, registry, mock_fs):
        mock_fs.exists.side_effect = lambda p: False # Make all paths appear non-existent

        with pytest.raises(ValueError, match="Configuration path project/conf does not exist."):
            registry.new("test_pipe")
        
        # Reset side_effect if needed for other tests or make it more specific
        mock_fs.exists.side_effect = None 
        mock_fs.exists.return_value = True # Restore default for other tests

    def test_new_pipeline_already_exists_no_overwrite(self, registry, mock_fs):
        pipeline_name = "existing_pipe"
        # fs.exists returns True by default from fixture, so files will appear to exist
        
        with pytest.raises(ValueError, match=f"Pipeline test_project.{pipeline_name} already exists."):
            registry.new(pipeline_name)

    def test_new_pipeline_already_exists_with_overwrite(self, registry, mock_fs, mock_pipeline_cfg_instance, mocker):
        pipeline_name = "existing_pipe"
        formatted_name = "existing_pipe"
        
        # fs.exists returns True by default, simulating files exist
        mocker.patch("flowerpower.pipeline.registry.PipelineConfig", return_value=mock_pipeline_cfg_instance)

        registry.new(pipeline_name, overwrite=True)

        expected_pipeline_file = posixpath.join(registry._pipelines_dir, f"{formatted_name}.py")
        expected_cfg_file = posixpath.join(registry._cfg_dir, "pipelines", f"{formatted_name}.yml")

        # Check that rm was called for existing files
        mock_fs.rm.assert_any_call(expected_pipeline_file)
        mock_fs.rm.assert_any_call(expected_cfg_file)
        
        # And then files were written
        mock_fs.open.assert_any_call(expected_pipeline_file, "w")
        mock_pipeline_cfg_instance.save.assert_called_once_with(fs=mock_fs)

    # --- Tests for delete() method ---
    def test_delete_pipeline_success_cfg_and_module(self, registry, mock_fs):
        pipeline_name = "pipe_to_delete"
        # fs.exists returns True by default
        
        registry.delete(pipeline_name, cfg=True, module=True)
        
        expected_cfg_path = posixpath.join(registry._cfg_dir, "pipelines", f"{pipeline_name}.yml")
        expected_py_path = posixpath.join(registry._pipelines_dir, f"{pipeline_name}.py")
        
        mock_fs.rm.assert_any_call(expected_cfg_path)
        mock_fs.rm.assert_any_call(expected_py_path)

    def test_delete_pipeline_only_cfg(self, registry, mock_fs):
        pipeline_name = "pipe_to_delete_cfg"
        registry.delete(pipeline_name, cfg=True, module=False)
        
        expected_cfg_path = posixpath.join(registry._cfg_dir, "pipelines", f"{pipeline_name}.yml")
        expected_py_path = posixpath.join(registry._pipelines_dir, f"{pipeline_name}.py")
        
        mock_fs.rm.assert_called_once_with(expected_cfg_path)
        # Ensure module was not deleted
        calls = [call(expected_py_path)]
        mock_fs.rm.assert_has_calls([call(expected_cfg_path)], any_order=True)
        for c in calls: # Check that expected_py_path was not called with rm
            assert c not in mock_fs.rm.call_args_list


    def test_delete_pipeline_files_not_found(self, registry, mock_fs, mocker):
        pipeline_name = "non_existent_pipe"
        mock_fs.exists.return_value = False # Simulate files don't exist
        
        # Mock logger to check warnings
        mock_logger_warning = mocker.patch("flowerpower.pipeline.registry.logger.warning")
        
        registry.delete(pipeline_name, cfg=True, module=True)
        
        mock_fs.rm.assert_not_called()
        
        expected_cfg_path = posixpath.join(registry._cfg_dir, "pipelines", f"{pipeline_name}.yml")
        expected_py_path = posixpath.join(registry._pipelines_dir, f"{pipeline_name}.py")
        
        mock_logger_warning.assert_any_call(f"Config file not found, skipping deletion: {expected_cfg_path}")
        mock_logger_warning.assert_any_call(f"Module file not found, skipping deletion: {expected_py_path}")
        mock_logger_warning.assert_any_call(f"No files found or specified for deletion for pipeline '{pipeline_name}'.")


    # --- Tests for _get_files() and _get_names() ---
    def test_get_files_and_names(self, registry, mock_fs):
        mock_fs.glob.return_value = [
            posixpath.join(registry._pipelines_dir, "pipe1.py"),
            posixpath.join(registry._pipelines_dir, "pipe2.py")
        ]
        
        files = registry._get_files()
        assert len(files) == 2
        assert posixpath.join(registry._pipelines_dir, "pipe1.py") in files
        
        names = registry._get_names()
        assert sorted(names) == sorted(["pipe1", "pipe2"])

    def test_get_files_fs_error(self, registry, mock_fs, mocker):
        mock_fs.glob.side_effect = Exception("FS error")
        mock_logger_error = mocker.patch("flowerpower.pipeline.registry.logger.error")
        
        assert registry._get_files() == []
        mock_logger_error.assert_called_once()


    # --- Tests for get_summary() method ---
    @patch("flowerpower.pipeline.registry.PipelineConfig") # Mock the class itself
    def test_get_summary_single_pipeline(self, MockPipelineConfig, registry, mock_fs, mock_project_cfg, mock_pipeline_cfg_instance):
        pipeline_name = "summary_pipe"
        
        # Setup mocks for this test
        mock_fs.glob.return_value = [posixpath.join(registry._pipelines_dir, f"{pipeline_name}.py")] # for _get_names
        MockPipelineConfig.load.return_value = mock_pipeline_cfg_instance # For PipelineConfig.load call
        mock_fs.cat.return_value = b"pipeline_code_content"
        mock_project_cfg.to_dict.return_value = {"project_data": "value"}

        summary = registry.get_summary(name=pipeline_name, cfg=True, code=True, project=True)

        assert "project" in summary
        assert summary["project"] == {"project_data": "value"}
        assert pipeline_name in summary["pipelines"]
        assert summary["pipelines"][pipeline_name]["cfg"] == mock_pipeline_cfg_instance.to_dict()
        assert summary["pipelines"][pipeline_name]["module"] == "pipeline_code_content"
        
        MockPipelineConfig.load.assert_called_once_with(name=pipeline_name, fs=mock_fs)
        mock_fs.cat.assert_called_once_with(posixpath.join(registry._pipelines_dir, f"{pipeline_name}.py"))

    @patch("flowerpower.pipeline.registry.PipelineConfig")
    def test_get_summary_all_pipelines(self, MockPipelineConfig, registry, mock_fs, mock_project_cfg, mock_pipeline_cfg_instance):
        # Similar to single, but _get_names will return multiple, and loop will run
        mock_fs.glob.return_value = [
            posixpath.join(registry._pipelines_dir, "pipe1.py"),
            posixpath.join(registry._pipelines_dir, "pipe2.py")
        ]
        # Make load return different cfgs if needed, or same for simplicity if only names matter for distinction
        mock_config1 = MagicMock(spec=PipelineConfig); mock_config1.name="pipe1"; mock_config1.to_dict.return_value={"name":"pipe1"}
        mock_config2 = MagicMock(spec=PipelineConfig); mock_config2.name="pipe2"; mock_config2.to_dict.return_value={"name":"pipe2"}
        MockPipelineConfig.load.side_effect = lambda name, fs: mock_config1 if name == "pipe1" else mock_config2
        
        mock_fs.cat.side_effect = lambda path: b"code_for_" + bytes(posixpath.basename(path).split('.')[0], 'utf-8')

        summary = registry.get_summary(cfg=True, code=True, project=False) # No project details

        assert "project" not in summary
        assert "pipe1" in summary["pipelines"]
        assert summary["pipelines"]["pipe1"]["cfg"] == {"name": "pipe1"}
        assert summary["pipelines"]["pipe1"]["module"] == "code_for_pipe1"
        assert "pipe2" in summary["pipelines"]
        assert summary["pipelines"]["pipe2"]["cfg"] == {"name": "pipe2"}
        assert summary["pipelines"]["pipe2"]["module"] == "code_for_pipe2"

    # --- Tests for _all_pipelines() and list_pipelines() ---
    def test_list_pipelines_and_all_pipelines(self, registry, mock_fs):
        # _all_pipelines(show=False) is what list_pipelines calls
        file_infos = [
            {"name": "p1", "path": posixpath.join(registry._pipelines_dir, "p1.py"), "mod_time": "t1", "size": "s1"},
            {"name": "p2", "path": posixpath.join(registry._pipelines_dir, "p2.py"), "mod_time": "t2", "size": "s2"},
        ]
        
        # Mock fs.ls to return the paths for which metadata will be fetched
        mock_fs.ls.return_value = [info["path"] for info in file_infos]
        
        # Mock fs.modified and fs.size to return corresponding values
        def mock_modified_side_effect(path):
            if path.endswith("p1.py"): return dt.datetime.strptime("2023-01-01 10:00:00", "%Y-%m-%d %H:%M:%S")
            if path.endswith("p2.py"): return dt.datetime.strptime("2023-01-02 11:00:00", "%Y-%m-%d %H:%M:%S")
            return dt.datetime.now()
        
        def mock_size_side_effect(path):
            if path.endswith("p1.py"): return 1000
            if path.endswith("p2.py"): return 2000
            return 0

        mock_fs.modified.side_effect = mock_modified_side_effect
        mock_fs.size.side_effect = mock_size_side_effect

        result = registry.list_pipelines() # Calls _all_pipelines(show=False)
        
        assert len(result) == 2
        assert any(item["name"] == "p1" and item["size"] == "1.0 KB" for item in result)
        assert any(item["name"] == "p2" and item["size"] == "2.0 KB" for item in result)

    def test_list_pipelines_empty_dir(self, registry, mock_fs, mocker):
        mock_fs.ls.return_value = []
        mock_rich_print = mocker.patch("flowerpower.pipeline.registry.rich.print")
        
        # _all_pipelines(show=True) prints, show=False returns list
        assert registry.list_pipelines() == [] # Calls _all_pipelines(show=False)
        
        registry._all_pipelines(show=True) # Test the print path
        mock_rich_print.assert_called_with("[yellow]No pipelines found[/yellow]")


    # --- Tests for add_hook() method ---
    def test_add_hook_success(self, registry, mock_fs):
        pipeline_name = "hooked_pipeline"
        hook_type = HookType.MQTT_BUILD_CONFIG
        function_name = "custom_mqtt_build_config"
        
        # Simulate hook file does not exist initially for makedirs check
        mock_fs.exists.return_value = False
        
        registry.add_hook(name=pipeline_name, type=hook_type, function_name=function_name)
        
        expected_hook_file_path = f"hooks/{pipeline_name}/hook.py"
        expected_content = HOOK_TEMPLATE__MQTT_BUILD_CONFIG.format(function_name=function_name)
        
        mock_fs.makedirs.assert_called_once_with(posixpath.dirname(expected_hook_file_path), exist_ok=True)
        mock_fs.open.assert_called_once_with(expected_hook_file_path, "a")
        
        # Check content written - fs.open is a mock_open instance
        handle = mock_fs.open()
        handle.write.assert_called_once_with(expected_content)

    def test_add_hook_default_function_name(self, registry, mock_fs):
        pipeline_name = "hooked_pipeline_default_func"
        hook_type = HookType.MQTT_BUILD_CONFIG
        
        mock_fs.exists.return_value = False
        registry.add_hook(name=pipeline_name, type=hook_type) # No function_name
        
        expected_hook_file_path = f"hooks/{pipeline_name}/hook.py"
        default_func_name = hook_type.default_function_name()
        expected_content = HOOK_TEMPLATE__MQTT_BUILD_CONFIG.format(function_name=default_func_name)
        
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
        expected_content = HOOK_TEMPLATE__MQTT_BUILD_CONFIG.format(function_name=default_func_name)
        
        mock_fs.makedirs.assert_called_once_with(posixpath.dirname(expected_hook_file_path), exist_ok=True)
        mock_fs.open.assert_called_once_with(expected_hook_file_path, "a")
        handle = mock_fs.open()
        handle.write.assert_called_once_with(expected_content)

```
