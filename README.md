<div align="center">
  <h1>FlowerPower 🌸</h1>
  <h3>Simple Workflow Framework - Hamilton + APScheduler = FlowerPower</h3>
  <img src="./image.png" alt="FlowerPower Logo" width="400" height="300">
</div>

A powerful and flexible data pipeline framework that simplifies data processing workflows, job scheduling, and event-driven architectures. FlowerPower combines modern data processing capabilities with robust job queue management and MQTT integration.

## ✨ Features

### Core Features
- 📊 **Pipeline Management**: Build and run data processing pipelines with support for multiple data formats and computation engines
- 🔄 **Job Queue Integration**: Support for multiple job queue backends (RQ, APScheduler)
- 📡 **MQTT Integration**: Built-in support for MQTT-based event processing
- 🎯 **Resilient Execution**: Automatic retries with configurable backoff and jitter
- 📊 **Data Format Support**: Work with CSV, JSON, Parquet files and more
- 🗄️ **Database Connectivity**: Connect to PostgreSQL, MySQL, SQLite, DuckDB, Oracle, and MSSQL

### Additional Features
- 🛠️ **CLI Tools**: Comprehensive command-line interface for all operations
- 📈 **Pipeline Visualization**: DAG visualization for pipeline understanding
- 🔍 **Monitoring**: Integration with OpenTelemetry for observability
- 🐳 **Docker Support**: Ready-to-use Docker configurations

## 🚀 Quick Start

### Installation

```bash
# Change into the folder, where you want to initialize a new flowerpower project
cd project/root/folder

# Creaet a new flowerpower project using the current github main branch
uvx --prerelease allow git+https://github.com/legout/flowerpower init --name hello-world-project

# Change into the flowerpower project folder
cd hello-world-project

# init uv and add the latest flowerpower version from github
uv init --base --no-readme
uv add git+https://github.com/legout/flowerpower --prerelease allow

uv run flowerpower pipeline new hello-world

```

### Create Your First Pipeline

1. Initialize a new project:
```bash
flowerpower init --name my-first-project
```

2. Create a simple pipeline in `pipelines/hello_world.py`:
```python
import pandas as pd

def load_data() -> pd.DataFrame:
    """Load sample data"""
    return pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35]
    })

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Add a greeting column"""
    df['greeting'] = 'Hello, ' + df['name']
    return df

def save_output(df: pd.DataFrame) -> None:
    """Save the processed data"""
    print(df)
```

3. Run the pipeline:
```bash
flowerpower pipeline run hello_world
```

## 💡 Key Concepts

### Pipeline Management

Pipelines are the core building blocks of FlowerPower. They can be:
- Run directly
- Scheduled
- Triggered by MQTT messages
- Executed as background jobs

```bash
# Run a pipeline
flowerpower pipeline run my_pipeline --inputs '{"source": "data.csv"}'

# Schedule a pipeline
flowerpower pipeline schedule my_pipeline --cron "0 * * * *"

# Show pipeline structure
flowerpower pipeline show-dag my_pipeline
```

### Job Queue Integration

FlowerPower supports multiple job queue backends:

```bash
# Start a worker with RQ backend
flowerpower job-queue start-worker --type rq

# Start APScheduler worker
flowerpower job-queue start-worker --type apscheduler

# Add a job with retry configuration
flowerpower job-queue add-job my_pipeline \
  --max-retries 3 \
  --retry-delay 2.0 \
  --jitter-factor 0.1
```

### MQTT Integration

Connect your pipelines to MQTT message brokers:

```bash
# Run a pipeline when messages arrive
flowerpower mqtt run-pipeline-on-message my_pipeline \
  --topic "sensors/data" \
  --max-retries 3 \
  --retry-delay 1.0

# Start a custom message listener
flowerpower mqtt start-listener \
  --on-message process_message \
  --topic "events/#"
```

## 📁 Project Structure

```
my-project/
├── conf/
│   ├── project.yml          # Project configuration
│   └── pipelines/          # Pipeline configurations
│       └── my_pipeline.yml
├── pipelines/              # Pipeline implementations
│   └── my_pipeline.py
└── data/                   # Data files (optional)
```

## 🔌 Data Connectors

### Supported File Formats
- CSV
- JSON
- Parquet
- Pydala Datasets

### Supported Databases
- PostgreSQL
- MySQL
- SQLite
- Oracle
- Microsoft SQL Server
- DuckDB

## 🐳 Docker Support

Run FlowerPower in containers:

```bash
cd docker
docker-compose up
```

The Docker setup includes:
- Python worker environment
- MQTT broker (Mosquitto)
- Built-in configuration

## 🛠️ Configuration

### Pipeline Configuration
```yaml
# conf/pipelines/my_pipeline.yml
name: my_pipeline
description: Example pipeline configuration
inputs:
  source_data:
    type: csv
    path: data/input.csv
outputs:
  processed_data:
    type: parquet
    path: data/output.parquet
```

### Job Queue Configuration
```yaml
# conf/project.yml
job_queue:
  type: rq  # or apscheduler
  redis_url: redis://localhost:6379
  max_retries: 3
  retry_delay: 1.0
```

## 📚 API Documentation

Visit our [API Documentation](docs/api.md) for detailed information about:
- Pipeline API
- Job Queue API
- MQTT Integration
- Data Connectors
- Configuration Options

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test category
pytest tests/test_pipeline/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Hamilton](https://github.com/DAGWorks-Inc/hamilton) for pipeline execution
- Uses [RQ](https://python-rq.org/) and [APScheduler](https://apscheduler.readthedocs.io/) for job queues
- MQTT support via [Paho MQTT](https://www.eclipse.org/paho/)
- Database connectivity through SQLAlchemy and native connectors
