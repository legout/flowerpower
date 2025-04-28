# filepath: /Volumes/WD_Blue_1TB/coding/libs/flowerpower/src/flowerpower/worker/rq/concurrent_workers.py
import concurrent.futures
import datetime as dt
import logging
import os
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from loguru import logger
from rq import worker
from rq.exceptions import DequeueTimeout
from rq.job import JobStatus
from rq.worker import StopRequested

from flowerpower.utils.logging import setup_logging

utcnow = dt.datetime.utcnow
setup_logging("INFO")


class ThreadWorker(worker.Worker):
    """
    A variation of the RQ Worker that uses a ThreadPoolExecutor to perform
    jobs concurrently within a single worker process.

    Ideal for I/O bound tasks where the GIL is released during waits.
    Jobs share the same memory space within the worker process.
    """

    def __init__(
        self,
        queues,
        name=None,
        max_threads=None,
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

        self.max_threads = (
            max_threads if max_threads is not None else (os.cpu_count() or 1) * 5
        )
        self._executor = None
        self._futures = set()
        self.log = logger

    def work(
        self,
        burst=False,
        logging_level="INFO",
        date_format=worker.DEFAULT_LOGGING_DATE_FORMAT,
        log_format=worker.DEFAULT_LOGGING_FORMAT,
        max_jobs=None,
        with_scheduler=False,
    ):
        """Starts the worker's main loop."""
        self._install_signal_handlers()
        did_perform_work = False
        self.register_birth()
        self.log.info("Worker %s: started, version %s", self.key, worker.VERSION)
        self.set_state(worker.WorkerStatus.STARTED)

        self._executor = ThreadPoolExecutor(max_workers=self.max_threads)
        self._futures = set()
        processed_jobs = 0

        try:
            while True:
                if self._stop_requested or (
                    max_jobs is not None and processed_jobs >= max_jobs
                ):
                    break

                self.run_maintenance_tasks()

                # Wait for space in the thread pool if it's full
                if len(self._futures) >= self.max_threads:
                    done, self._futures = concurrent.futures.wait(
                        self._futures,
                        timeout=1.0,
                        return_when=concurrent.futures.FIRST_COMPLETED,
                    )
                    for future in done:
                        try:
                            future.result()
                        except Exception as e:
                            self.log.error(
                                f"Error in completed job: {e}", exc_info=True
                            )
                    continue

                try:
                    result = self.dequeue_job_and_maintain_ttl(timeout=1)
                except DequeueTimeout:
                    if burst:
                        break
                    time.sleep(0.1)
                    continue
                except StopRequested:
                    break
                except Exception:
                    self.log.error("Error during dequeue:", exc_info=True)
                    time.sleep(1)
                    continue

                if result is None:
                    if burst:
                        did_perform_work = True
                        break
                    time.sleep(0.1)
                    continue

                job, queue = result
                self.log.info("Processing job %s: %s", job.id, job.description)

                try:
                    future = self._executor.submit(self.execute_job, job, queue)
                    self._futures.add(future)
                    future.add_done_callback(
                        lambda f, jid=job.id: self._handle_job_completion(f, jid)
                    )
                except Exception as e:
                    self.log.error(f"Failed to submit job {job.id}: {e}", exc_info=True)
                    continue

                did_perform_work = True
                processed_jobs += 1

        finally:
            if self._executor:
                self._executor.shutdown(wait=True)
            self.register_death()

        return did_perform_work

    def _handle_job_completion(self, future, job_id):
        """Handle completion of a job future, including logging any errors."""
        self._futures.discard(future)
        try:
            future.result()
        except Exception as e:
            self.log.error(f"Error in job {job_id}: {e}", exc_info=True)

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

    # def handle_job_failure(self, job, queue, started_job_registry, exec_string=None):
    #    """Handles job failure."""
    #    try:
    #        if started_job_registry:
    #            try:
    #                started_job_registry.remove(job)
    #            except NotImplementedError:
    #                pass
    #        job.ended_at = utcnow()
    #        job.set_status(JobStatus.FAILED)
    #    except Exception as e:
    #        self.log.error(f"Error handling job failure for {job.id}: {e}")

    def execute_job(self, job, queue):
        """Execute a job in a worker thread."""
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
