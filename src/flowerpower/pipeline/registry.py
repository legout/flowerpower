# -*- coding: utf-8 -*-
"""Pipeline Registry for discovery, listing, creation, and deletion."""

import datetime as dt
import os
import posixpath
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict

import rich
from fsspec_utils import AbstractFileSystem, filesystem
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from ..settings import CONFIG_DIR, LOG_LEVEL, PIPELINES_DIR
# Import necessary config types and utility functions
from ..cfg import PipelineConfig, ProjectConfig
from ..utils.logging import setup_logging
# Assuming view_img might be used indirectly or needed later
from ..utils.templates import (HOOK_TEMPLATE__MQTT_BUILD_CONFIG,
                               PIPELINE_PY_TEMPLATE)
# Import base utilities
from .base import load_module

if TYPE_CHECKING:
    from .pipeline import Pipeline
    from ..flowerpower import FlowerPowerProject

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


@dataclass
class CachedPipelineData:
    """Container for cached pipeline data."""
    pipeline: "Pipeline"
    config: PipelineConfig
    module: Any


setup_logging(level=LOG_LEVEL)


class PipelineRegistry:
    """Manages discovery, listing, creation, and deletion of pipelines."""

    def __init__(
        self,
        project_cfg: ProjectConfig,
        fs: AbstractFileSystem,
        base_dir: str | None = None,
        storage_options: dict | None = None,
    ):
        """
        Initializes the PipelineRegistry.

        Args:
            project_cfg: The project configuration object.
            fs: The filesystem instance.
            base_dir: The base directory path.
            storage_options: Storage options for filesystem operations.
        """
        self.project_cfg = project_cfg
        self._fs = fs
        self._cfg_dir = CONFIG_DIR
        self._pipelines_dir = PIPELINES_DIR
        self._base_dir = base_dir
        self._storage_options = storage_options or {}
        self._console = Console()

        # Consolidated cache for pipeline data
        self._pipeline_data_cache: Dict[str, CachedPipelineData] = {}

        # Ensure module paths are added
        self._add_modules_path()

    @classmethod
    def from_filesystem(
        cls,
        base_dir: str,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | None = None,
    ) -> "PipelineRegistry":
        """
        Create a PipelineRegistry from filesystem parameters.

        This factory method creates a complete PipelineRegistry instance by:
        1. Creating the filesystem if not provided
        2. Loading the ProjectConfig from the base directory
        3. Initializing the registry with the loaded configuration

        Args:
            base_dir: The base directory path for the FlowerPower project
            fs: Optional filesystem instance. If None, will be created from base_dir
            storage_options: Optional storage options for filesystem access

        Returns:
            PipelineRegistry: A fully configured registry instance

        Raises:
            ValueError: If base_dir is invalid or ProjectConfig cannot be loaded
            RuntimeError: If filesystem creation fails

        Example:
            ```python
            # Create registry from local directory
            registry = PipelineRegistry.from_filesystem("/path/to/project")

            # Create registry with S3 storage
            registry = PipelineRegistry.from_filesystem(
                "s3://my-bucket/project",
                storage_options={"key": "secret"}
            )
            ```
        """
        # Create filesystem if not provided
        if fs is None:
            fs = filesystem(
                base_dir,
                storage_options=storage_options,
                cached=storage_options is not None,
            )

        # Load project configuration
        project_cfg = ProjectConfig.load(base_dir=base_dir, fs=fs)

        # Ensure we have a ProjectConfig instance
        if not isinstance(project_cfg, ProjectConfig):
            raise TypeError(f"Expected ProjectConfig, got {type(project_cfg)}")

        # Create and return registry instance
        return cls(
            project_cfg=project_cfg,
            fs=fs,
            base_dir=base_dir,
            storage_options=storage_options,
        )

    def _add_modules_path(self) -> None:
        """Add pipeline module paths to Python path."""
        try:
            if hasattr(self._fs, "is_cache_fs") and self._fs.is_cache_fs:
                self._fs.sync_cache()
                project_path = self._fs._mapper.directory
                modules_path = posixpath.join(project_path, self._pipelines_dir)
            else:
                # Use the base directory directly if not using cache
                if hasattr(self._fs, "path"):
                    project_path = self._fs.path
                elif self._base_dir:
                    project_path = self._base_dir
                else:
                    # Fallback for mocked filesystems
                    project_path = "."
                modules_path = posixpath.join(project_path, self._pipelines_dir)

            if project_path not in sys.path:
                sys.path.insert(0, project_path)

            if modules_path not in sys.path:
                sys.path.insert(0, modules_path)
        except (AttributeError, TypeError):
            # Handle case where filesystem is mocked or doesn't have required properties
            logger.debug("Could not add modules path - using default Python path")

    # --- Pipeline Factory Methods ---

    def get_pipeline(
        self, name: str, project_context: "FlowerPowerProject", reload: bool = False
    ) -> "Pipeline":
        """Get a Pipeline instance for the given name.

        This method creates a fully-formed Pipeline object by loading its configuration
        and Python module, then injecting the project context.

        Args:
            name: Name of the pipeline to get
            project_context: Reference to the FlowerPowerProject
            reload: Whether to reload configuration and module from disk

        Returns:
            Pipeline instance ready for execution

        Raises:
            FileNotFoundError: If pipeline configuration or module doesn't exist
            ImportError: If pipeline module cannot be imported
            ValueError: If pipeline configuration is invalid
        """
        # Use cache if available and not reloading
        if not reload and name in self._pipeline_data_cache:
            logger.debug(f"Returning cached pipeline '{name}'")
            return self._pipeline_data_cache[name].pipeline

        logger.debug(f"Creating pipeline instance for '{name}'")

        # Load pipeline configuration
        config = self.load_config(name, reload=reload)

        # Load pipeline module
        module = self.load_module(name, reload=reload)

        # Import Pipeline class here to avoid circular import
        from .pipeline import Pipeline

        # Create Pipeline instance
        pipeline = Pipeline(
            name=name,
            config=config,
            module=module,
            project_context=project_context,
        )

        # Cache the pipeline data
        self._pipeline_data_cache[name] = CachedPipelineData(
            pipeline=pipeline,
            config=config,
            module=module,
        )

        logger.debug(f"Successfully created pipeline instance for '{name}'")
        return pipeline

    def load_config(self, name: str, reload: bool = False) -> PipelineConfig:
        """Load pipeline configuration from disk.

        Args:
            name: Name of the pipeline
            reload: Whether to reload from disk even if cached

        Returns:
            PipelineConfig instance
        """
        # Use cache if available and not reloading
        if not reload and name in self._pipeline_data_cache:
            logger.debug(f"Returning cached config for pipeline '{name}'")
            return self._pipeline_data_cache[name].config

        logger.debug(f"Loading configuration for pipeline '{name}'")

        # Load configuration from disk
        config = PipelineConfig.load(
            base_dir=self._base_dir,
            name=name,
            fs=self._fs,
            storage_options=self._storage_options,
        )

        # Cache the configuration (will be stored in consolidated cache when pipeline is created)
        # For now, we'll create a temporary cache entry if it doesn't exist
        if name not in self._pipeline_data_cache:
            self._pipeline_data_cache[name] = CachedPipelineData(
                pipeline=None,  # type: ignore
                config=config,
                module=None,  # type: ignore
            )

        return config

    def load_module(self, name: str, reload: bool = False) -> Any:
        """Load pipeline module from disk.

        Args:
            name: Name of the pipeline
            reload: Whether to reload from disk even if cached

        Returns:
            Loaded Python module
        """
        # Use cache if available and not reloading
        if not reload and name in self._pipeline_data_cache:
            cached_data = self._pipeline_data_cache[name]
            if cached_data.module is not None:
                logger.debug(f"Returning cached module for pipeline '{name}'")
                return cached_data.module

        logger.debug(f"Loading module for pipeline '{name}'")

        # Convert pipeline name to module name
        formatted_name = name.replace(".", "/").replace("-", "_")
        module_name = f"pipelines.{formatted_name}"

        # Load the module
        module = load_module(module_name, reload=reload)

        # Cache the module (will be stored in consolidated cache when pipeline is created)
        # For now, we'll update the existing cache entry if it exists
        if name in self._pipeline_data_cache:
            self._pipeline_data_cache[name].module = module
        else:
            self._pipeline_data_cache[name] = CachedPipelineData(
                pipeline=None,  # type: ignore
                config=None,  # type: ignore
                module=module,
            )

        return module

    def clear_cache(self, name: str | None = None):
        """Clear cached pipelines, configurations, and modules.

        Args:
            name: If provided, clear cache only for this pipeline.
                 If None, clear entire cache.
        """
        if name:
            logger.debug(f"Clearing cache for pipeline '{name}'")
            self._pipeline_data_cache.pop(name, None)
        else:
            logger.debug("Clearing entire pipeline cache")
            self._pipeline_data_cache.clear()

    # --- Methods moved from PipelineManager ---
    def new(self, name: str, overwrite: bool = False):
        """
        Adds a pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool): Whether to overwrite an existing pipeline. Defaults to False.

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
        cfg_file = posixpath.join(self._cfg_dir, PIPELINES_DIR, f"{formatted_name}.yml")

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
                self._cfg_dir, PIPELINES_DIR, f"{name}.yml"
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
        except (OSError, PermissionError) as e:
            logger.error(
                f"Error accessing pipeline directory {self._pipelines_dir}: {e}"
            )
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error accessing pipeline directory {self._pipelines_dir}: {e}"
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
                except (OSError, PermissionError, UnicodeDecodeError) as e:
                    logger.error(
                        f"Error reading module file for pipeline '{name}': {e}"
                    )
                    pipeline_summary["module"] = f"# Error reading module file: {e}"
                except Exception as e:
                    logger.error(
                        f"Unexpected error reading module file for pipeline '{name}': {e}"
                    )
                    pipeline_summary["module"] = f"# Unexpected error reading module file: {e}"

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
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not get size for {path}: {e}")
                size = "Error"
            except Exception as e:
                logger.warning(f"Unexpected error getting size for {path}: {e}")
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
