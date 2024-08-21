<center><h1>FlowerPower</h1></center>
<center><h2>Simple Workflow Framework - Hamilton + APScheduler = FlowerPower</h2></center>

<center><img src="./image.png" alt="Bild" width="600" height="400" ></center>

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
    1. [Initialze a new flowerpower project](#initialze-a-new-flowerpower-project)
    2. [Add a new pipeline](#add-a-new-pipeline)
    3. [Setup a pipeline](#setup-a-pipeline)
    4. [Run a pipeline](#run-a-pipeline)
    5. [Schedule a pipeline](#schedule-a-pipeline)
    6. [Start a woker](#start-a-woker)
    7. [Track a pipeline](#track-a-pipeline)
    8. [Optional: Dev Services](#optional-dev-services)


## Overview
FlowerPower is a simple workflow framework based on the fantastic python libraries [Hamilton](https://github.com/DAGWorks-Inc/hamilton) and [APScheduler (Advanced Python Scheduler)](https://github.com/agronholm/apscheduler) 

**[Hamilton](https://github.com/DAGWorks-Inc/hamilton)** is used as the core engine to create Directed Acyclic Graphs (DAGs) from your pipeline functions and execute them in a controlled manner. It is highly recommended to read the [Hamilton documentation](https://hamilton.dagworks.io/en/latest/) and check out their [examples](https://github.com/DAGWorks-Inc/hamilton/examples) to understand the core concepts of FlowerPower.

**[APScheduler](https://github.com/agronholm/apscheduler)** is used to schedule the pipeline execution. You can schedule the pipeline to run at a specific time, at a specific interval or at a specific cron expression. Furthermore, APScheduler can be used to run the pipeline in a distributed environment. 


#### The main features of the FlowerPower framework are:

1. **Pipeline Workflows**: FlowerPower uses the Hamilton library to create Directed Acyclic Graphs (DAGs) from pipeline functions, allowing you to define and execute complex workflow pipelines.

2. **Scheduling and Execution**: FlowerPower integrates the APScheduler library to allow scheduling of pipeline executions at specific times, intervals, or based on cron expressions. It supports running pipelines in a distributed environment with a data store and event broker.

3. **Parameterization**: FlowerPower allows you to parameterize your pipeline functions, either by setting default values or defining parameters in a configuration file.

4. **Tracking and Monitoring**: FlowerPower can integrate with the Hamilton UI to provide tracking and monitoring of pipeline executions, including visualization of the DAG.

5. **Flexible Configuration**: FlowerPower uses configuration files (`conf/pipelines.yml`, `conf/scheduler.yml`, `conf/tracker.yml`) to set up pipelines, scheduling, and tracking, allowing for easy customization.

6. **Distributed Execution**: FlowerPower supports running pipelines in a distributed environment by using a data store (e.g., PostgreSQL, MongoDB, SQLite) to persist job information and an event broker (e.g., Redis, MQTT) for communication between the scheduler and workers.

7. **Easy Setup and Usage**: FlowerPower provides command-line tools and Python APIs for initializing new projects, adding new pipelines, running and scheduling pipelines, and starting workers.

Overall, FlowerPower aims to provide a simple and flexible workflow framework that combines the power of Hamilton and APScheduler to enable the creation and execution of complex data pipelines, with support for scheduling, distribution, and monitoring.

## Installation

```shell
pip install flowerpower 
# scheduling 
pip install "flowerpower[scheduler]" 
# mqtt event broker
pip install "flowerpower[scheduler,mqtt]" 
# redis event broker
pip install "flowerpower[scheduler,redis]" 
# mongodb data store
pip install "flowerpower[scheduler,mongodb]"
# distributed computing using ray
pip install "flowerpower[scheduler,ray]"
# dask distributed computing using dask
pip install "flowerpower[scheduler,dask]"
```

## Usage

### Initialze a new flowerpower project
In the command line, run the following command to initialize a new flowerpower project
```shell
flowerpower init new-project
cd new-project
```
This adds basic config files `conf/pipelines.yml`, `conf/scheduler.yml` and `conf/tracker.yml`

or run the following in a python script/REPL
```python
from flowerpower import init
init("new-project")
```

### Add a new pipeline
In the command line run
```shell
flowerpower add my_flow
# or
flowerpower new my_flow
```
A new file `pipelines/my_flow.py` is created and the relevant entries are added to the config files.

or run the following in a python script/REPL
```python
from flowerpower.pipeline import PipelineManager, new

# using the PipelineManager
pm = PipelineManager()
pm.new("my_flow")

# or using the new function
new("my_flow")
```

### Setup a pipeline
##### Add pipeline functions
Add the pipeline functions to `pipelines/my_flow.py`.

FlowerPower uses [Hamilton](https://github.com/DAGWorks-Inc/hamilton) that converts your pipeline functions into nodes and then creates a [Directed Acyclic Graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph).

It is therefore mandatory to write your pipeline files according to the Hamilton paradigm. You can read more about this in the Hamilton documentaion chapter [Function, Nodes and DataFlow](https://hamilton.dagworks.io/en/latest/concepts/node/)

##### Parameterize the pipeline functions

To parameterize the pipeline  functions, you can either set reasonable default values in the function definition or define the parameters in the `conf/pipelines.yml` file.

###### 1. Set default values
Set the default values in the function definition
```python
...

def add_int_col(df: pd.DataFrame, col_name: str="foo", values:str="bar") -> pd.DataFrame:
    return df.assign(**{col_name: values})

...
```
###### 2. Define the parameters in the `conf/pipelines.yml`
Add the parameters to the `conf/pipelines.yml` file
```yaml
...

params:
  my_flow:
    add_int_col:
      col_name: foo
      values: bar

...
```
and add the parameterized decorator to the function
```python
...

@parameterize(**PARAMS.add_int_col)
def add_int_col(df: pd.DataFrame, col_name: str, values:int) -> pd.DataFrame:
    return df.assign(**{col_name: values})

...
```

### Run a pipeline
A flowerpower pipeline can be run in the command line or in a python script/REPL. 

When using the `run` command or function, the pipeline is executed in the current process. Using the `run-job` command or `run_job` function, the pipeline is executed as an apscheduler job and the job results is returned. The `add-job` command or `add_job`function is used to add a pipeline as an apscheduler job and a `job_id` is returned.This `job_id`, can be used to fetch the job result from the data store. The latter two options are useful when you want to run the pipeline in a distributed environment. Note: To execute these commands, you need to have a data store and an event broker setup and a worker running.

The 

In the command line
```shell
# This runs the pipeline wihtout using the apscheduler data store
flowerpower run my_flow
# This runs the pipeline as an apscheduler job
flowerpower run-job my_flow 
# This runs the pipeline as an apscheduler job using the apscheduler data store to store the job results
flowerpower add-job my_flow 
```
In a python script/REPL
```python
from flowerpower.pipeline import Pipeline, run, run_job, add_job

# using the Pipeline class
p = Pipeline("my_flow")
res = p.run()

# or using the run function
res = run("my_flow")

# or using the run_job function
res = run_job("my_flow")

# or using the add_job function
job_id = add_job("my_flow") # job_id can be used to fetch the job result from the data store
```

The above runs the pipelines with the default parameters, which are defined in the `conf/pipelines.yml` file. 

##### Configure the pipeline run parameters
You can configure the pipeline run parameters in the `conf/pipelines.yml` file
```yaml
...

run:
  my_flow:
    # dev and prod are the run environments. You can define as many environments as you want
    dev:
      # define all the pipeline input parameters here
      inputs:
        data_path: path/to/data.csv
        fs_profile: 
        fs_prtocol: local 
      # here you define the pipeline functions, for which you want to store the final result
      final_vars: 
        [
            add_int_col,
            final_df
        ]
      # wheter to use the Hamilton UI tracker or not. Note: Hamilton UI needs to be installed and running
      with_tracker: false
    
    ...
```
##### Overwrite the default parameters
You can overwrite the default parameters by using the parameters `--inputs` and `--final-vars` in the command line
```shell
# to run the pipeline with the parameters defined in the prod environment
flowerpower run my_flow --inputs data_path=path/to/data.csv,fs_protocol=local --final-vars final_df --enviroment prod
```
or in a python script/REPL
```python
from flowerpower.pipeline import run
res=run(
    "my_flow", 
    inputs={"data_path": "path/to/data.csv", "fs_protocol": "local"}, 
    final_vars=["final_df"],
    environment="prod"
)
```

### Schedule a pipeline
You can setup a scheduler for a flowerpower pipeline to run at a specific time, at a specific interval or based on a specific cron expression. Adding a flowerpower pipeline to the scheduler is done in the command line or in a python script/REPL.

```shell
# schedule the pipeline to run every 30 seconds
flowerpower schedule my_flow --type interval --interval-params seconds=30
# schedule the pipeline to run at a specific time
flowerpower schedule my_flow --type date --date-params year=2022,month=1,day=1,hour=0,minute=0,second=0
# schedule the pipeline to run based on a cron 
flowerpower schedule my_flow --type cron --cron-params second=0,minute=0,hour=0,day=1,month=1,day_of_week=0
# schedule the pipeline to run based on a crontab expression
flowerpower schedule my_flow --type cron --crontab "0 0 1 1 0"
```
or in a python script/REPL
```python
from flowerpower.scheduler import schedule, Pipeline

# using the Pipeline class
p = Pipeline("my_flow")
p.schedule("interval", seconds=30)

# or using the schedule function
schedule("my_flow", "interval", seconds=30)
```

### Start a woker
Scheduled flowerpower pipelines or jobs added to the scheduler are executed by a worker. To start a worker, you can use the command line or a python script/REPL.

```shell
flowerpower start-worker
```
or in a python script/REPL
```python
from flowerpower.scheduler import start_worker
start_worker()
```


##### Configure the scheduler/worker
The worker can run in the current process for testing purpose. In this case, no data store or event broker is required. To run the worker in a distributed environment, you need to setup a data store and an event broker.

The scheduler/worker can be configured in the `conf/scheduler.yml` file. 

```yaml
...

data_store:
  type: postgres # postgres is  can be replaced with sqlalchemy
  uri: postgresql+asyncpq://user:password@localhost:5432/flowerpower

# other data store options

# - sqlite
# data_store:
#  type: sqlite # sqlite is can be replaced with sqlalchemy
#  uri: sqlite+aiosqlite:///flowerpower.db

# - mysql
# data_store:
#  type: mysql # mysql is can be replaced with sqlalchemy
#  uri: mysql+aiomysql://user:password@localhost:3306/flowerpower

# - mongodb
# data_store:
#   type: mongodb
#   uri: mongodb://localhost:27017/flowerpower

# - memory
# data_store:
#   type: memory

event_broker:
  type: redis
  uri: redis://localhost:6379
  # or use host and port instead of uri
  # host: localhost
  # port: 6379

# - mqtt
# event_broker:
#   type: mqtt
#   host: localhost
#   port: 1883
#   # optional username and password
#   username: edge
#   password: edge

# - memory
# event_broker:
#   type: memory

...
```

### Track a pipeline
You can track the pipeline execution using the Hamilton UI. To use the Hamilton UI, you need to install the Hamilton UI package or have a run the Hamilton UI server running. See the [Hamilton UI documentation](https://hamilton.dagworks.io/en/latest/hamilton-ui/ui/) for more information.


##### Local Hamilton UI
```shell
pip install "flowerpower[ui]"

# start the Hamilton UI server
flowerpower hamilton-ui
```
This starts the Hamilton UI server on `http://localhost:8241`. 

##### Docker-based Hamilton UI
According to the [Hamilton UI documentation](https://hamilton.dagworks.io/en/latest/hamilton-ui/ui/#install), you can run the Hamilton UI server in a docker container. 
```shell
git clone https://github.com/dagworks-inc/hamilton

cd hamilton/ui

./run.sh
```
This starts the Hamilton UI server on `http://localhost:8242`. 


You need to set your username/email(and optionally an api key) during the first login. Create a new project in the Hamilton UI for each flowerpower pipeline you want to track.

To use the pipeline tracking, you need to configure the tracker in the `conf/tracker.yml` file
```yaml
username: my_email@example.com
api_url: http://localhost:8241
ui_url: http://localhost:8242
api_key: # optional

pipeline:
  my_flow:
    project_id: 1
    tags:
      environment: dev
      version: 1.0
    dag_name: my_flow_123
```

Now you can track the pipeline execution by setting the `with_tracker` parameter in the `conf/pipelines.yml` file to `true` or by using the `--with-tracker` parameter in the command line.




### *Optional: Dev Services*
To test the distributed (seperate workers) pipeline execution in a local environment, you need a data store and an event broker. You can use the following docker-compose file to setup the services.

Download the docker-compose file
```shell
curl -O https://raw.githubusercontent.com/legout/flowerpower/main/docker/docker-compose.yml
```
Start the relevant services
```shell
#  emqx mqtt broker if you want to use mqtt as the event broker
docker-compose up mqtt -d 
# valkey (OSS redis) if you want to use redis as the event broker
docker-compose up redis -d 
# mongodb if you want to use mongodb as the data store
docker-compose up mongodb -d 
 # postgres db if you want to use postgres as data store and/or event broker. 
docker-compose up postgres -d
```

