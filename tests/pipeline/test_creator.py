import datetime as dt
import posixpath
from unittest.mock import call

import pytest
from fsspeckit import AbstractFileSystem

from flowerpower.cfg import PipelineConfig, ProjectConfig
from flowerpower.pipeline.creator import PipelineCreator


@pytest.fixture
def mock_fs(mocker):
    """Fixture for a mocked AbstractFileSystem."""
    fs = mocker.MagicMock(spec=AbstractFileSystem)
    fs.exists = mocker.MagicMock(return_value=True)
    fs.open = mocker.mock_open()
    fs.makedirs = mocker.MagicMock()
    fs.rm = mocker.MagicMock()
    fs.glob = mocker.MagicMock(return_value=[])
    fs.ls = mocker.MagicMock(return_value=[])
    fs.modified = mocker.MagicMock(return_value=dt.datetime.now())
    fs.size = mocker.MagicMock(return_value=1024)
    fs.cat = mocker.MagicMock(return_value=b"")
    return fs


@pytest.fixture
def mock_project_cfg(mocker):
    """Fixture for a mocked ProjectConfig."""
    cfg = mocker.MagicMock(spec=ProjectConfig)
    cfg.name = "test_project"
    cfg.to_dict = mocker.MagicMock(
        return_value={"name": "test_project", "version": "0.1"}
    )
    return cfg


@pytest.fixture
def mock_pipeline_cfg_instance(mocker):
    """Fixture for a mocked PipelineConfig instance."""
    cfg_instance = mocker.MagicMock(spec=PipelineConfig)
    cfg_instance.name = "test_pipeline"
    cfg_instance.version = "1.0"
    cfg_instance.to_dict = mocker.MagicMock(
        return_value={"name": "test_pipeline", "version": "1.0"}
    )
    cfg_instance.save = mocker.MagicMock()
    return cfg_instance


@pytest.fixture
def creator(mock_project_cfg, mock_fs):
    """Fixture for PipelineCreator instance."""
    return PipelineCreator(
        project_cfg=mock_project_cfg,
        fs=mock_fs,
    )


class TestPipelineCreator:
    def test_initialization(self, creator, mock_project_cfg, mock_fs):
        assert creator.project_cfg == mock_project_cfg
        assert creator._fs == mock_fs
        assert creator._cfg_dir == "conf"
        assert creator._pipelines_dir == "pipelines"

    # --- Tests for new() method ---
    def test_new_pipeline_success(
        self, creator, mock_fs, mock_pipeline_cfg_instance, mocker
    ):
        pipeline_name = "my_new_pipeline"
        formatted_name = "my_new_pipeline"

        mock_fs.exists.side_effect = lambda p: p in {"conf", "pipelines"}

        mocker.patch(
            "flowerpower.pipeline.creator.PipelineConfig",
            return_value=mock_pipeline_cfg_instance,
        )

        creator.new(pipeline_name)

        expected_pipeline_file = posixpath.join(
            creator._pipelines_dir, f"{formatted_name}.py"
        )
        expected_cfg_file = posixpath.join(
            creator._cfg_dir, "pipelines", f"{formatted_name}.yml"
        )

        mock_fs.makedirs.assert_any_call(
            posixpath.dirname(expected_pipeline_file), exist_ok=True
        )
        mock_fs.makedirs.assert_any_call(
            posixpath.dirname(expected_cfg_file), exist_ok=True
        )
        mock_fs.open.assert_any_call(expected_pipeline_file, "w")
        handle = mock_fs.open()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        assert "_resolve_base_dir()" in written
        assert "project.yml" in written
        assert "project.yaml" in written
        assert "from flowerpower.utils.misc import dict_to_namespace" in written
        assert "PARAMS = dict_to_namespace(" in written

        from flowerpower.pipeline.creator import PipelineConfig as ActualPipelineConfig

        ActualPipelineConfig.assert_called_once_with(name=pipeline_name)
        mock_pipeline_cfg_instance.save.assert_called_once_with(
            fs=mock_fs, cfg_dir=creator._cfg_dir, pipelines_dir=creator._pipelines_dir
        )

    def test_new_pipeline_trims_surrounding_whitespace(self, creator, mock_fs, mock_pipeline_cfg_instance, mocker):
        pipeline_name = "  my_new_pipeline  "
        formatted_name = "my_new_pipeline"

        mock_fs.exists.side_effect = lambda p: p in {"conf", "pipelines"}

        mocker.patch(
            "flowerpower.pipeline.creator.PipelineConfig",
            return_value=mock_pipeline_cfg_instance,
        )

        creator.new(pipeline_name)

        mock_fs.open.assert_any_call(posixpath.join(creator._pipelines_dir, f"{formatted_name}.py"), "w")
        from flowerpower.pipeline.creator import PipelineConfig as ActualPipelineConfig
        ActualPipelineConfig.assert_called_once_with(name=formatted_name)
        mock_pipeline_cfg_instance.save.assert_called_once_with(
            fs=mock_fs, cfg_dir=creator._cfg_dir, pipelines_dir=creator._pipelines_dir
        )

    def test_new_pipeline_base_dirs_do_not_exist(self, creator, mock_fs):
        mock_fs.exists.side_effect = lambda p: False

        with pytest.raises(
            ValueError, match="Configuration path conf does not exist."
        ):
            creator.new("test_pipe")

        mock_fs.exists.side_effect = None
        mock_fs.exists.return_value = True

    def test_new_pipeline_already_exists_no_overwrite(self, creator, mock_fs):
        pipeline_name = "existing_pipe"

        with pytest.raises(
            ValueError, match=f"Pipeline test_project.{pipeline_name} already exists."
        ):
            creator.new(pipeline_name)

    def test_new_pipeline_rejects_existing_legacy_fallback_config(
        self, creator, mock_fs
    ):
        mock_fs.exists.side_effect = lambda path: path in {
            "conf",
            "pipelines",
            "conf/existing_pipe.yml",
        }

        with pytest.raises(
            ValueError, match="Pipeline test_project.existing_pipe already exists"
        ):
            creator.new("existing_pipe")

    def test_new_pipeline_skips_probe_errors_and_detects_fallback_config(
        self, creator, mock_fs
    ):
        def exists(path: str) -> bool:
            if path in {"conf", "pipelines"}:
                return True
            if path == "conf/pipelines/existing_pipe.yml":
                raise PermissionError("denied")
            return path == "conf/existing_pipe.yml"

        mock_fs.exists.side_effect = exists

        with pytest.raises(
            ValueError, match="Pipeline test_project.existing_pipe already exists"
        ):
            creator.new("existing_pipe")

    def test_new_pipeline_already_exists_with_overwrite(
        self, creator, mock_fs, mock_pipeline_cfg_instance, mocker
    ):
        pipeline_name = "existing_pipe"
        formatted_name = "existing_pipe"

        mocker.patch(
            "flowerpower.pipeline.creator.PipelineConfig",
            return_value=mock_pipeline_cfg_instance,
        )

        creator.new(pipeline_name, overwrite=True)

        expected_pipeline_file = posixpath.join(
            creator._pipelines_dir, f"{formatted_name}.py"
        )
        expected_cfg_file = posixpath.join(
            creator._cfg_dir, "pipelines", f"{formatted_name}.yml"
        )

        mock_fs.rm.assert_any_call(expected_pipeline_file)
        mock_fs.rm.assert_any_call(expected_cfg_file)
        mock_fs.open.assert_any_call(expected_pipeline_file, "w")
        mock_pipeline_cfg_instance.save.assert_called_once_with(
            fs=mock_fs, cfg_dir=creator._cfg_dir, pipelines_dir=creator._pipelines_dir
        )

    def test_new_pipeline_allows_empty_config_dir(
        self, mock_project_cfg, mock_fs, mock_pipeline_cfg_instance, mocker
    ):
        creator = PipelineCreator(
            project_cfg=mock_project_cfg,
            fs=mock_fs,
            cfg_dir="",
            pipelines_dir="flows",
        )

        mock_fs.exists.side_effect = lambda path: path in {".", "flows"}
        mocker.patch(
            "flowerpower.pipeline.creator.PipelineConfig",
            return_value=mock_pipeline_cfg_instance,
        )

        creator.new("group.my-pipeline")

        mock_fs.open.assert_any_call("flows/group/my_pipeline.py", "w")
        mock_pipeline_cfg_instance.save.assert_called_once_with(
            fs=mock_fs,
            cfg_dir="",
            pipelines_dir="flows",
        )

    # --- Tests for delete() method ---
    def test_delete_pipeline_success_cfg_and_module(self, creator, mock_fs):
        pipeline_name = "pipe_to_delete"

        creator.delete(pipeline_name, cfg=True, module=True)

        expected_cfg_path = posixpath.join(
            creator._cfg_dir, "pipelines", f"{pipeline_name}.yml"
        )
        expected_py_path = posixpath.join(
            creator._pipelines_dir, f"{pipeline_name}.py"
        )

        mock_fs.rm.assert_any_call(expected_cfg_path)
        mock_fs.rm.assert_any_call(expected_py_path)

    def test_delete_pipeline_only_cfg(self, creator, mock_fs):
        pipeline_name = "pipe_to_delete_cfg"
        mock_fs.exists.side_effect = lambda path: path == posixpath.join(
            creator._cfg_dir, "pipelines", f"{pipeline_name}.yml"
        )
        creator.delete(pipeline_name, cfg=True, module=False)

        expected_cfg_path = posixpath.join(
            creator._cfg_dir, "pipelines", f"{pipeline_name}.yml"
        )
        expected_py_path = posixpath.join(
            creator._pipelines_dir, f"{pipeline_name}.py"
        )

        mock_fs.rm.assert_called_once_with(expected_cfg_path)
        calls = [call(expected_py_path)]
        mock_fs.rm.assert_has_calls([call(expected_cfg_path)], any_order=True)
        for c in calls:
            assert c not in mock_fs.rm.call_args_list

    def test_delete_pipeline_removes_legacy_fallback_config(self, creator, mock_fs):
        pipeline_name = "pipe_to_delete_cfg"
        legacy_cfg_path = posixpath.join(creator._cfg_dir, f"{pipeline_name}.yml")
        canonical_cfg_path = posixpath.join(
            creator._cfg_dir, "pipelines", f"{pipeline_name}.yml"
        )

        mock_fs.exists.side_effect = lambda path: path in {legacy_cfg_path}

        creator.delete(pipeline_name, cfg=True, module=False)

        mock_fs.rm.assert_called_once_with(legacy_cfg_path)
        assert call(canonical_cfg_path) not in mock_fs.rm.call_args_list

    def test_delete_pipeline_skips_probe_errors_and_removes_fallback_config(
        self, creator, mock_fs
    ):
        pipeline_name = "pipe_to_delete_cfg"
        legacy_cfg_path = posixpath.join(creator._cfg_dir, f"{pipeline_name}.yml")

        def exists(path: str) -> bool:
            if path == posixpath.join(
                creator._cfg_dir, "pipelines", f"{pipeline_name}.yml"
            ):
                raise PermissionError("denied")
            return path == legacy_cfg_path

        mock_fs.exists.side_effect = exists

        creator.delete(pipeline_name, cfg=True, module=False)

        mock_fs.rm.assert_called_once_with(legacy_cfg_path)

    def test_delete_pipeline_files_not_found(self, creator, mock_fs, mocker):
        pipeline_name = "non_existent_pipe"
        mock_fs.exists.return_value = False

        mock_logger_warning = mocker.patch(
            "flowerpower.pipeline.creator.logger.warning"
        )

        creator.delete(pipeline_name, cfg=True, module=True)

        mock_fs.rm.assert_not_called()

        expected_cfg_path = posixpath.join(
            creator._cfg_dir, "pipelines", f"{pipeline_name}.yml"
        )
        expected_py_path = posixpath.join(
            creator._pipelines_dir, f"{pipeline_name}.py"
        )

        mock_logger_warning.assert_any_call(
            f"Config file not found, skipping deletion: {expected_cfg_path}"
        )
        mock_logger_warning.assert_any_call(
            f"Module file not found, skipping deletion: {expected_py_path}"
        )
        mock_logger_warning.assert_any_call(
            f"No files found or specified for deletion for pipeline '{pipeline_name}'."
        )

    # --- Tests for compatibility aliases ---
    def test_create_pipeline_alias(self, creator, mocker):
        mock_new = mocker.patch.object(creator, "new")
        creator.create_pipeline(name="test_pipe", overwrite=True)
        mock_new.assert_called_once_with(name="test_pipe", overwrite=True)

    def test_delete_pipeline_alias(self, creator, mocker):
        mock_delete = mocker.patch.object(creator, "delete")
        creator.delete_pipeline(name="test_pipe", cfg=True, module=False)
        mock_delete.assert_called_once_with(name="test_pipe", cfg=True, module=False)


class TestPipelineNameFormatting:
    """Tests for consistent name formatting between new() and delete()."""

    def test_new_and_delete_with_hyphenated_name(self, mocker):
        pipeline_name = "my-pipeline"
        expected_formatted_name = "my_pipeline"

        mock_fs = mocker.MagicMock(spec=AbstractFileSystem)
        mock_fs.makedirs = mocker.MagicMock()
        mock_fs.rm = mocker.MagicMock()
        mock_fs.open = mocker.mock_open()

        mock_project_cfg = mocker.MagicMock(spec=ProjectConfig)
        mock_project_cfg.name = "test_project"

        mock_cfg_instance = mocker.MagicMock(spec=PipelineConfig)
        mock_cfg_instance.save = mocker.MagicMock()

        mocker.patch(
            "flowerpower.pipeline.creator.PipelineConfig",
            return_value=mock_cfg_instance,
        )

        creator = PipelineCreator(project_cfg=mock_project_cfg, fs=mock_fs)

        def exists_side_effect(path):
            if expected_formatted_name in path:
                return False
            return True

        mock_fs.exists.side_effect = exists_side_effect

        creator.new(pipeline_name)

        expected_pipeline_file = posixpath.join(
            creator._pipelines_dir, f"{expected_formatted_name}.py"
        )
        expected_cfg_file = posixpath.join(
            creator._cfg_dir, "pipelines", f"{expected_formatted_name}.yml"
        )
        mock_fs.open.assert_any_call(expected_pipeline_file, "w")
        mock_cfg_instance.save.assert_called_once_with(
            fs=mock_fs, cfg_dir=creator._cfg_dir, pipelines_dir=creator._pipelines_dir
        )

        mock_fs.reset_mock()
        mock_fs.exists.return_value = True
        mock_fs.exists.side_effect = None

        creator.delete(pipeline_name, cfg=True, module=True)

        mock_fs.rm.assert_any_call(expected_cfg_file)
        mock_fs.rm.assert_any_call(expected_pipeline_file)

    def test_new_and_delete_with_dotted_name(self, mocker):
        pipeline_name = "sub.module"
        expected_formatted_name = "sub/module"

        mock_fs = mocker.MagicMock(spec=AbstractFileSystem)
        mock_fs.makedirs = mocker.MagicMock()
        mock_fs.rm = mocker.MagicMock()
        mock_fs.open = mocker.mock_open()

        mock_project_cfg = mocker.MagicMock(spec=ProjectConfig)
        mock_project_cfg.name = "test_project"

        mock_cfg_instance = mocker.MagicMock(spec=PipelineConfig)
        mock_cfg_instance.save = mocker.MagicMock()

        mocker.patch(
            "flowerpower.pipeline.creator.PipelineConfig",
            return_value=mock_cfg_instance,
        )

        creator = PipelineCreator(project_cfg=mock_project_cfg, fs=mock_fs)

        def exists_side_effect(path):
            if expected_formatted_name in path:
                return False
            return True

        mock_fs.exists.side_effect = exists_side_effect

        creator.new(pipeline_name)

        expected_pipeline_file = posixpath.join(
            creator._pipelines_dir, f"{expected_formatted_name}.py"
        )
        expected_cfg_file = posixpath.join(
            creator._cfg_dir, "pipelines", f"{expected_formatted_name}.yml"
        )
        mock_fs.open.assert_any_call(expected_pipeline_file, "w")
        mock_cfg_instance.save.assert_called_once_with(
            fs=mock_fs, cfg_dir=creator._cfg_dir, pipelines_dir=creator._pipelines_dir
        )

        mock_fs.reset_mock()
        mock_fs.exists.return_value = True
        mock_fs.exists.side_effect = None

        creator.delete(pipeline_name, cfg=True, module=True)

        mock_fs.rm.assert_any_call(expected_cfg_file)
        mock_fs.rm.assert_any_call(expected_pipeline_file)

    def test_new_and_delete_with_mixed_special_chars(self, mocker):
        pipeline_name = "my-pipeline.sub-module"
        expected_formatted_name = "my_pipeline/sub_module"

        mock_fs = mocker.MagicMock(spec=AbstractFileSystem)
        mock_fs.makedirs = mocker.MagicMock()
        mock_fs.rm = mocker.MagicMock()
        mock_fs.open = mocker.mock_open()

        mock_project_cfg = mocker.MagicMock(spec=ProjectConfig)
        mock_project_cfg.name = "test_project"

        mock_cfg_instance = mocker.MagicMock(spec=PipelineConfig)
        mock_cfg_instance.save = mocker.MagicMock()

        mocker.patch(
            "flowerpower.pipeline.creator.PipelineConfig",
            return_value=mock_cfg_instance,
        )

        creator = PipelineCreator(project_cfg=mock_project_cfg, fs=mock_fs)

        def exists_side_effect(path):
            if expected_formatted_name in path:
                return False
            return True

        mock_fs.exists.side_effect = exists_side_effect

        creator.new(pipeline_name)

        expected_pipeline_file = posixpath.join(
            creator._pipelines_dir, f"{expected_formatted_name}.py"
        )
        expected_cfg_file = posixpath.join(
            creator._cfg_dir, "pipelines", f"{expected_formatted_name}.yml"
        )
        mock_fs.open.assert_any_call(expected_pipeline_file, "w")
        mock_cfg_instance.save.assert_called_once_with(
            fs=mock_fs, cfg_dir=creator._cfg_dir, pipelines_dir=creator._pipelines_dir
        )

        mock_fs.reset_mock()
        mock_fs.exists.return_value = True
        mock_fs.exists.side_effect = None

        creator.delete(pipeline_name, cfg=True, module=True)

        mock_fs.rm.assert_any_call(expected_cfg_file)
        mock_fs.rm.assert_any_call(expected_pipeline_file)
