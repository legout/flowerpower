"""Pipeline Creator for pipeline CRUD operations."""

import datetime as dt
import posixpath

import rich
from fsspeckit import AbstractFileSystem
from loguru import logger

from ..cfg import PipelineConfig, ProjectConfig
from ..settings import CONFIG_DIR, PIPELINES_DIR
from ..utils.filesystem import format_pipeline_file_path, get_pipeline_config_paths
from ..utils.security import validate_directory_fragment, validate_pipeline_name
from ..utils.templates import PIPELINE_PY_TEMPLATE


class PipelineCreator:
    """Handles creation and deletion of pipelines.

    This class separates pipeline CRUD concerns from the
    :class:`PipelineRegistry`, which focuses on discovery, caching,
    and module loading.
    """

    def __init__(
        self,
        project_cfg: ProjectConfig,
        fs: AbstractFileSystem,
        cfg_dir: str | None = CONFIG_DIR,
        pipelines_dir: str | None = PIPELINES_DIR,
    ):
        """
        Initializes the PipelineCreator.

        Args:
            project_cfg: The project configuration object.
            fs: The filesystem instance.
            cfg_dir: Configuration directory name. Defaults to CONFIG_DIR.
            pipelines_dir: Pipelines directory name. Defaults to PIPELINES_DIR.
        """
        self.project_cfg = project_cfg
        self._fs = fs
        self._cfg_dir = validate_directory_fragment(
            cfg_dir if cfg_dir is not None else CONFIG_DIR
        )
        self._pipelines_dir = validate_directory_fragment(
            pipelines_dir if pipelines_dir is not None else PIPELINES_DIR
        )

    @classmethod
    def from_context(
        cls,
        context,
        *,
        project_cfg: ProjectConfig,
    ) -> "PipelineCreator":
        """Create a pipeline creator from project runtime context facts."""
        return cls(
            project_cfg=project_cfg,
            fs=context.fs,
            cfg_dir=context.cfg_dir,
            pipelines_dir=context.pipelines_dir,
        )

    def _path_exists(self, path: str, *, purpose: str) -> bool:
        try:
            return self._fs.exists(path)
        except Exception as error:
            logger.debug(f"Skipping unreadable {purpose} candidate {path}: {error}")
            return False

    def new(self, name: str, overwrite: bool = False):
        """
        Adds a pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool): Whether to overwrite an existing pipeline. Defaults to False.

        Raises:
            ValueError: If the configuration or pipeline path does not exist, or if the pipeline already exists.
        """
        name = validate_pipeline_name(name)

        for dir_path, label in (
            (self._cfg_dir, "configuration"),
            (self._pipelines_dir, "pipeline"),
        ):
            required_path = dir_path or "."
            if not self._fs.exists(required_path):
                raise ValueError(
                    f"{label.capitalize()} path {required_path} does not exist. Please run flowerpower init first."
                )

        formatted_name = format_pipeline_file_path(name)
        pipeline_file = posixpath.join(self._pipelines_dir, f"{formatted_name}.py")
        config_candidates = get_pipeline_config_paths(
            formatted_name,
            self._cfg_dir,
            self._pipelines_dir,
        )
        cfg_file = config_candidates[0]
        project_label = self.project_cfg.name or "project"

        def check_and_handle(path: str, *, purpose: str) -> None:
            if self._path_exists(path, purpose=purpose):
                if overwrite:
                    self._fs.rm(path)
                    return
                raise ValueError(
                    f"Pipeline {project_label}.{name} already exists. Use `overwrite=True` to overwrite."
                )

        check_and_handle(pipeline_file, purpose="pipeline module")
        for path in config_candidates:
            check_and_handle(path, purpose="pipeline config")

        # Ensure directories for the new files exist
        for file_path in (pipeline_file, cfg_file):
            parent_dir = posixpath.dirname(file_path)
            if parent_dir:
                self._fs.makedirs(parent_dir, exist_ok=True)

        # Write pipeline code template
        with self._fs.open(pipeline_file, "w") as f:
            f.write(
                PIPELINE_PY_TEMPLATE.format(
                    name=name,
                    date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    cfg_dir=self._cfg_dir,
                    pipelines_dir=self._pipelines_dir,
                )
            )

        # Create default pipeline config and save it directly using configured directories
        new_pipeline_cfg = PipelineConfig(name=name)
        new_pipeline_cfg.save(
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )

        rich.print(
            f"🔧 Created new pipeline [bold blue]{(self.project_cfg.name or 'project')}.{name}[/bold blue]"
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
        """
        name = validate_pipeline_name(name)

        deleted_files = []
        formatted_name = format_pipeline_file_path(name)

        if cfg:
            config_candidates = get_pipeline_config_paths(
                formatted_name,
                self._cfg_dir,
                self._pipelines_dir,
            )
            found_config = False
            for pipeline_cfg_path in config_candidates:
                if not self._path_exists(
                    pipeline_cfg_path,
                    purpose="pipeline config",
                ):
                    continue
                self._fs.rm(pipeline_cfg_path)
                deleted_files.append(pipeline_cfg_path)
                logger.debug(f"Deleted pipeline config: {pipeline_cfg_path}")
                found_config = True

            if not found_config:
                logger.warning(
                    f"Config file not found, skipping deletion: {config_candidates[0]}"
                )

        if module:
            pipeline_py_path = posixpath.join(self._pipelines_dir, f"{formatted_name}.py")
            if self._path_exists(pipeline_py_path, purpose="pipeline module"):
                self._fs.rm(pipeline_py_path)
                deleted_files.append(pipeline_py_path)
                logger.debug(f"Deleted pipeline module: {pipeline_py_path}")
            else:
                logger.warning(
                    f"Module file not found, skipping deletion: {pipeline_py_path}"
                )

        if not deleted_files:
            logger.warning(
                f"No files found or specified for deletion for pipeline '{name}'."
            )

        # Sync filesystem if needed (using _fs)
        if hasattr(self._fs, "sync_cache") and callable(self._fs.sync_cache):
            self._fs.sync_cache()

    def create_pipeline(
        self,
        name: str,
        overwrite: bool = False,
    ) -> None:
        """Create a new pipeline.

        This method provides compatibility with the lifecycle manager interface.

        Args:
            name: Name of the pipeline to create
            overwrite: Whether to overwrite existing pipeline
        """
        self.new(name=name, overwrite=overwrite)

    def delete_pipeline(
        self, name: str, cfg: bool = True, module: bool = False
    ) -> None:
        """Delete a pipeline.

        This method provides compatibility with the lifecycle manager interface.

        Args:
            name: Name of the pipeline to delete
            cfg: Whether to delete configuration files
            module: Whether to delete module files
        """
        self.delete(name=name, cfg=cfg, module=module)
