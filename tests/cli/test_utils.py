import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from flowerpower.cli.utils import load_hook, parse_dict_or_list_param


def test_parse_dict_or_list_param_splits_comma_separated_lists_cleanly() -> None:
    assert parse_dict_or_list_param("spend_mean,spend_std_dev", "list") == [
        "spend_mean",
        "spend_std_dev",
    ]


def test_parse_dict_or_list_param_strips_whitespace_in_key_value_pairs() -> None:
    assert parse_dict_or_list_param(
        "anon=true, endpoint=https://example.invalid",
        "dict",
    ) == {
        "anon": True,
        "endpoint": "https://example.invalid",
    }


@patch("flowerpower.cli.utils.importlib.util.module_from_spec")
@patch("flowerpower.cli.utils.importlib.util.spec_from_file_location")
@patch("flowerpower.cli.utils.os.path.exists", return_value=True)
def test_load_hook_uses_project_configured_hooks_dir(
    _mock_exists: MagicMock,
    mock_spec_from_file_location: MagicMock,
    mock_module_from_spec: MagicMock,
) -> None:
    mock_pm = MagicMock()
    mock_pm._fs.path = "/project"
    mock_pm.registry._hooks_dir = "custom_hooks"
    mock_pm._fs_helper.get_project_path.return_value = "/resolved-project"

    manager_context = MagicMock()
    manager_context.__enter__.return_value = mock_pm
    manager_context.__exit__.return_value = False

    spec = MagicMock()
    spec.loader = MagicMock()
    mock_spec_from_file_location.return_value = spec

    hook_module = SimpleNamespace(my_hook=lambda: "ok")
    mock_module_from_spec.return_value = hook_module

    with patch("flowerpower.cli.utils.PipelineManager", return_value=manager_context):
        hook = load_hook("pipeline_name", "pkg.module.my_hook")

    assert hook() == "ok"
    mock_spec_from_file_location.assert_called_once_with(
        "module",
        "/resolved-project/custom_hooks/pipeline_name/pkg/module.py",
    )


@patch("flowerpower.cli.utils.importlib.util.module_from_spec")
@patch("flowerpower.cli.utils.importlib.util.spec_from_file_location")
@patch("flowerpower.cli.utils.os.path.exists", return_value=True)
def test_load_hook_parses_storage_options_string(
    _mock_exists: MagicMock,
    mock_spec_from_file_location: MagicMock,
    mock_module_from_spec: MagicMock,
) -> None:
    mock_pm = MagicMock()
    mock_pm._fs.path = "/project"
    mock_pm.registry._hooks_dir = "hooks"
    mock_pm._fs_helper.get_project_path.return_value = "/project"

    manager_context = MagicMock()
    manager_context.__enter__.return_value = mock_pm
    manager_context.__exit__.return_value = False

    spec = MagicMock()
    spec.loader = MagicMock()
    mock_spec_from_file_location.return_value = spec
    mock_module_from_spec.return_value = SimpleNamespace(my_hook=lambda: "ok")

    with patch("flowerpower.cli.utils.PipelineManager", return_value=manager_context) as mock_manager:
        hook = load_hook(
            "pipeline_name",
            "module.my_hook",
            storage_options='{"anon": true}',
        )

    assert hook() == "ok"
    assert mock_manager.call_args.kwargs["storage_options"] == {"anon": True}


def test_load_hook_rejects_invalid_storage_options() -> None:
    try:
        load_hook("pipeline_name", "module.my_hook", storage_options="not-a-mapping")
    except ValueError as exc:
        assert "Invalid storage_options format" in str(exc)
    else:
        raise AssertionError("Expected load_hook to reject invalid storage_options")


def test_load_hook_rejects_invalid_function_path() -> None:
    with pytest.raises(ValueError, match="Invalid function_path format"):
        load_hook("pipeline_name", "pkg/module.my_hook")
