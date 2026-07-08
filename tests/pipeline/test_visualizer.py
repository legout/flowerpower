import sys
import tempfile
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
import yaml
from fsspeckit import filesystem

from flowerpower.pipeline.visualizer import PipelineVisualizer
from flowerpower.utils.security import SecurityError


def test_save_dag_defaults_to_project_graphs_directory() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()
    dag = MagicMock()

    visualizer = PipelineVisualizer(project_cfg=project_cfg, fs=fs)
    visualizer._get_dag_object = MagicMock(return_value=dag)

    result = visualizer.save_dag(name="example", format="svg")

    fs.makedirs.assert_called_once_with("./graphs", exist_ok=True)
    dag.render.assert_called_once_with(
        "./graphs/example",
        format="svg",
        cleanup=True,
        view=False,
    )
    assert result == "./graphs/example.svg"


def test_save_dag_status_message_omits_none_project_name() -> None:
    project_cfg = MagicMock()
    project_cfg.name = None
    fs = MagicMock()
    dag = MagicMock()

    visualizer = PipelineVisualizer(project_cfg=project_cfg, fs=fs)
    visualizer._get_dag_object = MagicMock(return_value=dag)

    with patch("flowerpower.pipeline.visualizer.print") as mock_print:
        visualizer.save_dag(name="example", format="svg")

    printed_message = mock_print.call_args[0][0]
    assert "None.example" not in printed_message
    assert "example" in printed_message


def test_save_dag_trims_surrounding_whitespace_from_pipeline_name() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()
    dag = MagicMock()

    visualizer = PipelineVisualizer(project_cfg=project_cfg, fs=fs)
    visualizer._get_dag_object = MagicMock(return_value=dag)

    result = visualizer.save_dag(name="  example  ", format="svg")

    visualizer._get_dag_object.assert_called_once_with(
        name="example",
        reload=False,
        additional_modules=None,
    )
    dag.render.assert_called_once_with(
        "./graphs/example",
        format="svg",
        cleanup=True,
        view=False,
    )
    assert result == "./graphs/example.svg"


def test_get_dag_object_uses_configured_dirs() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()
    pipeline_cfg = MagicMock()
    pipeline_cfg.run.config = {"mode": "test"}
    module = ModuleType("flows.example")
    dag = MagicMock()

    class FakeBuilder:
        def with_modules(self, *args, **_kwargs):
            assert len(args) == 1
            assert args[0] is module
            return self

        def enable_dynamic_execution(self, **_kwargs):
            return self

        def with_config(self, config):
            assert config == {"mode": "test"}
            return self

        def build(self):
            return MagicMock(display_all_functions=MagicMock(return_value=dag))

    visualizer = PipelineVisualizer(
        project_cfg=project_cfg,
        fs=fs,
        cfg_dir="settings",
        pipelines_dir="flows",
    )

    visualizer._config_manager.load_pipeline_config = MagicMock(
        return_value=pipeline_cfg
    )

    with patch.object(visualizer, "_resolve_modules", return_value=[module]):
        with patch(
            "flowerpower.pipeline.visualizer.driver.Builder", return_value=FakeBuilder()
        ):
            result = visualizer._get_dag_object(name="group.example")

    visualizer._config_manager.load_pipeline_config.assert_called_once_with(
        "group.example",
        reload=False,
    )
    assert result is dag


def test_visualizer_uses_base_dir_for_config_manager_and_module_path_setup() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()

    with patch(
        "flowerpower.pipeline.visualizer.PipelineConfigManager"
    ) as mock_config_manager:
        with patch(
            "flowerpower.pipeline.visualizer.add_modules_path"
        ) as mock_add_modules_path:
            PipelineVisualizer(
                project_cfg=project_cfg,
                fs=fs,
                base_dir="/project",
                cfg_dir="settings",
                pipelines_dir="flows",
            )

    mock_config_manager.assert_called_once_with(
        base_dir="/project",
        fs=fs,
        storage_options={},
        cfg_dir="settings",
        pipelines_dir="flows",
    )
    mock_add_modules_path.assert_called_once_with(fs, "flows", "/project")


def test_visualizer_preserves_empty_configured_dirs() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()

    with patch(
        "flowerpower.pipeline.visualizer.PipelineConfigManager"
    ) as mock_config_manager:
        with patch(
            "flowerpower.pipeline.visualizer.add_modules_path"
        ) as mock_add_modules_path:
            visualizer = PipelineVisualizer(
                project_cfg=project_cfg,
                fs=fs,
                cfg_dir="",
                pipelines_dir="",
            )

    assert visualizer._cfg_dir == ""
    assert visualizer._pipelines_dir == ""
    assert visualizer._module_resolver.package_root == ""
    mock_config_manager.assert_called_once_with(
        base_dir=".",
        fs=fs,
        storage_options={},
        cfg_dir="",
        pipelines_dir="",
    )
    mock_add_modules_path.assert_called_once_with(fs, "", ".")


def test_visualizer_rejects_traversal_pipeline_dirs() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()

    with pytest.raises(SecurityError):
        PipelineVisualizer(
            project_cfg=project_cfg,
            fs=fs,
            cfg_dir="../settings",
        )


def test_get_dag_object_trims_whitespace_before_module_resolution() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()
    pipeline_cfg = MagicMock()
    pipeline_cfg.run.config = {}
    module = ModuleType("flows.example")
    dag = MagicMock()

    class FakeBuilder:
        def with_modules(self, *args, **_kwargs):
            assert len(args) == 1
            assert args[0] is module
            return self

        def enable_dynamic_execution(self, **_kwargs):
            return self

        def with_config(self, config):
            assert config == {}
            return self

        def build(self):
            return MagicMock(display_all_functions=MagicMock(return_value=dag))

    visualizer = PipelineVisualizer(project_cfg=project_cfg, fs=fs)
    visualizer._config_manager.load_pipeline_config = MagicMock(
        return_value=pipeline_cfg
    )
    visualizer._resolve_modules = MagicMock(return_value=[module])

    with patch(
        "flowerpower.pipeline.visualizer.driver.Builder",
        return_value=FakeBuilder(),
    ):
        result = visualizer._get_dag_object(name="  example  ")

    visualizer._config_manager.load_pipeline_config.assert_called_once_with(
        "example",
        reload=False,
    )
    visualizer._resolve_modules.assert_called_once_with("example", None, False)
    assert result is dag


def test_get_dag_object_applies_env_overlays_via_config_manager() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        conf = Path(tmpdir) / "conf" / "pipelines"
        conf.mkdir(parents=True)
        with (Path(tmpdir) / "conf" / "project.yml").open("w") as fh:
            yaml.safe_dump({"name": "demo"}, fh)
        with (conf / "example.yml").open("w") as fh:
            yaml.safe_dump({"run": {"config": {"mode": "yaml"}}}, fh)

        project_cfg = MagicMock()
        project_cfg.name = "demo"
        visualizer = PipelineVisualizer(project_cfg=project_cfg, fs=fs)
        module = ModuleType("pipelines.example")
        dag = MagicMock()

        class FakeBuilder:
            def with_modules(self, *args, **_kwargs):
                return self

            def enable_dynamic_execution(self, **_kwargs):
                return self

            def with_config(self, config):
                assert config == {"mode": "env"}
                return self

            def build(self):
                return MagicMock(display_all_functions=MagicMock(return_value=dag))

        with patch.dict("os.environ", {"FP_PIPELINE__RUN__CONFIG__MODE": "env"}):
            with patch.object(visualizer, "_resolve_modules", return_value=[module]):
                with patch(
                    "flowerpower.pipeline.visualizer.driver.Builder",
                    return_value=FakeBuilder(),
                ):
                    result = visualizer._get_dag_object(name="example")

        assert result is dag


def test_visualizer_resolves_additional_modules_from_configured_pipeline_package() -> (
    None
):
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()
    module = ModuleType("flows.setup")

    visualizer = PipelineVisualizer(
        project_cfg=project_cfg,
        fs=fs,
        pipelines_dir="flows",
    )

    def fake_load(name: str, reload: bool = False):
        if name in ("setup", "flows.setup"):
            return module
        raise ImportError(name)

    with patch(
        "flowerpower.pipeline.module_resolver.load_module", side_effect=fake_load
    ):
        result = visualizer._coerce_to_module("setup")

    assert result is module


def test_visualizer_resolves_additional_modules_from_nested_pipeline_package() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()
    module = ModuleType("pkg.flows.setup")

    visualizer = PipelineVisualizer(
        project_cfg=project_cfg,
        fs=fs,
        pipelines_dir="pkg/flows",
    )

    def fake_load(name: str, reload: bool = False):
        if name in ("setup", "pkg.flows.setup"):
            return module
        raise ImportError(name)

    with patch(
        "flowerpower.pipeline.module_resolver.load_module", side_effect=fake_load
    ):
        result = visualizer._coerce_to_module("setup")

    assert result is module


def test_visualizer_standalone_adds_project_path_for_nested_pipeline_package() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    package_root = "zzvisualizerpkg"

    with tempfile.TemporaryDirectory() as tmpdir:
        fs = filesystem(tmpdir, cached=False, dirfs=True)
        root = Path(tmpdir)
        (root / package_root / "flows").mkdir(parents=True)
        (root / package_root / "__init__.py").write_text("")
        (root / package_root / "flows" / "__init__.py").write_text("")
        (root / package_root / "flows" / "example.py").write_text("VALUE = 1\n")

        original = list(sys.path)
        try:
            sys.path[:] = [path for path in sys.path if tmpdir not in str(path)]
            visualizer = PipelineVisualizer(
                project_cfg=project_cfg,
                fs=fs,
                pipelines_dir=f"{package_root}/flows",
            )
            module = visualizer._coerce_to_module("example")
        finally:
            sys.path[:] = original

    assert module.__name__ == f"{package_root}.flows.example"
    assert module.VALUE == 1


def test_visualizer_reload_reloads_unique_primary_and_additional_modules() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()
    visualizer = PipelineVisualizer(project_cfg=project_cfg, fs=fs)

    setup_module = ModuleType("pipelines.setup")
    primary_module = ModuleType("pipelines.example")

    def fake_load(name: str, reload: bool = False):
        if name == "pipelines.example":
            return primary_module
        raise ModuleNotFoundError(f"No module named {name!r}", name=name)

    with patch(
        "flowerpower.pipeline.module_resolver.load_module", side_effect=fake_load
    ):
        with patch(
            "flowerpower.pipeline.module_resolver.importlib.reload"
        ) as reload_module:
            result = visualizer._resolve_modules(
                "example",
                [setup_module, setup_module],
                reload=True,
            )

    assert result == [setup_module, primary_module]
    assert [call.args[0] for call in reload_module.call_args_list] == [
        setup_module,
        primary_module,
    ]
