# -*- coding: utf-8 -*-
# mypy: disable-error-code="attr-defined"
# pylint: disable=no-member, E1136, W0212, W0201
"""
Manages the import and export of pipelines.
"""

import posixpath

from fsspec.spec import AbstractFileSystem
from rich.console import Console

from ..fs.base import BaseStorageOptions, get_filesystem
from .registry import PipelineRegistry  # Needed for type hints

console = Console()


class PipelineIOManager:
    """Handles importing and exporting pipeline configurations and code."""

    def __init__(
        self,
        fs: AbstractFileSystem,
        # cfg_dir: str,
        # pipelines_dir: str,
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
        self._registry = registry  # Store registry
        self._cfg_dir = self._registry._cfg_dir
        self._pipelines_dir = self._registry._pipelines_dir

    def import_pipeline(
        self,
        name: str,
        base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """
        Import a pipeline from a given path.

        Args:
            name (str): The name of the pipeline.
            base_dir (str): The path of the flowerpower project directory.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
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
        if src_fs is None:
            src_fs = get_filesystem(base_dir, **(storage_options or {}))

        dest_pipeline_file = posixpath.join(
            self._pipelines_dir, f"{name.replace('.', '/')}.py"
        )
        dest_cfg_file = posixpath.join(
            self._cfg_dir, "pipelines", f"{name.replace('.', '/')}.yml"
        )
        src_pipeline_file = posixpath.join("pipelines", f"{name.replace('.', '/')}.py")
        src_cfg_file = posixpath.join(
            "conf", "pipelines", f"{name.replace('.', '/')}.yml"
        )

        if not src_fs.exists(src_pipeline_file):
            raise ValueError(f"Pipeline module file not found at: {src_pipeline_file}")
        if not src_fs.exists(src_cfg_file):
            raise ValueError(f"Pipeline config file not found at: {src_cfg_file}")

        cfg = self._registry._load_config_func()

        if self._fs.exists(dest_pipeline_file) or self._fs.exists(dest_cfg_file):
            if overwrite:
                if self._fs.exists(dest_pipeline_file):
                    self._fs.rm(dest_pipeline_file)
                if self._fs.exists(dest_cfg_file):
                    self._fs.rm(dest_cfg_file)
            else:
                # Use registry's project name if available
                project_name = cfg.project.name or "unknown_flowerpower_project"

                raise ValueError(
                    f"Pipeline {project_name}.{name.replace('.', '/')} already exists. "
                    "Use `overwrite=True` to overwrite."
                )

        self._fs.makedirs(posixpath.dirname(dest_pipeline_file), exist_ok=True)
        self._fs.makedirs(posixpath.dirname(dest_cfg_file), exist_ok=True)

        self._fs.write_bytes(dest_pipeline_file, src_fs.read_bytes(src_pipeline_file))
        self._fs.write_bytes(dest_cfg_file, src_fs.read_bytes(src_cfg_file))

        # Use registry's project name if available
        project_name = cfg.project.name if cfg else "unknown_flowerpower_project"
        console.print(
            f"✅ Imported pipeline [bold blue]{project_name}.{name}[/bold blue] from [green]{base_dir}[/green]"
        )

    def import_many(
        self,
        pipelines: dict[str, str] | list[str],
        base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """
        Import multiple pipelines from given paths.

        Args:
            pipelines (dict[str, str] | list[str]): A dictionary where keys are pipeline names and values are paths or
                a list of pipeline names to import.
            base_dir (str): The base path of the flowerpower project directory.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
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
        if isinstance(pipelines, list):
            pipelines = {name: base_dir for name in pipelines}

        for name, base_dir in pipelines.items():
            try:
                self.import_pipeline(
                    name=name,
                    base_dir=base_dir,
                    src_fs=src_fs,
                    storage_options=storage_options,
                    overwrite=overwrite,
                )
            except Exception as e:
                console.print(
                    f"❌ Failed to import pipeline [bold blue]{name}[/bold blue] from [red]{base_dir}[/red]: {e}",
                    style="red",
                )

    def import_all(
        self,
        base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Import all pipelines from a given path.

        Assumes the source path has a structure similar to the target `pipelines_dir` and `cfg_dir`/pipelines.

        Args:
            base_dir (str): The base path containing pipeline modules and configurations.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
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
        if not src_fs:
            src_fs = get_filesystem(base_dir, **(storage_options or {}))

        console.print(f"🔍 Search pipelines in [green]{base_dir}[/green]...")

        # Find all .py files in the source path (recursively)
        try:
            # Assuming pipelines are directly under the path, adjust if nested deeper e.g. path/pipelines/*.py
            pipeline_files = src_fs.glob("**/*.py", recursive=True)
        except NotImplementedError:
            # Fallback for filesystems that don't support recursive glob
            pipeline_files = src_fs.glob("*.py")  # Check top level
            # Add logic here to check common subdirs like 'pipelines' if needed

        names = [
            f.replace(f"{base_dir}/", "").replace(".py", "").replace("/", ".")
            for f in pipeline_files
            if not f.endswith("__init__.py")  # Exclude __init__.py
        ]

        if not names:
            console.print(
                "🤷 No pipeline modules (.py files) found in the specified path.",
                style="yellow",
            )
            return

        console.print(f"Found {len(names)} potential pipeline modules. Importing...")

        pipelines_to_import = {name: base_dir for name in names}
        self.import_many(
            pipelines=pipelines_to_import,
            base_dir=base_dir,
            src_fs=src_fs,
            storage_options=storage_options,
            overwrite=overwrite,
        )

    def export_pipeline(
        self,
        name: str,
        base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """
        Export a pipeline to a given path.

        Args:
            name (str): The name of the pipeline.
            base_dir (str): The destination path.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
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
        cfg = self._registry._load_config_func()
        # Use registry to check existence
        if name not in self._registry.pipelines:
            # Use registry's project name if available
            project_name = cfg.project.name or "unknown_flowerpower_project"

            raise ValueError(f"Pipeline {project_name}.{name} does not exist.")

        if dest_fs is None:
            dest_fs = get_filesystem(base_dir, **(storage_options or {}))

        dest_pipeline_file = posixpath.join("pipelines", f"{name.replace('.', '/')}.py")
        dest_cfg_file = posixpath.join(
            "conf", "pipelines", f"{name.replace('.', '/')}.yml"
        )
        src_pipeline_file = posixpath.join(
            self._pipelines_dir, f"{name.replace('.', '/')}.py"
        )
        src_cfg_file = posixpath.join(
            self._cfg_dir, "pipelines", f"{name.replace('.', '/')}.yml"
        )

        # Check overwrite condition for destination files
        if not overwrite and (
            dest_fs.exists(dest_pipeline_file) or dest_fs.exists(dest_cfg_file)
        ):
            raise ValueError(
                f"Destination path {base_dir}/{name.replace('.', '/')} already contains files. Use `overwrite=True` to overwrite."
            )

        # Create necessary subdirectories in the destination
        dest_fs.makedirs(posixpath.dirname(dest_pipeline_file), exist_ok=True)
        dest_fs.makedirs(posixpath.dirname(dest_cfg_file), exist_ok=True)

        # Copy pipeline module and config
        dest_fs.write_bytes(dest_pipeline_file, self._fs.read_bytes(src_pipeline_file))
        dest_fs.write_bytes(dest_cfg_file, self._fs.read_bytes(src_cfg_file))

        # Use registry's project name if available
        project_name = cfg.project.name or "unknown_flowerpower_project"

        console.print(
            f"✅ Exported pipeline [bold blue]{project_name}.{name}[/bold blue] to [green]{base_dir}[/green]"
        )

    def export_many(
        self,
        pipelines: list[str],
        base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """
        Export multiple pipelines to a directory.

        Args:
            pipelines (list[str]): A list of pipeline names to export.
            base_dir (str): The destination directory path.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
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
        for name in pipelines:
            try:
                self.export_pipeline(
                    name=name,
                    base_dir=base_dir,
                    dest_fs=dest_fs,
                    storage_options=storage_options,
                    overwrite=overwrite,
                )
            except Exception as e:
                # Use registry's project name if available
                cfg = self._registry._load_config_func()
                project_name = cfg.project.name or "unknown_flowerpower_project"

                console.print(
                    f"❌ Failed to export pipeline [bold blue]{project_name}.{name}[/bold blue] to [red]{base_dir}[/red]: {e}",
                    style="red",
                )

    def export_all(
        self,
        base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Export all pipelines to a given path.

        Args:
            base_dir (str): The destination directory path.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
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

        # Use registry to get all pipeline names
        pipelines = self._registry.pipelines
        if not pipelines:
            console.print(
                "🤷 No pipelines found in the registry to export.", style="yellow"
            )
            return

        console.print(
            f"Found {len(pipelines)} pipelines in the registry. Exporting all to [green]{base_dir}[/green]..."
        )

        self.export_many(
            pipelines=pipelines,
            base_dir=base_dir,
            dest_fs=dest_fs,
            storage_options=storage_options,
            overwrite=overwrite,
        )
