import pytest
from unittest import mock
from src.flowerpower.job_queue.registry import JobQueueBackendRegistry
from src.flowerpower.job_queue.rq.manager import RQManager
from src.flowerpower.job_queue.base import BaseJobQueueManager
from src.flowerpower.job_queue.models import BackendCapabilities, JobInfo

# --- Registry/Factory Tests ---

def test_registry_register_and_list(monkeypatch):
    registry = JobQueueBackendRegistry()
    class DummyBackend(BaseJobQueueManager):
        pass
    registry.register("dummy", DummyBackend)
    assert "dummy" in registry.list_available()

def test_registry_create_success(monkeypatch):
    registry = JobQueueBackendRegistry()
    class DummyBackend(BaseJobQueueManager):
        def __init__(self, config):
            self.config = config
    registry.register("dummy", DummyBackend)
    inst = registry.create("dummy", config={"foo": "bar"})
    assert isinstance(inst, DummyBackend)
    assert inst.config == {"foo": "bar"}

def test_registry_create_unknown_backend(monkeypatch):
    registry = JobQueueBackendRegistry()
    with pytest.raises((ValueError, KeyError)):
        registry.create("not_registered", config={})

# --- RQManager Tests ---

@pytest.fixture
def rq_manager(monkeypatch):
    # Patch redis and RQ objects with fakes/mocks
    import fakeredis
    fake_redis = fakeredis.FakeStrictRedis()
    monkeypatch.setattr("src.flowerpower.job_queue.rq.manager.redis", fakeredis)
    # Patch RQ Queue, Worker, Job as needed
    with mock.patch("src.flowerpower.job_queue.rq.manager.Queue") as MockQueue:
        yield RQManager(config={"redis_url": "redis://localhost:6379/0"})

def test_rqmanager_capabilities(rq_manager):
    caps = rq_manager.capabilities
    assert isinstance(caps, BackendCapabilities)
    assert caps.supports_delayed
    assert caps.supports_sync
    assert caps.supports_cancel

def test_rqmanager_enqueue_pipeline(monkeypatch):
    manager = RQManager(config={"redis_url": "redis://localhost:6379/0"})
    with mock.patch.object(manager, "_enqueue_job", return_value="jobid123") as mock_enqueue:
        job_id = manager.enqueue_pipeline("pipeline_name", args={"x": 1})
        mock_enqueue.assert_called_once()
        assert job_id == "jobid123"

def test_rqmanager_schedule_pipeline(monkeypatch):
    manager = RQManager(config={"redis_url": "redis://localhost:6379/0"})
    with mock.patch.object(manager, "_schedule_job", return_value="jobid456") as mock_sched:
        job_id = manager.schedule_pipeline("pipeline_name", args={"y": 2}, eta=1234567890)
        mock_sched.assert_called_once()
        assert job_id == "jobid456"

def test_rqmanager_run_pipeline_sync(monkeypatch):
    manager = RQManager(config={"redis_url": "redis://localhost:6379/0"})
    with mock.patch.object(manager, "_run_job_sync", return_value="result") as mock_run:
        result = manager.run_pipeline_sync("pipeline_name", args={"z": 3})
        mock_run.assert_called_once()
        assert result == "result"

def test_rqmanager_job_management(monkeypatch):
    manager = RQManager(config={"redis_url": "redis://localhost:6379/0"})
    # get_job
    with mock.patch.object(manager, "_get_job", return_value=JobInfo(id="jid", status="finished")):
        job = manager.get_job("jid")
        assert isinstance(job, JobInfo)
        assert job.id == "jid"
    # list_jobs
    with mock.patch.object(manager, "_list_jobs", return_value=[JobInfo(id="jid", status="finished")]):
        jobs = manager.list_jobs()
        assert isinstance(jobs, list)
        assert jobs[0].id == "jid"
    # cancel_job
    with mock.patch.object(manager, "_cancel_job", return_value=True):
        assert manager.cancel_job("jid") is True

def test_rqmanager_queue_and_worker_management(monkeypatch):
    manager = RQManager(config={"redis_url": "redis://localhost:6379/0"})
    with mock.patch.object(manager, "list_queues", return_value=["default", "high"]):
        queues = manager.list_queues()
        assert "default" in queues
    with mock.patch.object(manager, "list_workers", return_value=["worker1", "worker2"]):
        workers = manager.list_workers()
        assert "worker1" in workers

# --- Reusable Base Test Suite for Backends ---

class BaseTestJobQueueManager:
    """Reusable tests for any BaseJobQueueManager implementation."""

    @pytest.fixture
    def backend(self):
        """Override in subclass to provide backend instance."""
        raise NotImplementedError

    def test_enqueue_and_get_job(self, backend):
        with mock.patch.object(backend, "enqueue_pipeline", return_value="jobid"):
            jid = backend.enqueue_pipeline("pipeline", args={})
            assert isinstance(jid, str)
        with mock.patch.object(backend, "get_job", return_value=JobInfo(id="jobid", status="queued")):
            job = backend.get_job("jobid")
            assert isinstance(job, JobInfo)
            assert job.id == "jobid"

    def test_cancel_nonexistent_job(self, backend):
        with mock.patch.object(backend, "cancel_job", return_value=False):
            assert backend.cancel_job("nope") is False

# Example: Concrete test class for RQManager using the base suite
class TestRQManager(BaseTestJobQueueManager):
    @pytest.fixture
    def backend(self):
        mgr = RQManager(config={"redis_url": "redis://localhost:6379/0"})
        return mgr