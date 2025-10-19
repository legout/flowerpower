import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from flowerpower.cfg.pipeline import PipelineConfig, RunConfig
from flowerpower.cfg.pipeline.run import ExecutorConfig
from flowerpower.pipeline.runner import PipelineRunner


class FakeBuilder:
    last_instance = None

    def __init__(self):
        self.with_remote = False
        FakeBuilder.last_instance = self

    def with_modules(self, *_args, **_kwargs):
        return self

    def with_config(self, *_args, **_kwargs):
        return self

    def with_adapters(self, *_args, **_kwargs):
        return self

    def enable_dynamic_execution(self, **_kwargs):
        return self

    def with_local_executor(self, *_args, **_kwargs):
        return self

    def with_remote_executor(self, *_args, **_kwargs):
        self.with_remote = True
        return self

    def build(self):
        remote = self.with_remote

        class _Driver:
            def __init__(self, remote_flag: bool):
                self.remote = remote_flag

            def execute(self, **_kwargs):
                return {"remote": self.remote}

            async def execute_async(self, **_kwargs):
                return {"remote": self.remote}

        return _Driver(remote)


@pytest.fixture
def pipeline_stub():
    pipeline_cfg = PipelineConfig(
        name="test",
        run=RunConfig(
            executor=ExecutorConfig(type="synchronous"),
            inputs={},
        ),
    )
    module = SimpleNamespace()
    project_context = SimpleNamespace()
    return SimpleNamespace(
        name="test",
        config=pipeline_cfg,
        module=module,
        project_context=project_context,
        executor_factory=MagicMock(),
        adapter_manager=MagicMock(),
    )


@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
@patch("flowerpower.pipeline.runner.driver.Builder", FakeBuilder)
def test_runner_uses_remote_executor_when_not_synchronous(context_builder, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        [],
    )

    run_config = RunConfig(executor=ExecutorConfig(type="threadpool"))
    result = runner.run(run_config=run_config)

    assert result["remote"] is True
    assert FakeBuilder.last_instance.with_remote is True


@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
@patch("flowerpower.pipeline.runner.driver.Builder", FakeBuilder)
def test_runner_async_path_parity(context_builder, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        [],
    )

    run_config = RunConfig(executor=ExecutorConfig(type="synchronous"))
    result = asyncio.run(runner.run_async(run_config=run_config))

    assert result["remote"] is False
    assert FakeBuilder.last_instance.with_remote is False
