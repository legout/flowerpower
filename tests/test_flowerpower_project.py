# tests/test_flowerpower_project.py
import unittest
from unittest.mock import Mock, patch, mock_open

import pytest

from flowerpower.cfg.project import ProjectConfig
from flowerpower.cfg.project.adapter import AdapterConfig
from flowerpower.cfg.project.job_queue import JobQueueConfig
from flowerpower.flowerpower import FlowerPowerProject
from flowerpower.job_queue import JobQueueManager
from flowerpower.pipeline import PipelineManager


class TestFlowerPowerProject(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for FlowerPowerProject tests."""
        # Create mock pipeline manager
        self.mock_pipeline_manager = Mock(spec=PipelineManager)
        self.mock_pipeline_manager.project_cfg = ProjectConfig(
            name="test_project",
            job_queue=JobQueueConfig(type="rq", backend={"type": "redis"}),
            adapter=AdapterConfig(),
        )
        self.mock_pipeline_manager._base_dir = "/test/path"
        self.mock_pipeline_manager._fs = Mock()
        self.mock_pipeline_manager._storage_options = {}

        # Create mock job queue manager
        self.mock_job_queue_manager = Mock()
        self.mock_job_queue_manager.cfg = Mock()
        self.mock_job_queue_manager.cfg.type = "rq"
        self.mock_job_queue_manager.cfg.backend = {"type": "redis"}

    def test_flowerpower_project_creation(self):
        """Test FlowerPowerProject creation with managers."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        self.assertEqual(project.pipeline_manager, self.mock_pipeline_manager)
        self.assertEqual(project.job_queue_manager, self.mock_job_queue_manager)
        self.assertEqual(project.name, "test_project")
        self.assertEqual(project.job_queue_type, "rq")

    def test_flowerpower_project_creation_no_job_queue(self):
        """Test FlowerPowerProject creation without job queue manager."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager, job_queue_manager=None
        )

        self.assertEqual(project.pipeline_manager, self.mock_pipeline_manager)
        self.assertIsNone(project.job_queue_manager)
        self.assertEqual(project.name, "test_project")
        self.assertIsNone(project.job_queue_type)

    def test_run_method_delegates_to_pipeline_manager(self):
        """Test that run() method properly delegates to pipeline manager."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        # Mock the pipeline manager's run method
        expected_result = {"output": "test_result"}
        self.mock_pipeline_manager.run.return_value = expected_result

        # Call the project's run method
        result = project.run("test_pipeline", inputs={"x": 1, "y": 2})

        # Verify delegation
        self.mock_pipeline_manager.run.assert_called_once_with(
            name="test_pipeline",
            inputs={"x": 1, "y": 2},
            final_vars=None,
            config=None,
            cache=None,
            executor_cfg=None,
            with_adapter_cfg=None,
            pipeline_adapter_cfg=None,
            project_adapter_cfg=None,
            adapter=None,
            reload=False,
            log_level=None,
            max_retries=None,
            retry_delay=None,
            jitter_factor=None,
            retry_exceptions=None,
            on_success=None,
            on_failure=None,
        )
        self.assertEqual(result, expected_result)

    def test_run_method_validation_empty_name(self):
        """Test that run() method validates pipeline name."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        with pytest.raises(
            RuntimeError, match="Run failed: Pipeline 'name' must be a non-empty string"
        ):
            project.run("")


    def test_enqueue_method_delegates_to_job_queue_manager(self):
        """Test that enqueue() method properly delegates to job queue manager."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        # Mock the job queue manager's enqueue method
        expected_job_id = "job_123"
        self.mock_job_queue_manager.enqueue_pipeline.return_value = expected_job_id

        # Call the project's enqueue method
        job_id = project.enqueue("test_pipeline", inputs={"x": 1, "y": 2})

        # Verify delegation
        self.mock_job_queue_manager.enqueue_pipeline.assert_called_once_with(
            name="test_pipeline", project_context=project, inputs={"x": 1, "y": 2}
        )
        self.assertEqual(job_id, expected_job_id)

    def test_enqueue_method_no_job_queue_manager(self):
        """Test that enqueue() method raises error when no job queue manager."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager, job_queue_manager=None
        )

        with pytest.raises(RuntimeError, match="Job queue manager is not configured"):
            project.enqueue("test_pipeline")

    def test_schedule_method_delegates_to_job_queue_manager(self):
        """Test that schedule() method properly delegates to job queue manager."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        # Mock the job queue manager's schedule method
        expected_schedule_id = "schedule_123"
        self.mock_job_queue_manager.schedule_pipeline.return_value = (
            expected_schedule_id
        )

        # Call the project's schedule method
        schedule_id = project.schedule("test_pipeline", cron="0 9 * * *")

        # Verify delegation
        self.mock_job_queue_manager.schedule_pipeline.assert_called_once_with(
            name="test_pipeline", project_context=project, cron="0 9 * * *"
        )
        self.assertEqual(schedule_id, expected_schedule_id)

    def test_start_worker_method_delegates_to_job_queue_manager(self):
        """Test that start_worker() method properly delegates to job queue manager."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        # Call the project's start_worker method
        project.start_worker(background=True, queue_names=["high_priority"])

        # Verify delegation
        self.mock_job_queue_manager.start_worker.assert_called_once_with(
            background=True, queue_names=["high_priority"], with_scheduler=True
        )

    def test_start_worker_validation_invalid_queue_names(self):
        """Test that start_worker() validates queue_names parameter."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        with pytest.raises(RuntimeError, match="Start Worker failed: 'queue_names' must be a list of strings"):
            project.start_worker(queue_names="invalid")

    def test_start_worker_pool_validation_invalid_num_workers(self):
        """Test that start_worker_pool() validates num_workers parameter."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        with pytest.raises(
            RuntimeError, match="Start Worker Pool failed: 'num_workers' must be a positive integer"
        ):
            project.start_worker_pool(num_workers=0)

    def test_dependency_injection(self):
        """Test that dependency injection works correctly."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
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
    @patch('flowerpower.flowerpower.JobQueueManager')
    @patch('flowerpower.flowerpower.rich.print')
    @patch('flowerpower.flowerpower.os.makedirs')
    def test_new_method_creates_project(
        self,
        mock_os_makedirs,
        mock_print,
        mock_job_queue_manager,
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
        
        mock_jm = Mock()
        mock_job_queue_manager.return_value = mock_jm
        
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
                job_queue_type="rq",
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
                log_level="INFO"
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
                    with patch('flowerpower.flowerpower.JobQueueManager') as mock_job_queue_manager:
                        mock_cfg = Mock()
                        mock_project_config.load.return_value = mock_cfg
                        
                        mock_pm = Mock()
                        mock_pipeline_manager.return_value = mock_pm
                        
                        mock_jm = Mock()
                        mock_job_queue_manager.return_value = mock_jm
                        
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
                        mock_fs.rmdir.assert_any_call("conf", recursive=True)
                        mock_fs.rmdir.assert_any_call("pipelines", recursive=True)
                        mock_fs.rmdir.assert_any_call("hooks", recursive=True)
                        mock_fs.rm.assert_called_once_with("README.md")

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
            job_queue_type="rq",
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
            job_queue_type="rq",
            hooks_dir="custom_hooks",
            log_level="DEBUG"
        )

    # --- Tests for FlowerPowerProject.load method ---

    @patch('flowerpower.flowerpower.filesystem')
    @patch('flowerpower.flowerpower.Path')
    @patch('flowerpower.flowerpower.PipelineManager')
    @patch('flowerpower.flowerpower.JobQueueManager')
    @patch('flowerpower.flowerpower.rich.print')
    @patch('flowerpower.flowerpower.os.makedirs')
    def test_load_method_existing_project(
        self,
        mock_os_makedirs,
        mock_print,
        mock_job_queue_manager,
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
        
        mock_jm = Mock()
        mock_job_queue_manager.return_value = mock_jm
        
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
            self.assertEqual(result.job_queue_manager, mock_jm)
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
            mock_job_queue_manager.assert_called_once_with(
                name="test_project_job_queue",
                base_dir="/tmp/test/path",
                storage_options={},
                fs=mock_fs
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
