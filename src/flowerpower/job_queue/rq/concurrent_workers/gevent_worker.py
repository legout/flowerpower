# Monkey patch as early as possible
try:
    from gevent import monkey

    monkey.patch_all()
    import gevent
    import gevent.pool

    GEVENT_AVAILABLE = True
except ImportError:
    GEVENT_AVAILABLE = False
    raise ImportError(
        "Gevent is required for GeventWorker. Please install it with 'pip install gevent'."
    )


import datetime as dt

from loguru import logger
from rq import worker
from rq.exceptions import DequeueTimeout
from rq.job import JobStatus
from rq.worker import StopRequested

from flowerpower.utils.logging import setup_logging

# Use utcnow directly for simplicity
utcnow = dt.datetime.utcnow
setup_logging("INFO")


class GeventWorker(worker.Worker):
    """
    A variation of the RQ Worker that uses Gevent to perform jobs concurrently
    within a single worker process using greenlets.

    Ideal for I/O bound tasks, offering very lightweight concurrency.
    Jobs share the same memory space within the worker process.

    Requires gevent to be installed and monkey-patching to be applied
    (done automatically when this module is imported).
    """

    def __init__(
        self,
        queues,
        name=None,
        max_greenlets=1000,
        default_result_ttl=500,
        connection=None,
        exc_handler=None,
        exception_handlers=None,
        default_worker_ttl=None,
        job_class=None,
        queue_class=None,
        log_job_description=True,
        job_monitoring_interval=30,
        disable_default_exception_handler=False,
        prepare_for_work=True,
        maintenance_interval=600,
    ):
        super().__init__(
            queues,
            name=name,
            default_result_ttl=default_result_ttl,
            connection=connection,
            exc_handler=exc_handler,
            exception_handlers=exception_handlers,
            default_worker_ttl=default_worker_ttl,
            job_class=job_class,
            queue_class=queue_class,
            log_job_description=log_job_description,
            job_monitoring_interval=job_monitoring_interval,
            disable_default_exception_handler=disable_default_exception_handler,
            prepare_for_work=prepare_for_work,
            maintenance_interval=maintenance_interval,
        )

        self.max_greenlets = max_greenlets
        self._pool = None
        self.log = logger
        logger.info(f"GeventWorker initialized with max_greenlets={self.max_greenlets}")

    def work(
        self,
        burst=False,
        logging_level="INFO",
        date_format=worker.DEFAULT_LOGGING_DATE_FORMAT,
        log_format=worker.DEFAULT_LOGGING_FORMAT,
        max_jobs=None,
        with_scheduler=False,
    ):
        """Starts the worker's main loop using gevent for concurrent job execution."""
        self._install_signal_handlers()
        did_perform_work = False
        self.register_birth()
        self.log.info("Worker %s: started, version %s", self.key, worker.VERSION)
        self.set_state(worker.WorkerStatus.STARTED)

        self._pool = gevent.pool.Pool(self.max_greenlets)
        processed_jobs = 0

        try:
            while True:
                if self._stop_requested or (
                    max_jobs is not None and processed_jobs >= max_jobs
                ):
                    break

                self.run_maintenance_tasks()

                # Wait for space in the greenlet pool if it's full
                if self._pool.full():
                    gevent.sleep(0.1)  # Yield to other greenlets
                    continue

                try:
                    result = self.dequeue_job_and_maintain_ttl(timeout=1)
                except DequeueTimeout:
                    if burst:
                        break
                    gevent.sleep(0.1)
                    continue
                except StopRequested:
                    break
                except Exception:
                    self.log.error("Error during dequeue:", exc_info=True)
                    gevent.sleep(1)
                    continue

                if result is None:
                    if burst:
                        did_perform_work = True
                        break
                    gevent.sleep(0.1)
                    continue

                job, queue = result
                self.log.info("Processing job %s: %s", job.id, job.description)

                try:
                    # Spawn job execution in the gevent pool
                    greenlet = self._pool.spawn(self.execute_job, job, queue)
                    # Optional: Add error callback
                    greenlet.link_exception(
                        lambda g: self.log.error(
                            f"Error in greenlet for job {job.id}", exc_info=g.exception
                        )
                    )
                except Exception as e:
                    self.log.error(f"Failed to spawn job {job.id}: {e}", exc_info=True)
                    continue

                did_perform_work = True
                processed_jobs += 1

        finally:
            if self._pool:
                self.log.info("Waiting for active greenlets to complete...")
                self._pool.join(timeout=30)  # Wait up to 30 seconds for jobs to finish
                self._pool.kill()  # Kill any remaining greenlets
            self.register_death()

        return did_perform_work

    def set_job_status(self, job, status):
        """Sets the job status."""
        if job:
            job.set_status(status)

    def handle_job_success(self, job, queue, started_job_registry):
        """Handles job completion."""
        try:
            if started_job_registry:
                try:
                    started_job_registry.remove(job)
                except NotImplementedError:
                    pass
            job.ended_at = utcnow()
            job.set_status(JobStatus.FINISHED)
        except Exception as e:
            self.log.error(f"Error handling job success for {job.id}: {e}")

    def handle_job_failure(self, job, queue, started_job_registry, exc_info=None):
        """Handles job failure."""
        try:
            if started_job_registry:
                try:
                    started_job_registry.remove(job)
                except NotImplementedError:
                    pass
            job.ended_at = utcnow()
            job.set_status(JobStatus.FAILED)
        except Exception as e:
            self.log.error(f"Error handling job failure for {job.id}: {e}")

    def execute_job(self, job, queue):
        """Execute a job in a greenlet."""
        job_id = job.id if job else "unknown"

        try:
            self.set_job_status(job, JobStatus.STARTED)
            started_job_registry = queue.started_job_registry

            try:
                started_job_registry.add(
                    job,
                    self.job_monitoring_interval * 1000
                    if self.job_monitoring_interval
                    else -1,
                )
            except NotImplementedError:
                pass

            rv = job.perform()
            self.handle_job_success(
                job=job, queue=queue, started_job_registry=started_job_registry
            )
            return rv

        except Exception as e:
            self.log.error(f"Job {job_id} failed: {e}", exc_info=True)
            self.handle_job_failure(
                job=job, queue=queue, started_job_registry=started_job_registry
            )
            raise
