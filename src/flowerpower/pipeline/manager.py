import datetime as dt
import importlib
import importlib.util
import posixpath
import sys
from pathlib import Path
from types import TracebackType
from typing import Any, Callable  # Added Callable
from uuid import UUID

from loguru import logger
from munch import Munch
from rich.table import Table  # Keep Table for get_summary return type hint

from .. import settings
from ..cfg import PipelineConfig, ProjectConfig
from ..cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from ..cfg.pipeline.run import ExecutorConfig, WithAdapterConfig
from ..cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from ..fs import AbstractFileSystem, BaseStorageOptions, get_filesystem
from ..utils.logging import setup_logging
from .io import PipelineIOManager
from .registry import PipelineRegistry
from .runner import PipelineRunner
from .scheduler import PipelineScheduler
from .visualizer import PipelineVisualizer

# Conditional imports can be removed if not directly used by PipelineManager itself
# if importlib.util.find_spec("opentelemetry"): ...


setup_logging()


class PipelineManager:
    """
    Central manager for FlowerPower pipelines.

    Handles configuration loading, pipeline discovery, execution (via Runner),
    scheduling (via Scheduler), visualization (via Visualizer), and import/export (via IOManager).
    """

    def __init__(
        self,
        base_dir: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions | None = None,
        fs: AbstractFileSystem | None = None,
        cfg_dir: str | None = None,
        pipelines_dir: str | None = None,
        worker_type: str | None = None,  # Explicit worker type override
        log_level: str | None = None,
    ):
        """
        Initializes the PipelineManager.

        Args:
            base_dir (str | None): The FlowerPower base path. Defaults to CWD.
            storage_options (dict | Munch | BaseStorageOptions | None): Storage options. Defaults to {}.
            fs (AbstractFileSystem | None): Pre-configured fsspec filesystem. Defaults to auto-detection based on base_dir.
            cfg_dir (str | None): Override default configuration directory ('conf').
            pipelines_dir (str | None): Override default pipelines directory ('pipelines').
            worker_type (str | None): Override the worker type defined in project config or settings.
            log_level (str | None): Logging level for the manager. Defaults to None (uses project config or settings).
        """
        if log_level:
            setup_logging(level=log_level)

        self._base_dir = base_dir or str(Path.cwd())
        self._storage_options = storage_options
        if not fs:
            fs = get_filesystem(self._base_dir, storage_options=storage_options)
        self._fs = fs

        # Store overrides for ProjectConfig loading
        self._cfg_dir = cfg_dir or settings.CONFIG_DIR
        self._pipelines_dir = pipelines_dir or settings.PIPELINES_DIR
        self._worker_type = worker_type

        self._load_project_cfg(reload=True)  # Load project config

        # Ensure essential directories exist (using paths from loaded project_cfg)
        try:
            self._fs.makedirs(self._cfg_dir, exist_ok=True)
            self._fs.makedirs(self._pipelines_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating essential directories: {e}")
            # Consider raising an error here depending on desired behavior
        
        # Sync cache if applicable
        self._sync_cache()
        # Ensure pipeline modules can be imported
        self._append_modules_path()

        # Instantiate components using the loaded project config
        self.registry = PipelineRegistry(
            project_cfg=self.project_cfg,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )
        self.scheduler = PipelineScheduler(
            project_cfg=self.project_cfg,
            fs=self._fs,
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
            worker_type=self._worker_type,
        )
        self.visualizer = PipelineVisualizer(project_cfg=self.project_cfg, fs=self._fs)
        self.io = PipelineIOManager(registry=self.registry)

        self._current_pipeline_name: str | None = None
        self._pipeline_cfg: PipelineConfig | None = None
        

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
    def _sync_cache(self):
        """
        Sync the filesystem.

        Returns:
            None
        """
        # Use fs from project_cfg
        if self._fs.is_cache_fs:
            self._fs.sync_cache()

    def _append_modules_path(self):
        """
        Append the modules path to sys.path.
        This is necessary for dynamic module loading.
        Returns:
            None
        """
        # Use paths from project_cfg
        # Note: fs.path might not be reliable for all filesystems (e.g., S3)
        # Using the derived pipelines_dir relative to base_dir is safer.
        # However, for sys.path, we often need the *local* path if using CacheFileSystem.
        local_pipelines_path = posixpath.join(self._base_dir, self._pipelines_dir)
        if local_pipelines_path not in sys.path:
            # Add the potentially cached local path
            sys.path.append(local_pipelines_path)
            logger.debug(f"Appended {local_pipelines_path} to sys.path")
        # Also add the base directory itself, as pipelines might import from src
        if self._base_dir not in sys.path:
            sys.path.insert(0, self._base_dir)  # Insert at beginning
            logger.debug(f"Inserted {self._base_dir} into sys.path")

    def _load_project_cfg(self, reload: bool = False) -> ProjectConfig:
        """
        Load the project configuration.

        Returns:
            ProjectConfig: The loaded project configuration.
        """
        if hasattr(self, "_project_cfg") and not reload:
            return self._project_cfg

        # Pass overrides to ProjectConfig.load
        self._project_cfg = ProjectConfig.load(
            base_dir=self._base_dir,
            worker_type=self._worker_type,
            fs=self._fs,  # Pass pre-configured fs if provided
            storage_options=self._storage_options,
        )
        # Update internal fs reference in case ProjectConfig loaded/created one
        return self._project_cfg

    def _load_pipeline_cfg(self, name: str, reload: bool = False) -> PipelineConfig:
        """
        Load the pipeline configuration.

        Args:
            name (str): The name of the pipeline.

        Returns:
            PipelineConfig: The loaded pipeline configuration.
        """
        if name == self._current_pipeline_name and not reload:
            return self._pipeline_cfg

        self._current_pipeline_name = name
        # Use project_cfg attributes for loading pipeline config
        self._pipeline_cfg = PipelineConfig.load(
            base_dir=self._base_dir,
            name=name,
            fs=self._fs,
            storage_options=self._storage_options,
            # cfg_dir is implicitly handled by PipelineConfig.load using base_dir
        )
        return self._pipeline_cfg

    @property
    def current_pipeline_name(self) -> str:
        """
        Get the name of the current pipeline.

        Returns:
            str: The name of the current pipeline.
        """
        return self._current_pipeline_name

    @property
    def project_cfg(self) -> ProjectConfig:
        """
        Get the project configuration object.

        Returns:
            ProjectConfig: The project configuration object.
        """
        if not hasattr(self, "_project_cfg"):
            self._load_project_cfg()
        return self._project_cfg

    @property
    def pipeline_cfg(self) -> PipelineConfig:
        """
        Get the pipeline configuration object.

        Returns:
            PipelineConfig: The pipeline configuration object.
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
    ) -> dict[str, Any]:
        """
        Run a pipeline synchronously using PipelineRunner.

        Args:
            name (str): The name of the pipeline.
            inputs (dict | None): Inputs for the pipeline run (overrides config).
            final_vars (list | None): Final variables for the pipeline run (overrides config).
            config (dict | None): Hamilton driver config (overrides config).
            cache (dict | None): Cache configuration (overrides config).
            executor_cfg (... | None): Executor config (overrides config).
            with_adapter_cfg (... | None): Adapter enablement config (overrides config).
            pipeline_adapter_cfg (... | None): Pipeline adapter settings (overrides config).
            project_adapter_cfg (... | None): Project adapter settings (overrides config).
            adapter (dict | None): Additional Hamilton adapters (overrides config).
            reload (bool): Whether to reload module and pipeline config. Defaults to False.
            log_level (str | None): Log level for the run (overrides config).

        Returns:
            dict[str, Any]: The result of executing the pipeline.
        """
        pipeline_cfg = self._load_pipeline_cfg(name=name, reload=reload)

        # Instantiate PipelineRunner for this specific run
        with PipelineRunner(
            project_cfg=self.project_cfg, pipeline_cfg=pipeline_cfg
        ) as runner:
            # Delegate execution, passing all relevant arguments
            res = runner.run(
                inputs=inputs,
                final_vars=final_vars,
                config=config,
                cache=cache,
                executor_cfg=executor_cfg,
                with_adapter_cfg=with_adapter_cfg,
                pipeline_adapter_cfg=pipeline_adapter_cfg,
                project_adapter_cfg=project_adapter_cfg,
                adapter=adapter,
                reload=reload,  # Runner handles module reload if needed
                log_level=log_level,
            )
        return res

    # --- Delegated Methods ---

    # Registry Delegations
    def new(self, name: str, overwrite: bool = False):
        """Adds a new pipeline structure (config and module file)."""
        return self.registry.new(name=name, overwrite=overwrite)

    def delete(self, name: str, cfg: bool = True, module: bool = False):
        """Deletes pipeline files (config and/or module)."""
        return self.registry.delete(name=name, cfg=cfg, module=module)

    def get_summary(
        self,
        name: str | None = None,
        cfg: bool = True,
        code: bool = True,
        project: bool = True,
    ) -> dict[str, dict | str]:
        """Gets a summary dictionary of project/pipeline config and code."""
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
        """Prints a formatted summary of project/pipeline config and code."""
        return self.registry.show_summary(
            name=name,
            cfg=cfg,
            code=code,
            project=project,
            to_html=to_html,
            to_svg=to_svg,
        )

    def show_pipelines(self) -> None:
        """Prints a table of available pipelines."""
        return self.registry.show_pipelines()

    def list_pipelines(self) -> list[str]:
        """Returns a list of available pipeline names."""
        return self.registry.list_pipelines()

    @property
    def pipelines(self) -> list[str]:
        """Gets the list of available pipeline names."""
        return self.registry.pipelines

    @property
    def summary(self) -> dict[str, dict | str]:
        """Gets the summary dictionary for all pipelines."""
        return self.registry.summary

    # IO Delegations
    def import_pipeline(
        self,
        name: str,
        base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Imports a pipeline from a source directory."""
        return self.io.import_pipeline(
            name=name,
            src_base_dir=base_dir,
            src_fs=src_fs,
            src_storage_options=storage_options,
            overwrite=overwrite,
        )

    def import_many(
        self,
        pipelines: dict[str, str] | list[str],
        base_dir: str,  # Base dir for source if pipelines is a list
        src_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Imports multiple pipelines."""
        return self.io.import_many(
            pipelines=pipelines,
            src_base_dir=base_dir,
            src_fs=src_fs,
            src_storage_options=storage_options,
            overwrite=overwrite,
        )

    def import_all(
        self,
        base_dir: str,
        src_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Imports all pipelines found in a source directory."""
        return self.io.import_all(
            src_base_dir=base_dir,
            src_fs=src_fs,
            src_storage_options=storage_options,
            overwrite=overwrite,
        )

    def export_pipeline(
        self,
        name: str,
        base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Exports a single pipeline to a destination directory."""
        return self.io.export_pipeline(
            name=name,
            dest_base_dir=base_dir,
            dest_fs=dest_fs,
            des_storage_options=storage_options,
            overwrite=overwrite,
        )

    def export_many(
        self,
        pipelines: list[str],
        base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Exports multiple specified pipelines."""
        return self.io.export_many(
            pipelines=pipelines,
            dest_base_dir=base_dir,
            dest_fs=dest_fs,
            dest_storage_options=storage_options,
            overwrite=overwrite,
        )

    def export_all(
        self,
        base_dir: str,
        dest_fs: AbstractFileSystem | None = None,
        storage_options: BaseStorageOptions | None = None,
        overwrite: bool = False,
    ):
        """Exports all pipelines found in the registry."""
        return self.io.export_all(
            dest_base_dir=base_dir,
            dest_fs=dest_fs,
            dest_storage_options=storage_options,
            overwrite=overwrite,
        )

    # Visualizer Delegations
    def save_dag(self, name: str, format: str = "png", reload: bool = False):
        """Saves the DAG visualization of a pipeline to a file."""
        # Reload might be needed if code changed since manager init
        return self.visualizer.save_dag(name=name, format=format, reload=reload)

    def show_dag(
        self, name: str, format: str = "png", reload: bool = False, raw: bool = False
    ):
        """Displays or returns the DAG visualization object for a pipeline."""
        # Reload might be needed
        return self.visualizer.show_dag(
            name=name, format=format, reload=reload, raw=raw
        )

    # Scheduler Delegations
    def _get_run_func_for_job(self, name: str, reload: bool = False) -> Callable:
        """Helper to create a PipelineRunner instance and return its run method."""
        # This ensures the runner uses the correct, potentially reloaded, config for the job
        pipeline_cfg = self._load_pipeline_cfg(name=name, reload=reload)
        runner = PipelineRunner(project_cfg=self.project_cfg, pipeline_cfg=pipeline_cfg)
        # We return the bound method runner.run
        return runner.run

    def run_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list[str] | None = None,
        config: dict | None = None,
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,  # Reload config/module before creating run_func
        log_level: str | None = None,
        **kwargs,  # Worker specific args
    ) -> str | UUID:
        """Submits an immediate job run via the PipelineScheduler."""
        run_func = self._get_run_func_for_job(name, reload)
        return self.scheduler.run_job(
            run_func=run_func,
            name=name,  # Pass name for logging in scheduler
            # Pass run parameters
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor_cfg=executor_cfg,
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            adapter=adapter,
            reload=reload,  # Note: reload already happened in _get_run_func_for_job
            log_level=log_level,
            **kwargs,  # Pass worker args
        )

    def add_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list[str] | None = None,
        config: dict | None = None,
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,  # Reload config/module before creating run_func
        log_level: str | None = None,
        result_ttl: float | dt.timedelta = 0,
        **kwargs,  # Worker specific args
    ) -> str | UUID:
        """Submits an immediate job run with result storage via the PipelineScheduler."""
        run_func = self._get_run_func_for_job(name, reload)
        return self.scheduler.add_job(
            run_func=run_func,
            name=name,  # Pass name for logging
            # Pass run parameters
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor_cfg=executor_cfg,
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            adapter=adapter,
            reload=reload,  # Note: reload already happened
            log_level=log_level,
            # Pass scheduler-specific args
            result_ttl=result_ttl,
            **kwargs,  # Pass worker args
        )

    def schedule(
        self,
        name: str,
        # --- Run Parameters (passed to run_func) ---
        inputs: dict | None = None,
        final_vars: list[str] | None = None,
        config: dict | None = None,  # Driver config
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | PipelineAdapterConfig | None = None,
        project_adapter_cfg: dict | ProjectAdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,  # Reload config/module before creating run_func for schedule
        log_level: str | None = None,
        # --- Schedule Parameters (passed to worker.add_schedule) ---
        trigger_type: str | None = None,
        id_: str | None = None,
        paused: bool | None = None,
        coalesce: str | None = None,
        misfire_grace_time: float | dt.timedelta | None = None,
        max_jitter: float | dt.timedelta | None = None,
        max_running_jobs: int | None = None,
        conflict_policy: str | None = None,
        overwrite: bool = False,
        # --- Trigger Parameters ---
        **kwargs,  # Trigger specific args + any other worker args
    ) -> str | UUID:
        """Schedules a pipeline run via the PipelineScheduler."""
        # Need the specific pipeline's config to resolve defaults for the schedule call
        pipeline_cfg = self._load_pipeline_cfg(name=name, reload=reload)
        # Create the run function *now* with potentially reloaded config/module
        run_func = self._get_run_func_for_job(
            name, reload=False
        )  # Reload already done above

        return self.scheduler.schedule(
            run_func=run_func,
            pipeline_cfg=pipeline_cfg,  # Pass config for default resolution
            # Pass run parameters (overrides)
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor_cfg=executor_cfg,
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            adapter=adapter,
            reload=reload,  # Pass reload flag (though effect happened in run_func creation)
            log_level=log_level,
            # Pass schedule parameters (overrides)
            trigger_type=trigger_type,
            id_=id_,
            paused=paused,
            coalesce=coalesce,
            misfire_grace_time=misfire_grace_time,
            max_jitter=max_jitter,
            max_running_jobs=max_running_jobs,
            conflict_policy=conflict_policy,
            overwrite=overwrite,
            # Pass trigger/worker args
            **kwargs,
        )

    def schedule_all(self, **kwargs):
        """Schedules all pipelines enabled in their configuration."""
        # This logic now resides within PipelineManager
        scheduled_ids = []
        errors = []
        pipeline_names = self.list_pipelines()
        if not pipeline_names:
            logger.warning("No pipelines found to schedule.")
            return

        logger.info(f"Attempting to schedule {len(pipeline_names)} pipelines...")
        for name in pipeline_names:
            try:
                # Load config to check if enabled and get defaults
                # Use reload=True to ensure fresh config check for enablement
                pipeline_cfg = self._load_pipeline_cfg(name=name, reload=True)

                if not pipeline_cfg.schedule.enabled:
                    logger.info(
                        f"Skipping scheduling for '{name}': Not enabled in config."
                    )
                    continue

                logger.info(f"Scheduling [cyan]{name}[/cyan]...")
                # Schedule method handles defaults using the passed pipeline_cfg
                # Pass reload=False as config is already loaded fresh
                schedule_id = self.schedule(name=name, reload=False, **kwargs)
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
        """Gets the current list of schedules from the worker."""
        # Delegate to scheduler's internal method or property if it exists
        # Assuming _get_schedules is the way for now
        try:
            # Accessing private method, consider adding public property to Scheduler
            return self.scheduler._get_schedules()
        except Exception as e:
            logger.error(f"Failed to retrieve schedules: {e}")
            return []
