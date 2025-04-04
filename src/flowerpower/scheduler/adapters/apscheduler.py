import typing as t
from datetime import datetime

from apscheduler.job import Job
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.base import BaseTrigger

from flowerpower.utils.scheduler import create_scheduler  # Reusing existing factory

from .base import BaseSchedulerAdapter, JobFunc


class APSchedulerAdapter(BaseSchedulerAdapter):
    """Scheduler adapter for APScheduler."""

    def __init__(self, config: t.Dict[str, t.Any]):
        """
        Initializes the APScheduler adapter.

        :param config: Configuration dictionary for APScheduler.
                       Expected keys might include 'jobstores', 'executors',
                       'job_defaults', 'timezone', etc.
        """
        # Reuse the existing create_scheduler utility which handles
        # complex configuration like jobstores, executors etc.
        self._scheduler: BaseScheduler = create_scheduler(config)

    def add_job(
        self,
        func: t.Union[str, JobFunc],
        trigger: t.Union[BaseTrigger, str, None] = None,
        args: t.Optional[t.Sequence[t.Any]] = None,
        kwargs: t.Optional[t.Mapping[str, t.Any]] = None,
        id: t.Optional[str] = None,
        name: t.Optional[str] = None,
        *,
        misfire_grace_time: t.Optional[int] = None,
        coalesce: bool = False,
        max_instances: t.Optional[int] = None,
        next_run_time: t.Optional[datetime] = None,
        jobstore: str = "default",
        executor: str = "default",
        replace_existing: bool = False,
        **trigger_args: t.Any,
    ) -> Job:
        return self._scheduler.add_job(
            func=func,
            trigger=trigger,
            args=args,
            kwargs=kwargs,
            id=id,
            name=name,
            misfire_grace_time=misfire_grace_time,
            coalesce=coalesce,
            max_instances=max_instances,
            next_run_time=next_run_time,
            jobstore=jobstore,
            executor=executor,
            replace_existing=replace_existing,
            **trigger_args,
        )

    def remove_job(self, job_id: str, jobstore: t.Optional[str] = None) -> None:
        self._scheduler.remove_job(job_id=job_id, jobstore=jobstore)

    def get_jobs(self, jobstore: t.Optional[str] = None) -> t.List[Job]:
        return self._scheduler.get_jobs(jobstore=jobstore)

    def get_job(self, job_id: str, jobstore: t.Optional[str] = None) -> t.Optional[Job]:
        return self._scheduler.get_job(job_id=job_id, jobstore=jobstore)

    def start(self) -> None:
        # Check if scheduler is already running to avoid errors
        if not self._scheduler.running:
            self._scheduler.start()

    def shutdown(self, wait: bool = True) -> None:
        # Check if scheduler is running before shutting down
        if self._scheduler.running:
            self._scheduler.shutdown(wait=wait)

    def pause_job(self, job_id: str, jobstore: t.Optional[str] = None) -> Job:
        return self._scheduler.pause_job(job_id=job_id, jobstore=jobstore)

    def resume_job(self, job_id: str, jobstore: t.Optional[str] = None) -> Job:
        return self._scheduler.resume_job(job_id=job_id, jobstore=jobstore)

    def modify_job(self, job_id: str, jobstore: t.Optional[str] = None, **changes: t.Any) -> Job:
        return self._scheduler.modify_job(job_id=job_id, jobstore=jobstore, **changes)

    def reschedule_job(
        self,
        job_id: str,
        jobstore: t.Optional[str] = None,
        trigger: t.Union[BaseTrigger, str, None] = None,
        **trigger_args: t.Any,
    ) -> Job:
        return self._scheduler.reschedule_job(
            job_id=job_id, jobstore=jobstore, trigger=trigger, **trigger_args
        )

    # Optional: Add a property to access the underlying scheduler if needed
    @property
    def scheduler(self) -> BaseScheduler:
        return self._scheduler