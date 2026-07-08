"""Tests for env overlay error logging in PipelineConfigManager."""

from unittest.mock import MagicMock, patch

from flowerpower.pipeline import config_manager
from flowerpower.pipeline.config_manager import PipelineConfigManager


def test_env_overlay_error_is_logged_at_debug():
    """Test that env overlay parsing errors are logged at DEBUG level, not silently swallowed."""
    fs = MagicMock()
    mock_project_cfg = MagicMock()

    call_count = [0]

    def raise_and_count():
        call_count[0] += 1
        raise ValueError("Test env parsing error")

    log_calls = []

    def capture_debug(msg):
        log_calls.append(msg)

    with patch(
        "flowerpower.utils.env.parse_env_overrides", side_effect=raise_and_count
    ):
        with patch(
            "flowerpower.utils.env.logger.debug", side_effect=capture_debug
        ):
            with patch.object(
                config_manager.ProjectConfig, "from_yaml", return_value=mock_project_cfg
            ):
                manager = PipelineConfigManager(
                    base_dir="/project",
                    fs=fs,
                    storage_options={},
                )

                # This should NOT raise, but should log the error
                manager.load_project_config()

                # Verify parse_env_overrides was called
                assert call_count[0] == 1

                # Verify the error was logged at DEBUG level
                assert any(
                    "Env overlay application failed" in msg for msg in log_calls
                )
                assert any(
                    "Test env parsing error" in msg for msg in log_calls
                )


def test_pipeline_config_env_overlay_error_is_logged_at_debug():
    """Test that env overlay parsing errors in load_pipeline_config are logged."""
    fs = MagicMock()
    mock_project_cfg = MagicMock()
    mock_pipeline_cfg = MagicMock()

    # Mock fs.exists to return True for pipeline config
    fs.exists.return_value = True

    call_count = [0]

    def raise_and_count():
        call_count[0] += 1
        raise ValueError("Test pipeline env parsing error")

    log_calls = []

    def capture_debug(msg):
        log_calls.append(msg)

    with patch(
        "flowerpower.utils.env.parse_env_overrides", side_effect=raise_and_count
    ):
        with patch(
            "flowerpower.utils.env.logger.debug", side_effect=capture_debug
        ):
            with patch.object(
                config_manager.ProjectConfig, "from_yaml", return_value=mock_project_cfg
            ):
                with patch.object(
                    config_manager.PipelineConfig,
                    "from_yaml",
                    return_value=mock_pipeline_cfg,
                ):
                    manager = PipelineConfigManager(
                        base_dir="/project",
                        fs=fs,
                        storage_options={},
                    )

                    # This should NOT raise, but should log the error
                    manager.load_pipeline_config("test_pipeline")

                    # Verify parse_env_overrides was called
                    assert call_count[0] > 0

                    # Verify the error was logged at DEBUG level
                    assert any(
                        "Env overlay application failed" in msg for msg in log_calls
                    )
                    assert any(
                        "Test pipeline env parsing error" in msg for msg in log_calls
                    )
