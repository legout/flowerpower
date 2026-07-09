import datetime as dt
import os
import posixpath
from pathlib import Path
from types import TracebackType
from typing import Any

import rich
from fsspec.implementations.dirfs import DirFileSystem
from fsspeckit import AbstractFileSystem, BaseStorageOptions, filesystem
from .. import settings
from ..cfg import PipelineConfig, ProjectConfig
from ..cfg.pipeline.run import RunConfig
from ..settings import CACHE_DIR, CONFIG_DIR, PIPELINES_DIR
from ..utils.filesystem import FilesystemHelper
from ..utils.logging import setup_logging
from ..utils.security import validate_directory_fragment, validate_file_path
from .config_manager import PipelineConfigManager
from .creator import PipelineCreator
from .executor import PipelineExecutor
from .io import PipelineIOManager
from .registry import PipelineRegistry
from .project_context import ProjectRuntimeContext
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
        pipelines (list[str]): List of available pipeline names
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
        _context: ProjectRuntimeContext | None = None,
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
        self._context = _context or self._build_runtime_context(
            base_dir=base_dir,
            storage_options=storage_options,
            fs=fs,
            cfg_dir=cfg_dir,
            pipelines_dir=pipelines_dir,
        )
        self._base_dir = self._context.base_dir
        self._fs = self._context.fs
        self._storage_options = self._context.storage_options
        self._cfg_dir = self._context.cfg_dir
        self._pipelines_dir = self._context.pipelines_dir
        self._fs_helper = FilesystemHelper(self._base_dir, storage_options)
        self._initialize_managers()
        self._bootstrap_project_directories()

    @classmethod
    def _build_runtime_context(
        cls,
        *,
        base_dir: str | None,
        storage_options: dict | BaseStorageOptions | None,
        fs: AbstractFileSystem | None,
        cfg_dir: str | None,
        pipelines_dir: str | None,
    ) -> ProjectRuntimeContext:
        """Build runtime context facts for project facade components."""
        resolved_base_dir = base_dir or str(Path.cwd())
        resolved_cfg_dir = validate_directory_fragment(
            cfg_dir if cfg_dir is not None else CONFIG_DIR
        )
        resolved_pipelines_dir = validate_directory_fragment(
            pipelines_dir if pipelines_dir is not None else PIPELINES_DIR
        )

        owns_filesystem = fs is None
        if fs is None:
            if storage_options is not None:
                cached = True
                cache_storage = posixpath.join(
                    posixpath.expanduser(CACHE_DIR),
                    resolved_base_dir.split("://")[-1],
                )
                os.makedirs(cache_storage, exist_ok=True)
            else:
                cached = False
                cache_storage = None

            fs = filesystem(
                resolved_base_dir,
                storage_options=(storage_options or {}),
                cached=cached,
                cache_storage=cache_storage,
            )

        try:
            resolved_storage_options = (
                storage_options or fs.storage_options
                if getattr(fs, "protocol", None) != "dir"
                else fs.fs.storage_options
            )
        except Exception:
            resolved_storage_options = storage_options or {}

        return ProjectRuntimeContext(
            fs=fs,
            base_dir=resolved_base_dir,
            storage_options=resolved_storage_options,
            cfg_dir=resolved_cfg_dir,
            pipelines_dir=resolved_pipelines_dir,
            owns_filesystem=owns_filesystem,
        )

    @staticmethod
    def _is_dir_fs(fs: AbstractFileSystem) -> bool:
        if isinstance(fs, DirFileSystem):
            return True
        inner = getattr(fs, "fs", None)
        if inner is not None and inner is not fs and isinstance(inner, AbstractFileSystem):
            return PipelineManager._is_dir_fs(inner)
        return False

    @classmethod
    def _check_project_exists(
        cls,
        base_dir: str,
        fs: AbstractFileSystem,
    ) -> tuple[bool, str]:
        """Return whether an existing FlowerPower project structure is present."""
        root_path = "." if cls._is_dir_fs(fs) else base_dir
        if not fs.exists(root_path):
            return (
                False,
                "Project directory does not exist. Please initialize it first.",
            )

        config_path = posixpath.join(root_path, settings.CONFIG_DIR)
        pipelines_path = posixpath.join(root_path, settings.PIPELINES_DIR)
        if not fs.exists(config_path) or not fs.exists(pipelines_path):
            return False, "Project configuration or pipelines directory is missing"

        return True, ""

    @classmethod
    def load_existing(
        cls,
        base_dir: str | None = None,
        storage_options: dict | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        log_level: str | None = None,
    ) -> "PipelineManager | None":
        """Load an existing FlowerPower project as a PipelineManager facade."""
        if log_level is not None:
            setup_logging(level=log_level)

        context = cls._build_runtime_context(
            base_dir=base_dir,
            storage_options=storage_options,
            fs=fs,
            cfg_dir=CONFIG_DIR,
            pipelines_dir=PIPELINES_DIR,
        )
        project_exists, message = cls._check_project_exists(
            context.base_dir,
            context.fs,
        )
        if not project_exists:
            rich.print(f"[red]{message}[/red]")
            return None

        return cls(
            base_dir=context.base_dir,
            storage_options=storage_options,
            fs=context.fs,
            log_level=log_level,
            _context=context,
        )

    @classmethod
    def _resolve_project_params(
        cls,
        name: str | None,
        base_dir: str | None,
    ) -> tuple[str, str]:
        """Resolve project name and base directory."""
        if name is None and base_dir is None:
            name = str(Path.cwd().name)
            base_dir = posixpath.join(str(Path.cwd().parent), name)
        elif name is None:
            name = Path(base_dir).name
        elif base_dir is None:
            base_dir = posixpath.join(str(Path.cwd()), name)

        return name, base_dir

    @classmethod
    def _build_project_creation_context(
        cls,
        base_dir: str,
        storage_options: dict | BaseStorageOptions | None,
        fs: AbstractFileSystem | None,
    ) -> ProjectRuntimeContext:
        """Build runtime context for project creation operations."""
        owns_filesystem = fs is None
        if fs is None:
            fs = filesystem(
                protocol_or_path=base_dir,
                dirfs=True,
                storage_options=storage_options,
            )
        return ProjectRuntimeContext(
            fs=fs,
            base_dir=base_dir,
            storage_options=storage_options or {},
            cfg_dir=CONFIG_DIR,
            pipelines_dir=PIPELINES_DIR,
            owns_filesystem=owns_filesystem,
        )

    @classmethod
    def _handle_existing_project(
        cls,
        base_dir: str,
        fs: AbstractFileSystem,
        hooks_dir: str,
        overwrite: bool,
    ) -> None:
        """Handle an existing project before creating a new one."""
        project_exists, _ = cls._check_project_exists(base_dir, fs)
        if not project_exists:
            return

        if overwrite:
            helper = FilesystemHelper(base_dir)
            helper.clean_directory(
                fs,
                f"{settings.CONFIG_DIR}",
                settings.PIPELINES_DIR,
                hooks_dir,
                recursive=True,
            )
            if fs.exists("README.md"):
                fs.rm("README.md")
            return

        error_msg = (
            f"Project already exists at {base_dir}. "
            "Use overwrite=True to overwrite the existing project."
        )
        rich.print(f"[red]{error_msg}[/red]")
        raise FileExistsError(error_msg)

    @staticmethod
    def _create_project_structure(fs: AbstractFileSystem, hooks_dir: str) -> None:
        """Create project directory structure."""
        fs.makedirs(f"{settings.CONFIG_DIR}/{settings.PIPELINES_DIR}", exist_ok=True)
        fs.makedirs(settings.PIPELINES_DIR, exist_ok=True)
        fs.makedirs(hooks_dir, exist_ok=True)

    @staticmethod
    def _initialize_project_config(
        name: str,
        fs: AbstractFileSystem,
        hooks_dir: str,
    ) -> ProjectConfig:
        """Initialize project configuration and README."""
        cfg = ProjectConfig.load(name=name, fs=fs)
        validate_file_path(hooks_dir, allow_absolute=False, allow_relative=True)
        cfg.hooks_dir = hooks_dir

        with fs.open("README.md", "w") as f:
            f.write(
                f"# FlowerPower project {name.replace('_', ' ').upper()}\n\n"
                "**created on**\n\n"
                f"*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            )

        cfg.save(fs=fs)
        return cfg

    @staticmethod
    def _print_success_message(name: str, base_dir: str) -> None:
        """Print a short success message for new projects."""
        rich.print(
            f"\n✨ Initialized FlowerPower project [bold blue]{name}[/bold blue] "
            f"at [italic green]{base_dir}[/italic green]\n"
        )

    @classmethod
    def new_project(
        cls,
        name: str | None = None,
        base_dir: str | None = None,
        storage_options: dict | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        hooks_dir: str = settings.HOOKS_DIR,
        log_level: str | None = None,
        overwrite: bool = False,
    ) -> "PipelineManager":
        """Create a FlowerPower project and return its PipelineManager facade."""
        if log_level:
            setup_logging(level=log_level)

        name, base_dir = cls._resolve_project_params(name, base_dir)
        validate_file_path(hooks_dir, allow_absolute=False, allow_relative=True)
        context = cls._build_project_creation_context(base_dir, storage_options, fs)

        cls._handle_existing_project(
            context.base_dir,
            context.fs,
            hooks_dir,
            overwrite,
        )
        cls._create_project_structure(context.fs, hooks_dir)
        cls._initialize_project_config(name, context.fs, hooks_dir)
        cls._print_success_message(name, context.base_dir)

        return cls(
            base_dir=context.base_dir,
            storage_options=storage_options,
            fs=context.fs,
            log_level=log_level,
            _context=context,
        )

    def _initialize_managers(self) -> None:
        """Initialize all facade components from runtime context."""
        self._config_manager = PipelineConfigManager(
            base_dir=self._context.base_dir,
            fs=self._context.fs,
            storage_options=self._context.storage_options,
            cfg_dir=self._context.cfg_dir,
            pipelines_dir=self._context.pipelines_dir,
        )

        project_cfg = self._config_manager.load_project_config()

        self.registry = PipelineRegistry.from_context(
            self._context,
            project_cfg=project_cfg,
            config_manager=self._config_manager,
        )
        self._creator = PipelineCreator.from_context(
            self._context,
            project_cfg=project_cfg,
        )
        self._executor = PipelineExecutor.from_context(
            self._context,
            config_manager=self._config_manager,
            registry=self.registry,
        )
        self.visualizer = PipelineVisualizer.from_context(
            self._context,
            project_cfg=project_cfg,
        )
        self.io = PipelineIOManager(registry=self.registry)

    def _bootstrap_project_directories(self) -> None:
        """Ensure essential project directories exist."""
        self._fs_helper.ensure_directories_exist(
            self._context.fs,
            self._context.cfg_dir or ".",
            self._context.pipelines_dir or ".",
            posixpath.join(self._context.cfg_dir or ".", self._context.pipelines_dir or "."),
        )

    def _ensure_directories_exist(self) -> None:
        """Compatibility alias for older tests/extensions."""
        self._bootstrap_project_directories()

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
        """Release manager-owned cached filesystem resources on context exit.

        Caller-supplied filesystems are left alone; only filesystems created by
        the facade are eligible for cache cleanup.

        Args:
            exc_type: Type of exception that occurred, if any
            exc_val: Exception instance that occurred, if any
            exc_tb: Traceback of exception that occurred, if any
        """
        if not self._context.owns_filesystem:
            return
        try:
            self._context.fs.clear_instance_cache()
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
        return self.registry.load_config(name, reload=reload)

    # --- Properties ---

    @property
    def project_cfg(self) -> ProjectConfig:
        """Get the project configuration.

        Returns:
            ProjectConfig: Project-wide configuration object.

        Example:
            >>> manager = PipelineManager()
            >>> cfg = manager.project_cfg
            >>> print(cfg.name)
            'my_project'
        """
        return self.registry.project_cfg

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
        return await self._executor.run_async(
            name=name, run_config=run_config, **kwargs
        )
