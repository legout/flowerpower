# FlowerPower Library Analysis Summary

**Date:** 2025-04-30

**Analysis Goal:** To gain a deep understanding of the `flowerpower` Python library located in `src/flowerpower/`, using `examples/` for context.

**Methodology:**
1.  Analyzed source code structure (`src/flowerpower/`) using `agent-research`.
2.  Analyzed example usage (`examples/`) using `agent-research`.
3.  Synthesized findings.

**Synthesized Understanding:**

`flowerpower` is a Python framework designed for building, configuring, scheduling, and executing data processing pipelines. It promotes a modular and configuration-driven approach.

**Core Architecture & Components:**

*   **`pipeline/`:** Contains the central logic for defining, managing, running, and visualizing data pipelines.
*   **`plugins/`:** Provides extensibility, primarily for Input/Output (I/O). It includes loaders and savers for various data formats (CSV, JSON, Parquet, DeltaTable) and systems (DuckDB, PostgreSQL, MySQL, MSSQL, Oracle, MQTT, SQLite), allowing pipelines to connect to diverse data sources and destinations.
*   **`cfg/`:** Manages configuration loading and parsing. It handles settings defined in YAML files for the overall project, individual pipelines (including run parameters and scheduling), and the chosen job queue system.
*   **`job_queue/`:** Abstracts the task execution backend. It supports different systems like APScheduler (for scheduled jobs, potentially in-process or using backends like PostgreSQL) and RQ (Redis Queue, for distributed task queues), allowing users to choose the appropriate backend for their needs.
*   **`cli/`:** Offers command-line interface tools for interacting with the framework, likely for running pipelines, managing jobs, and handling configurations.
*   **`web/`:** Includes a web application component (using HTML templates, suggesting a framework like Flask or FastAPI) providing a graphical user interface for managing and monitoring pipelines and schedules.
*   **`fs/`:** Provides a filesystem abstraction layer, likely simplifying interactions with different storage systems.
*   **`utils/`:** Contains miscellaneous utility functions supporting various parts of the library (logging, SQL interactions, etc.).

**Typical Workflow & Usage (Based on Examples):**

1.  **Project Setup:** Users configure project-level settings in `conf/project.yml`. This is where the primary `job_queue` type (`apscheduler` or `rq`) and its specific backend details (e.g., database connection string, Redis URL) are defined.
2.  **Pipeline Definition (YAML):** Individual pipelines are defined in separate YAML files within `conf/pipelines/`. These files specify pipeline-specific parameters (`params`), run configurations (`run`), and scheduling details (`schedule` using cron, interval, or specific dates).
3.  **Pipeline Implementation (Python):** The actual pipeline logic is written in Python scripts (e.g., within `pipelines/*.py`). These scripts often leverage the Hamilton library for defining dataflows. They use `flowerpower`'s configuration system (e.g., `Config.load()`) and decorators (`@parameterize`, `@config.when`) to link the Python code with the parameters and settings defined in the corresponding YAML files.

**Key Features & Takeaways:**

*   **Modularity:** The library is highly modular, allowing users to swap job queue backends (APScheduler vs. RQ) and easily extend I/O capabilities via plugins without changing core pipeline logic.
*   **Configuration-Driven:** Pipeline behavior, parameters, and scheduling are primarily controlled through YAML configuration files, separating configuration from code.
*   **Job Scheduling/Queuing:** Provides built-in support for different asynchronous execution models suitable for various use cases (scheduled tasks vs. distributed queues).
*   **Multiple Interfaces:** Offers both a CLI and a Web UI for interacting with pipelines.
*   **Hamilton Integration:** The examples suggest a strong integration or reliance on the Hamilton library for defining the actual data transformations within the Python pipeline scripts.

**Conclusion:**

`flowerpower` provides the infrastructure and conventions to define data pipelines in Python (likely using Hamilton), configure their parameters and scheduling in YAML, and run them using different scheduling/queuing backends via either a command line or a web interface. This document summarizes the initial analysis and can be used as context for future tasks related to this library.