import asyncio
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from flowerpower.cfg.pipeline import PipelineConfig, RunConfig
from flowerpower.cfg.pipeline.run import ExecutorConfig, RetryConfig, WithAdapterConfig
from flowerpower.cfg.project import ProjectConfig
from flowerpower.cfg.project.adapter import AdapterConfig
from flowerpower.flowerpower import FlowerPowerProject
from flowerpower.pipeline.pipeline import Pipeline


class TestPipeline(unittest.TestCase):
    def setUp(self) -> None:
        adapter_cfg = AdapterConfig()
        self.project_cfg = ProjectConfig(name="test_project", adapter=adapter_cfg)

        self.project_context = MagicMock(spec=FlowerPowerProject)
        self.project_context.pipeline_manager = MagicMock()
        self.project_context.pipeline_manager._project_cfg = self.project_cfg

        self.pipeline_config = PipelineConfig(
            name="test_pipeline",
            run=RunConfig(
                inputs={"x": 1},
                executor=ExecutorConfig(type="synchronous"),
            ),
        )

        module = types.ModuleType("test_module")

        def node() -> int:
            return 42

        module.node = node
        self.module = module

    def test_pipeline_initialization(self):
        pipeline = Pipeline(
            name="test_pipeline",
            config=self.pipeline_config,
            module=self.module,
            project_context=self.project_context,
        )

        self.assertEqual(pipeline.name, "test_pipeline")
        self.assertIsNotNone(pipeline.adapter_manager)
        self.assertIsNotNone(pipeline.executor_factory)

    @patch("flowerpower.pipeline.pipeline.PipelineRunner")
    def test_run_delegates_to_runner(self, runner_cls):
        runner_instance = runner_cls.return_value
        pipeline = Pipeline(
            name="test_pipeline",
            config=self.pipeline_config,
            module=self.module,
            project_context=self.project_context,
        )

        pipeline.run(inputs={"x": 2})

        runner_instance.run.assert_called_once()
        args, kwargs = runner_instance.run.call_args
        self.assertEqual(set(kwargs.keys()), {"run_config"})
        passed = kwargs["run_config"]
        self.assertIsInstance(passed, RunConfig)
        self.assertEqual(passed.inputs, {"x": 2})
        self.assertEqual(passed.executor.type, "synchronous")

    @patch("flowerpower.pipeline.pipeline.PipelineRunner")
    def test_run_resolves_kwargs_into_run_config_without_forwarding(self, runner_cls):
        runner_instance = runner_cls.return_value
        pipeline = Pipeline(
            name="test_pipeline",
            config=self.pipeline_config,
            module=self.module,
            project_context=self.project_context,
        )

        pipeline.run(inputs={"x": 2}, executor_cfg="threadpool", final_vars=["node"])

        runner_instance.run.assert_called_once()
        args, kwargs = runner_instance.run.call_args
        self.assertEqual(set(kwargs.keys()), {"run_config"})
        passed = kwargs["run_config"]
        self.assertIsInstance(passed, RunConfig)
        self.assertEqual(passed.inputs, {"x": 2})
        self.assertEqual(passed.executor.type, "threadpool")
        self.assertEqual(passed.final_vars, ["node"])

    @patch("flowerpower.pipeline.pipeline.PipelineRunner")
    def test_run_does_not_mutate_caller_run_config_and_preserves_explicit_defaults(
        self, runner_cls
    ):
        runner_instance = runner_cls.return_value
        pipeline = Pipeline(
            name="test_pipeline",
            config=PipelineConfig(
                name="test_pipeline",
                run=RunConfig(
                    inputs={"y": 0},
                    final_vars=["base"],
                    config={"base": "value"},
                    cache={"recompute": ["node1"]},
                    executor=ExecutorConfig(type="local"),
                ),
            ),
            module=self.module,
            project_context=self.project_context,
        )
        caller = RunConfig(
            inputs={"x": 1},
            final_vars=[],
            config={},
            cache=False,
            executor=ExecutorConfig(type="synchronous"),
            explicit_overrides=["final_vars", "config", "cache"],
        )
        original_inputs = dict(caller.inputs)
        original_executor_type = caller.executor.type

        pipeline.run(run_config=caller, inputs={"x": 2})

        self.assertEqual(caller.inputs, original_inputs)
        self.assertEqual(caller.executor.type, original_executor_type)
        passed = runner_instance.run.call_args.kwargs["run_config"]
        self.assertEqual(passed.inputs, {"y": 0, "x": 2})
        self.assertEqual(passed.final_vars, [])
        self.assertEqual(passed.config, {})
        self.assertFalse(passed.cache)
        self.assertEqual(passed.executor.type, "synchronous")

    @patch("flowerpower.pipeline.pipeline.PipelineRunner")
    def test_run_async_delegates_to_runner(self, runner_cls):
        runner_instance = runner_cls.return_value
        runner_instance.run_async = AsyncMock(return_value={"result": 1})

        pipeline = Pipeline(
            name="test_pipeline",
            config=self.pipeline_config,
            module=self.module,
            project_context=self.project_context,
        )

        result = asyncio.run(pipeline.run_async(run_config=None))

        self.assertEqual(result, {"result": 1})
        runner_instance.run_async.assert_awaited_once()
        args, kwargs = runner_instance.run_async.call_args
        self.assertEqual(set(kwargs.keys()), {"run_config"})
        passed = kwargs["run_config"]
        self.assertIsInstance(passed, RunConfig)
        self.assertEqual(passed.inputs, {"x": 1})
        self.assertEqual(passed.executor.type, "synchronous")

    @patch("flowerpower.pipeline.pipeline.PipelineRunner")
    def test_run_merges_partial_run_config_with_pipeline_defaults(self, runner_cls):
        pipeline = Pipeline(
            name="test_pipeline",
            config=PipelineConfig(
                name="test_pipeline",
                run=RunConfig(
                    executor=ExecutorConfig(type="local", max_workers=None, num_cpus=None),
                    retry=RetryConfig(max_retries=5, retry_delay=9.0, jitter_factor=0.3),
                    with_adapter=WithAdapterConfig(mlflow=True),
                ),
            ),
            module=self.module,
            project_context=self.project_context,
        )

        partial = RunConfig(
            executor=ExecutorConfig(max_workers=2),
            retry=RetryConfig(max_retries=1),
            with_adapter=WithAdapterConfig(hamilton_tracker=True),
        )

        pipeline.run(run_config=partial)

        args, kwargs = runner_cls.return_value.run.call_args
        self.assertEqual(set(kwargs.keys()), {"run_config"})
        passed = kwargs["run_config"]
        self.assertIsInstance(passed, RunConfig)
        self.assertEqual(passed.executor.type, "local")
        self.assertEqual(passed.executor.max_workers, 2)
        self.assertEqual(passed.retry.max_retries, 1)
        self.assertEqual(passed.retry.retry_delay, 9.0)
        self.assertTrue(passed.with_adapter.hamilton_tracker)
        self.assertTrue(passed.with_adapter.mlflow)

if __name__ == "__main__":
    unittest.main()
