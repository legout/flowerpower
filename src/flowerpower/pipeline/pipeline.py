import posixpath
import sys
from pathlib import Path
from types import TracebackType
from typing import Any, Callable

from .. import settings
from ..cfg import PipelineConfig, ProjectConfig
from ..cfg.adapter import AdapterConfig
from ..cfg.pipeline.run import ExecutorConfig, RetryConfig, WithAdapterConfig
from ..fs import (AbstractFileSystem, BaseStorageOptions, get_protocol,
                  get_storage_options_and_fs)
from ..utils.callback import run_with_callback
from ..utils.logging import setup_logging
from .registry import PipelineRegistry
from .runner import run_pipeline
from .visualizer import PipelineVisualizer


class Pipeline:
    """The Pipeline class represents a data processing pipeline.
    It is used to manage the configuration and execution of the pipeline."""

    def __init__(
        self,
        name: str | None = None,
        base_dir: str | None = None,
        storage_options: BaseStorageOptions | dict | None = None,
        fs: AbstractFileSystem | None = None,
        cfg_dir: str | None = None,
        pipelines_dir: str | None = None,
        log_level: str | None = None,
        # cfg: PipelineConfig | None = None,
        # project_cfg: ProjectConfig | None = None,
    ):
        """Initialize the Pipeline with configuration parameters.

        Args:
            name (str, optional): Name of the pipeline.
            base_dir (str, optional): Base directory for the pipeline.
            storage_options (BaseStorageOptions | dict, optional): Storage options for the filesystem.
            fs (AbstractFileSystem, optional): Filesystem instance.
            cfg_dir (str, optional): Directory for configuration files.
            pipelines_dir (str, optional): Directory for pipeline files.
            log_level (str, optional): Logging level.
        """
        if log_level:
            setup_logging(log_level or settings.LOG_LEVEL)

        self.name = name
        self._base_dir = base_dir or str(Path.cwd())
        self._cfg_dir = cfg_dir or settings.CONFIG_DIR
        self._pipelines_dir = pipelines_dir or settings.PIPELINES_DIR
        self._run_func = None
        self._on_success = None
        self._on_failure = None
        cached = (
            True
            if storage_options is not None or get_protocol(self._base_dir) != "file"
            else False
        )
        self._fs, _ = get_storage_options_and_fs(
            base_dir=self._base_dir,
            storage_options=storage_options,
            fs=fs,
            cached=cached,
        )

        # Store provided configs if given
        # self.cfg = cfg
        # self.project_cfg = project_cfg
        self._cfg, self._adapter_cfg = self._load_config()
        self._add_modules_path()

    def __enter__(self) -> "Pipeline":
        """Enter the context manager.

        Enables use of the manager in a with statement for automatic resource cleanup.

        Returns:
            Pipeline: Self for use in context manager.

        Example:
            >>> from flowerpower.pipeline import Pipeline
            >>>
            >>> with Pipeline("my_pipeline") as pipeline:
            ...     result = pipeline.run(inputs={"date": "2025-04-28"})
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
            >>> with Pipeline("my_pipeline") as pipeline:
            ...     # Run the pipeline
            ...     result = pipeline.run(inputs={"date": "2025-04-28"})

        Raises:
            RuntimeError: If an error occurs during pipeline execution.
        """
        # Add cleanup code if needed
        pass

    def _load_config(self):
        """Load the pipeline configuration from the filesystem."""
        if not self.name:
            raise ValueError("Pipeline name must be set to load configuration.")
        if hasattr(self, "_cfg"):
            return self._cfg, self._adapter_cfg
        # Load project configuration
        project_cfg = ProjectConfig.load(base_dir=self._base_dir, fs=self._fs)
        self._project_name = project_cfg.name
        project_adapter_cfg = project_cfg.adapter

        # Load pipeline-specific configuration
        self._cfg = PipelineConfig.load(name=self.name, fs=self._fs)

        self._adapter_cfg = AdapterConfig.from_adapters(
            project_hamilton_tracker_cfg=project_adapter_cfg.hamilton_tracker,
            pipeline_hamilton_tracker_cfg=self._cfg.adapter.hamilton_tracker,
            project_mlflow_cfg=project_adapter_cfg.mlflow,
            pipeline_mlflow_cfg=self._cfg.adapter.mlflow,
            ray_cfg=project_adapter_cfg.ray,
            opentelemetry_cfg=project_adapter_cfg.opentelemetry,
        )
        return self._cfg, self._adapter_cfg

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

    @property
    def cfg(self) -> PipelineConfig:
        """Get the pipeline configuration."""
        if not hasattr(self, "_cfg"):
            self._load_config()
        return self._cfg

    @property
    def adapter_cfg(self) -> AdapterConfig:
        """Get the adapter configuration."""
        if not hasattr(self, "_adapter_cfg"):
            self._load_config()
        return self._adapter_cfg

    def _get_run_func(
        self,
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
            self._run_func is None
            or reload
            or on_success != self._on_success
            or on_failure != self._on_failure
        ):
            # run_pipeline_ = partial(run_pipeline, project_cfg=self.project_cfg, pipeline_cfg=self._pipeline_cfg)
            self._run_func = run_with_callback(
                on_success=on_success, on_failure=on_failure
            )(run_pipeline)
            return self._run_func

        return self._run_func

    def run(
        self,
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
        """Run the pipeline with the given configuration.

        Args:
            inputs (dict[str, Any], optional): Input data for the pipeline.
            final_vars (set[str], optional): Variables to return after execution.
            run_config (dict[str, Any], optional): Configuration for the run.
            cache (dict[str, Any], optional): Cache for intermediate results.
            executor (str | dict[str, Any] | ExecutorConfig, optional): Executor configuration.
            with_adapter (dict[str, Any] | WithAdapterConfig, optional): Adapter configuration.
            retry (dict[str, Any] | RetryConfig, optional): Retry configuration.
            adapter_cfg (dict[str, Any], optional): Adapter configuration dictionary.
            hamilton_adapters (dict[str, Any], optional): Hamilton adapters configuration.
            log_level (str, optional): Logging level for this run.
            on_success (Callable | tuple[Callable, tuple | None, dict | None], optional): Callback on success.
            on_failure (Callable | tuple[Callable, tuple | None, dict | None], optional): Callback on failure.

        Returns:
            dict[str, Any]: Results of the pipeline execution.
        """
        # pipeline_cfg = self._load_pipeline_cfg(name=name, reload=reload)
        run_func = self._get_run_func(
            reload=reload, on_success=on_success, on_failure=on_failure
        )

        res = run_func(
            project_name=self._project_name,
            pipeline_cfg=self.cfg,
            inputs=inputs,
            final_vars=final_vars,
            config=run_config,
            cache=cache,
            executor=executor,
            with_adapter=with_adapter,
            adapter_cfg=adapter_cfg,
            hamilton_adapters=hamilton_adapters,
            log_level=log_level,
            retry=retry,
        )

        return res

    def get_summary(self, code: bool = True, cfg: bool = True) -> dict[str, dict | str]:
        """Get a summary of the pipeline configuration and code.

        Args:
            code (bool): Whether to include code in the summary.
            cfg (bool): Whether to include configuration in the summary.

        Returns:
            dict[str, dict | str]: Summary containing code and configuration.
        """
        with PipelineRegistry(
            project_name=self._project_name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            return registry.get_summary(
                name=self.name, code=code, cfg=cfg, project=False
            )

    def show_summary(
        self,
        code: bool = True,
        cfg: bool = True,
        to_html: bool = False,
        to_svg: bool = False,
    ) -> None | str:
        """Display a summary of the pipeline configuration and code.

        Args:
            code (bool): Whether to include code in the summary.
            cfg (bool): Whether to include configuration in the summary.
            to_html (bool): Whether to convert the summary to HTML.
            to_svg (bool): Whether to convert the summary to SVG.
        """
        with PipelineRegistry(
            project_name=self._project_name,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        ) as registry:
            return registry.show_summary(
                name=self.name,
                code=code,
                cfg=cfg,
                project=False,
                to_html=to_html,
                to_svg=to_svg,
            )

    @property
    def summary(self) -> dict[str, dict | str]:
        """Get a summary of the pipeline configuration and code."""
        return self.get_summary(code=True, cfg=True)

    def save_dag(
        self,
        format: str = "png",
        reload: bool = False,
    ) -> None:
        """Save the directed acyclic graph (DAG) of the pipeline to a file.

        Args:
            format (str): The format of the graph file. Defaults to "png".
            reload (bool): Whether to reload the pipeline data. Defaults to False.

        Raises:
            ImportError: If the graphviz module cannot be loaded.
        """
        with PipelineVisualizer(
            project_name=self._project_name,
            base_dir=self._base_dir,
            fs=self._fs,
        ) as visualizer:
            visualizer.save_dag(name=self.name, format=format, reload=reload)

    def show_dag(
        self,
        format: str = "png",
        reload: bool = False,
        raw: bool = False,
    ) -> None | str:
        """Display the directed acyclic graph (DAG) of the pipeline.

        Args:
            format (str): The format of the graph file. Defaults to "png".
            reload (bool): Whether to reload the pipeline data. Defaults to False.
            raw (bool): Whether to return the raw graph object instead of rendering it.

        Returns:
            None | str: If raw is True, returns the raw graph object; otherwise, displays the graph.
        """
        with PipelineVisualizer(
            project_name=self._project_name,
            base_dir=self._base_dir,
            fs=self._fs,
        ) as visualizer:
            return visualizer.show_dag(
                name=self.name, format=format, reload=reload, raw=raw
            )
