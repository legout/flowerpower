# Web Scraping Pipeline Example

This example demonstrates concurrent web scraping and content processing using FlowerPower, covering multi-source data extraction, parallel HTTP requests, and content analysis.

## Prerequisites

- Python 3.11+
- Redis (for job queue functionality)

## Quick Start

All commands should be run from the `examples/web-scraping-pipeline` directory.

### 1. Run Synchronously

Execute the pipeline directly. Ideal for development and testing.

**Using the script:**
```bash
uv run scripts/run_example.py sync
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower pipeline run news_scraper
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.run("news_scraper")
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
uv run flowerpower job-queue enqueue-pipeline news_scraper
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.enqueue("news_scraper")
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
uv run flowerpower job-queue schedule-pipeline news_scraper --cron "0 6 * * *"
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.schedule("news_scraper", cron="0 6 * * *")
```

**Terminal 2: Start Worker with Scheduler**
```bash
uv run flowerpower job-queue start-worker --with-scheduler
```

## Project Structure

```
web-scraping-pipeline/
├── conf/
│   ├── project.yml          # Project-level configuration
│   └── pipelines/
│       └── news_scraper.yml # Pipeline-specific configuration
├── data/                   # Sample configuration data
├── output/                 # Scraped content (created automatically)
├── pipelines/
│   └── news_scraper.py     # Pipeline implementation
└── scripts/
    └── run_example.py      # Script to run the example
```

## Key Components

- **Pipeline Configuration (`conf/pipelines/news_scraper.yml`):** Defines target sites, scraping parameters, content processing options, and filtering rules.
- **Pipeline Implementation (`pipelines/news_scraper.py`):** Contains the core scraping logic, including functions for concurrent requests, content parsing, and data processing.

## Configuration Options

You can customize the pipeline's behavior by editing `conf/pipelines/news_scraper.yml`:

- **`target_sites`**: Specify URLs to scrape with their content types (HTML, JSON, XML).
- **`scraping_config`**: Set concurrency limits, request delays, timeouts, and retry logic.
- **`content_processing`**: Configure NLP features like keyword extraction, sentiment analysis, and language detection.
- **`filtering`**: Define inclusion/exclusion keywords and content quality rules.

## Expected Output

Running the pipeline generates scraped articles with metadata, processing statistics, and content analysis results. The output is saved to timestamped JSON files in the `output/` directory.

## FlowerPower Features Demonstrated

- **Configuration-Driven Pipelines**: Customize scraping behavior without changing code.
- **Multiple Execution Modes**: Run synchronously, via a job queue, or on a schedule.
- **Concurrent Processing**: Parallel HTTP requests with rate limiting and retry logic.
- **Content Analysis**: Built-in text processing and filtering capabilities.

## Customizing the Example

- **Add New Sites**: Update `target_sites.urls` in the configuration with new URLs and selectors.
- **Modify Processing Logic**: Adjust the content processing functions in `pipelines/news_scraper.py`.
- **Change Filtering Rules**: Update the `filtering` section in the configuration to refine content selection.

## Troubleshooting

- **HTTP Errors**: Check network connectivity and site availability.
- **Rate Limiting**: Reduce `max_concurrent_requests` and increase `request_delay` in the configuration.
- **Redis Connection Error**: Make sure the Redis server is running before using the job queue.
- **Permission Denied**: Check write permissions for the `output/` directory.

## Learning Path & Related Examples

- [`data-etl-pipeline`](../data-etl-pipeline/): Data preprocessing and validation patterns.
- [`scheduled-reports`](../scheduled-reports/): Automated reporting and scheduling workflows.
- [`pipeline-only-example`](../pipeline-only-example/): Lightweight content processing examples.