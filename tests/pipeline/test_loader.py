"""Unit tests for the PipelineLoader extraction."""

from unittest.mock import MagicMock

import pytest
from fsspeckit import AbstractFileSystem

from flowerpower.cfg import PipelineConfig, ProjectConfig
from flowerpower.pipeline.config_manager import PipelineConfigManager
from flowerpower.pipeline.loader import CachedPipelineData, PipelineLoader
from flowerpower.pipeline.module_resolver import PipelineModuleResolver


@pytest.fixture
def loader(mocker):
    config_manager = mocker.MagicMock(spec=PipelineConfigManager)
    module_resolver = mocker.MagicMock(spec=PipelineModuleResolver)
    fs = mocker.MagicMock(spec=AbstractFileSystem)
    project_cfg = mocker.MagicMock(spec=ProjectConfig)
    project_cfg.hooks_dir = None

    return PipelineLoader(
        config_manager=config_manager,
        module_resolver=module_resolver,
        fs=fs,
        project_cfg=project_cfg,
    )


def _set_project_config(loader, mocker, cfg):
    type(loader._config_manager).project_config = mocker.PropertyMock(return_value=cfg)


def _set_project_config_error(loader, mocker, exc):
    type(loader._config_manager).project_config = mocker.PropertyMock(side_effect=exc)


def test_load_config_cache_hit_returns_cached_config(loader):
    cached = PipelineConfig(name="my_pipeline")
    loader._pipeline_data_cache["my_pipeline"] = CachedPipelineData(config=cached)
    loader._config_manager.load_pipeline_config.assert_not_called()

    result = loader.load_config("my_pipeline")

    assert result is cached
    loader._config_manager.load_pipeline_config.assert_not_called()


def test_load_config_reload_invalidates_cached_pipeline_and_module(loader, mocker):
    old_config = PipelineConfig(name="my_pipeline")
    new_config = PipelineConfig(name="my_pipeline")
    fake_module = mocker.MagicMock()
    fake_pipeline = mocker.MagicMock()

    loader._pipeline_data_cache["my_pipeline"] = CachedPipelineData(
        config=old_config,
        module=fake_module,
        pipeline=fake_pipeline,
    )
    loader._config_manager.load_pipeline_config.return_value = new_config

    result = loader.load_config("my_pipeline", reload=True)

    assert result is new_config
    loader._config_manager.load_pipeline_config.assert_called_once_with(
        "my_pipeline", reload=True
    )
    cached = loader._pipeline_data_cache["my_pipeline"]
    assert cached.config is new_config
    assert cached.pipeline is None
    assert cached.module is None


def test_load_config_cache_hit_calls_sync_project_state(loader, mocker):
    cached = PipelineConfig(name="my_pipeline")
    loader._pipeline_data_cache["my_pipeline"] = CachedPipelineData(config=cached)

    updated_cfg = mocker.MagicMock(spec=ProjectConfig)
    updated_cfg.hooks_dir = "/new/hooks"
    _set_project_config(loader, mocker, updated_cfg)

    loader.load_config("my_pipeline")

    assert loader.project_cfg is updated_cfg
    assert loader._hooks_dir == "/new/hooks"


def test_load_config_valueerror_from_sync_keeps_existing_project_cfg(loader, mocker):
    cached = PipelineConfig(name="my_pipeline")
    loader._pipeline_data_cache["my_pipeline"] = CachedPipelineData(config=cached)
    original_cfg = loader.project_cfg

    _set_project_config_error(loader, mocker, ValueError("boom"))

    loader.load_config("my_pipeline")

    assert loader.project_cfg is original_cfg
    assert loader._hooks_dir is not None


def test_load_module_cache_hit_returns_cached_module(loader, mocker):
    fake_module = mocker.MagicMock()
    loader._pipeline_data_cache["my_pipeline"] = CachedPipelineData(module=fake_module)

    result = loader.load_module("my_pipeline")

    assert result is fake_module
    loader._module_resolver.load.assert_not_called()


def test_load_module_reload_invalidates_cached_pipeline(loader, mocker):
    old_module = mocker.MagicMock()
    new_module = mocker.MagicMock()
    fake_pipeline = mocker.MagicMock()
    fake_config = PipelineConfig(name="my_pipeline")

    loader._pipeline_data_cache["my_pipeline"] = CachedPipelineData(
        config=fake_config,
        module=old_module,
        pipeline=fake_pipeline,
    )
    loader._module_resolver.load.return_value = new_module

    result = loader.load_module("my_pipeline", reload=True)

    assert result is new_module
    loader._module_resolver.load.assert_called_once_with("my_pipeline", reload=True)
    cached = loader._pipeline_data_cache["my_pipeline"]
    assert cached.module is new_module
    assert cached.pipeline is None
    assert cached.config is fake_config


def test_get_pipeline_ignores_partial_cache_and_constructs_new(loader, mocker):
    fake_config = PipelineConfig(name="my_pipeline")
    fake_module = mocker.MagicMock()
    fake_pipeline_instance = mocker.MagicMock()
    project_context = mocker.MagicMock()

    loader._pipeline_data_cache["my_pipeline"] = CachedPipelineData(
        config=fake_config,
        module=fake_module,
        pipeline=None,
    )
    loader._config_manager.load_pipeline_config.return_value = fake_config
    loader._module_resolver.load.return_value = fake_module

    PipelineMock = mocker.patch(
        "flowerpower.pipeline.pipeline.Pipeline", return_value=fake_pipeline_instance
    )

    result = loader.get_pipeline("my_pipeline", project_context=project_context)

    assert result is fake_pipeline_instance
    PipelineMock.assert_called_once_with(
        name="my_pipeline",
        config=fake_config,
        module=fake_module,
        project_context=project_context,
    )
    cached = loader._pipeline_data_cache["my_pipeline"]
    assert cached.pipeline is fake_pipeline_instance
    assert cached.config is fake_config
    assert cached.module is fake_module


def test_get_pipeline_returns_cached_pipeline_when_present(loader, mocker):
    fake_pipeline = mocker.MagicMock()
    loader._pipeline_data_cache["my_pipeline"] = CachedPipelineData(
        pipeline=fake_pipeline
    )

    result = loader.get_pipeline("my_pipeline", project_context=mocker.MagicMock())

    assert result is fake_pipeline
    loader._config_manager.load_pipeline_config.assert_not_called()
    loader._module_resolver.load.assert_not_called()


def test_get_pipeline_cached_return_calls_sync_project_state(loader, mocker):
    fake_pipeline = mocker.MagicMock()
    loader._pipeline_data_cache["my_pipeline"] = CachedPipelineData(
        pipeline=fake_pipeline
    )

    updated_cfg = mocker.MagicMock(spec=ProjectConfig)
    updated_cfg.hooks_dir = "/new/hooks"
    _set_project_config(loader, mocker, updated_cfg)

    loader.get_pipeline("my_pipeline", project_context=mocker.MagicMock())

    assert loader.project_cfg is updated_cfg
    assert loader._hooks_dir == "/new/hooks"


def test_get_pipeline_reload_reconstructs_pipeline(loader, mocker):
    fake_pipeline = mocker.MagicMock()
    fake_config = PipelineConfig(name="my_pipeline")
    fake_module = mocker.MagicMock()
    project_context = mocker.MagicMock()

    loader._pipeline_data_cache["my_pipeline"] = CachedPipelineData(
        pipeline=fake_pipeline,
        config=fake_config,
        module=fake_module,
    )
    loader._config_manager.load_pipeline_config.return_value = fake_config
    loader._module_resolver.load.return_value = fake_module

    PipelineMock = mocker.patch(
        "flowerpower.pipeline.pipeline.Pipeline",
        return_value=mocker.MagicMock(),
    )

    result = loader.get_pipeline(
        "my_pipeline", project_context=project_context, reload=True
    )

    assert result is PipelineMock.return_value
    PipelineMock.assert_called_once_with(
        name="my_pipeline",
        config=fake_config,
        module=fake_module,
        project_context=project_context,
    )


def test_clear_cache_by_name_pops_one_entry(loader, mocker):
    loader._pipeline_data_cache["a"] = CachedPipelineData()
    loader._pipeline_data_cache["b"] = CachedPipelineData()

    loader.clear_cache("a")

    assert "a" not in loader._pipeline_data_cache
    assert "b" in loader._pipeline_data_cache


def test_clear_cache_all_clears_dict(loader, mocker):
    loader._pipeline_data_cache["a"] = CachedPipelineData()
    loader._pipeline_data_cache["b"] = CachedPipelineData()

    loader.clear_cache()

    assert loader._pipeline_data_cache == {}


def test_sync_project_state_updates_project_cfg_and_hooks_dir(loader, mocker):
    updated_cfg = mocker.MagicMock(spec=ProjectConfig)
    updated_cfg.hooks_dir = "/custom/hooks"
    _set_project_config(loader, mocker, updated_cfg)

    loader.sync_project_state()

    assert loader.project_cfg is updated_cfg
    assert loader._hooks_dir == "/custom/hooks"


def test_sync_project_state_valueerror_keeps_existing_state(loader, mocker):
    original_cfg = loader.project_cfg
    original_hooks_dir = loader._hooks_dir

    _set_project_config_error(loader, mocker, ValueError("err"))

    loader.sync_project_state()

    assert loader.project_cfg is original_cfg
    assert loader._hooks_dir == original_hooks_dir
