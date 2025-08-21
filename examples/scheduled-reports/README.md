# Scheduled Reports Example

This example demonstrates automated business reporting using FlowerPower's scheduling capabilities, showcasing dashboard generation, KPI tracking, and alert systems.

## Prerequisites

- Python 3.11+
- Redis (for job queue functionality)

## Quick Start

All commands should be run from the `examples/scheduled-reports` directory.

### 1. Run Synchronously

Execute the pipeline directly. Ideal for development and testing.

**Using the script:**
```bash
uv run scripts/run_example.py sync
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower pipeline run business_dashboard
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.run("business_dashboard")
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
uv run flowerpower job-queue enqueue-pipeline business_dashboard
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.enqueue("business_dashboard")
```

**Terminal 2: Start Worker**
```bash
uv run flowerpower job-queue start-worker --queue-names reports
```

### 3. Schedule a Pipeline Run

Schedule the pipeline to run at a predefined time (e.g., monthly on the 1st at 9 AM).

**Terminal 1: Schedule Job**

**Using the script:**
```bash
uv run scripts/run_example.py schedule
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower job-queue schedule-pipeline business_dashboard --cron "0 9 1 * *"
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.schedule("business_dashboard", cron="0 9 1 * *")
```

**Terminal 2: Start Worker with Scheduler**
```bash
uv run flowerpower job-queue start-worker --with-scheduler
```

## Project Structure

```
scheduled-reports/
├── conf/
│   ├── project.yml               # Project-level configuration
│   └── pipelines/
│       └── business_dashboard.yml  # Pipeline-specific configuration
├── data/
│   ├── sales_data.csv           # Sample sales data
│   ├── inventory_data.csv       # Sample inventory data
│   └── customer_data.csv        # Sample customer data
├── pipelines/
│   └── business_dashboard.py    # Pipeline implementation
├── reports/                     # Generated reports (created automatically)
└── scripts/
    └── run_example.py           # Script to run the example
```

## Key Components

- **Pipeline Configuration (`conf/pipelines/business_dashboard.yml`):** Defines parameters for data sources, reporting periods, KPI thresholds, and output settings.
- **Pipeline Implementation (`pipelines/business_dashboard.py`):** Contains the core business logic, including functions for data loading, KPI calculation, visualization, and report generation.

## Configuration Options

You can customize the pipeline's behavior by editing `conf/pipelines/business_dashboard.yml`:

- **`sales_file`, `inventory_file`, `customer_file`**: Paths to input data files.
- **`report_frequency`**: Reporting period (daily, weekly, monthly, quarterly).
- **`output_format`**: Report format (html, pdf, excel).
- **`include_charts`**: Whether to generate visualizations.
- **`sales_target_monthly`, `low_inventory_threshold`, `customer_retention_target`**: KPI thresholds for alerts.

## Expected Output

Running the pipeline generates a business dashboard HTML report with KPIs, charts, and alerts. The report is saved to the `reports/` directory with a timestamp.

## FlowerPower Features Demonstrated

- **Configuration-Driven Pipelines**: Customize pipeline behavior without changing code.
- **Multiple Execution Modes**: Run pipelines synchronously, via a job queue, or on a schedule.
- **Business Intelligence**: KPI calculation, threshold monitoring, and alert generation.
- **Report Generation**: HTML dashboard creation with interactive visualizations.

## Customizing the Example

- **Use Different Data**: Modify the data loading functions in `pipelines/business_dashboard.py` and update the configuration.
- **Add New KPIs**: Create new calculation functions and include them in the dashboard.
- **Change Report Format**: Modify the output format and styling in the pipeline implementation.
- **Adjust Schedules**: Edit the cron expression to change when reports are generated.

## Troubleshooting

- **`FileNotFoundError`**: Ensure you are in the correct directory and the data files exist in the `data/` directory.
- **Redis Connection Error**: Make sure the Redis server is running before using the job queue.
- **Missing Dependencies**: Install required packages with `uv pip install -r requirements.txt`.
- **Permission Denied**: Check write permissions for the `reports/` directory.

## Learning Path & Related Examples

- [`data-etl-pipeline`](../data-etl-pipeline/): Data preprocessing and validation
- [`ml-training-pipeline`](../ml-training-pipeline/): Predictive analytics and ML
- [`pipeline-only-example`](../pipeline-only-example/): Lightweight report generation