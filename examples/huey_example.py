"""
Example: Using WorkerManager with Huey backend

This script demonstrates how to use the flowerpower WorkerManager
with the Huey backend to enqueue a simple task.
"""

from flowerpower.worker.manager import WorkerManager
from flowerpower.worker.config import HueyConfig

# Define a simple task function
def simple_task(message):
    print(f"Received: {message}")

# Instantiate WorkerManager with Huey backend (default local Redis, huey_name required)
config = HueyConfig(type="huey", url="redis://localhost:6379/0", huey_name="test")
manager = WorkerManager(config)

# Register the task function with the manager
task = manager.define_task(simple_task)

# Enqueue the task using the manager
manager.enqueue_task(task, "Hello from Huey!")

print("Task enqueued with Huey. (Make sure a Huey consumer is running to process the job.)")