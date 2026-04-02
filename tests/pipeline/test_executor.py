from unittest.mock import MagicMock

from flowerpower.cfg.pipeline import PipelineConfig
from flowerpower.cfg.pipeline.run import RunConfig
from flowerpower.pipeline.executor import PipelineExecutor
from flowerpower.utils.config import RunConfigBuilder


def test_merge_pipeline_run_config_preserves_adapter_override():
    base = RunConfig()
    override = RunConfig(adapter={"custom": "adapter"})

    merged = PipelineExecutor._merge_pipeline_run_config(base, override)

    assert merged.adapter == {"custom": "adapter"}


def test_merge_pipeline_run_config_preserves_raw_executor_override():
    base = RunConfig()
    override = RunConfigBuilder().with_executor(
        {"type": "threadpool", "max_workers": None}
    ).build()

    merged = PipelineExecutor._merge_pipeline_run_config(base, override)

    assert merged.executor_override_raw == {"type": "threadpool", "max_workers": None}
    assert merged.executor.type == "threadpool"
    assert merged.executor.max_workers is None


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
