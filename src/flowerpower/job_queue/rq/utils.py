from typing import TYPE_CHECKING

from ..models import JobInfo, JobStatus, WorkerInfo

if TYPE_CHECKING:
    import rq


def _rq_status_to_job_status(rq_status: str) -> JobStatus:
    mapping = {
        "queued": JobStatus.QUEUED,
        "started": JobStatus.RUNNING,
        "finished": JobStatus.SUCCEEDED,
        "failed": JobStatus.FAILED,
        "deferred": JobStatus.QUEUED,
        "scheduled": JobStatus.QUEUED,
        "canceled": JobStatus.CANCELLED,
        "stopped": JobStatus.CANCELLED,
        "stopping": JobStatus.CANCELLED,
        "retry": JobStatus.RETRY,
    }
    return mapping.get(rq_status, JobStatus.UNKNOWN)


def _rq_job_to_job_info(rq_job: "rq.Job") -> JobInfo:
    return JobInfo(
        id=str(rq_job.id),
        status=_rq_status_to_job_status(rq_job.get_status()),
        enqueued_at=rq_job.enqueued_at,
        started_at=getattr(rq_job, "started_at", None),
        ended_at=getattr(rq_job, "ended_at", None),
        result=getattr(rq_job, "result", None),
        exc_info=getattr(rq_job, "exc_info", None),
        meta=dict(rq_job.meta) if hasattr(rq_job, "meta") else {},
        description=getattr(rq_job, "description", None),
        func_name=getattr(rq_job, "func_name", None),
        args=getattr(rq_job, "args", None),
        kwargs=getattr(rq_job, "kwargs", None),
    )


def _rq_worker_to_worker_info(rq_worker: "rq.Worker") -> WorkerInfo:
    return WorkerInfo(
        name=rq_worker.name,
        state=getattr(rq_worker, "state", None),
        queues=[q.name for q in rq_worker.queues],
        current_job_id=str(rq_worker.get_current_job_id())
        if rq_worker.get_current_job_id()
        else None,
        hostname=getattr(rq_worker, "hostname", None),
        pid=getattr(rq_worker, "pid", None),
        last_heartbeat=getattr(rq_worker, "last_heartbeat", None),
    )
