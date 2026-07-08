import datetime as dt
import posixpath
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml
from fsspeckit import AbstractFileSystem, filesystem

from flowerpower.cfg import PipelineConfig, ProjectConfig
from flowerpower.pipeline.catalog import PipelineCatalog
from flowerpower.utils.security import SecurityError


# --- Fixtures ---


@pytest.fixture
def mock_fs():
    """Fixture for a mocked AbstractFileSystem."""
    fs = MagicMock(spec=AbstractFileSystem)
    fs.exists = MagicMock(return_value=True)
    fs.open = mock_open()
    fs.makedirs = MagicMock()
    fs.rm = MagicMock()
    fs.glob = MagicMock(return_value=[])
    fs.ls = MagicMock(return_value=[])
    fs.modified = MagicMock(return_value=dt.datetime.now())
    fs.size = MagicMock(return_value=1024)
    fs.cat = MagicMock(return_value=b"")
    return fs


@pytest.fixture
def mock_project_cfg():
    """Fixture for a mocked ProjectConfig."""
    cfg = MagicMock(spec=ProjectConfig)
    cfg.name = "test_project"
    cfg.to_dict = MagicMock(return_value={"name": "test_project", "version": "0.1"})
    return cfg


@pytest.fixture
def mock_pipeline_cfg_instance():
    """Fixture for a mocked PipelineConfig instance."""
    cfg_instance = MagicMock(spec=PipelineConfig)
    cfg_instance.name = "test_pipeline"
    cfg_instance.to_dict = MagicMock(
        return_value={"name": "test_pipeline", "version": "1.0"}
    )
    return cfg_instance


@pytest.fixture
def catalog(mock_fs, mock_project_cfg):
    """Fixture for a PipelineCatalog instance."""
    return PipelineCatalog(
        fs=mock_fs,
        cfg_dir="conf",
        pipelines_dir="pipelines",
        project_cfg=mock_project_cfg,
        config_provider=lambda name: MagicMock(spec=PipelineConfig, to_dict=MagicMock(return_value={"name": name})),
        project_cfg_provider=lambda: mock_project_cfg,
    )


# --- Test Cases ---


class TestPipelineCatalog:
    def test_initialization(self, catalog, mock_fs, mock_project_cfg):
        assert catalog._fs == mock_fs
        assert catalog._cfg_dir == "conf"
        assert catalog._pipelines_dir == "pipelines"
        assert catalog._project_cfg == mock_project_cfg

    def test_get_files_and_names(self, catalog, mock_fs):
        mock_fs.glob.return_value = [
            posixpath.join(catalog._pipelines_dir, "pipe1.py"),
            posixpath.join(catalog._pipelines_dir, "pipe2.py"),
        ]

        files = catalog.get_files()
        assert len(files) == 2
        assert posixpath.join(catalog._pipelines_dir, "pipe1.py") in files

        names = catalog.get_names()
        assert sorted(names) == sorted(["pipe1", "pipe2"])

    def test_get_names_discovers_nested_modules(self, catalog, mock_fs):
        mock_fs.glob.side_effect = [
            [posixpath.join(catalog._pipelines_dir, "top_level.py")],
            [posixpath.join(catalog._pipelines_dir, "group", "nested_pipe.py")],
        ]

        assert catalog.get_names() == ["group.nested_pipe", "top_level"]

    def test_get_names_prefers_stored_pipeline_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)
            pipelines_dir = Path(tmpdir) / "pipelines" / "group"
            config_dir = Path(tmpdir) / "conf" / "pipelines" / "group"
            pipelines_dir.mkdir(parents=True)
            config_dir.mkdir(parents=True)
            (pipelines_dir / "my_pipeline.py").write_text("def x():\n    return 1\n")
            with (config_dir / "my_pipeline.yml").open("w") as fh:
                yaml.safe_dump({"name": "group.my-pipeline"}, fh)

            catalog = PipelineCatalog(
                fs=fs,
                cfg_dir="conf",
                pipelines_dir="pipelines",
            )

            assert catalog.get_names() == ["group.my-pipeline"]

    def test_read_stored_pipeline_name_skips_probe_errors(self, catalog, mock_fs):
        def exists(path: str) -> bool:
            if path == "conf/pipelines/group/my_pipeline.yml":
                raise PermissionError("denied")
            return path == "conf/group/my_pipeline.yml"

        mock_fs.exists.side_effect = exists
        mock_fs.open = MagicMock()
        mock_fs.open.return_value.__enter__.return_value = "name: group.my-pipeline\n"

        assert catalog.read_stored_pipeline_name("group/my_pipeline") == "group.my-pipeline"

    def test_get_files_fs_error(self, catalog, mock_fs):
        mock_fs.glob.side_effect = Exception("FS error")

        with patch("flowerpower.pipeline.catalog.logger.error") as mock_logger_error:
            assert catalog.get_files() == []
            mock_logger_error.assert_called_once()

    def test_get_files_ignores_unsupported_recursive_glob(self, catalog, mock_fs):
        mock_fs.glob.side_effect = [
            [posixpath.join(catalog._pipelines_dir, "top_level.py")],
            NotImplementedError("recursive glob unsupported"),
        ]

        assert catalog.get_files() == [
            posixpath.join(catalog._pipelines_dir, "top_level.py")
        ]

    def test_list_pipelines_returns_names_only(self, catalog, mock_fs):
        mock_fs.glob.side_effect = [
            [posixpath.join(catalog._pipelines_dir, "pipe1.py")],
            [posixpath.join(catalog._pipelines_dir, "group", "pipe2.py")],
        ]

        assert catalog.list_pipelines() == ["group.pipe2", "pipe1"]

    def test_pipelines_property_returns_names_only(self, catalog, mock_fs):
        mock_fs.glob.side_effect = [
            [posixpath.join(catalog._pipelines_dir, "pipe1.py")],
            [posixpath.join(catalog._pipelines_dir, "group", "pipe2.py")],
        ]

        assert catalog.pipelines == ["group.pipe2", "pipe1"]

    def test_list_pipeline_info_and_collect_pipeline_info(self, catalog, mock_fs):
        file_infos = [
            {
                "name": "p1",
                "path": posixpath.join(catalog._pipelines_dir, "p1.py"),
                "mod_time": "t1",
                "size": "s1",
            },
            {
                "name": "p2",
                "path": posixpath.join(catalog._pipelines_dir, "p2.py"),
                "mod_time": "t2",
                "size": "s2",
            },
        ]

        mock_fs.glob.side_effect = [[info["path"] for info in file_infos], []]

        def mock_modified_side_effect(path):
            if path.endswith("p1.py"):
                return dt.datetime.strptime("2023-01-01 10:00:00", "%Y-%m-%d %H:%M:%S")
            if path.endswith("p2.py"):
                return dt.datetime.strptime("2023-01-02 11:00:00", "%Y-%m-%d %H:%M:%S")
            return dt.datetime.now()

        def mock_size_side_effect(path):
            if path.endswith("p1.py"):
                return 1000
            if path.endswith("p2.py"):
                return 2000
            return 0

        mock_fs.modified.side_effect = mock_modified_side_effect
        mock_fs.size.side_effect = mock_size_side_effect

        result = catalog.list_pipeline_info()

        assert len(result) == 2
        assert any(item["name"] == "p1" and item["size"] == "1.0 KB" for item in result)
        assert any(item["name"] == "p2" and item["size"] == "2.0 KB" for item in result)

        # collect_pipeline_info is the same implementation
        mock_fs.glob.side_effect = [[info["path"] for info in file_infos], []]
        collect_result = catalog.collect_pipeline_info()
        assert len(collect_result) == 2
        assert any(
            item["name"] == "p1" and item["size"] == "1.0 KB" for item in collect_result
        )
        assert any(
            item["name"] == "p2" and item["size"] == "2.0 KB" for item in collect_result
        )

    def test_get_summary_single_pipeline(
        self, catalog, mock_fs, mock_project_cfg, mock_pipeline_cfg_instance
    ):
        pipeline_name = "summary_pipe"

        mock_fs.glob.return_value = [
            posixpath.join(catalog._pipelines_dir, f"{pipeline_name}.py")
        ]
        mock_fs.cat.return_value = b"pipeline_code_content"

        def config_provider(name):
            assert name == pipeline_name
            return mock_pipeline_cfg_instance

        catalog._config_provider = config_provider

        summary = catalog.get_summary(
            name=pipeline_name, cfg=True, code=True, project=True
        )

        assert "project" in summary
        assert summary["project"] == {"name": "test_project", "version": "0.1"}
        assert pipeline_name in summary["pipelines"]
        assert (
            summary["pipelines"][pipeline_name]["cfg"]
            == mock_pipeline_cfg_instance.to_dict()
        )
        assert summary["pipelines"][pipeline_name]["module"] == "pipeline_code_content"

        mock_fs.cat.assert_called_once_with(
            posixpath.join(catalog._pipelines_dir, f"{pipeline_name}.py")
        )

    def test_get_summary_uses_formatted_module_path_for_dotted_pipeline(
        self, catalog, mock_fs, mock_pipeline_cfg_instance
    ):
        pipeline_name = "group.my-pipeline"
        mock_fs.cat.return_value = b"pipeline_code_content"

        catalog._config_provider = lambda name: mock_pipeline_cfg_instance

        catalog.get_summary(name=pipeline_name, cfg=True, code=True, project=False)

        mock_fs.cat.assert_called_once_with(
            posixpath.join(catalog._pipelines_dir, "group", "my_pipeline.py")
        )

    def test_get_summary_all_pipelines(
        self, catalog, mock_fs, mock_project_cfg, mock_pipeline_cfg_instance
    ):
        mock_fs.glob.return_value = [
            posixpath.join(catalog._pipelines_dir, "pipe1.py"),
            posixpath.join(catalog._pipelines_dir, "pipe2.py"),
        ]

        mock_config1 = MagicMock(spec=PipelineConfig)
        mock_config1.name = "pipe1"
        mock_config1.to_dict.return_value = {"name": "pipe1"}
        mock_config2 = MagicMock(spec=PipelineConfig)
        mock_config2.name = "pipe2"
        mock_config2.to_dict.return_value = {"name": "pipe2"}

        def config_provider(name):
            return mock_config1 if name == "pipe1" else mock_config2

        catalog._config_provider = config_provider

        mock_fs.cat.side_effect = lambda path: b"code_for_" + bytes(
            posixpath.basename(path).split(".")[0], "utf-8"
        )

        summary = catalog.get_summary(cfg=True, code=True, project=False)

        assert "project" not in summary
        assert "pipe1" in summary["pipelines"]
        assert summary["pipelines"]["pipe1"]["cfg"] == {"name": "pipe1"}
        assert summary["pipelines"]["pipe1"]["module"] == "code_for_pipe1"
        assert "pipe2" in summary["pipelines"]
        assert summary["pipelines"]["pipe2"]["cfg"] == {"name": "pipe2"}
        assert summary["pipelines"]["pipe2"]["module"] == "code_for_pipe2"
