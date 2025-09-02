#!/usr/bin/env python3
# /// script
# dependencies = [
#     "flowerpower",
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
- Custom configuration for different scraping scenarios
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import typer

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
        final_vars=["processed_articles"],
    )

    print("✅ Scraping completed successfully!")
    if "processed_articles" in result:
        scraping_info = result["processed_articles"]
        print(f"📄 Articles saved to: {scraping_info['output_file']}")
        print(f"📊 Total articles: {scraping_info['total_articles']}")
        print(f"🌐 Sources: {scraping_info['unique_sources']}")
        print(f"📈 Average length: {scraping_info['average_content_length']:.0f} chars")

    return result


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
        "sentiment_analysis": True,
    }

    # Run with custom configuration
    result = project.pipeline_manager.run(
        "news_scraper", inputs=custom_inputs, final_vars=["processed_articles"]
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
                "timeout": 60,
            },
        },
        {
            "name": "balanced",
            "config": {
                "max_concurrent_requests": 5,
                "request_delay": 1.0,
                "timeout": 30,
            },
        },
        {
            "name": "aggressive",
            "config": {
                "max_concurrent_requests": 10,
                "request_delay": 0.5,
                "timeout": 15,
            },
        },
    ]

    batch_results = []
    for config_set in configurations:
        name = config_set["name"]
        config = config_set["config"]

        # Add timestamp to config
        config["scrape_timestamp"] = datetime.now().isoformat()

        # Run pipeline with config
        result = project.pipeline_manager.run(
            "news_scraper",
            inputs=config,
            final_vars=["processed_articles"],
        )

        batch_results.append((name, result))
        print(f"✅ Completed {name} scraping run")

    print(f"\n📋 Total batch runs: {len(batch_results)}")

    return batch_results


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


if __name__ == "__main__":
    app()