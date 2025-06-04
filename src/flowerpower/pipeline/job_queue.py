# -*- coding: utf-8 -*-
# pylint: disable=logging-fstring-interpolation
# flake8: noqa: E501
"""Pipeline Job Queue."""

import datetime as dt
from typing import Any, Callable, Optional, Union
from uuid import UUID

from loguru import logger
from rich import print as rprint

from .. import settings
# Import necessary config types
from ..cfg import PipelineConfig, ProjectConfig
from ..fs import AbstractFileSystem
from ..job_queue import JobQueueBackend, JobQueueManager
from ..utils.logging import setup_logging
from .registry import PipelineRegistry

setup_logging()


class PipelineJobQueue:
    """Handles scheduling of pipeline runs via a configured job queue backend."""

    def __init__(
        self,
        project_cfg: ProjectConfig,
        fs: AbstractFileSystem,
        cfg_dir: str,
        pipelines_dir: str,
        # job_queue_type: str | None = None,
    ):
        """Initialize PipelineJobQueue.

        Args:
            project_cfg: The project configuration object.
            fs: The file system to use for file operations.
            cfg_dir: The directory for configuration files.
            pipelines_dir: The directory for pipeline files.
            job_queue_type: The type of job queue to use (e.g., 'rq', 'apscheduler'). If None, defaults to the project config.
        """
        self.project_cfg = project_cfg
        self._fs = fs
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        self._job_queue_type = project_cfg.job_queue.type
        self._job_queue_backend_cfg = project_cfg.job_queue.backend
        self._job_queue = None

        # if not self._job_queue_type:
        #    # Fallback or default if not specified in project config
        #    self._job_queue_type = settings.JOB_QUEUE_TYPE
        #    logger.warning(
        #        f"Job queue type not specified in project config, defaulting to '{self._job_queue_type}'"
        #    )

    @property
    def job_queue(self) -> Optional[Any]:
        """
        Lazily instantiate and cache a Job queue instance.
        Handles the case where JobQueueManager returns None due to missing dependencies.

        Returns:
            Optional[Any]: The job queue manager instance, or None if the backend is unavailable.
        """
        logger.debug(
            f"Instantiating job queue of type: {self._job_queue_type} for project '{self.project_cfg.name}'"
        )
        if self._job_queue is None:
            self._job_queue = JobQueueManager(
                name=self.project_cfg.name,
                type=self._job_queue_type,
                backend=JobQueueBackend(
                    job_queue_type=self._job_queue_type,
                    **self._job_queue_backend_cfg.to_dict(),
                ),
            )

        if self._job_queue is None:
            if self._job_queue_type == "rq":
                logger.warning(
                    "JobQueueManager could not be instantiated. The RQ backend is unavailable. "
                    "Please ensure RQ is installed and configured correctly and that the Redis server is running."
                )
            elif self._job_queue_type == "apscheduler":
                logger.warning(
                    "JobQueueManager could not be instantiated. The APScheduler backend is unavailable. "
                    f"Please ensure APScheduler is installed and configured correctly, and that the configured data store ({self.project_cfg.job_queue.backend.data_store.type}) "
                    f"and event_broker ({self.project_cfg.job_queue.backend.event_broker.type}) are accessible."
                )
            return None
        return self._job_queue

    def _get_schedule_ids(self) -> list[Any]:
        """Get all schedules from the job queue backend.

        Returns:
            list[Any]: List of schedule IDs, or empty list if job queue backend is unavailable.
        """

        if self.job_queue is None:
            return []
        with self.job_queue as job_queue:
            logger.debug("Fetching schedules ids from job queue")
            return job_queue.schedule_ids

    def run_job(
        self,
        run_func: Callable,
        pipeline_cfg: PipelineConfig,  # Pipeline configuration object
        name: str,  # name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        cache: bool | dict = False,
        executor_cfg: str | dict | Any | None = None,
        with_adapter_cfg: dict | Any | None = None,
        pipeline_adapter_cfg: dict | Any | None = None,
        project_adapter_cfg: dict | Any | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,
        log_level: str | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        jitter_factor: float | None = None,
        retry_exceptions: tuple | None = None,
        **kwargs,
    ) -> Optional[dict[str, Any]]:
        """
        Add a job to run the pipeline immediately via the job queue queue.

        Args:
            run_func (Callable): The function to execute in the job queue (e.g., a configured PipelineRunner.run).
            pipeline_cfg (PipelineConfig): The pipeline configuration object.
            name (str): The name of the pipeline (used for logging).
            inputs (dict | None): Inputs for the pipeline run.
            final_vars (list | None): Final variables for the pipeline run.
            config (dict | None): Hamilton driver config.
            cache (bool | dict): Cache configuration.
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration.
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter configuration.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline adapter configuration.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project adapter configuration.
            adapter (dict[str, Any] | None): Additional adapter configuration.
            reload (bool): Whether to reload the pipeline module.
            log_level (str | None): Log level for the run.
            max_retries (int): Maximum number of retries for the job.
            retry_delay (float): Delay between retries.
            jitter_factor (float): Jitter factor for retry delay.
            retry_exceptions (tuple): Exceptions that should trigger a retry.
            **kwargs: Additional keyword arguments passed directly to the job queue's add_job method.

        Returns:
            Optional[dict[str, Any]]: The result of the job execution, or None if job queue backend is unavailable.
        """
        logger.debug(f"Adding immediate job for pipeline: {name}")

        pipeline_run_args = {
            # 'name' is not passed to run_func, it's part of the context already in PipelineRunner
            "project_cfg": self.project_cfg,
            "pipeline_cfg": pipeline_cfg,
            "inputs": inputs,
            "final_vars": final_vars,
            "config": config,
            "cache": cache,
            "executor_cfg": executor_cfg,
            "with_adapter_cfg": with_adapter_cfg,
            "pipeline_adapter_cfg": pipeline_adapter_cfg,
            "project_adapter_cfg": project_adapter_cfg,
            "adapter": adapter,
            "reload": reload,
            "log_level": log_level,
            "max_retries": max_retries,
            "retry_delay": retry_delay,
            "jitter_factor": jitter_factor,
            "retry_exceptions": retry_exceptions,
        }
        pipeline_run_args = {
            k: v for k, v in pipeline_run_args.items() if v is not None
        }
        logger.debug(
            f"Resolved arguments for target run_func for job '{name}': {pipeline_run_args}"
        )

        if self.job_queue is None:
            return None
        with self.job_queue as job_queue:
            res = job_queue.run_job(
                func=run_func,
                func_kwargs=pipeline_run_args,
                **kwargs,
            )

        return res

    def add_job(
        self,
        run_func: Callable,  # The actual function to run (e.g., PipelineRunner(...).run)
        pipeline_cfg: PipelineConfig,  # Pipeline configuration object
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        cache: bool | dict = False,
        executor_cfg: str | dict | Any | None = None,
        with_adapter_cfg: dict | Any | None = None,
        pipeline_adapter_cfg: dict | Any | None = None,
        project_adapter_cfg: dict | Any | None = None,
        adapter: dict[str, Any] | None = None,
        result_ttl: int | dt.timedelta = 120,
        run_at: dt.datetime | None = None,
        run_in: float | dt.timedelta | None = None,
        reload: bool = False,
        log_level: str | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        jitter_factor: float | None = None,
        retry_exceptions: tuple | list | None = None,
        **kwargs,  # Allow other job queue-specific args if needed
    ) -> Optional[Any]:
        """
        Add a job to run the pipeline immediately via the job queue, storing the result.

        Executes the job immediately and returns the job id (UUID). The job result will be stored
        by the job queue backend for the given `result_ttl` and can be fetched using the job id.

        Args:
            run_func (Callable): The function to execute in the job queue (e.g., a configured PipelineRunner.run).
            pipeline_cfg (PipelineConfig): The pipeline configuration object.
            name (str): The name of the pipeline (used for logging).
            inputs (dict | None): Inputs for the pipeline run.
            final_vars (list | None): Final variables for the pipeline run.
            config (dict | None): Hamilton driver config.
            cache (bool | dict): Cache configuration.
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration.
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter configuration.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline adapter configuration.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project adapter configuration.
            adapter (dict[str, Any] | None): Additional adapter configuration.
            reload (bool): Whether to reload the pipeline module.
            log_level (str | None): Log level for the run.
            result_ttl (int | dt.timedelta): How long the job result should be stored. Defaults to 0 (don't store).
            run_at (dt.datetime | None): Optional datetime to run the job at.
            run_in (float | dt.timedelta | None): Optional delay before running the job.
            max_retries (int): Maximum number of retries for the job.
            retry_delay (float): Delay between retries.
            jitter_factor (float): Jitter factor for retry delay.
            retry_exceptions (tuple): Exceptions that should trigger a retry.
            **kwargs: Additional keyword arguments passed directly to the job queue's add_job method.

        Returns:
            Optional[Any]: The ID of the added job or the job object itself, or None if job queue backend is unavailable.
        """
        logger.debug(f"Adding immediate job with result TTL for pipeline: {name}")

        pipeline_run_args = {
            "project_cfg": self.project_cfg,
            "pipeline_cfg": pipeline_cfg,
            "inputs": inputs,
            "final_vars": final_vars,
            "config": config,
            "cache": cache,
            "executor_cfg": executor_cfg,
            "with_adapter_cfg": with_adapter_cfg,
            "pipeline_adapter_cfg": pipeline_adapter_cfg,
            "project_adapter_cfg": project_adapter_cfg,
            "adapter": adapter,
            "reload": reload,
            "log_level": log_level,
            "max_retries": max_retries,
            "retry_delay": retry_delay,
            "jitter_factor": jitter_factor,
            "retry_exceptions": retry_exceptions,
        }
        pipeline_run_args = {
            k: v for k, v in pipeline_run_args.items() if v is not None
        }
        logger.debug(
            f"Resolved arguments for target run_func for job (TTL) '{name}': {pipeline_run_args}"
        )

        if self.job_queue is None:
            return None
        with self.job_queue as job_queue:
            job = job_queue.add_job(
                func=run_func,
                func_kwargs=pipeline_run_args,
                result_ttl=result_ttl,
                run_at=run_at,
                run_in=run_in,
                **kwargs,
            )
        rprint(
            f"✅ Successfully added job for "
            f"[blue]{self.project_cfg.name}.{name}[/blue] with ID [green]{job if isinstance(job, (str, UUID)) else job.id}[/green]"
            f" and result TTL of {result_ttl} seconds."
        )
        return job

    # --- End Moved from PipelineManager ---

    def schedule(
        self,
        run_func: Callable,
        pipeline_cfg: PipelineConfig,
        # --- Run Parameters (passed to run_func) ---
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,  # Driver config
        cache: bool | dict = False,
        executor_cfg: str | dict | Any | None = None,
        with_adapter_cfg: dict | Any | None = None,
        pipeline_adapter_cfg: dict | Any | None = None,
        project_adapter_cfg: dict | Any | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,
        log_level: str | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        jitter_factor: float | None = None,
        retry_exceptions: tuple | None = None,
        # --- Schedule Parameters (passed to job queue.add_schedule) ---
        cron: str | dict[str, str | int] | None = None,
        interval: int | str | dict[str, str | int] | None = None,
        date: dt.datetime | None = None,
        overwrite: bool = False,
        schedule_id: str | None = None,
        **kwargs,
    ) -> Optional[Union[str, UUID]]:
        """
        Schedule a pipeline for execution using the configured job queue.

        Args:
            run_func (Callable): The function to execute in the job queue.
            pipeline_cfg (PipelineConfig): The pipeline configuration object.
            inputs (dict | None): Inputs for the pipeline run (overrides config).
            final_vars (list | None): Final variables for the pipeline run (overrides config).
            config (dict | None): Hamilton driver config (overrides config).
            cache (bool | dict): Cache configuration (overrides config).
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration (overrides config).
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter configuration (overrides config).
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline adapter configuration (overrides config).
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project adapter configuration (overrides config).
            adapter (dict | None): Additional Hamilton adapters (overrides config).
            reload (bool): Whether to reload module (overrides config).
            log_level (str | None): Log level for the run (overrides config).
            max_retries (int): Maximum number of retries for the job.
            retry_delay (float): Delay between retries.
            jitter_factor (float): Jitter factor for retry delay.
            retry_exceptions (tuple): Exceptions that should trigger a retry.
            cron (str | dict | None): Cron expression or dict for cron trigger.
            interval (int | str | dict | None): Interval in seconds or dict for interval trigger.
            date (dt.datetime | None): Date for date trigger.
            overwrite (bool): If True and id_ is None, generates ID '{name}-1', potentially overwriting.
            schedule_id (str | None): Optional ID for the schedule. If None, generates a new ID.
            **kwargs: Additional keyword arguments passed to the job queue's add_schedule method,
                For RQ this includes:
                    - repeat: Repeat count (int or dict)
                    - result_ttl: Time to live for the job result (float or timedelta)
                    - ttl: Time to live for the job (float or timedelta)
                    - use_local_time_zone: Whether to use local time zone for scheduling (bool)
                For APScheduler, this includes:
                    - misfire_grace_time: Grace time for misfires (timedelta)
                    - coalesce: Whether to coalesce jobs (bool)
                    - max_running_jobs: Maximum instances of the job (int)
                    - max_jitter: Maximum jitter for scheduling (int)
                    - conflict_policy: Policy for conflicting jobs (str)
                    - paused: Whether to pause the job (bool)


        Returns:
            Optional[Union[str, UUID]]: The ID of the scheduled pipeline, or None if job queue backend is unavailable.

        Raises:
            ValueError: If trigger_type is invalid or required args are missing.
            Exception: Can raise exceptions from the job queue backend.
        """

        project_name = self.project_cfg.name
        name = pipeline_cfg.name
        logger.debug(
            f"Attempting to schedule pipeline: {project_name}.{name} with id: {schedule_id}"
        )

        # --- Resolve Parameters using pipeline_cfg for defaults ---
        schedule_cfg = pipeline_cfg.schedule
        # run_cfg = pipeline_cfg.run

        pipeline_run_args = {
            "project_cfg": self.project_cfg,
            "pipeline_cfg": pipeline_cfg,
            "inputs": inputs,
            "final_vars": final_vars,
            "config": config,
            "cache": cache,
            "executor_cfg": executor_cfg,
            "with_adapter_cfg": with_adapter_cfg,
            "pipeline_adapter_cfg": pipeline_adapter_cfg,
            "project_adapter_cfg": project_adapter_cfg,
            "adapter": adapter,
            "reload": reload,
            "log_level": log_level,
            "max_retries": max_retries,
            "retry_delay": retry_delay,
            "jitter_factor": jitter_factor,
            "retry_exceptions": retry_exceptions,
        }
        pipeline_run_args = {
            k: v for k, v in pipeline_run_args.items() if v is not None
        }
        logger.debug(f"Resolved run_kwargs for '{name}': {pipeline_run_args}")

        cron = cron if cron is not None else schedule_cfg.cron
        interval = interval if interval is not None else schedule_cfg.interval
        date = date if date is not None else schedule_cfg.date
        logger.debug(
            f"Resolved schedule parameters for '{name}': cron={cron}, interval={interval}, date={date}"
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
                existing_ids = self._get_schedule_ids()
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

        schedule_id = _generate_id(name, schedule_id, overwrite)

        # --- Add Schedule via Job queue ---
        try:
            if self.job_queue is None:
                return None
            with self.job_queue as job_queue:
                # Job queue is now responsible for creating the trigger object
                # Pass trigger type and kwargs directly
                added_id = job_queue.add_schedule(
                    func=run_func,
                    func_kwargs=pipeline_run_args,  # Pass resolved run parameters
                    cron=cron,
                    interval=interval,
                    date=date,
                    schedule_id=schedule_id,
                    **kwargs,  # Pass resolved schedule run parameters
                )
                logger.info(
                    f"✅ Successfully scheduled job for "
                    f"[blue]{project_name}.{name}[/blue] with ID [green]{added_id}[/green]"
                )
                return added_id
        except Exception as e:
            logger.error(
                f"Failed to add schedule '{schedule_id}' for pipeline '{name}': {e}"
            )
            raise

    # --- schedule_all method removed ---
    # PipelineManager will be responsible for iterating and calling schedule()

    def schedule_all(self, registry: PipelineRegistry, **kwargs) -> Optional[list[str]]:
        """
        Schedule all pipelines found by the registry.

        Args:
            registry (PipelineRegistry): The pipeline registry to use for finding pipelines.
            **kwargs: Arguments passed directly to the `schedule` method for each pipeline.
                      Note: Pipeline-specific configurations will still take precedence for
                      defaults if not overridden by kwargs.

        Returns:
            Optional[list[str]]: List of scheduled pipeline IDs, or None if job queue backend is unavailable.
        """
        if self.job_queue is None:
            logger.warning(
                "Job queue backend is unavailable. Cannot schedule pipelines."
            )
            return None

        try:
            names = registry._get_names()  # Use registry to find pipelines
            if not names:
                logger.info("[yellow]No pipelines found to schedule.[/yellow]")
                return []

            logger.info(f"Attempting to schedule {len(names)} pipelines...")
            scheduled_ids = []
            errors = []
            for name in names:
                try:
                    # Load config specifically for this pipeline to get defaults
                    # Note: schedule() will load it again, potential optimization later
                    cfg = registry.load_config(name=name)
                    if (
                        not cfg
                        or not cfg.pipeline
                        or not cfg.pipeline.schedule
                        or not cfg.pipeline.schedule.enabled
                    ):
                        logger.info(
                            f"🟡 Skipping schedule for [cyan]{name}[/cyan]: Not configured or disabled in config."
                        )
                        continue

                    logger.info(f"Scheduling [cyan]{name}[/cyan]...")
                    # Pass kwargs, allowing overrides of config defaults
                    run_func = registry.get_runner(name).run
                    schedule_id = self.schedule(
                        run_func=run_func, pipeline_cfg=cfg.pipeline, **kwargs
                    )
                    if schedule_id is None:
                        logger.info(
                            f"Skipping adding None schedule_id for pipeline '{name}' to scheduled_ids list."
                        )
                        continue
                    scheduled_ids.append(schedule_id)
                except Exception as e:
                    logger.error(f"Failed to schedule pipeline '{name}': {e}")
                    errors.append(name)
                    logger.error(f"❌ Error scheduling [cyan]{name}[/cyan]: {e}")

            if errors:
                logger.error(
                    f"\n[bold red]Finished scheduling with errors for: {', '.join(errors)}[/bold red]"
                )
            else:
                logger.success(
                    f"\n[bold green]Successfully scheduled {len(scheduled_ids)} pipelines.[/bold green]"
                )

            return scheduled_ids

        except Exception as e:
            logger.error(
                f"[bold red]An unexpected error occurred during schedule_all: {e}[/bold red]"
            )
            return None
