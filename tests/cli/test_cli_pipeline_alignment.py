from __future__ import annotations

from typing import Callable
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from flowerpower.cli import app

runner = CliRunner()


def _stubbed_manager(
    monkeypatch: pytest.MonkeyPatch,
    configure: Callable[[MagicMock], None],
) -> MagicMock:
    manager_instance = MagicMock()
    configure(manager_instance)

    manager_context = MagicMock()
    manager_context.__enter__.return_value = manager_instance
    manager_context.__exit__.return_value = False

    manager_factory = MagicMock(return_value=manager_context)
    monkeypatch.setattr("flowerpower.cli.pipeline.PipelineManager", manager_factory)
    return manager_instance


def test_cli_save_dag_logs_returned_path(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_path = "/tmp/example_graph.svg"

    def configure(manager: MagicMock) -> None:
        manager.save_dag.return_value = expected_path

    manager_instance = _stubbed_manager(monkeypatch, configure)
    logger_mock = MagicMock()
    monkeypatch.setattr("flowerpower.cli.pipeline.logger", logger_mock)

    result = runner.invoke(
        app,
        ["pipeline", "save-dag", "example"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    manager_instance.save_dag.assert_called_once_with(
        name="example", format="png", output_path=None
    )
    logger_mock.info.assert_called_once_with(
        f"DAG for pipeline 'example' saved to {expected_path}."
    )
    logger_mock.error.assert_not_called()


@pytest.mark.parametrize("requested_format", ["json", "yaml"])
def test_cli_show_pipelines_format(monkeypatch: pytest.MonkeyPatch, requested_format: str) -> None:
    def configure(manager: MagicMock) -> None:
        manager.show_pipelines.return_value = None

    manager_instance = _stubbed_manager(monkeypatch, configure)

    result = runner.invoke(
        app,
        ["pipeline", "show-pipelines", "--format", requested_format],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    manager_instance.show_pipelines.assert_called_once_with(format=requested_format)
