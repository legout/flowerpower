"""
Example: Using WorkerManager with RQ backend

This script demonstrates how to use the flowerpower WorkerManager
with the RQ backend to enqueue a simple task.
"""

from flowerpower.worker.manager import WorkerManager
from flowerpower.worker.config import RQConfig

# Define a simple task function
def simple_task(message):
    print(f"Received: {message}")

# Instantiate WorkerManager with RQ backend (default local Redis)
config = RQConfig(type="rq", url="redis://localhost:6379/0")
manager = WorkerManager(config)

# Register the task function with the manager
task = manager.define_task(simple_task)

# Enqueue the task using the manager
manager.enqueue_task(task, "Hello from RQ!")

print("Task enqueued with RQ. (Make sure an RQ worker is running to process the job.)")