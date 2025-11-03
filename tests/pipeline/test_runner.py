import asyncio
import importlib
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from flowerpower.cfg.pipeline import PipelineConfig, RunConfig
from flowerpower.cfg.pipeline.run import ExecutorConfig
from flowerpower.pipeline.runner import PipelineRunner


class FakeBuilder:
    last_instance = None

    def __init__(self):
        self.with_remote = False
        self.modules = ()
        FakeBuilder.last_instance = self

    def with_modules(self, *args, **_kwargs):
        self.modules = args
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


class FakeAsyncBuilder:
    last_instance = None

    def __init__(self):
        self.with_remote = False
        self.modules = ()
        self.adapters = ()
        self.local_executor = None
        FakeAsyncBuilder.last_instance = self

    def with_modules(self, *args, **_kwargs):
        self.modules = args
        return self

    def with_config(self, *_args, **_kwargs):
        return self

    def with_adapters(self, *args):
        self.adapters = args
        return self

    def enable_dynamic_execution(self, **_kwargs):
        return self

    def with_local_executor(self, executor, **_kwargs):
        self.local_executor = executor
        return self

    def with_remote_executor(self, *_args, **_kwargs):
        self.with_remote = True
        return self

    async def build(self):
        remote_flag = self.with_remote
        adapters = self.adapters

        class _AsyncDriver:
            async def execute(self_inner, **_kwargs):
                return {"remote": remote_flag, "adapters": adapters}

        return _AsyncDriver()


@pytest.fixture
def pipeline_stub():
    pipeline_cfg = PipelineConfig(
        name="test",
        run=RunConfig(
            executor=ExecutorConfig(type="synchronous"),
            inputs={},
        ),
    )
    module = ModuleType("pipeline_module")
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
def test_runner_async_path_parity(context_builder, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        [],
    )

    fake_async_module = SimpleNamespace(Builder=FakeAsyncBuilder)

    with patch("flowerpower.pipeline.runner.hamilton_async_driver", fake_async_module):
        run_config = RunConfig(executor=ExecutorConfig(type="synchronous"))
        result = asyncio.run(runner.run_async(run_config=run_config))

    assert result["remote"] is False
    assert FakeAsyncBuilder.last_instance.with_remote is False


@patch("flowerpower.pipeline.runner.setup_logging")
@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
@patch("flowerpower.pipeline.runner.driver.Builder", FakeBuilder)
def test_runner_applies_log_level(context_builder, mock_setup_logging, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        [],
    )

    run_config = RunConfig(executor=ExecutorConfig(type="synchronous"), log_level="DEBUG")
    runner.run(run_config=run_config)

    mock_setup_logging.assert_called_with(level="DEBUG")


@patch("flowerpower.pipeline.runner.setup_logging")
@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
def test_runner_async_applies_log_level(context_builder, mock_setup_logging, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        [],
    )

    fake_async_module = SimpleNamespace(Builder=FakeAsyncBuilder)

    with patch("flowerpower.pipeline.runner.hamilton_async_driver", fake_async_module):
        run_config = RunConfig(
            executor=ExecutorConfig(type="synchronous"),
            log_level="INFO",
        )
        asyncio.run(runner.run_async(run_config=run_config))

    mock_setup_logging.assert_called_with(level="INFO")


@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
@patch("flowerpower.pipeline.runner.driver.Builder", FakeBuilder)
def test_runner_additional_modules_are_imported_and_passed(context_builder, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        [],
    )

    setup_module = ModuleType("setup")

    def fake_import(name: str):
        if name in ("setup", "pipelines.setup"):
            return setup_module
        raise ImportError(name)

    with patch("flowerpower.pipeline.runner.importlib.import_module", side_effect=fake_import):
        run_config = RunConfig(
            executor=ExecutorConfig(type="synchronous"),
            additional_modules=["setup"],
        )
        runner.run(run_config=run_config)

    assert FakeBuilder.last_instance.modules[0] is setup_module
    assert FakeBuilder.last_instance.modules[1] is pipeline_stub.module


@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
def test_runner_additional_modules_async_path(context_builder, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        ["adapter"],
    )

    setup_module = ModuleType("setup_async")

    original_import = importlib.import_module

    def fake_import(name: str, *args, **kwargs):
        if name in ("setup_async", "pipelines.setup_async"):
            return setup_module
        return original_import(name, *args, **kwargs)

    fake_async_module = SimpleNamespace(Builder=FakeAsyncBuilder)

    with patch("flowerpower.pipeline.runner.importlib.import_module", side_effect=fake_import):
        with patch("flowerpower.pipeline.runner.hamilton_async_driver", fake_async_module):
            run_config = RunConfig(
                executor=ExecutorConfig(type="synchronous"),
                additional_modules=["setup_async"],
            )
            result = asyncio.run(runner.run_async(run_config=run_config))

    assert result["remote"] is False
    assert FakeAsyncBuilder.last_instance.modules[0] is setup_module
    assert FakeAsyncBuilder.last_instance.modules[1] is pipeline_stub.module
    assert FakeAsyncBuilder.last_instance.adapters == ("adapter",)


@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
@patch("flowerpower.pipeline.runner.driver.Builder", FakeBuilder)
def test_runner_additional_modules_missing_raises_clear_error(context_builder, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        [],
    )

    with patch(
        "flowerpower.pipeline.runner.importlib.import_module",
        side_effect=ImportError("boom"),
    ):
        run_config = RunConfig(
            executor=ExecutorConfig(type="synchronous"),
            additional_modules=["missing"],
        )
        with pytest.raises(ImportError) as exc:
            runner.run(run_config=run_config)

    message = str(exc.value)
    assert "missing" in message
    assert "Tried" in message


@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
@patch("flowerpower.pipeline.runner.driver.Builder", FakeBuilder)
def test_runner_reload_reloads_additional_modules(context_builder, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        [],
    )

    setup_module = ModuleType("setup_reload")

    run_config = RunConfig(
        executor=ExecutorConfig(type="synchronous"),
        additional_modules=[setup_module],
        reload=True,
    )

    with patch("flowerpower.pipeline.runner.importlib.reload") as import_reload:
        runner.run(run_config=run_config)

    reloaded = [call.args[0].__name__ for call in import_reload.call_args_list]
    assert "setup_reload" in reloaded


@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
def test_runner_async_driver_disabled_raises(context_builder, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        [],
    )

    fake_async_module = SimpleNamespace(Builder=FakeAsyncBuilder)

    with patch("flowerpower.pipeline.runner.hamilton_async_driver", fake_async_module):
        run_config = RunConfig(async_driver=False)
        with pytest.raises(ValueError):
            asyncio.run(runner.run_async(run_config=run_config))


@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
def test_runner_async_missing_driver_raises_helpful_error(context_builder, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    context_builder.return_value.build.return_value = (
        SimpleNamespace(),
        None,
        [],
    )

    with patch("flowerpower.pipeline.runner.hamilton_async_driver", None):
        run_config = RunConfig()
        with pytest.raises(ImportError) as exc:
            asyncio.run(runner.run_async(run_config=run_config))

    assert "hamilton" in str(exc.value).lower()


@patch("flowerpower.pipeline.runner.ExecutionContextBuilder")
def test_runner_async_remote_executor_respected(context_builder, pipeline_stub):
    runner = PipelineRunner(pipeline_stub)
    fake_executor = SimpleNamespace()
    context_builder.return_value.build.return_value = (
        fake_executor,
        None,
        [],
    )

    fake_async_module = SimpleNamespace(Builder=FakeAsyncBuilder)

    with patch("flowerpower.pipeline.runner.hamilton_async_driver", fake_async_module):
        run_config = RunConfig(executor=ExecutorConfig(type="threadpool"))
        asyncio.run(runner.run_async(run_config=run_config))

    assert FakeAsyncBuilder.last_instance.with_remote is True
