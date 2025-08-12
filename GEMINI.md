# FlowerPower Project Overview

FlowerPower is a Python framework designed for building, configuring, scheduling, and executing data processing pipelines. It promotes a modular, configuration-driven approach, leveraging Hamilton for defining dataflows and integrating with job queue systems like APScheduler and RQ for orchestration. The project emphasizes flexibility, extensibility, and ease of use for various data processing tasks.

## Key Features:
*   **Modular Pipeline Design:** Utilizes Hamilton for defining data processing logic as Directed Acyclic Graphs (DAGs) within Python modules.
*   **Configuration-Driven:** Pipeline parameters, execution logic, and scheduling are defined declaratively using YAML files.
*   **Job Queue Integration:** Supports APScheduler for time-based scheduling and RQ (Redis Queue) for distributed task queues.
*   **Extensible I/O Plugins:** Connects to various data sources and destinations (CSV, JSON, Parquet, DeltaTable, DuckDB, PostgreSQL, MySQL, MSSQL, Oracle, MQTT, SQLite, etc.).
*   **Multiple Interfaces:** Provides a Command Line Interface (CLI) for running, managing, and inspecting pipelines, and a Web UI (Hamilton UI) for monitoring.
*   **Filesystem Abstraction:** Simplifies file handling across local and remote filesystems (e.g., S3, GCS).
*   **Database Management:** Uses Alembic for database migrations, primarily with SQLite for managing project context, decisions, and progress.

## Project Structure:
*   `src/flowerpower/`: Core Python source code for the FlowerPower framework.
*   `conf/`: Configuration files for projects and pipelines.
*   `pipelines/`: Directory for defining pipeline logic.
*   `tests/`: Unit and integration tests for the framework.
*   `docker/`: Docker-related files, including `docker-compose.yml` for local development environment setup.
*   `docs/`: Project documentation.
*   `alembic/`: Database migration scripts and configuration.
*   `scripts/`: Utility scripts, including the test runner.

## Building and Running:

FlowerPower uses `uv` for dependency management and building.

### Installation:
It is recommended to use `uv` for installing FlowerPower and managing project environments.

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate # Or .\.venv\Scripts\activate on Windows

# Install FlowerPower
uv pip install flowerpower

# Optional: Install additional dependencies for specific features
uv pip install flowerpower[apscheduler,rq] # Example for APScheduler and RQ
uv pip install flowerpower[io] # Example for I/O plugins
uv pip install flowerpower[ui] # Example for Hamilton UI
uv pip install flowerpower[all] # Install all optional dependencies
```

### Project Initialization:
To set up a new FlowerPower project:

```bash
flowerpower init --name my-flowerpower-project
cd my-flowerpower-project
```

### Running Pipelines:

#### Synchronous Execution (CLI):
```bash
flowerpower pipeline run hello_world --base_dir .
```

#### Asynchronous Execution (Job Queues):
Ensure the required job queue backend (e.g., Redis for RQ) is running.

```bash
# Add job to queue (non-blocking)
flowerpower pipeline add-job hello_world --base_dir .

# Start job queue worker
flowerpower job-queue start-worker --base_dir .
```

### Local Development Environment (Docker):
A comprehensive `docker-compose.yml` is provided in the `docker/` directory to set up services like Redis, PostgreSQL, MQTT, Minio, Hamilton UI, etc.

```bash
cd docker
docker-compose up -d redis postgres # Example: Start Redis and PostgreSQL
```

### Testing:
Tests are run using `pytest` with `pytest-cov` for code coverage.

```bash
./scripts/test.sh
```

### Building and Publishing (CI/CD):
The project uses GitHub Actions for building and publishing to PyPI. The build process involves:

```bash
uv sync
uv build --sdist --wheel
uv publish --token $PYPI_TOKEN
```

## Development Conventions:
*   **Dependency Management:** `uv` is used for managing Python dependencies.
*   **Code Formatting & Linting:** `ruff` and `isort` are listed as development dependencies, suggesting their use for code quality. `.pre-commit-config.yaml` is present, indicating pre-commit hooks are used to enforce code style.
*   **Testing:** `pytest` is the chosen testing framework.
*   **Database Migrations:** `Alembic` is used for managing database schema changes.
