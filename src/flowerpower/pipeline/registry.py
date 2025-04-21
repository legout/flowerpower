# -*- coding: utf-8 -*-
"""Pipeline Registry for discovery, listing, creation, and deletion."""

import datetime as dt
import logging
import posixpath
from typing import TYPE_CHECKING, Callable

import rich  # <-- Add this import
from fsspec.spec import AbstractFileSystem
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

# Import necessary config types and utility functions
from ..cfg import PipelineConfig

# Assuming view_img might be used indirectly or needed later
from ..utils.templates import PIPELINE_PY_TEMPLATE

if TYPE_CHECKING:
    # Keep this for type hinting if needed elsewhere, though Config is imported directly now
    pass


logger = logging.getLogger(__name__)


class PipelineRegistry:
    """Manages discovery, listing, creation, and deletion of pipelines."""

    def __init__(
        self,
        fs: AbstractFileSystem,
        base_dir: str,
        cfg_dir: str,
        pipelines_dir: str,
        load_config_func: Callable,
    ):
        """
        Initializes the PipelineRegistry.

        Args:
            fs: Filesystem object.
            base_dir: Base directory for the project.
            cfg_dir: Configuration directory path.
            pipelines_dir: Pipelines directory path.
            load_config_func: Function to load configuration.
        """
        self._fs = fs
        self._base_dir = base_dir
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        self._load_config_func = load_config_func
        self._console = Console()

    # --- Methods moved from PipelineManager ---
    def new(self, name: str, overwrite: bool = False):
        """
        Adds a pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool): Whether to overwrite an existing pipeline. Defaults to False.
            worker_type (str | None): The type of worker to use. Defaults to None.

        Raises:
            ValueError: If the configuration or pipeline path does not exist, or if the pipeline already exists.

        Examples:
            pm = PipelineManager()
            pm.new("my_pipeline")
        """
        cfg = self._load_config_func()

        for dir_path, label in (
            (self._cfg_dir, "configuration"),
            (self._pipelines_dir, "pipeline"),
        ):
            if not self._fs.exists(dir_path):
                raise ValueError(
                    f"{label.capitalize()} path {dir_path} does not exist. Please run flowerpower init first."
                )

        formatted_name = name.replace(".", "/")
        pipeline_file = posixpath.join(self._pipelines_dir, f"{formatted_name}.py")
        cfg_file = posixpath.join(self._cfg_dir, "pipelines", f"{formatted_name}.yml")

        def check_and_handle(path: str):
            if self._fs.exists(path):
                if overwrite:
                    self._fs.rm(path)
                else:
                    raise ValueError(
                        f"Pipeline {cfg.project.name}.{formatted_name} already exists. Use `overwrite=True` to overwrite."
                    )

        check_and_handle(pipeline_file)
        check_and_handle(cfg_file)

        # Ensure directories for the new files exist
        for file_path in (pipeline_file, cfg_file):
            self._fs.makedirs(file_path.rsplit("/", 1)[0], exist_ok=True)

        with self._fs.open(pipeline_file, "w") as f:
            f.write(
                PIPELINE_PY_TEMPLATE.format(
                    name=name,
                    date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
            )

        cfg.pipeline = PipelineConfig(name=name)
        save_project = not self._fs.exists(f"{self._cfg_dir}/project.yml")
        cfg.save(project=save_project, pipeline=True)
        rich.print(
            f"🔧 Created new pipeline [bold blue]{cfg.project.name}.{name}[/bold blue]"
        )

    def delete(self, name: str, cfg: bool = True, module: bool = False):
        """
        Delete a pipeline.

        Args:
            name (str): The name of the pipeline.
            cfg (bool, optional): Whether to delete the config file. Defaults to True.
            module (bool, optional): Whether to delete the module file. Defaults to False.

        Returns:
            None

        Raises:
            FileNotFoundError: If the specified files do not exist.

        Examples:
            >>> pm = PipelineManager()
            >>> pm.delete("my_pipeline")
        """
        deleted_files = []
        if cfg:
            pipeline_cfg_path = posixpath.join(
                self._cfg_dir, "pipelines", f"{name}.yml"
            )
            if self._fs.exists(pipeline_cfg_path):
                self._fs.rm(pipeline_cfg_path)
                deleted_files.append(pipeline_cfg_path)
                logger.info(f"Deleted pipeline config: {pipeline_cfg_path}")
            else:
                logger.warning(
                    f"Config file not found, skipping deletion: {pipeline_cfg_path}"
                )

        if module:
            pipeline_py_path = posixpath.join(self._pipelines_dir, f"{name}.py")
            if self._fs.exists(pipeline_py_path):
                self._fs.rm(pipeline_py_path)
                deleted_files.append(pipeline_py_path)
                logger.info(f"Deleted pipeline module: {pipeline_py_path}")
            else:
                logger.warning(
                    f"Module file not found, skipping deletion: {pipeline_py_path}"
                )

        if not deleted_files:
            logger.warning(
                f"No files found or specified for deletion for pipeline '{name}'."
            )

        # Sync filesystem if needed
        if hasattr(self._fs, "sync") and Callable(getattr(self._fs, "sync")):
            self._fs.sync()

    def _get_files(self) -> list[str]:
        """
        Get the list of pipeline files.

        Returns:
            list[str]: The list of pipeline files.
        """
        try:
            return self._fs.glob(posixpath.join(self._pipelines_dir, "*.py"))
        except Exception as e:
            logger.error(
                f"Error accessing pipeline directory {self._pipelines_dir}: {e}"
            )
            return []

    def _get_names(self) -> list[str]:
        """
        Get the list of pipeline names.

        Returns:
            list[str]: The list of pipeline names.
        """
        files = self._get_files()
        return [posixpath.basename(f).replace(".py", "") for f in files]

    def get_summary(
        self,
        name: str | None = None,
        cfg: bool = True,
        code: bool = True,
        project: bool = True,
    ) -> dict[str, dict | str]:
        """
        Get a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            cfg (bool, optional): Whether to show the configuration. Defaults to True.
            code (bool, optional): Whether to show the module. Defaults to True.
            project (bool, optional): Whether to show the project configuration. Defaults to True.
        Returns:
            dict[str, dict | str]: A dictionary containing the pipeline summary.

        Examples:
            ```python
            pm = PipelineManager()
            summary=pm.get_summary()
            ```
        """
        if name:
            pipeline_names = [name]
        else:
            pipeline_names = self._get_names()

        summary = {}
        summary["pipelines"] = {}

        if project:
            project_cfg = self._load_config_func().project
            summary["project"] = project_cfg.to_dict()

        for name in pipeline_names:
            pipeline_cfg = self._load_config_func(name=name).pipeline
            if cfg:
                summary["pipelines"][name] = {"cfg": pipeline_cfg.to_dict()}
            if code:
                summary["pipelines"][name].update(
                    {
                        "module": self._fs.cat(
                            f"{self._pipelines_dir}/{name}.py"
                        ).decode(),
                    }
                )
        return summary

    def show_summary(
        self,
        name: str | None = None,
        cfg: bool = True,
        code: bool = True,
        project: bool = True,
        to_html: bool = False,
        to_svg: bool = False,
    ) -> None | str:
        """
        Show a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            cfg (bool, optional): Whether to show the configuration. Defaults to True.
            code (bool, optional): Whether to show the module. Defaults to True.
            project (bool, optional): Whether to show the project configuration. Defaults to True.
            to_html (bool, optional): Whether to export the summary to HTML. Defaults to False.
            to_svg (bool, optional): Whether to export the summary to SVG. Defaults to False.

        Returns:
            None | str: The summary of the pipelines. If `to_html` is True, returns the HTML string.
                If `to_svg` is True, returns the SVG string.

        Examples:
            ```python
            pm = PipelineManager()
            pm.show_summary()
            ```
        """

        summary = self.get_summary(name=name, cfg=cfg, code=code, project=project)
        project_summary = summary.get("project", {})
        pipeline_summary = summary["pipelines"]

        def add_dict_to_tree(tree, dict_data, style="green"):
            for key, value in dict_data.items():
                if isinstance(value, dict):
                    branch = tree.add(f"[cyan]{key}:", style="bold cyan")
                    add_dict_to_tree(branch, value, style)
                else:
                    tree.add(f"[cyan]{key}:[/] [green]{value}[/]")

        console = Console()

        if project:
            # Create tree for project config
            project_tree = Tree("📁 Project Configuration", style="bold magenta")
            add_dict_to_tree(project_tree, project_summary)

            # Print project configuration
            console.print(
                Panel(
                    project_tree,
                    title="Project Configuration",
                    border_style="blue",
                    padding=(2, 2),
                )
            )
            console.print("\n")

        for pipeline, info in pipeline_summary.items():
            # Create tree for config
            config_tree = Tree("📋 Pipeline Configuration", style="bold magenta")
            add_dict_to_tree(config_tree, info["cfg"])

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

            if cfg:
                # console.print(f"🔄 Pipeline: {pipeline}", style="bold blue")
                console.print(
                    Panel(
                        config_tree,
                        title=f"🔄 Pipeline: {pipeline}",
                        subtitle="Configuration",
                        border_style="blue",
                        padding=(2, 2),
                    )
                )
                console.print("\n")

            if code:
                # console.print(f"🔄 Pipeline: {pipeline}", style="bold blue")
                console.print(
                    Panel(
                        code_view,
                        title=f"🔄 Pipeline: {pipeline}",
                        subtitle="Module",
                        border_style="blue",
                        padding=(2, 2),
                    )
                )
                console.print("\n")
        if to_html:
            return console.export_html()
        elif to_svg:
            return console.export_svg()

    @property
    def summary(self) -> dict[str, dict | str]:
        """
        Get a summary of the pipelines.

        Returns:
            dict: A dictionary containing the pipeline summary.
        """
        return self.get_summary()

    def _all_pipelines(
        self, show: bool = True, to_html: bool = False, to_svg: bool = False
    ) -> list[str] | None:
        """
        Print all available pipelines in a formatted table.

        Args:
            show (bool, optional): Whether to print the table. Defaults to True.
            to_html (bool, optional): Whether to export the table to HTML. Defaults to False.
            to_svg (bool, optional): Whether to export the table to SVG. Defaults to False.

        Returns:
            list[str] | None: A list of pipeline names if `show` is False.

        Examples:
            ```python
            pm = PipelineManager()
            all_pipelines = pm._pipelines(show=False)
            ```
        """
        if to_html or to_svg:
            show = True

        pipeline_files = [
            f for f in self._fs.ls(self._pipelines_dir) if f.endswith(".py")
        ]
        pipeline_names = [
            posixpath.splitext(f)[0]
            .replace(self._pipelines_dir, "")
            .lstrip("/")
            .replace("/", ".")
            for f in pipeline_files
        ]

        if not pipeline_files:
            rich.print("[yellow]No pipelines found[/yellow]")
            return

        pipeline_info = []

        for path, name in zip(pipeline_files, pipeline_names):
            # path = posixpath.join( f)
            try:
                mod_time = self._fs.modified(path).strftime("%Y-%m-%d %H:%M:%S")
            except NotImplementedError:
                mod_time = "N/A"
            size = f"{self._fs.size(path) / 1024:.1f} KB"
            pipeline_info.append(
                {"name": name, "path": path, "mod_time": mod_time, "size": size}
            )

        if show:
            table = Table(title="Available Pipelines")
            table.add_column("Pipeline Name", style="blue")
            table.add_column("Path", style="magenta")
            table.add_column("Last Modified", style="green")
            table.add_column("Size", style="cyan")

            for info in pipeline_info:
                table.add_row(
                    info["name"], info["path"], info["mod_time"], info["size"]
                )
            console = Console(record=True)
            console.print(table)
            if to_html:
                return console.export_html()
            elif to_svg:
                return console.export_svg()

        else:
            return pipeline_info

    def show_pipelines(self) -> None:
        """
        Print all available pipelines in a formatted table.

        Examples:
            ```python
            pm = PipelineManager()
            pm.show_pipelines()
            ```
        """
        self._all_pipelines(show=True)

    def list_pipelines(self) -> list[str]:
        """
        Get a list of all available pipelines.

        Returns:
            list[str] | None: A list of pipeline names.

        Examples:
            ```python
            pm = PipelineManager()
            pipelines = pm.list_pipelines()
            ```
        """
        return self._all_pipelines(show=False)

    @property
    def pipelines(self) -> list[str]:
        """
        Get a list of all available pipelines.

        Returns:
            list[str] | None: A list of pipeline names.

        Examples:
            ```python
            pm = PipelineManager()
            pipelines = pm.pipelines
            ```
        """
        return self._all_pipelines(show=False)
