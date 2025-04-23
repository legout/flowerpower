# -*- coding: utf-8 -*-
# pylint: disable=logging-fstring-interpolation
# flake8: noqa: E501
"""Pipeline Scheduler."""

import datetime as dt
from typing import Any, Callable
from uuid import UUID

from loguru import logger
from rich import print as rprint

# Import necessary config types
from ..cfg import PipelineConfig, ProjectConfig
from ..utils.logging import setup_logging
from ..worker import Worker
from ..fs import AbstractFileSystem
# Note: get_trigger is worker-specific and should be handled within the worker implementation
# from ..utils.scheduler import get_trigger # Removed - Worker handles trigger creation

setup_logging()


class PipelineScheduler:
    """Handles scheduling of pipeline runs via a configured worker backend."""

    def __init__(
        self,
        project_cfg: ProjectConfig,
        fs: AbstractFileSystem,
        cfg_dir: str,
        pipelines_dir: str,
        worker_type: str | None = None,
    ):
        """Initialize PipelineScheduler.

        Args:
            project_cfg: The project configuration object.
            fs: The file system to use for file operations.
            cfg_dir: The directory for configuration files.
            pipelines_dir: The directory for pipeline files.
            worker_type: The type of worker to use (e.g., 'rq', 'apscheduler'). If None, defaults to the project config.
        """
        self.project_cfg = project_cfg
        self._fs = fs
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        self._worker_type = worker_type or project_cfg.worker.type
        if not self._worker_type:
            # Fallback or default if not specified in project config
            self._worker_type = "rq"  # Or load from settings.FP_DEFAULT_WORKER_TYPE
            logger.warning(
                f"Worker type not specified in project config, defaulting to '{self._worker_type}'"
            )

        # logger.debug(
        #     f"Initialized PipelineScheduler for project '{project_cfg.name}' with worker type: {self._worker_type}"
        # )
        # # Worker instance is created on demand via the property

    @property
    def worker(self):
        """
        Lazily instantiate and cache a Worker instance.
        """
        # Lazily instantiate worker using project_cfg attributes
        logger.debug(
            f"Instantiating worker of type: {self._worker_type} for project '{self.project_cfg.name}'"
        )
        # Pass the necessary parts of project_cfg to the Worker
        return Worker(
            type=self._worker_type,
            fs=self._fs,
            # Pass worker-specific config from project_cfg if needed by Worker.__init__
            # e.g., worker_config=self.project_cfg.worker.get(self._worker_type, {})
        )

    def _get_schedules(self) -> list[Any]:
        """Get all schedules from the worker backend."""

        with self.worker as worker:

            logger.debug("Fetching schedules from worker")
            return worker.get_schedules()

    def run_job(
        self,
        run_func: Callable,  # The actual function to run (e.g., PipelineRunner(...).run)
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor_cfg: str | dict | Any | None = None,  # Match PipelineRunner arg
        with_adapter_cfg: dict | Any | None = None,  # Match PipelineRunner arg
        pipeline_adapter_cfg: dict | Any | None = None,  # Match PipelineRunner arg
        project_adapter_cfg: dict | Any | None = None,  # Match PipelineRunner arg
        adapter: dict[str, Any] | None = None,  # Match PipelineRunner arg
        reload: bool = False,
        log_level: str | None = None,  # Match PipelineRunner arg
        **kwargs,  # Allow other worker-specific args if needed
    ) -> dict[str, Any]:
        """
        Add a job to run the pipeline immediately via the worker queue.

        Args:
            run_func (Callable): The function to execute in the worker (e.g., a configured PipelineRunner.run).
            name (str): The name of the pipeline (used for logging).
            inputs (dict | None): Inputs for the pipeline run.
            final_vars (list | None): Final variables for the pipeline run.
            config (dict | None): Hamilton driver config.
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration.
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter configuration.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline adapter configuration.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project adapter configuration.
            adapter (dict[str, Any] | None): Additional adapter configuration.
            reload (bool): Whether to reload the pipeline module.
            log_level (str | None): Log level for the run.
            **kwargs: Additional keyword arguments passed directly to the worker's add_job method.

        Returns:
            dict[str, Any]: The result of the job execution.
        """
        logger.debug(f"Adding immediate job for pipeline: {name}")

        # Prepare the arguments for the target run_func
        # These names MUST match the parameters of the target run_func (PipelineRunner.run)
        pipeline_run_args = {
            # 'name' is not passed to run_func, it's part of the context already in PipelineRunner
            "inputs": inputs,
            "final_vars": final_vars,
            "config": config,
            "executor_cfg": executor_cfg,
            "with_adapter_cfg": with_adapter_cfg,
            "pipeline_adapter_cfg": pipeline_adapter_cfg,
            "project_adapter_cfg": project_adapter_cfg,
            "adapter": adapter,
            "reload": reload,
            "log_level": log_level,
            # **kwargs, # Be careful not to pass worker args to run_func
        }
        # Filter out None values AFTER merging
        pipeline_run_args = {
            k: v for k, v in pipeline_run_args.items() if v is not None
        }
        logger.debug(
            f"Resolved arguments for target run_func for job '{name}': {pipeline_run_args}"
        )

        with self.worker as worker:
            job_id = worker.add_job(
                func=run_func,  # Pass the function to be executed by the worker
                kwargs=pipeline_run_args,  # Pass the arguments for that function
                result_ttl=120,
                **kwargs,  # Pass any extra args meant for the worker backend
            )
            res = worker.get_result(job_id)
        #logger.info(
        #    f"✅ Successfully submitted immediate job for "
        #    f"[blue]{self.project_cfg.name}.{name}[/blue] with ID [green]{job_id}[/green]"
        #)
        return res

    def add_job(
        self,
        run_func: Callable,  # The actual function to run (e.g., PipelineRunner(...).run)
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor_cfg: str | dict | Any | None = None,  # Match PipelineRunner arg
        with_adapter_cfg: dict | Any | None = None,  # Match PipelineRunner arg
        pipeline_adapter_cfg: dict | Any | None = None,  # Match PipelineRunner arg
        project_adapter_cfg: dict | Any | None = None,  # Match PipelineRunner arg
        adapter: dict[str, Any] | None = None,  # Match PipelineRunner arg
        reload: bool = False,
        log_level: str | None = None,  # Match PipelineRunner arg
        result_ttl: float | dt.timedelta = 120,
        **kwargs,  # Allow other worker-specific args if needed
    ) -> str | UUID:
        """
        Add a job to run the pipeline immediately via the worker queue, storing the result.

        Executes the job immediately and returns the job id (UUID). The job result will be stored
        by the worker backend for the given `result_ttl` and can be fetched using the job id.

        Args:
            run_func (Callable): The function to execute in the worker (e.g., a configured PipelineRunner.run).
            name (str): The name of the pipeline (used for logging).
            inputs (dict | None): Inputs for the pipeline run.
            final_vars (list | None): Final variables for the pipeline run.
            config (dict | None): Hamilton driver config.
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration.
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter configuration.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline adapter configuration.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project adapter configuration.
            adapter (dict[str, Any] | None): Additional adapter configuration.
            reload (bool): Whether to reload the pipeline module.
            log_level (str | None): Log level for the run.
            result_ttl (float | dt.timedelta): How long the job result should be stored. Defaults to 0 (don't store).
            **kwargs: Additional keyword arguments passed directly to the worker's add_job method.

        Returns:
            str | UUID: The ID of the added job.
        """
        logger.debug(f"Adding immediate job with result TTL for pipeline: {name}")

        # Prepare the arguments for the target run_func
        pipeline_run_args = {
            "inputs": inputs,
            "final_vars": final_vars,
            "config": config,
            "executor_cfg": executor_cfg,
            "with_adapter_cfg": with_adapter_cfg,
            "pipeline_adapter_cfg": pipeline_adapter_cfg,
            "project_adapter_cfg": project_adapter_cfg,
            "adapter": adapter,
            "reload": reload,
            "log_level": log_level,
        }
        pipeline_run_args = {
            k: v for k, v in pipeline_run_args.items() if v is not None
        }
        logger.debug(
            f"Resolved arguments for target run_func for job (TTL) '{name}': {pipeline_run_args}"
        )

        with self.worker as worker:
            job_id = worker.add_job(
                func=run_func,
                kwargs=pipeline_run_args,
                result_ttl=result_ttl,
                **kwargs,  # Pass any extra args meant for the worker backend
            )
        rprint(
            f"✅ Successfully added job for "
            f"[blue]{self.project_cfg.name}.{name}[/blue] with ID [green]{job_id}[/green]"
        )
        return job_id

    # --- End Moved from PipelineManager ---

    def schedule(
        self,
        run_func: Callable,  # The actual function to run (e.g., PipelineRunner(...).run)
        pipeline_cfg: PipelineConfig,  # Pass the specific pipeline's config
        # --- Run Parameters (passed to run_func) ---
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,  # Driver config
        executor_cfg: str | dict | Any | None = None,  # Match PipelineRunner arg
        with_adapter_cfg: dict | Any | None = None,  # Match PipelineRunner arg
        pipeline_adapter_cfg: dict | Any | None = None,  # Match PipelineRunner arg
        project_adapter_cfg: dict | Any | None = None,  # Match PipelineRunner arg
        adapter: dict[str, Any] | None = None,  # Match PipelineRunner arg
        reload: bool = False,
        log_level: str | None = None,  # Match PipelineRunner arg
        # --- Schedule Parameters (passed to worker.add_schedule) ---
        trigger_type: str | None = None,
        id_: str | None = None,
        paused: bool | None = None,  # Allow None to use config default
        coalesce: str | None = None,
        misfire_grace_time: float | dt.timedelta | None = None,
        max_jitter: float | dt.timedelta | None = None,
        max_running_jobs: int | None = None,
        conflict_policy: str | None = None,
        overwrite: bool = False,
        # --- Trigger Parameters (passed within trigger_kwargs to worker.add_schedule) ---
        **kwargs,  # Trigger specific args (e.g., seconds=30) + any other worker args
    ) -> str | UUID:
        """
        Schedule a pipeline for execution using the configured worker.

        Args:
            run_func (Callable): The function to execute in the worker.
            pipeline_cfg (PipelineConfig): The configuration object for the specific pipeline being scheduled.
            inputs (dict | None): Inputs for the pipeline run (overrides config).
            final_vars (list | None): Final variables for the pipeline run (overrides config).
            config (dict | None): Hamilton driver config (overrides config).
            executor_cfg (... | None): Executor config (overrides config).
            with_adapter_cfg (... | None): Adapter enablement config (overrides config).
            pipeline_adapter_cfg (... | None): Pipeline adapter settings (overrides config).
            project_adapter_cfg (... | None): Project adapter settings (overrides config).
            adapter (dict | None): Additional Hamilton adapters (overrides config).
            reload (bool): Whether to reload module (overrides config).
            log_level (str | None): Log level for the run (overrides config).
            trigger_type (str | None): Type of trigger (e.g., 'interval', 'cron') (overrides config).
            id_ (str | None): Explicit ID for the schedule. Auto-generated if None.
            paused (bool | None): Start paused (overrides config). Defaults to False if not in config.
            coalesce (str | None): Coalesce strategy (overrides config).
            misfire_grace_time (... | None): Grace time for misfires (overrides config).
            max_jitter (... | None): Max random delay (overrides config).
            max_running_jobs (int | None): Max concurrent runs (overrides config).
            conflict_policy (str | None): Action on ID conflict (overrides config). Defaults to 'do_nothing'.
            overwrite (bool): If True and id_ is None, generates ID '{name}-1', potentially overwriting.
            **kwargs: Additional keyword arguments passed to the worker's add_schedule method,
                      including trigger-specific parameters (e.g., seconds=30 for interval).

        Returns:
            str | UUID: The ID of the scheduled pipeline.

        Raises:
            ValueError: If trigger_type is invalid or required args are missing.
            Exception: Can raise exceptions from the worker backend.
        """
        name = pipeline_cfg.name  # Get name from the provided config
        project_name = self.project_cfg.name
        logger.debug(
            f"Attempting to schedule pipeline: {project_name}.{name} with id: {id_}"
        )

        # --- Resolve Parameters using pipeline_cfg for defaults ---
        schedule_cfg = pipeline_cfg.schedule
        run_cfg = pipeline_cfg.run

        # 1. Run Parameters (passed to the pipeline execution function)
        pipeline_run_args = {
            "inputs": inputs if inputs is not None else run_cfg.inputs,
            "final_vars": final_vars if final_vars is not None else run_cfg.final_vars,
            "config": config if config is not None else run_cfg.config,
            "executor_cfg": executor_cfg
            if executor_cfg is not None
            else run_cfg.executor,
            "with_adapter_cfg": with_adapter_cfg
            if with_adapter_cfg is not None
            else run_cfg.with_adapter,
            "pipeline_adapter_cfg": pipeline_adapter_cfg
            if pipeline_adapter_cfg is not None
            else pipeline_cfg.adapter,  # Default from pipeline level
            "project_adapter_cfg": project_adapter_cfg
            if project_adapter_cfg is not None
            else self.project_cfg.adapter,  # Default from project level
            "adapter": adapter,  # No default in config, only passed directly
            "reload": reload if reload is not None else run_cfg.reload,
            "log_level": log_level if log_level is not None else run_cfg.log_level,
        }
        # Filter out None values AFTER merging
        pipeline_run_args = {
            k: v for k, v in pipeline_run_args.items() if v is not None
        }
        logger.debug(f"Resolved run_kwargs for '{name}': {pipeline_run_args}")

        # 2. Trigger Parameters (passed to worker)
        trigger_type = trigger_type or schedule_cfg.trigger.type_
        if not trigger_type:
            raise ValueError(
                f"Trigger type must be specified either in config or as argument for pipeline '{name}'"
            )

        # Get defaults for the specified trigger type from config
        trigger_defaults = getattr(schedule_cfg.trigger, trigger_type, {}).to_dict()
        trigger_kwargs = trigger_defaults.copy()
        # Overlay explicit kwargs passed to the function that are trigger-related
        # Worker's add_schedule should handle extracting relevant trigger args from kwargs
        trigger_kwargs.update(kwargs)
        # Filter out None values
        trigger_kwargs = {k: v for k, v in trigger_kwargs.items() if v is not None}
        logger.debug(
            f"Resolved trigger_kwargs for '{name}' (type={trigger_type}): {trigger_kwargs}"
        )

        # 3. Schedule Run Parameters (passed to the worker's add_schedule method)
        schedule_run_defaults = schedule_cfg.run.to_dict()
        schedule_run_kwargs = {
            "paused": paused
            if paused is not None
            else schedule_run_defaults.get("paused", False),
            "coalesce": coalesce
            if coalesce is not None
            else schedule_run_defaults.get("coalesce"),
            "misfire_grace_time": misfire_grace_time
            if misfire_grace_time is not None
            else schedule_run_defaults.get("misfire_grace_time"),
            "max_jitter": max_jitter
            if max_jitter is not None
            else schedule_run_defaults.get("max_jitter"),
            "max_running_jobs": max_running_jobs
            if max_running_jobs is not None
            else schedule_run_defaults.get("max_running_jobs"),
            "conflict_policy": conflict_policy
            if conflict_policy is not None
            else schedule_run_defaults.get("conflict_policy", "do_nothing"),
            # Pass any remaining kwargs not used by trigger or run_func to worker
            **{k: v for k, v in kwargs.items() if k not in trigger_kwargs},
        }
        # Filter out None values AFTER merging
        schedule_run_kwargs = {
            k: v for k, v in schedule_run_kwargs.items() if v is not None
        }
        logger.debug(
            f"Resolved schedule_run_kwargs for '{name}': {schedule_run_kwargs}"
        )

        # --- Generate ID if not provided ---
        # (Keep _generate_id function as is, it uses self._get_schedules())
        def _generate_id(
            pipeline_name: str, explicit_id: str | None, force_overwrite_base: bool
        ) -> str:
            if explicit_id:
                logger.debug(f"Using explicit schedule ID: {explicit_id}")
                return explicit_id

            base_id = f"{pipeline_name}-1"
            if force_overwrite_base:
                logger.debug(f"Overwrite specified, using base ID: {base_id}")
                return base_id

            try:
                existing_schedules = self._get_schedules()
                existing_ids = {schedule.id for schedule in existing_schedules}
                logger.debug(f"Existing schedule IDs: {existing_ids}")

                if not any(
                    id_val.startswith(f"{pipeline_name}-") for id_val in existing_ids
                ):
                    logger.debug(
                        f"No existing schedules found for '{pipeline_name}', using base ID: {base_id}"
                    )
                    return base_id

                # Find highest existing number for this pipeline name
                max_num = 0
                for id_val in existing_ids:
                    if id_val.startswith(f"{pipeline_name}-"):
                        try:
                            num_part = id_val.split("-")[-1]
                            num = int(num_part)
                            if num > max_num:
                                max_num = num
                        except (ValueError, IndexError):
                            logger.warning(
                                f"Could not parse number from existing schedule ID: {id_val}"
                            )
                            continue  # Skip malformed IDs

                new_id = f"{pipeline_name}-{max_num + 1}"
                logger.debug(f"Generated new schedule ID: {new_id}")
                return new_id

            except Exception as e:
                logger.error(
                    f"Error getting existing schedules to generate ID: {e}. Falling back to base ID: {base_id}"
                )
                # Fallback in case of error fetching schedules
                return base_id

        schedule_id = _generate_id(name, id_, overwrite)

        # --- Add Schedule via Worker ---
        try:
            with self.worker as worker:
                # Worker is now responsible for creating the trigger object
                # Pass trigger type and kwargs directly
                added_id = worker.add_schedule(
                    func=run_func,
                    kwargs=pipeline_run_args,  # Pass resolved run parameters
                    trigger_type=trigger_type,
                    trigger_kwargs=trigger_kwargs,
                    id=schedule_id,
                    **schedule_run_kwargs,  # Pass resolved schedule run parameters
                )
                rprint(
                    f"✅ Successfully scheduled job for "
                    f"[blue]{project_name}.{name}[/blue] with ID [green]{added_id}[/green]"
                )
                return added_id
        except Exception as e:
            logger.error(
                f"Failed to add schedule '{schedule_id}' for pipeline '{name}': {e}"
            )
            rprint(f"[bold red]Error scheduling pipeline '{name}': {e}[/bold red]")
            # Re-raise the exception so the caller knows it failed
            raise

    # --- schedule_all method removed ---
    # PipelineManager will be responsible for iterating and calling schedule()

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
            names = registry._get_names()  # Use registry to find pipelines
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
                    if (
                        not cfg
                        or not cfg.pipeline
                        or not cfg.pipeline.schedule
                        or not cfg.pipeline.schedule.enabled
                    ):
                        logger.info(
                            f"Skipping scheduling for '{name}': Not configured or not enabled."
                        )
                        rprint(
                            f"🟡 Skipping schedule for [cyan]{name}[/cyan]: Not configured or disabled in config."
                        )
                        continue

                    rprint(f"Scheduling [cyan]{name}[/cyan]...")
                    # Pass kwargs, allowing overrides of config defaults
                    schedule_id = self.schedule(name=name, **kwargs)
                    scheduled_ids.append(schedule_id)
                except Exception as e:
                    logger.error(f"Failed to schedule pipeline '{name}': {e}")
                    errors.append(name)
                    rprint(f"❌ Error scheduling [cyan]{name}[/cyan]: {e}")

            if errors:
                rprint(
                    f"\n[bold red]Finished scheduling with errors for: {', '.join(errors)}[/bold red]"
                )
            else:
                rprint(
                    f"\n[bold green]Successfully scheduled {len(scheduled_ids)} pipelines.[/bold green]"
                )

        except Exception as e:
            logger.error(f"An unexpected error occurred during schedule_all: {e}")
            rprint(
                f"[bold red]An unexpected error occurred during schedule_all: {e}[/bold red]"
            )
