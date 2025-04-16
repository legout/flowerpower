# -*- coding: utf-8 -*-
# mypy: disable-error-code="attr-defined"
# pylint: disable=no-member, E1136, W0212, W0201
"""
Manages the import and export of pipelines.
"""
import posixpath
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from fsspec.spec import AbstractFileSystem
from munch import Munch
from rich.console import Console

from ..cfg.pipeline.params import PipelineConfig
from ..cfg.pipeline.run import PipelineRunConfig
from ..cfg.pipeline.schedule import PipelineScheduleConfig
from ..cfg.pipeline.tracker import PipelineTrackerConfig
from ..cfg.project import ProjectConfig
from ..fs.base import BaseStorageOptions, get_filesystem
from .registry import PipelineRegistry  # Needed for type hints

console = Console()


class PipelineIOManager:
    """Handles importing and exporting pipeline configurations and code."""

    def __init__(
        self,
        fs: AbstractFileSystem,
        cfg_dir: str,
        pipelines_dir: str,
        registry: PipelineRegistry,  # Add registry dependency
    ):
        """
        Initializes the PipelineIOManager.

        Args:
            fs: The filesystem instance.
            cfg_dir: The directory for pipeline configurations.
            pipelines_dir: The directory for pipeline code.
            registry: The pipeline registry instance.
        """
        self._fs = fs
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        self._registry = registry  # Store registry

    def import_pipeline(
        self,
        name: str,
        path: str,
        storage_options: Optional[BaseStorageOptions] = None,
        overwrite: bool = False,
    ):
        """
        Import a pipeline from a given path.

        Args:
            name (str): The name of the pipeline.
            path (str): The path to the pipeline directory.
            storage_options (BaseStorageOptions | None, optional): The storage options. Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing pipeline. Defaults to False.

        Returns:
            None

        Raises:
            ValueError: If the pipeline already exists and overwrite is False.

        Examples:
            ```python
            pm = PipelineManager()
            pm.import_pipeline("my_pipeline", "/path/to/pipeline")
            ```
        """
        fs = get_filesystem(path, **(storage_options or {}))

        pipeline_path = f"{self._pipelines_dir}/{name.replace('.', '/')}.py"
        cfg_path = f"{self._cfg_dir}/pipelines/{name.replace('.', '/')}.yml"

        if self._fs.exists(pipeline_path) or self._fs.exists(cfg_path):
            if overwrite:
                if self._fs.exists(pipeline_path):
                    self._fs.rm(pipeline_path)
                if self._fs.exists(cfg_path):
                    self._fs.rm(cfg_path)
            else:
                # Use registry's project name if available
                project_name = self._registry.cfg.project.name if self._registry.cfg else "unknown_project"
                raise ValueError(
                    f"Pipeline {project_name}.{name.replace('.', '/')} already exists. "
                    "Use `overwrite=True` to overwrite."
                )

        self._fs.makedirs(pipeline_path.rsplit("/", 1)[0], exist_ok=True)
        self._fs.makedirs(cfg_path.rsplit("/", 1)[0], exist_ok=True)

        # Copy pipeline module
        src_pipeline_file = f"{path}/{name.replace('.', '/')}.py"
        if fs.exists(src_pipeline_file):
            with fs.open(src_pipeline_file, "rb") as f_src, self._fs.open(
                pipeline_path, "wb"
            ) as f_dst:
                shutil.copyfileobj(f_src, f_dst)
        else:
            console.print(f"⚠️ Pipeline module file not found at: {src_pipeline_file}", style="yellow")


        # Copy pipeline config
        src_cfg_file = f"{path}/{name.replace('.', '/')}.yml"
        if fs.exists(src_cfg_file):
             with fs.open(src_cfg_file, "rb") as f_src, self._fs.open(
                cfg_path, "wb"
            ) as f_dst:
                shutil.copyfileobj(f_src, f_dst)
        else:
            console.print(f"⚠️ Pipeline config file not found at: {src_cfg_file}", style="yellow")


        # Use registry's project name if available
        project_name = self._registry.cfg.project.name if self._registry.cfg else "unknown_project"
        console.print(
            f"✅ Imported pipeline [bold blue]{project_name}.{name}[/bold blue] from [green]{path}[/green]"
        )

    def import_many(
        self,
        pipelines: Dict[str, str],
        storage_options: Optional[BaseStorageOptions] = None,
        overwrite: bool = False,
    ):
        """
        Import multiple pipelines from given paths.

        Args:
            pipelines (Dict[str, str]): A dictionary where keys are pipeline names and values are paths.
            storage_options (BaseStorageOptions | None, optional): The storage options. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing pipelines. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            pipelines_to_import = {
                "pipeline1": "/path/to/pipeline1",
                "pipeline2": "s3://bucket/pipeline2"
            }
            pm.import_many(pipelines_to_import, overwrite=True)
            ```
        """
        for name, path in pipelines.items():
            try:
                self.import_pipeline(
                    name=name,
                    path=path,
                    storage_options=storage_options,
                    overwrite=overwrite,
                )
            except Exception as e:
                console.print(
                    f"❌ Failed to import pipeline [bold blue]{name}[/bold blue] from [red]{path}[/red]: {e}",
                    style="red",
                )

    def import_all(
        self,
        path: str,
        storage_options: Optional[BaseStorageOptions] = None,
        overwrite: bool = False,
    ):
        """Import all pipelines from a given path.

        Assumes the source path has a structure similar to the target `pipelines_dir` and `cfg_dir`/pipelines.

        Args:
            path (str): The base path containing pipeline modules and configurations.
            storage_options (BaseStorageOptions | None, optional): Storage options for the source path. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing pipelines. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            # Import all pipelines from a local directory
            pm.import_all("/path/to/exported_pipelines", overwrite=True)
            # Import all pipelines from an S3 bucket
            # pm.import_all("s3://my-bucket/pipelines_backup", storage_options={"key": "...", "secret": "..."}, overwrite=False)
            ```
        """
        fs = get_filesystem(path, **(storage_options or {}))
        console.print(f"🔍 Searching for pipelines in [green]{path}[/green]...")

        # Find all .py files in the source path (recursively)
        try:
            # Assuming pipelines are directly under the path, adjust if nested deeper e.g. path/pipelines/*.py
            pipeline_files = fs.glob(f"{path}/**/*.py", recursive=True)
        except NotImplementedError:
             # Fallback for filesystems that don't support recursive glob
             pipeline_files = fs.glob(f"{path}/*.py") # Check top level
             # Add logic here to check common subdirs like 'pipelines' if needed

        names = [
            f.replace(f"{path}/", "").replace(".py", "").replace("/", ".")
            for f in pipeline_files if not f.endswith("__init__.py") # Exclude __init__.py
        ]

        if not names:
            console.print("🤷 No pipeline modules (.py files) found in the specified path.", style="yellow")
            return

        console.print(f"Found {len(names)} potential pipeline modules. Importing...")

        pipelines_to_import = {name: path for name in names}
        self.import_many(pipelines_to_import, storage_options, overwrite)


    def export(
        self,
        name: str,
        path: str,
        storage_options: Optional[BaseStorageOptions] = None,
        overwrite: bool = False,
    ):
        """
        Export a pipeline to a given path.

        Args:
            name (str): The name of the pipeline.
            path (str): The destination path.
            storage_options (BaseStorageOptions | None, optional): Storage options for the destination path. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files at the destination. Defaults to False.

        Returns:
            None

        Raises:
            ValueError: If the pipeline does not exist or if the destination exists and overwrite is False.

        Examples:
            ```python
            pm = PipelineManager()
            pm.export("my_pipeline", "/path/to/export_dir")
            # Export to S3
            # pm.export("my_pipeline", "s3://my-bucket/exports", storage_options={"key": "...", "secret": "..."})
            ```
        """
        # Use registry to check existence
        if name not in self._registry.pipelines:
             # Use registry's project name if available
            project_name = self._registry.cfg.project.name if self._registry.cfg else "unknown_project"
            raise ValueError(f"Pipeline {project_name}.{name} does not exist.")

        fs = get_filesystem(path, **(storage_options or {}))
        fs.makedirs(path, exist_ok=True) # Ensure destination exists

        dest_pipeline_path = f"{path}/{name.replace('.', '/')}.py"
        dest_cfg_path = f"{path}/{name.replace('.', '/')}.yml"

        # Check overwrite condition for destination files
        if not overwrite and (fs.exists(dest_pipeline_path) or fs.exists(dest_cfg_path)):
            raise ValueError(
                f"Destination path {path}/{name.replace('.', '/')} already contains files. Use `overwrite=True` to overwrite."
            )

        # Create necessary subdirectories in the destination
        fs.makedirs(dest_pipeline_path.rsplit("/", 1)[0], exist_ok=True)
        fs.makedirs(dest_cfg_path.rsplit("/", 1)[0], exist_ok=True)


        # Copy pipeline module
        src_pipeline_path = f"{self._pipelines_dir}/{name.replace('.', '/')}.py"
        if self._fs.exists(src_pipeline_path):
            with self._fs.open(src_pipeline_path, "rb") as f_src, fs.open(
                dest_pipeline_path, "wb"
            ) as f_dst:
                shutil.copyfileobj(f_src, f_dst)
        else:
             console.print(f"⚠️ Source pipeline module not found: {src_pipeline_path}", style="yellow")


        # Copy pipeline config
        src_cfg_path = f"{self._cfg_dir}/pipelines/{name.replace('.', '/')}.yml"
        if self._fs.exists(src_cfg_path):
            with self._fs.open(src_cfg_path, "rb") as f_src, fs.open(
                dest_cfg_path, "wb"
            ) as f_dst:
                shutil.copyfileobj(f_src, f_dst)
        else:
            console.print(f"⚠️ Source pipeline config not found: {src_cfg_path}", style="yellow")

        # Use registry's project name if available
        project_name = self._registry.cfg.project.name if self._registry.cfg else "unknown_project"
        console.print(
            f"✅ Exported pipeline [bold blue]{project_name}.{name}[/bold blue] to [green]{path}[/green]"
        )


    def export_many(
        self,
        pipelines: List[str],
        path: str,
        storage_options: Optional[BaseStorageOptions] = None,
        overwrite: bool = False,
    ):
        """
        Export multiple pipelines to a directory.

        Args:
            pipelines (List[str]): A list of pipeline names to export.
            path (str): The destination directory path.
            storage_options (BaseStorageOptions | None, optional): Storage options for the destination path. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files at the destination. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            pipelines_to_export = ["pipeline1", "pipeline2.subpipeline"]
            pm.export_many(pipelines_to_export, "/path/to/export_dir", overwrite=True)
            ```
        """
        fs = get_filesystem(path, **(storage_options or {}))
        fs.makedirs(path, exist_ok=True) # Ensure base destination exists

        for name in pipelines:
            try:
                self.export(
                    name=name,
                    path=path, # Pass the base path
                    storage_options=storage_options,
                    overwrite=overwrite,
                )
            except Exception as e:
                 # Use registry's project name if available
                project_name = self._registry.cfg.project.name if self._registry.cfg else "unknown_project"
                console.print(
                    f"❌ Failed to export pipeline [bold blue]{project_name}.{name}[/bold blue] to [red]{path}[/red]: {e}",
                    style="red",
                )

    def export_all(
        self,
        path: str,
        storage_options: Optional[BaseStorageOptions] = None,
        overwrite: bool = False,
    ):
        """Export all pipelines to a given path.

        Args:
            path (str): The destination directory path.
            storage_options (BaseStorageOptions | None, optional): Storage options for the destination path. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files at the destination. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            # Export all pipelines to a local directory
            pm.export_all("/path/to/backup_dir", overwrite=True)
            # Export all pipelines to S3
            # pm.export_all("s3://my-bucket/pipelines_backup", storage_options={"key": "...", "secret": "..."}, overwrite=False)
            ```
        """
        fs = get_filesystem(path, **(storage_options or {}))
        fs.makedirs(path, exist_ok=True) # Ensure base destination exists

        # Use registry to get all pipeline names
        names = self._registry.pipelines
        if not names:
            console.print("🤷 No pipelines found in the registry to export.", style="yellow")
            return

        console.print(f"Found {len(names)} pipelines in the registry. Exporting all to [green]{path}[/green]...")

        self.export_many(names, path, storage_options, overwrite)