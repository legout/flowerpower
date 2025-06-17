# -*- coding: utf-8 -*-
"""Pipeline Registry for discovery, listing, creation, and deletion."""

import datetime as dt
import os
import posixpath
from typing import TYPE_CHECKING

import rich
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from .. import settings
# Import necessary config types and utility functions
from ..cfg import PipelineConfig, ProjectConfig
from ..fs import AbstractFileSystem
from ..utils.logging import setup_logging
# Assuming view_img might be used indirectly or needed later
from ..utils.templates import (HOOK_TEMPLATE__MQTT_BUILD_CONFIG,
                               PIPELINE_PY_TEMPLATE)

if TYPE_CHECKING:
    # Keep this for type hinting if needed elsewhere, though Config is imported directly now
    pass

from enum import Enum


class HookType(str, Enum):
    MQTT_BUILD_CONFIG = "mqtt-build-config"

    def default_function_name(self) -> str:
        match self.value:
            case HookType.MQTT_BUILD_CONFIG:
                return self.value.replace("-", "_")
            case _:
                return self.value

    def __str__(self) -> str:
        return self.value


setup_logging(level=settings.LOG_LEVEL)


class PipelineRegistry:
    """Manages discovery, listing, creation, and deletion of pipelines."""

    def __init__(
        self,
        project_cfg: ProjectConfig,
        fs: AbstractFileSystem,
        cfg_dir: str,
        pipelines_dir: str,
    ):
        """
        Initializes the PipelineRegistry.

        Args:
            project_cfg: The project configuration object.
            fs: The filesystem instance.
            cfg_dir: The configuration directory path.
            pipelines_dir: The pipelines directory path.
        """
        self.project_cfg = project_cfg
        self._fs = fs
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        self._console = Console()

    # --- Methods moved from PipelineManager ---
    def new(self, name: str, overwrite: bool = False):
        """
        Adds a pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool): Whether to overwrite an existing pipeline. Defaults to False.
            job_queue_type (str | None): The type of worker to use. Defaults to None.

        Raises:
            ValueError: If the configuration or pipeline path does not exist, or if the pipeline already exists.

        Examples:
            >>> pm = PipelineManager()
            >>> pm.new("my_pipeline")
        """
        # Use attributes derived from self.project_cfg
        for dir_path, label in (
            (self._cfg_dir, "configuration"),
            (self._pipelines_dir, "pipeline"),
        ):
            if not self._fs.exists(dir_path):
                raise ValueError(
                    f"{label.capitalize()} path {dir_path} does not exist. Please run flowerpower init first."
                )

        formatted_name = name.replace(".", "/").replace("-", "_")
        pipeline_file = posixpath.join(self._pipelines_dir, f"{formatted_name}.py")
        cfg_file = posixpath.join(self._cfg_dir, "pipelines", f"{formatted_name}.yml")

        def check_and_handle(path: str):
            if self._fs.exists(path):
                if overwrite:
                    self._fs.rm(path)
                else:
                    raise ValueError(
                        f"Pipeline {self.project_cfg.name}.{formatted_name} already exists. Use `overwrite=True` to overwrite."
                    )

        check_and_handle(pipeline_file)
        check_and_handle(cfg_file)

        # Ensure directories for the new files exist
        for file_path in (pipeline_file, cfg_file):
            self._fs.makedirs(file_path.rsplit("/", 1)[0], exist_ok=True)

        # Write pipeline code template
        with self._fs.open(pipeline_file, "w") as f:
            f.write(
                PIPELINE_PY_TEMPLATE.format(
                    name=name,
                    date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
            )

        # Create default pipeline config and save it directly
        new_pipeline_cfg = PipelineConfig(name=name)
        new_pipeline_cfg.save(fs=self._fs)  # Save only the pipeline part

        rich.print(
            f"🔧 Created new pipeline [bold blue]{self.project_cfg.name}.{name}[/bold blue]"
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
                logger.debug(
                    f"Deleted pipeline config: {pipeline_cfg_path}"
                )  # Changed to DEBUG
            else:
                logger.warning(
                    f"Config file not found, skipping deletion: {pipeline_cfg_path}"
                )

        if module:
            pipeline_py_path = posixpath.join(self._pipelines_dir, f"{name}.py")
            if self._fs.exists(pipeline_py_path):
                self._fs.rm(pipeline_py_path)
                deleted_files.append(pipeline_py_path)
                logger.debug(
                    f"Deleted pipeline module: {pipeline_py_path}"
                )  # Changed to DEBUG
            else:
                logger.warning(
                    f"Module file not found, skipping deletion: {pipeline_py_path}"
                )

        if not deleted_files:
            logger.warning(
                f"No files found or specified for deletion for pipeline '{name}'."
            )

        # Sync filesystem if needed (using _fs)
        if hasattr(self._fs, "sync_cache") and callable(
            getattr(self._fs, "sync_cache")
        ):
            self._fs.sync_cache()

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
            # Use self.project_cfg directly
            summary["project"] = self.project_cfg.to_dict()

        for name in pipeline_names:
            # Load pipeline config directly

            pipeline_summary = {}
            if cfg:
                pipeline_cfg = PipelineConfig.load(name=name, fs=self._fs)
                pipeline_summary["cfg"] = pipeline_cfg.to_dict()
            if code:
                try:
                    module_content = self._fs.cat(
                        posixpath.join(self._pipelines_dir, f"{name}.py")
                    ).decode()
                    pipeline_summary["module"] = module_content
                except FileNotFoundError:
                    logger.warning(f"Module file not found for pipeline '{name}'")
                    pipeline_summary["module"] = "# Module file not found"
                except Exception as e:
                    logger.error(
                        f"Error reading module file for pipeline '{name}': {e}"
                    )
                    pipeline_summary["module"] = f"# Error reading module file: {e}"

            if pipeline_summary:  # Only add if cfg or code was requested and found
                summary["pipelines"][name] = pipeline_summary
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
            posixpath.splitext(posixpath.basename(f))[0] for f in pipeline_files
        ]  # Simplified name extraction

        if not pipeline_files:
            rich.print("[yellow]No pipelines found[/yellow]")
            return []  # Return empty list for consistency

        pipeline_info = []

        for path, name in zip(pipeline_files, pipeline_names):
            try:
                mod_time = self._fs.modified(path).strftime("%Y-%m-%d %H:%M:%S")
            except NotImplementedError:
                mod_time = "N/A"
            try:
                size_bytes = self._fs.size(path)
                size = f"{size_bytes / 1024:.1f} KB" if size_bytes else "0.0 KB"
            except NotImplementedError:
                size = "N/A"
            except Exception as e:
                logger.warning(f"Could not get size for {path}: {e}")
                size = "Error"

            pipeline_info.append({
                "name": name,
                "path": path,
                "mod_time": mod_time,
                "size": size,
            })

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

    def add_hook(
        self,
        name: str,
        type: HookType,
        to: str | None = None,
        function_name: str | None = None,
    ):
        """
        Add a hook to the pipeline module.

        Args:
            name (str): The name of the pipeline
            type (HookType): The type of the hook.
            to (str | None, optional): The name of the file to add the hook to. Defaults to the hook.py file in the pipelines hooks folder.
            function_name (str | None, optional): The name of the function. If not provided uses default name of hook type.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            pm.add_hook(HookType.PRE_EXECUTE)
            ```
        """

        if to is None:
            to = f"hooks/{name}/hook.py"
        else:
            to = f"hooks/{name}/{to}"

        match type:
            case HookType.MQTT_BUILD_CONFIG:
                template = HOOK_TEMPLATE__MQTT_BUILD_CONFIG

        if function_name is None:
            function_name = type.default_function_name()

        if not self._fs.exists(to):
            self._fs.makedirs(os.path.dirname(to), exist_ok=True)

        with self._fs.open(to, "a") as f:
            f.write(template.format(function_name=function_name))

        rich.print(
            f"🔧 Added hook [bold blue]{type.value}[/bold blue] to {to} as {function_name} for {name}"
        )
