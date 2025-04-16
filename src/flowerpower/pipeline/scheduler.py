# -*- coding: utf-8 -*-
# pylint: disable=logging-fstring-interpolation
# flake8: noqa: E501
"""Pipeline Scheduler."""
import datetime as dt
import logging
from typing import Any, Callable
from uuid import UUID # Add UUID import

from fsspec.spec import AbstractFileSystem
from munch import Munch
from rich import print as rprint

# Assuming Config structure is available or relevant parts passed via funcs
# from .cfg import PipelineConfig # May not be needed directly if using funcs
from ..fs.base import BaseStorageOptions
from ..utils.misc import short_uuid # Keep if short_uuid is needed, otherwise remove
from ..utils.scheduler import get_trigger
from ..worker import Worker
from ..worker.base import BaseSchedule # Import BaseSchedule for type hinting

log = logging.getLogger(__name__)


class PipelineScheduler:
    """Handles scheduling of pipeline runs."""

    def __init__(
        self,
        fs: AbstractFileSystem,
        base_dir: str,
        storage_options: dict | Munch | BaseStorageOptions,
        worker_type: str,
        load_config_func: Callable, # e.g., PipelineManager.load_config
        get_project_name_func: Callable, # e.g., lambda: self.cfg.project.name
        get_pipeline_run_func: Callable, # e.g., PipelineManager._runner.run
        get_registry_func: Callable, # e.g., lambda: self._registry
    ):
        """Initialize PipelineScheduler.

        Args:
            fs: Filesystem instance.
            base_dir: Base directory for pipelines.
            storage_options: Storage options for the filesystem.
            worker_type: Type of worker to use (e.g., 'rq', 'apscheduler').
            load_config_func: Function to load pipeline configuration for a given name.
                              Expected signature: load_config_func(name: str) -> Config
            get_project_name_func: Function to get the project name.
                                   Expected signature: get_project_name_func() -> str
            get_pipeline_run_func: Function representing the pipeline execution logic.
                                   Expected signature matches PipelineRunner.run or PipelineManager.run
            get_registry_func: Function to get the pipeline registry instance.
                               Expected signature: get_registry_func() -> PipelineRegistry
        """
        self._fs = fs
        self._base_dir = base_dir
        self._storage_options = storage_options
        self._worker_type = worker_type
        self._load_config_func = load_config_func
        self._get_project_name_func = get_project_name_func
        self._get_pipeline_run_func = get_pipeline_run_func
        self._get_registry_func = get_registry_func

        log.debug(f"Initialized PipelineScheduler with worker type: {self._worker_type}")
        self._worker_instance = None # Initialize worker instance cache

    @property
    def worker(self):
        """
        Lazily instantiate and cache a Worker instance.
        """
        if not hasattr(self, '_worker_instance') or self._worker_instance is None:
            # Use attributes passed during PipelineScheduler init
            log.debug(f"Instantiating worker of type: {self._worker_type}")
            self._worker_instance = Worker(
                type=self._worker_type,
                fs=self._fs,
                base_dir=self._base_dir,
                storage_options=self._storage_options,
            )
        return self._worker_instance

    def _get_schedules(self) -> list[BaseSchedule]:
        """Get all schedules from the worker backend."""
        # TODO: Consider caching or optimizing if called frequently
        # Use the worker property directly
        return self.worker.get_schedules()

    # --- Moved from PipelineManager ---
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
        # worker_type: str | None = None, # Removed - Scheduler has fixed worker type
        **kwargs,
    ) -> str:
        """
        Add a job to run the pipeline with the given parameters to the worker queue.
        Returns the job ID (always).

        Args:
            name (str): The name of the job (pipeline).
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            config (dict | None, optional): The configuration for the job. Defaults to None.
            executor (str | None, optional): Executor hint. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry. Defaults to None.
            with_progressbar (bool | None, optional): Whether to use a progress bar. Defaults to None.
            reload (bool, optional): Whether to reload the job module. Defaults to False.
            **kwargs: Additional keyword arguments passed to the pipeline's run method.

        Returns:
            str: The ID of the enqueued job.
        """
        log.debug(f"Adding immediate job for pipeline: {name}")
        # Explicitly create kwargs for the worker job
        run_kwargs = {
            "name": name,
            "inputs": inputs,
            "final_vars": final_vars,
            "config": config,
            "executor": executor,
            "with_tracker": with_tracker,
            "with_opentelemetry": with_opentelemetry,
            "with_progressbar": with_progressbar,
            "reload": reload,
            **kwargs  # Include any extra kwargs passed to run_job
        }
        # Filter out None values AFTER merging
        run_kwargs = {k: v for k, v in run_kwargs.items() if v is not None}
        log.debug(f"Resolved run_kwargs for immediate job '{name}': {run_kwargs}")

        job_id = self.worker.add_job( # Use the worker property
            func=self._get_pipeline_run_func(), # Use the provided run function
            kwargs=run_kwargs,
            # Note: Worker-specific args might be needed here depending on the backend
        )
        rprint(
            f"✅ Successfully submitted immediate job for "
            f"[blue]{self._get_project_name_func()}.{name}[/blue] with ID [green]{job_id}[/green]"
        )
        return job_id

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
        # worker_type: str | None = None, # Removed - Scheduler has fixed worker type
        **kwargs,
    ) -> UUID:
        """
        Add a job to run the pipeline with the given parameters to the worker data store.
        Executes the job immediately and returns the job id (UUID). The job result will be stored
        for the given `result_ttl` and can be fetched using the job id.

        Args:
            name (str): The name of the job (pipeline).
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            config (dict | None, optional): The configuration for the job. Defaults to None.
            executor (str | None, optional): Executor hint. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry. Defaults to None.
            with_progressbar (bool | None, optional): Whether to use a progress bar. Defaults to None.
            reload (bool, optional): Whether to reload the job module. Defaults to False.
            result_ttl (float | dt.timedelta, optional): How long the job result should be stored.
                Defaults to 0 (don't store).
            **kwargs: Additional keyword arguments passed to the pipeline's run method.

        Returns:
            UUID: The ID of the added job.
        """
        log.debug(f"Adding immediate job with result TTL for pipeline: {name}")
        # Explicitly create kwargs for the worker job
        run_kwargs = {
            "name": name,
            "inputs": inputs,
            "final_vars": final_vars,
            "config": config,
            "executor": executor,
            "with_tracker": with_tracker,
            "with_opentelemetry": with_opentelemetry,
            "with_progressbar": with_progressbar,
            "reload": reload,
            **kwargs  # Include any extra kwargs passed to add_job
        }
         # Filter out None values AFTER merging
        run_kwargs = {k: v for k, v in run_kwargs.items() if v is not None}
        log.debug(f"Resolved run_kwargs for immediate job (TTL) '{name}': {run_kwargs}")

        id_ = self.worker.add_job( # Use the worker property
            func=self._get_pipeline_run_func(), # Use the provided run function
            kwargs=run_kwargs,
            result_ttl=result_ttl,
            # Note: Worker-specific args might be needed here depending on the backend
        )
        rprint(
            f"✅ Successfully added job for "
            f"[blue]{self._get_project_name_func()}.{name}[/blue] with ID [green]{id_}[/green]" # Use project name func
        )
        return id_

    # --- End Moved from PipelineManager ---

    def schedule(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None, # Driver config
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        trigger_type: str | None = None,
        id_: str | None = None,
        paused: bool = False,
        coalesce: str | None = None, # Default handled by worker
        misfire_grace_time: float | dt.timedelta | None = None,
        max_jitter: float | dt.timedelta | None = None,
        max_running_jobs: int | None = None,
        conflict_policy: str | None = None, # Default handled by worker
        overwrite: bool = False,
        # worker_type: str | None = None, # worker_type is fixed for the scheduler instance
        **kwargs, # Trigger specific args + run specific args not explicitly listed
    ) -> str:
        """
        Schedule a pipeline for execution using the configured worker.

        Args:
            name (str): The name of the pipeline.
            inputs (dict | None, optional): Inputs for the pipeline run. Defaults to config.
            final_vars (list | None, optional): Final variables for the pipeline run. Defaults to config.
            config (dict | None, optional): Hamilton driver config. Defaults to config.
            executor (str | None, optional): Executor for the pipeline run. Defaults to config.
            with_tracker (bool | None, optional): Enable tracker. Defaults to config.
            with_opentelemetry (bool | None, optional): Enable OpenTelemetry. Defaults to config.
            with_progressbar (bool | None, optional): Enable progress bar. Defaults to config.
            trigger_type (str | None, optional): Type of trigger (e.g., 'interval', 'cron'). Defaults to config.
            id_ (str | None, optional): Explicit ID for the schedule. Auto-generated if None.
            paused (bool, optional): Start the schedule in a paused state. Defaults to False or config.
            coalesce (str, optional): Coalesce strategy ('latest', 'earliest', 'all'). Defaults to worker default.
            misfire_grace_time (float | dt.timedelta | None, optional): Grace time for misfires. Defaults to worker default.
            max_jitter (float | dt.timedelta | None, optional): Max random delay added to run time. Defaults to worker default.
            max_running_jobs (int | None, optional): Max concurrent runs for this schedule. Defaults to worker default.
            conflict_policy (str, optional): Action on ID conflict ('replace', 'update', 'do_nothing'). Defaults to worker default ('do_nothing').
            overwrite (bool, optional): If True and id_ is None, generates ID '{name}-1', potentially overwriting. Defaults to False.
            **kwargs: Additional keyword arguments. Can include trigger-specific args (e.g., seconds=30 for interval)
                      or run-specific args not covered above.

        Returns:
            str: The ID of the scheduled pipeline.

        Raises:
            ValueError: If the specified trigger_type is invalid or required args are missing.
            Exception: Can raise exceptions from the worker backend during scheduling.
        """
        log.debug(f"Attempting to schedule pipeline: {name} with id: {id_}")
        # Load the specific pipeline's configuration
        try:
            cfg = self._load_config_func(name=name)
            if not cfg or not cfg.pipeline:
                 raise ValueError(f"Could not load valid configuration for pipeline '{name}'")
            schedule_cfg = cfg.pipeline.schedule
            run_cfg = cfg.pipeline.run
            project_name = self._get_project_name_func()
        except Exception as e:
            log.error(f"Failed to load configuration or get project name for pipeline '{name}': {e}")
            raise ValueError(f"Configuration error for pipeline '{name}': {e}") from e

        # --- Resolve Parameters ---
        # Combine args passed to this method with defaults from the loaded config

        # 1. Run Parameters (passed to the pipeline execution function)
        run_kwargs = {
            "name": name, # Always pass the pipeline name
            "inputs": inputs if inputs is not None else run_cfg.get("inputs"),
            "final_vars": final_vars if final_vars is not None else run_cfg.get("final_vars"),
            "config": config if config is not None else run_cfg.get("config"),
            "executor": executor if executor is not None else run_cfg.get("executor"),
            "with_tracker": with_tracker if with_tracker is not None else run_cfg.get("with_tracker"),
            "with_opentelemetry": with_opentelemetry if with_opentelemetry is not None else run_cfg.get("with_opentelemetry"),
            "with_progressbar": with_progressbar if with_progressbar is not None else run_cfg.get("with_progressbar"),
            # Include any extra kwargs that aren't schedule/trigger related
             **{k: v for k, v in kwargs.items() if k not in ['seconds', 'minutes', 'hours', 'days', 'weeks', 'start_date', 'end_date', 'timezone', 'jitter', 'year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second']} # Basic filter
        }
        # Filter out None values AFTER merging, so explicit None overrides default
        run_kwargs = {k: v for k, v in run_kwargs.items() if v is not None}
        log.debug(f"Resolved run_kwargs for '{name}': {run_kwargs}")


        # 2. Trigger Parameters
        trigger_type = trigger_type or schedule_cfg.trigger.type_
        if not trigger_type:
            raise ValueError(f"Trigger type must be specified either in config or as argument for pipeline '{name}'")

        # Get defaults for the specified trigger type
        trigger_defaults = getattr(schedule_cfg.trigger, trigger_type, Munch()).to_dict()
        trigger_kwargs = trigger_defaults.copy()
        # Overlay explicit kwargs passed to the function
        trigger_kwargs.update({k: v for k, v in kwargs.items() if k in trigger_defaults or k in ['seconds', 'minutes', 'hours', 'days', 'weeks', 'start_date', 'end_date', 'timezone', 'jitter', 'year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second']}) # Heuristic filter
        trigger_kwargs.pop("type_", None) # Remove internal type_ field
        # Filter out None values
        trigger_kwargs = {k: v for k, v in trigger_kwargs.items() if v is not None}
        log.debug(f"Resolved trigger_kwargs for '{name}' (type={trigger_type}): {trigger_kwargs}")


        # 3. Schedule Run Parameters (passed to the worker's add_schedule method)
        schedule_run_defaults = schedule_cfg.run.to_dict()
        schedule_run_kwargs = {
            "paused": paused if paused is not None else schedule_run_defaults.get("paused", False), # Explicit False default
            "coalesce": coalesce if coalesce is not None else schedule_run_defaults.get("coalesce"),
            "misfire_grace_time": misfire_grace_time if misfire_grace_time is not None else schedule_run_defaults.get("misfire_grace_time"),
            "max_jitter": max_jitter if max_jitter is not None else schedule_run_defaults.get("max_jitter"),
            "max_running_jobs": max_running_jobs if max_running_jobs is not None else schedule_run_defaults.get("max_running_jobs"),
            "conflict_policy": conflict_policy if conflict_policy is not None else schedule_run_defaults.get("conflict_policy", "do_nothing"), # Explicit default
        }
         # Filter out None values AFTER merging
        schedule_run_kwargs = {k: v for k, v in schedule_run_kwargs.items() if v is not None}
        log.debug(f"Resolved schedule_run_kwargs for '{name}': {schedule_run_kwargs}")


        # --- Generate ID if not provided ---
        def _generate_id(pipeline_name: str, explicit_id: str | None, force_overwrite_base: bool) -> str:
            if explicit_id:
                log.debug(f"Using explicit schedule ID: {explicit_id}")
                return explicit_id

            base_id = f"{pipeline_name}-1"
            if force_overwrite_base:
                log.debug(f"Overwrite specified, using base ID: {base_id}")
                return base_id

            try:
                existing_schedules = self._get_schedules()
                existing_ids = {schedule.id for schedule in existing_schedules}
                log.debug(f"Existing schedule IDs: {existing_ids}")

                if not any(id_val.startswith(f"{pipeline_name}-") for id_val in existing_ids):
                     log.debug(f"No existing schedules found for '{pipeline_name}', using base ID: {base_id}")
                     return base_id

                # Find highest existing number for this pipeline name
                max_num = 0
                for id_val in existing_ids:
                    if id_val.startswith(f"{pipeline_name}-"):
                        try:
                            num_part = id_val.split('-')[-1]
                            num = int(num_part)
                            if num > max_num:
                                max_num = num
                        except (ValueError, IndexError):
                            log.warning(f"Could not parse number from existing schedule ID: {id_val}")
                            continue # Skip malformed IDs

                new_id = f"{pipeline_name}-{max_num + 1}"
                log.debug(f"Generated new schedule ID: {new_id}")
                return new_id

            except Exception as e:
                log.error(f"Error getting existing schedules to generate ID: {e}. Falling back to base ID: {base_id}")
                # Fallback in case of error fetching schedules
                return base_id

        schedule_id = _generate_id(name, id_, overwrite)

        # --- Add Schedule via Worker ---
        try:
            with Worker(
                type=self._worker_type,
                fs=self._fs,
                base_dir=self._base_dir,
                storage_options=self._storage_options,
                # name=f"scheduler_{name}" # Optional name
            ) as worker:
                trigger = get_trigger(type_=trigger_type, **trigger_kwargs)

                # Pass the pipeline execution function obtained from the manager
                pipeline_func = self._get_pipeline_run_func()

                added_id = worker.add_schedule(
                    func=pipeline_func,
                    kwargs=run_kwargs, # Pass resolved run parameters
                    trigger=trigger,
                    id=schedule_id,
                    **schedule_run_kwargs # Pass resolved schedule run parameters
                )
                rprint(
                    f"✅ Successfully scheduled job for "
                    f"[blue]{project_name}.{name}[/blue] with ID [green]{added_id}[/green]"
                )
                return added_id
        except Exception as e:
            log.error(f"Failed to add schedule '{schedule_id}' for pipeline '{name}': {e}")
            rprint(f"[bold red]Error scheduling pipeline '{name}': {e}[/bold red]")
            # Re-raise the exception so the caller knows it failed
            raise

    def schedule_all(self, **kwargs):
        """
        Schedule all pipelines found by the registry.

        Args:
            **kwargs: Arguments passed directly to the `schedule` method for each pipeline.
                      Note: Pipeline-specific configurations will still take precedence for
                      defaults if not overridden by kwargs.
        """
        try:
            registry = self._get_registry_func()
            names = registry._get_names() # Use registry to find pipelines
            if not names:
                rprint("[yellow]No pipelines found to schedule.[/yellow]")
                return

            rprint(f"Attempting to schedule {len(names)} pipelines...")
            scheduled_ids = []
            errors = []
            for name in names:
                try:
                    # Load config specifically for this pipeline to get defaults
                    # Note: schedule() will load it again, potential optimization later
                    cfg = self._load_config_func(name=name)
                    if not cfg or not cfg.pipeline or not cfg.pipeline.schedule or not cfg.pipeline.schedule.enabled:
                         log.info(f"Skipping scheduling for '{name}': Not configured or not enabled.")
                         rprint(f"🟡 Skipping schedule for [cyan]{name}[/cyan]: Not configured or disabled in config.")
                         continue

                    rprint(f"Scheduling [cyan]{name}[/cyan]...")
                    # Pass kwargs, allowing overrides of config defaults
                    schedule_id = self.schedule(name=name, **kwargs)
                    scheduled_ids.append(schedule_id)
                except Exception as e:
                    log.error(f"Failed to schedule pipeline '{name}': {e}")
                    errors.append(name)
                    rprint(f"❌ Error scheduling [cyan]{name}[/cyan]: {e}")

            if errors:
                rprint(f"\n[bold red]Finished scheduling with errors for: {', '.join(errors)}[/bold red]")
            else:
                rprint(f"\n[bold green]Successfully scheduled {len(scheduled_ids)} pipelines.[/bold green]")

        except Exception as e:
            log.error(f"An unexpected error occurred during schedule_all: {e}")
            rprint(f"[bold red]An unexpected error occurred during schedule_all: {e}[/bold red]")