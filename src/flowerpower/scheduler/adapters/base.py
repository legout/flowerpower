import abc
import typing as t
from datetime import datetime

from apscheduler.job import Job
from apscheduler.triggers.base import BaseTrigger

# Define a generic type for the job function/callable
JobFunc = t.TypeVar("JobFunc", bound=t.Callable[..., t.Any])


class BaseSchedulerAdapter(abc.ABC):
    """Abstract base class for scheduler adapters."""

    @abc.abstractmethod
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
        """
        Adds the given job to the job store and schedules it to be run.

        :param func: callable (or a textual reference to one) to run at the scheduled time
        :param trigger: trigger that determines when ``func`` is called
        :param args: list of positional arguments to call func with
        :param kwargs: dict of keyword arguments to call func with
        :param id: explicit identifier for the job (for modifying it later)
        :param name: textual description of the job
        :param misfire_grace_time: seconds after the designated runtime that the job is still
            allowed to be run
        :param coalesce: run once instead of many times if the scheduler determines that the
            job should be run more than once in succession
        :param max_instances: maximum number of concurrently running instances allowed for this job
        :param next_run_time: when to first run the job, regardless of the trigger (pass None to
            add the job as paused)
        :param jobstore: alias of the job store to store the job in
        :param executor: alias of the executor to run the job with
        :param replace_existing: ``True`` to replace an existing job with the same ``id``
            (by default, an error is raised)
        :param trigger_args: arguments to be passed to the trigger constructor
        :return: the scheduled job
        """
        raise NotImplementedError

    @abc.abstractmethod
    def remove_job(self, job_id: str, jobstore: t.Optional[str] = None) -> None:
        """
        Removes a job, preventing it from being run any more.

        :param job_id: the identifier of the job
        :param jobstore: alias of the job store that contains the job
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_jobs(self, jobstore: t.Optional[str] = None) -> t.List[Job]:
        """
        Returns a list of pending jobs.

        :param jobstore: alias of the job store whose jobs to list
        :return: a list of :class:`~apscheduler.job.Job` instances
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_job(self, job_id: str, jobstore: t.Optional[str] = None) -> t.Optional[Job]:
        """
        Returns the Job that matches the given ``job_id``.

        :param job_id: the identifier of the job
        :param jobstore: alias of the job store that contains the job
        :return: the Job, or ``None`` if no job matches the ``job_id``
        """
        raise NotImplementedError

    @abc.abstractmethod
    def start(self) -> None:
        """Starts the scheduler."""
        raise NotImplementedError

    @abc.abstractmethod
    def shutdown(self, wait: bool = True) -> None:
        """
        Shuts down the scheduler. Does not interrupt any currently running jobs.

        :param wait: ``True`` to wait until all currently executing jobs have finished
        """
        raise NotImplementedError

    @abc.abstractmethod
    def pause_job(self, job_id: str, jobstore: t.Optional[str] = None) -> Job:
        """
        Pause the job with the given ID.

        :param job_id: the identifier of the job
        :param jobstore: alias of the job store that contains the job
        :return: the paused job
        """
        raise NotImplementedError

    @abc.abstractmethod
    def resume_job(self, job_id: str, jobstore: t.Optional[str] = None) -> Job:
        """
        Resume the schedule of the job with the given ID.

        :param job_id: the identifier of the job
        :param jobstore: alias of the job store that contains the job
        :return: the resumed job
        """
        raise NotImplementedError

    @abc.abstractmethod
    def modify_job(self, job_id: str, jobstore: t.Optional[str] = None, **changes: t.Any) -> Job:
        """
        Modifies the properties of a single job.

        Modifications are passed to this method as extra keyword arguments.

        :param job_id: the identifier of the job
        :param jobstore: alias of the job store that contains the job
        :return: the modified job
        """
        raise NotImplementedError

    @abc.abstractmethod
    def reschedule_job(
        self,
        job_id: str,
        jobstore: t.Optional[str] = None,
        trigger: t.Union[BaseTrigger, str, None] = None,
        **trigger_args: t.Any,
    ) -> Job:
        """
        Constructs a new trigger for the given job and updates its schedule.

        :param job_id: the identifier of the job
        :param jobstore: alias of the job store that contains the job
        :param trigger: trigger that determines when ``func`` is called
        :param trigger_args: arguments to be passed to the trigger constructor
        :return: the modified job
        """
        raise NotImplementedError