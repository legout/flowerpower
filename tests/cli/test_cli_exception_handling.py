"""Tests for CLI exception handling behavior (flo-m7pr).

Verifies that bare ``except Exception`` has been replaced with specific
exception tuples so that KeyboardInterrupt and SystemExit propagate cleanly.
"""

import ast
from pathlib import Path

import pytest
from typer.testing import CliRunner

from flowerpower.cli import app

runner = CliRunner()


def _mock_project(mocker, side_effect):
    """Patch FlowerPowerProject.load to return a mock whose .run() raises *side_effect*."""
    mock_instance = mocker.MagicMock()
    mock_instance.run.side_effect = side_effect
    mocker.patch(
        "flowerpower.cli.pipeline.FlowerPowerProject.load",
        return_value=mock_instance,
    )
    return mock_instance


class TestKeyboardInterruptAndSystemExit:
    """Verify KeyboardInterrupt and SystemExit are not caught by CLI handlers."""

    def test_run_keyboard_interrupt_propagates(self, mocker):
        """KeyboardInterrupt during pipeline run should propagate cleanly.

        Click/Typer converts KeyboardInterrupt into SystemExit(130)
        (standard exit code for SIGINT). The key property is that our
        exception handler does NOT intercept it and log an error.
        """
        _mock_project(mocker, KeyboardInterrupt())

        result = runner.invoke(app, ["pipeline", "run", "test_pipeline"])

        assert isinstance(result.exception, SystemExit)
        assert result.exception.code == 130

    def test_run_system_exit_propagates(self, mocker):
        """SystemExit during pipeline run should propagate with original code."""
        _mock_project(mocker, SystemExit(42))

        result = runner.invoke(app, ["pipeline", "run", "test_pipeline"])

        assert isinstance(result.exception, SystemExit)
        assert result.exception.code == 42


class TestNarrowedExceptionsStillCaught:
    """Verify the narrowed exception types are still caught and exit with code 1."""

    def test_run_runtime_error_caught(self, mocker):
        """RuntimeError should still be caught and result in exit code 1."""
        _mock_project(mocker, RuntimeError("test failure"))

        result = runner.invoke(app, ["pipeline", "run", "test_pipeline"])

        assert result.exit_code == 1

    def test_run_type_error_caught(self, mocker):
        """TypeError should still be caught and result in exit code 1."""
        _mock_project(mocker, TypeError("bad type"))

        result = runner.invoke(app, ["pipeline", "run", "test_pipeline"])

        assert result.exit_code == 1


class TestStructuralNoBareExceptException:
    """Structural regression: cli/pipeline.py contains no bare 'except Exception'."""

    def test_no_bare_except_exception(self):
        from flowerpower.cli import pipeline

        source = Path(pipeline.__file__).read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if isinstance(node.type, ast.Name) and node.type.id == "Exception":
                    pytest.fail(
                        f"Found bare 'except Exception' at line {node.lineno} in "
                        f"cli/pipeline.py — narrow it to specific exception types."
                    )
