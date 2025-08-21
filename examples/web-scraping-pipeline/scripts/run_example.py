#!/usr/bin/env python3
# /// script
# dependencies = [
#     "flowerpower[rq]",
#     "requests>=2.28.0",
#     "beautifulsoup4>=4.11.0",
#     "pandas>=2.0.0",
#     "typer>=0.9.0",
# ]
# ///
"""
Web Scraping Pipeline Example Runner

This script demonstrates different ways to run the news scraping pipeline:
- Synchronous execution for immediate scraping
- Job queue execution for background scraping
- Scheduled execution for recurring scraping
- Custom configuration for different scraping scenarios
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

app = typer.Typer(help="Run web scraping pipeline examples with FlowerPower")


def run_sync_scraping():
    """Run the news scraping pipeline synchronously."""
    print("🔄 Running news scraping synchronously...")
    
    # Initialize FlowerPower project
    project = FlowerPowerProject.from_config(".")
    
    # Run the pipeline immediately
    result = project.pipeline_manager.run(
        "news_scraper",
        inputs={"scrape_timestamp": datetime.now().isoformat()},
        final_vars=["processed_articles"]
    )
    
    print("✅ Scraping completed successfully!")
    if "processed_articles" in result:
        scraping_info = result["processed_articles"]
        print(f"📄 Articles saved to: {scraping_info['output_file']}")
        print(f"📊 Total articles: {scraping_info['total_articles']}")
        print(f"🌐 Sources: {scraping_info['unique_sources']}")
        print(f"📈 Average length: {scraping_info['average_content_length']:.0f} chars")
    
    return result


def run_queue_scraping():
    """Enqueue the news scraping for background processing."""
    print("📥 Enqueuing news scraping for background processing...")
    
    # Initialize FlowerPower project
    project = FlowerPowerProject.from_config(".")
    
    # Enqueue the pipeline
    job = project.pipeline_manager.enqueue(
        "news_scraper",
        inputs={"scrape_timestamp": datetime.now().isoformat()},
        final_vars=["processed_articles"],
        queue_name="scraping"
    )
    
    print(f"✅ Scraping job enqueued successfully!")
    print(f"🔧 Job ID: {job.id}")
    print(f"📋 Queue: {job.origin}")
    print("\n🚀 To process this job, start a worker:")
    print("   flowerpower job-queue start-worker --queue-names scraping")
    
    return job


def run_scheduled_scraping():
    """Schedule the news scraping for recurring execution."""
    print("📅 Scheduling news scraping for recurring execution...")
    
    # Initialize FlowerPower project
    project = FlowerPowerProject.from_config(".")
    
    # Schedule hourly scraping
    job = project.pipeline_manager.schedule(
        "news_scraper",
        cron="0 * * * *",  # Every hour
        inputs={"scrape_timestamp": datetime.now().isoformat()},
        final_vars=["processed_articles"],
        queue_name="scraping"
    )
    
    print("✅ Scraping scheduled successfully!")
    print(f"🔧 Job ID: {job.id}")
    print(f"📅 Schedule: Every hour")
    print("\n🚀 To process scheduled jobs, start a worker with scheduler:")
    print("   flowerpower job-queue start-worker --with-scheduler")
    
    return job


def run_custom_scraping_config():
    """Run news scraping with custom configuration."""
    print("⚙️ Running news scraping with custom configuration...")
    
    # Initialize FlowerPower project
    project = FlowerPowerProject.from_config(".")
    
    # Custom inputs for aggressive scraping
    custom_inputs = {
        "scrape_timestamp": datetime.now().isoformat(),
        "max_concurrent_requests": 10,
        "request_delay": 0.5,
        "min_content_length": 100,
        "extract_keywords": True,
        "sentiment_analysis": True
    }
    
    # Run with custom configuration
    result = project.pipeline_manager.run(
        "news_scraper",
        inputs=custom_inputs,
        final_vars=["processed_articles"]
    )
    
    print("✅ Custom scraping completed successfully!")
    if "processed_articles" in result:
        scraping_info = result["processed_articles"]
        print(f"📄 Articles saved to: {scraping_info['output_file']}")
        print(f"📊 Total articles: {scraping_info['total_articles']}")
        print(f"⚡ Used aggressive settings: 10 concurrent, 0.5s delay")
    
    return result


def run_batch_scraping():
    """Run multiple scraping jobs with different configurations."""
    print("🔄 Running batch scraping with different configurations...")
    
    project = FlowerPowerProject.from_config(".")
    
    # Different scraping configurations
    configurations = [
        {
            "name": "conservative",
            "config": {
                "max_concurrent_requests": 2,
                "request_delay": 2.0,
                "timeout": 60
            }
        },
        {
            "name": "balanced",
            "config": {
                "max_concurrent_requests": 5,
                "request_delay": 1.0,
                "timeout": 30
            }
        },
        {
            "name": "aggressive",
            "config": {
                "max_concurrent_requests": 10,
                "request_delay": 0.5,
                "timeout": 15
            }
        }
    ]
    
    batch_jobs = []
    for config_set in configurations:
        name = config_set["name"]
        config = config_set["config"]
        
        # Add timestamp to config
        config["scrape_timestamp"] = datetime.now().isoformat()
        
        # Enqueue job
        job = project.pipeline_manager.enqueue(
            "news_scraper",
            inputs=config,
            final_vars=["processed_articles"],
            queue_name="scraping",
            job_id=f"scrape_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        batch_jobs.append((name, job))
        print(f"✅ Enqueued {name} scraping job: {job.id}")
    
    print(f"\n📋 Total batch jobs: {len(batch_jobs)}")
    print("🚀 Start workers to process these jobs:")
    print("   flowerpower job-queue start-worker --queue-names scraping")
    
    return batch_jobs


def demo_multiple_schedules():
    """Demonstrate different scraping scheduling patterns."""
    print("📅 Demonstrating different scraping schedules...")
    
    project = FlowerPowerProject.from_config(".")
    
    schedules = [
        ("hourly", "0 * * * *", "Every hour"),
        ("daily", "0 8 * * *", "Daily at 8 AM"),
        ("weekly", "0 8 * * 1", "Weekly on Mondays at 8 AM"),
        ("custom", "*/15 * * * *", "Every 15 minutes")
    ]
    
    scheduled_jobs = []
    for name, cron, description in schedules:
        job = project.pipeline_manager.schedule(
            "news_scraper",
            cron=cron,
            inputs={"scrape_timestamp": datetime.now().isoformat()},
            final_vars=["processed_articles"],
            queue_name="scraping",
            job_id=f"scraper_{name}"
        )
        scheduled_jobs.append((name, job, description))
        print(f"✅ Scheduled {name} scraping: {description}")
    
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
    """Run news scraping pipeline synchronously for immediate results."""
    _setup_working_directory()
    print("🎯 Mode: sync")
    
    try:
        result = run_sync_scraping()
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
    """Enqueue news scraping for background processing."""
    _setup_working_directory()
    print("🎯 Mode: queue")
    
    try:
        result = run_queue_scraping()
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
    """Schedule news scraping for recurring execution."""
    _setup_working_directory()
    print("🎯 Mode: schedule")
    
    try:
        result = run_scheduled_scraping()
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
    """Run news scraping with custom configuration parameters."""
    _setup_working_directory()
    print("🎯 Mode: custom")
    
    try:
        result = run_custom_scraping_config()
        print("\n" + "=" * 60)
        print("🎉 Example completed successfully!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def batch():
    """Run multiple scraping configurations in batch mode."""
    _setup_working_directory()
    print("🎯 Mode: batch")
    
    try:
        result = run_batch_scraping()
        print("\n" + "=" * 60)
        print("🎉 Example completed successfully!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def demo_schedules():
    """Demonstrate different scraping scheduling patterns."""
    _setup_working_directory()
    print("🎯 Mode: demo-schedules")
    
    try:
        result = demo_multiple_schedules()
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