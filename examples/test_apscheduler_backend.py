#!/usr/bin/env python
"""
Example script to test the APScheduler backend for FlowerPower.
This demonstrates basic functionality like adding jobs and schedules.
"""

import datetime as dt
import time
from pathlib import Path

from flowerpower.scheduler.apscheduler.scheduler import APSchedulerBackend, APSchedulerTrigger


# Sample function to be executed by the scheduler
def sample_job(name="World", extra_info=None):
    current_time = dt.datetime.now().strftime("%H:%M:%S")
    print(f"[{current_time}] Hello, {name}!")
    if extra_info:
        print(f"Extra info: {extra_info}")
    return f"Job completed at {current_time}"


def add_job():
    # Initialize the scheduler backend
    base_dir = str(Path.cwd())
    print(f"Using base directory: {base_dir}")

    # Create scheduler instance
    scheduler = APSchedulerBackend(
        name="test-scheduler",
        base_dir=base_dir,
    )

    print("\n1. Testing immediate job execution:")
    # Add and run a job immediately
    job_id = scheduler.add_job(
        sample_job, 
        args=("APScheduler",), 
        kwargs={"extra_info": "This is an immediate job"},
        result_expiration_time=60
    )
    print(f"Added job with ID: {job_id}")
    scheduler.start_worker(background=True)
    # Wait a moment for the job to execute
    time.sleep(2)
    scheduler.stop_worker()
    # Try to get result (may not be available depending on data store)
    result = scheduler.get_job_result(job_id)
    print(f"Job result: {result}")

def add_schedule():
    base_dir = str(Path.cwd())
    # Create scheduler instance
    scheduler = APSchedulerBackend(
        name="test-scheduler",
        base_dir=base_dir,
    )
    print("\n2. Testing scheduled job execution:")
    # Create a trigger for interval-based execution (every 5 seconds)
    interval_trigger = APSchedulerTrigger("interval")
    interval_trigger_instance = interval_trigger.get_trigger_instance(seconds=5)

    # Schedule a job to run every 5 seconds
    schedule_id = scheduler.add_schedule(
        sample_job,
        trigger=interval_trigger_instance,
        args=("Scheduled APScheduler",),
        kwargs={"extra_info": "This runs every 5 seconds"},
        schedule_id="test-interval-schedule"
    )
    print(f"Added schedule with ID: {schedule_id}")
    scheduler.start_worker(background=True)
    # Display all schedules
    print("\nSchedules:")
    scheduler.show_schedules()
    
    # Let it run for a while
    print("\nWaiting for scheduled jobs to execute (20 seconds)...")
    #try:
    #    for i in range(6):
    #        time.sleep(5)
    #        print(f"Still running... ({(i+1)*5} seconds elapsed)")
    #except KeyboardInterrupt:
    #    print("Interrupted!")
    time.sleep(20)
    print("\nRemoving schedule...")
    scheduler.remove_schedule(schedule_id)
    
    print("\nRemaining schedules:")
    scheduler.show_schedules()
    
    print("\nTest completed!")
    scheduler.stop_worker()

if __name__ == "__main__":
    add_job()
