from unittest.mock import MagicMock, Mock, patch

from flowerpower.cfg.pipeline import PipelineConfig
from flowerpower.cfg.pipeline.adapter import AdapterConfig
from flowerpower.cfg.pipeline.run import (
    CallbackSpec,
    ExecutorConfig,
    RetryConfig,
    RunConfig,
)
from flowerpower.pipeline.execution_context import ExecutionContextBuilder
from flowerpower.pipeline.executor import PipelineExecutor
from flowerpower.utils.adapter import AdapterManager
from flowerpower.utils.config import RunConfigBuilder


def test_merge_pipeline_run_config_preserves_adapter_override():
    base = RunConfig()
    adapter = Mock()
    override = RunConfig(adapter={"custom": adapter})

    merged = PipelineExecutor._merge_pipeline_run_config(base, override)

    assert merged.adapter == {"custom": adapter}
    assert merged.adapter["custom"] is adapter


def test_merge_pipeline_run_config_preserves_callback_identity():
    base = RunConfig()
    callback = Mock()
    override = RunConfig(
        on_success=CallbackSpec(func=callback, args=("extra",), kwargs={"flag": True})
    )

    merged = PipelineExecutor._merge_pipeline_run_config(base, override)

    assert merged.on_success.func is callback
    assert merged.on_success.args == ("extra",)
    assert merged.on_success.kwargs == {"flag": True}


def test_merge_pipeline_run_config_preserves_raw_executor_override():
    base = RunConfig()
    override = RunConfigBuilder().with_executor(
        {"type": "threadpool", "max_workers": None}
    ).build()

    merged = PipelineExecutor._merge_pipeline_run_config(base, override)

    assert merged.executor_override_raw == {"type": "threadpool", "max_workers": None}
    assert merged.executor.type == "threadpool"
    assert merged.executor.max_workers is None


def test_merge_pipeline_run_config_partially_overrides_executor_without_resetting_base():
    base = RunConfig(executor=ExecutorConfig(type="local", max_workers=None, num_cpus=None))
    override = RunConfig(executor=ExecutorConfig(max_workers=2))

    merged = PipelineExecutor._merge_pipeline_run_config(base, override)

    assert merged.executor.type == "local"
    assert merged.executor.max_workers == 2
    assert merged.executor.num_cpus is None


def test_merge_pipeline_run_config_partially_overrides_retry_without_resetting_base():
    base = RunConfig(retry=RetryConfig(max_retries=5, retry_delay=9.0, jitter_factor=0.3))
    override = RunConfig(retry=RetryConfig(max_retries=1))

    merged = PipelineExecutor._merge_pipeline_run_config(base, override)

    assert merged.retry.max_retries == 1
    assert merged.retry.retry_delay == 9.0
    assert merged.retry.jitter_factor == 0.3


def test_adapter_manager_preserves_existing_nested_adapter_values_on_partial_override():
    manager = AdapterManager()
    base = AdapterConfig(hamilton_tracker={"project_id": 123})
    override = AdapterConfig(hamilton_tracker={"tags": {"env": "prod"}})

    merged = manager.resolve_pipeline_adapter_config(override, base)

    assert merged.hamilton_tracker.project_id == 123
    assert merged.hamilton_tracker.tags == {"env": "prod"}


def test_executor_run_does_not_mutate_pipeline_defaults():
    pipeline_cfg = PipelineConfig(name="pipe", run=RunConfig())
    config_manager = MagicMock()
    config_manager.load_pipeline_config.return_value = pipeline_cfg

    pipeline = MagicMock()
    pipeline.run.return_value = {"ok": True}
    registry = MagicMock()
    registry.get_pipeline.return_value = pipeline

    executor = PipelineExecutor(config_manager=config_manager, registry=registry)

    result = executor.run(name="pipe", inputs={"x": 1})

    assert result == {"ok": True}
    assert pipeline_cfg.run.inputs == {}
    passed_run_config = pipeline.run.call_args.kwargs["run_config"]
    assert passed_run_config.inputs == {"x": 1}


def test_executor_forwards_reload_flag_to_registry():
    pipeline_cfg = PipelineConfig(name="pipe", run=RunConfig())
    config_manager = MagicMock()
    config_manager.load_pipeline_config.return_value = pipeline_cfg

    pipeline = MagicMock()
    pipeline.run.return_value = {"ok": True}
    registry = MagicMock()
    registry.get_pipeline.return_value = pipeline

    executor = PipelineExecutor(config_manager=config_manager, registry=registry)

    executor.run(name="pipe", run_config=RunConfig(reload=True))

    registry.get_pipeline.assert_called_once()
    assert registry.get_pipeline.call_args.kwargs["reload"] is True


def test_execution_context_builder_finds_project_config_via_pipeline_manager():
    executor_factory = MagicMock()
    executor_factory.create_executor.return_value = MagicMock(name="executor")

    ray_module = MagicMock()
    ray_module.shutdown = MagicMock(name="shutdown")

    pipeline_manager = MagicMock()
    pipeline_manager._project_cfg = MagicMock()
    pipeline_manager._project_cfg.adapter = MagicMock()
    pipeline_manager._project_cfg.adapter.ray = MagicMock(
        shutdown_ray_on_completion=True
    )

    project_context = MagicMock()
    project_context.pipeline_manager = pipeline_manager

    builder = ExecutionContextBuilder(
        executor_factory=executor_factory,
        adapter_manager=MagicMock(),
        pipeline_config=MagicMock(run=MagicMock(executor=MagicMock())),
        project_context=project_context,
    )

    with patch(
        "flowerpower.pipeline.execution_context.ExecutionContextBuilder._get_optional_ray",
        return_value=ray_module,
    ):
        executor, cleanup_fn = builder._create_executor(ExecutorConfig(type="ray"))

    assert executor is executor_factory.create_executor.return_value
    assert cleanup_fn is ray_module.shutdown
