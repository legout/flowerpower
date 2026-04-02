from unittest.mock import MagicMock, patch

from flowerpower.pipeline.io import PipelineIOManager


def _make_registry() -> MagicMock:
    registry = MagicMock()
    registry.project_cfg = MagicMock(name="demo_project")
    registry.project_cfg.name = "demo"
    registry._fs = MagicMock()
    registry._cfg_dir = "conf"
    registry._pipelines_dir = "pipelines"
    registry._format_pipeline_path.side_effect = (
        lambda name: name.replace(".", "/").replace("-", "_")
    )
    return registry


def test_get_pipeline_files_resolves_normalized_dotted_pipeline_paths() -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    fs_view = MagicMock()
    fs_view.exists.side_effect = lambda path: path in {
        "conf/project.yml",
        "conf/pipelines/group/analytics.yml",
        "pipelines/group/analytics.py",
    }
    manager._get_filesystem_view = MagicMock(return_value=fs_view)

    files = manager._get_pipeline_files(
        "group.analytics",
        base_dir=".",
        fs=registry._fs,
        storage_options=None,
    )

    assert files == [
        "conf/project.yml",
        "conf/pipelines/group/analytics.yml",
        "pipelines/group/analytics.py",
    ]


def test_get_pipeline_files_uses_registry_configured_directories() -> None:
    registry = _make_registry()
    registry._cfg_dir = "settings"
    registry._pipelines_dir = "flows"
    manager = PipelineIOManager(registry)

    fs_view = MagicMock()
    fs_view.exists.side_effect = lambda path: path in {
        "settings/project.yml",
        "settings/flows/group/analytics.yml",
        "flows/group/analytics.py",
    }
    manager._get_filesystem_view = MagicMock(return_value=fs_view)

    files = manager._get_pipeline_files(
        "group.analytics",
        base_dir=".",
        fs=registry._fs,
        storage_options=None,
    )

    assert files == [
        "settings/project.yml",
        "settings/flows/group/analytics.yml",
        "flows/group/analytics.py",
    ]


def test_export_many_accepts_registry_pipeline_metadata_dicts() -> None:
    registry = _make_registry()
    registry.pipelines = [{"name": "group.analytics", "path": "pipelines/group/analytics.py"}]
    manager = PipelineIOManager(registry)
    manager._get_many_pipeline_files = MagicMock(
        return_value=[
            "conf/project.yml",
            "conf/pipelines/group/analytics.yml",
            "pipelines/group/analytics.py",
        ]
    )
    manager._sync_filesystem = MagicMock()

    manager.export_many(["group.analytics"], "export-dir", overwrite=True)

    manager._get_many_pipeline_files.assert_called_once_with(
        ["group.analytics"],
        base_dir=".",
        fs=registry._fs,
        storage_options=None,
    )
    manager._sync_filesystem.assert_called_once()


def test_export_pipeline_rejects_unknown_pipeline_name() -> None:
    registry = _make_registry()
    registry.pipelines = [{"name": "known.pipeline", "path": "pipelines/known/pipeline.py"}]
    manager = PipelineIOManager(registry)

    try:
        manager.export_pipeline("missing.pipeline", "export-dir")
    except ValueError as exc:
        assert "missing.pipeline" in str(exc)
    else:
        raise AssertionError("Expected export_pipeline to reject unknown pipeline names")


@patch("flowerpower.pipeline.io.console.print")
def test_print_import_success_for_all_pipelines(mock_print: MagicMock) -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    manager._print_import_success([], "source-dir")

    mock_print.assert_called_once_with(
        "✅ Imported all pipelines from [green]source-dir[/green] to [bold blue]demo[/bold blue]"
    )


@patch("flowerpower.pipeline.io.console.print")
def test_print_export_success_handles_missing_project_name(mock_print: MagicMock) -> None:
    registry = _make_registry()
    registry.project_cfg.name = None
    manager = PipelineIOManager(registry)

    manager._print_export_success(["group.analytics"], "export-dir")

    mock_print.assert_called_once_with(
        "✅ Exported pipelines [bold blue]group.analytics[/bold blue] to [green]export-dir[/green]"
    )


@patch("flowerpower.pipeline.io.console.print")
def test_print_export_all_success_handles_missing_project_name(mock_print: MagicMock) -> None:
    registry = _make_registry()
    registry.project_cfg.name = None
    manager = PipelineIOManager(registry)

    manager._print_export_success(None, "export-dir")

    mock_print.assert_called_once_with(
        "✅ Exported all pipelines from [bold blue]project[/bold blue] to [green]export-dir[/green]"
    )


@patch("flowerpower.pipeline.io.console.print")
def test_export_all_uses_safe_project_label(mock_print: MagicMock) -> None:
    registry = _make_registry()
    registry.project_cfg.name = None
    manager = PipelineIOManager(registry)
    manager._sync_filesystem = MagicMock()

    manager.export_all("export-dir", overwrite=True)

    manager._sync_filesystem.assert_called_once()
    mock_print.assert_called_once_with(
        "✅ Exported all pipelines from [bold blue]project[/bold blue] to [green]export-dir[/green]"
    )
