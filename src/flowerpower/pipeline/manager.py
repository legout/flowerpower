import datetime as dt
import importlib
import importlib.util
import posixpath
import sys
from typing import Any

from hamilton import driver

from ..fs import AbstractFileSystem
from .io import PipelineIOManager  # Add import for PipelineIOManager

# Import the new registry class
from .registry import PipelineRegistry
from .runner import PipelineRunner  # Add import for PipelineRunner
from .scheduler import PipelineScheduler  # Add import for PipelineScheduler
from .visualizer import PipelineVisualizer  # Add import for PipelineVisualizer

if importlib.util.find_spec("opentelemetry"):
    from hamilton.plugins import h_opentelemetry

    from ..utils.open_telemetry import init_tracer

else:
    h_opentelemetry = None
    init_tracer = None
import rich
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from ..cfg import Config
from ..fs import get_filesystem
from ..fs.storage_options import BaseStorageOptions

# Keep conditional import for opentelemetry and other plugins
if importlib.util.find_spec("opentelemetry"):
    # ... (rest of conditional imports remain the same)
    pass  # Placeholder, original code follows

# Remove the old SchedulerManager logic
# SchedulerManager = None # Removed
from pathlib import Path
from types import TracebackType
from uuid import UUID

from munch import Munch


class PipelineManager:
    def __init__(
        self,
        base_dir: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions = {},
        fs: AbstractFileSystem | None = None,
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        telemetry: bool = False,
        worker_type: str | None = None,  # New parameter for worker backend
    ):
        """
        Initializes the Pipeline object.

        Args:
            base_dir (str | None): The flowerpower base path. Defaults to None.
            storage_options (dict | Munch | BaseStorageOptions, optional): The storage options. Defaults to {}.
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.
            cfg_dir (str, optional): The configuration directory. Defaults to "conf".
            pipelines_dir (str, optional): The pipelines directory. Defaults to "pipelines".
            telemetry (bool, optional): Whether to enable hamilton telemetry. Defaults to False.
            worker_type (str | None, optional): The type of worker to use. If None, the worker type from the project config
                will be used. Defaults to None.

        Returns:
            None
        """
        self._telemetry = telemetry
        self._base_dir = base_dir or str(Path.cwd())
        self._storage_options = storage_options or {}
        if fs is None:
            fs = get_filesystem(self._base_dir, **self._storage_options)
        self._fs = fs

        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        # Store worker_type

        try:
            self._fs.makedirs(f"{self._cfg_dir}/pipelines", exist_ok=True)
            self._fs.makedirs(self._pipelines_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")

        self._sync_fs()
        self.load_config()  # Initial load for project config

        self._worker_type = worker_type or self.cfg.project.worker.type

        # Instantiate the PipelineRegistry
        self._registry = PipelineRegistry(
            fs=self._fs,
            base_dir=self._base_dir,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
            load_config_func=self.load_config,  # Pass the method itself
        )

        # Instantiate the PipelineRunner
        self._runner = PipelineRunner(
            fs=self._fs,
            base_dir=self._base_dir,
            pipelines_dir=self._pipelines_dir,
            telemetry=self._telemetry,
            load_config_func=self.load_config,  # Pass the method
            load_module_func=self.load_module,  # Pass the method
            # Use lambda to access cfg after it's loaded
            get_project_name_func=lambda: self.cfg.project.name
            if hasattr(self, "cfg") and self.cfg
            else "unknown_project",
        )

        # Instantiate the PipelineScheduler
        self._scheduler = PipelineScheduler(
            fs=self._fs,
            base_dir=self._base_dir,
            storage_options=self._storage_options,
            worker_type=self._worker_type,
            load_config_func=self.load_config,  # Pass the method
            get_project_name_func=lambda: self.cfg.project.name
            if hasattr(self, "cfg") and self.cfg
            else "unknown_project",  # Pass lambda
            get_pipeline_run_func=self._runner.run,  # Pass the runner's run method
            get_registry_func=lambda: self._registry,  # Pass lambda to get registry
        )

        # Instantiate the PipelineIOManager
        self._io_manager = PipelineIOManager(
            fs=self._fs,
            registry=self._registry,  # Pass registry instance
        )

        # Helper function for basic driver builder needed by visualizer
        def get_base_driver_builder(module, config):
            # Basic builder needed for visualization
            return (
                driver.Builder()
                .enable_dynamic_execution(allow_experimental_mode=True)
                .with_modules(module)
                .with_config(config)
                # No adapters or complex executors needed for display_all_functions
            )

        # Instantiate the PipelineVisualizer
        self._visualizer = PipelineVisualizer(
            fs=self._fs,
            base_dir=self._base_dir,
            load_config_func=self.load_config,  # Pass the method
            load_module_func=self.load_module,  # Pass the method
            get_driver_builder_func=get_base_driver_builder,  # Pass the helper function
        )

    def __enter__(self) -> "PipelineManager":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # Add any cleanup code here if needed
        pass

    # _get_schedules method removed, moved to PipelineScheduler
    def _sync_fs(self):
        """
        Sync the filesystem.

        Returns:
            None
        """
        if self._fs.is_cache_fs:
            self._fs.sync()

        modules_path = posixpath.join(self._fs.path, self._pipelines_dir)
        if modules_path not in sys.path:
            sys.path.append(modules_path)

    def load_module(self, name: str, reload: bool = False):
        """
        Load a module dynamically.

        Args:
            name (str): The name of the module to load.

        Returns:
            None
        """
        sys.path.append(posixpath.join(self._fs.path, self._pipelines_dir))

        if not hasattr(self, "_module"):
            self._module = importlib.import_module(name)

        else:
            if reload:
                importlib.reload(self._module)

        return self._module

    def load_config(self, name: str | None = None, reload: bool = False) -> Config:
        """
        Load the configuration file.

        This method loads the configuration file specified by the `_cfg_dir` attribute and
        assigns it to the `cfg` attribute.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.

        Returns:
            None
        """
        if reload:
            del self.cfg
            self.cfg = Config.load(
                base_dir=self._base_dir, pipeline_name=name, fs=self._fs
            )
            return self.cfg

        self.cfg = Config.load(base_dir=self._base_dir, pipeline_name=name, fs=self._fs)

        return self.cfg

    # _get_driver method removed, moved to PipelineRunner

    # _resolve_parameters method removed, moved to PipelineRunner

    # worker property removed, moved to PipelineScheduler

    def run(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,  # Driver config
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        reload: bool = False,
        **kwargs,  # Pass tracker/otel specific args here
    ) -> dict[str, Any]:
        """
        Run the pipeline by delegating to the PipelineRunner.

        Args:
            name (str): The name of the pipeline.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            config (dict | None): Hamilton driver config.
            executor (str | None): Executor for the pipeline run.
            with_tracker (bool | None): Enable tracker.
            with_opentelemetry (bool | None): Enable OpenTelemetry.
            with_progressbar (bool | None): Enable progress bar.
            reload (bool): Whether to reload the pipeline config and module. Defaults to False.
            **kwargs: Additional keyword arguments passed to the runner (e.g., project_id, otel_host).

        Returns:
            dict[str,Any]: The result of executing the pipeline.
        """
        # Delegate the execution to the PipelineRunner instance
        # Pass all arguments through
        return self._runner.run(
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
            reload=reload,
            **kwargs,
        )

    # --- Delegate job submission to PipelineScheduler ---
    def run_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        reload: bool = False,
        # worker_type: str | None = None, # Override not directly supported here anymore
        **kwargs,
    ) -> str:
        """
        Submit an immediate job run via the PipelineScheduler.

        Args:
            name (str): The name of the pipeline.
            inputs (dict | None): Inputs for the pipeline run.
            final_vars (list | None): Final variables for the pipeline run.
            config (dict | None): Hamilton driver config.
            executor (str | None): Executor for the pipeline run.
            with_tracker (bool | None): Enable tracker.
            with_opentelemetry (bool | None): Enable OpenTelemetry.
            with_progressbar (bool | None): Enable progress bar.
            reload (bool): Whether to reload the pipeline module. Defaults to False.
            **kwargs: Additional keyword arguments passed to the scheduler's run_job method.

        Returns:
            str: The ID of the submitted job.
        """
        # Delegate to the PipelineScheduler instance
        return self._scheduler.run_job(
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
            reload=reload,
            **kwargs,
        )

    def add_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        reload: bool = False,
        result_ttl: float | dt.timedelta = 0,
        # worker_type: str | None = None, # Override not directly supported here anymore
        **kwargs,
    ) -> UUID:  # Return type should be UUID as per scheduler's add_job
        """
        Submit an immediate job run with result storage via the PipelineScheduler.

        Args:
            name (str): The name of the pipeline.
            inputs (dict | None): Inputs for the pipeline run.
            final_vars (list | None): Final variables for the pipeline run.
            config (dict | None): Hamilton driver config.
            executor (str | None): Executor for the pipeline run.
            with_tracker (bool | None): Enable tracker.
            with_opentelemetry (bool | None): Enable OpenTelemetry.
            with_progressbar (bool | None): Enable progress bar.
            reload (bool): Whether to reload the pipeline module. Defaults to False.
            result_ttl (float | dt.timedelta): How long the job result should be stored.
                Defaults to 0 (don't store).
            **kwargs: Additional keyword arguments passed to the scheduler's add_job method.

        Returns:
            UUID: The ID of the submitted job.
        """

        return self._scheduler.add_job(
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
            reload=reload,
            result_ttl=result_ttl,
            **kwargs,
        )

    # --- End Delegate job submission ---

    def schedule(self, name: str, **kwargs) -> str:
        """
        Schedule a pipeline by delegating to the PipelineScheduler.

        Args:
            name (str): The name of the pipeline.
            **kwargs: Arguments passed directly to PipelineScheduler.schedule.
                      See PipelineScheduler.schedule for detailed arguments.

        Returns:
            str: The ID of the scheduled pipeline.
        """
        # Delegate the scheduling to the PipelineScheduler instance
        return self._scheduler.schedule(name=name, **kwargs)

    def schedule_all(self, **kwargs):
        """
        Schedule all pipelines by delegating to the PipelineScheduler.

        Args:
            **kwargs: Arguments passed directly to PipelineScheduler.schedule_all.
                      See PipelineScheduler.schedule_all for details.
        """
        # Delegate scheduling all pipelines to the PipelineScheduler instance
        self._scheduler.schedule_all(**kwargs)

    def new(
        self,
        name: str,
        overwrite: bool = False,
    ):
        """
        Adds a pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool): Whether to overwrite an existing pipeline. Defaults to False.
            worker_type (str | None): The type of worker to use. Defaults to None.

        Raises:
            ValueError: If the configuration or pipeline path does not exist, or if the pipeline already exists.

        Examples:
            pm = PipelineManager()
            pm.new("my_pipeline")
        """
        self._registry.new(
            name=name,
            overwrite=overwrite,
        )

    # --- Delegate Methods for IO Manager ---

    def import_pipeline(
        self,
        name: str,
        base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Delegates importing a pipeline to the PipelineIOManager."""
        # Note: The original method had different args (cfg_dir, pipelines_dir, fs).
        # The new IOManager method takes these from its __init__.
        # We pass only the arguments relevant to the *delegated* call.
        return self._io_manager.import_pipeline(
            name=name, base_dir=base_dir, src_fs=src_fs, storage_options=storage_options, overwrite=overwrite
        )

    def import_many(
        self,
        pipelines: dict[str, str] | list[str],
        base_dir: str | None = None,
        src_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Delegates importing multiple pipelines to the PipelineIOManager."""
        # Note: The original method had different args (names, path, cfg_dir, etc.).
        # The new IOManager method takes a dict {name: path}.
        return self._io_manager.import_many(
            pipelines=pipelines, base_dir=base_dir, src_fs=src_fs, storage_options=storage_options, overwrite=overwrite
        )

    def import_all(
        self,
        base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Delegates importing all pipelines to the PipelineIOManager."""
        return self._io_manager.import_all(
           base_dir=base_dir, src_fs=src_fs, storage_options=storage_options, overwrite=overwrite
        )

    def export_pipeline(
        self,
        name: str,
        base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Delegates exporting a pipeline to the PipelineIOManager."""
        return self._io_manager.export_pipeline(
            name=name, base_dir=base_dir, dest_fs=dest_fs, storage_options=storage_options, overwrite=overwrite
        )

    def export_many(
        self,
        pipelines: list[str],
        base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Delegates exporting multiple pipelines to the PipelineIOManager."""
        return self._io_manager.export_many(
            pipelines=pipelines, base_dir=base_dir, dest_fs=dest_fs, storage_options=storage_options, overwrite=overwrite
        )

    def export_all(
        self,
        base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Delegates exporting all pipelines to the PipelineIOManager."""
        return self._io_manager.export_all(
            base_dir=base_dir, dest_fs=dest_fs, storage_options=storage_options, overwrite=overwrite
        )

    # --- End Delegate Methods ---

    def delete(self, name: str, cfg: bool = True, module: bool = False):
        """
        Delete a pipeline.

        Args:
            name (str): The name of the pipeline to delete.
            cfg (bool, optional): Whether to delete the pipeline configuration. Defaults to True.
            module (bool, optional): Whether to delete the pipeline module file. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            pm.delete("my_pipeline")
            ```
        """

        if cfg:
            if self._fs.exists(f"{self._cfg_dir}/pipelines/{name}.yml"):
                self._fs.rm(f"{self._cfg_dir}/pipelines/{name}.yml")
                rich.print(f"🗑️ Deleted pipeline config for {name}")

        if module:
            if self._fs.exists(f"{self._pipelines_dir}/{name}.py"):
                self._fs.rm(f"{self._pipelines_dir}/{name}.py")
                rich.print(
                    f"🗑️ Deleted pipeline config for {self.cfg.project.name}.{name}"
                )

    # --- Delegate Methods for Visualization ---

    def save_dag(self, name: str, format: str = "png", reload: bool = False):
        """Delegates saving the DAG image to the PipelineVisualizer."""
        self._visualizer.save_dag(name=name, format=format, reload=reload)

    def show_dag(
        self, name: str, format: str = "png", reload: bool = False, raw: bool = False
    ):
        """Delegates displaying or returning the DAG object to the PipelineVisualizer."""
        return self._visualizer.show_dag(
            name=name, format=format, reload=reload, raw=raw
        )

    # --- Delegate Methods for Registry ---

    def get_summary(
        self, name: str, reload: bool = False, rich_render: bool = False
    ) -> dict[str, Any] | Table:
        """Gets the summary of a pipeline by delegating to the registry."""
        # The registry's get_summary now uses the load_config_func passed during init
        return self._registry.get_summary(
            name=name, reload=reload, rich_render=rich_render
        )

    def show_summary(
        self,
        name: str,
        reload: bool = False,
        show_code: bool = False,
        show_dag: bool = False,  # Keep show_dag here as it needs driver
        max_lines: int | None = None,
    ) -> None:
        """Shows the summary of a pipeline by delegating display logic."""
        # Delegate core summary display (config, code)
        self._registry.show_summary(
            name=name, reload=reload, show_code=show_code, max_lines=max_lines
        )

    @property
    def schedules(self) -> list[str]:
        """Gets the schedules by delegating to the scheduler."""
        return self._scheduler.schedules

    @property
    def pipelines(self) -> list[str]:
        """Gets the pipelines by delegating to the registry."""
        return self._registry.pipelines
    
    @property
    def summary(self):
        """Gets the summary of the pipeline manager."""
        return self._registry.summary
