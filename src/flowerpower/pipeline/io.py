# -*- coding: utf-8 -*-
# mypy: disable-error-code="attr-defined"
# pylint: disable=no-member, E1136, W0212, W0201
"""
Manages the import and export of pipelines.
"""

import posixpath

from loguru import logger
from rich.console import Console

# Import necessary config types and utility functions
from ..fs.base import (AbstractFileSystem, BaseStorageOptions, DirFileSystem,
                       get_filesystem)
from ..settings import LOG_LEVEL
from ..utils.logging import setup_logging
from .registry import PipelineRegistry

console = Console()

setup_logging(level=LOG_LEVEL)


class PipelineIOManager:
    """Handles importing and exporting pipeline configurations and code."""

    def __init__(
        self,
        registry: PipelineRegistry,
    ):
        """
        Initializes the PipelineIOManager.

        Args:
            registry: The pipeline registry instance.
        """
        self.project_cfg = registry.project_cfg
        self.registry = registry
        self._fs = registry._fs
        self._cfg_dir = registry._cfg_dir
        self._pipelines_dir = registry._pipelines_dir

    def _sync_filesystem(
        self,
        src_base_dir: str,
        dest_base_dir: str,
        src_fs: AbstractFileSystem | None,
        dest_fs: AbstractFileSystem | None,
        src_storage_options: dict | BaseStorageOptions | None = {},
        dest_storage_options: dict | BaseStorageOptions | None = {},
        files: list[str] | None = None,
        overwrite: bool = False,
    ):
        """
        Synchronizes the source and destination filesystems.

        Args:
            src_base_dir (str): The source base directory.
            dest_base_dir (str): The destination base directory.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
            src_storage_options (dict | BaseStorageOptions | None, optional): Storage options for the source filesystem. Defaults to None.
            dest_storage_options (dict | BaseStorageOptions | None, optional): Storage options for the destination filesystem. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files. Defaults to False.
        Returns:
            tuple: A tuple containing the source and destination filesystems.
        """

        def _get_filesystem(base_dir, fs, storage_options):
            if fs is None:
                fs = get_filesystem(base_dir, storage_options=storage_options)
            else:
                if not isinstance(fs, AbstractFileSystem):
                    raise ValueError(
                        f"Invalid filesystem type: {type(fs)}. Expected AbstractFileSystem."
                    )
                if isinstance(fs, DirFileSystem):
                    if not fs.path == base_dir:
                        fs = DirFileSystem(base_dir, fs=fs)
                else:
                    fs = DirFileSystem(base_dir, fs=fs)
            return fs

        src_fs = _get_filesystem(src_base_dir, src_fs, src_storage_options)
        logger.debug(f"Source filesystem: {src_fs}")
        dest_fs = _get_filesystem(dest_base_dir, dest_fs, dest_storage_options)
        logger.debug(f"Destination filesystem: {dest_fs}")
        # try:
        #     src_mapper = src_fs.get_mapper(check=True, create=True)
        # except NotImplementedError:
        # try:
        #     src_mapper = src_fs.get_mapper(check=True, create=False)
        # except NotImplementedError:
        #     src_mapper = src_fs.get_mapper(check=False, create=False)
        # try:
        #     dest_mapper = dest_fs.get_mapper(check=True, create=False)
        # except NotImplementedError:
        #     raise NotImplementedError(
        #         f"The destination filesystem {dest_fs }does not support get_mapper."
        #     )

        if files is None:
            files = src_fs.glob("**/*.py")
            files.extend(src_fs.glob("**/*.yml"))

        for file in files:
            logger.debug(f"Copying {file} from {src_fs} to {dest_fs}")
            if not dest_fs.exists(posixpath.dirname(file)):
                logger.debug(
                    f"Creating directory {posixpath.dirname(file)} in destination filesystem."
                )
                try:
                    dest_fs.mkdir(posixpath.dirname(file), create_parents=True)
                except PermissionError:
                    dest_fs.touch(file, truncate=False)
            else:
                if not overwrite and dest_fs.exists(file):
                    logger.warning(
                        f"File {file} already exists in the destination. Skipping write. Use overwrite=True to overwrite."
                    )
                    continue

            content = src_fs.read_bytes(file)
            dest_fs.write_bytes(file, content)

    def import_pipeline(
        self,
        name: str,
        src_base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        src_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ):
        """
        Import a pipeline from a given path.

        Args:
            name (str): The name of the pipeline.
            src_base_dir (str): The path of the flowerpower project directory.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
            src_storage_options (BaseStorageOptions | None, optional): The storage options. Defaults to None.
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
        files = [
            "conf/project.yml",
            f"conf/pipelines/{name}.yml",
            f"pipelines/{name}.py",
        ]

        self._sync_filesystem(
            src_base_dir=src_base_dir,
            src_fs=src_fs,
            src_storage_options=src_storage_options,
            dest_base_dir=".",
            dest_fs=self._fs,
            dest_storage_options=None,
            files=files,
            overwrite=overwrite,
        )

        # Use project_cfg.name directly
        console.print(
            f"✅ Imported pipeline [bold blue]{name}[/bold blue] from [green]{src_base_dir}[/green] to [bold blue]{self.project_cfg.name}[/bold blue]"
        )

    def import_many(
        self,
        names: list[str],
        src_base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        src_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ):
        """
        Import multiple pipelines from given paths.

        Args:
            names (list[str]): A list of pipeline names to import.
            src_base_dir (str): The base path of the flowerpower project directory.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
            src_storage_options (BaseStorageOptions | None, optional): The storage options. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing pipelines. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()


            # Import multiple pipelines from a list
            pipelines_to_import = ["pipeline1", "pipeline2"]
            pm.import_many(pipelines_to_import, "/path/to/fp_project", overwrite=True)
            ```
        """

        files = ["conf/project.yml"]

        for name in names:
            files.extend(
                [
                    f"conf/pipelines/{name}.yml",
                    f"pipelines/{name}.py",
                ]
            )

        # Sync the filesystem
        self._sync_filesystem(
            src_base_dir=src_base_dir,
            src_fs=src_fs,
            src_storage_options=src_storage_options,
            dest_base_dir=".",
            dest_fs=self._fs,
            dest_storage_options=None,
            files=files,
            overwrite=overwrite,
        )
        console.print(
            f"✅ Imported pipelines [bold blue]{', '.join(names)}[/bold blue] from [green]{src_base_dir}[/green] to [bold blue]{self.project_cfg.name}[/bold blue]"
        )

    def import_all(
        self,
        src_base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        src_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ):
        """Import all pipelines from a given path.

        Args:
            src_base_dir (str): The base path containing pipeline modules and configurations.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
            src_storage_options (BaseStorageOptions | None, optional): Storage options for the source path. Defaults to None.
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
        self._sync_filesystem(
            src_base_dir=src_base_dir,
            src_fs=src_fs,
            src_storage_options=src_storage_options,
            dest_base_dir=".",
            dest_fs=self._fs,
            dest_storage_options=None,
            files=None,
            overwrite=overwrite,
        )
        console.print(
            f"✅ Imported all pipelines from [green]{src_base_dir}[/green] to [bold blue]{self.project_cfg.name}[/bold blue]"
        )

    def export_pipeline(
        self,
        name: str,
        dest_base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        dest_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ):
        """
        Export a pipeline to a given path.

        Args:
            name (str): The name of the pipeline.
            dest_base_dir (str): The destination path.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
            dest_storage_options (BaseStorageOptions | None, optional): Storage options for the destination path. Defaults to None.
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
        files = [
            "conf/project.yml",
            f"conf/pipelines/{name}.yml",
            f"pipelines/{name}.py",
        ]

        # Sync the filesystem
        self._sync_filesystem(
            src_base_dir=".",
            src_fs=self._fs,
            src_storage_options=None,
            dest_base_dir=dest_base_dir,
            dest_fs=dest_fs,
            dest_storage_options=dest_storage_options,
            files=files,
            overwrite=overwrite,
        )

        console.print(
            f"✅ Exported pipeline [bold blue]{self.project_cfg.name}.{name}[/bold blue] to [green]{dest_base_dir}[/green]"
        )

    def export_many(
        self,
        names: list[str],
        dest_base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        dest_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ):
        """
        Export multiple pipelines to a directory.

        Args:
            pipelines (list[str]): A list of pipeline names to export.
            dest_base_dir (str): The destination directory path.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
            dest_storage_options (BaseStorageOptions | None, optional): Storage options for the destination path. Defaults to None.
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
        files = [
            "conf/project.yml",
        ]
        for name in names:
            # Check if the pipeline exists in the registry
            if not self.registry.has_pipeline(name):
                raise ValueError(
                    f"Pipeline {name} does not exist in the registry. Please check the name."
                )
            # Add pipeline files to the list
            files.extend(
                [
                    f"conf/pipelines/{name}.yml",
                    f"pipelines/{name}.py",
                ]
            )
        # Sync the filesystem
        self._sync_filesystem(
            src_base_dir=".",
            src_fs=self._fs,
            src_storage_options=None,
            dest_base_dir=dest_base_dir,
            dest_fs=dest_fs,
            dest_storage_options=dest_storage_options,
            files=files,
            overwrite=overwrite,
        )
        console.print(
            f"✅ Exported pipelines [bold blue]{', '.join([self.project_cfg.name + '.' + name for name in names])}[/bold blue] to [green]{dest_base_dir}[/green]"
        )

    def export_all(
        self,
        dest_base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        dest_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ):
        """Export all pipelines to a given path.

        Args:
            dest_base_dir (str): The destination directory path.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
            dest_storage_options (BaseStorageOptions | None, optional): Storage options for the destination path. Defaults to None.
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
        # sync the filesystem
        self._sync_filesystem(
            src_base_dir=".",
            src_fs=self._fs,
            src_storage_options=None,
            dest_base_dir=dest_base_dir,
            dest_fs=dest_fs,
            dest_storage_options=dest_storage_options,
            files=None,
            overwrite=overwrite,
        )
        console.print(
            f"✅ Exported all pipelines from [bold blue]{self.project_cfg.name}[/bold blue] to [green]{dest_base_dir}[/green]"
        )
