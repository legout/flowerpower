#!/usr/bin/env python3
# /// script
# dependencies = [
#     "flowerpower[rq]",
#     "typer>=0.9.0",
# ]
# ///
"""
Job Queue-Only Example Runner

This script demonstrates how to use FlowerPower's job queue functionality
without any pipeline dependencies. Perfect for general task processing,
background jobs, and scenarios where simple function execution is preferred
over complex pipeline workflows.
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import typer

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

from flowerpower.cfg.project import ProjectConfig
from flowerpower.job_queue.manager import JobQueueManager

app = typer.Typer(help="Run job queue-only processing examples with FlowerPower")


def create_job_queue_manager():
    """Create a JobQueueManager instance for direct job processing."""
    # Load project configuration
    project_cfg = ProjectConfig.from_yaml("conf/project.yml")

    # Create job queue manager
    job_manager = JobQueueManager(project_cfg)

    return job_manager


def run_simple_calculations():
    """Demonstrate simple calculation jobs."""
    print("🧮 Running simple calculation jobs...")

    job_manager = create_job_queue_manager()

    # Import the task function
    from tasks.data_processing import simple_calculation

    # Enqueue several calculation jobs
    calculation_jobs = [
        {"x": 10, "y": 5, "operation": "add"},
        {"x": 20, "y": 4, "operation": "multiply"},
        {"x": 100, "y": 25, "operation": "divide"},
        {"x": 50, "y": 15, "operation": "subtract"},
    ]

    enqueued_jobs = []
    for calc in calculation_jobs:
        job = job_manager.enqueue(
            func=simple_calculation, queue_name="calculations", **calc
        )
        enqueued_jobs.append(job)
        print(f"✅ Enqueued {calc['operation']} job: {job.id}")

    print(f"\n📋 Total jobs enqueued: {len(enqueued_jobs)}")
    print("🚀 To process these jobs, start a worker:")
    print("   flowerpower job-queue start-worker --queue-names calculations")

    return enqueued_jobs


def run_batch_processing():
    """Demonstrate batch data processing jobs."""
    print("📦 Running batch processing jobs...")

    job_manager = create_job_queue_manager()

    # Import the task function
    from tasks.data_processing import process_batch_data

    # Generate sample data
    sample_data = []
    for i in range(50):
        sample_data.append({
            "id": i,
            "name": f"Item_{i}",
            "value": random.randint(1, 100),
            "category": random.choice(["A", "B", "C"]),
            "created_at": datetime.now().isoformat(),
        })

    # Enqueue batch processing jobs with different batch sizes
    batch_configs = [
        {"batch_size": 5, "queue": "small_batches"},
        {"batch_size": 10, "queue": "medium_batches"},
        {"batch_size": 25, "queue": "large_batches"},
    ]

    enqueued_jobs = []
    for config in batch_configs:
        job = job_manager.enqueue(
            func=process_batch_data,
            queue_name=config["queue"],
            data_list=sample_data,
            batch_size=config["batch_size"],
        )
        enqueued_jobs.append(job)
        print(f"✅ Enqueued batch job (size {config['batch_size']}): {job.id}")

    print(f"\n📋 Total batch jobs enqueued: {len(enqueued_jobs)}")
    print("🚀 To process these jobs, start workers:")
    print(
        "   flowerpower job-queue start-worker --queue-names small_batches,medium_batches,large_batches"
    )

    return enqueued_jobs


def run_report_generation():
    """Demonstrate report generation jobs."""
    print("📊 Running report generation jobs...")

    job_manager = create_job_queue_manager()

    # Import the task function
    from tasks.data_processing import generate_report

    # Enqueue different types of reports
    report_configs = [
        {"data_source": "sales_data.csv", "report_type": "summary"},
        {"data_source": "customer_data.csv", "report_type": "detailed"},
        {"data_source": "inventory_data.csv", "report_type": "analysis"},
        {"data_source": "financial_data.csv", "report_type": "summary"},
    ]

    enqueued_jobs = []
    for config in report_configs:
        job = job_manager.enqueue(func=generate_report, queue_name="reports", **config)
        enqueued_jobs.append(job)
        print(f"✅ Enqueued {config['report_type']} report job: {job.id}")

    print(f"\n📋 Total report jobs enqueued: {len(enqueued_jobs)}")
    print("🚀 To process these jobs, start a worker:")
    print("   flowerpower job-queue start-worker --queue-names reports")

    return enqueued_jobs


def run_notifications():
    """Demonstrate notification jobs."""
    print("📢 Running notification jobs...")

    job_manager = create_job_queue_manager()

    # Import the task function
    from tasks.data_processing import send_notification

    # Enqueue notification jobs
    notification_configs = [
        {
            "recipient": "admin@company.com",
            "message": "System backup completed",
            "channel": "email",
        },
        {
            "recipient": "+1234567890",
            "message": "Alert: High CPU usage detected",
            "channel": "sms",
        },
        {
            "recipient": "#alerts",
            "message": "Daily report is ready",
            "channel": "slack",
        },
        {
            "recipient": "user@company.com",
            "message": "Your report has been generated",
            "channel": "email",
        },
    ]

    enqueued_jobs = []
    for config in notification_configs:
        job = job_manager.enqueue(
            func=send_notification, queue_name="notifications", **config
        )
        enqueued_jobs.append(job)
        print(f"✅ Enqueued {config['channel']} notification: {job.id}")

    print(f"\n📋 Total notification jobs enqueued: {len(enqueued_jobs)}")
    print("🚀 To process these jobs, start a worker:")
    print("   flowerpower job-queue start-worker --queue-names notifications")

    return enqueued_jobs


def run_scheduled_tasks():
    """Demonstrate scheduled task jobs."""
    print("📅 Running scheduled task jobs...")

    job_manager = create_job_queue_manager()

    # Import task functions
    from tasks.data_processing import cleanup_old_files, generate_report

    # Schedule recurring tasks
    scheduled_jobs = []

    # Daily cleanup task
    cleanup_job = job_manager.schedule(
        func=cleanup_old_files,
        cron="0 2 * * *",  # Daily at 2 AM
        queue_name="maintenance",
        job_id="daily_cleanup",
        directory="/tmp/app_logs",
        days_old=7,
    )
    scheduled_jobs.append(("daily_cleanup", cleanup_job))
    print("✅ Scheduled daily cleanup task")

    # Weekly report
    weekly_report_job = job_manager.schedule(
        func=generate_report,
        cron="0 9 * * 1",  # Mondays at 9 AM
        queue_name="reports",
        job_id="weekly_report",
        data_source="weekly_analytics.csv",
        report_type="detailed",
    )
    scheduled_jobs.append(("weekly_report", weekly_report_job))
    print("✅ Scheduled weekly report task")

    # Monthly maintenance
    monthly_job = job_manager.schedule(
        func=cleanup_old_files,
        cron="0 1 1 * *",  # 1st of month at 1 AM
        queue_name="maintenance",
        job_id="monthly_cleanup",
        directory="/app/archive",
        days_old=30,
    )
    scheduled_jobs.append(("monthly_cleanup", monthly_job))
    print("✅ Scheduled monthly maintenance task")

    print(f"\n📋 Total scheduled jobs: {len(scheduled_jobs)}")
    print("🚀 To process scheduled jobs, start a worker with scheduler:")
    print("   flowerpower job-queue start-worker --with-scheduler")

    return scheduled_jobs


def run_long_running_jobs():
    """Demonstrate long-running computation jobs."""
    print("⏱️ Running long-running computation jobs...")

    job_manager = create_job_queue_manager()

    # Import the task function
    from tasks.data_processing import long_running_computation

    # Enqueue long-running jobs with different configurations
    computation_configs = [
        {"iterations": 50, "delay_ms": 200, "job_name": "quick_computation"},
        {"iterations": 100, "delay_ms": 100, "job_name": "medium_computation"},
        {"iterations": 200, "delay_ms": 50, "job_name": "long_computation"},
    ]

    enqueued_jobs = []
    for config in computation_configs:
        job_name = config.pop("job_name")
        job = job_manager.enqueue(
            func=long_running_computation,
            queue_name="computations",
            job_id=f"{job_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            **config,
        )
        enqueued_jobs.append(job)
        expected_duration = (config["iterations"] * config["delay_ms"]) / 1000
        print(f"✅ Enqueued {job_name} (est. {expected_duration:.1f}s): {job.id}")

    print(f"\n📋 Total computation jobs enqueued: {len(enqueued_jobs)}")
    print("🚀 To process these jobs, start a worker:")
    print("   flowerpower job-queue start-worker --queue-names computations")

    return enqueued_jobs


def run_data_validation():
    """Demonstrate data validation jobs."""
    print("✅ Running data validation jobs...")

    job_manager = create_job_queue_manager()

    # Import the task function
    from tasks.data_processing import data_validation_task

    # Generate sample data with some invalid items
    sample_data = []
    for i in range(20):
        item = {
            "id": i,
            "name": f"Item_{i}",
            "value": random.randint(-10, 150),  # Some values will be invalid
            "email": f"user{i}@example.com"
            if i % 5 != 0
            else "invalid_email",  # Some invalid emails
            "category": random.choice([
                "A",
                "B",
                "C",
                "INVALID",
            ]),  # Some invalid categories
        }

        # Randomly omit required fields for some items
        if i % 7 == 0:
            del item["name"]

        sample_data.append(item)

    # Define validation rules
    validation_rules = {
        "id": {"type": "int", "required": True, "min": 0},
        "name": {"type": "str", "required": True, "min_length": 3, "max_length": 50},
        "value": {"type": "int", "min": 0, "max": 100},
        "email": {"type": "str", "required": True},
        "category": {"type": "str", "required": True},
    }

    # Enqueue validation job
    job = job_manager.enqueue(
        func=data_validation_task,
        queue_name="validation",
        data=sample_data,
        validation_rules=validation_rules,
    )

    print(f"✅ Enqueued data validation job: {job.id}")
    print(
        f"📊 Validating {len(sample_data)} items against {len(validation_rules)} rules"
    )
    print("🚀 To process this job, start a worker:")
    print("   flowerpower job-queue start-worker --queue-names validation")

    return [job]


def run_mixed_workload():
    """Demonstrate a mixed workload with different job types."""
    print("🎯 Running mixed workload demonstration...")

    job_manager = create_job_queue_manager()

    # Import all task functions
    from tasks.data_processing import (cleanup_old_files, generate_report,
                                       process_batch_data, send_notification,
                                       simple_calculation)

    all_jobs = []

    # Mix of different job types
    jobs_to_enqueue = [
        # Quick calculations
        {
            "func": simple_calculation,
            "queue": "quick",
            "args": {"x": 15, "y": 3, "operation": "multiply"},
        },
        {
            "func": simple_calculation,
            "queue": "quick",
            "args": {"x": 100, "y": 7, "operation": "divide"},
        },
        # Reports
        {
            "func": generate_report,
            "queue": "reports",
            "args": {"data_source": "mixed_data.csv", "report_type": "summary"},
        },
        # Notifications
        {
            "func": send_notification,
            "queue": "notifications",
            "args": {
                "recipient": "ops@company.com",
                "message": "Mixed workload test",
                "channel": "email",
            },
        },
        # Maintenance
        {
            "func": cleanup_old_files,
            "queue": "maintenance",
            "args": {"directory": "/tmp/test", "days_old": 1},
        },
        # Batch processing
        {
            "func": process_batch_data,
            "queue": "batch",
            "args": {
                "data_list": [{"id": i, "value": i * 2} for i in range(10)],
                "batch_size": 3,
            },
        },
    ]

    for job_config in jobs_to_enqueue:
        job = job_manager.enqueue(
            func=job_config["func"],
            queue_name=job_config["queue"],
            **job_config["args"],
        )
        all_jobs.append(job)
        print(
            f"✅ Enqueued {job_config['func'].__name__} to {job_config['queue']}: {job.id}"
        )

    print(f"\n📋 Total mixed jobs enqueued: {len(all_jobs)}")
    print("🚀 To process all job types, start workers:")
    print(
        "   flowerpower job-queue start-worker --queue-names quick,reports,notifications,maintenance,batch"
    )

    return all_jobs


def inspect_job_queues():
    """Inspect current job queue status."""
    print("🔍 Inspecting job queue status...")

    job_manager = create_job_queue_manager()

    # Get queue information
    try:
        queues = job_manager.get_queue_info()

        if queues:
            print(f"\n📋 Found {len(queues)} queues:")
            for queue_name, info in queues.items():
                print(f"   📦 {queue_name}: {info.get('jobs', 'N/A')} jobs")
        else:
            print("\n📭 No active queues found")

        # Get worker information
        workers = job_manager.get_worker_info()
        if workers:
            print(f"\n👷 Found {len(workers)} workers:")
            for worker in workers:
                print(
                    f"   🔧 {worker.get('name', 'Unknown')}: {worker.get('state', 'Unknown')}"
                )
        else:
            print("\n👷 No active workers found")

    except Exception as e:
        print(f"❌ Error inspecting queues: {e}")
        print("💡 Make sure Redis is running and accessible")

    print("\n💡 Job Queue-Only Features:")
    print("   • No pipeline dependencies required")
    print("   • Direct function execution")
    print("   • Flexible queue management")
    print("   • Simple task scheduling")
    print("   • Minimal configuration overhead")


def _setup_working_directory():
    """Setup working directory for example execution."""
    example_dir = Path(__file__).parent.parent
    os.chdir(example_dir)
    print(f"🏠 Working directory: {example_dir}")
    print("💡 This example uses ONLY job queue functionality - no pipelines required!")
    print("=" * 75)


@app.command()
def calculations():
    """Run simple calculation jobs."""
    _setup_working_directory()
    print("🎯 Mode: calculations")

    try:
        result = run_simple_calculations()
        print("\n" + "=" * 75)
        print("🎉 Job queue-only example completed successfully!")
        print("💡 No Hamilton pipelines were required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def batch():
    """Run batch data processing jobs."""
    _setup_working_directory()
    print("🎯 Mode: batch")

    try:
        result = run_batch_processing()
        print("\n" + "=" * 75)
        print("🎉 Job queue-only example completed successfully!")
        print("💡 No Hamilton pipelines were required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def reports():
    """Run report generation jobs."""
    _setup_working_directory()
    print("🎯 Mode: reports")

    try:
        result = run_report_generation()
        print("\n" + "=" * 75)
        print("🎉 Job queue-only example completed successfully!")
        print("💡 No Hamilton pipelines were required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def notifications():
    """Run notification jobs."""
    _setup_working_directory()
    print("🎯 Mode: notifications")

    try:
        result = run_notifications()
        print("\n" + "=" * 75)
        print("🎉 Job queue-only example completed successfully!")
        print("💡 No Hamilton pipelines were required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def scheduled():
    """Run scheduled task jobs."""
    _setup_working_directory()
    print("🎯 Mode: scheduled")

    try:
        result = run_scheduled_tasks()
        print("\n" + "=" * 75)
        print("🎉 Job queue-only example completed successfully!")
        print("💡 No Hamilton pipelines were required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def long_running():
    """Run long-running computation jobs."""
    _setup_working_directory()
    print("🎯 Mode: long-running")

    try:
        result = run_long_running_jobs()
        print("\n" + "=" * 75)
        print("🎉 Job queue-only example completed successfully!")
        print("💡 No Hamilton pipelines were required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def validation():
    """Run data validation jobs."""
    _setup_working_directory()
    print("🎯 Mode: validation")

    try:
        result = run_data_validation()
        print("\n" + "=" * 75)
        print("🎉 Job queue-only example completed successfully!")
        print("💡 No Hamilton pipelines were required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def mixed():
    """Run mixed workload with different job types."""
    _setup_working_directory()
    print("🎯 Mode: mixed")

    try:
        result = run_mixed_workload()
        print("\n" + "=" * 75)
        print("🎉 Job queue-only example completed successfully!")
        print("💡 No Hamilton pipelines were required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def inspect():
    """Inspect current job queue status."""
    _setup_working_directory()
    print("🎯 Mode: inspect")

    try:
        result = inspect_job_queues()
        print("\n" + "=" * 75)
        print("🎉 Job queue-only example completed successfully!")
        print("💡 No Hamilton pipelines were required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
