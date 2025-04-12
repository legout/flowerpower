"""
Example: Using WorkerManager with APScheduler backend

This script demonstrates how to use the flowerpower WorkerManager
with the APScheduler backend to schedule a simple task.
"""

from flowerpower.worker.manager import WorkerManager
from flowerpower.worker.config import APSchedulerConfig
from datetime import datetime, timedelta
import time

# Define a simple task function
def simple_task(message):
    print(f"Received: {message}")

# Instantiate WorkerManager with APScheduler backend (in-memory config)
config = APSchedulerConfig(type="apscheduler")
manager = WorkerManager(config)

# Register the task function with the manager
task = manager.define_task(simple_task)

# Schedule the task to run once, 10 seconds from now
run_time = datetime.utcnow() + timedelta(seconds=10)
manager.schedule_task_at(task, run_time, "Hello from APScheduler!")

print("Task scheduled with APScheduler. Waiting for execution...")
# Keep the script alive long enough for the job to run
time.sleep(15)