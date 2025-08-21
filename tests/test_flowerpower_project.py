# tests/test_flowerpower_project.py
import unittest
from unittest.mock import Mock, patch

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
            ValueError, match="Pipeline 'name' must be a non-empty string"
        ):
            project.run("")

    def test_run_method_validation_invalid_inputs(self):
        """Test that run() method validates inputs parameter."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        with pytest.raises(TypeError, match="'inputs' must be a dictionary"):
            project.run("test_pipeline", inputs="invalid")

    def test_run_method_validation_invalid_final_vars(self):
        """Test that run() method validates final_vars parameter."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        with pytest.raises(TypeError, match="'final_vars' must be a list of strings"):
            project.run("test_pipeline", final_vars="invalid")

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

        with pytest.raises(TypeError, match="'queue_names' must be a list of strings"):
            project.start_worker(queue_names="invalid")

    def test_start_worker_pool_validation_invalid_num_workers(self):
        """Test that start_worker_pool() validates num_workers parameter."""
        project = FlowerPowerProject(
            pipeline_manager=self.mock_pipeline_manager,
            job_queue_manager=self.mock_job_queue_manager,
        )

        with pytest.raises(
            ValueError, match="'num_workers' must be a positive integer"
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


if __name__ == "__main__":
    unittest.main()
