from pathlib import Path
from unittest.mock import MagicMock, patch

from flowerpower.cfg import Config
from flowerpower.cfg.exceptions import ConfigLoadError
from flowerpower.cfg.pipeline import PipelineConfig
from flowerpower.cfg.project import ProjectConfig
from flowerpower.utils.security import validate_file_path


def test_pipeline_config_from_dict_runs_post_init_once() -> None:
    with patch.object(
        PipelineConfig,
        "to_h_params",
        wraps=PipelineConfig.to_h_params,
    ) as mock_to_h_params:
        cfg = PipelineConfig.from_dict(
            "demo",
            {"params": {"value": 1}},
        )

    assert cfg.name == "demo"
    assert mock_to_h_params.call_count == 1


def test_loaded_pipeline_h_params_support_attribute_and_mapping_access(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "conf" / "pipelines" / "raw_to_stage1.yml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text("params:\n  fs:\n    name: mdsp\n")

    cfg = Config.load(str(tmp_path), pipeline_name="raw_to_stage1")

    assert cfg.pipeline.h_params.fs is cfg.pipeline.h_params["fs"]
    assert {**cfg.pipeline.h_params.fs} == {"fs": cfg.pipeline.h_params.fs["fs"]}
    config_dict = cfg.to_dict()
    pipeline_dict = config_dict["pipeline"]
    assert isinstance(pipeline_dict, dict)
    assert isinstance(pipeline_dict["h_params"], dict)


def test_project_config_from_yaml_runs_post_init_once() -> None:
    fs = MagicMock()
    fs.open.return_value.__enter__.return_value.read.return_value = (
        "name: demo\nhooks_dir: hooks\n"
    )

    with patch(
        "flowerpower.cfg.project.validate_file_path",
        wraps=validate_file_path,
    ) as mock_validate_hooks_dir:
        cfg = ProjectConfig.from_yaml("conf/project.yml", fs)

    assert cfg.name == "demo"
    assert cfg.hooks_dir == "hooks"
    assert mock_validate_hooks_dir.call_count == 2


def test_project_config_from_yaml_wraps_validation_errors() -> None:
    fs = MagicMock()
    fs.open.return_value.__enter__.return_value.read.return_value = (
        "name: demo\nhooks_dir: ../escape\n"
    )

    try:
        ProjectConfig.from_yaml("conf/project.yml", fs)
    except ConfigLoadError as exc:
        assert "Failed to validate configuration" in str(exc)
    else:
        raise AssertionError("Expected ConfigLoadError for invalid hooks_dir")
