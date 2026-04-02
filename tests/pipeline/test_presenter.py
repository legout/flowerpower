"""Tests for PipelinePresenter."""

from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from flowerpower.pipeline.presenter import PipelinePresenter


@pytest.fixture
def presenter():
    """Fixture for PipelinePresenter instance."""
    return PipelinePresenter()


@pytest.fixture
def mock_console():
    """Fixture for mocked Console."""
    return MagicMock(spec=Console)


class TestPipelinePresenter:
    """Test cases for PipelinePresenter."""

    def test_initialization_with_default_console(self):
        """Test that presenter creates a console if none provided."""
        presenter = PipelinePresenter()
        assert presenter._console is not None
        assert isinstance(presenter._console, Console)

    def test_initialization_with_custom_console(self, mock_console):
        """Test that presenter uses provided console."""
        presenter = PipelinePresenter(console=mock_console)
        assert presenter._console == mock_console

    def test_show_pipelines_table_with_data(self, presenter):
        """Test rendering table with pipeline data."""
        pipeline_info = [
            {
                "name": "pipe1",
                "path": "/path/to/pipe1.py",
                "mod_time": "2023-01-01 10:00:00",
                "size": "1.0 KB",
            },
            {
                "name": "pipe2",
                "path": "/path/to/pipe2.py",
                "mod_time": "2023-01-02 11:00:00",
                "size": "2.0 KB",
            },
        ]

        with patch.object(presenter, '_console') as mock_console:
            result = presenter.show_pipelines_table(pipeline_info)
            
            # Should print a Table to console (not a plain string)
            assert mock_console.print.call_count == 1
            printed_arg = mock_console.print.call_args[0][0]
            assert isinstance(printed_arg, Table)
            # Should return None (not HTML/SVG)
            assert result is None

    def test_show_pipelines_table_empty(self, presenter):
        """Test rendering table with no pipelines."""
        with patch('flowerpower.pipeline.presenter.rich.print') as mock_rich_print:
            result = presenter.show_pipelines_table([])
            
            # Should print "No pipelines found" message
            mock_rich_print.assert_called_once_with("[yellow]No pipelines found[/yellow]")
            assert result is None

    def test_show_pipelines_table_to_html(self, presenter):
        """Test exporting table to HTML."""
        pipeline_info = [
            {
                "name": "pipe1",
                "path": "/path/to/pipe1.py",
                "mod_time": "2023-01-01 10:00:00",
                "size": "1.0 KB",
            },
        ]

        result = presenter.show_pipelines_table(pipeline_info, to_html=True)
        
        # Should return HTML string
        assert result is not None
        assert "<html" in result.lower() or "<!doctype" in result.lower()

    def test_show_pipelines_table_to_svg(self, presenter):
        """Test exporting table to SVG."""
        pipeline_info = [
            {
                "name": "pipe1",
                "path": "/path/to/pipe1.py",
                "mod_time": "2023-01-01 10:00:00",
                "size": "1.0 KB",
            },
        ]

        result = presenter.show_pipelines_table(pipeline_info, to_svg=True)
        
        # Should return SVG string
        assert result is not None
        assert "<svg" in result.lower()

    def test_show_pipelines_table_non_export_uses_primary_console_only(self, mock_console):
        """Test that non-export rendering does not create a second recording console."""
        presenter = PipelinePresenter(console=mock_console)
        pipeline_info = [
            {
                "name": "pipe1",
                "path": "/path/to/pipe1.py",
                "mod_time": "2023-01-01 10:00:00",
                "size": "1.0 KB",
            },
        ]

        with patch("flowerpower.pipeline.presenter.Console") as mock_console_cls:
            result = presenter.show_pipelines_table(pipeline_info)

        assert result is None
        mock_console_cls.assert_not_called()
        mock_console.print.assert_called_once()

    def test_show_summary_with_project_and_pipelines(self, presenter):
        """Test rendering summary with project and pipeline data."""
        summary = {
            "project": {"name": "test_project", "version": "1.0"},
            "pipelines": {
                "pipe1": {
                    "cfg": {"name": "pipe1", "executor": "local"},
                    "module": "def test(): pass",
                }
            },
        }

        with patch.object(presenter, '_console') as mock_console:
            result = presenter.show_summary(summary, cfg=True, code=True, project=True)
            
            # Should print Rich objects (Panels) to console, not plain text
            assert mock_console.print.call_count == 6  # Project panel + nl + pipeline panel + nl + code panel + nl
            # Verify Panels are printed (not plain strings/export_text)
            printed_types = [type(args[0][0]) for args in mock_console.print.call_args_list]
            assert Panel in printed_types
            # Should not be called with plain strings (export_text output)
            assert not any(isinstance(arg, str) for arg in printed_types)
            assert result is None

    def test_show_summary_no_project(self, presenter):
        """Test rendering summary without project info."""
        summary = {
            "pipelines": {
                "pipe1": {
                    "cfg": {"name": "pipe1"},
                }
            },
        }

        with patch.object(presenter, '_console') as mock_console:
            result = presenter.show_summary(summary, cfg=True, code=False, project=False)
            
            # Should print Panel (not plain text)
            assert mock_console.print.call_count == 2  # Panel + newline
            printed_arg = mock_console.print.call_args_list[0][0][0]
            assert isinstance(printed_arg, Panel)
            assert result is None

    def test_show_summary_to_html(self, presenter):
        """Test exporting summary to HTML."""
        summary = {
            "project": {"name": "test_project"},
            "pipelines": {
                "pipe1": {
                    "cfg": {"name": "pipe1"},
                    "module": "def test(): pass",
                }
            },
        }

        result = presenter.show_summary(summary, to_html=True)
        
        # Should return HTML string
        assert result is not None
        assert "<html" in result.lower() or "<!doctype" in result.lower()

    def test_show_summary_to_svg(self, presenter):
        """Test exporting summary to SVG."""
        summary = {
            "project": {"name": "test_project"},
            "pipelines": {
                "pipe1": {
                    "cfg": {"name": "pipe1"},
                    "module": "def test(): pass",
                }
            },
        }

        result = presenter.show_summary(summary, to_svg=True)
        
        # Should return SVG string
        assert result is not None
        assert "<svg" in result.lower()

    def test_show_summary_empty_pipelines(self, presenter):
        """Test rendering summary with empty pipelines."""
        summary = {
            "project": {"name": "test_project"},
            "pipelines": {},
        }

        with patch.object(presenter, '_console') as mock_console:
            result = presenter.show_summary(summary)
            
            # Should still print project panel (not plain text)
            assert mock_console.print.call_count == 2  # Panel + newline
            printed_arg = mock_console.print.call_args_list[0][0][0]
            assert isinstance(printed_arg, Panel)

    def test_print_no_pipelines_found(self, presenter):
        """Test printing no pipelines message."""
        with patch('flowerpower.pipeline.presenter.rich.print') as mock_rich_print:
            presenter.print_no_pipelines_found()
            mock_rich_print.assert_called_once_with("[yellow]No pipelines found[/yellow]")

    def test_show_summary_nested_config(self, presenter):
        """Test rendering summary with nested config dictionary."""
        summary = {
            "project": {
                "name": "test_project",
                "settings": {
                    "debug": True,
                    "timeout": 30,
                },
            },
            "pipelines": {
                "pipe1": {
                    "cfg": {
                        "name": "pipe1",
                        "nested": {"key": "value"},
                    },
                }
            },
        }

        with patch.object(presenter, '_console') as mock_console:
            result = presenter.show_summary(summary, cfg=True, code=False, project=True)
            
            # Verify Panels and Trees are printed (not plain strings)
            printed_types = [type(args[0][0]) for args in mock_console.print.call_args_list]
            assert Panel in printed_types
            assert not any(isinstance(arg, str) and len(arg) > 100 for arg in printed_types)  # Not export_text
            assert result is None

    def test_show_summary_only_cfg_no_code(self, presenter):
        """Test rendering summary with only config, no code."""
        summary = {
            "pipelines": {
                "pipe1": {
                    "cfg": {"name": "pipe1"},
                    "module": "def test(): pass",
                }
            },
        }

        with patch.object(presenter, '_console') as mock_console:
            result = presenter.show_summary(summary, cfg=True, code=False, project=False)
            
            # Should print Panel with Tree (config only)
            assert mock_console.print.call_count == 2  # Panel + newline
            printed_arg = mock_console.print.call_args_list[0][0][0]
            assert isinstance(printed_arg, Panel)
            # Panel contains a Tree (config view)
            assert isinstance(printed_arg.renderable, Tree)

    def test_show_summary_only_code_no_cfg(self, presenter):
        """Test rendering summary with only code, no config."""
        summary = {
            "pipelines": {
                "pipe1": {
                    "cfg": {"name": "pipe1"},
                    "module": "def test(): pass",
                }
            },
        }

        with patch.object(presenter, '_console') as mock_console:
            result = presenter.show_summary(summary, cfg=False, code=True, project=False)
            
            # Should print Panel with Syntax (code)
            assert mock_console.print.call_count == 2  # Panel + newline
            printed_arg = mock_console.print.call_args_list[0][0][0]
            assert isinstance(printed_arg, Panel)
            # Verify it contains Syntax (code view)
            assert isinstance(printed_arg.renderable, Syntax)

    def test_show_summary_non_export_renders_rich_objects_not_text(self, presenter):
        """Test that non-export path renders Rich objects directly, not export_text()."""
        summary = {
            "project": {"name": "test_project"},
            "pipelines": {
                "pipe1": {
                    "cfg": {"name": "pipe1"},
                    "module": "def test(): pass",
                }
            },
        }

        with patch.object(presenter, '_console') as mock_console:
            result = presenter.show_summary(summary, to_html=False, to_svg=False)
            
            # Should return None (not export)
            assert result is None
            
            # Should print Rich objects (Panel, Tree, Syntax) to the actual console
            printed_args = [args[0][0] for args in mock_console.print.call_args_list]
            
            # Verify we got Rich renderables, not plain text strings
            rich_types = (Panel, Tree, Syntax)
            has_rich_objects = any(isinstance(arg, rich_types) for arg in printed_args)
            assert has_rich_objects, f"Expected Rich objects, got types: {[type(a) for a in printed_args]}"
            
            # Verify we did NOT get a long plain string (which would be export_text() output)
            long_string_args = [arg for arg in printed_args 
                               if isinstance(arg, str) and len(arg) > 200]
            assert not long_string_args, "Should not use export_text() style output"
