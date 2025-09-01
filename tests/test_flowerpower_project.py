# tests/test_flowerpower_project.py
import unittest
from unittest.mock import Mock, patch, mock_open

import pytest

from flowerpower.cfg.project import ProjectConfig
from flowerpower.cfg.project.adapter import AdapterConfig
from flowerpower.flowerpower import FlowerPowerProject
from flowerpower.pipeline import PipelineManager


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
            RuntimeError, match="Run failed: Pipeline 'name' must be a non-empty string"
        ):
            project.run("")


    def test_dependency_injection(self):
        """Test that dependency injection works correctly."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
        )

        # Call dependency injection
        project._inject_dependencies()

        # Verify project context was set
        self.assertEqual(self.mock_pipeline_manager._project_context, project)

    # --- Tests for FlowerPowerProject.new method (renamed from init) ---

    @patch('flowerpower.flowerpower.filesystem')
    @patch('flowerpower.flowerpower.Path')
    @patch('flowerpower.flowerpower.ProjectConfig')
    @patch('flowerpower.flowerpower.PipelineManager')
    @patch('flowerpower.flowerpower.rich.print')
    @patch('flowerpower.flowerpower.os.makedirs')
    def test_new_method_creates_project(
        self,
        mock_os_makedirs,
        mock_print,
        mock_pipeline_manager,
        mock_project_config,
        mock_path,
        mock_filesystem
    ):
        """Test FlowerPowerProject.new creates a new project successfully."""
        # Setup mocks
        mock_fs = Mock()
        mock_filesystem.return_value = mock_fs
        mock_fs.exists.return_value = False  # Project doesn't exist
        
        # Mock file open with context manager support
        mock_fs.open = mock_open()
        
        mock_cfg = Mock()
        mock_project_config.load.return_value = mock_cfg
        
        mock_pm = Mock()
        mock_pipeline_manager.return_value = mock_pm
        
        
        mock_path_instance = Mock()
        mock_path_instance.name = "test_project"
        mock_path_instance.cwd.return_value = mock_path_instance
        mock_path_instance.parent = Mock()
        mock_path_instance.parent.__str__ = Mock(return_value="/parent")
        mock_path.return_value = mock_path_instance
        
        # Mock the load method to return a project instance
        with patch.object(FlowerPowerProject, 'load') as mock_load:
            mock_project = Mock(spec=FlowerPowerProject)
            mock_load.return_value = mock_project
            
            # Call the new method
            result = FlowerPowerProject.new(name="test_project", base_dir="/tmp/test_path")
            
            # Verify result
            self.assertEqual(result, mock_project)
            
            # Verify filesystem operations
            mock_fs.makedirs.assert_any_call("conf/pipelines", exist_ok=True)
            mock_fs.makedirs.assert_any_call("pipelines", exist_ok=True)
            mock_fs.makedirs.assert_any_call("hooks", exist_ok=True)
            
            # Verify config operations
            mock_project_config.load.assert_called_once_with(
                name="test_project",
                fs=mock_fs
            )
            mock_cfg.save.assert_called_once_with(fs=mock_fs)
            
            # Verify file creation
            mock_fs.open.assert_called_once_with("README.md", "w")
            
            # Verify load was called
            mock_load.assert_called_once_with(
                base_dir="/tmp/test_path",
                storage_options={},
                fs=mock_fs,
                log_level=None
            )
    @patch('flowerpower.flowerpower.filesystem')
    @patch('flowerpower.flowerpower.Path')
    @patch('flowerpower.flowerpower.rich.print')
    @patch('flowerpower.flowerpower.os.makedirs')
    def test_new_method_with_overwrite_true(
        self,
        mock_os_makedirs,
        mock_print,
        mock_path,
        mock_filesystem
    ):
        """Test FlowerPowerProject.new with overwrite=True removes existing project."""
        # Setup mocks
        mock_fs = Mock()
        mock_filesystem.return_value = mock_fs
        mock_fs.exists.return_value = True  # Project exists
        
        # Mock file open with context manager support
        mock_fs.open = mock_open()
        
        mock_path_instance = Mock()
        mock_path_instance.name = "test_project"
        mock_path_instance.cwd.return_value = mock_path_instance
        mock_path_instance.parent = Mock()
        mock_path_instance.parent.__str__ = Mock(return_value="/parent")
        mock_path.return_value = mock_path_instance
        
        # Mock the load method to return a project instance
        with patch.object(FlowerPowerProject, 'load') as mock_load:
            with patch('flowerpower.flowerpower.ProjectConfig') as mock_project_config:
                with patch('flowerpower.flowerpower.PipelineManager') as mock_pipeline_manager:
                    mock_cfg = Mock()
                    mock_project_config.load.return_value = mock_cfg
                    
                    mock_pm = Mock()
                    mock_pipeline_manager.return_value = mock_pm
                    
                    mock_project = Mock(spec=FlowerPowerProject)
                    mock_load.return_value = mock_project
                    
                    # Call the new method with overwrite=True
                    result = FlowerPowerProject.new(
                        name="test_project",
                        base_dir="/tmp/test_path",
                        overwrite=True
                    )
                    
                    # Verify result
                    self.assertEqual(result, mock_project)
                    
                    # Verify existing project was removed
                    mock_fs.rm.assert_any_call("conf", recursive=True)
                    mock_fs.rm.assert_any_call("pipelines", recursive=True)
                    mock_fs.rm.assert_any_call("hooks", recursive=True)
                    mock_fs.rm.assert_any_call("README.md")

    @patch('flowerpower.flowerpower.filesystem')
    @patch('flowerpower.flowerpower.Path')
    @patch('flowerpower.flowerpower.rich.print')
    def test_new_method_with_overwrite_false_raises_error(
        self,
        mock_print,
        mock_path,
        mock_filesystem
    ):
        """Test FlowerPowerProject.new with overwrite=False raises FileExistsError."""
        # Setup mocks
        mock_fs = Mock()
        mock_filesystem.return_value = mock_fs
        mock_fs.exists.return_value = True  # Project exists
        
        mock_path_instance = Mock()
        mock_path_instance.name = "test_project"
        mock_path_instance.cwd.return_value = mock_path_instance
        mock_path_instance.parent = Mock()
        mock_path_instance.parent.__str__ = Mock(return_value="/parent")
        mock_path.return_value = mock_path_instance
        
        # Call the new method with overwrite=False (default)
        with self.assertRaises(FileExistsError) as context:
            FlowerPowerProject.new(name="test_project", base_dir="/test/path")
        
        # Verify error message
        expected_msg = "Project already exists at /test/path. Use overwrite=True to overwrite the existing project."
        self.assertIn(expected_msg, str(context.exception))
        
        # Verify print was called with error message
        mock_print.assert_called_once()

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
            storage_options={},
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
            storage_options={},
            fs=None,
            hooks_dir="custom_hooks",
            log_level="DEBUG"
        )
    # --- Tests for FlowerPowerProject.load method ---

    @patch('flowerpower.flowerpower.filesystem')
    @patch('flowerpower.flowerpower.Path')
    @patch('flowerpower.flowerpower.PipelineManager')
    @patch('flowerpower.flowerpower.rich.print')
    @patch('flowerpower.flowerpower.os.makedirs')
    def test_load_method_existing_project(
        self,
        mock_os_makedirs,
        mock_print,
        mock_pipeline_manager,
        mock_path,
        mock_filesystem
    ):
        """Test FlowerPowerProject.load loads existing project successfully."""
        # Setup mocks
        mock_fs = Mock()
        mock_filesystem.return_value = mock_fs
        
        mock_pm = Mock()
        mock_pm.project_cfg = Mock()
        mock_pm.project_cfg.name = "test_project"
        mock_pipeline_manager.return_value = mock_pm
        
        mock_path_instance = Mock()
        mock_path_instance.cwd.return_value = "/current/dir"
        mock_path.return_value = mock_path_instance
        
        # Mock _check_project_exists to return True
        with patch.object(FlowerPowerProject, '_check_project_exists') as mock_check:
            mock_check.return_value = (True, "")
            
            # Call the load method
            result = FlowerPowerProject.load(base_dir="/tmp/test/path")
            
            # Verify result is a FlowerPowerProject instance
            self.assertIsInstance(result, FlowerPowerProject)
            self.assertEqual(result.pipeline_manager, mock_pm)
            self.assertEqual(result.name, "test_project")
            
            # Verify project existence check
            mock_check.assert_called_once_with("/tmp/test/path", mock_fs)
            
            # Verify manager creation
            mock_pipeline_manager.assert_called_once_with(
                base_dir="/tmp/test/path",
                storage_options={},
                fs=mock_fs,
                log_level=None
            )

    @patch('flowerpower.flowerpower.filesystem')
    @patch('flowerpower.flowerpower.Path')
    @patch('flowerpower.flowerpower.rich.print')
    @patch('flowerpower.flowerpower.os.makedirs')
    def test_load_method_nonexistent_project_returns_none(
        self,
        mock_os_makedirs,
        mock_print,
        mock_path,
        mock_filesystem
    ):
        """Test FlowerPowerProject.load returns None for non-existent project."""
        # Setup mocks
        mock_fs = Mock()
        mock_filesystem.return_value = mock_fs
        
        mock_path_instance = Mock()
        mock_path_instance.cwd.return_value = "/current/dir"
        mock_path.return_value = mock_path_instance
        
        # Mock _check_project_exists to return False
        with patch.object(FlowerPowerProject, '_check_project_exists') as mock_check:
            mock_check.return_value = (False, "Project does not exist")
            
            # Call the load method
            result = FlowerPowerProject.load(base_dir="/tmp/test/path")
            
            # Verify result is None
            self.assertIsNone(result)
            
            # Verify project existence check
            mock_check.assert_called_once_with("/tmp/test/path", mock_fs)
            
            # Verify print was called with error message
            mock_print.assert_called_once()


if __name__ == "__main__":
    unittest.main()
