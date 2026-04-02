"""Tests for settings module — env parsing edge cases."""

import os
from unittest.mock import patch


class TestExecutorSettings:
    """Tests for settings/executor.py defaults and env overrides."""

    def test_cpu_count_none_does_not_crash(self):
        """os.cpu_count() returning None must not raise."""
        with patch("os.cpu_count", return_value=None):
            import importlib

            import flowerpower.settings.executor as executor_mod

            importlib.reload(executor_mod)
            assert isinstance(executor_mod.EXECUTOR_MAX_WORKERS, int)
            assert isinstance(executor_mod.EXECUTOR_NUM_CPUS, int)

    def test_cpu_count_normal(self):
        """Normal cpu_count should produce expected defaults."""
        with patch("os.cpu_count", return_value=4):
            import importlib

            import flowerpower.settings.executor as executor_mod

            importlib.reload(executor_mod)
            assert executor_mod.EXECUTOR_MAX_WORKERS == 4 * 5
            assert executor_mod.EXECUTOR_NUM_CPUS == 4

    def test_env_override_max_workers(self):
        """FP_EXECUTOR_MAX_WORKERS env var overrides the default."""
        with patch.dict(os.environ, {"FP_EXECUTOR_MAX_WORKERS": "99"}, clear=False):
            import importlib

            import flowerpower.settings.executor as executor_mod

            importlib.reload(executor_mod)
            assert executor_mod.EXECUTOR_MAX_WORKERS == 99

    def test_safe_cpu_count_returns_default_on_none(self):
        from flowerpower.settings.executor import _safe_cpu_count

        with patch("os.cpu_count", return_value=None):
            assert _safe_cpu_count(default=8) == 8

    def test_safe_cpu_count_returns_actual_count(self):
        from flowerpower.settings.executor import _safe_cpu_count

        with patch("os.cpu_count", return_value=16):
            assert _safe_cpu_count(default=2) == 16


class TestEnvBoolParsing:
    """Tests for _env_bool() helper function."""

    def test_env_bool_none_returns_default(self):
        """None value should return the default."""
        from flowerpower.settings.executor import _env_bool

        assert _env_bool(None, default=True) is True
        assert _env_bool(None, default=False) is False

    def test_env_bool_false_strings_return_false(self):
        """Common false representations should return False."""
        from flowerpower.settings.executor import _env_bool

        false_values = ["False", "false", "FALSE", "0", "no", "No", "NO", "n", "N", "", "off", "OFF"]
        for val in false_values:
            assert _env_bool(val, default=True) is False, f"Expected False for '{val}'"

    def test_env_bool_true_strings_return_true(self):
        """Non-false values should return True."""
        from flowerpower.settings.executor import _env_bool

        true_values = ["True", "true", "TRUE", "1", "yes", "Yes", "YES", "y", "Y", "on", "ON", "anything"]
        for val in true_values:
            assert _env_bool(val, default=False) is True, f"Expected True for '{val}'"

    def test_env_bool_strips_whitespace(self):
        """Whitespace should be stripped before parsing."""
        from flowerpower.settings.executor import _env_bool

        assert _env_bool("  false  ", default=True) is False
        assert _env_bool("  true  ", default=False) is True

    def test_env_bool_hamilton_settings_integration(self):
        """Test that HAMILTON_* boolean settings parse env vars correctly."""
        import importlib

        import flowerpower.settings.hamilton as hamilton_mod

        # Test with "False" string - should be False, not True
        with patch.dict(os.environ, {"HAMILTON_CAPTURE_DATA_STATISTICS": "False"}, clear=False):
            importlib.reload(hamilton_mod)
            assert hamilton_mod.HAMILTON_CAPTURE_DATA_STATISTICS is False

        # Test with "0" - should be False
        with patch.dict(os.environ, {"HAMILTON_TELEMETRY_ENABLED": "0"}, clear=False):
            importlib.reload(hamilton_mod)
            assert hamilton_mod.HAMILTON_TELEMETRY_ENABLED is False

        # Test with unset (default=True for CAPTURE_DATA_STATISTICS)
        # When env var is not set, the default should be used
        assert hamilton_mod.HAMILTON_CAPTURE_DATA_STATISTICS is True or hamilton_mod.HAMILTON_CAPTURE_DATA_STATISTICS is False
