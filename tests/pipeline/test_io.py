import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from fsspeckit import filesystem

from flowerpower.pipeline.io import PipelineIOManager


def _make_registry() -> MagicMock:
    registry = MagicMock()
    registry.project_cfg = MagicMock(name="demo_project")
    registry.project_cfg.name = "demo"
    registry._fs = MagicMock()
    registry._cfg_dir = "conf"
    registry._pipelines_dir = "pipelines"
    return registry


def test_get_pipeline_files_returns_expected_paths() -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    files = manager._get_pipeline_files("group.analytics")

    assert files == [
        "conf/project.yml",
        "conf/pipelines/group/analytics.yml",
        "pipelines/group/analytics.py",
    ]


def test_get_many_pipeline_files_returns_expected_paths() -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    files = manager._get_many_pipeline_files(["group.analytics", "other"])

    assert files == [
        "conf/project.yml",
        "conf/pipelines/group/analytics.yml",
        "pipelines/group/analytics.py",
        "conf/pipelines/other.yml",
        "pipelines/other.py",
    ]


def test_get_pipeline_files_uses_custom_dirs_and_formatter() -> None:
    registry = _make_registry()
    registry._cfg_dir = "settings"
    registry._pipelines_dir = "flows"
    manager = PipelineIOManager(registry)

    files = manager._get_pipeline_files("group.my-pipeline")

    assert files == [
        "settings/project.yml",
        "settings/flows/group/my_pipeline.yml",
        "flows/group/my_pipeline.py",
    ]


def test_get_pipeline_files_prefers_existing_fallback_config_path() -> None:
    registry = _make_registry()
    registry._fs.exists.side_effect = lambda path: path == "conf/my_pipeline.yml"
    manager = PipelineIOManager(registry)

    files = manager._get_pipeline_files("my-pipeline", fs=registry._fs)

    assert files == [
        "conf/project.yml",
        "conf/my_pipeline.yml",
        "pipelines/my_pipeline.py",
    ]


def test_get_pipeline_files_prefers_existing_project_yaml() -> None:
    registry = _make_registry()
    registry._fs.exists.side_effect = lambda path: path == "conf/project.yaml"
    manager = PipelineIOManager(registry)

    files = manager._get_pipeline_files("my-pipeline", fs=registry._fs)

    assert files[0] == "conf/project.yaml"


def test_get_pipeline_files_skips_project_probe_errors() -> None:
    registry = _make_registry()

    def exists(path: str) -> bool:
        if path == "conf/project.yml":
            raise PermissionError("denied")
        return path == "conf/project.yaml"

    registry._fs.exists.side_effect = exists
    manager = PipelineIOManager(registry)

    files = manager._get_pipeline_files("my-pipeline", fs=registry._fs)

    assert files[0] == "conf/project.yaml"


def test_get_many_pipeline_files_prefers_existing_project_yaml() -> None:
    registry = _make_registry()
    registry._fs.exists.side_effect = lambda path: path == "conf/project.yaml"
    manager = PipelineIOManager(registry)

    files = manager._get_many_pipeline_files(["my-pipeline"], fs=registry._fs)

    assert files[0] == "conf/project.yaml"


def test_get_pipeline_files_skips_pipeline_probe_errors() -> None:
    registry = _make_registry()

    def exists(path: str) -> bool:
        if path == "conf/pipelines/my_pipeline.yml":
            raise PermissionError("denied")
        return path == "conf/my_pipeline.yml"

    registry._fs.exists.side_effect = exists
    manager = PipelineIOManager(registry)

    files = manager._get_pipeline_files("my-pipeline", fs=registry._fs)

    assert files[1] == "conf/my_pipeline.yml"


def test_export_many_accepts_registry_pipeline_names() -> None:
    registry = _make_registry()
    registry.pipelines = ["group.analytics"]
    manager = PipelineIOManager(registry)
    manager._get_many_pipeline_files = MagicMock(
        return_value=[
            "conf/project.yml",
            "conf/pipelines/group.analytics.yml",
            "pipelines/group.analytics.py",
        ]
    )
    manager._sync_filesystem = MagicMock()

    manager.export_many(["group.analytics"], "export-dir", overwrite=True)

    manager._get_many_pipeline_files.assert_called_once_with(
        ["group.analytics"],
        fs=registry._fs,
    )
    manager._sync_filesystem.assert_called_once()


def test_export_accepts_original_hyphenated_name_when_registry_lists_module_name() -> None:
    registry = _make_registry()
    registry.pipelines = ["group.my_pipeline"]
    manager = PipelineIOManager(registry)
    manager._get_pipeline_files = MagicMock(
        return_value=[
            "conf/project.yml",
            "conf/pipelines/group/my_pipeline.yml",
            "pipelines/group/my_pipeline.py",
        ]
    )
    manager._sync_filesystem = MagicMock()

    manager.export_pipeline("group.my-pipeline", "export-dir", overwrite=True)

    manager._get_pipeline_files.assert_called_once_with(
        "group.my-pipeline",
        fs=registry._fs,
    )
    manager._sync_filesystem.assert_called_once()


def test_export_accepts_underscored_name_when_registry_lists_hyphenated_name() -> None:
    registry = _make_registry()
    registry.pipelines = ["group.my-pipeline"]
    manager = PipelineIOManager(registry)
    manager._get_pipeline_files = MagicMock(
        return_value=[
            "conf/project.yml",
            "conf/pipelines/group/my_pipeline.yml",
            "pipelines/group/my_pipeline.py",
        ]
    )
    manager._sync_filesystem = MagicMock()

    manager.export_pipeline("group.my_pipeline", "export-dir", overwrite=True)

    manager._get_pipeline_files.assert_called_once_with(
        "group.my_pipeline",
        fs=registry._fs,
    )
    manager._sync_filesystem.assert_called_once()


def test_export_accepts_mixed_hyphen_underscore_variants() -> None:
    registry = _make_registry()
    registry.pipelines = ["group.my-pipeline.sub_module"]
    manager = PipelineIOManager(registry)
    manager._get_pipeline_files = MagicMock(
        return_value=[
            "conf/project.yml",
            "conf/pipelines/group/my_pipeline/sub_module.yml",
            "pipelines/group/my_pipeline/sub_module.py",
        ]
    )
    manager._sync_filesystem = MagicMock()

    manager.export_pipeline("group.my_pipeline.sub_module", "export-dir", overwrite=True)

    manager._get_pipeline_files.assert_called_once_with(
        "group.my_pipeline.sub_module",
        fs=registry._fs,
    )
    manager._sync_filesystem.assert_called_once()


def test_export_accepts_fully_mixed_hyphen_underscore_variants() -> None:
    registry = _make_registry()
    registry.pipelines = ["group.my-pipeline.sub-module"]
    manager = PipelineIOManager(registry)
    manager._get_pipeline_files = MagicMock(
        return_value=[
            "conf/project.yml",
            "conf/pipelines/group/my_pipeline/sub_module.yml",
            "pipelines/group/my_pipeline/sub_module.py",
        ]
    )
    manager._sync_filesystem = MagicMock()

    manager.export_pipeline("group.my_pipeline.sub_module", "export-dir", overwrite=True)

    manager._get_pipeline_files.assert_called_once_with(
        "group.my_pipeline.sub_module",
        fs=registry._fs,
    )
    manager._sync_filesystem.assert_called_once()


def test_export_pipeline_rejects_unknown_pipeline_name() -> None:
    registry = _make_registry()
    registry.pipelines = ["known.pipeline"]
    manager = PipelineIOManager(registry)

    try:
        manager.export_pipeline("missing.pipeline", "export-dir")
    except ValueError as exc:
        assert "missing.pipeline" in str(exc)
    else:
        raise AssertionError("Expected export_pipeline to reject unknown pipeline names")


def test_export_many_rejects_unknown_pipeline_name() -> None:
    registry = _make_registry()
    registry.pipelines = ["known.pipeline"]
    manager = PipelineIOManager(registry)

    try:
        manager.export_many(["missing.pipeline"], "export-dir")
    except ValueError as exc:
        assert "missing.pipeline" in str(exc)
    else:
        raise AssertionError("Expected export_many to reject unknown pipeline names")


@patch("flowerpower.pipeline.io.console.print")
def test_print_import_success_for_all_pipelines(mock_print: MagicMock) -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    manager._print_import_success(["group.analytics"], "source-dir")

    mock_print.assert_called_once_with(
        "✅ Imported pipelines [bold blue]group.analytics[/bold blue] from [green]source-dir[/green] to [bold blue]demo[/bold blue]"
    )


@patch("flowerpower.pipeline.io.console.print")
def test_print_import_success_without_names_imported_all(mock_print: MagicMock) -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    manager._print_import_success(None, "source-dir")

    mock_print.assert_called_once_with(
        "✅ Imported all pipelines from [green]source-dir[/green] to [bold blue]demo[/bold blue]"
    )


@patch("flowerpower.pipeline.io.console.print")
def test_print_import_success_uses_safe_project_label_when_name_missing(
    mock_print: MagicMock,
) -> None:
    registry = _make_registry()
    registry.project_cfg.name = None
    manager = PipelineIOManager(registry)

    manager._print_import_success(None, "source-dir")

    mock_print.assert_called_once_with(
        "✅ Imported all pipelines from [green]source-dir[/green] to [bold blue]project[/bold blue]"
    )


@patch("flowerpower.pipeline.io.console.print")
def test_print_export_success_with_names(mock_print: MagicMock) -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    manager._print_export_success(["group.analytics"], "export-dir")

    mock_print.assert_called_once_with(
        "✅ Exported pipelines [bold blue]demo.group.analytics[/bold blue] to [green]export-dir[/green]"
    )


@patch("flowerpower.pipeline.io.console.print")
def test_print_export_success_handles_missing_project_name(
    mock_print: MagicMock,
) -> None:
    registry = _make_registry()
    registry.project_cfg.name = None
    manager = PipelineIOManager(registry)

    manager._print_export_success(["group.analytics"], "export-dir")

    mock_print.assert_called_once_with(
        "✅ Exported pipelines [bold blue]group.analytics[/bold blue] to [green]export-dir[/green]"
    )


@patch("flowerpower.pipeline.io.console.print")
def test_print_export_success_no_names(mock_print: MagicMock) -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    manager._print_export_success(None, "export-dir")

    mock_print.assert_called_once_with(
        "✅ Exported all pipelines from [bold blue]demo[/bold blue] to [green]export-dir[/green]"
    )


@patch("flowerpower.pipeline.io.console.print")
def test_export_all_uses_project_name(mock_print: MagicMock) -> None:
    registry = _make_registry()
    registry.project_cfg.name = "my-project"
    manager = PipelineIOManager(registry)
    manager._sync_filesystem = MagicMock()

    manager.export_all("export-dir", overwrite=True)

    manager._sync_filesystem.assert_called_once()
    mock_print.assert_called_once_with(
        "✅ Exported all pipelines from [bold blue]my-project[/bold blue] to [green]export-dir[/green]"
    )


@patch("flowerpower.pipeline.io.console.print")
def test_export_all_uses_safe_project_label_when_name_missing(
    mock_print: MagicMock,
) -> None:
    registry = _make_registry()
    registry.project_cfg.name = None
    manager = PipelineIOManager(registry)
    manager._sync_filesystem = MagicMock()

    manager.export_all("export-dir", overwrite=True)

    manager._sync_filesystem.assert_called_once()
    mock_print.assert_called_once_with(
        "✅ Exported all pipelines from [bold blue]project[/bold blue] to [green]export-dir[/green]"
    )


def test_discover_all_pipeline_files_uses_configured_dirs_only() -> None:
    registry = _make_registry()
    registry._cfg_dir = "settings"
    registry._pipelines_dir = "flows"
    manager = PipelineIOManager(registry)

    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        root = Path(tmpdir)
        (root / "settings" / "flows" / "group").mkdir(parents=True)
        (root / "flows" / "group").mkdir(parents=True)
        (root / "scripts").mkdir()

        (root / "settings" / "project.yml").write_text("name: demo\n")
        (root / "settings" / "flows" / "pipe.yml").write_text("name: pipe\n")
        (root / "settings" / "flows" / "group" / "nested.yml").write_text(
            "name: group.nested\n"
        )
        (root / "settings" / "other.yml").write_text("ignored: true\n")
        (root / "flows" / "pipe.py").write_text("VALUE = 1\n")
        (root / "flows" / "group" / "nested.py").write_text("VALUE = 2\n")
        (root / "flows" / "__init__.py").write_text("")
        (root / "scripts" / "helper.py").write_text("VALUE = 3\n")

        files = manager._discover_all_pipeline_files(fs)

    assert files == [
        "flows/group/nested.py",
        "flows/pipe.py",
        "settings/flows/group/nested.yml",
        "settings/flows/pipe.yml",
        "settings/project.yml",
    ]


def test_discover_all_pipeline_files_ignores_unsupported_recursive_glob() -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    fs = MagicMock()
    fs.exists.side_effect = lambda path: path in {
        "conf/project.yml",
        "conf/pipelines/pipe.yml",
    }
    fs.glob.side_effect = [
        ["pipelines/pipe.py"],
        NotImplementedError("recursive glob unsupported"),
    ]

    files = manager._discover_all_pipeline_files(fs)

    assert files == ["conf/pipelines/pipe.yml", "conf/project.yml", "pipelines/pipe.py"]


def test_discover_all_pipeline_files_includes_fallback_config_paths() -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        root = Path(tmpdir)
        (root / "conf").mkdir()
        (root / "pipelines").mkdir()
        (root / "conf" / "project.yml").write_text("name: demo\n")
        (root / "conf" / "my_pipeline.yml").write_text("name: my-pipeline\n")
        (root / "pipelines" / "my_pipeline.py").write_text("VALUE = 1\n")

        files = manager._discover_all_pipeline_files(fs)

    assert files == [
        "conf/my_pipeline.yml",
        "conf/project.yml",
        "pipelines/my_pipeline.py",
    ]


def test_discover_all_pipeline_files_prefers_single_project_and_pipeline_config() -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        root = Path(tmpdir)
        (root / "conf" / "pipelines").mkdir(parents=True)
        (root / "pipelines").mkdir()
        (root / "conf" / "project.yml").write_text("name: demo\n")
        (root / "conf" / "project.yaml").write_text("name: stale-demo\n")
        (root / "conf" / "pipelines" / "my_pipeline.yml").write_text(
            "name: my-pipeline\n"
        )
        (root / "conf" / "my_pipeline.yml").write_text("name: legacy-my-pipeline\n")
        (root / "pipelines" / "my_pipeline.py").write_text("VALUE = 1\n")

        files = manager._discover_all_pipeline_files(fs)

    assert files == [
        "conf/pipelines/my_pipeline.yml",
        "conf/project.yml",
        "pipelines/my_pipeline.py",
    ]


def test_discover_all_pipeline_files_skips_probe_errors_for_candidate_paths() -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    fs = MagicMock()

    def exists(path: str) -> bool:
        if path in {"conf/project.yml", "conf/pipelines/pipe.yml"}:
            raise PermissionError("denied")
        return path in {"conf/project.yaml", "conf/pipe.yml"}

    fs.exists.side_effect = exists
    fs.glob.side_effect = [["pipelines/pipe.py"], []]

    files = manager._discover_all_pipeline_files(fs)

    assert files == ["conf/pipe.yml", "conf/project.yaml", "pipelines/pipe.py"]


def test_sync_filesystem_handles_top_level_files_without_parent_dir() -> None:
    import tempfile
    from pathlib import Path

    registry = _make_registry()
    registry._cfg_dir = ""
    manager = PipelineIOManager(registry)

    with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as dest_dir:
        (Path(src_dir) / "project.yml").write_text("project: demo")

        manager._sync_filesystem(
            src_base_dir=src_dir,
            dest_base_dir=dest_dir,
            src_fs=None,
            dest_fs=None,
            files=["project.yml"],
            overwrite=True,
        )

        assert (Path(dest_dir) / "project.yml").read_text() == "project: demo"


def test_sync_filesystem_creates_missing_parent_dirs_with_makedirs() -> None:
    registry = _make_registry()
    manager = PipelineIOManager(registry)

    src_fs = MagicMock()
    src_fs.read_bytes.return_value = b"payload"

    dest_fs = MagicMock()
    dest_fs.exists.side_effect = lambda path: False

    with patch.object(
        manager,
        "_get_dir_filesystem",
        side_effect=[src_fs, dest_fs],
    ):
        manager._sync_filesystem(
            src_base_dir="src",
            dest_base_dir="dest",
            src_fs=None,
            dest_fs=None,
            files=["nested/file.txt"],
            overwrite=True,
        )

    dest_fs.makedirs.assert_called_once_with("nested", exist_ok=True)
    dest_fs.write_bytes.assert_called_once_with("nested/file.txt", b"payload")
