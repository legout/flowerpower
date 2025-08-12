# tests/pipeline/test_runner.py
import unittest
from unittest.mock import MagicMock

from flowerpower.cfg import PipelineConfig, ProjectConfig
from flowerpower.cfg.pipeline import (ExecutorConfig, PipelineAdapterConfig,
                                      PipelineRunConfig, WithAdapterConfig)
from flowerpower.cfg.project import ProjectAdapterConfig
from flowerpower.pipeline.runner import PipelineRunner, run_pipeline
from tests.pipelines.test_pipeline_module import reset_flaky_attempts

# It's good practice to place test modules in a way that mimics the main structure if possible,
# or ensure sys.path is handled correctly for Hamilton to find the module.
# For this test, we'll assume Hamilton can find 'tests.pipelines.test_pipeline_module'


class TestPipelineRunner(unittest.TestCase):
    def setUp(self):
        # Mock ProjectConfig
        self.mock_project_cfg = ProjectConfig(
            name="test_project",
            # Define other necessary fields for ProjectConfig, potentially with MagicMock for complex ones
            # For example, if adapter configurations are accessed:
            adapter=ProjectAdapterConfig(),  # Use default or mock further if needed
        )

        # Mock PipelineConfig
        self.mock_pipeline_cfg = PipelineConfig(
            name="tests.pipelines.test_pipeline_module",  # This is crucial for loading the test module
            # Define other necessary fields for PipelineConfig
            run=PipelineRunConfig(  # Assuming default run config is okay, or mock as needed
                inputs={},
                final_vars=[],
                executor=ExecutorConfig(
                    type="synchronous"
                ),  # Default to synchronous for basic tests
                with_adapter=WithAdapterConfig(),  # Default adapter settings
            ),
            adapter=PipelineAdapterConfig(),  # Default or mock further
        )

        self.runner = PipelineRunner(
            project_cfg=self.mock_project_cfg, pipeline_cfg=self.mock_pipeline_cfg
        )

    def test_initialization(self):
        # A simple test to ensure the runner initializes
        self.assertIsNotNone(self.runner)
        self.assertEqual(self.runner.name, "tests.pipelines.test_pipeline_module")

    def test_basic_pipeline_execution(self):
        results = self.runner.run(final_vars=["output_value", "another_output"])
        self.assertIn("output_value", results)
        self.assertIn("another_output", results)
        self.assertEqual(results["output_value"], 25)  # (10 * 2) + 5
        self.assertEqual(results["another_output"], {"input": 10, "intermediate": 20})

    def test_pipeline_execution_with_threadpool_executor(self):
        executor_config = ExecutorConfig(type="threadpool", max_workers=2)
        results = self.runner.run(
            final_vars=["output_value"], executor_cfg=executor_config
        )
        self.assertEqual(results["output_value"], 25)

    def test_run_pipeline_convenience_function(self):
        # For the convenience function, we might need to pass the module path directly
        # if it doesn't pick it up from pipeline_cfg.name in the same way.
        # However, run_pipeline should internally create a PipelineRunner
        # which should respect the pipeline_cfg.name for module loading.
        results = run_pipeline(
            project_cfg=self.mock_project_cfg,
            pipeline_cfg=self.mock_pipeline_cfg,
            final_vars=["output_value"],
            # Inputs and other params can be specified if needed
        )
        self.assertEqual(results["output_value"], 25)

    def test_pipeline_execution_with_adapters(self):
        adapter_types = ["hamilton_tracker", "mlflow", "opentelemetry", "progressbar"]
        for adapter_type in adapter_types:
            with self.subTest(adapter_type=adapter_type):
                adapter_config_dict = {adapter_type: True}
                adapter_config = WithAdapterConfig(**adapter_config_dict)
                # We rely on the PipelineRunner's internal checks for library availability
                # and log warnings if they are not present.
                # A more robust test might mock importlib.util.find_spec or capture logs.
                try:
                    results = self.runner.run(
                        with_adapter_cfg=adapter_config, final_vars=["output_value"]
                    )
                    self.assertEqual(results["output_value"], 25)
                except Exception as e:
                    # This test primarily ensures that enabling adapters doesn't crash the runner.
                    # Specific adapter functionality would need more targeted tests with mocks.
                    self.fail(
                        f"Pipeline run failed with adapter {adapter_type} enabled: {e}"
                    )

    def test_pipeline_execution_with_caching(self):
        # Hamilton's default cache is in-memory. This test ensures it runs.
        # To truly test caching effectiveness, one might mock time.time,
        # check logs, or use functions with side effects.
        results = self.runner.run(final_vars=["output_value"], cache=True)
        self.assertEqual(results["output_value"], 25)
        # Potentially, run again and verify a log message or mocked function call
        # For now, just ensuring it doesn't break.

    def test_retry_mechanism(self):
        # Test with a function that succeeds after a few retries
        reset_flaky_attempts()  # Reset counter in the test module
        pipeline_cfg_flaky = self.mock_pipeline_cfg.model_copy(deep=True)
        # pipeline_cfg_flaky.name remains "tests.pipelines.test_pipeline_module"

        results_flaky = self.runner.run(
            pipeline_cfg=pipeline_cfg_flaky,  # Runner uses this to load the module
            final_vars=["output_from_flaky"],
            max_retries=3,
            retry_delay=0.01,
            retry_exceptions=["ValueError"],  # As strings
        )
        self.assertEqual(results_flaky["output_from_flaky"], 15)  # 10 (input_data) + 5

        # Test with a function that always fails
        pipeline_cfg_always_fails = self.mock_pipeline_cfg.model_copy(deep=True)

        with self.assertRaises(
            ValueError
        ):  # Expecting a ValueError after retries are exhausted
            self.runner.run(
                pipeline_cfg=pipeline_cfg_always_fails,
                final_vars=["output_from_always_fails"],
                max_retries=2,
                retry_delay=0.01,
                retry_exceptions=[ValueError],  # As actual exception types
            )
