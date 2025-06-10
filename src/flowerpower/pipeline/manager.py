import datetime as dt
import os
import posixpath
import sys
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, TypeVar, Union
from uuid import UUID

import duration_parser
from loguru import logger
from munch import Munch

try:
    from graphviz import Digraph
except ImportError:
    Digraph = Any  # Type alias for when graphviz isn't installed

from .. import settings
from ..cfg import PipelineConfig, ProjectConfig
from ..cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from ..cfg.pipeline.run import ExecutorConfig, WithAdapterConfig
from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from ..fs import AbstractFileSystem, BaseStorageOptions, get_filesystem
from ..utils.callback import run_with_callback
from ..utils.logging import setup_logging
from .io import PipelineIOManager
from .job_queue import PipelineJobQueue
from .registry import HookType, PipelineRegistry
from .runner import run_pipeline
from .visualizer import PipelineVisualizer

setup_logging(level=settings.LOG_LEVEL)

GraphType = TypeVar("GraphType")  # Type variable for graphviz.Digraph


class PipelineManager:
    """Central manager for FlowerPower pipeline operations.

    This class provides a unified interface for managing pipelines, including:
    - Configuration management and loading
    - Pipeline creation, deletion, and discovery
    - Pipeline execution via PipelineRunner
    - Job scheduling via PipelineScheduler
    - Visualization via PipelineVisualizer
    - Import/export operations via PipelineIOManager

    Attributes:
        registry (PipelineRegistry): Handles pipeline registration and discovery
        scheduler (PipelineScheduler): Manages job scheduling and execution
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
        ...     job_queue_type="rq",
        ...     log_level="DEBUG"
        ... )
    """

    def __init__(
        self,
        base_dir: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        cfg_dir: str | None = settings.CONFIG_DIR,
        pipelines_dir: str | None = settings.PIPELINES_DIR,
        job_queue_type: str | None = None,
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
            job_queue_type: Override worker type from project config/settings.
                Valid values: "rq", "apscheduler", or "huey".
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
            ...     job_queue_type="rq",
            ...     log_level="DEBUG"
            ... )
        """
        if log_level:
            setup_logging(level=log_level)

        self._base_dir = base_dir or str(Path.cwd())
        # self._storage_options = storage_options
        if storage_options is not None:
            cached = True
            cache_storage = posixpath.join(
                posixpath.expanduser(settings.CACHE_DIR),
                self._base_dir.split("://")[-1],
            )
            os.makedirs(cache_storage, exist_ok=True)
        else:
            cached = False
            cache_storage = None
        if not fs:
            fs = get_filesystem(
                self._base_dir,
                storage_options=storage_options,
                cached=cached,
                cache_storage=cache_storage,
            )
        self._fs = fs
        self._storage_options = (
            storage_options or fs.storage_options
            if fs.protocol != "dir"
            else fs.fs.storage_options
        )

        # Store overrides for ProjectConfig loading
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir

        self._load_project_cfg(
            reload=True, job_queue_type=job_queue_type
        )  # Load project config
        self._job_queue_type = job_queue_type or self.project_cfg.job_queue.type

        # Ensure essential directories exist (using paths from loaded project_cfg)
        try:
            self._fs.makedirs(self._cfg_dir, exist_ok=True)
            self._fs.makedirs(self._pipelines_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating essential directories: {e}")
            # Consider raising an error here depending on desired behavior

        # Ensure pipeline modules can be imported
        self._add_modules_path()

        # Instantiate components using the loaded project config
        self.registry = PipelineRegistry(
            project_cfg=self.project_cfg,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )
        pipeline_job_queue = PipelineJobQueue(
            project_cfg=self.project_cfg,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )
        if pipeline_job_queue.job_queue is None:
            logger.warning(
                "Job queue backend is unavailable. Some features may not work."
            )
            self.jqm = None
        else:
            self.jqm = pipeline_job_queue
        self.visualizer = PipelineVisualizer(project_cfg=self.project_cfg, fs=self._fs)
        self.io = PipelineIOManager(registry=self.registry)

        self._current_pipeline_name: str | None = None
        self._pipeline_cfg: PipelineConfig | None = None

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

    def _get_run_func(
        self,
        name: str,
        reload: bool = False,
        on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
    ) -> Callable:
        """Create a PipelineRunner instance and return its run method.

        This internal helper method ensures that each job gets a fresh runner
        with the correct configuration state.

        Args:
            name: Name of the pipeline to create runner for
            reload: Whether to reload pipeline configuration

        Returns:
            Callable: Bound run method from a fresh PipelineRunner instance

        Example:
            >>> # Internal usage
            >>> manager = PipelineManager()
            >>> run_func = manager._get_run_func_for_job("data_pipeline")
            >>> result = run_func(inputs={"date": "2025-04-28"})
        """
        if (
            name == self._current_pipeline_name and not reload
            # and hasattr(self, "_runner")
        ):
            # run_pipeline_ = partial(run_pipeline, project_cfg=self.project_cfg, pipeline_cfg=self._pipeline_cfg)
            run_func = run_with_callback(on_success=on_success, on_failure=on_failure)(
                run_pipeline
            )
            return run_func

        _ = self.load_pipeline(name=name, reload=reload)
        # run_pipeline_ = partial(run_pipeline, project_cfg=self.project_cfg, pipeline_cfg=pipeline_cfg)

        run_func = run_with_callback(on_success=on_success, on_failure=on_failure)(
            run_pipeline
        )
        return run_func

    def _add_modules_path(self) -> None:
        """Add pipeline module paths to Python path.

        This internal method ensures that pipeline modules can be imported by:
        1. Syncing filesystem cache if needed
        2. Adding project root to Python path
        3. Adding pipelines directory to Python path

        Raises:
            RuntimeError: If filesystem sync fails or paths are invalid

        Example:
            >>> # Internal usage
            >>> manager = PipelineManager()
            >>> manager._add_modules_path()
            >>> import my_pipeline  # Now importable
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

    def _load_project_cfg(
        self, reload: bool = False, job_queue_type: str | None = None
    ) -> ProjectConfig:
        """Load or reload the project configuration.

        This internal method handles loading project-wide settings from the config
        directory, applying overrides, and maintaining configuration state.

        Args:
            reload: Force reload configuration even if already loaded.
                Defaults to False for caching behavior.

        Returns:
            ProjectConfig: The loaded project configuration object with any
                specified overrides applied.

        Raises:
            FileNotFoundError: If project configuration file doesn't exist
            ValueError: If configuration format is invalid
            RuntimeError: If filesystem operations fail during loading

        Example:
            >>> # Internal usage
            >>> manager = PipelineManager()
            >>> project_cfg = manager._load_project_cfg(reload=True)
            >>> print(project_cfg.worker.type)
            'rq'
        """
        if hasattr(self, "_project_cfg") and not reload:
            return self._project_cfg

        # Pass overrides to ProjectConfig.load
        self._project_cfg = ProjectConfig.load(
            base_dir=self._base_dir,
            job_queue_type=job_queue_type,
            fs=self._fs,  # Pass pre-configured fs if provided
            storage_options=self._storage_options,
        )
        # Update internal fs reference in case ProjectConfig loaded/created one
        return self._project_cfg

    def load_pipeline(self, name: str, reload: bool = False) -> PipelineConfig:
        """Load or reload configuration for a specific pipeline.

        This internal method handles loading pipeline-specific settings from the config
        directory and maintaining the configuration cache state.

        Args:
            name: Name of the pipeline whose configuration to load
            reload: Force reload configuration even if already loaded.
                When False, returns cached config if available.

        Returns:
            PipelineConfig: The loaded pipeline configuration object

        Raises:
            FileNotFoundError: If pipeline configuration file doesn't exist
            ValueError: If configuration format is invalid
            RuntimeError: If filesystem operations fail during loading

        Example:
            >>> # Internal usage
            >>> manager = PipelineManager()
            >>> cfg = manager._load_pipeline_cfg("data_pipeline", reload=True)
            >>> print(cfg.run.executor.type)
            'async'
        """
        if name == self._current_pipeline_name and not reload:
            return self._pipeline_cfg

        self._current_pipeline_name = name
        self._pipeline_cfg = PipelineConfig.load(
            base_dir=self._base_dir,
            name=name,
            fs=self._fs,
            storage_options=self._storage_options,
        )
        return self._pipeline_cfg

    @property
    def current_pipeline_name(self) -> str:
        """Get the name of the currently loaded pipeline.

        Returns:
            str: Name of the currently loaded pipeline, or empty string if none loaded.

        Example:
            >>> manager = PipelineManager()
            >>> manager._load_pipeline_cfg("example_pipeline")
            >>> print(manager.current_pipeline_name)
            'example_pipeline'
        """
        return self._current_pipeline_name

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
            >>> print(cfg.worker.type)
            'rq'
        """
        if not hasattr(self, "_project_cfg"):
            self._load_project_cfg()
        return self._project_cfg

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
        if not hasattr(self, "_pipeline_cfg"):
            logger.warning("Pipeline config not loaded.")
            return
        return self._pipeline_cfg

    # --- Core Execution Method ---

    def run(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list[str] | None = None,
        config: dict | None = None,
        cache: dict | None = None,
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,
        log_level: str | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        jitter_factor: float | None = None,
        retry_exceptions: tuple | list | None = None,
        on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
    ) -> dict[str, Any]:
        """Execute a pipeline synchronously and return its results.

        This is the main method for running pipelines directly. It handles configuration
        loading, adapter setup, and execution via PipelineRunner.

        Args:
            name (str): Name of the pipeline to run. Must be a valid identifier.
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
            >>> # Complex run with overrides
            >>> results = manager.run(
            ...     name="ml_pipeline",
            ...     inputs={
            ...         "training_date": "2025-04-28",
            ...         "model_params": {"n_estimators": 100}
            ...     },
            ...     final_vars=["model", "metrics"],
            ...     executor_cfg={"type": "threadpool", "max_workers": 4},
            ...     with_adapter_cfg={"tracker": True},
            ...     reload=True
            ... )
        """
        # pipeline_cfg = self._load_pipeline_cfg(name=name, reload=reload)
        run_func = self._get_run_func(
            name=name, reload=reload, on_success=on_success, on_failure=on_failure
        )

        res = run_func(
            project_cfg=self._project_cfg,
            pipeline_cfg=self._pipeline_cfg,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            cache=cache,
            executor_cfg=executor_cfg,
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            adapter=adapter,
            # reload=reload,  # Runner handles module reload if needed
            log_level=log_level,
            max_retries=max_retries,
            retry_delay=retry_delay,
            jitter_factor=jitter_factor,
            retry_exceptions=retry_exceptions,
        )

        return res

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
        self.registry.new(name=name, overwrite=overwrite)

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
        self.registry.delete(name=name, cfg=cfg, module=module)

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
        return self.registry.show_summary(
            name=name,
            cfg=cfg,
            code=code,
            project=project,
            to_html=to_html,
            to_svg=to_svg,
        )

    def show_pipelines(self) -> None:
        """Display all available pipelines in a formatted table.

        The table includes pipeline names, types, and enablement status.
        Uses rich formatting for terminal display.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> manager.show_pipelines()

        """
        self.registry.show_pipelines()

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
        return self.registry.list_pipelines()

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
        return self.registry.pipelines

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
        return self.registry.summary

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
        self.registry.add_hook(
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

    def run_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list[str] | None = None,
        config: dict | None = None,
        cache: bool | dict = False,
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,
        log_level: str | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        jitter_factor: float | None = None,
        retry_exceptions: tuple | list | None = None,
        on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        on_success_pipeline: Callable
        | tuple[Callable, tuple | None, dict | None]
        | None = None,
        on_failure_pipeline: Callable
        | tuple[Callable, tuple | None, dict | None]
        | None = None,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Execute a pipeline job immediately through the job queue.

        Unlike the run() method which executes synchronously, this method runs
        the pipeline through the configured worker system (RQ, APScheduler, etc.).

        If the job queue is not configured, it logs an error and returns None.

        Args:
            name (str): Name of the pipeline to run. Must be a valid identifier.
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
            on_success (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on successful job execution.
                This runs after the pipeline execution through the job queue was executed successfully.
            on_failure (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on job execution failure.
                This runs if the job creation or the pipeline execution through the job queue fails or raises an exception.
            on_success_pipeline (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on successful pipeline execution.
                This runs after the pipeline completes successfully.
            on_failure_pipeline (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on pipeline execution failure.
                This runs if the pipeline fails or raises an exception.

            **kwargs: JobQueue-specific arguments
                For RQ:
                    - queue_name: Queue to use (str)
                    - retry: Number of retries (int)
                    - result_ttl: Time to live for the job result (float or timedelta)
                    - ttl: Time to live for the job (float or timedelta)
                    - timeout: Time to wait for the job to complete (float or timedelta)
                    - repeat: Repeat count (int or dict)
                    - rq_on_failure: Callback function on failure (callable)
                    - rq_on_success: Callback function on success (callable)
                    - rq_on_stopped: Callback function on stop (callable)
                For APScheduler:
                    - job_executor: Executor type (str)

        Returns:
            dict[str, Any] | None: Job execution results if successful, otherwise None.

        Raises:
            ValueError: If pipeline or configuration is invalid
            RuntimeError: If job execution fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Simple job execution
            >>> result = manager.run_job("data_pipeline")
            >>>
            >>> # Complex job with retry logic
            >>> result = manager.run_job(
            ...     name="ml_training",
            ...     inputs={"training_date": "2025-04-28"},
            ...     executor_cfg={"type": "async"},
            ...     with_adapter_cfg={"enable_tracking": True},
            ...     retry=3,
            ...     queue_name="ml_jobs"
            ... )
        """
        if self.jqm is None:
            logger.error(
                "This PipelineManager instance does not have a job queue configured. Skipping job execution."
            )
            return None

        kwargs["on_success"] = kwargs.get("rq_on_success", None)
        kwargs["on_failure"] = kwargs.get("rq_on_failure", None)
        kwargs["on_stopped"] = kwargs.get("rq_on_stopped", None)

        run_func = self._get_run_func(
            name=name,
            reload=reload,
            on_success=on_success_pipeline,
            on_failure=on_failure_pipeline,
        )
        # run_func = run_with_callback(on_success=on_success_pipeline, on_failure=on_failure_pipeline)(
        #    run_func_
        # )
        run_job = run_with_callback(on_success=on_success, on_failure=on_failure)(
            self.jqm.run_job
        )

        return run_job(
            run_func=run_func,
            pipeline_cfg=self._pipeline_cfg,
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            cache=cache,
            executor_cfg=executor_cfg,
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            adapter=adapter,
            log_level=log_level,
            max_retries=max_retries,
            retry_delay=retry_delay,
            jitter_factor=jitter_factor,
            retry_exceptions=retry_exceptions,
            **kwargs,
        )

    def add_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list[str] | None = None,
        config: dict | None = None,
        cache: bool | dict = False,
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,  # Reload config/module before creating run_func
        log_level: str | None = None,
        result_ttl: int | dt.timedelta = 0,
        run_at: dt.datetime | str | None = None,
        run_in: dt.datetime | str | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        jitter_factor: float = 0.1,
        retry_exceptions: tuple = (Exception,),
        on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        on_success_pipeline: Callable
        | tuple[Callable, tuple | None, dict | None]
        | None = None,
        on_failure_pipeline: Callable
        | tuple[Callable, tuple | None, dict | None]
        | None = None,
        **kwargs,  # JobQueue specific args
    ) -> str | UUID | None:
        """Adds a job to the job queue.

        If the job queue is not configured, it logs an error and returns None.

        Args:
            name (str): Name of the pipeline to run. Must be a valid identifier.
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
            run_at (dt.datetime | str | None): Future date to run the job.
                Example: datetime(2025, 4, 28, 12, 0)
                Example str: "2025-04-28T12:00:00" (ISO format)
            run_in (dt.datetime | str | None): Time interval to run the job.
                Example: 3600 (every hour in seconds)
                Example: datetime.timedelta(days=1)
                Example str: "1d" (1 day)
            result_ttl (int | dt.timedelta): Time to live for the job result.
                Example: 3600 (1 hour in seconds)
            log_level (str | None): Logging level for the execution. Default None uses project config.
                Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            max_retries (int): Maximum number of retries for execution.
            retry_delay (float): Delay between retries in seconds.
            jitter_factor (float): Random jitter factor to add to retry delay
            retry_exceptions (tuple): Exceptions that trigger a retry.
            on_success (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on successful job creation.
            on_failure (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on job creation failure.
            on_success_pipeline (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on successful pipeline execution.
            on_failure_pipeline (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on pipeline execution failure.
            **kwargs: Additional keyword arguments passed to the worker's add_job method.
                For RQ this includes:
                    - result_ttl: Time to live for the job result (float or timedelta)
                    - ttl: Time to live for the job (float or timedelta)
                    - timeout: Time to wait for the job to complete (float or timedelta)
                    - queue_name: Name of the queue to use (str)
                    - retry: Number of retries (int)
                    - repeat: Repeat count (int or dict)
                    - rq_on_failure: Callback function on failure (callable)
                    - rq_on_success: Callback function on success (callable)
                    - rq_on_stopped: Callback function on stop (callable)
                For APScheduler, this includes:
                    - job_executor: Job executor to use (str)

        Returns:
            str | UUID | None: The ID of the job that was added to the job queue, or None if the job queue is not configured.

        Raises:
            ValueError: If the job ID is not valid or if the job cannot be scheduled.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>> pm = PipelineManager()
            >>> job_id = pm.add_job("example_pipeline", inputs={"input1": 42})

        """
        if self.jqm is None:
            logger.error(
                "This PipelineManager instance does not have a job queue configured. Skipping job execution."
            )
            return None

        kwargs["on_success"] = kwargs.get("rq_on_success", None)
        kwargs["on_failure"] = kwargs.get("rq_on_failure", None)
        kwargs["on_stopped"] = kwargs.get("rq_on_stopped", None)

        run_func = self._get_run_func(
            name=name,
            reload=reload,
            on_success=on_success_pipeline,
            on_failure=on_failure_pipeline,
        )

        run_in = (
            duration_parser.parse(run_in) if isinstance(run_in, str) else run_in
        )  # convert to seconds
        run_at = (
            dt.datetime.fromisoformat(run_at) if isinstance(run_at, str) else run_at
        )

        add_job = run_with_callback(on_success=on_success, on_failure=on_failure)(
            self.jqm.add_job
        )
        return add_job(
            run_func=run_func,
            pipeline_cfg=self._pipeline_cfg,
            name=name,  # Pass name for logging
            # Pass run parameters
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            cache=cache,
            executor_cfg=executor_cfg,
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            adapter=adapter,
            # reload=reload,  # Note: reload already happened
            log_level=log_level,
            result_ttl=result_ttl,
            run_at=run_at,
            run_in=run_in,
            max_retries=max_retries,
            retry_delay=retry_delay,
            jitter_factor=jitter_factor,
            retry_exceptions=retry_exceptions,
            **kwargs,  # Pass worker args
        )

    def schedule(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list[str] | None = None,
        config: dict | None = None,
        cache: bool | dict = False,
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,
        log_level: str | None = None,
        cron: str | dict[str, str | int] | None = None,
        interval: int | str | dict[str, str | int] | None = None,
        date: dt.datetime | str | None = None,
        overwrite: bool = False,
        schedule_id: str | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        jitter_factor: float | None = None,
        retry_exceptions: tuple | list | None = None,
        on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        on_success_pipeline: Callable
        | tuple[Callable, tuple | None, dict | None]
        | None = None,
        on_failure_pipeline: Callable
        | tuple[Callable, tuple | None, dict | None]
        | None = None,
        **kwargs: Any,
    ) -> str | UUID | None:
        """Schedule a pipeline to run on a recurring or future basis.

        If the job queue is not configured, it logs an error and returns None.

        Args:
            name (str): The name of the pipeline to run.
            inputs (dict | None): Inputs for the pipeline run (overrides config).
            final_vars (list[str] | None): Final variables for the pipeline run (overrides config).
            config (dict | None): Hamilton driver config (overrides config).
            cache (bool | dict): Cache settings (overrides config).
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration (overrides config).
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter configuration (overrides config).
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline adapter configuration (overrides config).
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project adapter configuration (overrides config).
            adapter (dict[str, Any] | None): Additional Hamilton adapters (overrides config).
            reload (bool): Whether to reload module and pipeline config. Defaults to False.
            log_level (str | None): Log level for the run (overrides config).
            cron (str | dict[str, str | int] | None): Cron expression or settings
                Example string: "0 0 * * *" (daily at midnight)
                Example dict: {"minute": "0", "hour": "*/2"} (every 2 hours)
            interval (int | str | dict[str, str | int] | None): Time interval for recurring execution
                Example int: 3600 (every hour in seconds)
                Example str: "1h" (every hour)
                Example dict: {"hours": 1, "minutes": 30} (every 90 minutes)
            date (dt.datetime | str | None): Future date for
                Example: datetime(2025, 4, 28, 12, 0)
                Example str: "2025-04-28T12:00:00" (ISO format)
            overwrite (bool): Whether to overwrite existing schedule with the same ID
            schedule_id (str | None): Unique identifier for the schedule
            max_retries (int): Maximum number of retries for execution
            retry_delay (float): Delay between retries in seconds
            jitter_factor (float): Random jitter factor to add to retry delay
            retry_exceptions (tuple): Exceptions that trigger a retry
            on_success (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on successful schedule creation.
            on_failure (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on schedule creation failure.
            on_success_pipeline (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on successful pipeline execution.
            on_failure_pipeline (Callable | tuple[Callable, tuple | None, dict | None] | None): Callback to run on pipeline execution failure.
            **kwargs: JobQueue-specific scheduling options
                For RQ:
                    - result_ttl: Result lifetime (int seconds)
                    - ttl: Job lifetime (int seconds)
                    - timeout: Job execution timeout (int seconds)
                    - queue_name: Queue to use (str)
                    - repeat: Repeat count (int or dict)
                    - rq_on_failure: Callback function on failure (callable)
                    - rq_on_success: Callback function on success (callable)
                    - rq_on_stopped: Callback function on stop (callable)
                For APScheduler:
                    - misfire_grace_time: Late execution window
                    - coalesce: Combine missed executions (bool)
                    - max_running_jobs: Concurrent instances limit (int)

        Returns:
            str | UUID | None: Unique identifier for the created schedule, or None if scheduling fails.

        Raises:
            ValueError: If schedule parameters are invalid
            RuntimeError: If scheduling fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>> from datetime import datetime, timedelta
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Daily schedule with cron
            >>> schedule_id = manager.schedule(
            ...     name="daily_metrics",
            ...     cron="0 0 * * *",
            ...     inputs={"date": "{{ execution_date }}"}
            ... )
            >>>
            >>> # Interval-based schedule
            >>> schedule_id = manager.schedule(
            ...     name="monitoring",
            ...     interval={"minutes": 15},
            ...     with_adapter_cfg={"enable_alerts": True}
            ... )
            >>>
            >>> # Future one-time execution
            >>> future_date = datetime.now() + timedelta(days=1)
            >>> schedule_id = manager.schedule(
            ...     name="batch_process",
            ...     date=future_date,
            ...     executor_cfg={"type": "async"}
            ... )
        """
        if self.jqm is None:
            logger.error(
                "This PipelineManager instance does not have a job queue configured. Skipping job execution."
            )
            return None

        kwargs["on_success"] = kwargs.get("rq_on_success", None)
        kwargs["on_failure"] = kwargs.get("rq_on_failure", None)
        kwargs["on_stopped"] = kwargs.get("rq_on_stopped", None)

        # pipeline_cfg = self._load_pipeline_cfg(name=name, reload=reload)
        run_func = self._get_run_func(
            name=name,
            reload=reload,
            on_success=on_success_pipeline,
            on_failure=on_failure_pipeline,
        )
        interval = (
            duration_parser.parse(interval) if isinstance(interval, str) else interval
        )
        date = dt.datetime.fromisoformat(date) if isinstance(date, str) else date

        schedule = run_with_callback(on_success=on_success, on_failure=on_failure)(
            self.jqm.schedule
        )
        return schedule(
            run_func=run_func,
            pipeline_cfg=self._pipeline_cfg,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            cache=cache,
            executor_cfg=executor_cfg,
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            adapter=adapter,
            reload=reload,
            log_level=log_level,
            cron=cron,
            interval=interval,
            date=date,
            overwrite=overwrite,
            schedule_id=schedule_id,
            max_retries=max_retries,
            retry_delay=retry_delay,
            jitter_factor=jitter_factor,
            retry_exceptions=retry_exceptions,
            **kwargs,
        )

    def schedule_all(self, **kwargs: Any) -> None:
        """Schedule all pipelines that are enabled in their configuration.

        For each enabled pipeline, applies its configured schedule settings
        and any provided overrides.

        Args:
            **kwargs: Overrides for schedule settings that apply to all pipelines.
                See schedule() method for supported arguments.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Schedule all with default settings
            >>> manager.schedule_all()
            >>>
            >>> # Schedule all with common overrides
            >>> manager.schedule_all(
            ...     max_running_jobs=2,
            ...     coalesce=True,
            ...     misfire_grace_time=300
            ... )
        """
        scheduled_ids = []
        errors = []
        pipeline_names = self.list_pipelines()
        if not pipeline_names:
            logger.warning("No pipelines found to schedule.")
            return

        logger.info(f"Attempting to schedule {len(pipeline_names)} pipelines...")
        for name in pipeline_names:
            try:
                pipeline_cfg = self.load_pipeline(name=name, reload=True)

                if not pipeline_cfg.schedule.enabled:
                    logger.info(
                        f"Skipping scheduling for '{name}': Not enabled in config."
                    )
                    continue

                logger.info(f"Scheduling [cyan]{name}[/cyan]...")
                schedule_id = self.schedule(name=name, reload=False, **kwargs)
                if schedule_id is None:
                    logger.info(
                        f"🟡 Skipping adding schedule for [cyan]{name}[/cyan]: Job queue backend not available or scheduling failed."
                    )
                    continue
                scheduled_ids.append(schedule_id)
            except Exception as e:
                logger.error(f"Failed to schedule pipeline '{name}': {e}")
                errors.append(name)

        if errors:
            logger.error(f"Finished scheduling with errors for: {', '.join(errors)}")
        else:
            logger.info(f"Successfully scheduled {len(scheduled_ids)} pipelines.")

    @property
    def schedules(self) -> list[Any]:
        """Get list of current pipeline schedules.

        Retrieves all active schedules from the worker system.

        Returns:
            list[Any]: List of schedule objects. Exact type depends on worker:
                - RQ: List[rq.job.Job]
                - APScheduler: List[apscheduler.schedulers.base.Schedule]

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> for schedule in manager.schedules:
            ...     print(f"{schedule.id}: Next run at {schedule.next_run_time}")
        """
        if self.jqm is None:
            logger.error(
                "This PipelineManager instance does not have a job queue configured. Skipping schedule retrieval."
            )
            return []
        try:
            return self.jqm._get_schedules()
        except Exception as e:
            logger.error(f"Failed to retrieve schedules: {e}")
            return []
