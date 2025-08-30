import datetime as dt
import os
import posixpath
from pathlib import Path
from typing import Any, Callable, Optional, TYPE_CHECKING
from functools import wraps

import rich
from fsspec_utils import (AbstractFileSystem, BaseStorageOptions,
                          DirFileSystem, filesystem)
from loguru import logger

from . import settings
from .cfg import ProjectConfig
from .cfg.pipeline import ExecutorConfig, WithAdapterConfig
from .cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from .cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from .pipeline import PipelineManager
from .utils.logging import setup_logging

# Attempt to import JobQueueManager from the optional flowerpower-scheduler package
try:
    from flowerpower_scheduler import JobQueueManager
except ImportError:
    JobQueueManager = None

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
            # For methods like 'run', 'enqueue', 'schedule', we want to log the pipeline name if available
            if 'name' in kwargs and func.__name__ in ['run', 'enqueue', 'schedule']:
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
        job_queue_manager: Optional['JobQueueManager'] = None,
    ):
        """
        Initialize a FlowerPower project.
        Args:
            pipeline_manager (PipelineManager | None): Instance of PipelineManager to manage pipelines.
            job_queue_manager (Optional[JobQueueManager]): Instance of JobQueueManager to manage job queues.
        """
        self.pipeline_manager = pipeline_manager
        self.job_queue_manager = job_queue_manager
        self.name = self.pipeline_manager.project_cfg.name
        self.job_queue_type = (
            self.job_queue_manager.cfg.type
            if self.job_queue_manager is not None
            else None
        )
        self.job_queue_backend = (
            self.job_queue_manager.cfg.backend
            if self.job_queue_manager is not None
            else None
        )

    def _validate_job_queue_manager(self) -> None:
        """Validate that the job queue manager is configured."""
        if self.job_queue_manager is None:
            raise RuntimeError(
                "Job queue manager is not configured. "
                "Please install 'flowerpower-scheduler' and ensure it is configured correctly."
            )

    def _validate_pipeline_name(self, name: str) -> None:
        """Validate the pipeline name argument."""
        if not name or not isinstance(name, str):
            raise ValueError("Pipeline 'name' must be a non-empty string")
        if name.strip() != name:
            raise ValueError(
                "Pipeline 'name' cannot have leading or trailing whitespace"
            )

    def _validate_queue_names(self, queue_names: list[str] | None) -> None:
        """Validate the queue_names argument."""
        if queue_names is not None and not isinstance(queue_names, list):
            raise TypeError("'queue_names' must be a list of strings")
        if queue_names is not None:
            for queue_name in queue_names:
                if not isinstance(queue_name, str):
                    raise TypeError("All items in 'queue_names' must be strings")

    def _validate_worker_args(self, background: bool, with_scheduler: bool) -> None:
        """Validate boolean arguments for worker methods."""
        if not isinstance(background, bool):
            raise TypeError("'background' must be a boolean")
        if not isinstance(with_scheduler, bool):
            raise TypeError("'with_scheduler' must be a boolean")

    def _inject_dependencies(self):
        """Inject dependencies between managers for proper architecture.

        This method establishes the correct dependency flow:
        - Project context is properly established for pipeline execution
        - JobQueueManager automatically creates its own PipelineRegistry via property
        """
        # Store project reference for pipeline context
        # This will be used when creating Pipeline instances
        self.pipeline_manager._project_context = self

        # Note: JobQueueManager now creates its own PipelineRegistry automatically
        # via the pipeline_registry property, so no manual injection needed

    # --- Convenience Methods for Pipeline Operations ---

    @handle_errors
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

        This is a convenience method that delegates to the pipeline manager.
        It provides the same functionality as `self.pipeline_manager.run()`.

        Args:
            name: Name of the pipeline to run. Must be a valid identifier.
            inputs: Override pipeline input values. Example: {"data_date": "2025-04-28"}
            final_vars: Specify which output variables to return. Example: ["model", "metrics"]
            config: Configuration for Hamilton pipeline executor. Example: {"model": "LogisticRegression"}
            cache: Cache configuration for results. Example: {"recompute": ["node1", "final_node"]}
            executor_cfg: Execution configuration, can be:
                - str: Executor name, e.g. "threadpool", "local"
                - dict: Raw config, e.g. {"type": "threadpool", "max_workers": 4}
                - ExecutorConfig: Structured config object
            with_adapter_cfg: Adapter settings for pipeline execution.
                Example: {"opentelemetry": True, "tracker": False}
            pipeline_adapter_cfg: Pipeline-specific adapter settings.
                Example: {"tracker": {"project_id": "123", "tags": {"env": "prod"}}}
            project_adapter_cfg: Project-level adapter settings.
                Example: {"opentelemetry": {"host": "http://localhost:4317"}}
            adapter: Custom adapter instance for pipeline
                Example: {"ray_graph_adapter": RayGraphAdapter()}
            reload: Force reload of pipeline configuration.
            log_level: Logging level for the execution. Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            max_retries: Maximum number of retries for execution.
            retry_delay: Delay between retries in seconds.
            jitter_factor: Random jitter factor to add to retry delay
            retry_exceptions: Exceptions that trigger a retry.
            on_success: Callback to run on successful pipeline execution.
            on_failure: Callback to run on pipeline execution failure.

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

            # With custom inputs
            result = project.run(
                "ml_pipeline",
                inputs={"data_date": "2025-01-01"},
                final_vars=["model", "metrics"]
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

        return self.pipeline_manager.run(
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
            reload=reload,
            log_level=log_level,
            max_retries=max_retries,
            retry_delay=retry_delay,
            jitter_factor=jitter_factor,
            retry_exceptions=retry_exceptions,
            on_success=on_success,
            on_failure=on_failure,
        )

    @handle_errors
    def enqueue(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        """Enqueue a pipeline for execution via the job queue.

        This is a convenience method that delegates to the job queue manager's
        enqueue_pipeline method. It provides asynchronous pipeline execution.

        Args:
            name: Name of the pipeline to enqueue
            *args: Additional positional arguments for job execution
            **kwargs: Keyword arguments for pipeline execution and job queue options.
                Supports all parameters from pipeline_manager.run() plus job queue specific options:
                - run_in: Schedule the job to run after a delay
                - run_at: Schedule the job to run at a specific datetime
                - queue_name: Queue to use (for RQ)
                - timeout: Job execution timeout
                - retry: Number of retries
                - result_ttl: Result time to live
                - ttl: Job time to live

        Returns:
            Job ID or result depending on implementation, or None if job queue not configured

        Raises:
            RuntimeError: If job queue manager is not configured

        Example:
            ```python
            project = FlowerPowerProject.load(".")

            # Immediate execution via job queue
            job_id = project.enqueue("my_pipeline", inputs={"date": "today"})

            # Delayed execution
            job_id = project.enqueue("my_pipeline", inputs={"date": "today"}, run_in=300)

            # Scheduled execution
            from datetime import datetime
            job_id = project.enqueue(
                "my_pipeline",
                inputs={"date": "today"},
                run_at=datetime(2025, 1, 1, 9, 0)
            )
            ```
        """
        # Validate job queue manager and arguments
        self._validate_job_queue_manager()
        self._validate_pipeline_name(name)

        return self.job_queue_manager.enqueue_pipeline(
            name=name, project_context=self, *args, **kwargs
        )

    @handle_errors
    def schedule(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        """Schedule a pipeline for recurring or future execution.

        This is a convenience method that delegates to the job queue manager's
        schedule_pipeline method. It provides scheduled pipeline execution.

        Args:
            name: Name of the pipeline to schedule
            *args: Additional positional arguments for scheduling
            **kwargs: Keyword arguments for pipeline execution and scheduling options.
                Supports all parameters from pipeline_manager.run() plus scheduling options:
                - cron: Cron expression for recurring execution (e.g., "0 9 * * *")
                - interval: Time interval for recurring execution (int seconds or dict)
                - date: Future date for one-time execution (datetime or ISO string)
                - schedule_id: Unique identifier for the schedule
                - overwrite: Whether to overwrite existing schedule with same ID

        Returns:
            Schedule ID or job ID depending on implementation, or None if job queue not configured

        Raises:
            RuntimeError: If job queue manager is not configured

        Example:
            ```python
            project = FlowerPowerProject.load(".")

            # Daily schedule with cron
            schedule_id = project.schedule(
                "daily_metrics",
                cron="0 9 * * *",  # 9 AM daily
                inputs={"date": "{{ execution_date }}"}
            )

            # Interval-based schedule
            schedule_id = project.schedule(
                "monitoring",
                interval={"minutes": 15},
                inputs={"check_type": "health"}
            )

            # Future one-time execution
            from datetime import datetime, timedelta
            future_date = datetime.now() + timedelta(days=1)
            schedule_id = project.schedule(
                "batch_process",
                date=future_date,
                inputs={"process_date": "tomorrow"}
            )
            ```
        """
        # Validate job queue manager and arguments
        self._validate_job_queue_manager()
        self._validate_pipeline_name(name)

        return self.job_queue_manager.schedule_pipeline(
            name=name, project_context=self, *args, **kwargs
        )

    @handle_errors
    def start_worker(
        self,
        background: bool = False,
        queue_names: list[str] | None = None,
        with_scheduler: bool = True,
        **kwargs: Any,
    ) -> None:
        """Start a worker process for processing jobs from the queues.

        This is a convenience method that delegates to the job queue manager's
        start_worker method.

        Args:
            background: If True, runs the worker in a non-blocking background mode.
                If False, runs in the current process and blocks until stopped.
            queue_names: List of queue names to process. If None, processes all
                queues defined in the backend configuration.
            with_scheduler: Whether to include the scheduler queue for processing
                scheduled jobs (if supported by the backend).
            **kwargs: Additional worker configuration options specific to the job queue backend.

        Raises:
            RuntimeError: If job queue manager is not configured

        Example:
            ```python
            project = FlowerPowerProject.load(".")

            # Start worker in foreground (blocks)
            project.start_worker()

            # Start worker in background
            project.start_worker(background=True)

            # Start worker for specific queues
            project.start_worker(queue_names=["high_priority", "default"])
            ```
        """
        # Validate job queue manager and arguments
        self._validate_job_queue_manager()
        self._validate_queue_names(queue_names)
        self._validate_worker_args(background, with_scheduler)

        return self.job_queue_manager.start_worker(
            background=background,
            queue_names=queue_names,
            with_scheduler=with_scheduler,
            **kwargs,
        )

    @handle_errors
    def stop_worker(self) -> None:
        """Stop the worker process.

        This is a convenience method that delegates to the job queue manager's
        stop_worker method.

        Raises:
            RuntimeError: If job queue manager is not configured

        Example:
            ```python
            project = FlowerPowerProject.load(".")
            project.stop_worker()
            ```
        """
        # Validate job queue manager is available
        self._validate_job_queue_manager()

        return self.job_queue_manager.stop_worker()

    @handle_errors
    def start_worker_pool(
        self,
        num_workers: int | None = None,
        background: bool = False,
        queue_names: list[str] | None = None,
        with_scheduler: bool = True,
        **kwargs: Any,
    ) -> None:
        """Start a pool of worker processes to handle jobs in parallel.

        This is a convenience method that delegates to the job queue manager's
        start_worker_pool method.

        Args:
            num_workers: Number of worker processes to start. If None, uses CPU
                count or backend-specific default.
            background: If True, runs the worker pool in a non-blocking background mode.
                If False, runs in the current process and blocks until stopped.
            queue_names: List of queue names to process. If None, processes all
                queues defined in the backend configuration.
            with_scheduler: Whether to include the scheduler queue for processing
                scheduled jobs (if supported by the backend).
            **kwargs: Additional worker pool configuration options specific to the job queue backend.

        Raises:
            RuntimeError: If job queue manager is not configured

        Example:
            ```python
            project = FlowerPowerProject.load(".")

            # Start worker pool with default number of workers
            project.start_worker_pool()

            # Start 4 workers in background
            project.start_worker_pool(num_workers=4, background=True)

            # Start worker pool for specific queues
            project.start_worker_pool(
                num_workers=2,
                queue_names=["high_priority", "default"]
            )
            ```
        """
        # Validate job queue manager and arguments
        self._validate_job_queue_manager()
        if num_workers is not None and (
            not isinstance(num_workers, int) or num_workers <= 0
        ):
            raise ValueError("'num_workers' must be a positive integer")
        self._validate_queue_names(queue_names)
        self._validate_worker_args(background, with_scheduler)

        return self.job_queue_manager.start_worker_pool(
            num_workers=num_workers,
            background=background,
            queue_names=queue_names,
            with_scheduler=with_scheduler,
            **kwargs,
        )

    @handle_errors
    def stop_worker_pool(self) -> None:
        """Stop all worker processes in the worker pool.

        This is a convenience method that delegates to the job queue manager's
        stop_worker_pool method.

        Raises:
            RuntimeError: If job queue manager is not configured

        Example:
            ```python
            project = FlowerPowerProject.load(".")
            project.stop_worker_pool()
            ```
        """
        # Validate job queue manager is available
        self._validate_job_queue_manager()

        return self.job_queue_manager.stop_worker_pool()

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

            job_queue_manager = None
            if JobQueueManager is not None:
                try:
                    job_queue_manager = JobQueueManager(
                        name=f"{pipeline_manager.project_cfg.name}_job_queue",
                        base_dir=base_dir,
                        storage_options=storage_options,
                        fs=fs,
                    )
                except Exception as e:
                    logger.warning(f"Failed to initialize JobQueueManager: {e}")

            # Create the project instance
            project = cls(
                pipeline_manager=pipeline_manager,
                job_queue_manager=job_queue_manager,
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

        if name is None:
            name = str(Path.cwd().name)
            base_dir = posixpath.join(str(Path.cwd().parent), name)

        if base_dir is None:
            base_dir = posixpath.join(str(Path.cwd()), name)

        if fs is None:
            fs = filesystem(
                protocol_or_path=base_dir,
                dirfs=True,
                storage_options=storage_options,
            )

        # Check if project already exists
        project_exists, message = cls._check_project_exists(base_dir, fs)
        if project_exists:
            if overwrite:
                # Delete existing project files and directories
                logger.info(f"Overwriting existing project at {base_dir}")
                
                # Remove directories recursively
                config_path = f"{settings.CONFIG_DIR}"
                pipelines_path = settings.PIPELINES_DIR
                
                if fs.exists(config_path):
                    fs.rm(config_path, recursive=True)
                if fs.exists(pipelines_path):
                    fs.rm(pipelines_path, recursive=True)
                if fs.exists(hooks_dir):
                    fs.rm(hooks_dir, recursive=True)
                
                # Remove README.md file
                if fs.exists("README.md"):
                    fs.rm("README.md")
            else:
                error_msg = f"Project already exists at {base_dir}. Use overwrite=True to overwrite the existing project."
                rich.print(f"[red]{error_msg}[/red]")
                logger.error(error_msg)
                raise FileExistsError(error_msg)

        fs.makedirs(f"{settings.CONFIG_DIR}/pipelines", exist_ok=True)
        fs.makedirs(settings.PIPELINES_DIR, exist_ok=True)
        fs.makedirs(hooks_dir, exist_ok=True)

        # Load project configuration without job_queue_type
        cfg = ProjectConfig.load(name=name, fs=fs)

        with fs.open("README.md", "w") as f:
            f.write(
                f"# FlowerPower project {name.replace('_', ' ').upper()}\n\n"
                f"**created on**\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            )
        cfg.save(fs=fs)

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

        return cls.load(
            base_dir=base_dir,
            storage_options=storage_options,
            fs=fs,
            log_level=log_level,
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
    """
    Create or load a FlowerPower project.

    If a project exists at the specified base_dir, it will be loaded.
    Otherwise, a new project will be initialized.

    Args:
        name (str | None): The name of the project. If None, it defaults to the current directory name.
        base_dir (str | None): The base directory where the project will be created or loaded from.
                               If None, it defaults to the current working directory.
        storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
        fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
        hooks_dir (str): The directory where the project hooks will be stored.

    Returns:
        FlowerPowerProject: An instance of FlowerPowerProject.
    """
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
