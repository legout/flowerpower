import asyncio
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock, patch

import pytest

from flowerpower.flowerpower import FlowerPowerProject
from flowerpower.pipeline.manager import PipelineManager
from flowerpower.pipeline.project_context import ProjectRuntimeContext


def test_project_runtime_context_is_frozen_and_facts_only():
    fs = MagicMock()
    context = ProjectRuntimeContext(
        fs=fs,
        base_dir="/project",
        storage_options={"token": "secret"},
        cfg_dir="conf",
        pipelines_dir="pipelines",
        owns_filesystem=True,
    )

    assert context.fs is fs
    assert context.base_dir == "/project"
    assert context.storage_options == {"token": "secret"}
    assert context.cfg_dir == "conf"
    assert context.pipelines_dir == "pipelines"
    assert context.owns_filesystem is True

    for forbidden in (
        "project_cfg",
        "config_manager",
        "loader",
        "registry",
        "executor",
        "visualizer",
        "creator",
        "io",
    ):
        assert not hasattr(context, forbidden)

    with pytest.raises(FrozenInstanceError):
        context.base_dir = "/other"


def test_pipeline_manager_context_exit_only_clears_owned_filesystem():
    owned_fs = MagicMock()
    supplied_fs = MagicMock()

    with patch.object(PipelineManager, "_initialize_managers"), patch.object(
        PipelineManager, "_bootstrap_project_directories"
    ), patch("flowerpower.pipeline.manager.filesystem", return_value=owned_fs):
        owned_manager = PipelineManager(base_dir="/owned")
        owned_manager.__exit__(None, None, None)

    owned_fs.clear_instance_cache.assert_called_once()

    with patch.object(PipelineManager, "_initialize_managers"), patch.object(
        PipelineManager, "_bootstrap_project_directories"
    ):
        supplied_manager = PipelineManager(base_dir="/supplied", fs=supplied_fs)
        supplied_manager.__exit__(None, None, None)

    supplied_fs.clear_instance_cache.assert_not_called()


def test_pipeline_manager_run_does_not_mutate_executor_project_context():
    class GuardedExecutor:
        def __setattr__(self, name, value):
            if name == "_project_context":
                raise AssertionError("PipelineManager.run must not mutate executor context")
            super().__setattr__(name, value)

        def run(self, *, name, run_config=None, **kwargs):
            return {"name": name, "kwargs": kwargs}

    manager = PipelineManager.__new__(PipelineManager)
    manager._executor = GuardedExecutor()

    result = PipelineManager.run(manager, "demo", log_level="DEBUG")

    assert result == {"name": "demo", "kwargs": {"log_level": "DEBUG"}}


def test_pipeline_manager_run_async_does_not_mutate_executor_project_context():
    class GuardedExecutor:
        def __setattr__(self, name, value):
            if name == "_project_context":
                raise AssertionError(
                    "PipelineManager.run_async must not mutate executor context"
                )
            super().__setattr__(name, value)

        async def run_async(self, *, name, run_config=None, **kwargs):
            return {"name": name, "kwargs": kwargs}

    manager = PipelineManager.__new__(PipelineManager)
    manager._executor = GuardedExecutor()

    result = asyncio.run(PipelineManager.run_async(manager, "demo", reload=True))

    assert result == {"name": "demo", "kwargs": {"reload": True}}


def test_pipeline_manager_new_project_and_load_existing(tmp_path):
    project_dir = tmp_path / "demo_project"

    manager = PipelineManager.new_project(name="demo", base_dir=str(project_dir))

    assert isinstance(manager, PipelineManager)
    assert manager.project_cfg.name == "demo"
    assert manager.registry is not None
    assert manager.visualizer is not None
    assert manager.io is not None
    assert manager.creator is not None
    assert manager.executor is not None

    loaded = PipelineManager.load_existing(base_dir=str(project_dir))

    assert isinstance(loaded, PipelineManager)
    assert loaded.project_cfg.name == "demo"


def test_pipeline_manager_load_existing_returns_none_for_missing_project(tmp_path):
    missing = tmp_path / "missing"

    assert PipelineManager.load_existing(base_dir=str(missing)) is None


def test_pipeline_manager_new_project_existing_project_requires_overwrite(tmp_path):
    project_dir = tmp_path / "demo_project"
    PipelineManager.new_project(name="demo", base_dir=str(project_dir))

    with pytest.raises(FileExistsError):
        PipelineManager.new_project(name="demo", base_dir=str(project_dir))


def test_flowerpower_project_delegates_load_and_new_to_pipeline_manager(tmp_path):
    project_dir = tmp_path / "delegated_project"

    with patch.object(PipelineManager, "new_project") as new_project:
        manager = MagicMock(spec=PipelineManager)
        manager.project_cfg.name = "delegated"
        new_project.return_value = manager

        project = FlowerPowerProject.new(name="delegated", base_dir=str(project_dir))

    assert project.pipeline_manager is manager
    assert project.name == "delegated"
    new_project.assert_called_once()

    with patch.object(PipelineManager, "load_existing") as load_existing:
        manager = MagicMock(spec=PipelineManager)
        manager.project_cfg.name = "delegated"
        load_existing.return_value = manager

        project = FlowerPowerProject.load(base_dir=str(project_dir))

    assert project is not None
    assert project.pipeline_manager is manager
    assert project.name == "delegated"
    load_existing.assert_called_once()
