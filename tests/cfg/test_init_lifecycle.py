from unittest.mock import MagicMock, patch

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


def test_project_config_from_yaml_runs_post_init_once() -> None:
    fs = MagicMock()
    fs.open.return_value.__enter__.return_value.read.return_value = (
        "name: demo\nhooks_dir: hooks\n"
    )

    with patch(
        "flowerpower.cfg.project.security_validate_file_path",
        wraps=validate_file_path,
    ) as mock_validate_hooks_dir:
        cfg = ProjectConfig.from_yaml("conf/project.yml", fs)

    assert cfg.name == "demo"
    assert cfg.hooks_dir == "hooks"
    assert mock_validate_hooks_dir.call_count == 1
