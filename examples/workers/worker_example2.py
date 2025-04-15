# %%
from flowerpower.worker import Worker
from flowerpower.worker.rq import RQBackend
from flowerpower.worker.apscheduler import APSBackend, APSDataStore, APSEventBroker
from tasks import simple_task

rq_backend = RQBackend(type="redis")
aps_backend = APSBackend(
    APSDataStore(type="postgresql", username="postgres", password="password"),
    event_broker=APSEventBroker(type="postgresql", username="postgres", password="password"),
)

#rq_worker = Worker(type="rq", backend=rq_backend, name="example_worker")
aps_worker = Worker(type="apscheduler", backend=aps_backend, name="example_worker")
# worker.add

# %%

with Worker(type="rq", backend=rq_backend, name="example_worker") as rq_worker:
    rq_worker.start_worker(background=True)
    rq_job_id = rq_worker.add_job(simple_task, args=("Hello from simple_task",), result_ttl=200)
    rq_res = rq_worker.get_job_result(rq_job_id)
    rq_worker.stop_worker()


    print(f"Job ID: {rq_job_id}")
    print(f"Job Result: {rq_res}")
# %%
aps_job_id = aps_worker.add_job(simple_task, args=("Hello from simple_task",))
aps_res = aps_worker.get_job_result(aps_job_id)
print(f"Job ID: {aps_job_id}")
print(f"Job Result: {aps_res}")
# %%
