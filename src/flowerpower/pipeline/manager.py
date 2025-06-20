# Add this import at the top with the others
import posixpath
import sys
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, TypeVar, Union

from loguru import logger
from munch import Munch

try:
    from graphviz import Digraph
except ImportError:
    Digraph = Any  # Type alias for when graphviz isn't installed

from .. import settings
from ..cfg import ProjectConfig
from ..cfg.pipeline.run import ExecutorConfig, RetryConfig, WithAdapterConfig
from ..fs import (AbstractFileSystem, BaseStorageOptions, get_protocol,
                  get_storage_options_and_fs)
from ..utils.logging import setup_logging
from .io import PipelineIOManager
from .pipeline import Pipeline
from .registry import HookType, PipelineRegistry

setup_logging(level=settings.LOG_LEVEL)

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
        ...     job_queue_type="rq",
        ...     log_level="DEBUG"
        ... )
    """

    def __init__(
        self,
        base_dir: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        cfg_dir: str | None = None,
        pipelines_dir: str | None = None,
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
                Valid values: "rq".
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
            setup_logging(level=log_level or settings.LOG_LEVEL)

        self._base_dir = base_dir or str(Path.cwd())
        cached = True if storage_options is not None or get_protocol(self._base_dir) != "file" else False
        self._fs, self._storage_options = get_storage_options_and_fs(
            base_dir=self._base_dir,
            storage_options=storage_options,
            fs=fs,
            cached=cached
        )

        # Store overrides for ProjectConfig loading
        self._cfg_dir = cfg_dir or settings.CONFIG_DIR
        self._pipelines_dir = pipelines_dir or settings.PIPELINES_DIR

        self._load_project_cfg(
            reload=True,
        )  # Load project config

        # Ensure essential directories exist (using paths from loaded project_cfg)
        try:
            self._fs.makedirs(self._cfg_dir, exist_ok=True)
            self._fs.makedirs(self._pipelines_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating essential directories: {e}")
            # Consider raising an error here depending on desired behavior

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

    def _load_project_cfg(self, reload: bool = False) -> ProjectConfig:
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
            fs=self._fs,
        )
        # Update internal fs reference in case ProjectConfig loaded/created one
        return self._project_cfg

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

    def run(
        self,
        name: str,
        inputs: dict[str, Any] | None = None,
        final_vars: set[str] | None = None,
        run_config: dict[str, Any] | None = None,
        cache: dict[str, Any] | None = None,
        executor: str | dict[str, Any] | ExecutorConfig | None = None,
        with_adapter: dict[str, Any] | WithAdapterConfig | None = None,
        retry: dict[str, Any] | RetryConfig | None = None,
        adapter_cfg: dict[str, Any] | None = None,
        hamilton_adapters: dict[str, Any] | None = None,
        log_level: str | None = None,
        on_success: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        on_failure: Callable | tuple[Callable, tuple | None, dict | None] | None = None,
        reload: bool = False,
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
            executor (str | dict | ExecutorConfig | None): Execution configuration, can be:
                - str: Executor name, e.g. "threadpool", "local"
                - dict: Raw config, e.g. {"type": "threadpool", "max_workers": 4}
                - ExecutorConfig: Structured config object
            with_adapter (dict | WithAdapterConfig | None): Adapter settings for pipeline execution.
                Example: {"opentelemetry": True, "hamilton_tracker": False}
            adapter_cfg (dict | AdapterConfig | None): Adapter settings.
                Example: {"hamilton_tracker": {"project_id": "123", "tags": {"env": "prod"}},
                        "opentelemetry": {"host": "http://localhost:4317"}}
            hamilton_adapters (dict[str, Any] | None): Custom adapter instance for pipeline
                Example: {"ray_graph_adapter": RayGraphAdapter()}
            reload (bool): Force reload of pipeline configuration.
            log_level (str | None): Logging level for the execution. Default None uses project config.
                Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            retry (dict | RetryConfig | None): Retry configuration for execution failures.
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
            ...     executor={"type": "threadpool", "max_workers": 4},
            ...     with_adapter={"tracker": True},
            ...     reload=True
            ... )
        """
        with Pipeline(
            name=name,
            base_dir=self._base_dir,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
            log_level=log_level,
        ) as pipeline:
            # Load pipeline configuration
            return pipeline.run(
                reload=reload,
                inputs=inputs,
                final_vars=final_vars,
                run_config=run_config,
                cache=cache,
                executor=executor,
                with_adapter=with_adapter,
                retry=retry,
                adapter_cfg=adapter_cfg,
                hamilton_adapters=hamilton_adapters,
                on_failure=on_failure,
                on_success=on_success,
            )

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
        with PipelineRegistry(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            registry.new(name=name, overwrite=overwrite)

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
        with PipelineRegistry(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            registry.delete(name=name, cfg=cfg, module=module)

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
        with PipelineRegistry(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            # Ensure registry is initialized with current project settings
            return registry.get_summary(
                project_cfg=self.project_cfg,
                name=name,
                cfg=cfg,
                code=code,
                project=project,
            )

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
        with PipelineRegistry(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            return registry.show_summary(
                project_cfg=self.project_cfg,
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
        with PipelineRegistry(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            registry.show_pipelines()

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
        with PipelineRegistry(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            return registry.list_pipelines()

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
        with PipelineRegistry(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            return registry.pipelines

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
        with PipelineRegistry(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            return registry.summary

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
        with PipelineRegistry(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            registry.add_hook(
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
        with PipelineIOManager(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as io:
            return io.import_pipeline(
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
        with PipelineIOManager(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as io:
            return io.import_many(
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
        with PipelineIOManager(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as io:
            return io.import_all(
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
        with PipelineIOManager(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as io:
            return io.export_pipeline(
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
        with PipelineIOManager(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as io:
            return io.export_many(
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
        with PipelineIOManager(
            project_name=self.project_cfg.name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as io:
            return io.export_all(
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
        with Pipeline(
            name=name,
            base_dir=self._base_dir,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as pipeline:
            pipeline.save_dag(format=format, reload=reload)

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
        with Pipeline(
            name=name,
            base_dir=self._base_dir,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as pipeline:
            return pipeline.show_dag(format=format, reload=reload, raw=raw)
