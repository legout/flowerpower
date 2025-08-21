#!/usr/bin/env python3
# /// script
# dependencies = [
#     "flowerpower[rq]",
#     "pandas>=2.0.0",
#     "plotly>=5.15.0",
#     "typer>=0.9.0",
#     "weasyprint>=60.0"
# ]
# ///
"""
Scheduled Reports Example Runner

This script demonstrates different ways to run the business dashboard pipeline:
- Synchronous execution for immediate reports
- Job queue execution for background report generation
- Scheduled execution for automated recurring reports
- Custom configuration for different reporting scenarios
"""

import sys
import os
from pathlib import Path
import typer
from datetime import datetime, timedelta
from typing import Optional

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

from flowerpower.flowerpower import FlowerPowerProject

app = typer.Typer(help="Run scheduled reports example with FlowerPower")


def run_sync_report_config():
    """Run the business dashboard synchronously."""
    print("🔄 Running business dashboard synchronously...")
    
    # Initialize FlowerPower project
    project = FlowerPowerProject.from_config(".")
    
    # Run the pipeline immediately
    result = project.pipeline_manager.run(
        "business_dashboard",
        inputs={"current_date": "2024-11-30"},
        final_vars=["business_dashboard"]
    )
    
    print("✅ Report generated successfully!")
    if "business_dashboard" in result:
        report_info = result["business_dashboard"]
        print(f"📄 Report saved to: {report_info['report_path']}")
        print(f"📊 KPIs calculated: Sales, Inventory, Customer metrics")
        print(f"🚨 Alerts generated: {len(report_info['alerts'])}")
    
    return result


def run_queue_report():
    """Enqueue the business dashboard for background processing."""
    print("📥 Enqueuing business dashboard for background processing...")
    
    # Initialize FlowerPower project
    project = FlowerPowerProject.from_config(".")
    
    # Enqueue the pipeline
    job = project.job_queue_manager.enqueue_pipeline(
        "business_dashboard",
        inputs={"current_date": "2024-11-30"},
        final_vars=["business_dashboard"],
        queue_name="reports"
    )
    
    print(f"✅ Job enqueued successfully!")
    print(f"🔧 Job ID: {job.id}")
    print(f"📋 Queue: {job.origin}")
    print("\n🚀 To process this job, start a worker:")
    print("   flowerpower job-queue start-worker --queue-names reports")
    
    return job


def run_scheduled_report():
    """Schedule the business dashboard for recurring execution."""
    print("📅 Scheduling business dashboard for recurring execution...")
    
    # Initialize FlowerPower project
    project = FlowerPowerProject.from_config(".")
    
    # Schedule monthly reports (1st of every month at 9 AM)
    job = project.job_queue_manager.schedule_pipeline(
        "business_dashboard",
        cron="0 9 1 * *",  # Monthly on 1st at 9 AM
        inputs={"current_date": "2024-11-30"},
        final_vars=["business_dashboard"],
        queue_name="reports"
    )
    
    print("✅ Report scheduled successfully!")
    print(f"🔧 Job ID: {job.id}")
    print(f"📅 Schedule: Monthly on 1st at 9:00 AM UTC")
    print("\n🚀 To process scheduled jobs, start a worker with scheduler:")
    print("   flowerpower job-queue start-worker --with-scheduler")
    
    return job


def run_custom_report_config():
    """Run business dashboard with custom configuration."""
    print("⚙️ Running business dashboard with custom configuration...")
    
    # Initialize FlowerPower project
    project = FlowerPowerProject.from_config(".")
    
    # Custom inputs for different reporting scenario
    custom_inputs = {
        "current_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "report_frequency": "weekly",
        "include_charts": True,
        "output_format": "html",
        "alerts_enabled": True
    }
    
    # Run with custom configuration
    result = project.pipeline_manager.run(
        "business_dashboard",
        inputs=custom_inputs,
        final_vars=["business_dashboard"]
    )
    
    print("✅ Custom report generated successfully!")
    if "business_dashboard" in result:
        report_info = result["business_dashboard"]
        print(f"📄 Report saved to: {report_info['report_path']}")
        print(f"📊 Report type: Weekly dashboard")
        print(f"📈 Charts included: {report_info['charts_included']}")
    
    return result


def demo_schedules():
    """Demonstrate different scheduling patterns."""
    print("📅 Demonstrating different scheduling patterns...")
    
    project = FlowerPowerProject.from_config(".")
    
    schedules = [
        ("daily", "0 8 * * *", "Daily at 8 AM"),
        ("weekly", "0 9 * * 1", "Weekly on Mondays at 9 AM"),
        ("monthly", "0 9 1 * *", "Monthly on 1st at 9 AM"),
        ("quarterly", "0 9 1 1,4,7,10 *", "Quarterly on 1st at 9 AM")
    ]
    
    scheduled_jobs = []
    for name, cron, description in schedules:
        job = project.job_queue_manager.schedule_pipeline(
            "business_dashboard",
            cron=cron,
            inputs={"current_date": "2024-11-30", "report_frequency": name},
            final_vars=["business_dashboard"],
            queue_name="reports",
            job_id=f"dashboard_{name}"
        )
        scheduled_jobs.append((name, job, description))
        print(f"✅ Scheduled {name} reports: {description}")
    
    print(f"\n📋 Total scheduled jobs: {len(scheduled_jobs)}")
    print("🚀 Start worker with scheduler to process these jobs:")
    print("   flowerpower job-queue start-worker --with-scheduler")
    
    return scheduled_jobs


def _setup_working_directory():
    """Setup working directory for example execution."""
    example_dir = Path(__file__).parent.parent
    os.chdir(example_dir)
    print(f"🏠 Working directory: {example_dir}")
    print("=" * 60)


@app.command()
def sync():
    """Run business dashboard synchronously for immediate reports."""
    _setup_working_directory()
    print("🎯 Mode: sync")
    
    try:
        result = run_sync_report_config()
        print("\n" + "=" * 60)
        print("🎉 Example completed successfully!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def queue():
    """Enqueue business dashboard for background processing."""
    _setup_working_directory()
    print("🎯 Mode: queue")
    
    try:
        result = run_queue_report()
        print("\n" + "=" * 60)
        print("🎉 Example completed successfully!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def schedule():
    """Schedule business dashboard for recurring execution."""
    _setup_working_directory()
    print("🎯 Mode: schedule")
    
    try:
        result = run_scheduled_report()
        print("\n" + "=" * 60)
        print("🎉 Example completed successfully!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def custom():
    """Run business dashboard with custom configuration."""
    _setup_working_directory()
    print("🎯 Mode: custom")
    
    try:
        result = run_custom_report_config()
        print("\n" + "=" * 60)
        print("🎉 Example completed successfully!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command(name="demo-schedules")
def demo_schedules_cmd():
    """Demonstrate different scheduling patterns."""
    _setup_working_directory()
    print("🎯 Mode: demo-schedules")
    
    try:
        result = demo_schedules()
        print("\n" + "=" * 60)
        print("🎉 Example completed successfully!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()