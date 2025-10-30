import datetime as dt
import os
import posixpath
from pathlib import Path
from typing import Any, Callable, Optional, TYPE_CHECKING
from functools import wraps

import rich
from fsspeckit import (AbstractFileSystem, BaseStorageOptions,
                          DirFileSystem, filesystem)
from loguru import logger

from . import settings
from .cfg import ProjectConfig
from .cfg.pipeline import ExecutorConfig, WithAdapterConfig, RunConfig
from .cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from .cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from .pipeline import PipelineManager
from .utils.logging import setup_logging
from .utils.security import validate_pipeline_name
from .utils.config import merge_run_config_with_kwargs
from .utils.filesystem import FilesystemHelper

setup_logging()

def handle_errors(func):
    """Decorator to handle exceptions, log them, and re-raise as RuntimeError."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            # Extract operation name from function name for better logging
            operation_name = func.__name__.replace('_', ' ').title()
            # For methods like 'run', we want to log the pipeline name if available
            if 'name' in kwargs and func.__name__ in ['run']:
                logger.error(f"Failed to {operation_name.lower()} pipeline '{kwargs.get('name')}': {e}")
                raise RuntimeError(f"Pipeline {operation_name.lower()} failed for '{kwargs.get('name')}': {e}") from e
            else:
                logger.error(f"Failed to {operation_name.lower()}: {e}")
                raise RuntimeError(f"{operation_name} failed: {e}") from e
    return wrapper


class FlowerPowerProject:
    def __init__(
        self,
        pipeline_manager: PipelineManager,
    ):
        """
        Initialize a FlowerPower project.
        Args:
            pipeline_manager (PipelineManager | None): Instance of PipelineManager to manage pipelines.
        """
        self.pipeline_manager = pipeline_manager
        self.name = self.pipeline_manager.project_cfg.name

    def _validate_pipeline_name(self, name: str) -> None:
        """Validate the pipeline name argument using security utilities."""
        validate_pipeline_name(name)  # Use secure validation function

    def _inject_dependencies(self):
        """Inject dependencies between managers for proper architecture.

        This method establishes the correct dependency flow:
        - Project context is properly established for pipeline execution
        """
        # Store project reference for pipeline context
        # This will be used when creating Pipeline instances
        self.pipeline_manager._project_context = self


    # --- Convenience Methods for Pipeline Operations ---

    @handle_errors
    def run(
        self,
        name: str,
        run_config: RunConfig | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """Execute a pipeline synchronously and return its results.

        This is a convenience method that delegates to the pipeline manager.
        It provides the same functionality as `self.pipeline_manager.run()`.

        Args:
            name: Name of the pipeline to run. Must be a valid identifier.
            run_config: Run configuration object containing all execution parameters.
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
            dict[str, Any]: Pipeline execution results, mapping output variable names to their computed values.

        Raises:
            ValueError: If pipeline name doesn't exist or configuration is invalid
            ImportError: If pipeline module cannot be imported
            RuntimeError: If execution fails due to pipeline or adapter errors

        Example:
            ```python
            project = FlowerPowerProject.load(".")

            # Simple execution
            result = project.run("my_pipeline")

            # Run with custom RunConfig
            from flowerpower.cfg.pipeline.run import RunConfig
            config = RunConfig(inputs={"date": "2025-04-28"}, final_vars=["result"])
            result = project.run("ml_pipeline", run_config=config)

            # Complex run with kwargs overrides
            result = project.run(
                "ml_pipeline",
                inputs={"training_date": "2025-04-28"},
                final_vars=["model", "metrics"],
                executor_cfg={"type": "threadpool", "max_workers": 4},
                with_adapter_cfg={"tracker": True},
                reload=True
            )
            ```
        """
        # Validate pipeline manager is available
        if self.pipeline_manager is None:
            raise RuntimeError(
                "Pipeline manager is not configured. Cannot execute pipeline. "
                "Ensure the project was loaded correctly."
            )

        # Validate required arguments
        self._validate_pipeline_name(name)

        # Initialize run_config - use provided config or create empty one
        run_config = run_config or RunConfig()
        
        # Merge kwargs into run_config
        if kwargs:
            run_config = merge_run_config_with_kwargs(run_config, kwargs)

        return self.pipeline_manager.run(
            name=name,
            run_config=run_config,
        )

    @staticmethod
    def _check_project_exists(base_dir: str, fs: AbstractFileSystem | None = None) -> tuple[bool, str]:
        if fs is None:
            fs = filesystem(base_dir, dirfs=True)
        
        # Determine the root path for existence checks
        # For DirFileSystem, paths are relative to its root, so we check "." for the project root.
        # For other filesystems, we use the base_dir directly.
        root_path = "." if isinstance(fs, DirFileSystem) else base_dir

        if not fs.exists(root_path):
            return False, "Project directory does not exist. Please initialize it first."
        
        # Check for required subdirectories
        config_path = posixpath.join(root_path, settings.CONFIG_DIR)
        pipelines_path = posixpath.join(root_path, settings.PIPELINES_DIR)
        
        if not fs.exists(config_path) or not fs.exists(pipelines_path):
            return False, "Project configuration or pipelines directory is missing"

        logger.debug(f"Project exists at {base_dir}")
        return True, ""

    @classmethod
    def load(
        cls,
        base_dir: str | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
        fs: AbstractFileSystem | None = None,
        log_level: str | None = None,
    ) -> "FlowerPowerProject":
        """
        Load an existing FlowerPower project.
        If the project does not exist, it will raise an error.

        Args:
            base_dir (str | None): The base directory of the project. If None, it defaults to the current working directory.
            storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
            fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
            log_level (str | None): The logging level to set for the project. If None, it uses the default log level.

        Returns:
            FlowerPowerProject: An instance of FlowerPowerProject if the project exists, otherwise None.
        Raises:
            FileNotFoundError: If the project does not exist at the specified base directory.
        """
        if log_level is not None:
            setup_logging(level=log_level)

        base_dir = base_dir or str(Path.cwd())

        if storage_options is not None:
            cached = True
            cache_storage = posixpath.join(
                posixpath.expanduser(settings.CACHE_DIR), base_dir.split("://")[-1]
            )
            os.makedirs(cache_storage, exist_ok=True)
        else:
            cached = False
            cache_storage = None
        if not fs:
            fs = filesystem(
                base_dir,
                storage_options=storage_options,
                cached=cached,
                cache_storage=cache_storage,
            )

        project_exists, message = cls._check_project_exists(base_dir, fs)
        if project_exists:
            logger.info(f"Loading FlowerPower project from {base_dir}")
            pipeline_manager = PipelineManager(
                base_dir=base_dir,
                storage_options=storage_options,
                fs=fs,
                log_level=log_level,
            )

            # Create the project instance
            project = cls(
                pipeline_manager=pipeline_manager,
            )

            # Inject dependencies after creation to avoid circular imports
            project._inject_dependencies()

            return project
        else:
            rich.print(f"[red]{message}[/red]")
            logger.error(message)
            return None

    @classmethod
    def new(
        cls,
        name: str | None = None,
        base_dir: str | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
        fs: AbstractFileSystem | None = None,
        hooks_dir: str = settings.HOOKS_DIR,
        log_level: str | None = None,
        overwrite: bool = False,
    ) -> "FlowerPowerProject":
        """
        Initialize a new FlowerPower project.

        Args:
            name (str | None): The name of the project. If None, it defaults to the current directory name.
            base_dir (str | None): The base directory where the project will be created. If None, it defaults to the current working directory.
            storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
            fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
            hooks_dir (str): The directory where the project hooks will be stored.
            overwrite (bool): Whether to overwrite an existing project at the specified base directory.
        Returns:
            FlowerPowerProject: An instance of FlowerPowerProject initialized with the new project.
        Raises:
            FileExistsError: If the project already exists at the specified base directory and overwrite is False.
        """
        if log_level:
            setup_logging(level=log_level)

        # Initialize project parameters
        name, base_dir = cls._resolve_project_params(name, base_dir)

        # Setup filesystem
        fs = cls._setup_filesystem(base_dir, storage_options, fs)

        # Handle existing project
        cls._handle_existing_project(base_dir, fs, hooks_dir, overwrite)

        # Create project structure
        cls._create_project_structure(fs, hooks_dir)

        # Initialize project configuration
        cls._initialize_project_config(name, fs)

        # Print success message and getting started guide
        cls._print_success_message(name, base_dir)

        return cls.load(
            base_dir=base_dir,
            storage_options=storage_options,
            fs=fs,
            log_level=log_level,
        )

    @classmethod
    def _resolve_project_params(
        cls,
        name: str | None,
        base_dir: str | None
    ) -> tuple[str, str]:
        """Resolve project name and base directory."""
        if name is None:
            name = str(Path.cwd().name)
            base_dir = posixpath.join(str(Path.cwd().parent), name)

        if base_dir is None:
            base_dir = posixpath.join(str(Path.cwd()), name)

        return name, base_dir

    @classmethod
    def _setup_filesystem(
        cls,
        base_dir: str,
        storage_options: dict | BaseStorageOptions | None,
        fs: AbstractFileSystem | None
    ) -> AbstractFileSystem:
        """Setup filesystem for project operations."""
        if fs is None:
            fs = filesystem(
                protocol_or_path=base_dir,
                dirfs=True,
                storage_options=storage_options,
            )
        return fs

    @classmethod
    def _handle_existing_project(
        cls,
        base_dir: str,
        fs: AbstractFileSystem,
        hooks_dir: str,
        overwrite: bool
    ) -> None:
        """Handle existing project directory."""
        project_exists, _ = cls._check_project_exists(base_dir, fs)

        if project_exists:
            if overwrite:
                logger.info(f"Overwriting existing project at {base_dir}")

                # Use FilesystemHelper to clean existing files
                fs_helper = FilesystemHelper(base_dir)
                fs_helper.clean_directory(
                    fs,
                    f"{settings.CONFIG_DIR}",
                    settings.PIPELINES_DIR,
                    hooks_dir,
                    recursive=True,
                )
                if fs.exists("README.md"):
                    fs.rm("README.md")
            else:
                error_msg = f"Project already exists at {base_dir}. Use overwrite=True to overwrite the existing project."
                rich.print(f"[red]{error_msg}[/red]")
                logger.error(error_msg)
                raise FileExistsError(error_msg)

    @classmethod
    def _create_project_structure(
        cls,
        fs: AbstractFileSystem,
        hooks_dir: str
    ) -> None:
        """Create project directory structure."""
        fs.makedirs(f"{settings.CONFIG_DIR}/pipelines", exist_ok=True)
        fs.makedirs(settings.PIPELINES_DIR, exist_ok=True)
        fs.makedirs(hooks_dir, exist_ok=True)

    @classmethod
    def _initialize_project_config(
        cls,
        name: str,
        fs: AbstractFileSystem
    ) -> ProjectConfig:
        """Initialize project configuration and create README."""
        # Load project configuration
        cfg = ProjectConfig.load(name=name, fs=fs)

        # Create README file
        with fs.open("README.md", "w") as f:
            f.write(
                f"# FlowerPower project {name.replace('_', ' ').upper()}\n\n"
                f"**created on**\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            )

        # Save configuration
        cfg.save(fs=fs)
        return cfg

    @classmethod
    def _print_success_message(cls, name: str, base_dir: str) -> None:
        """Print success message and getting started guide."""
        rich.print(
            f"\n✨ Initialized FlowerPower project [bold blue]{name}[/bold blue] "
            f"at [italic green]{base_dir}[/italic green]\n"
        )

        rich.print(
            """[bold yellow]Getting Started:[/bold yellow]

0. 🔧 [bold white]Optional: Install uv project manager[/bold white]
    It is recommended to use the python project manager [bold cyan]`uv`[/bold cyan] to manage the
    dependencies of your FlowerPower project.

    Install uv:
        [dim]Run:[/dim] [bold white]pip install uv[/bold white]
        [dim]More options:[/dim] [blue underline]https://docs.astral.sh/uv/getting-started/installation/[/blue underline]

    Initialize uv in your flowerpower project:
        [dim]Run the following in your project directory:[/dim]
        [bold lightgrey]uv init --bare --no-readme[/bold lightgrey]

1. 🚀 [bold white]Create your first pipeline[/bold white]

    CLI command to create a new pipeline:

    [dim]Run the following in your project directory:[/dim]
    [bold lightgrey]flowerpower pipeline new my_first_pipeline[/bold lightgrey]

    Python API to create a new pipeline:"""
        )
        rich.print(
            rich.syntax.Syntax(
                code="""
    from flowerpower import FlowerPowerProject
    project = FlowerPowerProject.load(...)
    project.pipeline_manager.new(name="my_first_pipeline")
        """,
                lexer="python",
                theme="nord",
            )
        )


def initialize_project(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | BaseStorageOptions | None = {},
    fs: AbstractFileSystem | None = None,
    hooks_dir: str = settings.HOOKS_DIR,
    log_level: str | None = None,
) -> FlowerPowerProject:
    """
    Initialize a new FlowerPower project.
    
    
    This is a standalone function that directly calls FlowerPowerProject.new
    with the same arguments, providing easier, separately importable access.
    
    Args:
        name (str | None): The name of the project. If None, it defaults to the current directory name.
        base_dir (str | None): The base directory where the project will be created. If None, it defaults to the current working directory.
        storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
        fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
        hooks_dir (str): The directory where the project hooks will be stored.
        log_level (str | None): The logging level to set for the project.
    
    Returns:
        FlowerPowerProject: An instance of FlowerPowerProject initialized with the new project.
    """
    return FlowerPowerProject.new(
        name=name,
        base_dir=base_dir,
        storage_options=storage_options,
        fs=fs,
        hooks_dir=hooks_dir,
        log_level=log_level,
    )

def create_project(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | BaseStorageOptions | None = {},
    fs: AbstractFileSystem | None = None,
    hooks_dir: str = settings.HOOKS_DIR,
) -> FlowerPowerProject:
    # Note: _check_project_exists expects base_dir to be a string.
    # If base_dir is None, it will be handled by _check_project_exists or the load/init methods.
    # We pass fs directly, as _check_project_exists can handle fs being None.
    # Note: _check_project_exists expects base_dir to be a string.
    # If base_dir is None, it will be handled by _check_project_exists or the load/init methods.
    # We pass fs directly, as _check_project_exists can handle fs being None.
    project_exists, _ = FlowerPowerProject._check_project_exists(base_dir or str(Path.cwd()), fs=fs)

    if project_exists:
        return FlowerPowerProject.load(
            base_dir=base_dir,
            storage_options=storage_options,
            fs=fs,
        )
    else:
        error_message = "Project does not exist. Use `initialize_project()` or `FlowerPowerProject.new()` to create it."
        rich.print(f"[red]{error_message}[/red]")
        logger.error(error_message)
        raise FileNotFoundError(error_message)

# Alias for backward compatibility or alternative naming
FlowerPower = create_project


# The standalone init function is removed as it was a direct pass-through
# to FlowerPowerProject.new(). Users can now use FlowerPowerProject.new() directly
# or the new create_project() function which handles both loading and initialization.
