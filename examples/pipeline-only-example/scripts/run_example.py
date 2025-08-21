#!/usr/bin/env python3
# /// script
# dependencies = [
#     "flowerpower",
#     "typer>=0.9.0",
# ]
# ///
"""
Pipeline-Only Example Runner

This script demonstrates how to use FlowerPower's pipeline functionality
without any job queue dependencies. Perfect for lightweight processing,
development workflows, and scenarios where immediate execution is preferred.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

from flowerpower.pipeline.manager import PipelineManager

app = typer.Typer(help="Run pipeline-only text processing examples with FlowerPower")


def run_direct_pipeline():
    """Run the text processing pipeline directly using PipelineManager."""
    print("🔄 Running text processing pipeline directly...")

    # Initialize pipeline manager without job queue
    pipeline_manager = PipelineManager(
        project_cfg_path="conf/project.yml",
        base_dir=".",
        fs=None,  # Use default local filesystem
        cfg_dir="conf",
        pipelines_dir="pipelines",
    )

    # Run the pipeline immediately
    result = pipeline_manager.run(
        "text_processor",
        inputs={"process_timestamp": datetime.now().isoformat()},
        final_vars=["text_analysis_results"],
    )

    print("✅ Text processing completed successfully!")
    if "text_analysis_results" in result:
        analysis = result["text_analysis_results"]
        print(
            f"📄 Analysis completed at: {analysis['processing_metadata']['completed_at']}"
        )
        print(
            f"📊 Chunks processed: {analysis['processing_metadata']['total_chunks_processed']}"
        )

        # Show analysis summary
        if "word_analysis" in analysis:
            word_stats = analysis["word_analysis"]
            print(
                f"📝 Words: {word_stats['total_words']} total, {word_stats['unique_words']} unique"
            )

        if "sentiment_analysis" in analysis:
            sentiment = analysis["sentiment_analysis"]
            print(f"😊 Overall sentiment: {sentiment['overall_sentiment']}")

        if "output_file" in analysis:
            print(f"💾 Results saved to: {analysis['output_file']}")

    return result


def run_simple_analysis():
    """Run a simplified version with minimal processing."""
    print("⚡ Running simplified text analysis...")

    pipeline_manager = PipelineManager(
        project_cfg_path="conf/project.yml",
        base_dir=".",
        fs=None,
        cfg_dir="conf",
        pipelines_dir="pipelines",
    )

    # Custom inputs for minimal processing
    simple_inputs = {
        "process_timestamp": datetime.now().isoformat(),
        "operations": ["word_count", "sentence_count"],  # Only basic stats
        "save_to_file": False,  # Don't save file
        "include_statistics": False,  # Minimal output
    }

    result = pipeline_manager.run(
        "text_processor", inputs=simple_inputs, final_vars=["text_analysis_results"]
    )

    print("✅ Simple analysis completed!")
    if "text_analysis_results" in result:
        analysis = result["text_analysis_results"]
        print(f"📊 Processing completed with minimal operations")
        print(f"⏱️ No file output - results in memory only")

    return result


def run_custom_processing():
    """Run with custom processing configuration."""
    print("⚙️ Running custom text processing configuration...")

    pipeline_manager = PipelineManager(
        project_cfg_path="conf/project.yml",
        base_dir=".",
        fs=None,
        cfg_dir="conf",
        pipelines_dir="pipelines",
    )

    # Custom configuration for advanced processing
    custom_inputs = {
        "process_timestamp": datetime.now().isoformat(),
        "chunk_size": 500,  # Smaller chunks
        "operations": ["word_count", "extract_keywords", "analyze_sentiment"],
        "min_words": 10,  # Higher word threshold
        "remove_stopwords": True,
        "output_format": "json",
        "include_statistics": True,
        "save_to_file": True,
    }

    result = pipeline_manager.run(
        "text_processor", inputs=custom_inputs, final_vars=["text_analysis_results"]
    )

    print("✅ Custom processing completed successfully!")
    if "text_analysis_results" in result:
        analysis = result["text_analysis_results"]

        if "keyword_analysis" in analysis:
            keywords = analysis["keyword_analysis"]
            top_keywords = keywords["global_keywords"][:5]
            print(f"🔑 Top keywords: {[kw[0] for kw in top_keywords]}")

        if "processing_statistics" in analysis:
            stats = analysis["processing_statistics"]
            modules = stats["analysis_modules_used"]
            print(f"🧩 Analysis modules used: {', '.join(modules)}")

    return result


def demo_pipeline_features():
    """Demonstrate various pipeline features without job queue."""
    print("🎯 Demonstrating pipeline-only features...")

    pipeline_manager = PipelineManager(
        project_cfg_path="conf/project.yml",
        base_dir=".",
        fs=None,
        cfg_dir="conf",
        pipelines_dir="pipelines",
    )

    # Run multiple configurations to show flexibility
    configurations = [
        {
            "name": "basic",
            "config": {
                "operations": ["word_count", "character_count"],
                "save_to_file": False,
            },
        },
        {
            "name": "comprehensive",
            "config": {
                "operations": [
                    "word_count",
                    "sentence_count",
                    "extract_keywords",
                    "analyze_sentiment",
                ],
                "remove_stopwords": True,
                "save_to_file": True,
            },
        },
        {
            "name": "keywords_only",
            "config": {
                "operations": ["extract_keywords"],
                "chunk_size": 2000,
                "save_to_file": False,
            },
        },
    ]

    results = {}
    for config_set in configurations:
        name = config_set["name"]
        config = config_set["config"]

        print(f"\n🔄 Running {name} configuration...")

        # Add timestamp to config
        config["process_timestamp"] = datetime.now().isoformat()

        result = pipeline_manager.run(
            "text_processor", inputs=config, final_vars=["text_analysis_results"]
        )

        results[name] = result
        print(f"✅ {name} configuration completed")

        if "text_analysis_results" in result:
            analysis = result["text_analysis_results"]
            chunk_count = analysis["processing_metadata"]["total_chunks_processed"]
            print(f"   📊 Processed {chunk_count} chunks")

    print(f"\n🎉 Completed {len(results)} different pipeline configurations!")
    return results


def inspect_pipeline():
    """Inspect the pipeline structure and configuration."""
    print("🔍 Inspecting pipeline structure...")

    pipeline_manager = PipelineManager(
        project_cfg_path="conf/project.yml",
        base_dir=".",
        fs=None,
        cfg_dir="conf",
        pipelines_dir="pipelines",
    )

    # Get pipeline information
    pipelines = pipeline_manager.list_pipelines()
    print(f"📋 Available pipelines: {pipelines}")

    if "text_processor" in pipelines:
        print("\n📖 Text Processor Pipeline Details:")
        print("   • Input: Raw text file")
        print("   • Processing: Text chunking, word/sentence/character analysis")
        print("   • Features: Keyword extraction, sentiment analysis")
        print("   • Output: JSON analysis results")
        print("   • Execution: Synchronous (no job queue required)")

    return pipelines


def _setup_working_directory():
    """Setup working directory for example execution."""
    example_dir = Path(__file__).parent.parent
    os.chdir(example_dir)
    print(f"🏠 Working directory: {example_dir}")
    print("💡 This example uses ONLY pipeline functionality - no job queue required!")
    print("=" * 70)


@app.command()
def direct():
    """Run text processing pipeline directly using PipelineManager."""
    _setup_working_directory()
    print("🎯 Mode: direct")

    try:
        result = run_direct_pipeline()
        print("\n" + "=" * 70)
        print("🎉 Pipeline-only example completed successfully!")
        print("💡 No Redis or job queue was required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def simple():
    """Run simplified analysis with minimal processing operations."""
    _setup_working_directory()
    print("🎯 Mode: simple")

    try:
        result = run_simple_analysis()
        print("\n" + "=" * 70)
        print("🎉 Pipeline-only example completed successfully!")
        print("💡 No Redis or job queue was required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def custom():
    """Run text processing with custom configuration parameters."""
    _setup_working_directory()
    print("🎯 Mode: custom")

    try:
        result = run_custom_processing()
        print("\n" + "=" * 70)
        print("🎉 Pipeline-only example completed successfully!")
        print("💡 No Redis or job queue was required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def demo():
    """Demonstrate various pipeline features with different configurations."""
    _setup_working_directory()
    print("🎯 Mode: demo")

    try:
        result = demo_pipeline_features()
        print("\n" + "=" * 70)
        print("🎉 Pipeline-only example completed successfully!")
        print("💡 No Redis or job queue was required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def inspect():
    """Inspect pipeline structure and available configurations."""
    _setup_working_directory()
    print("🎯 Mode: inspect")

    try:
        result = inspect_pipeline()
        print("\n" + "=" * 70)
        print("🎉 Pipeline-only example completed successfully!")
        print("💡 No Redis or job queue was required for this processing!")
        return result
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
