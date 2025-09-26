#!/usr/bin/env python3
# /// script
# dependencies = [
#     "flowerpower",
#     "pandas>=2.0.0",
#     "plotly>=5.15.0",
#     "typer>=0.9.0",
#     "numpy>=1.21.0",
#     "scikit-learn>=1.3.0",
#     "joblib>=1.2.0",
# ]
# ///
"""
Example runner script for the ml-training-pipeline FlowerPower project.

This script demonstrates different ways to run the ML training pipeline:
1. Synchronous execution
2. Custom hyperparameter training
"""

import sys
from pathlib import Path
from typing import Annotated

import typer

# Add project root to path for imports
project_root = Path(__file__).parents[1]
sys.path.insert(0, str(project_root))

from flowerpower import FlowerPowerProject

app = typer.Typer()


def run_synchronous():
    """Run the ML training pipeline synchronously."""
    print("🤖 Running ML training pipeline synchronously...")

    # Load the FlowerPower project
    project = FlowerPowerProject.load(str(project_root))

    # Run the pipeline
    result = project.run("customer_churn")

    print("✅ ML training completed successfully!")
    print(f"📊 Results summary:")

    # Extract key results
    evaluation = result.get("model_evaluation", {})
    test_perf = evaluation.get("test_performance", {})

    print(f"  - Algorithm: {evaluation.get('algorithm', 'Unknown')}")
    print(
        f"  - Test Accuracy: {test_perf.get('accuracy', 'N/A'):.4f}"
        if isinstance(test_perf.get("accuracy"), float)
        else f"  - Test Accuracy: {test_perf.get('accuracy', 'N/A')}"
    )
    print(
        f"  - Test F1 Score: {test_perf.get('f1', 'N/A'):.4f}"
        if isinstance(test_perf.get("f1"), float)
        else f"  - Test F1 Score: {test_perf.get('f1', 'N/A')}"
    )

    # Feature importance
    feature_importance = result.get("feature_importance", {})
    if feature_importance:
        top_features = list(feature_importance.keys())[:3]
        print(f"  - Top 3 Features: {', '.join(top_features)}")

    # Model artifacts
    artifacts = result.get("model_artifacts", {})
    if artifacts and isinstance(artifacts, dict):
        print(f"  - Model saved: {'Yes' if 'model_file' in artifacts else 'No'}")

    return result




def train_with_hyperparameters():
    """Train model with custom hyperparameters."""
    print("🔬 Training ML model with custom hyperparameters...")

    # Load the FlowerPower project
    project = FlowerPowerProject.load(str(project_root))

    # Override hyperparameters for experimentation
    custom_config = {
        "algorithm": "gradient_boosting",
        "enable_feature_selection": True,
        "cross_validation": True,
    }

    custom_inputs = {
        "hyperparameters": {
            "n_estimators": 200,
            "max_depth": 5,
            "learning_rate": 0.1,
            "random_state": 42,
        }
    }

    # Run with custom configuration
    result = project.run("customer_churn", config=custom_config, inputs=custom_inputs)

    print("✅ Custom hyperparameter training completed!")

    # Show comparison with default
    evaluation = result.get("model_evaluation", {})
    test_perf = evaluation.get("test_performance", {})
    print(f"📊 Custom Model Performance:")
    print(f"  - Algorithm: Gradient Boosting")
    print(
        f"  - Test Accuracy: {test_perf.get('accuracy', 'N/A'):.4f}"
        if isinstance(test_perf.get("accuracy"), float)
        else f"  - Test Accuracy: {test_perf.get('accuracy', 'N/A')}"
    )

    return result


@app.command()
def sync():
    """Run training pipeline synchronously."""
    run_synchronous()




@app.command()
def custom():
    """Train with custom hyperparameters."""
    train_with_hyperparameters()


def main():
    """Main entry point for the Typer CLI application."""
    app()


if __name__ == "__main__":
    main()
