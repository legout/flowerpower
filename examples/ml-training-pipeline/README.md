# ML Training Pipeline Example

This example demonstrates a machine learning training workflow using FlowerPower, covering data preprocessing, feature engineering, model training, and evaluation.

## Prerequisites

- Python 3.11+

## Quick Start

All commands should be run from the `examples/ml-training-pipeline` directory.

### 1. Run Synchronously

Execute the pipeline directly. Ideal for development and testing.

**Using the script:**
```bash
uv run scripts/run_example.py sync
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower pipeline run customer_churn
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.run("customer_churn")
```


## Project Structure

```
ml-training-pipeline/
├── conf/
│   ├── project.yml          # Project-level configuration
│   └── pipelines/
│       └── customer_churn.yml  # Pipeline-specific configuration
├── data/
│   └── customer_data.csv    # Sample input data
├── models/                  # Model artifacts (created automatically)
├── pipelines/
│   └── customer_churn.py    # Pipeline implementation
└── scripts/
    └── run_example.py       # Script to run the example
```

## Key Components

- **Pipeline Configuration (`conf/pipelines/customer_churn.yml`):** Defines parameters for data sources, feature engineering, model selection, and evaluation metrics.
- **Pipeline Implementation (`pipelines/customer_churn.py`):** Contains the ML training logic, including functions for data preprocessing, feature engineering, model training, and evaluation.

## Configuration Options

You can customize the pipeline's behavior by editing `conf/pipelines/customer_churn.yml`:

- **`data_source`**: Specify input file path, target column, and data splitting parameters.
- **`feature_engineering`**: Define categorical and numerical columns and scaling options.
- **`model_config`**: Select the algorithm and set hyperparameters.
- **`evaluation`**: Configure cross-validation and scoring metrics.

## Expected Output

Running the pipeline generates a trained model, evaluation metrics, feature importance scores, and saved model artifacts in the `models/` directory.

## FlowerPower Features Demonstrated

- **Configuration-Driven ML Pipelines**: Customize model training without changing code.
- **Synchronous Execution**: Run training pipelines directly for development and testing.
- **ML-Specific Functions**: Use Hamilton's features for clear and modular ML workflows.

## Customizing the Example

- **Use Different Data**: Modify the `raw_data()` function in `pipelines/customer_churn.py` and update the configuration.
- **Add New Algorithms**: Extend the `trained_model()` function with additional ML algorithms.
- **Custom Feature Engineering**: Modify the `engineered_features()` function to implement new transformations.

## Troubleshooting

- **`FileNotFoundError`**: Ensure you are in the correct directory and the `data/customer_data.csv` file exists.
- **Model Training Issues**: Check that all required ML dependencies are installed.

## Learning Path & Related Examples

- [`data-etl-pipeline`](../data-etl-pipeline/): Data preprocessing and validation patterns.
- [`pipeline-only-example`](../pipeline-only-example/): Lightweight ML experimentation.