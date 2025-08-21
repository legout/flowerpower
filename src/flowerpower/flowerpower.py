import datetime as dt
import os
import posixpath
from pathlib import Path
from typing import Any, Callable

import rich
from fsspec_utils import (AbstractFileSystem, BaseStorageOptions,
                          DirFileSystem, filesystem)
from loguru import logger

from . import settings
from .cfg import ProjectConfig
from .cfg.pipeline import ExecutorConfig, WithAdapterConfig
from .cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from .cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from .job_queue import JobQueueManager
from .pipeline import PipelineManager
from .utils.logging import setup_logging

setup_logging(level=settings.LOG_LEVEL)


class FlowerPowerProject:
    def __init__(
        self,
        pipeline_manager: PipelineManager,
        job_queue_manager: JobQueueManager | None = None,
    ):
        """
        Initialize a FlowerPower project.
        Args:
            pipeline_manager (PipelineManager | None): Instance of PipelineManager to manage pipelines.
            job_queue_manager (JobQueueManager | None): Instance of JobQueueManager to manage job queues.
        """
        self.pipeline_manager = pipeline_manager
        self.job_queue_manager = job_queue_manager
        self.name = self.pipeline_manager.project_cfg.name
        self._base_dir = self.pipeline_manager._base_dir
        self._fs = self.pipeline_manager._fs
        self._storage_options = self.pipeline_manager._storage_options
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
        if not name or not isinstance(name, str):
            raise ValueError("Pipeline 'name' must be a non-empty string")

        if name.strip() != name:
            raise ValueError(
                "Pipeline 'name' cannot have leading or trailing whitespace"
            )

        # Validate optional arguments
        if inputs is not None and not isinstance(inputs, dict):
            raise TypeError("'inputs' must be a dictionary")

        if final_vars is not None and not isinstance(final_vars, list):
            raise TypeError("'final_vars' must be a list of strings")

        if final_vars is not None:
            for var in final_vars:
                if not isinstance(var, str):
                    raise TypeError("All items in 'final_vars' must be strings")

        try:
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
        except Exception as e:
            # Log error and re-raise with context
            logger.error(f"Failed to execute pipeline '{name}': {e}")
            raise RuntimeError(f"Pipeline execution failed for '{name}': {e}") from e

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
        # Validate job queue manager is available
        if self.job_queue_manager is None:
            raise RuntimeError(
                "Job queue manager is not configured. Cannot enqueue pipeline jobs. "
                "Ensure the project was loaded with a job queue configuration."
            )

        # Validate required arguments
        if not name or not isinstance(name, str):
            raise ValueError("Pipeline 'name' must be a non-empty string")

        if name.strip() != name:
            raise ValueError(
                "Pipeline 'name' cannot have leading or trailing whitespace"
            )

        try:
            return self.job_queue_manager.enqueue_pipeline(
                name=name, project_context=self, *args, **kwargs
            )
        except Exception as e:
            # Log error and re-raise with context
            logger.error(f"Failed to enqueue pipeline '{name}': {e}")
            raise RuntimeError(f"Pipeline enqueue failed for '{name}': {e}") from e

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
        # Validate job queue manager is available
        if self.job_queue_manager is None:
            raise RuntimeError(
                "Job queue manager is not configured. Cannot schedule pipeline jobs. "
                "Ensure the project was loaded with a job queue configuration."
            )

        # Validate required arguments
        if not name or not isinstance(name, str):
            raise ValueError("Pipeline 'name' must be a non-empty string")

        if name.strip() != name:
            raise ValueError(
                "Pipeline 'name' cannot have leading or trailing whitespace"
            )

        try:
            return self.job_queue_manager.schedule_pipeline(
                name=name, project_context=self, *args, **kwargs
            )
        except Exception as e:
            # Log error and re-raise with context
            logger.error(f"Failed to schedule pipeline '{name}': {e}")
            raise RuntimeError(f"Pipeline schedule failed for '{name}': {e}") from e

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
        # Validate job queue manager is available
        if self.job_queue_manager is None:
            raise RuntimeError(
                "Job queue manager is not configured. Cannot start worker. "
                "Ensure the project was loaded with a job queue configuration."
            )

        # Validate optional arguments
        if queue_names is not None and not isinstance(queue_names, list):
            raise TypeError("'queue_names' must be a list of strings")

        if queue_names is not None:
            for queue_name in queue_names:
                if not isinstance(queue_name, str):
                    raise TypeError("All items in 'queue_names' must be strings")

        if not isinstance(background, bool):
            raise TypeError("'background' must be a boolean")

        if not isinstance(with_scheduler, bool):
            raise TypeError("'with_scheduler' must be a boolean")

        try:
            return self.job_queue_manager.start_worker(
                background=background,
                queue_names=queue_names,
                with_scheduler=with_scheduler,
                **kwargs,
            )
        except Exception as e:
            # Log error and re-raise with context
            logger.error(f"Failed to start worker: {e}")
            raise RuntimeError(f"Worker start failed: {e}") from e

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
        if self.job_queue_manager is None:
            raise RuntimeError(
                "Job queue manager is not configured. Cannot stop worker. "
                "Ensure the project was loaded with a job queue configuration."
            )

        try:
            return self.job_queue_manager.stop_worker()
        except Exception as e:
            # Log error and re-raise with context
            logger.error(f"Failed to stop worker: {e}")
            raise RuntimeError(f"Worker stop failed: {e}") from e

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
        # Validate job queue manager is available
        if self.job_queue_manager is None:
            raise RuntimeError(
                "Job queue manager is not configured. Cannot start worker pool. "
                "Ensure the project was loaded with a job queue configuration."
            )

        # Validate optional arguments
        if num_workers is not None and (
            not isinstance(num_workers, int) or num_workers <= 0
        ):
            raise ValueError("'num_workers' must be a positive integer")

        if queue_names is not None and not isinstance(queue_names, list):
            raise TypeError("'queue_names' must be a list of strings")

        if queue_names is not None:
            for queue_name in queue_names:
                if not isinstance(queue_name, str):
                    raise TypeError("All items in 'queue_names' must be strings")

        if not isinstance(background, bool):
            raise TypeError("'background' must be a boolean")

        if not isinstance(with_scheduler, bool):
            raise TypeError("'with_scheduler' must be a boolean")

        try:
            return self.job_queue_manager.start_worker_pool(
                num_workers=num_workers,
                background=background,
                queue_names=queue_names,
                with_scheduler=with_scheduler,
                **kwargs,
            )
        except Exception as e:
            # Log error and re-raise with context
            logger.error(f"Failed to start worker pool: {e}")
            raise RuntimeError(f"Worker pool start failed: {e}") from e

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
        if self.job_queue_manager is None:
            raise RuntimeError(
                "Job queue manager is not configured. Cannot stop worker pool. "
                "Ensure the project was loaded with a job queue configuration."
            )

        try:
            return self.job_queue_manager.stop_worker_pool()
        except Exception as e:
            # Log error and re-raise with context
            logger.error(f"Failed to stop worker pool: {e}")
            raise RuntimeError(f"Worker pool stop failed: {e}") from e

    @staticmethod
    def _check_project_exists(base_dir: str, fs: AbstractFileSystem | None = None):
        if fs is None:
            fs = filesystem(base_dir, dirfs=True)
        if isinstance(fs, DirFileSystem):
            if not fs.exists("."):
                rich.print(
                    "[red]Project directory does not exist. Please initialize it first.[/red]"
                )
                return False
            if not fs.exists("conf") or not fs.exists("pipelines"):
                rich.print(
                    "[red]Project configuration or pipelines directory is missing[/red]"
                )
                return False
        else:
            if not fs.exists(base_dir):
                rich.print(
                    "[red]Project directory does not exist. Please initialize it first.[/red]"
                )
                return False
            if not fs.exists(posixpath.join(base_dir, "conf")) or not fs.exists(
                posixpath.join(base_dir, "pipelines")
            ):
                rich.print(
                    "[red]Project configuration or pipelines directory is missing[/red]"
                )
                return False

        logger.debug(f"Project exists at {base_dir}")
        return True

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
        if log_level:
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

        if cls._check_project_exists(base_dir, fs):
            logger.info(f"Loading FlowerPower project from {base_dir}")
            pipeline_manager = PipelineManager(
                base_dir=base_dir,
                storage_options=storage_options,
                fs=fs,
                log_level=log_level,
            )

            job_queue_manager = JobQueueManager(
                name=f"{pipeline_manager.project_cfg.name}_job_queue",
                base_dir=base_dir,
                storage_options=storage_options,
                fs=fs,
            )

            # Create the project instance
            project = cls(
                pipeline_manager=pipeline_manager,
                job_queue_manager=job_queue_manager,
            )

            # Inject dependencies after creation to avoid circular imports
            project._inject_dependencies()

            return project
        else:
            logger.error(
                f"Project does not exist at {base_dir}. Please initialize it first. Use `FlowerPowerProject.init()` to create a new project."
            )
            return None

    @classmethod
    def init(
        cls,
        name: str | None = None,
        base_dir: str | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
        fs: AbstractFileSystem | None = None,
        job_queue_type: str = settings.JOB_QUEUE_TYPE,
        hooks_dir: str = settings.HOOKS_DIR,
        log_level: str | None = None,
    ) -> "FlowerPowerProject":
        """
        Initialize a new FlowerPower project.

        Args:
            name (str | None): The name of the project. If None, it defaults to the current directory name.
            base_dir (str | None): The base directory where the project will be created. If None, it defaults to the current working directory.
            storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
            fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
            job_queue_type (str): The type of job queue to use for the project.
            hooks_dir (str): The directory where the project hooks will be stored.
        Returns:
            FlowerPowerProject: An instance of FlowerPowerProject initialized with the new project.
        Raises:
            FileExistsError: If the project already exists at the specified base directory.
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

        fs.makedirs(f"{settings.CONFIG_DIR}/pipelines", exist_ok=True)
        fs.makedirs(settings.PIPELINES_DIR, exist_ok=True)
        fs.makedirs(hooks_dir, exist_ok=True)

        cfg = ProjectConfig.load(name=name, job_queue_type=job_queue_type, fs=fs)

        with fs.open("README.md", "w") as f:
            f.write(
                f"# FlowerPower project {name.replace('_', ' ').upper()}\n\n"
                f"**created on**\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            )
        cfg.save(fs=fs)
        os.chdir(posixpath.join(base_dir, name))

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
            log_level=settings.LOG_LEVEL,
        )


class FlowerPower:
    def __new__(
        self,
        name: str | None = None,
        base_dir: str | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
        fs: AbstractFileSystem | None = None,
        job_queue_type: str = settings.JOB_QUEUE_TYPE,
        hooks_dir: str = settings.HOOKS_DIR,
    ) -> FlowerPowerProject:
        """
        Initialize a FlowerPower project.

        Args:
            name (str | None): The name of the project. If None, it defaults to the current directory name.
            base_dir (str | None): The base directory where the project will be created. If None, it defaults to the current working directory.
            storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
            fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
            job_queue_type (str): The type of job queue to use for the project.
            hooks_dir (str): The directory where the project hooks will be stored.

        Returns:
            FlowerPowerProject: An instance of FlowerPowerProject initialized with the new project.
        """
        if FlowerPowerProject._check_project_exists(base_dir, fs=fs):
            return FlowerPowerProject.load(
                base_dir=base_dir,
                storage_options=storage_options,
                fs=fs,
            )
        else:
            return FlowerPowerProject.init(
                name=name,
                base_dir=base_dir,
                storage_options=storage_options,
                fs=fs,
                job_queue_type=job_queue_type,
                hooks_dir=hooks_dir,
            )

    def __call__(self) -> FlowerPowerProject:
        """
        Call the FlowerPower instance to return the current project.

        Returns:
            FlowerPowerProject: The current FlowerPower project.
        """
        return self


def init(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | BaseStorageOptions | None = {},
    fs: AbstractFileSystem | None = None,
    job_queue_type: str = settings.JOB_QUEUE_TYPE,
    hooks_dir: str = settings.HOOKS_DIR,
) -> FlowerPowerProject:
    """
    Initialize a FlowerPower project.

    Args:
        name (str | None): The name of the project. If None, it defaults to the current directory name.
        base_dir (str | None): The base directory where the project will be created. If None, it defaults to the current working directory.
        storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
        fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
        job_queue_type (str): The type of job queue to use for the project.
        hooks_dir (str): The directory where the project hooks will be stored.

    Returns:
        FlowerPowerProject: An instance of FlowerPowerProject initialized with the new project.
    """
    return FlowerPowerProject.init(
        name=name,
        base_dir=base_dir,
        storage_options=storage_options,
        fs=fs,
        job_queue_type=job_queue_type,
        hooks_dir=hooks_dir,
    )
