# tests/test_flowerpower_project.py
import unittest
from unittest.mock import Mock, patch, mock_open

import pytest

from flowerpower.cfg.project import ProjectConfig
from flowerpower.cfg.project.adapter import AdapterConfig
from flowerpower.flowerpower import FlowerPowerProject
from flowerpower.pipeline import PipelineManager
from flowerpower.utils.security import SecurityError


class TestFlowerPowerProject(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for FlowerPowerProject tests."""
        # Create mock pipeline manager
        self.mock_pipeline_manager = Mock(spec=PipelineManager)
        self.mock_pipeline_manager.project_cfg = ProjectConfig(
            name="test_project",
            adapter=AdapterConfig(),
        )
        self.mock_pipeline_manager._base_dir = "/test/path"
        self.mock_pipeline_manager._fs = Mock()
        self.mock_pipeline_manager._storage_options = {}


    def test_flowerpower_project_creation(self):
        """Test FlowerPowerProject creation with managers."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
        )

        self.assertEqual(project.pipeline_manager, self.mock_pipeline_manager)
        self.assertEqual(project.name, "test_project")

    def test_run_method_delegates_to_pipeline_manager(self):
        """Test that run() method properly delegates to pipeline manager."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
        )

        # Mock the pipeline manager's run method
        expected_result = {"output": "test_result"}
        self.mock_pipeline_manager.run.return_value = expected_result

        # Call the project's run method
        result = project.run("test_pipeline", inputs={"x": 1, "y": 2})

        # Verify delegation - check that it was called with name and run_config
        self.mock_pipeline_manager.run.assert_called_once()
        call_args = self.mock_pipeline_manager.run.call_args
        self.assertEqual(call_args[1]['name'], "test_pipeline")
        self.assertIn('run_config', call_args[1])
        self.assertEqual(call_args[1]['run_config'].inputs, {"x": 1, "y": 2})
        self.assertEqual(result, expected_result)

    def test_run_method_validation_empty_name(self):
        """Test that run() method validates pipeline name."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
        )

        with pytest.raises(
            RuntimeError, match="Run failed: Pipeline name must be a non-empty string"
        ):
            project.run("")


    def test_dependency_injection_is_compatibility_noop(self):
        """Dependency injection is no-op because PipelineManager wires context."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
        )

        self.assertIsNone(project._inject_dependencies())
        self.assertFalse(hasattr(self.mock_pipeline_manager, "_project_context"))

    # --- Tests for FlowerPowerProject.new method (renamed from init) ---

    @patch('flowerpower.flowerpower.PipelineManager.new_project')
    def test_new_method_creates_project(self, mock_new_project):
        """FlowerPowerProject.new delegates to PipelineManager.new_project."""
        mock_pm = Mock(spec=PipelineManager)
        mock_pm.project_cfg = ProjectConfig(name="test_project", adapter=AdapterConfig())
        mock_new_project.return_value = mock_pm

        result = FlowerPowerProject.new(name="test_project", base_dir="/tmp/test_path")

        self.assertIsInstance(result, FlowerPowerProject)
        self.assertEqual(result.pipeline_manager, mock_pm)
        self.assertEqual(result.name, "test_project")
        mock_new_project.assert_called_once_with(
            name="test_project",
            base_dir="/tmp/test_path",
            storage_options=None,
            fs=None,
            hooks_dir="hooks",
            log_level=None,
            overwrite=False,
        )

    def test_new_method_rejects_invalid_hooks_dir(self):
        with pytest.raises(SecurityError, match="Directory traversal"):
            FlowerPowerProject.new(
                name="test_project",
                base_dir="/tmp/test_path",
                hooks_dir="../escape",
            )

    @patch('flowerpower.flowerpower.PipelineManager.new_project')
    def test_new_method_with_overwrite_true(self, mock_new_project):
        """FlowerPowerProject.new passes overwrite=True to PipelineManager."""
        mock_pm = Mock(spec=PipelineManager)
        mock_pm.project_cfg = ProjectConfig(name="test_project", adapter=AdapterConfig())
        mock_new_project.return_value = mock_pm

        result = FlowerPowerProject.new(
            name="test_project",
            base_dir="/tmp/test_path",
            overwrite=True,
        )

        self.assertIsInstance(result, FlowerPowerProject)
        mock_new_project.assert_called_once_with(
            name="test_project",
            base_dir="/tmp/test_path",
            storage_options=None,
            fs=None,
            hooks_dir="hooks",
            log_level=None,
            overwrite=True,
        )

    @patch('flowerpower.flowerpower.PipelineManager.new_project')
    def test_new_method_with_overwrite_false_raises_error(self, mock_new_project):
        """FlowerPowerProject.new propagates manager factory FileExistsError."""
        error = FileExistsError(
            "Project already exists at /test/path. "
            "Use overwrite=True to overwrite the existing project."
        )
        mock_new_project.side_effect = error

        with self.assertRaises(FileExistsError) as context:
            FlowerPowerProject.new(name="test_project", base_dir="/test/path")

        self.assertIn("Project already exists at /test/path", str(context.exception))

    # --- Tests for create_project function ---

    @patch('flowerpower.flowerpower.FlowerPowerProject._check_project_exists')
    @patch('flowerpower.flowerpower.FlowerPowerProject.load')
    def test_create_project_existing_project_loads_project(
        self,
        mock_load,
        mock_check_project_exists
    ):
        """Test create_project loads existing project."""
        # Setup mocks
        mock_check_project_exists.return_value = (True, "")
        mock_project = Mock(spec=FlowerPowerProject)
        mock_load.return_value = mock_project
        
        # Import create_project function
        from flowerpower.flowerpower import create_project
        
        # Call create_project
        result = create_project(name="test_project", base_dir="/test/path")
        
        # Verify result
        self.assertEqual(result, mock_project)
        
        # Verify project existence check
        mock_check_project_exists.assert_called_once_with("/test/path", fs=None)
        
        # Verify load was called
        mock_load.assert_called_once_with(
            base_dir="/test/path",
            storage_options=None,
            fs=None
        )

    @patch('flowerpower.flowerpower.FlowerPowerProject._check_project_exists')
    @patch('flowerpower.flowerpower.rich.print')
    def test_create_project_nonexistent_project_raises_error(
        self,
        mock_print,
        mock_check_project_exists
    ):
        """Test create_project raises FileNotFoundError for non-existent project."""
        # Setup mocks
        mock_check_project_exists.return_value = (False, "Project does not exist")
        
        # Import create_project function
        from flowerpower.flowerpower import create_project
        
        # Call create_project and expect FileNotFoundError
        with self.assertRaises(FileNotFoundError) as context:
            create_project(name="test_project", base_dir="/test/path")
        
        # Verify error message
        expected_msg = "Project does not exist. Use `initialize_project()` or `FlowerPowerProject.new()` to create it."
        self.assertIn(expected_msg, str(context.exception))
        
        # Verify print was called with error message
        mock_print.assert_called_once()

    # --- Tests for initialize_project function ---

    @patch('flowerpower.flowerpower.FlowerPowerProject.new')
    def test_initialize_project_calls_new_method(self, mock_new):
        """Test initialize_project calls FlowerPowerProject.new with correct arguments."""
        # Setup mocks
        mock_project = Mock(spec=FlowerPowerProject)
        mock_new.return_value = mock_project
        
        
        # Import initialize_project function
        from flowerpower.flowerpower import initialize_project
        
        # Call initialize_project
        result = initialize_project(
            name="test_project",
            base_dir="/test/path",
            hooks_dir="custom_hooks",
            log_level="DEBUG"
        )
        
        # Verify result
        self.assertEqual(result, mock_project)
        
        # Verify new was called with correct arguments
        mock_new.assert_called_once_with(
            name="test_project",
            base_dir="/test/path",
            storage_options=None,
            fs=None,
            hooks_dir="custom_hooks",
            log_level="DEBUG"
        )
    # --- Tests for FlowerPowerProject.load method ---

    @patch('flowerpower.flowerpower.PipelineManager.load_existing')
    def test_load_method_existing_project(self, mock_load_existing):
        """FlowerPowerProject.load wraps PipelineManager.load_existing."""
        mock_pm = Mock(spec=PipelineManager)
        mock_pm.project_cfg = Mock()
        mock_pm.project_cfg.name = "test_project"
        mock_load_existing.return_value = mock_pm

        result = FlowerPowerProject.load(base_dir="/tmp/test/path")

        self.assertIsInstance(result, FlowerPowerProject)
        self.assertEqual(result.pipeline_manager, mock_pm)
        self.assertEqual(result.name, "test_project")
        mock_load_existing.assert_called_once_with(
            base_dir="/tmp/test/path",
            storage_options=None,
            fs=None,
            log_level=None,
        )

    @patch('flowerpower.flowerpower.PipelineManager.load_existing')
    def test_load_method_nonexistent_project_returns_none(self, mock_load_existing):
        """FlowerPowerProject.load returns None when manager factory returns None."""
        mock_load_existing.return_value = None

        result = FlowerPowerProject.load(base_dir="/tmp/test/path")

        self.assertIsNone(result)
        mock_load_existing.assert_called_once_with(
            base_dir="/tmp/test/path",
            storage_options=None,
            fs=None,
            log_level=None,
        )


    def test_check_project_exists_with_plain_dir_filesystem(self):
        """Test _check_project_exists detects project with plain DirFileSystem."""
        import tempfile
        import os
        from fsspeckit import DirFileSystem
        from flowerpower import settings

        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, settings.CONFIG_DIR), exist_ok=True)
            os.makedirs(os.path.join(td, settings.PIPELINES_DIR), exist_ok=True)
            fs = DirFileSystem(path=td)
            result = FlowerPowerProject._check_project_exists(td, fs=fs)
            self.assertEqual(result, (True, ""))

    def test_check_project_exists_with_cached_dir_filesystem(self):
        """Test _check_project_exists detects project with cached DirFileSystem wrapper."""
        import tempfile
        import os
        from fsspeckit import DirFileSystem
        from fsspeckit.core import MonitoredSimpleCacheFileSystem
        from flowerpower import settings

        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, settings.CONFIG_DIR), exist_ok=True)
            os.makedirs(os.path.join(td, settings.PIPELINES_DIR), exist_ok=True)
            dir_fs = DirFileSystem(path=td)
            cached_fs = MonitoredSimpleCacheFileSystem(fs=dir_fs, cache_storage=td)
            result = FlowerPowerProject._check_project_exists(td, fs=cached_fs)
            self.assertEqual(result, (True, ""))


if __name__ == "__main__":
    unittest.main()
