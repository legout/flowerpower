import os
import posixpath
from pathlib import Path
from types import TracebackType
from typing import Any

from fsspeckit import AbstractFileSystem, BaseStorageOptions, filesystem
from ..cfg import PipelineConfig, ProjectConfig
from ..cfg.pipeline.run import RunConfig
from ..settings import CACHE_DIR, CONFIG_DIR, PIPELINES_DIR
from ..utils.filesystem import FilesystemHelper
from ..utils.logging import setup_logging
from ..utils.security import validate_directory_fragment
from .config_manager import PipelineConfigManager
from .creator import PipelineCreator
from .executor import PipelineExecutor
from .io import PipelineIOManager
from .registry import PipelineRegistry
from .visualizer import PipelineVisualizer

setup_logging()


class PipelineManager:
    """Central manager for FlowerPower pipeline operations.

    This class provides a unified interface for managing pipelines, including:
    - Configuration management and loading
    - Pipeline execution via PipelineExecutor
    - Access to sub-managers for registry, IO, visualization, and execution

    Sub-managers are accessible as properties:
    - ``registry`` — Pipeline creation, deletion, discovery, hooks
    - ``io`` — Pipeline import/export operations
    - ``visualizer`` — DAG visualization
    - ``executor`` — Pipeline execution engine

    Attributes:
        registry (PipelineRegistry): Handles pipeline registration and discovery
        visualizer (PipelineVisualizer): Handles pipeline visualization
        io (PipelineIOManager): Manages pipeline import/export operations
        executor (PipelineExecutor): Handles pipeline execution
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
        >>>
        >>> # Run a pipeline
        >>> result = manager.run("my_pipeline")
        >>>
        >>> # Access sub-managers directly
        >>> manager.creator.create_pipeline("new_pipeline")
        >>> manager.io.import_pipeline("new", "/path/to/source")
        >>> manager.visualizer.save_dag("my_pipeline", base_dir=".")
        >>> manager.visualizer.show_dag("my_pipeline")
    """

    def __init__(
        self,
        base_dir: str | None = None,
        storage_options: dict | BaseStorageOptions | None = None,
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
            ... },
            ...     log_level="DEBUG"
            ... )
        """
        if log_level:
            setup_logging(level=log_level)

        self._setup_filesystem(base_dir, storage_options, fs, cfg_dir, pipelines_dir)
        self._initialize_managers()
        self._ensure_directories_exist()

    def _setup_filesystem(
        self,
        base_dir: str | None,
        storage_options: dict | BaseStorageOptions | None,
        fs: AbstractFileSystem | None,
        cfg_dir: str | None,
        pipelines_dir: str | None,
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
        self._cfg_dir = validate_directory_fragment(
            cfg_dir if cfg_dir is not None else CONFIG_DIR
        )
        self._pipelines_dir = validate_directory_fragment(
            pipelines_dir if pipelines_dir is not None else PIPELINES_DIR
        )

        # Setup filesystem helper
        self._fs_helper = FilesystemHelper(self._base_dir, storage_options)

        # Get filesystem instance
        if fs is not None:
            self._fs = fs
        else:
            # Configure caching only when creating our own filesystem
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

            self._fs = filesystem(
                self._base_dir,
                storage_options=(storage_options or {}),
                cached=cached,
                cache_storage=cache_storage,
            )
        try:
            self._storage_options = (
                storage_options or self._fs.storage_options
                if getattr(self._fs, "protocol", None) != "dir"
                else self._fs.fs.storage_options
            )
        except Exception:
            self._storage_options = storage_options or {}

    def _initialize_managers(self) -> None:
        """Initialize all manager components."""
        # Initialize config manager
        self._config_manager = PipelineConfigManager(
            base_dir=self._base_dir,
            fs=self._fs,
            storage_options=self._storage_options,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )

        # Load project configuration
        self._config_manager.load_project_config(reload=True)

        # Initialize registry
        self.registry = PipelineRegistry(
            project_cfg=self._config_manager.project_config,
            fs=self._fs,
            base_dir=self._base_dir,
            storage_options=self._storage_options,
            config_manager=self._config_manager,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )

        # Initialize creator
        self._creator = PipelineCreator(
            project_cfg=self._config_manager.project_config,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )

        # Initialize executor
        self._executor = PipelineExecutor(
            config_manager=self._config_manager, registry=self.registry
        )

        # Initialize other components
        self._project_context = None
        self.visualizer = PipelineVisualizer(
            project_cfg=self._config_manager.project_config,
            fs=self._fs,
            base_dir=self._base_dir,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )
        self.io = PipelineIOManager(registry=self.registry)

    def _ensure_directories_exist(self) -> None:
        """Ensure essential directories exist."""
        self._fs_helper.ensure_directories_exist(
            self._fs,
            self._cfg_dir or ".",
            self._pipelines_dir or ".",
            posixpath.join(self._cfg_dir or ".", self._pipelines_dir or "."),
        )

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
        """Release cached filesystem resources on context exit.

        Clears the fsspec filesystem instance cache so that remote
        backends (S3, GCS) release cached connections.

        Args:
            exc_type: Type of exception that occurred, if any
            exc_val: Exception instance that occurred, if any
            exc_tb: Traceback of exception that occurred, if any
        """
        try:
            self._fs.clear_instance_cache()
        except Exception:
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

    # --- Properties ---

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
            >>> manager.load_pipeline("example_pipeline")
            >>> cfg = manager.pipeline_cfg
            >>> print(cfg.run.executor)
            'local'
        """
        return self._config_manager.pipeline_config

    @property
    def creator(self) -> PipelineCreator:
        """Get the pipeline creator.

        Returns:
            PipelineCreator: The pipeline creation/deletion helper.
        """
        return self._creator

    @property
    def executor(self) -> PipelineExecutor:
        """Get the pipeline executor.

        Returns:
            PipelineExecutor: The pipeline execution engine.
        """
        return self._executor

    @property
    def pipelines(self) -> list[str]:
        """Get list of all available pipeline names.

        Delegates to ``registry.pipelines``.

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

        Delegates to ``registry.summary``.

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

    # --- Core Execution Method ---

    def run(
        self, name: str, run_config: RunConfig | None = None, **kwargs
    ) -> dict[str, Any]:
        """Execute a pipeline synchronously and return its results.

        This is the main method for running pipelines directly. It handles configuration
        loading, adapter setup, and execution via PipelineExecutor.

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
                    Example: {"hamilton_tracker": True, "mlflow": False}
                pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline-specific adapter settings.
                    Example: {"hamilton_tracker": {"project_id": "123", "tags": {"env": "prod"}}}
                project_adapter_cfg (dict | ProjectAdapterConfig | None): Project-level adapter settings.
                    Example: {"hamilton_tracker": {"api_url": "http://localhost:8241"}}
                adapter (dict[str, Any] | None): Custom adapter instance for pipeline
                    Example: {"ray_graph_adapter": RayGraphAdapter()}
                additional_modules (list[str | ModuleType] | None): Extra modules to
                    load alongside the primary pipeline for Hamilton execution.
                    Example: ["setup", setup_module]
                    Notes:
                        - Unqualified string entries are first resolved against the
                          configured pipeline package, then attempted as raw imports,
                          with hyphen-to-underscore and `pipelines.<name>` fallbacks
                          for compatibility.
                        - When multiple modules provide the same node, later modules
                          take precedence following Hamilton semantics.
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
            ...     additional_modules=["setup"],
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

    async def run_async(
        self, name: str, run_config: RunConfig | None = None, **kwargs
    ) -> dict[str, Any]:
        """Execute a pipeline asynchronously and return its results.

        This is the async counterpart to :meth:`run`. It uses Hamilton's async
        driver internally.

        Args:
            name: Name of the pipeline to run.
            run_config: Run configuration object. When ``async_driver`` is
                ``None`` or ``True`` the Hamilton async driver is used; setting
                it to ``False`` raises a ``ValueError``.
            **kwargs: Additional parameters to override the run_config. See
                :meth:`run` for the full list of supported keyword arguments.

        Returns:
            dict[str, Any]: Results of pipeline execution.

        Example:
            >>> manager = PipelineManager()
            >>> result = await manager.run_async("my_pipeline")
        """
        if hasattr(self, "_project_context") and self._project_context is not None:
            self._executor._project_context = self._project_context

        return await self._executor.run_async(
            name=name, run_config=run_config, **kwargs
        )
