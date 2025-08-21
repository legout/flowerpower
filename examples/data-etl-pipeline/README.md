# Data ETL Pipeline Example

This example demonstrates a standard ETL (Extract, Transform, Load) workflow using FlowerPower, covering data validation, cleaning, and aggregation.

## Prerequisites

- Python 3.11+
- Redis (for job queue functionality)

## Quick Start

All commands should be run from the `examples/data-etl-pipeline` directory.

### 1. Run Synchronously

Execute the pipeline directly. Ideal for development and testing.

**Using the script:**
```bash
uv run scripts/run_example.py sync
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower pipeline run sales_etl
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.run("sales_etl")
```

### 2. Run with the Job Queue

Add the pipeline run as a job to be processed asynchronously.

**Terminal 1: Enqueue Job**

**Using the script:**
```bash
uv run scripts/run_example.py queue
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower job-queue enqueue-pipeline sales_etl
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.enqueue("sales_etl")
```

**Terminal 2: Start Worker**
```bash
uv run flowerpower job-queue start-worker
```

### 3. Schedule a Pipeline Run

Schedule the pipeline to run at a predefined time (e.g., daily at 6 AM).

**Terminal 1: Schedule Job**

**Using the script:**
```bash
uv run scripts/run_example.py schedule
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower job-queue schedule-pipeline sales_etl --cron "0 6 * * *"
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.schedule("sales_etl", cron="0 6 * * *")
```

**Terminal 2: Start Worker with Scheduler**
```bash
uv run flowerpower job-queue start-worker --with-scheduler
```

## Project Structure

```
data-etl-pipeline/
├── conf/
│   ├── project.yml          # Project-level configuration
│   └── pipelines/
│       └── sales_etl.yml    # Pipeline-specific configuration
├── data/
│   └── sales_data.csv       # Sample input data
├── pipelines/
│   └── sales_etl.py         # Pipeline implementation
└── scripts/
    └── run_example.py       # Script to run the example
```

## Key Components

- **Pipeline Configuration (`conf/pipelines/sales_etl.yml`):** Defines parameters for data sources, validation rules, and aggregation logic.
- **Pipeline Implementation (`pipelines/sales_etl.py`):** Contains the core ETL logic, including functions for loading, cleaning, and summarizing data.

## Configuration Options

You can customize the pipeline's behavior by editing `conf/pipelines/sales_etl.yml`:

- **`data_source`**: Specify input and output file paths.
- **`validation`**: Set rules for data quality checks (e.g., price ranges, required columns).
- **`aggregation`**: Define how data is grouped and which metrics are calculated.
- **`run.config`**: Toggle features like data validation and saving intermediate results.

## Expected Output

Running the pipeline generates a validation report, a cleaned dataset, and a sales summary. If `save_intermediate` is enabled in the configuration, the processed data is saved to the `data/processed/` directory.

## FlowerPower Features Demonstrated

- **Configuration-Driven Pipelines**: Customize pipeline behavior without changing code.
- **Multiple Execution Modes**: Run pipelines synchronously, via a job queue, or on a schedule.
- **Data-Centric Functions**: Use Hamilton's features for clear and modular data transformations.

## Customizing the Example

- **Use Different Data**: Modify the `raw_data()` function in `pipelines/sales_etl.py` and update the configuration in `sales_etl.yml`.
- **Add Validation**: Extend the `validation_report()` function with new checks.
- **Change Aggregations**: Adjust the `sales_summary()` function to alter grouping and metrics.

## Troubleshooting

- **`FileNotFoundError`**: Ensure you are in the correct directory and the `data/sales_data.csv` file exists.
- **Redis Connection Error**: Make sure the Redis server is running before using the job queue.
- **Permission Denied**: Check write permissions for the `data/processed/` directory.