<div align="center">
  <h1>FlowerPower</h1>
  <h3>Simple Workflow Framework - Hamilton + APScheduler = FlowerPower</h3>
  <img src="./image.png" alt="FlowerPower Logo" width="600" height="400">
</div>

---

## 📚 Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
   - [Initialize Project](#initialize-project)
   - [Add Pipeline](#add-pipeline)
   - [Setup Pipeline](#setup-pipeline)
   - [Run Pipeline](#run-pipeline)
   - [Schedule Pipeline](#schedule-pipeline)
   - [Start Worker](#start-worker)
   - [Track Pipeline](#track-pipeline)
4. [Development](#development)
   - [Dev Services](#dev-services)

---

## 🔍 Overview

FlowerPower is a simple workflow framework based on two fantastic Python libraries:

- **[Hamilton](https://github.com/DAGWorks-Inc/hamilton)**: Creates DAGs from your pipeline functions
- **[APScheduler](https://github.com/agronholm/apscheduler)**: Handles pipeline scheduling

### Key Features

- 🔄 **Pipeline Workflows**: Create and execute complex DAG-based workflows
- ⏰ **Scheduling**: Run pipelines at specific times or intervals
- ⚙️ **Parameterization**: Easily configure pipeline parameters
- 📊 **Tracking**: Monitor executions with Hamilton UI
- 🛠️ **Flexible Configuration**: Simple YAML-based setup
- 📡 **Distributed Execution**: Support for distributed environments

[More details in Hamilton docs](https://hamilton.dagworks.io/en/latest/)

---

## 📦 Installation

```bash
# Basic installation
pip install flowerpower

# With scheduling support
pip install "flowerpower[scheduler]"

# Additional components
pip install "flowerpower[mqtt]"     # MQTT broker
pip install "flowerpower[redis]"    # Redis broker
pip install "flowerpower[mongodb]"  # MongoDB store
pip install "flowerpower[ray]"      # Ray computing
pip install "flowerpower[dask]"     # Dask computing
pip install "flowerpower[ui]"       # Hamilton UI
pip install "flowerpower[websever]" # Web server
```

---

## 🚀 Getting Started

### Initialize Project

**Option 1: Command Line**
```bash
flowerpower init new-project
cd new-project
```

**Option 2: Python**
```python
from flowerpower import init
init("new-project")
```

This creates basic config files:
- `conf/project.yml`


### 📦 Optional: Project Management with UV (Recommended)

It is recommended to use the project manager `uv` to manage your project dependencies.

**Installation**
```bash
pip install uv
```
> For more installation options, visit: https://docs.astral.sh/uv/getting-started/installation/

**Project Initialization**
```bash
uv init --app --no-readme --vcs git
```
---

### Pipeline Management

#### Creating a New Pipeline

**Option 1: Command Line**
```bash
flowerpower new my_flow
```

**Option 2: Python**
```python
# Using PipelineManager
from flowerpower.pipeline import PipelineManager
pm = PipelineManager()
pm.new("my_flow")

# Or using the new function directly
from flowerpower.pipeline import new
new("my_flow")
```

This creates the new pipeline and configuration file:
- `pipelines/my_flow.py`
- `conf/pipelines/my_flow.yml`

#### Setting Up a Pipeline

1. **Add Pipeline Functions**
Build your pipeline by adding the functions (nodes) to `pipelines/my_flow.py` that build the DAG, following the Hamilton paradigm.

2. **Parameterize Functions**

You can parameterize functions in two ways:

**Method 1: Default Values**
```python
def add_int_col(
    df: pd.DataFrame,
    col_name: str = "foo",
    values: str = "bar"
) -> pd.DataFrame:
    return df.assign(**{col_name: values})
```

**Method 2: Configuration File**

In `conf/pipelines/my_flow.yml`:
```yaml
...
func:
  add_int_col:
    col_name: foo
    values: bar
...
```

Add the `@parameterize` decorator to the function in your pipeline file:
```python
@parameterize(**PARAMS.add_int_col)
def add_int_col(
    df: pd.DataFrame,
    col_name: str,
    values: int
) -> pd.DataFrame:
    return df.assign(**{col_name: values})
```

---

### Running Pipelines

#### Configuration

You can configure the pipeline parameters `inputs`, and `final_vars`, and other parameters in the pipeline
configuration file `conf/pipelines/my_flow.yml` or directly in the pipeline execution function.

#### Using the Pipeline Configuration
```yaml
...
run:
  inputs:
    data_path: path/to/data.csv
    fs_protocol: local
  final_vars: [add_int_col, final_df]
  # optional parameters
  with_tracker: false
  executor: threadpool # or processpool, ray, dask
...
```

#### Execution Methods
There are three ways to execute a pipeline:

1. **Direct Execution**
   - Runs in current process
   - No data store required

2. **Job Execution**
   - Runs as APScheduler job
   - Returns job results
   - Requires data store and event broker

3. **Async Job Addition**
   - Adds to APScheduler
   - Returns job ID
   - Results retrievable from data store


#### Command Line Usage
```bash
# Note: add --inputs and --final-vars and other optional parameters if not specified in the config file
# Direct execution
flowerpower run my_flow
# Job execution
flowerpower run-job my_flow

# Add as scheduled job
flowerpower add-job my_flow
```

You can also use the `--inputs` and `--final-vars` flags to override the configuration file parameters or if they are not specified in the configuration file.

```bash
flowerpower run my_flow \
    --inputs data_path=path/to/data.csv,fs_protocol=local \
    --final-vars final_df \
    --executor threadpool
    --without-tracker
```

#### Python Usage
```python
from flowerpower.pipeline import Pipeline, run, run_job, add_job

# Using Pipeline class
p = Pipeline("my_flow")
# Note: add inputs, final_vars, and other optional arguments if not specified in the config file
result = p.run()
result = p.run_job()
job_id = p.add_job()

# Using functions
result = run("my_flow")
result = run_job("my_flow")
job_id = add_job("my_flow")
```

You can also use the `inputs` and `final-vars` arguments to override the configuration file parameters or if they are not specified in the configuration file.

```python
result = run(
    "my_flow",
    inputs={
        "data_path": "path/to/data.csv",
        "fs_protocol": "local"
    },
    final_vars=["final_df"],
    executor="threadpool",
    with_tracker=False
)
```

---
## ⏰ Scheduling Pipelines

### Setting Up Schedules

#### Command Line Options

```bash
# Run every 30 seconds
flowerpower schedule my_flow \
    --type interval \
    --interval-params seconds=30

# Run at specific date/time
flowerpower schedule my_flow \
    --type date \
    --date-params year=2022,month=1,day=1,hour=0,minute=0,second=0

# Run with cron parameters
flowerpower schedule my_flow \
    --type cron \
    --cron-params second=0,minute=0,hour=0,day=1,month=1,day_of_week=0

# Run with crontab expression
flowerpower schedule my_flow \
    --type cron \
    --crontab "0 0 1 1 0"
```

#### Python Usage
```python
from flowerpower.scheduler import schedule, Pipeline

# Using Pipeline class
p = Pipeline("my_flow")
p.schedule("interval", seconds=30)

# Using schedule function
schedule("my_flow", "interval", seconds=30)
```

---

## 👷 Worker Management

### Starting a Worker

**Command Line**
```bash
flowerpower start-worker
```

**Python**
```python
# Using the SchedulerManager class
from flowerpower.scheduler import SchedulerManager
sm = SchedulerManager()
sm.start_worker()

# Using the start_worker function
from flowerpower.scheduler import start_worker
start_worker()
```

### Worker Configuration

Configure your worker in `conf/project.yml`:

```yaml
# PostgreSQL Configuration
data_store:
  type: postgres
  uri: postgresql+asyncpq://user:password@localhost:5432/flowerpower

# Redis Event Broker
event_broker:
  type: redis
  uri: redis://localhost:6379
  # Alternative configuration:
  # host: localhost
  # port: 6379
```

#### Alternative Data Store Options

**SQLite**
```yaml
data_store:
  type: sqlite
  uri: sqlite+aiosqlite:///flowerpower.db
```

**MySQL**
```yaml
data_store:
  type: mysql
  uri: mysql+aiomysql://user:password@localhost:3306/flowerpower
```

**MongoDB**
```yaml
data_store:
  type: mongodb
  uri: mongodb://localhost:27017/flowerpower
```

**In-Memory**
```yaml
data_store:
  type: memory
```

#### Alternative Event Broker Options

**MQTT**
```yaml
event_broker:
  type: mqtt
  host: localhost
  port: 1883
  username: user  # optional if required
  password: supersecret  # optional if required
```
**Redis**
```yaml
event_broker:
  type: redis
  uri: redis://localhost:6379
  # Alternative configuration:
  # host: localhost
  # port: 6379
```

**In-Memory**
```yaml
event_broker:
  type: memory
```

---

## 📊 Pipeline Tracking

### Hamilton UI Setup

#### Local Installation
```bash
# Install UI package
pip install "flowerpower[ui]"

# Start UI server
flowerpower hamilton-ui
```
> Access the UI at: http://localhost:8241

#### Docker Installation
```bash
# Clone Hamilton repository
git clone https://github.com/dagworks-inc/hamilton
cd hamilton/ui

# Start UI server
./run.sh
```
> Access the UI at: http://localhost:8242

### Tracker Configuration

Configure tracking in `conf/project.yml`:

```yaml
username: my_email@example.com
api_url: http://localhost:8241
ui_url: http://localhost:8242
api_key: optional_key
```

And  specify the `tracker` parameter in the pipeline configuration `conf/pipelines/my_flow.yml:

```yaml
...
tracker:
  project_id: 1
  tags:
    environment: dev
    version: 1.0
  dag_name: my_flow_123
...
```

---

## 🛠️ Development Services

### Local Development Setup

Download the docker-compose configuration:
```bash
curl -O https://raw.githubusercontent.com/legout/flowerpower/main/docker/docker-compose.yml
```

### Starting Services

```bash
# MQTT Broker (EMQX)
docker-compose up mqtt -d

# Redis
docker-compose up redis -d

# MongoDB
docker-compose up mongodb -d

# PostgreSQL
docker-compose up postgres -d
```

---

## 📝 License

[MIT License](LICENSE)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📫 Support

For support, please open an issue in the GitHub repository.
