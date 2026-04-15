# mypy: disable-error-code="attr-defined"
# pylint: disable=no-member, E1136, W0212, W0201
"""
Manages the import and export of pipelines.
"""

import posixpath

from fsspeckit import (
    AbstractFileSystem,
    BaseStorageOptions,
    DirFileSystem,
    filesystem,
)
from loguru import logger
from rich.console import Console

from ..settings import LOG_LEVEL
from ..utils.filesystem import (
    find_first_existing_path,
    format_pipeline_file_path,
    get_pipeline_config_paths,
    get_project_config_paths,
)
from ..utils.logging import setup_logging
from ..utils.security import validate_pipeline_name
from .registry import PipelineRegistry

# Import necessary config types and utility functions


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
        self.registry = registry
        self._fs = registry._fs
        self._cfg_dir = registry._cfg_dir
        self._pipelines_dir = registry._pipelines_dir

    @property
    def project_cfg(self):
        return self.registry.project_cfg

    @staticmethod
    def _get_dir_filesystem(
        base_dir: str,
        fs: AbstractFileSystem | None,
        storage_options: dict | BaseStorageOptions | None,
    ) -> AbstractFileSystem:
        if fs is None:
            return filesystem(base_dir, storage_options=storage_options)

        if not isinstance(fs, AbstractFileSystem):
            raise ValueError(
                f"Invalid filesystem type: {type(fs)}. Expected AbstractFileSystem."
            )

        if isinstance(fs, DirFileSystem):
            if fs.path == base_dir:
                return fs
            return DirFileSystem(base_dir, fs=fs)

        return DirFileSystem(base_dir, fs=fs)

    def _project_config_files(self) -> list[str]:
        return get_project_config_paths(self._cfg_dir)

    def _resolve_project_config_file(
        self,
        fs: AbstractFileSystem | None = None,
    ) -> str:
        candidates = self._project_config_files()
        if fs is None:
            return candidates[0]

        return (
            find_first_existing_path(fs, candidates, purpose="project config")
            or candidates[0]
        )

    def _resolve_pipeline_config_file(
        self,
        name: str,
        fs: AbstractFileSystem | None = None,
    ) -> str:
        formatted_name = format_pipeline_file_path(name)
        candidates = get_pipeline_config_paths(
            formatted_name,
            self._cfg_dir,
            self._pipelines_dir,
        )
        if fs is None:
            return candidates[0]

        return (
            find_first_existing_path(fs, candidates, purpose="pipeline config")
            or candidates[0]
        )

    def _project_label(self) -> str:
        project_name = getattr(self.project_cfg, "name", None)
        return project_name or "project"

    def _format_export_label(self, name: str) -> str:
        project_name = getattr(self.project_cfg, "name", None)
        return f"{project_name}.{name}" if project_name else name

    def _get_pipeline_files(
        self,
        name: str,
        fs: AbstractFileSystem | None = None,
    ) -> list[str]:
        """Get the list of files for a single pipeline."""
        formatted_name = format_pipeline_file_path(name)
        return [
            self._resolve_project_config_file(fs=fs),
            self._resolve_pipeline_config_file(name, fs=fs),
            posixpath.join(self._pipelines_dir, f"{formatted_name}.py"),
        ]

    def _get_many_pipeline_files(
        self,
        names: list[str],
        fs: AbstractFileSystem | None = None,
    ) -> list[str]:
        """Get the list of files for multiple pipelines."""
        files = [self._resolve_project_config_file(fs=fs)]
        for name in names:
            files.extend(self._get_pipeline_files(name, fs=fs)[1:])
        return files

    def _pipeline_exists(self, name: str) -> bool:
        name = validate_pipeline_name(name)
        target = format_pipeline_file_path(name)
        available = {
            format_pipeline_file_path(candidate) for candidate in self.registry.pipelines
        }
        return target in available

    def _discover_all_pipeline_files(self, fs: AbstractFileSystem) -> list[str]:
        """Discover all project/pipeline files for import/export.

        Restricts discovery to configured project, pipeline-config, and pipeline-module
        locations instead of copying every ``*.py``/``*.yml`` file in the tree.
        """
        files: list[str] = []
        seen: set[str] = set()

        project_config = find_first_existing_path(
            fs,
            self._project_config_files(),
            purpose="project config",
        )
        if project_config is not None:
            seen.add(project_config)
            files.append(project_config)

        module_patterns = [
            posixpath.join(self._pipelines_dir, "*.py"),
            posixpath.join(self._pipelines_dir, "**", "*.py"),
        ]

        module_files: list[str] = []
        for pattern in module_patterns:
            try:
                paths = fs.glob(pattern)
            except Exception as e:
                logger.debug(
                    f"Skipping unsupported pipeline discovery pattern {pattern}: {e}"
                )
                continue

            for path in paths:
                if posixpath.basename(path) == "__init__.py" or path in seen:
                    continue
                seen.add(path)
                files.append(path)
                module_files.append(path)

        for module_file in module_files:
            module_path = posixpath.splitext(
                posixpath.relpath(module_file, self._pipelines_dir)
            )[0]
            cfg_path = find_first_existing_path(
                fs,
                get_pipeline_config_paths(
                    module_path,
                    self._cfg_dir,
                    self._pipelines_dir,
                ),
                purpose="pipeline config",
            )
            if cfg_path is not None and cfg_path not in seen:
                seen.add(cfg_path)
                files.append(cfg_path)

        return sorted(files)

    def _print_import_success(
        self, names: list[str] | None, src_base_dir: str
    ) -> None:
        """Print success message for import operations."""
        project_label = self._project_label()
        if names:
            console.print(
                f"✅ Imported pipelines [bold blue]{', '.join(names)}[/bold blue] from [green]{src_base_dir}[/green] to [bold blue]{project_label}[/bold blue]"
            )
        else:
            console.print(
                f"✅ Imported all pipelines from [green]{src_base_dir}[/green] to [bold blue]{project_label}[/bold blue]"
            )

    def _print_export_success(
        self, names: list[str] | None, dest_base_dir: str
    ) -> None:
        """Print success message for export operations."""
        project_label = self._project_label()
        if names:
            exported = ", ".join(self._format_export_label(name) for name in names)
            console.print(
                f"✅ Exported pipelines [bold blue]{exported}[/bold blue] to [green]{dest_base_dir}[/green]"
            )
        else:
            console.print(
                f"✅ Exported all pipelines from [bold blue]{project_label}[/bold blue] to [green]{dest_base_dir}[/green]"
            )

    def _sync_filesystem(
        self,
        src_base_dir: str,
        dest_base_dir: str,
        src_fs: AbstractFileSystem | None,
        dest_fs: AbstractFileSystem | None,
        src_storage_options: dict | BaseStorageOptions | None = None,
        dest_storage_options: dict | BaseStorageOptions | None = None,
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
            files (list[str] | None, optional): Specific files to sync. If None, all pipeline files are discovered automatically.
            overwrite (bool, optional): Whether to overwrite existing files. Defaults to False.
        """

        src_fs = self._get_dir_filesystem(
            src_base_dir,
            src_fs,
            src_storage_options or {},
        )
        logger.debug(f"Source filesystem: {src_fs}")
        dest_fs = self._get_dir_filesystem(
            dest_base_dir,
            dest_fs,
            dest_storage_options or {},
        )
        logger.debug(f"Destination filesystem: {dest_fs}")

        if files is None:
            files = self._discover_all_pipeline_files(src_fs)

        for file in files:
            logger.debug(f"Copying {file} from {src_fs} to {dest_fs}")
            parent_dir = posixpath.dirname(file)
            if parent_dir and not dest_fs.exists(parent_dir):
                logger.debug(
                    f"Creating directory {parent_dir} in destination filesystem."
                )
                dest_fs.makedirs(parent_dir, exist_ok=True)
            elif not overwrite and dest_fs.exists(file):
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
        src_storage_options: dict | BaseStorageOptions | None = None,
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
        name = validate_pipeline_name(name)

        resolved_src_fs = self._get_dir_filesystem(
            src_base_dir,
            src_fs,
            src_storage_options or {},
        )
        files = self._get_pipeline_files(name, fs=resolved_src_fs)
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

        self._print_import_success([name], src_base_dir)

    def import_many(
        self,
        names: list[str],
        src_base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        src_storage_options: dict | BaseStorageOptions | None = None,
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

        names = [validate_pipeline_name(name) for name in names]

        resolved_src_fs = self._get_dir_filesystem(
            src_base_dir,
            src_fs,
            src_storage_options or {},
        )
        files = self._get_many_pipeline_files(names, fs=resolved_src_fs)

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
        self._print_import_success(names, src_base_dir)

    def import_all(
        self,
        src_base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        src_storage_options: dict | BaseStorageOptions | None = None,
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
        self._print_import_success(None, src_base_dir)

    def export_pipeline(
        self,
        name: str,
        dest_base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        dest_storage_options: dict | BaseStorageOptions | None = None,
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
        name = validate_pipeline_name(name)

        if not self._pipeline_exists(name):
            raise ValueError(
                f"Pipeline {name} does not exist in the registry. Please check the name."
            )

        files = self._get_pipeline_files(name, fs=self._fs)

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

        self._print_export_success([name], dest_base_dir)

    def export_many(
        self,
        names: list[str],
        dest_base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        dest_storage_options: dict | BaseStorageOptions | None = None,
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
        names = [validate_pipeline_name(name) for name in names]

        # Check if pipelines exist in the registry
        for name in names:
            if not self._pipeline_exists(name):
                raise ValueError(
                    f"Pipeline {name} does not exist in the registry. Please check the name."
                )

        files = self._get_many_pipeline_files(names, fs=self._fs)

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
        self._print_export_success(names, dest_base_dir)

    def export_all(
        self,
        dest_base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        dest_storage_options: dict | BaseStorageOptions | None = None,
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
            f"✅ Exported all pipelines from [bold blue]{self._project_label()}[/bold blue] to [green]{dest_base_dir}[/green]"
        )
