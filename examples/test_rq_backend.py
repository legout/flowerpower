#!/usr/bin/env python
"""
Example script to test the RQ backend for FlowerPower.
This demonstrates basic functionality like adding jobs and schedules.
"""

import datetime as dt
import time
from pathlib import Path
import sys
from flowerpower.scheduler.rq_backend import RQSchedulerBackend, RQTrigger


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
    scheduler = RQSchedulerBackend(
        name="test-scheduler",
        base_dir=base_dir,
    )
    
    print("\n1. Testing immediate job execution:")
    # Add and run a job immediately
    job_id = scheduler.add_job(
        sample_job, 
        args=("RQ",), 
        kwargs={"extra_info": "This is an immediate job"},
        result_expiration_time=300  # Keep result for 5 minutes
    )
    print(f"Added job with ID: {job_id}")
    
    # Check if a worker is running
    print("\nIMPORTANT: Make sure you have an RQ worker running!")
    print("If not, please run the following command in a separate terminal:")
    print("rq worker flowerpower --with-scheduler")
    
    # Wait a moment for the job to execute (if a worker is running)
    print("Waiting for job to execute...")
    time.sleep(5)
    
    # Try to get result
    result = scheduler.get_job_result(job_id)
    if result:
        print(f"Job result: {result}")
    else:
        print("No result yet. Make sure you have an RQ worker running.")

def add_schedule():
    base_dir = str(Path.cwd())
    scheduler = RQSchedulerBackend(
        name="test-scheduler",
        base_dir=base_dir,
    )
    
    print("\n2. Testing scheduled job execution:")
    # Create a trigger for interval-based execution (every 10 seconds)
    interval_trigger = RQTrigger("interval")
    interval_trigger_config = interval_trigger.get_trigger_instance(seconds=10)
    
    # Schedule a job to run every 10 seconds
    schedule_id = scheduler.add_schedule(
        sample_job,
        trigger=interval_trigger_config,
        args=("Scheduled RQ",),
        kwargs={"extra_info": "This runs every 10 seconds"},
        schedule_id="test-interval-schedule"
    )
    print(f"Added schedule with ID: {schedule_id}")
    
    # Display all schedules
    print("\nSchedules:")
    scheduler.show_schedules()
    
    # Let it run for a while
    print("\nWaiting for scheduled jobs to execute (60 seconds)...")
    print("(Make sure you have an RQ worker running with --with-scheduler flag)")
    try:
        for i in range(6):
            time.sleep(10)
            print(f"Still running... ({(i+1)*10} seconds elapsed)")
    except KeyboardInterrupt:
        print("Interrupted!")
    
    print("\nRemoving schedule...")
    scheduler.remove_schedule(schedule_id)
    
    print("\nRemaining schedules:")
    scheduler.show_schedules()
    
    # Test cron trigger
    print("\n3. Testing cron trigger:")
    cron_trigger = RQTrigger("cron")
    # Run every minute
    cron_config = cron_trigger.get_trigger_instance(crontab="* * * * *")
    
    cron_id = scheduler.add_schedule(
        sample_job,
        trigger=cron_config,
        args=("Cron RQ",),
        kwargs={"extra_info": "This runs every minute"},
        schedule_id="test-cron-schedule"
    )
    print(f"Added cron schedule with ID: {cron_id}")
    print("This would run every minute. Removing after 5 seconds...")
    time.sleep(5)
    
    scheduler.remove_schedule(cron_id)
    print("Cron schedule removed.")
    
    print("\nTest completed!")


if __name__ == "__main__":
    main()
