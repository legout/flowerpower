import asyncio
import types
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from flowerpower.cfg.pipeline import PipelineConfig
from flowerpower.cfg.pipeline.adapter import AdapterConfig
from flowerpower.cfg.pipeline.run import (
    CallbackSpec,
    ExecutorConfig,
    RetryConfig,
    RunConfig,
    WithAdapterConfig,
)
from flowerpower.pipeline.adapter_provider import ResolvedAdapterSet
from flowerpower.pipeline.execution_context import (
    ExecutionContextBuilder,
)
from flowerpower.pipeline.executor import PipelineExecutor, PipelineRunPlan
from flowerpower.pipeline.pipeline import Pipeline
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
    pipeline._run_resolved.return_value = {"ok": True}
    registry = MagicMock()
    registry.get_pipeline.return_value = pipeline

    executor = PipelineExecutor(config_manager=config_manager, registry=registry)

    result = executor.run(name="pipe", inputs={"x": 1})

    assert result == {"ok": True}
    assert pipeline_cfg.run.inputs == {}
    passed_run_config = pipeline._run_resolved.call_args.kwargs["run_config"]
    assert passed_run_config.inputs == {"x": 1}


def test_executor_forwards_reload_flag_to_registry():
    pipeline_cfg = PipelineConfig(name="pipe", run=RunConfig())
    config_manager = MagicMock()
    config_manager.load_pipeline_config.return_value = pipeline_cfg

    pipeline = MagicMock()
    pipeline._run_resolved.return_value = {"ok": True}
    registry = MagicMock()
    registry.get_pipeline.return_value = pipeline

    executor = PipelineExecutor(config_manager=config_manager, registry=registry)

    executor.run(name="pipe", run_config=RunConfig(reload=True))

    registry.get_pipeline.assert_called_once()
    assert registry.get_pipeline.call_args.kwargs["reload"] is True


def test_executor_run_uses_resolved_seam_and_preserves_settings():
    """PipelineExecutor.run resolves once and uses the resolved-only seam.

    After merging pipeline defaults, runtime RunConfig, and legacy kwargs, the
    executor must hand the runner a single resolved RunConfig and must not
    re-enter the public Pipeline.run path.
    """
    pipeline_config = PipelineConfig(
        name="pipe",
        run=RunConfig(
            inputs={"x": 1, "y": 2},
            final_vars=["base"],
            config={"base": "value"},
            executor=ExecutorConfig(type="synchronous"),
            retry=RetryConfig(max_retries=5, retry_delay=0.1),
        ),
    )
    config_manager = MagicMock()
    config_manager.load_pipeline_config.return_value = pipeline_config

    module = types.ModuleType("pipe_module")

    def node() -> int:
        return 42

    module.node = node

    pipeline = Pipeline(
        name="pipe",
        config=pipeline_config,
        module=module,
        project_context=MagicMock(),
    )
    registry = MagicMock()
    registry.get_pipeline.return_value = pipeline

    executor = PipelineExecutor(config_manager=config_manager, registry=registry)

    caller_config = RunConfig(inputs={"x": 10}, final_vars=["override"])
    original_inputs = dict(caller_config.inputs)

    with patch("flowerpower.pipeline.pipeline.PipelineRunner") as runner_cls, patch(
        "flowerpower.pipeline.pipeline.Pipeline.run"
    ) as mock_public_run:
        runner_instance = runner_cls.return_value
        runner_instance.run.return_value = {"resolved": "ok"}

        result = executor.run(
            name="pipe",
            run_config=caller_config,
            config={"extra": "value"},
            log_level="DEBUG",
        )

        mock_public_run.assert_not_called()
        runner_instance.run.assert_called_once()
        args, kwargs = runner_instance.run.call_args
        assert set(kwargs.keys()) == {"run_config", "adapter_set"}
        assert kwargs["adapter_set"].runtime_adapters == []
        passed = kwargs["run_config"]
        assert isinstance(passed, RunConfig)
        assert passed.inputs == {"x": 10, "y": 2}
        assert passed.final_vars == ["override"]
        assert passed.config == {"base": "value", "extra": "value"}
        assert passed.executor.type == "synchronous"
        assert passed.retry.max_retries == 5
        assert passed.retry.retry_delay == 0.1
        assert passed.log_level == "DEBUG"
        assert caller_config.inputs == original_inputs
        assert result == {"resolved": "ok"}

def test_executor_build_run_plan_centralizes_execution_resolution():
    """_build_run_plan returns the complete resolved execution artifact."""
    pipeline_config = PipelineConfig(
        name="pipe",
        adapter=AdapterConfig(hamilton_tracker={"project_id": 999}),
        run=RunConfig(
            inputs={"x": 1, "y": 2},
            config={"base": "value"},
            executor=ExecutorConfig(type="synchronous"),
        ),
    )
    config_manager = MagicMock()
    config_manager.load_pipeline_config.return_value = pipeline_config

    pipeline = MagicMock()
    registry = MagicMock()
    registry.get_pipeline.return_value = pipeline
    project_context = MagicMock()

    executor = PipelineExecutor(
        config_manager=config_manager,
        registry=registry,
        project_context=project_context,
    )

    plan = executor._build_run_plan(
        "pipe",
        RunConfig(
            inputs={"x": 10},
            pipeline_adapter_cfg=AdapterConfig(
                hamilton_tracker={"tags": {"env": "prod"}}
            ),
        ),
        config={"extra": "value"},
        reload=True,
    )

    assert isinstance(plan, PipelineRunPlan)
    assert plan.name == "pipe"
    assert plan.pipeline_config is pipeline_config
    assert plan.pipeline is pipeline
    assert plan.run_config.inputs == {"x": 10, "y": 2}
    assert plan.run_config.config == {"base": "value", "extra": "value"}
    assert plan.run_config.reload is True
    assert plan.run_config.pipeline_adapter_cfg.hamilton_tracker.project_id == 999
    assert plan.run_config.pipeline_adapter_cfg.hamilton_tracker.tags == {"env": "prod"}
    config_manager.load_pipeline_config.assert_called_once_with("pipe")
    registry.get_pipeline.assert_called_once_with(
        name="pipe",
        project_context=project_context,
        reload=True,
    )


def test_executor_run_async_uses_resolved_async_seam():
    """PipelineExecutor.run_async must not re-enter public Pipeline.run_async."""
    pipeline_config = PipelineConfig(name="pipe", run=RunConfig())
    config_manager = MagicMock()
    config_manager.load_pipeline_config.return_value = pipeline_config

    pipeline = MagicMock()
    pipeline._run_resolved_async = AsyncMock(return_value={"async": "ok"})
    pipeline.run_async = AsyncMock()
    registry = MagicMock()
    registry.get_pipeline.return_value = pipeline

    executor = PipelineExecutor(config_manager=config_manager, registry=registry)

    result = asyncio.run(executor.run_async(name="pipe", inputs={"x": 1}))

    assert result == {"async": "ok"}
    pipeline._run_resolved_async.assert_awaited_once()
    passed_run_config = pipeline._run_resolved_async.call_args.kwargs["run_config"]
    passed_adapter_set = pipeline._run_resolved_async.call_args.kwargs["adapter_set"]
    assert passed_run_config.inputs == {"x": 1}
    assert passed_adapter_set.runtime_adapters == []
    pipeline.run_async.assert_not_called()


def test_execution_context_builder_uses_resolved_run_config_for_executor_and_adapters():
    """Runtime construction consumes the resolved RunConfig values.

    The builder must not fall back to pipeline_config.run defaults to decide
    executor or adapter precedence.
    """
    executor_factory = MagicMock()
    executor_factory.create_executor.return_value = MagicMock(name="executor")
    resolved_adapters = [MagicMock(name="adapter")]
    run_config = RunConfig(
        executor=ExecutorConfig(type="threadpool", max_workers=4, num_cpus=2),
        with_adapter=WithAdapterConfig(hamilton_tracker=False, mlflow=False),
        pipeline_adapter_cfg=AdapterConfig(hamilton_tracker={"project_id": 123}),
    )
    adapter_set = ResolvedAdapterSet(
        with_adapter_cfg=run_config.with_adapter,
        pipeline_adapter_cfg=run_config.pipeline_adapter_cfg,
        project_adapter_cfg=MagicMock(ray=None),
        runtime_adapters=resolved_adapters,
    )

    builder = ExecutionContextBuilder(
        executor_factory=executor_factory,
        pipeline_config=MagicMock(),
        project_context=MagicMock(),
    )
    executor, cleanup, adapters = builder.build(run_config, adapter_set)

    executor_factory.create_executor.assert_called_once()
    passed_executor_cfg = executor_factory.create_executor.call_args[0][0]
    assert passed_executor_cfg.type == "threadpool"
    assert passed_executor_cfg.max_workers == 4
    assert passed_executor_cfg.num_cpus == 2
    assert executor is executor_factory.create_executor.return_value
    assert cleanup is None
    assert adapters == resolved_adapters


def test_executor_run_resolves_pipeline_adapter_config_into_run_config():
    """PipelineExecutor folds pipeline adapter defaults into the resolved RunConfig."""
    pipeline_config = PipelineConfig(
        name="pipe",
        adapter=AdapterConfig(hamilton_tracker={"project_id": 999}),
        run=RunConfig(),
    )
    config_manager = MagicMock()
    config_manager.load_pipeline_config.return_value = pipeline_config

    pipeline = MagicMock()
    pipeline._run_resolved.return_value = {"ok": True}
    registry = MagicMock()
    registry.get_pipeline.return_value = pipeline

    executor = PipelineExecutor(config_manager=config_manager, registry=registry)

    result = executor.run(
        name="pipe",
        run_config=RunConfig(
            pipeline_adapter_cfg=AdapterConfig(hamilton_tracker={"tags": {"env": "prod"}})
        ),
    )

    passed_run_config = pipeline._run_resolved.call_args.kwargs["run_config"]
    assert passed_run_config.pipeline_adapter_cfg.hamilton_tracker.project_id == 999
    assert passed_run_config.pipeline_adapter_cfg.hamilton_tracker.tags == {"env": "prod"}
    assert result == {"ok": True}

def test_executor_main_path_does_not_extract_adapter_config_from_project_context():
    pipeline_config = PipelineConfig(name="pipe", run=RunConfig())
    config_manager = MagicMock()
    config_manager.load_pipeline_config.return_value = pipeline_config

    pipeline = MagicMock()
    pipeline._run_resolved.return_value = {"ok": True}
    registry = MagicMock()
    registry.get_pipeline.return_value = pipeline
    registry.project_cfg = MagicMock(adapter=None)

    executor = PipelineExecutor(
        config_manager=config_manager,
        registry=registry,
        project_context=MagicMock(),
    )

    with patch(
        "flowerpower.utils.adapter.extract_project_adapter_base",
        side_effect=AssertionError("opaque project-context extraction used"),
    ):
        result = executor.run(name="pipe")

    assert result == {"ok": True}


def test_execution_context_builder_uses_resolved_project_adapter_for_ray_cleanup():
    executor_factory = MagicMock()
    executor_factory.create_executor.return_value = MagicMock(name="executor")

    ray_module = MagicMock()
    ray_module.shutdown = MagicMock(name="shutdown")

    project_adapter_cfg = MagicMock()
    project_adapter_cfg.ray = MagicMock(shutdown_ray_on_completion=True)

    builder = ExecutionContextBuilder(
        executor_factory=executor_factory,
        adapter_manager=MagicMock(),
        pipeline_config=MagicMock(run=MagicMock(executor=MagicMock())),
        project_context=MagicMock(),
    )

    with patch(
        "flowerpower.pipeline.execution_context.ExecutionContextBuilder._get_optional_ray",
        return_value=ray_module,
    ):
        executor, cleanup_fn = builder._create_executor(
            ExecutorConfig(type="ray"),
            project_adapter_cfg,
        )

    assert executor is executor_factory.create_executor.return_value
    assert cleanup_fn is ray_module.shutdown
