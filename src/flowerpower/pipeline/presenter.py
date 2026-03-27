"""Pipeline Presenter for Rich rendering of pipeline information."""

from typing import Any

import rich
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree


class PipelinePresenter:
    """Handles Rich rendering of pipeline information.

    This class is responsible for displaying pipelines and their summaries
    using Rich formatting (tables, panels, syntax highlighting, etc.).
    It separates presentation concerns from the registry's data management.

    Attributes:
        _console: Rich Console instance for output.
    """

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the PipelinePresenter.

        Args:
            console: Optional Rich Console instance. If not provided,
                    a new Console will be created.
        """
        self._console = console or Console()

    def show_pipelines_table(
        self,
        pipeline_info: list[dict[str, Any]],
        to_html: bool = False,
        to_svg: bool = False,
    ) -> str | None:
        """Render a table of pipelines.

        Args:
            pipeline_info: List of pipeline info dictionaries, each containing
                          'name', 'path', 'mod_time', and 'size' keys.
            to_html: Whether to export the table to HTML. Defaults to False.
            to_svg: Whether to export the table to SVG. Defaults to False.

        Returns:
            str | None: HTML or SVG string if export is requested, otherwise None.
        """
        if not pipeline_info:
            rich.print("[yellow]No pipelines found[/yellow]")
            return None

        table = Table(title="Available Pipelines")
        table.add_column("Pipeline Name", style="blue")
        table.add_column("Path", style="magenta")
        table.add_column("Last Modified", style="green")
        table.add_column("Size", style="cyan")

        for info in pipeline_info:
            table.add_row(
                info["name"],
                info["path"],
                info["mod_time"],
                info["size"],
            )

        if to_html:
            console = Console(record=True)
            console.print(table)
            return console.export_html()
        elif to_svg:
            console = Console(record=True)
            console.print(table)
            return console.export_svg()
        else:
            self._console.print(table)
            return None

    def show_summary(
        self,
        summary: dict[str, Any],
        cfg: bool = True,
        code: bool = True,
        project: bool = True,
        to_html: bool = False,
        to_svg: bool = False,
    ) -> str | None:
        """Render a summary of pipelines.

        Args:
            summary: Dictionary containing 'project' and 'pipelines' keys.
            cfg: Whether configuration was included in the summary.
            code: Whether code/module was included in the summary.
            project: Whether project info was included in the summary.
            to_html: Whether to export to HTML. Defaults to False.
            to_svg: Whether to export to SVG. Defaults to False.

        Returns:
            str | None: HTML or SVG string if export is requested, otherwise None.
        """
        project_summary = summary.get("project", {})
        pipeline_summary = summary.get("pipelines", {})

        def add_dict_to_tree(tree: Tree, dict_data: dict, style: str = "green") -> None:
            """Recursively add dictionary items to a tree."""
            for key, value in dict_data.items():
                if isinstance(value, dict):
                    branch = tree.add(f"[cyan]{key}:", style="bold cyan")
                    add_dict_to_tree(branch, value, style)
                else:
                    tree.add(f"[cyan]{key}:[/] [green]{value}[/]")

        # For export, use a recording console; for normal rendering, use main console
        export_console = Console(record=True) if (to_html or to_svg) else None
        target_console = export_console if export_console else self._console

        if project and project_summary:
            # Create tree for project config
            project_tree = Tree("📁 Project Configuration", style="bold magenta")
            add_dict_to_tree(project_tree, project_summary)

            # Print project configuration
            target_console.print(
                Panel(
                    project_tree,
                    title="Project Configuration",
                    border_style="blue",
                    padding=(2, 2),
                )
            )
            target_console.print("\n")

        for pipeline, info in pipeline_summary.items():
            if cfg and "cfg" in info:
                # Create tree for config
                config_tree = Tree("📋 Pipeline Configuration", style="bold magenta")
                add_dict_to_tree(config_tree, info["cfg"])

                target_console.print(
                    Panel(
                        config_tree,
                        title=f"🔄 Pipeline: {pipeline}",
                        subtitle="Configuration",
                        border_style="blue",
                        padding=(2, 2),
                    )
                )
                target_console.print("\n")

            if code and "module" in info:
                # Create syntax-highlighted code view
                code_view = Syntax(
                    info["module"],
                    "python",
                    theme="default",
                    line_numbers=False,
                    word_wrap=True,
                    code_width=80,
                    padding=2,
                )

                target_console.print(
                    Panel(
                        code_view,
                        title=f"🔄 Pipeline: {pipeline}",
                        subtitle="Module",
                        border_style="blue",
                        padding=(2, 2),
                    )
                )
                target_console.print("\n")

        if to_html and export_console is not None:
            return export_console.export_html()
        elif to_svg and export_console is not None:
            return export_console.export_svg()
        else:
            # Normal rendering already done to self._console
            return None

    def print_no_pipelines_found(self) -> None:
        """Print a message when no pipelines are found."""
        rich.print("[yellow]No pipelines found[/yellow]")
