# FlowerPower

![Bild](./image.png)

FlowerPower is a simple workflow framework based on the fantastic [Hamilton](https://github.com/DAGWorks-Inc/hamilton) and [Advanced Python Scheduler - APScheduler](https://github.com/agronholm/apscheduler)

## Installation

```shell
pip install "flowerpower" 
# with scheduler
pip install "flowerpower[scheduler]" 
# with mqtt event broker
pip install "flowerpower[scheduler,mqtt]" 
# with redis event broker
pip install "flowerpower[scheduler,redis]" 
# with mongodb data store
pip install "flowerpower[scheduler,mongodb]"
# with ray distributed computing
pip install "flowerpower[scheduler,ray]"
# with dask distributed computing
pip install "flowerpower[scheduler,dask]"
```

## Usage

### 0) Optional: Dev Services
```shell
curl -O https://raw.githubusercontent.com/legout/flowerpower/main/docker/Dockerfile
curl -O https://raw.githubusercontent.com/legout/flowerpower/main/docker/docker-compose.yml

# Hamilton UI, which allows you to track and visualize your pipelines
docker-compose up hamilton_ui -d 
# jupyterlab and code-server
docker-compose up jupytercode -d 
# s3 compatible object storage
docker-compose up minio -d 
#  mosquitto mqtt broker if you want to use mqtt as the event broker
docker-compose up mqtt -d 
# valkey (OSS redis) if you want to use redis as the event broker
docker-compose up redis -d 
# mongodb if you want to use mongodb as the data store
docker-compose up mongodb -d 
 # postgres db if you want to use postgres as data store and/or event broker. This db is also used for hamilton ui
docker-compose up postgres -d

```


### a) Initialze a new flowerpower project
```shell
flowerpower init new-project
cd new-project
```
This adds basic config files `conf/pipelines.yml`, `conf/scheduler.yml` and `conf/tracker.yml`

### b) Add a new pipeline
```shell
flowerpoweradd-pipeline my_flow
```
A new file `pipelines/my_flow.py` is created and the relevant entries are added to the config files.

### c) Setup the new pipeline
Edit `pipelines/my_flow.py` and add the pipeline functions.

FlowerPower uses [Hamilton](https://github.com/DAGWorks-Inc/hamilton) that converts your pipeline functions into nodes and then creates a [Directed Acyclic Graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph).

It is therefore mandatory to write your pipeline files according to the Hamilton paradigm. You can read more about this in the Hamilton documentaion chapter [Function, Nodes and DataFlow](https://hamilton.dagworks.io/en/latest/concepts/node/)

Optinally edit the config files `conf/pipelines.yml`, `conf/scheduler.yml` and `conf/tracker.yml`

### d) Run or Scheduler the new pipeline
```shell
flowerpower run-pipeline my_flow
# or schedule with a 30 seconds interval
flowerpower schedule-pipeline my_flow interval --interval-params seconds=30 --auto-start
```





