import datetime as dt
import os
import posixpath
import sys
import warnings
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, TypeVar, Union
from uuid import UUID

from loguru import logger
from munch import Munch

try:
    from graphviz import Digraph
except ImportError:
    Digraph = Any  # Type alias for when graphviz isn't installed

from fsspec_utils import AbstractFileSystem, BaseStorageOptions, filesystem

from ..settings import CONFIG_DIR, PIPELINES_DIR, CACHE_DIR
from ..cfg import PipelineConfig, ProjectConfig
from ..cfg.pipeline.run import RunConfig
from ..utils.logging import setup_logging
from ..utils.config import merge_run_config_with_kwargs
from ..utils.filesystem import FilesystemHelper
from .config_manager import PipelineConfigManager
from .executor import PipelineExecutor
from .io import PipelineIOManager
from .lifecycle_manager import PipelineLifecycleManager
from .registry import PipelineRegistry, HookType
from .visualizer import PipelineVisualizer

setup_logging()

GraphType = TypeVar("GraphType")  # Type variable for graphviz.Digraph


class PipelineManager:
    """Central manager for FlowerPower pipeline operations.

    This class provides a unified interface for managing pipelines, including:
    - Configuration management and loading
    - Pipeline creation, deletion, and discovery
    - Pipeline execution via PipelineRunner
    - Visualization via PipelineVisualizer
    - Import/export operations via PipelineIOManager

    Attributes:
        registry (PipelineRegistry): Handles pipeline registration and discovery
        visualizer (PipelineVisualizer): Handles pipeline visualization
        io (PipelineIOManager): Manages pipeline import/export operations
        project_cfg (ProjectConfig): Current project configuration
        pipeline_cfg (PipelineConfig): Current pipeline configuration
        pipelines (list[str]): List of available pipeline names
        current_pipeline_name (str): Name of the currently loaded pipeline
        summary (dict[str, dict | str]): Summary of all pipelines

    Example:
        >>> from flowerpower.pipeline import PipelineManager
        >>>
        >>> # Create manager with default settings
        >>> manager = PipelineManager()
        >>>
        >>> # Create manager with custom settings
        >>> manager = PipelineManager(
        ...     base_dir="/path/to/project",
        ...     log_level="DEBUG"
        ... )
    """

    def __init__(
        self,
        base_dir: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        cfg_dir: str | None = CONFIG_DIR,
        pipelines_dir: str | None = PIPELINES_DIR,
        
        log_level: str | None = None,
    ) -> None:
        """Initialize the PipelineManager.

        Args:
            base_dir: Root directory for the FlowerPower project. Defaults to current
                working directory if not specified.
            storage_options: Configuration options for filesystem access. Can be:
                - dict: Raw key-value options
                - Munch: Dot-accessible options object
                - BaseStorageOptions: Structured options class
                Used for S3, GCS, etc. Example: {"key": "abc", "secret": "xyz"}
            fs: Pre-configured fsspec filesystem instance. If provided, used instead
                of creating new filesystem from base_dir and storage_options.
            cfg_dir: Override default configuration directory name ('conf').
                Example: "config" or "settings".
            pipelines_dir: Override default pipelines directory name ('pipelines').
                Example: "flows" or "dags".
            
            log_level: Set logging level for the manager.
                Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

        Raises:
            ValueError: If provided configuration paths don't exist or can't be created
            RuntimeError: If filesystem operations fail during initialization
            ImportError: If required dependencies for specified worker type not installed

        Example:
            >>> # Basic initialization
            >>> manager = PipelineManager()
            >>>
            >>> # Custom configuration with S3 storage
            >>> manager = PipelineManager(
            ...     base_dir="s3://my-bucket/project",
            ...     storage_options={
            ...         "key": "ACCESS_KEY",
            ...         "secret": "SECRET_KEY"
            ...     },
            
            ...     log_level="DEBUG"
            ... )
        """
        if log_level:
            setup_logging(level=log_level)

        self._setup_filesystem(base_dir, storage_options, fs, cfg_dir, pipelines_dir)
        self._initialize_managers()
        self._ensure_directories_exist()
        self._add_modules_path()

    def _setup_filesystem(
        self,
        base_dir: str | None,
        storage_options: dict | Munch | BaseStorageOptions | None,
        fs: AbstractFileSystem | None,
        cfg_dir: str | None,
        pipelines_dir: str | None
    ) -> None:
        """Setup filesystem and configuration directories.

        Args:
            base_dir: Root directory for the project
            storage_options: Storage options for filesystem
            fs: Pre-configured filesystem instance
            cfg_dir: Configuration directory name
            pipelines_dir: Pipelines directory name
        """
        self._base_dir = base_dir or str(Path.cwd())
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir

        # Setup filesystem helper
        self._fs_helper = FilesystemHelper(self._base_dir, storage_options)

        # Configure caching if storage options provided
        if storage_options is not None:
            cached = True
            cache_storage = posixpath.join(
                posixpath.expanduser(CACHE_DIR),
                self._base_dir.split("://")[-1],
            )
            os.makedirs(cache_storage, exist_ok=True)
        else:
            cached = False
            cache_storage = None

        # Get filesystem instance
        self._fs = fs or self._fs_helper.get_filesystem(cached=cached, cache_storage=cache_storage)
        self._storage_options = (
            storage_options or self._fs.storage_options
            if self._fs.protocol != "dir"
            else self._fs.fs.storage_options
        )

    def _initialize_managers(self) -> None:
        """Initialize all manager components."""
        # Initialize config manager
        self._config_manager = PipelineConfigManager(
            base_dir=self._base_dir,
            fs=self._fs,
            storage_options=self._storage_options,
            cfg_dir=self._cfg_dir
        )

        # Load project configuration
        self._config_manager.load_project_config(reload=True)

        # Initialize registry
        self.registry = PipelineRegistry(
            project_cfg=self._config_manager.project_config,
            fs=self._fs,
            base_dir=self._base_dir,
            storage_options=self._storage_options,
        )

        # Initialize specialized managers
        self._executor = PipelineExecutor(
            config_manager=self._config_manager,
            registry=self.registry
        )
        self._lifecycle_manager = PipelineLifecycleManager(registry=self.registry)

        # Initialize other components
        self._project_context = None
        self.visualizer = PipelineVisualizer(
            project_cfg=self._config_manager.project_config,
            fs=self._fs
        )
        self.io = PipelineIOManager(registry=self.registry)

    def _ensure_directories_exist(self) -> None:
        """Ensure essential directories exist."""
        self._fs_helper.ensure_directories_exist(
            self._fs,
            self._cfg_dir,
            self._pipelines_dir
        )

    def _add_modules_path(self) -> None:
        """Add pipeline module paths to Python path.

        This internal method ensures that pipeline modules can be imported by:
        1. Syncing filesystem cache if needed
        2. Adding project root to Python path
        3. Adding pipelines directory to Python path
        """
        if self._fs.is_cache_fs:
            self._fs.sync_cache()
            project_path = self._fs._mapper.directory
            modules_path = posixpath.join(project_path, self._pipelines_dir)
        else:
            # Use the base directory directly if not using cache
            project_path = self._fs.path
            modules_path = posixpath.join(project_path, self._pipelines_dir)

        if project_path not in sys.path:
            sys.path.insert(0, project_path)

        if modules_path not in sys.path:
            sys.path.insert(0, modules_path)

    def __enter__(self) -> "PipelineManager":
        """Enter the context manager.

        Enables use of the manager in a with statement for automatic resource cleanup.

        Returns:
            PipelineManager: Self for use in context manager.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> with PipelineManager() as manager:
            ...     result = manager.run("my_pipeline")
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager.

        Handles cleanup of resources when exiting a with statement.

        Args:
            exc_type: Type of exception that occurred, if any
            exc_val: Exception instance that occurred, if any
            exc_tb: Traceback of exception that occurred, if any

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> with PipelineManager() as manager:
            ...     try:
            ...         result = manager.run("my_pipeline")
            ...     except Exception as e:
            ...         print(f"Error: {e}")
            ...     # Resources automatically cleaned up here
        """
        # Add cleanup code if needed
        pass


    def load_pipeline(self, name: str, reload: bool = False) -> PipelineConfig:
        """Load or reload configuration for a specific pipeline.

        Args:
            name: Name of the pipeline whose configuration to load
            reload: Force reload configuration even if already loaded.
                When False, returns cached config if available.

        Returns:
            PipelineConfig: The loaded pipeline configuration object
        """
        return self._config_manager.load_pipeline_config(name, reload)

    @property
    def current_pipeline_name(self) -> str:
        """Get the name of the currently loaded pipeline.

        Returns:
            str: Name of the currently loaded pipeline, or None if none loaded.
        """
        return self._config_manager.current_pipeline_name

    @property
    def project_cfg(self) -> ProjectConfig:
        """Get the project configuration.

        Loads configuration if not already loaded.

        Returns:
            ProjectConfig: Project-wide configuration object.

        Raises:
            RuntimeError: If configuration loading fails.

        Example:
            >>> manager = PipelineManager()
            >>> cfg = manager.project_cfg
            >>> print(cfg.name)
            'my_project'
        """
        return self._config_manager.project_config

    @property
    def pipeline_cfg(self) -> PipelineConfig:
        """Get the configuration for the currently loaded pipeline.

        Returns:
            PipelineConfig: Pipeline-specific configuration object.

        Warns:
            UserWarning: If no pipeline is currently loaded.

        Example:
            >>> manager = PipelineManager()
            >>> manager._load_pipeline_cfg("example_pipeline")
            >>> cfg = manager.pipeline_cfg
            >>> print(cfg.run.executor)
            'local'
        """
        return self._config_manager.pipeline_config

    # --- Core Execution Method ---


    def run(
        self,
        name: str,
        run_config: RunConfig | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """Execute a pipeline synchronously and return its results.

        This is the main method for running pipelines directly. It handles configuration
        loading, adapter setup, and execution via PipelineRunner.

        Args:
            name (str): Name of the pipeline to run. Must be a valid identifier.
            run_config (RunConfig | None): Run configuration object containing all execution parameters.
                If None, the default configuration from the pipeline will be used.
            **kwargs: Additional parameters to override the run_config. Supported parameters include:
                inputs (dict | None): Override pipeline input values. Example: {"data_date": "2025-04-28"}
                final_vars (list[str] | None): Specify which output variables to return.
                    Example: ["model", "metrics"]
                config (dict | None): Configuration for Hamilton pipeline executor.
                    Example: {"model": "LogisticRegression"}
                cache (dict | None): Cache configuration for results. Example: {"recompute": ["node1", "final_node"]}
                executor_cfg (str | dict | ExecutorConfig | None): Execution configuration, can be:
                    - str: Executor name, e.g. "threadpool", "local"
                    - dict: Raw config, e.g. {"type": "threadpool", "max_workers": 4}
                    - ExecutorConfig: Structured config object
                with_adapter_cfg (dict | WithAdapterConfig | None): Adapter settings for pipeline execution.
                    Example: {"opentelemetry": True, "tracker": False}
                pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline-specific adapter settings.
                    Example: {"tracker": {"project_id": "123", "tags": {"env": "prod"}}}
                project_adapter_cfg (dict | ProjectAdapterConfig | None): Project-level adapter settings.
                    Example: {"opentelemetry": {"host": "http://localhost:4317"}}
                adapter (dict[str, Any] | None): Custom adapter instance for pipeline
                    Example: {"ray_graph_adapter": RayGraphAdapter()}
                reload (bool): Force reload of pipeline configuration.
                log_level (str | None): Logging level for the execution. Default None uses project config.
                    Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
                max_retries (int): Maximum number of retries for execution.
                retry_delay (float): Delay between retries in seconds.
                jitter_factor (float): Random jitter factor to add to retry delay
                retry_exceptions (tuple): Exceptions that trigger a retry.
                on_success (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on successful pipeline execution.
                on_failure (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on pipeline execution failure.

        Returns:
            dict[str, Any]: Pipeline execution results, mapping output variable names
                to their computed values.

        Raises:
            ValueError: If pipeline name doesn't exist or configuration is invalid
            ImportError: If pipeline module cannot be imported
            RuntimeError: If execution fails due to pipeline or adapter errors

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Basic pipeline run
            >>> results = manager.run("data_pipeline")
            >>>
            >>> # Run with custom RunConfig
            >>> from flowerpower.cfg.pipeline.run import RunConfig
            >>> config = RunConfig(inputs={"date": "2025-04-28"}, final_vars=["result"])
            >>> results = manager.run("ml_pipeline", run_config=config)
            >>>
            >>> # Complex run with kwargs overrides
            >>> results = manager.run(
            ...     "ml_pipeline",
            ...     inputs={"training_date": "2025-04-28"},
            ...     final_vars=["model", "metrics"],
            ...     executor_cfg={"type": "threadpool", "max_workers": 4},
            ...     with_adapter_cfg={"tracker": True},
            ...     reload=True
            ... )
        """
        # Set project context for executor
        if hasattr(self, "_project_context") and self._project_context is not None:
            self._executor._project_context = self._project_context
        
        # Delegate to executor
        return self._executor.run(name=name, run_config=run_config, **kwargs)

    # --- Delegated Methods ---

    # Registry Delegations
    def new(self, name: str, overwrite: bool = False) -> None:
        """Create a new pipeline with the given name.

        Creates necessary configuration files and pipeline module template.

        Args:
            name: Name for the new pipeline. Must be a valid Python identifier.
            overwrite: Whether to overwrite existing pipeline with same name.
                Default False for safety.

        Raises:
            ValueError: If name is invalid or pipeline exists and overwrite=False
            RuntimeError: If file creation fails
            PermissionError: If lacking write permissions

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> # Create new pipeline
            >>> manager = PipelineManager()
            >>> manager.new("data_transformation")
            >>>
            >>> # Overwrite existing pipeline
            >>> manager.new("data_transformation", overwrite=True)
        """
        self._lifecycle_manager.create_pipeline(name=name, overwrite=overwrite)

    def delete(self, name: str, cfg: bool = True, module: bool = False) -> None:
        """
        Delete a pipeline and its associated files.

        Args:
            name: Name of the pipeline to delete
            cfg: Whether to delete configuration files. Default True.
            module: Whether to delete Python module file. Default False
                for safety since it may contain custom code.

        Raises:
            FileNotFoundError: If specified pipeline files don't exist
            PermissionError: If lacking delete permissions
            RuntimeError: If deletion fails partially, leaving inconsistent state

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> # Delete pipeline config only
            >>> manager = PipelineManager()
            >>> manager.delete("old_pipeline")
            >>>
            >>> # Delete both config and module
            >>> manager.delete("test_pipeline", module=True)
        """
        self._lifecycle_manager.delete_pipeline(name=name, cfg=cfg, module=module)

    def get_summary(
        self,
        name: str | None = None,
        cfg: bool = True,
        code: bool = True,
        project: bool = True,
    ) -> dict[str, dict | str]:
        """Get a detailed summary of pipeline(s) configuration and code.

        Args:
            name: Specific pipeline to summarize. If None, summarizes all.
            cfg: Include pipeline configuration details. Default True.
            code: Include pipeline module code. Default True.
            project: Include project configuration. Default True.

        Returns:
            dict[str, dict | str]: Nested dictionary containing requested
                summaries. Structure varies based on input parameters:
                - With name: {"config": dict, "code": str, "project": dict}
                - Without name: {pipeline_name: {"config": dict, ...}, ...}

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Get summary of specific pipeline
            >>> summary = manager.get_summary("data_pipeline")
            >>> print(summary["config"]["schedule"]["enabled"])
            True
            >>>
            >>> # Get summary of all pipelines' code
            >>> all_code = manager.get_summary(
            ...     cfg=False,
            ...     code=True,
            ...     project=False
            ... )
        """
        return self.registry.get_summary(name=name, cfg=cfg, code=code, project=project)

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
            >>> pm = PipelineManager()
            >>> pm.show_summary()
        """
        return self._lifecycle_manager.show_summary(
            name=name,
            cfg=cfg,
            code=code,
            project=project,
            to_html=to_html,
            to_svg=to_svg,
        )

    def list_pipelines(self) -> list[str]:
        """Get list of all available pipeline names.

        Returns:
            list[str]: Names of all registered pipelines, sorted alphabetically.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> pipelines = manager.list_pipelines()
            >>> print(pipelines)
            ['data_ingestion', 'model_training', 'reporting']
        """
        return self._lifecycle_manager.list_pipelines()

    def show_pipelines(self) -> None:
        """Display all available pipelines in a formatted table.

        Uses rich formatting for terminal display.
        """
        return self.registry.show_pipelines()

    @property
    def pipelines(self) -> list[str]:
        """Get list of all available pipeline names.

        Similar to list_pipelines() but as a property.

        Returns:
            list[str]: Names of all registered pipelines, sorted alphabetically.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> print(manager.pipelines)
            ['data_ingestion', 'model_training', 'reporting']
        """
        return self._lifecycle_manager.pipelines

    @property
    def summary(self) -> dict[str, dict | str]:
        """Get complete summary of all pipelines.

        Returns:
            dict[str, dict | str]: Full summary including configuration,
            code, and project settings for all pipelines.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> summary = manager.summary
            >>> for name, details in summary.items():
            ...     print(f"{name}: {details['config']['type']}")
            data_pipeline: batch
            ml_pipeline: streaming
        """
        return self._lifecycle_manager.summary

    def add_hook(
        self,
        name: str,
        type: HookType,
        to: str | None,
        function_name: str | None,
    ) -> None:
        """Add a hook to the pipeline module.

        Args:
            name (str): The name of the pipeline
            type (HookType): The type of the hook.
            to (str | None, optional): The name of the file to add the hook to. Defaults to the hook.py file in the pipelines hooks folder.
            function_name (str | None, optional): The name of the function. If not provided uses default name of hook type.

        Returns:
            None

        Raises:
            ValueError: If the hook type is not valid

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> manager.add_hook(
            ...     name="data_pipeline",
            ...     type=HookType.PRE_EXECUTE,
            ...     to="pre_execute_hook",
            ...     function_name="my_pre_execute_function"
            ... )
        """
        self._lifecycle_manager.add_hook(
            name=name,
            type=type,
            to=to,
            function_name=function_name,
        )

    # IO Delegations
    def import_pipeline(
        self,
        name: str,
        src_base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        src_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ) -> None:
        """Import a pipeline from another FlowerPower project.

        Copies both pipeline configuration and code files from the source location
        to the current project.

        Args:
            name (str): Name for the new pipeline in the current project
            src_base_dir (str): Source FlowerPower project directory or URI
                Examples:
                    - Local: "/path/to/other/project"
                    - S3: "s3://bucket/project"
                    - GitHub: "github://org/repo/project"
            src_fs (AbstractFileSystem | None): Pre-configured source filesystem
                Example: S3FileSystem(key='ACCESS_KEY', secret='SECRET_KEY')
            src_storage_options (dict | BaseStorageOptions | None): Options for source filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite: Whether to replace existing pipeline if name exists

        Raises:
            ValueError: If pipeline name exists and overwrite=False
            FileNotFoundError: If source pipeline not found
            RuntimeError: If import fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>> from s3fs import S3FileSystem
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Import from local filesystem
            >>> manager.import_pipeline(
            ...     "new_pipeline",
            ...     "/path/to/other/project"
            ... )
            >>>
            >>> # Import from S3 with custom filesystem
            >>> s3 = S3FileSystem(anon=False)
            >>> manager.import_pipeline(
            ...     "s3_pipeline",
            ...     "s3://bucket/project",
            ...     src_fs=s3
            ... )
        """
        return self.io.import_pipeline(
            name=name,
            src_base_dir=src_base_dir,
            src_fs=src_fs,
            src_storage_options=src_storage_options,
            overwrite=overwrite,
        )

    def import_many(
        self,
        names: list[str],
        src_base_dir: str,  # Base dir for source if pipelines is a list
        src_fs: AbstractFileSystem | None = None,
        src_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ) -> None:
        """Import multiple pipelines from another project or location.


        Args:
            pipelines(list[str]): List of pipeline names to import
            src_base_dir (str, optional): Source project directory or URI
                Examples:
                    - Local: "/path/to/other/project"
                    - S3: "s3://bucket/project"
                    - GitHub: "github://org/repo/project"
            src_fs (AbstractFileSystem | None, optional): Pre-configured source filesystem
                Example: S3FileSystem(key='ACCESS_KEY', secret="SECRET_KEY")
            storage_options (dict | BaseStorageOptions | None, optional): Options for source filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite (bool, optional): Whether to replace existing pipelines

        Raises:
            ValueError: If any pipeline exists and overwrite=False
            FileNotFoundError: If source pipelines not found
            RuntimeError: If import operation fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Import keeping original names
            >>> manager.import_many(
            ...     names=["pipeline1", "pipeline2"],
            ...     src_base_dir="s3://bucket/source",
            ...     src_storage_options={
            ...         "key": "ACCESS_KEY",
            ...         "secret": "SECRET_KEY"
            ...     }
            ... )
        """
        return self.io.import_many(
            names=names,
            src_base_dir=src_base_dir,
            src_fs=src_fs,
            src_storage_options=src_storage_options,
            overwrite=overwrite,
        )

    def import_all(
        self,
        src_base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        src_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ) -> None:
        """Import all pipelines from another FlowerPower project.

        Args:
            src_base_dir (str): Source project directory or URI
                Examples:
                    - Local: "/path/to/other/project"
                    - S3: "s3://bucket/project"
                    - GitHub: "github://org/repo/project"
            src_fs (AbstractFileSystem | None): Pre-configured source filesystem
                Example: S3FileSystem(key='KEY',secret='SECRET')
            src_storage_options (dict | BaseStorageOptions | None): Options for source filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite (bool): Whether to replace existing pipelines

        Raises:
            FileNotFoundError: If source location not found
            RuntimeError: If import fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Import all from backup
            >>> manager.import_all("/path/to/backup")
            >>>
            >>> # Import all from S3 with credentials
            >>> manager.import_all(
            ...     "s3://bucket/backup",
            ...     src_storage_options={
            ...         "key": "ACCESS_KEY",
            ...         "secret": "SECRET_KEY"
            ...     }
            ... )
        """
        return self.io.import_all(
            src_base_dir=src_base_dir,
            src_fs=src_fs,
            src_storage_options=src_storage_options,
            overwrite=overwrite,
        )

    def export_pipeline(
        self,
        name: str,
        dest_base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        dest_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ) -> None:
        """Export a pipeline to another location or project.

        Copies pipeline configuration and code files to the destination location
        while preserving directory structure.

        Args:
            name (str): Name of the pipeline to export
            dest_base_dir (str): Destination directory or URI
                Examples:
                    - Local: "/path/to/exports"
                    - S3: "s3://bucket/exports"
                    - Azure: "abfs://container/exports"
            dest_fs (AbstractFileSystem | None): Pre-configured destination filesystem
                Example: S3FileSystem(key='ACCESS_KEY', secret='SECRET_KEY')
            dest_storage_options (dict | BaseStorageOptions | None): Options for destination filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite (bool): Whether to replace existing files at destination

        Raises:
            ValueError: If pipeline doesn't exist
            FileNotFoundError: If destination not accessible
            RuntimeError: If export fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>> from gcsfs import GCSFileSystem
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Export to local backup
            >>> manager.export_pipeline(
            ...     "my_pipeline",
            ...     "/path/to/backup"
            ... )
            >>>
            >>> # Export to Google Cloud Storage
            >>> gcs = GCSFileSystem(project='my-project')
            >>> manager.export_pipeline(
            ...     "prod_pipeline",
            ...     "gs://my-bucket/backups",
            ...     dest_fs=gcs
            ... )
        """
        return self.io.export_pipeline(
            name=name,
            dest_base_dir=dest_base_dir,
            dest_fs=dest_fs,
            dest_storage_options=dest_storage_options,
            overwrite=overwrite,
        )

    def export_many(
        self,
        names: list[str],
        dest_base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        dest_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ) -> None:
        """Export multiple pipelines to another location.

        Efficiently exports multiple pipelines in a single operation,
        preserving directory structure and metadata.

        Args:
            names (list[str]): List of pipeline names to export
            dest_base_dir (str): Destination directory or URI
                Examples:
                    - Local: "/path/to/exports"
                    - S3: "s3://bucket/exports"
                    - Azure: "abfs://container/exports"
            dest_fs (AbstractFileSystem | None): Pre-configured destination filesystem
                Example: S3FileSystem(key='ACCESS_KEY', secret='SECRET_KEY')
            dest_storage_options (dict | BaseStorageOptions | None): Options for destination filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite (bool): Whether to replace existing files at destination

        Raises:
            ValueError: If any pipeline doesn't exist
            FileNotFoundError: If destination not accessible
            RuntimeError: If export operation fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>> from azure.storage.filedatalake import DataLakeServiceClient
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Export multiple pipelines to Azure Data Lake
            >>> manager.export_many(
            ...     pipelines=["ingest", "process", "report"],
            ...     base_dir="abfs://data/backups",
            ...     dest_storage_options={
            ...         "account_name": "myaccount",
            ...         "sas_token": "...",
            ...     }
            ... )
        """
        return self.io.export_many(
            names=names,
            dest_base_dir=dest_base_dir,
            dest_fs=dest_fs,
            dest_storage_options=dest_storage_options,
            overwrite=overwrite,
        )

    def export_all(
        self,
        dest_base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        dest_storage_options: dict | BaseStorageOptions | None = {},
        overwrite: bool = False,
    ) -> None:
        """Export all pipelines to another location.

        Args:
            dest_base_dir (str): Destination directory or URI
                Examples:
                    - Local: "/path/to/exports"
                    - S3: "s3://bucket/exports"
                    - Azure: "abfs://container/exports"
            dest_fs (AbstractFileSystem | None): Pre-configured destination filesystem
                Example: S3FileSystem(key='ACCESS_KEY', secret='SECRET_KEY')
            dest_storage_options (dict | BaseStorageOptions | None): Options for destination filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite (bool): Whether to replace existing files at destination

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Export all to backup directory
            >>> manager.export_all("/path/to/backup")
            >>>
            >>> # Export all to cloud storage
            >>> manager.export_all(
            ...     "gs://bucket/pipelines",
            ...     dest_storage_options={
            ...         "token": "SERVICE_ACCOUNT_TOKEN",
            ...         "project": "my-project"
            ...     }
            ... )
        """
        return self.io.export_all(
            dest_base_dir=dest_base_dir,
            dest_fs=dest_fs,
            dest_storage_options=dest_storage_options,
            overwrite=overwrite,
        )

    # Visualizer Delegations
    def save_dag(self, name: str, format: str = "png", reload: bool = False) -> None:
        """Save pipeline DAG visualization to a file.

        Creates a visual representation of the pipeline's directed acyclic graph (DAG)
        showing function dependencies and data flow.

        Args:
            name: Name of the pipeline to visualize
            format: Output file format. Supported formats:
                - "png": Standard bitmap image
                - "svg": Scalable vector graphic
                - "pdf": Portable document format
                - "dot": Graphviz DOT format
            reload: Whether to reload pipeline before visualization

        Raises:
            ValueError: If pipeline name doesn't exist
            ImportError: If required visualization dependencies missing
            RuntimeError: If graph generation fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Save as PNG
            >>> manager.save_dag("data_pipeline")
            >>>
            >>> # Save as SVG with reload
            >>> manager.save_dag(
            ...     name="ml_pipeline",
            ...     format="svg",
            ...     reload=True
            ... )
        """
        self.visualizer.save_dag(name=name, format=format, reload=reload)

    def show_dag(
        self, name: str, format: str = "png", reload: bool = False, raw: bool = False
    ) -> Union[GraphType, None]:
        """Display pipeline DAG visualization interactively.

        Similar to save_dag() but displays the graph immediately in notebook
        environments or returns the raw graph object for custom rendering.

        Args:
            name: Name of the pipeline to visualize
            format: Output format (see save_dag() for options)
            reload: Whether to reload pipeline before visualization
            raw: If True, return the raw graph object instead of displaying

        Returns:
            Union[GraphType, None]: Raw graph object if raw=True, else None after
                displaying the visualization

        Raises:
            ValueError: If pipeline name doesn't exist
            ImportError: If visualization dependencies missing
            RuntimeError: If graph generation fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Display in notebook
            >>> manager.show_dag("data_pipeline")
            >>>
            >>> # Get raw graph for custom rendering
            >>> graph = manager.show_dag(
            ...     name="ml_pipeline",
            ...     format="svg",
            ...     raw=True
            ... )
            >>> # Custom rendering
            >>> graph.render("custom_vis", view=True)
        """
        return self.visualizer.show_dag(
            name=name, format=format, reload=reload, raw=raw
        )
