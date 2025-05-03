This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.
The content has been processed where content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: src, examples, docker
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

## Additional Info

# Directory Structure
```
docker/
  conf/
    etc/
      hosts
    mosquitto.conf
  python-worker/
    .dockerignore
    Dockerfile.dev
    hello.py
    pyproject.toml
  Caddyfile
  docker-compose.yml
examples/
  apscheduler/
    hello-world/
      conf/
        pipelines/
          hello_world.yml
          test_mqtt.yml
        project.yml
      pipelines/
        hello_world.py
        test_mqtt.py
      README.md
  hello-world/
    conf/
      pipelines/
        hello_world.yml
        test_mqtt.yml
      project.yml
    pipelines/
      hello_world.py
      test_mqtt.py
    README.md
  rq/
    hello-world/
      conf/
        pipelines/
          hello_world.yml
          test_mqtt.yml
        project_bak.yml
        project.yml
      pipelines/
        hello_world.py
        test_mqtt.py
      README.md
src/
  flowerpower/
    cfg/
      pipeline/
        __init__.py
        adapter.py
        run.py
        schedule.py
      project/
        __init__.py
        adapter.py
        job_queue.py
      __init__.py
      base.py
    cli/
      __init__.py
      cfg.py
      job_queue.py
      mqtt.py
      pipeline.py
      utils.py
    fs/
      __init__.py
      base.py
      ext.py
      storage_options.py
    job_queue/
      apscheduler/
        _setup/
          datastore.py
          eventbroker.py
        __init__.py
        manager.py
        setup.py
        trigger.py
        utils.py
      rq/
        concurrent_workers/
          gevent_worker.py
          thread_worker.py
        __init__.py
        _trigger.py
        manager.py
        setup.py
        utils.py
      __init__.py
      base.py
    pipeline/
      __init__.py
      base.py
      io.py
      job_queue.py
      manager.py
      registry.py
      runner.py
      visualizer.py
    plugins/
      io/
        loader/
          __init__.py
          _duckdb.py
          csv.py
          deltatable.py
          duckdb.py
          json.py
          mqtt.py
          mssql.py
          mysql.py
          oracle.py
          parquet.py
          postgres.py
          pydala.py
          sqlite.py
        saver/
          __init__.py
          _duckdb.py
          csv.py
          deltatable.py
          duckdb.py
          json.py
          mssql.py
          mysql.py
          oracle.py
          parquet.py
          postgres.py
          pydala.py
          sqlite.py
        base.py
        metadata.py
      mqtt/
        __init__.py
        cfg.py
        manager.py
    utils/
      logging.py
      misc.py
      monkey.py
      open_telemetry.py
      polars.py
      scheduler.py
      sql.py
      templates.py
    web/
      templates/
        base.html
        index.html
        index1.html
        new_pipeline.html
        pipeline_detail.html
        pipelines.html
        schedule_pipeline.html
        schedules.html
    __init__.py
    flowerpower.py
    mqtt.py
    settings.py
```

# Files

## File: docker/conf/mosquitto.conf
````
listener 1883
allow_anonymous true

max_queued_messages 10
max_queued_bytes 0

persistence true
persistence_location /mosquitto/data/

persistent_client_expiration 1h
````

## File: examples/hello-world/pipelines/test_mqtt.py
````python
# FlowerPower pipeline test_mqtt.py
# Created on 2024-11-07 16:29:15
⋮----
# from hamilton.function_modifiers import parameterize
⋮----
PARAMS = Config.load(
⋮----
def df(payload: bytes) -> pd.DataFrame
⋮----
data = json.loads(payload)
⋮----
def print_df(df: pd.DataFrame) -> None
````

## File: examples/hello-world/README.md
````markdown
# HELLO-WORLD

**created with FlowerPower**

*2024-10-26 12:43:48*
````

## File: src/flowerpower/cli/cfg.py
````python
app = typer.Typer(help="Config management commands")
⋮----
# @app.command()
# def get_project(request) -> json:
#     cfg = request.app.ctx.pipeline_manager.cfg.project.to_dict()
#     # cfg.pop("fs")
#     return json({"cfg": cfg})
⋮----
# @bp.get("/pipeline/<pipeline_name>")
# async def get_pipeline(request, pipeline_name) -> json:
#     if pipeline_name != request.app.ctx.pipeline_manager.cfg.pipeline.name:
#         request.app.ctx.pipeline_manager.load_config(pipeline_name)
#     cfg = request.app.ctx.pipeline_manager.cfg.pipeline.to_dict()
⋮----
# @bp.post("/pipeline/<pipeline_name>")
# @openapi.body({"application/json": PipelineConfig}, required=True)
# @validate(json=PipelineConfig)
# async def update_pipeline(request, pipeline_name, body: PipelineConfig) -> json:
#     data = request.json
⋮----
#     cfg = request.app.ctx.pipeline_manager.cfg.pipeline.copy()
#     cfg.update(data)
#     try:
#         cfg.to_yaml(
#             posixpath.join(
#                 "pipelines",
#                 pipeline_name + ".yml",
#             ),
#             fs=request.app.ctx.pipeline_manager.cfg.fs,
#         )
#     except NotImplementedError as e:
#         raise SanicException(f"Update failed. {e}", status_code=404)
#     cfg
````

## File: src/flowerpower/utils/monkey.py
````python
def patch_pickle()
⋮----
"""
    Patch the pickle serializer in the apscheduler module.

    This function replaces the `dumps` and `loads` functions in the `apscheduler.serializers.pickle` module
    with custom implementations.

    This is useful when you want to modify the behavior of the pickle serializer used by the apscheduler module.

    Example usage:
    patch_pickle()

    """
⋮----
def job_to_dict(job)
⋮----
def task_to_dict(task)
⋮----
def schedule_to_dict(schedule)
````

## File: src/flowerpower/utils/open_telemetry.py
````python
# If you wanted to use another OpenTelemetry destination such as the open-source Jaeger,
# setup the container locally and use the following code
⋮----
# Add more open telemetry exporters here
⋮----
jaeger_exporter = JaegerExporter(
⋮----
agent_host_name=host,  # Replace with your Jaeger agent host
agent_port=port,  # Replace with your Jaeger agent port
⋮----
span_processor = SimpleSpanProcessor(jaeger_exporter)
provider = TracerProvider(
````

## File: src/flowerpower/utils/polars.py
````python
def get_timestamp_column(df: pl.DataFrame | pl.LazyFrame) -> str | list[str]
⋮----
def get_timedelta_str(timedelta_string: str, to: str = "polars") -> str
⋮----
polars_timedelta_units = [
duckdb_timedelta_units = [
⋮----
unit = re.sub("[0-9]", "", timedelta_string).strip()
val = timedelta_string.replace(unit, "").strip()
⋮----
all_columns = df.columns if isinstance(df, pl.DataFrame) else df.collect_schema()
⋮----
def _unnest_with_prefix(columns)
⋮----
columns = [col for col in all_columns if df[col].dtype == pl.Struct]
⋮----
columns = [columns]
⋮----
df = _unnest_with_prefix(columns=columns)
⋮----
s = s.set(s == "-", None).set(s == "", None).set(s == "None", None)
⋮----
# cast string numbers to int or float
⋮----
s = (
⋮----
# .str.replace_all("^0{1,}$", "+0")
# .str.strip_chars_start("0")
⋮----
s = s.cast(pl.Float32(), strict=True)
⋮----
s = s.cast(pl.Int64(), strict=True)
⋮----
s = s.shrink_dtype()
⋮----
# cast str to datetime
⋮----
s = pl.Series(
⋮----
# cast str to bool
⋮----
s = s.str.to_lowercase().str.contains(
⋮----
_opt_dtype_strict = partial(_opt_dtype, strict=strict)
_opt_dtype_not_strict = partial(_opt_dtype, strict=False)
all_columns = (
⋮----
include = [include]
exclude = [col for col in all_columns if col not in include]
⋮----
def explode_all(df: pl.DataFrame | pl.LazyFrame) -> pl.DataFrame | pl.LazyFrame
⋮----
list_columns = [col for col in all_columns if df[col].dtype == pl.List]
⋮----
df = df.explode(col)
⋮----
timestamp_column = get_timestamp_column(df)
⋮----
timestamp_column = timestamp_column[0]
⋮----
strftime = [strftime]
⋮----
column_names = [column_names]
⋮----
column_names = [
# print("timestamp_column, with_strftime_columns", timestamp_column)
⋮----
truncate_by = [truncate_by]
⋮----
truncate_by = [
⋮----
strftime = []
column_names = []
⋮----
column_names = [col for col in column_names if col not in all_columns]
# print("timestamp_column, with_datepart_columns", timestamp_column)
⋮----
over = None
⋮----
over = [over]
⋮----
def unify_schema(dfs: list[pl.DataFrame | pl.LazyFrame]) -> pl.Schema
⋮----
df = pl.concat(dfs, how="diagonal_relaxed")
⋮----
columns = df.collect_schema().names()
⋮----
columns = df.schema.names()
new_columns = [col for col in schema.names() if col not in columns]
⋮----
s1 = df1.select(~cs.by_dtype(pl.Null())).collect_schema()
s2 = df2.select(~cs.by_dtype(pl.Null())).collect_schema()
⋮----
columns = sorted(set(s1.names()) & set(s2.names()))
⋮----
subset = df1.columns
⋮----
subset = [subset]
⋮----
subset = sorted(set(columns) & set(subset))
⋮----
df2 = df2.lazy()
⋮----
df1 = df1.lazy()
⋮----
# cast to equal schema
unified_schema = unify_schema([df1.select(subset), df2.select(subset)])
⋮----
df1 = df1.cast_relaxed(unified_schema)
df2 = df2.cast_relaxed(unified_schema)
⋮----
df = df1.join(df2, on=subset, how="anti", join_nulls=True)
⋮----
columns_ = columns.copy()
⋮----
columns_ = []
⋮----
drop_columns = columns_.copy()
⋮----
df = df.with_striftime_columns(
strftime_columns = [
⋮----
timedelta = [timedelta]
⋮----
df = df.with_duration_columns(
timedelta_columns = [f"_timedelta_{timedelta_}_" for timedelta_ in timedelta]
⋮----
datetime_columns = [
⋮----
datetime_columns = {
⋮----
df = df.with_datepart_columns(
⋮----
# if isinstance(df, pl.LazyFrame):
#    df = df.collect()
columns_ = [col for col in columns_ if col in all_columns]
⋮----
df = df.with_row_count_ext(over=columns_).with_columns(
⋮----
partitions = [
⋮----
def drop_null_columns(df: pl.DataFrame | pl.LazyFrame) -> pl.DataFrame | pl.LazyFrame
⋮----
# pl.DataFrame.unnest_all = unnest_all
⋮----
# pl.LazyFrame.unnest_all = unnest_all
````

## File: src/flowerpower/utils/scheduler.py
````python
def humanize_crontab(minute, hour, day, month, day_of_week)
⋮----
days = {
months = {
⋮----
def get_day_name(day_input)
⋮----
day_input = str(day_input).lower().strip()
⋮----
parts = []
⋮----
def format_trigger(trigger)
⋮----
trigger_type = trigger.__class__.__name__
⋮----
cron_parts = dict(
cron_parts = {k: v.strip("'") for k, v in cron_parts.items()}
crontab = f"{cron_parts['minute']} {cron_parts['hour']} {cron_parts['day']} {cron_parts['month']} {cron_parts['day_of_week']}"
human_readable = humanize_crontab(
⋮----
def display_schedules(schedules: List)
⋮----
console = Console()
total_width = console.width - 10
⋮----
width_ratios = {
⋮----
widths = {k: max(10, int(total_width * ratio)) for k, ratio in width_ratios.items()}
⋮----
table = Table(
⋮----
def display_tasks(tasks)
⋮----
table = Table(title="Tasks")
⋮----
widths = {"id": 50, "executor": 15, "max_jobs": 15, "misfire": 20}
⋮----
def display_jobs(jobs)
⋮----
table = Table(title="Jobs")
⋮----
widths = {
⋮----
status = "Running" if job.acquired_by else "Pending"
````

## File: docker/conf/etc/hosts
````
127.0.0.1 codeserver.flowerpower.local
127.0.0.1 minio.flowerpower.local
127.0.0.1 frontend.flowerpower.local
127.0.0.1 dockge.flowerpower.local
````

## File: docker/python-worker/.dockerignore
````
.venv
````

## File: docker/python-worker/Dockerfile.dev
````
# An example using multi-stage image builds to create a final image without uv.

# First, build the application in the `/app` directory.
# See `Dockerfile` for details.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Then, use a final image without uv
FROM python:3.12-slim-bookworm
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the FastAPI application by default
CMD ["tail", "-f", "/dev/null"]
````

## File: docker/python-worker/hello.py
````python
def main()
````

## File: docker/python-worker/pyproject.toml
````toml
[project]
name = "python-worker"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12.8"
dependencies = [
    "flowerpower[io,mqtt,redis,scheduler]>=0.9.12.4",
    "rq>=2.3.2",
    "rq-scheduler>=0.14.0",
]


[tool.uv]
prerelease = "allow"
````

## File: examples/apscheduler/hello-world/pipelines/hello_world.py
````python
# FlowerPower pipeline hello_world.py
# Created on 2024-10-26 12:44:27
⋮----
PARAMS = Config.load(
⋮----
@config.when(range=10_000)
def spend__10000() -> pd.Series
⋮----
"""Returns a series of spend data."""
# time.sleep(2)
⋮----
@config.when(range=10_000)
def signups__10000() -> pd.Series
⋮----
"""Returns a series of signups data."""
⋮----
@config.when(range=1_000)
def spend__1000() -> pd.Series
⋮----
@config.when(range=1_000)
def signups__1000() -> pd.Series
⋮----
)  # (**{"avg_x_wk_spend": {"rolling": value(3)}})  #
def avg_x_wk_spend(spend: pd.Series, rolling: int) -> pd.Series
⋮----
"""Rolling x week average spend."""
⋮----
def spend_per_signup(spend: pd.Series, signups: pd.Series) -> pd.Series
⋮----
"""The cost per signup in relation to spend."""
⋮----
def spend_mean(spend: pd.Series) -> float
⋮----
"""Shows function creating a scalar. In this case it computes the mean of the entire column."""
⋮----
)  # (**{"spend_zero_mean": {"offset": value(0)}})  #
def spend_zero_mean(spend: pd.Series, spend_mean: float, offset: int) -> pd.Series
⋮----
"""Shows function that takes a scalar. In this case to zero mean spend."""
⋮----
def spend_std_dev(spend: pd.Series) -> float
⋮----
"""Function that computes the standard deviation of the spend column."""
⋮----
"""Function showing one way to make spend have zero mean and unit variance."""
````

## File: examples/apscheduler/hello-world/pipelines/test_mqtt.py
````python
# FlowerPower pipeline test_mqtt.py
# Created on 2024-11-07 16:29:15
⋮----
# from hamilton.function_modifiers import parameterize
⋮----
PARAMS = Config.load(
⋮----
def df(payload: bytes) -> pd.DataFrame
⋮----
data = json.loads(payload)
⋮----
def print_df(df: pd.DataFrame) -> None
````

## File: examples/apscheduler/hello-world/README.md
````markdown
# HELLO-WORLD

**created with FlowerPower**

*2024-10-26 12:43:48*
````

## File: examples/rq/hello-world/conf/project_bak.yml
````yaml
name: ewnnesigateway_gdi
job_queue:
  type: rq
  backend:
    type: redis
    uri: null
    username: null
    password: ffGg6X0nUrux
    host: lodl.nes.siemens.de
    port: 6379
    database: 0
    ssl: true
    cert_file: null
    key_file: null
    ca_file: null
    verify_ssl: false
    queues:
    - default
    - high
    - low
    - scheduler
    num_workers: 10
adapter:
  hamilton_tracker:
    username: null
    api_url: http://localhost:8241
    ui_url: http://localhost:8242
    api_key: null
    verify: false
  mlflow:
    tracking_uri: null
    registry_uri: null
    artifact_location: null
  ray:
    ray_init_config: null
    shutdown_ray_on_completion: false
  opentelemetry:
    host: localhost
    port: 6831
````

## File: examples/rq/hello-world/pipelines/hello_world.py
````python
# FlowerPower pipeline hello_world.py
# Created on 2024-10-26 12:44:27
⋮----
PARAMS = Config.load(
⋮----
@config.when(range=10_000)
def spend__10000() -> pd.Series
⋮----
"""Returns a series of spend data."""
# time.sleep(2)
⋮----
@config.when(range=10_000)
def signups__10000() -> pd.Series
⋮----
"""Returns a series of signups data."""
⋮----
@config.when(range=1_000)
def spend__1000() -> pd.Series
⋮----
@config.when(range=1_000)
def signups__1000() -> pd.Series
⋮----
)  # (**{"avg_x_wk_spend": {"rolling": value(3)}})  #
def avg_x_wk_spend(spend: pd.Series, rolling: int) -> pd.Series
⋮----
"""Rolling x week average spend."""
⋮----
def spend_per_signup(spend: pd.Series, signups: pd.Series) -> pd.Series
⋮----
"""The cost per signup in relation to spend."""
⋮----
def spend_mean(spend: pd.Series) -> float
⋮----
"""Shows function creating a scalar. In this case it computes the mean of the entire column."""
⋮----
)  # (**{"spend_zero_mean": {"offset": value(0)}})  #
def spend_zero_mean(spend: pd.Series, spend_mean: float, offset: int) -> pd.Series
⋮----
"""Shows function that takes a scalar. In this case to zero mean spend."""
⋮----
def spend_std_dev(spend: pd.Series) -> float
⋮----
"""Function that computes the standard deviation of the spend column."""
⋮----
"""Function showing one way to make spend have zero mean and unit variance."""
````

## File: examples/rq/hello-world/pipelines/test_mqtt.py
````python
# FlowerPower pipeline test_mqtt.py
# Created on 2024-11-07 16:29:15
⋮----
# from hamilton.function_modifiers import parameterize
⋮----
PARAMS = Config.load(
⋮----
def df(payload: bytes) -> pd.DataFrame
⋮----
data = json.loads(payload)
⋮----
def print_df(df: pd.DataFrame) -> None
````

## File: examples/rq/hello-world/README.md
````markdown
# HELLO-WORLD

**created with FlowerPower**

*2024-10-26 12:43:48*
````

## File: src/flowerpower/job_queue/apscheduler/_setup/datastore.py
````python
class APSDataStoreType(BackendType)
⋮----
POSTGRESQL = "postgresql"
SQLITE = "sqlite"
MYSQL = "mysql"
MONGODB = "mongodb"
MEMORY = "memory"
⋮----
class APSDataStore(BaseBackend)
⋮----
"""Data store for APScheduler."""
⋮----
def __post_init__(self)
⋮----
@classmethod
    def from_dict(cls, d: dict[str, any]) -> "APSDataStore"
⋮----
def _validate_inputs(self) -> None
⋮----
async def _setup_db(self) -> None
⋮----
sqla_engine = create_async_engine(self.uri)
⋮----
async def _create_schema(self, engine: AsyncEngine) -> None
⋮----
async def _create_database_and_schema(self, engine: AsyncEngine) -> None
⋮----
database_name = self.uri.split("/")[-1].split("?")[0]
temp_uri = self.uri.replace(f"/{database_name}", "/template1")
temp_engine = create_async_engine(temp_uri)
⋮----
def setup_db(self) -> None
⋮----
def _setup_sqlalchemy(self) -> None
⋮----
def _setup_mongodb(self) -> None
⋮----
def _setup_memory(self) -> None
⋮----
def setup(self) -> None
⋮----
@property
    def client(self) -> BaseDataStore
⋮----
@property
    def sqla_engine(self) -> AsyncEngine | None
````

## File: src/flowerpower/job_queue/apscheduler/_setup/eventbroker.py
````python
class APSEventBrokerType(BackendType)
⋮----
POSTGRESQL = "postgresql"
MEMORY = "memory"
REDIS = "redis"
MQTT = "mqtt"
⋮----
class APSEventBroker(BaseBackend)
⋮----
"""Data store for APScheduler."""
⋮----
def __post_init__(self)
⋮----
@classmethod
    def from_dict(cls, d: dict[str, any]) -> "APSEventBroker"
⋮----
def _validate_inputs(self) -> None
⋮----
def _setup_asyncpg_event_broker(self)
⋮----
def _setup_mqtt_event_broker(self)
⋮----
# Parse the URI
parsed = urllib.parse.urlparse(self.uri)
⋮----
hostname = parsed.hostname
port = parsed.port
username = parsed.username
password = parsed.password
use_ssl = parsed.scheme == "mqtts"
⋮----
def _setup_redis_event_broker(self)
⋮----
def _setup_local_event_broker(self)
⋮----
def setup(self)
⋮----
@property
    def client(self) -> BaseEventBroker
⋮----
@property
    def sqla_engine(self) -> AsyncEngine | None
````

## File: src/flowerpower/job_queue/apscheduler/setup.py
````python
# Standard library imports
⋮----
# Third-party imports
⋮----
# Local imports
⋮----
@dataclass  # (slots=True)
@dataclass  # (slots=True)
class APSDataStore(BaseBackend)
⋮----
"""APScheduler data store implementation that supports multiple backend types.

    This class provides a flexible data store interface for APScheduler, supporting various
    backend storage options including SQLAlchemy-compatible databases, MongoDB, and in-memory
    storage.

    Args:
        schema (str | None): Database schema name. Defaults to "flowerpower".
            Note: Ignored for SQLite databases.

    Attributes:
        type (BackendType): Type of backend storage (inherited from BaseBackend)
        uri (str): Connection URI for the backend (inherited from BaseBackend)
        _client (BaseDataStore): The APScheduler data store instance
        _sqla_engine (AsyncEngine): SQLAlchemy async engine for SQL databases

    Raises:
        ValueError: If an invalid backend type is specified

    Example:
        ```python
        # Create PostgreSQL data store
        data_store = APSDataStore(
            type="postgresql",
            uri="postgresql+asyncpg://user:pass@localhost/db",
            schema="scheduler"
        )
        data_store.setup()

        # Create in-memory data store
        memory_store = APSDataStore(type="memory")
        memory_store.setup()

        # Create MongoDB data store
        mongo_store = APSDataStore(
            type="mongodb",
            uri="mongodb://localhost:27017",
            schema="scheduler"
        )
        mongo_store.setup()
        ```
    """
⋮----
schema: str | None = "flowerpower"
⋮----
def __post_init__(self)
⋮----
"""Initialize and validate the data store configuration.

        This method is called automatically after instance creation. It:
        1. Sets default type to "memory" if not specified
        2. Calls parent class initialization
        3. Validates backend type
        4. Warns about schema limitations with SQLite

        Raises:
            ValueError: If an invalid backend type is specified
        """
⋮----
async def _setup_db(self) -> None
⋮----
"""Initialize database and schema for SQL backends.

        Creates the database and schema if they don't exist. This is an internal async
        method called by setup_db().

        Raises:
            Exception: If database/schema creation fails
        """
sqla_engine = create_async_engine(self.uri)
⋮----
async def _create_schema(self, engine: AsyncEngine) -> None
⋮----
"""Create schema in existing database if it doesn't exist.

        Args:
            engine: SQLAlchemy async engine connected to the database
        """
⋮----
async def _create_database_and_schema(self, engine: AsyncEngine) -> None
⋮----
"""Create both database and schema if they don't exist.

        Creates a temporary connection to template1 to create the database,
        then creates the schema within the new database.

        Args:
            engine: SQLAlchemy async engine
        """
database_name = self.uri.split("/")[-1].split("?")[0]
temp_uri = self.uri.replace(f"/{database_name}", "/template1")
temp_engine = create_async_engine(temp_uri)
⋮----
def setup_db(self) -> None
⋮----
"""Initialize the database synchronously.

        This is a blocking wrapper around the async _setup_db() method.
        Uses anyio portal to run async code from synchronous context.
        """
⋮----
def _setup_sqlalchemy(self) -> None
⋮----
"""Initialize SQLAlchemy data store.

        Sets up SQLAlchemy engine and data store for PostgreSQL, MySQL, or SQLite.
        Creates database and schema if needed.
        """
⋮----
def _setup_mongodb(self) -> None
⋮----
"""Initialize MongoDB data store.

        Creates MongoDBDataStore instance using provided URI and schema (database name).
        """
⋮----
def _setup_memory(self) -> None
⋮----
"""Initialize in-memory data store.

        Creates MemoryDataStore instance for temporary storage.
        """
⋮----
def setup(self) -> None
⋮----
"""Initialize the appropriate data store based on backend type.

        This is the main setup method that should be called after creating the data store.
        It delegates to the appropriate setup method based on the backend type.
        """
⋮----
@property
    def client(self) -> BaseDataStore
⋮----
"""Get the initialized data store client.

        Returns:
            BaseDataStore: The APScheduler data store instance, initializing it if needed.
        """
⋮----
@property
    def sqla_engine(self) -> AsyncEngine | None
⋮----
"""Get the SQLAlchemy engine.

        Returns:
            AsyncEngine | None: The async SQLAlchemy engine for SQL backends,
                None for non-SQL backends
        """
⋮----
@dataclass  # (slots=True)
class APSEventBroker(BaseBackend)
⋮----
"""APScheduler event broker implementation supporting multiple messaging backends.

    This class provides a flexible event broker interface for APScheduler that can use
    various messaging systems including PostgreSQL NOTIFY/LISTEN, MQTT, Redis pub/sub,
    and in-memory event handling.

    Attributes:
        type (BackendType): Type of backend messaging system (inherited from BaseBackend)
        uri (str): Connection URI for the backend (inherited from BaseBackend)
        _client (BaseEventBroker): The APScheduler event broker instance
        _sqla_engine (AsyncEngine): SQLAlchemy async engine for PostgreSQL NOTIFY/LISTEN

    Raises:
        ValueError: If an invalid backend type is specified or if SQLAlchemy engine is not PostgreSQL
            when using from_ds_sqla

    Example:
        ```python
        # Create Redis event broker
        redis_broker = APSEventBroker(
            type="redis",
            uri="redis://localhost:6379/0"
        )
        redis_broker.setup()

        # Create MQTT event broker
        mqtt_broker = APSEventBroker(
            type="mqtt",
            uri="mqtt://user:pass@localhost:1883"
        )
        mqtt_broker.setup()

        # Create PostgreSQL event broker from existing SQLAlchemy engine
        pg_broker = APSEventBroker.from_ds_sqla(pg_engine)

        # Create in-memory event broker
        memory_broker = APSEventBroker(type="memory")
        memory_broker.setup()
        ```
    """
⋮----
"""Initialize and validate the event broker configuration.

        This method is called automatically after instance creation. It:
        1. Sets default type to "memory" if not specified
        2. Calls parent class initialization
        3. Validates backend type compatibility

        Raises:
            ValueError: If an invalid backend type is specified or an unsupported
                combination of settings is provided (e.g., Redis without URI)
        """
⋮----
def _setup_asyncpg_event_broker(self)
⋮----
"""Initialize PostgreSQL event broker.

        Sets up AsyncpgEventBroker using either a DSN string or existing SQLAlchemy engine.
        Uses PostgreSQL's NOTIFY/LISTEN for event messaging.
        """
⋮----
def _setup_mqtt_event_broker(self)
⋮----
"""Initialize MQTT event broker.

        Parses MQTT connection URI for host, port, credentials and SSL settings.
        Sets up MQTTEventBroker for pub/sub messaging.
        """
⋮----
# Parse the URI
parsed = urllib.parse.urlparse(self.uri)
⋮----
hostname = parsed.hostname
port = parsed.port
username = parsed.username
password = parsed.password
use_ssl = parsed.scheme == "mqtts"
⋮----
def _setup_redis_event_broker(self)
⋮----
"""Initialize Redis event broker.

        Creates RedisEventBroker instance using provided Redis URI.
        Uses Redis pub/sub for event messaging.
        """
⋮----
def _setup_local_event_broker(self)
⋮----
"""Initialize in-memory event broker.

        Creates LocalEventBroker for in-process event handling.
        """
⋮----
def setup(self)
⋮----
"""Initialize the appropriate event broker based on backend type.

        This is the main setup method that should be called after creating the event broker.
        It delegates to the appropriate setup method based on the backend type.
        """
⋮----
@property
    def client(self) -> BaseEventBroker
⋮----
"""Get the initialized event broker client.

        Returns:
            BaseEventBroker: The APScheduler event broker instance, initializing it if needed.
        """
⋮----
"""Get the SQLAlchemy engine.

        Returns:
            AsyncEngine | None: The async SQLAlchemy engine for PostgreSQL backend,
                None for other backends
        """
⋮----
@classmethod
    def from_ds_sqla(cls, sqla_engine: AsyncEngine) -> "APSEventBroker"
⋮----
"""Create event broker from existing SQLAlchemy engine.

        This factory method creates a PostgreSQL event broker that shares the
        same database connection as a data store.

        Args:
            sqla_engine: Async SQLAlchemy engine, must be PostgreSQL with asyncpg driver

        Returns:
            APSEventBroker: New event broker instance using the provided engine

        Raises:
            ValueError: If engine is not PostgreSQL with asyncpg driver

        Example:
            ```python
            # Create data store with PostgreSQL
            data_store = APSDataStore(
                type="postgresql",
                uri="postgresql+asyncpg://user:pass@localhost/db"
            )
            data_store.setup()

            # Create event broker using same connection
            event_broker = APSEventBroker.from_ds_sqla(data_store.sqla_engine)
            ```
        """
⋮----
@dataclass(slots=True)
class APSBackend
⋮----
"""Main backend configuration class for APScheduler combining data store and event broker.

    This class serves as a container for configuring both the data store and event broker
    components of APScheduler. It handles initialization and setup of both components,
    with support for dictionary-based configuration.

    Args:
        data_store (APSDataStore | dict | None): Data store configuration, either as an
            APSDataStore instance or a configuration dictionary. Defaults to a new
            APSDataStore instance.
        event_broker (APSEventBroker | dict | None): Event broker configuration, either as
            an APSEventBroker instance or a configuration dictionary. Defaults to a new
            APSEventBroker instance.

    Example:
        ```python
        # Create backend with default memory storage
        backend = APSBackend()

        # Create backend with PostgreSQL data store and Redis event broker
        backend = APSBackend(
            data_store={
                "type": "postgresql",
                "uri": "postgresql+asyncpg://user:pass@localhost/db",
                "schema": "scheduler"
            },
            event_broker={
                "type": "redis",
                "uri": "redis://localhost:6379/0"
            }
        )

        # Create backend with PostgreSQL for both data store and event broker
        backend = APSBackend(
            data_store={
                "type": "postgresql",
                "uri": "postgresql+asyncpg://user:pass@localhost/db",
            },
            event_broker={
                "from_ds_sqla": True  # Use same PostgreSQL connection for events
            }
        )
        ```
    """
⋮----
data_store: APSDataStore | dict | None = field(default_factory=APSDataStore)
event_broker: APSEventBroker | dict | None = field(default_factory=APSEventBroker)
⋮----
"""Initialize and setup data store and event broker components.

        Called automatically after instance creation. This method:
        1. Converts data store dict to APSDataStore instance if needed
        2. Initializes data store
        3. Converts event broker dict to APSEventBroker instance if needed
        4. Sets up event broker using data store connection if specified
        5. Initializes event broker
        """
````

## File: src/flowerpower/job_queue/apscheduler/trigger.py
````python
class TriggerType(Enum)
⋮----
CRON = "cron"
INTERVAL = "interval"
CALENDARINTERVAL = "calendarinterval"
DATE = "date"
⋮----
# Mapping of trigger type to its class and allowed kwargs
TRIGGER_CONFIG: Dict[TriggerType, Dict[str, Any]] = {
⋮----
class APSTrigger(BaseTrigger)
⋮----
"""
    Implementation of BaseTrigger for APScheduler.

    Provides a factory for creating APScheduler trigger instances
    with validation and filtering of keyword arguments.
    """
⋮----
trigger_type: TriggerType
⋮----
def __init__(self, trigger_type: str)
⋮----
"""
        Initialize APSchedulerTrigger with a trigger type.

        Args:
            trigger_type (str): The type of trigger (cron, interval, calendarinterval, date).

        Raises:
            ValueError: If the trigger_type is invalid.
        """
⋮----
valid_types = [t.value for t in TriggerType]
⋮----
def _get_allowed_kwargs(self) -> set
⋮----
"""Return the set of allowed kwargs for the current trigger type."""
⋮----
def _check_kwargs(self, **kwargs) -> None
⋮----
"""
        Validate that all provided kwargs are allowed for the trigger type.

        Raises:
            ValueError: If any kwarg is not allowed.
        """
allowed = self._get_allowed_kwargs()
invalid = [k for k in kwargs if k not in allowed]
⋮----
def _filter_kwargs(self, **kwargs) -> Dict[str, Any]
⋮----
"""
        Filter kwargs to only those allowed for the trigger type and not None.

        Returns:
            Dict[str, Any]: Filtered kwargs.
        """
⋮----
def get_trigger_instance(self, **kwargs) -> Any
⋮----
"""
        Create and return an APScheduler trigger instance based on the trigger type.

        Args:
            **kwargs: Keyword arguments for the trigger.

        Returns:
            Any: An APScheduler trigger instance.

        Raises:
            ValueError: If invalid arguments are provided or trigger type is unknown.
        """
⋮----
filtered_kwargs = self._filter_kwargs(**kwargs)
trigger_cls: Type = TRIGGER_CONFIG[self.trigger_type]["class"]
⋮----
crontab = filtered_kwargs.pop("crontab", None)
⋮----
# Default to now if not specified
⋮----
# This should never be reached due to Enum validation in __init__
⋮----
# End of file
````

## File: src/flowerpower/job_queue/rq/concurrent_workers/gevent_worker.py
````python
# Monkey patch as early as possible
⋮----
GEVENT_AVAILABLE = True
⋮----
GEVENT_AVAILABLE = False
⋮----
# Use utcnow directly for simplicity
utcnow = dt.datetime.utcnow
⋮----
class GeventWorker(worker.Worker)
⋮----
"""
    A variation of the RQ Worker that uses Gevent to perform jobs concurrently
    within a single worker process using greenlets.

    Ideal for I/O bound tasks, offering very lightweight concurrency.
    Jobs share the same memory space within the worker process.

    Requires gevent to be installed and monkey-patching to be applied
    (done automatically when this module is imported).
    """
⋮----
"""Starts the worker's main loop using gevent for concurrent job execution."""
⋮----
did_perform_work = False
⋮----
processed_jobs = 0
⋮----
# Wait for space in the greenlet pool if it's full
⋮----
gevent.sleep(0.1)  # Yield to other greenlets
⋮----
result = self.dequeue_job_and_maintain_ttl(timeout=1)
⋮----
did_perform_work = True
⋮----
# Spawn job execution in the gevent pool
greenlet = self._pool.spawn(self.execute_job, job, queue)
# Optional: Add error callback
⋮----
self._pool.join(timeout=30)  # Wait up to 30 seconds for jobs to finish
self._pool.kill()  # Kill any remaining greenlets
⋮----
def set_job_status(self, job, status)
⋮----
"""Sets the job status."""
⋮----
def handle_job_success(self, job, queue, started_job_registry)
⋮----
"""Handles job completion."""
⋮----
def handle_job_failure(self, job, queue, started_job_registry, exc_info=None)
⋮----
"""Handles job failure."""
⋮----
def execute_job(self, job, queue)
⋮----
"""Execute a job in a greenlet."""
job_id = job.id if job else "unknown"
⋮----
started_job_registry = queue.started_job_registry
⋮----
rv = job.perform()
````

## File: src/flowerpower/job_queue/rq/concurrent_workers/thread_worker.py
````python
# filepath: /Volumes/WD_Blue_1TB/coding/libs/flowerpower/src/flowerpower/worker/rq/concurrent_workers.py
⋮----
utcnow = dt.datetime.utcnow
⋮----
class ThreadWorker(worker.Worker)
⋮----
"""
    A variation of the RQ Worker that uses a ThreadPoolExecutor to perform
    jobs concurrently within a single worker process.

    Ideal for I/O bound tasks where the GIL is released during waits.
    Jobs share the same memory space within the worker process.
    """
⋮----
"""Starts the worker's main loop."""
⋮----
did_perform_work = False
⋮----
processed_jobs = 0
⋮----
# Wait for space in the thread pool if it's full
⋮----
result = self.dequeue_job_and_maintain_ttl(timeout=1)
⋮----
did_perform_work = True
⋮----
future = self._executor.submit(self.execute_job, job, queue)
⋮----
def _handle_job_completion(self, future, job_id)
⋮----
"""Handle completion of a job future, including logging any errors."""
⋮----
def set_job_status(self, job, status)
⋮----
"""Sets the job status."""
⋮----
def handle_job_success(self, job, queue, started_job_registry)
⋮----
"""Handles job completion."""
⋮----
# def handle_job_failure(self, job, queue, started_job_registry, exec_string=None):
#    """Handles job failure."""
#    try:
#        if started_job_registry:
#            try:
#                started_job_registry.remove(job)
#            except NotImplementedError:
#                pass
#        job.ended_at = utcnow()
#        job.set_status(JobStatus.FAILED)
#    except Exception as e:
#        self.log.error(f"Error handling job failure for {job.id}: {e}")
⋮----
def execute_job(self, job, queue)
⋮----
"""Execute a job in a worker thread."""
job_id = job.id if job else "unknown"
⋮----
started_job_registry = queue.started_job_registry
⋮----
rv = job.perform()
````

## File: src/flowerpower/job_queue/rq/_trigger.py
````python
class RQTrigger(BaseTrigger)
⋮----
"""
    RQTrigger adapts trigger logic for the RQ worker backend.

    Inherits from BaseTrigger and provides a trigger instance
    in dictionary format suitable for RQ scheduling.
    """
⋮----
def __init__(self, trigger_type: str)
⋮----
def get_trigger_instance(self, **kwargs) -> Dict[str, Any]
⋮----
"""
        Get trigger parameters for RQ Scheduler.

        Args:
            **kwargs: Keyword arguments for the trigger

        Returns:
            Dict[str, Any]: A dictionary with trigger configuration
        """
# RQ doesn't have specific trigger classes like APScheduler.
# Instead, we'll return a dictionary with parameters that can
# be used by RQSchedulerBackend to schedule jobs appropriately.
⋮----
result = {"type": self.trigger_type, **kwargs}
⋮----
# For cron triggers, handle crontab string specifically
````

## File: src/flowerpower/job_queue/rq/utils.py
````python
def show_schedules(scheduler: Scheduler) -> None
⋮----
"""
    Display the schedules in a user-friendly format.

    Args:
        scheduler (Scheduler): An instance of rq_scheduler.Scheduler.
    """
console = Console()
table = Table(title="Scheduled Jobs")
⋮----
# Determine schedule type and format
schedule_type = "Unknown"
⋮----
schedule_type = f"Cron: {job.meta['cron']}"
⋮----
schedule_type = f"Interval: {job.meta['interval']}s"
⋮----
next_run = (
⋮----
def show_jobs(queue: Queue) -> None
⋮----
"""
    Display the jobs in a user-friendly format.

    Args:
        queue (Queue): An instance of rq.Queue.
    """
⋮----
table = Table(title="Jobs")
````

## File: src/flowerpower/plugins/io/loader/__init__.py
````python
__all__ = [
````

## File: src/flowerpower/plugins/io/loader/_duckdb.py
````python
# import datetime as dt
⋮----
# from hamilton.function_modifiers import dataloader
⋮----
class DuckDBLoader(BaseModel)
⋮----
path: str | None = None
read_only: bool = False
conn: duckdb.DuckDBPyConnection | None = None
host: str | None = None
port: int | None = None
socket: str | None = None
user: str | None = None
password: str | None = None
database: str | None = None
⋮----
def _is_sqlite_file(self, path: str) -> bool
⋮----
"""Check if file is SQLite by reading first 16 bytes for SQLite header."""
⋮----
header = f.read(16)
⋮----
def model_post_init(self, __context)
⋮----
# For SQLite files, create in-memory DuckDB and attach SQLite
⋮----
# For DuckDB files, connect directly
⋮----
# For new files, create new DuckDB database
⋮----
def _update_from_env(self)
⋮----
connection_string = ""
⋮----
def to_duckdb_relation(self, query: str) -> duckdb.DuckDBPyRelation
⋮----
def to_pandas(self, query: str) -> pd.DataFrame
⋮----
def to_polars(self, query: str) -> pl.DataFrame
⋮----
def to_pyarrow_table(self, query: str) -> pa.Table
⋮----
def to_table(self, query: str) -> pa.Table
⋮----
def to_pyarrow_dataset(self, query: str) -> pds.Dataset
⋮----
def to_dataset(self, query: str) -> pds.Dataset
⋮----
# @dataloader()
# def load_from_duckdb(
#     query: str,
#     path: str | None = None,
#     conn: duckdb.DuckDBPyConnection | None = None,
#     **kwargs,
# ) -> tuple[duckdb.DuckDBPyRelation, dict]:
#     """
#     Load data from a DuckDB database.
⋮----
#     Args:
#         query: (str) SQL query.
#         path: (str) Path to the database file. If None, an in-memory database is created.
#         conn: (DuckDBPyConnection) DuckDB connection.
#         **kwargs: Additional keyword arguments to pass to `duckdb.connect`.
⋮----
#     Returns:
#         table: (DuckDBPyRelation) DuckDB relation.
#         metadata: (dict) Metadata dictionary.
⋮----
#     if conn is None:
#         conn = duckdb.connect(path, **kwargs)
⋮----
#     table = conn.sql(query)
#     metadata = {
#         "path": path,
#         "format": "duckdb",
#         "timestamp": dt.datetime.now().timestamp(),
#         "query": query,
#     }
#     return table, metadata
⋮----
# def load_from_sqlite(
⋮----
#     Load data from a SQLite database.
⋮----
#         "format": "sqlite",
⋮----
# def load_from_postgres(
⋮----
#     host: str | None = None,
#     port: int | None = None,
#     user: str | None = None,
#     password: str | None = None,
#     database: str | None = None,
⋮----
#     Load data from a PostgreSQL database.
⋮----
#         host: (str) PostgreSQL host.
#         port: (int) PostgreSQL port.
#         user: (str) PostgreSQL user.
#         password: (str) PostgreSQL password.
#         database: (str) PostgreSQL database.
⋮----
#         if path is None:
#             path = ":memory:"
⋮----
#     conn.execute("INSTALL postgres; LOAD postgres;")
#     connection_string = " ".join(
#         f"{k}={v}"
#         for k, v in {
#             "host": host,
#             "port": port,
#             "user": user,
#             "password": password,
#             "database": database,
#         }.items()
#         if v is not None
#     )
#     conn.execute(
#         f"ATTACH {connection_string} AS postgres_db (TYPE POSTGRES, READ_ONLY);"
⋮----
#         "format": "postgres",
⋮----
# def load_from_mysql(
⋮----
#     Load data from a MySQL database.
⋮----
#         host: (str) MySQL host.
#         port: (int) MySQL port.
#         user: (str) MySQL user.
#         password: (str) MySQL password.
#         database: (str) MySQL database.
⋮----
#     conn.execute("INSTALL mysql; LOAD mysql;")
⋮----
#     conn.execute(f"ATTACH {connection_string} AS mysql_db (TYPE MYSQL, READ_ONLY);")
⋮----
#         "format": "mysql",
````

## File: src/flowerpower/plugins/io/loader/csv.py
````python
class CSVFileReader(BaseFileReader)
⋮----
"""CSV file loader.

    This class is responsible for loading CSV files into several dataframe formats,
    duckdb and datafusion.

    Examples:
        ```python
        loader = CSVFileReader("data.csv")
        df = loader.to_pandas()
    ```
    """
⋮----
format: str = "csv"
⋮----
def model_post_init(self, __context)
⋮----
class CSVDatasetReader(BaseDatasetReader)
⋮----
"""CSV dataset loader.

    This class is responsible for loading CSV files into several dataframe formats,
    duckdb and datafusion.

    Examples:
        ```python
        loader = CSVDatasetReader("csv_data/")
        df = loader.to_pandas()
        ```
    """
````

## File: src/flowerpower/plugins/io/loader/deltatable.py
````python
# import datetime as dt
⋮----
# from ..utils import get_dataframe_metadata, get_delta_metadata
⋮----
# from hamilton.function_modifiers import dataloader
⋮----
class DeltaTableReader(BaseDatasetReader)
⋮----
"""Delta table loader.

    This class is responsible for loading Delta tables into several dataframe formats,
    duckdb and datafusion.

    """
⋮----
delta_table: DeltaTable | None = None
with_lock: bool = False
redis: str | None = None
format: str = "delta"
⋮----
def model_post_init(self, __context)
⋮----
def _init_dt(self)
⋮----
@property
    def dt(self) -> DeltaTable
⋮----
def _load(self, reload: bool = False)
⋮----
"""Converts the DeltaTable to a PyArrow Dataset.

        Args:
            metadata (bool, optional): Whether to include metadata. Defaults to False.
            reload (bool, optional): Whether to reload the dataset. Defaults to False.

        Returns:
            pds.Dataset | tuple[pds.Dataset, dict[str, any]]: PyArrow Dataset or tuple of PyArrow Dataset and metadata.
        """
⋮----
metadata = get_pyarrow_dataset_metadata(
⋮----
"""Converts the DeltaTable to a PyArrow Table.

        Args:
            metadata (bool, optional): Whether to include metadata. Defaults to False.
            reload (bool, optional): Whether to reload the table. Defaults to False.

        Returns:
            pa.Table | tuple[pa.Table, dict[str, any]]: PyArrow Table or tuple of PyArrow Table and metadata.
        """
⋮----
metadata = get_dataframe_metadata(table, self._raw_path, "parquet")
⋮----
def _compact()
⋮----
def _z_order()
⋮----
@property
    def metadata(self) -> dict
````

## File: src/flowerpower/plugins/io/loader/duckdb.py
````python
class DuckDBReader(BaseDatabaseReader)
⋮----
"""DuckDB loader.

    This class is responsible for loading dataframes from DuckDB database.

    Examples:
        ```python
        loader = DuckDBReader(table_name="table", path="data.db")
        df = loader.to_polars("SELECT * FROM table WHERE column = 'value'")
        ```
    """
⋮----
type_: str = "duckdb"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/loader/json.py
````python
class JsonFileReader(BaseFileReader)
⋮----
"""
    JSON file loader.

    This class is responsible for loading dataframes from JSON files.

    Examples:
        ```python
        loader = JsonFileReader("data.json")
        df = loader.load()
        ```
    """
⋮----
format: str = "json"
⋮----
def model_post_init(self, __context)
⋮----
class JsonDatasetReader(BaseFileReader)
⋮----
"""
    JSON dataset loader.

    This class is responsible for loading dataframes from JSON dataset.

    Examples:
        ```python
        loader = JsonDatasetReader("json_data/")
        df = loader.load()
        ```
    """
````

## File: src/flowerpower/plugins/io/loader/mqtt.py
````python
class PayloadReader(BaseModel)
⋮----
model_config = ConfigDict(arbitrary_types_allowed=True)
payload: bytes | dict[str, Any]
topic: str | None = None
conn: duckdb.DuckDBPyConnection | None = None
ctx: datafusion.SessionContext | None = None
format: str = "mqtt"
⋮----
def model_post_init(self, __context)
⋮----
df = pa.Table.from_pydict(self.payload)
⋮----
df = pa.Table.from_pylist([self.payload])
⋮----
df = pd.DataFrame(self.payload)
⋮----
df = pd.DataFrame([self.payload])
⋮----
df = pl.DataFrame(self.payload)
⋮----
df = pl.DataFrame([self.payload])
⋮----
df = pl.LazyFrame(self.payload)
⋮----
df = pl.LazyFrame([self.payload])
⋮----
conn = duckdb.connect()
⋮----
rel = self.conn.from_arrow(self.to_pyarrow_table())
⋮----
name = f"mqtt:{self.topic}"
⋮----
ctx = datafusion.SessionContext()
⋮----
def filter(self, filter_expr: str | pl.Expr) -> pl.DataFrame | pl.LazyFrame
⋮----
pl_schema = (
filter_expr = (
````

## File: src/flowerpower/plugins/io/loader/mssql.py
````python
class MSSQLReader(BaseDatabaseReader)
⋮----
"""MSSQL loader.

    This class is responsible for loading dataframes from MSSQL database.

    Examples:
        ```python
        loader = MSSQLReader(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        df = loader.to_polars()

        # or
        loader = MSSQLReader(table_name="table",
                                connection_string="mssql+pyodbc://user:password@localhost:5432/database")
        df = loader.to_pyarrow_table("SELECT * FROM table WHERE column = 'value'")
        ```
    """
⋮----
type_: str = "mssql"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/loader/mysql.py
````python
class MySQLReader(BaseDatabaseReader)
⋮----
"""MySQL loader.

    This class is responsible for loading dataframes from MySQL database.

    Examples:
        ```python
        loader = MySQLReader(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        df = loader.to_polars()

        # or
        loader = MySQLReader(table_name="table",
                                connection_string="mssql+pyodbc://user:password@localhost:5432/database")
        df = loader.to_pyarrow_table("SELECT * FROM table WHERE column = 'value'")
        ```
    """
⋮----
type_: str = "mysql"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/loader/oracle.py
````python
class OracleDBReader(BaseDatabaseReader)
⋮----
"""OracleDB loader.

    This class is responsible for loading dataframes from OracleDB database.

    Examples:
        ```python
        loader = OracleDBReader(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        df = loader.to_polars()

        # or
        loader = OracleDBReader(table_name="table",
                                connection_string="mssql+pyodbc://user:password@localhost:5432/database")
        df = loader.to_pyarrow_table("SELECT * FROM table WHERE column = 'value'")
        ```
    """
⋮----
type_: str = "oracle"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/loader/parquet.py
````python
class ParquetFileReader(BaseFileReader)
⋮----
"""Parquet file loader.

    This class is responsible for loading dataframes from Parquet files.

    Examples:
        ```python
        loader = ParquetFileReader("data.parquet")
        df = loader.load()
        ```
    """
⋮----
format: str = "parquet"
⋮----
def model_post_init(self, __context)
⋮----
class ParquetDatasetReader(BaseDatasetReader)
⋮----
"""Parquet dataset loader.

    This class is responsible for loading dataframes from Parquet dataset.

    Examples:
        ```python
        loader = ParquetDatasetReader("parquet_data/")
        df = loader.load()
        ```
    """
````

## File: src/flowerpower/plugins/io/loader/postgres.py
````python
class PostgreSQLReader(BaseDatabaseReader)
⋮----
"""PostgreSQL loader.

    This class is responsible for loading dataframes from PostgreSQL database.

    Examples:
        ```python
        loader = PostgreSQLReader(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        df = loader.to_polars()

        # or
        loader = PostgreSQLReader(table_name="table",
                                connection_string="mssql+pyodbc://user:password@localhost:5432/database")
        df = loader.to_pyarrow_table("SELECT * FROM table WHERE column = 'value'")
        ```
    """
⋮----
type_: str = "postgres"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/loader/pydala.py
````python
class PydalaDatasetReader(BaseDatasetReader)
⋮----
"""Pydala dataset loader.

    This class is responsible for loading dataframes from Pydala dataset.

    Examples:
        ```python
        loader = PydalaDatasetReader("pydala_data/")
        df = loader.load()
        ```
    """
⋮----
format: str = "parquet"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/loader/sqlite.py
````python
class SQLiteReader(BaseDatabaseReader)
⋮----
"""SQLite loader.

    This class is responsible for loading dataframes from SQLite database.

    Examples:
        ```python
        loader = SQLiteReader(table_name="table", path="data.db")
        df = loader.to_polars("SELECT * FROM table WHERE column = 'value'")

        # or
        loader = SQLiteReader(table_name="table", connection_string="sqlite://data.db")
        df = loader.to_pyarrow_table()
        ```
    """
⋮----
type_: str = "sqlite"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/saver/__init__.py
````python
__all__ = [
````

## File: src/flowerpower/plugins/io/saver/_duckdb.py
````python
class DuckDBSaver(BaseModel)
⋮----
path: str | None = None
table_name: str
mode: Literal["overwrite", "append", "fail", "merge", "update"] = "append"
key_columns: list[str] | None = None  # Required for merge/update modes
conn: duckdb.DuckDBPyConnection | None = None
host: str | None = None
port: int | None = None
socket: str | None = None
user: str | None = None
password: str | None = None
database: str | None = None
⋮----
def _is_sqlite_file(self, path: str) -> bool
⋮----
"""Check if file is SQLite by reading first 16 bytes for SQLite header."""
⋮----
header = f.read(16)
⋮----
def model_post_init(self, __context)
⋮----
# For SQLite files, create in-memory DuckDB and attach SQLite
⋮----
# For DuckDB files, connect directly
⋮----
# For new files, create new DuckDB database
⋮----
def _update_from_env(self)
⋮----
def _attach_postgres(self)
⋮----
connection_string = " ".join(
⋮----
def _attach_mysql(self)
⋮----
def _validate_merge_params(self)
⋮----
# raise ValueError(f"key_columns must be specified for mode '{self.mode}'")
# key columns should be all columns in the table
⋮----
def _table_exists(self) -> bool
⋮----
tables_query = (
result = self.conn.execute(
⋮----
def _handle_existing_table(self) -> bool
⋮----
"""Handle existing table based on mode. Returns True if table exists."""
exists = self._table_exists()
⋮----
"""Write data to database with specified merge strategy.

        Args:
            data: Data to write. Supports pandas/polars DataFrames, pyarrow Tables/Batches, or dicts
        """
mode = mode or self.mode
key_columns = key_columns or self.key_columns
⋮----
data = _dict_to_dataframe(data)
⋮----
data = [data]
⋮----
data = [_dict_to_dataframe(d) for d in data]
⋮----
data = [d.collect() for d in data]
⋮----
data = pl.concat(data, how="diagonal_relaxed").to_arrow()
⋮----
data = pa.concat_tables(
⋮----
data = pa.Table.from_batches(data)
⋮----
data = pa.concat_tables(data, promote_options="permissive")
⋮----
table_exists = self._handle_existing_table()
⋮----
# Convert input to temporary table
temp_name = f"temp_{self.table_name}"
⋮----
# Simple case - just rename temp table
⋮----
# Insert only rows where key columns don't exist in target
key_matches = " AND ".join(f"t.{col} = m.{col}" for col in key_columns)
⋮----
# Create staging table
staging_name = f"staging_{self.table_name}"
⋮----
# First copy all rows from target that don't match key columns
⋮----
# Then add all rows from new data
⋮----
# Replace original with staging
⋮----
# Cleanup
````

## File: src/flowerpower/plugins/io/saver/csv.py
````python
class CSVFileWriter(BaseFileWriter)
⋮----
"""CSV file writer.

    This class is responsible for writing dataframes to CSV files.

    Examples:
        ```python
        writer = CSVFileWriter(df, "data.csv")
        writer.write()
        ```
    """
⋮----
format: str = "csv"
⋮----
def model_post_init(self, __context)
⋮----
class CSVDatasetWriter(BaseDatasetWriter)
⋮----
"""CSV dataset writer.

    This class is responsible for writing dataframes to CSV dataset.

    Examples:
        ```python
        writer = CSVDatasetWriter(df, "csv_data/")
        writer.write()
        ```

    """
````

## File: src/flowerpower/plugins/io/saver/deltatable.py
````python
class DeltaTableWriter(BaseDatasetWriter)
⋮----
"""Delta table writer.

    This class is responsible for writing dataframes to Delta tables.

    Examples:
        ```python
        writer = DeltaTableWriter("data/")
        writer.write(df)
        ```
    """
⋮----
description: str | None = None
with_lock: bool = False
redis: StrictRedis | Redis | None = None
format: str = "delta"
⋮----
def model_post_init(self, __context)
⋮----
mode: str = "append",  # "overwrite" | "append" | "error | "ignore"
⋮----
schema_mode: str | None = None,  # "merge" | "overwrite"
⋮----
# writerproperties
⋮----
"""
        Write data to a Delta table.

        Args:
            data: Data to write
            mode: Write mode
            schema: Schema of the data
            schema_mode: Schema mode
            partition_by: Columns to partition by
            partition_filters: Filters to apply to the partitions
            predicate: Predicate to apply to the data
            target_file_size: Target file size
            large_dtypes: Whether to use large dtypes
            custom_metadata: Custom metadata
            post_commithook_properties: Post-commit hook properties
            commit_properties: Commit properties
            data_page_size_limit: Data page size limit
            dictionary_page_size_limit: Dictionary page size limit
            data_page_row_count_limit: Data page row count limit
            write_batch_size: Write batch size
            max_row_group_size: Maximum row group size
            compression: Compression method
            compression_level: Compression level
            statistics_truncate_length: Statistics truncate length
            default_column_properties: Default column properties
            column_properties: Column properties

        Returns:
            Metadata
        """
⋮----
data = self.data
⋮----
data = _dict_to_dataframe(data)
⋮----
data = [data]
⋮----
data = [_dict_to_dataframe(d) for d in data]
⋮----
data = [d.collect() for d in data]
⋮----
data = pl.concat(data, how="diagonal_relaxed").to_arrow()
⋮----
data = pa.concat_tables(
⋮----
data = pa.Table.from_batches(data)
⋮----
data = pa.concat_tables(data, promote_options="permissive")
⋮----
metadata = get_dataframe_metadata(data, path=self._raw_path, format=self.format)
⋮----
writer_properties = WriterProperties(
⋮----
def _write()
````

## File: src/flowerpower/plugins/io/saver/duckdb.py
````python
class DuckDBWriter(BaseDatabaseWriter)
⋮----
"""DuckDB writer.

    This class is responsible for writing dataframes to DuckDB database.

    Examples:
        ```python
        writer = DuckDBWriter(table_name="table", path="data.db")
        writer.write(df)
        ```
    """
⋮----
type_: str = "duckdb"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/saver/json.py
````python
class JsonFileWriter(BaseFileWriter)
⋮----
"""CSV file writer.

    This class is responsible for writing dataframes to CSV files.

    Examples:
        ```python
        writer = CSVFileWriter(df, "data.csv")
        writer.write()
        ```
    """
⋮----
format: str = "json"
⋮----
def model_post_init(self, __context)
⋮----
class JsonDatasetWriter(BaseFileWriter)
⋮----
"""CSV dataset writer.

    This class is responsible for writing dataframes to CSV dataset.

    Examples:
        ```python
        writer = CSVDatasetWriter([df1, df2], "csv_data/")
        writer.write()
        ```

    """
````

## File: src/flowerpower/plugins/io/saver/mssql.py
````python
class MSSQLWriter(BaseDatabaseWriter)
⋮----
"""MSSQL writer.

    This class is responsible for writing dataframes to MsSQL database.

    Examples:
        ```python
        writer = MSSQLWriter(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        writer.write(df)

        # or
        writer = MSSQLWriter(table_name="table",
                                connection_string="mssql+pyodbc://user:password@localhost:5432/database")
        writer.write(df)
        ```
    """
⋮----
type_: str = "mssql"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/saver/mysql.py
````python
class MySQLWriter(BaseDatabaseWriter)
⋮----
"""MySQL writer.

    This class is responsible for writing dataframes to MySQL database.

    Examples:
        ```python
        writer = MySQLWriter(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        writer.write(df)

        # or
        writer = MySQLWriter(table_name="table",
                                connection_string="mysql+pymsql://user:password@localhost:5432/database")
        writer.write(df)
        ```
    """
⋮----
type_: str = "mysql"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/saver/oracle.py
````python
class OracleDBWriter(BaseDatabaseWriter)
⋮----
"""OracleDB writer.

    This class is responsible for writing dataframes to OracleDB database.

    Examples:
        ```python
        writer = OracleDBWriter(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        writer.write(df)

        # or
        writer = OracleDBWriter(table_name="table",
                                connection_string="mysql+pymsql://user:password@localhost:5432/database")
        writer.write(df)
        ```
    """
⋮----
type_: str = "oracle"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/saver/parquet.py
````python
class ParquetFileWriter(BaseFileWriter)
⋮----
"""CSV file writer.

    This class is responsible for writing dataframes to CSV files.

    Examples:
        ```python
        writer = CSVFileWriter(df, "data.csv")
        writer.write()
        ```
    """
⋮----
format: str = "parquet"
⋮----
def model_post_init(self, __context)
⋮----
class ParquetDatasetWriter(BaseDatasetWriter)
⋮----
"""CSV dataset writer.

    This class is responsible for writing dataframes to CSV dataset.

    Examples:
        ```python
        writer = CSVDatasetWriter(df, "csv_data/")
        writer.write()
        ```

    """
````

## File: src/flowerpower/plugins/io/saver/postgres.py
````python
class PostgreSQLWriter(BaseDatabaseWriter)
⋮----
"""PostgreSQL writer.

    This class is responsible for writing dataframes to PostgreSQL database.

    Examples:
        ```python
        writer = PostgreSQLWriter(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        writer.write(df)

        # or
        writer = PostgreSQLWriter(table_name="table",
                                connection_string="postgresql://user:password@localhost:5432/database")
        writer.write(df)
        ```
    """
⋮----
type_: str = "postgres"
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/saver/pydala.py
````python
class PydalaDatasetWriter(BaseDatasetWriter)
⋮----
"""Writer for Pydala dataset.

    This class is responsible for writing dataframes to Pydala dataset.

    Examples:
        ```python
        writer = PydalaDatasetWriter(path="pydala_data/")
        writer.write(df)
        ```
    """
⋮----
format: str = "parquet"
is_pydala_dataset: bool = True
⋮----
def model_post_init(self, __context)
````

## File: src/flowerpower/plugins/io/saver/sqlite.py
````python
class SQLiteWriter(BaseDatabaseWriter)
⋮----
"""SQLite writer.

    This class is responsible for writing dataframes to SQLite database.

    Examples:
        ```python
        writer = SQLiteWriter(table_name="table", path="data.db")
        writer.write(df)

        # or
        writer = SQLiteWriter(table_name="table",
                                connection_string="sqkite:///data.db")
        writer.write(df)
        ```
    """
⋮----
type_: str = "sqlite"
⋮----
def model_post_init(self, __context)
⋮----
# self.type_ = "sqlite"
````

## File: src/flowerpower/plugins/io/base.py
````python
ParquetDataset = None
⋮----
create_engine = None
text = None
⋮----
class BaseFileIO(BaseModel)
⋮----
"""
    Base class for file I/O operations supporting various storage backends.
    This class provides a foundation for file operations across different storage systems
    including AWS S3, Google Cloud Storage, Azure Blob Storage, GitHub, and GitLab.

    Args:
        path (str | list[str]): Path or list of paths to file(s).
        storage_options (AwsStorageOptions | GcsStorageOptions | AzureStorageOptions |
                             GitHubStorageOptions | GitLabStorageOptions | dict[str, Any] |  None, optional):
            Storage-specific options for accessing remote filesystems.
        fs (AbstractFileSystem, optional): Filesystem instance for handling file operations.
        format (str, optional): File format extension (without dot).

    Notes:
        ```python
        file_io = BaseFileIO(
            path="s3://bucket/path/to/files",
            storage_options=AwsStorageOptions(
                key="access_key",
                secret="secret_key"
        files = file_io.list_files()
        ```
    Notes:
        - Supports multiple cloud storage backends through different storage options
        - Automatically handles filesystem initialization based on path protocol
        - Supports both single path and multiple path inputs
        - Can read credentials from environment variables when using from_env() methods

    """
⋮----
model_config = ConfigDict(arbitrary_types_allowed=True)
path: str | list[str]
storage_options: (
fs: AbstractFileSystem | None = None
format: str | None = None
⋮----
def model_post_init(self, __context)
⋮----
protocol = self.storage_options.protocol
⋮----
protocol = self.fs.protocol
⋮----
protocol = (
⋮----
protocol = protocol[0]
⋮----
@property
    def _path(self)
⋮----
@property
    def _glob_path(self)
⋮----
def list_files(self)
⋮----
class BaseFileReader(BaseFileIO)
⋮----
"""
    Base class for file loading operations supporting various file formats.
    This class provides a foundation for file loading operations across different file formats
    including CSV, Parquet, JSON, Arrow, and IPC.

    Args:
        path (str | list[str]): Path or list of paths to file(s).
        format (str, optional): File format extension (without dot).
        fs (AbstractFileSystem, optional): Filesystem instance for handling file operations.
        include_file_path (bool, optional): Include file path in the output DataFrame.
        concat (bool, optional): Concatenate multiple files into a single DataFrame.
        conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
        ctx (datafusion.SessionContext, optional): DataFusion session context instance.

    Examples:
        ```python
        file_loader = BaseFileReader(
            path="s3://bucket/path/to/files",
            format="csv",
            include_file_path=True,
            concat=True,
            conn=duckdb.connect(),
            ctx=datafusion.SessionContext()
        data = file_loader.to_polars()
        ```
    Notes:
        - Supports multiple file formats including CSV, Parquet, JSON, Arrow, and IPC
        - Automatically handles filesystem initialization based on path protocol
        - Supports both single path and multiple path inputs
        - Supports loading data into DuckDB and DataFusion for SQL operations

    """
⋮----
include_file_path: bool = False
concat: bool = True
batch_size: int | None = None
conn: duckdb.DuckDBPyConnection | None = None
ctx: datafusion.SessionContext | None = None
jsonlines: bool | None = None
partitioning: str | list[str] | pds.Partitioning | None = None
⋮----
def _load(self, reload: bool = False, **kwargs)
⋮----
reload = True
⋮----
"""Convert data to Pandas DataFrame(s).

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            tuple[pd.DataFrame | list[pd.DataFrame], dict[str, Any]] | pd.DataFrame | list[pd.DataFrame]: Pandas
                DataFrame or list of DataFrames and optional metadata.
        """
⋮----
df = [
df = pd.concat(df) if self.concat else df
⋮----
df = (
⋮----
metadata = get_dataframe_metadata(df, path=self.path, format=self.format)
⋮----
"""Iterate over Pandas DataFrames.

        Args:
            batch_size (int, optional): Batch size for iteration. Default is 1.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            Generator[pd.DataFrame, None, None]: Generator of Pandas DataFrames.
        """
⋮----
df = pl.concat(df) if self.concat else df
⋮----
"""Iterate over Polars DataFrames.

        Returns:
            Generator[pl.DataFrame, None, None]: Generator of Polars DataFrames.
        """
⋮----
df = [df.lazy() for df in self._to_polars_dataframe()]
⋮----
df = self._to_polars_dataframe.lazy()
⋮----
"""Iterate over Polars LazyFrames.

        Args:
            batch_size (int, optional): Batch size for iteration. Default is 1.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            Generator[pl.LazyFrame, None, None]: Generator of Polars LazyFrames.
        """
⋮----
"""Convert data to Polars DataFrame or LazyFrame.

        Args:
            lazy (bool, optional): Return a LazyFrame if True, else a DataFrame.
            metadata (bool, optional): Include metadata in the output. Default is False.

        Returns:
            pl.DataFrame | pl.LazyFrame | list[pl.DataFrame] | list[pl.LazyFrame] | tuple[pl.DataFrame | pl.LazyFrame
                | list[pl.DataFrame] | list[pl.LazyFrame], dict[str, Any]]: Polars DataFrame or LazyFrame and optional
                metadata.
        """
⋮----
"""Convert data to PyArrow Table(s).

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            pa.Table | list[pa.Table] | tuple[pa.Table | list[pa.Table], dict[str, Any]]: PyArrow Table or list of
                Tables and optional metadata.
        """
⋮----
df = pa.concat_tables(df) if self.concat else df
⋮----
"""Iterate over PyArrow Tables.

        Returns:
            Generator[pa.Table, None, None]: Generator of PyArrow Tables.
        """
⋮----
"""Convert data to DuckDB relation.

        Args:
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            duckdb.DuckDBPyRelation | tuple[duckdb.DuckDBPyRelation, dict[str, Any]]: DuckDB relation and optional
                metadata.
        """
⋮----
conn = duckdb.connect()
⋮----
"""Register data in DuckDB.

        Args:
            conn (duckdb.DuckDBPyConnection): DuckDB connection instance.
            name (str, optional): Name for the DuckDB table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]: DuckDB connection instance
                or DuckDB connection instance and optional metadata.
        """
⋮----
name = f"{self.format}:{self.path}"
⋮----
"""Convert data to DuckDB relation or register in DuckDB.

        Args:
            as_relation (bool, optional): Return a DuckDB relation if True, else register in DuckDB. Default is True.
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            name (str, optional): Name for the DuckDB table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyRelation | duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyRelation, dict[str, Any]] |
                tuple[duckdb.DuckDBPyConnection, dict[str, Any]]: DuckDB relation or connection instance
                or DuckDB relation or connection instance and optional metadata.

        """
⋮----
"""Register data in DataFusion.

        Args:
            ctx (datafusion.SessionContext): DataFusion session context instance.
            name (str, optional): Name for the DataFusion table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
⋮----
ctx = datafusion.SessionContext()
⋮----
"""Filter data based on a filter expression.

        Args:
            filter_expr (str | pl.Expr | pa.compute.Expression): Filter expression. Can be a SQL expression, Polars
                expression, or PyArrow compute expression.

        Returns:
            pl.DataFrame | pl.LazyFrame | pa.Table | list[pl.DataFrame] | list[pl.LazyFrame]
                | list[pa.Table]: Filtered data.
        """
⋮----
pl_schema = (
filter_expr = (
⋮----
pa_schema = self._data.schema
⋮----
pa_schema = self._data[0].schema
⋮----
@property
    def metadata(self)
⋮----
class BaseDatasetReader(BaseFileReader)
⋮----
"""
    Base class for dataset loading operations supporting various file formats.
    This class provides a foundation for dataset loading operations across different file formats
    including CSV, Parquet, JSON, Arrow, and IPC.

    Args:
        path (str | list[str]): Path or list of paths to file(s).
        format (str, optional): File format extension (without dot).
        fs (AbstractFileSystem, optional): Filesystem instance for handling file operations.
        include_file_path (bool, optional): Include file path in the output DataFrame.
        concat (bool, optional): Concatenate multiple files into a single DataFrame.
        conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
        ctx (datafusion.SessionContext, optional): DataFusion session context instance.
        schema (pa.Schema, optional): PyArrow schema for the dataset.
        partitioning (str | list[str] | pds.Partitioning, optional): Dataset partitioning scheme.

        Examples:
        ```python
        dataset_loader = BaseDatasetReader(
            path="s3://bucket/path/to/files",
            format="csv",
            include_file_path=True,
            concat=True,
            conn=duckdb.connect(),
            ctx=datafusion.SessionContext(),
            schema=pa.schema([
                pa.field("column1", pa.int64()),
                pa.field("column2", pa.string())
            ]),
            partitioning="hive"
        )
        data = dataset_loader.to_polars()
        ```
    Notes:
        - Supports multiple file formats including CSV, Parquet, JSON, Arrow, and IPC
        - Automatically handles filesystem initialization based on path protocol
        - Supports both single path and multiple path inputs
        - Supports loading data into DuckDB and DataFusion for SQL operations
        - Supports custom schema and partitioning for datasets

    """
⋮----
schema_: pa.Schema | None = None
⋮----
"""
        Convert data to PyArrow Dataset.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            pds.Dataset: PyArrow Dataset.
        """
⋮----
"""
        Convert data to Pandas DataFrame.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.

        Returns:
            pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]: Pandas DataFrame and optional metadata.
        """
⋮----
df = self._dataset.to_table().to_pandas()
⋮----
df = pl.from_arrow(self._dataset.to_table())
⋮----
df = pl.scan_pyarrow_dataset(self._dataset)
⋮----
"""
        Convert data to Polars DataFrame or LazyFrame.

        Args:
            lazy (bool, optional): Return a LazyFrame if True, else a DataFrame.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            pl.DataFrame | pl.LazyFrame | tuple[pl.DataFrame | pl.LazyFrame, dict[str, Any]]: Polars DataFrame or
                LazyFrame and optional metadata.
        """
⋮----
"""Convert data to PyArrow Table.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.

        Returns:
            pa.Table | tuple[pa.Table, dict]: PyArrow Table and optional metadata.
        """
⋮----
df = self._dataset.to_table()
⋮----
) -> ParquetDataset | tuple[ParquetDataset, dict[str, Any]]:  # type: ignore
"""Convert data to Pydala ParquetDataset.

        Args:
            metadata (bool, optional): Include metadata in the output. Default is False.

        Returns:
            ParquetDataset: Pydala ParquetDataset.
        """
⋮----
"""Register data in DuckDB.

        Args:
            conn (duckdb.DuckDBPyConnection): DuckDB connection instance.
            name (str, optional): Name for the DuckDB table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            reload (bool, optional): Reload data if True. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyConnection | tuple[duckdb.DuckDBPyConnection, dict[str, Any]]: DuckDB connection instance
                or DuckDB connection instance and optional metadata.
        """
⋮----
"""Convert data to DuckDB relation or register in DuckDB.

        Args:
            as_relation (bool, optional): Return a DuckDB relation if True, else register in DuckDB. Default is True.
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            name (str, optional): Name for the DuckDB table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyRelation | duckdb.DuckDBPyConnection: DuckDB relation or connection instance.
        """
⋮----
"""Register data in DataFusion.

        Args:
            ctx (datafusion.SessionContext): DataFusion session context instance.
            name (str, optional): Name for the DataFusion table.
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            datafusion.SessionContext | tuple[datafusion.SessionContext, dict[str, Any]]: DataFusion session
                context or instance and optional metadata.
        """
⋮----
def filter(self, filter_exp: str | pa.compute.Expression) -> pds.Dataset
⋮----
"""
        Filter data based on a filter expression.

        Args:
            filter_exp (str | pa.compute.Expression): Filter expression. Can be a SQL expression or
                PyArrow compute expression.

        Returns:
            pds.Dataset: Filtered dataset.

        """
⋮----
filter_exp = sql2pyarrow_filter(filter_exp, self._dataset.schema)
⋮----
class BaseFileWriter(BaseFileIO)
⋮----
"""
    Base class for file writing operations supporting various storage backends.
    This class provides a foundation for file writing operations across different storage systems
    including AWS S3, Google Cloud Storage, Azure Blob Storage, GitHub, and GitLab.

    Args:
        path (str | list[str]): Path or list of paths to file(s).
        storage_options (AwsStorageOptions | GcsStorageOptions | AzureStorageOptions |
                             GitHubStorageOptions | GitLabStorageOptions | dict[str, Any] |  None, optional):
                             Storage-specific options for accessing remote filesystems.
        fs (AbstractFileSystem, optional): Filesystem instance for handling file operations.
        format (str, optional): File format extension (without dot).
        basename (str, optional): Basename for the output file(s).
        concat (bool, optional): Concatenate multiple files into a single DataFrame.
        mode (str, optional): Write mode (append, overwrite, delete_matching, error_if_exists).
        unique (bool | list[str] | str, optional): Unique columns for deduplication.

    Examples:
        ```python
        file_writer = BaseFileWriter(
            path="s3://bucket/path/to/files",
            storage_options=AwsStorageOptions(
                key="access_key",
                secret="secret_key"),
            format="csv",
            basename="output",
            concat=True,
            mode="append",
            unique=True
        )
        file_writer.write(data=df)
        ```

    Notes:
        - Supports multiple cloud storage backends through different storage options
        - Automatically handles filesystem initialization based on path protocol
        - Supports both single path and multiple path inputs
        - Supports writing data to cloud storage with various write modes
    """
⋮----
basename: str | None = None
concat: bool = False
mode: str = "append"  # append, overwrite, delete_matching, error_if_exists
unique: bool | list[str] | str = False
⋮----
"""
        Write data to file.

        Args:
            data (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict[str, Any] | list[pl.DataFrame |
                pl.LazyFrame | pa.Table | pd.DataFrame | dict[str, Any]] | None, optional): Data to write.
            basename (str, optional): Basename for the output file(s).
            concat (bool, optional): Concatenate multiple files into a single DataFrame.
            unique (bool | list[str] | str, optional): Unique columns for deduplication.
            mode (str, optional): Write mode (append, overwrite, delete_matching, error_if_exists).
            **kwargs: Additional keyword arguments.

        Returns:
            dict[str, Any]: Metadata for the written data
        """
⋮----
data = _dict_to_dataframe(data)
⋮----
data=data,  # if data is not None else self.data,
⋮----
class BaseDatasetWriter(BaseFileWriter)
⋮----
"""
    Base class for dataset writing operations supporting various file formats.
    This class provides a foundation for dataset writing operations across different file formats
    including CSV, Parquet, JSON, Arrow, and IPC.

    Args:
        path (str | list[str]): Path or list of paths to file(s).
        format (str, optional): File format extension (without dot).
        storage_options (AwsStorageOptions | GcsStorageOptions | AzureStorageOptions |
                                GitHubStorageOptions | GitLabStorageOptions | dict[str, Any] |  None, optional):
            Storage-specific options for accessing remote filesystems.
        fs (AbstractFileSystem, optional): Filesystem instance for handling file operations.
        basename (str, optional): Basename for the output file(s).
        schema (pa.Schema, optional): PyArrow schema for the dataset.
        partition_by (str | list[str] | pds.Partitioning, optional): Dataset partitioning scheme.
        partitioning_flavor (str, optional): Partitioning flavor for the dataset.
        compression (str, optional): Compression codec for the dataset.
        row_group_size (int, optional): Row group size for the dataset.
        max_rows_per_file (int, optional): Maximum number of rows per file.
        concat (bool, optional): Concatenate multiple files into a single DataFrame.
        unique (bool | list[str] | str, optional): Unique columns for deduplication.
        mode (str, optional): Write mode (append, overwrite, delete_matching, error_if_exists).
        is_pydala_dataset (bool, optional): Write data as a Pydala ParquetDataset.

    Examples:
        ```python
        dataset_writer = BaseDatasetWriter(
            path="s3://bucket/path/to/files",
            format="parquet",
            storage_options=AwsStorageOptions(
                key="access_key",
                secret="secret_key"),
            basename="output",
            schema=pa.schema([
                pa.field("column1", pa.int64()),
                pa.field("column2", pa.string())
            ]),
            partition_by="column1",
            partitioning_flavor="hive",
            compression="zstd",
            row_group_size=250_000,
            max_rows_per_file=2_500_000,
            concat=True,
            unique=True,
            mode="append",
            is_pydala_dataset=False
        )
        dataset_writer.write(data=df)
        ```
    Notes:
        - Supports multiple file formats including CSV, Parquet, JSON, Arrow, and IPC
        - Automatically handles filesystem initialization based on path protocol
        - Supports both single path and multiple path inputs
        - Supports writing data to cloud storage with various write modes
        - Supports writing data as a Pydala ParquetDataset
    """
⋮----
partition_by: str | list[str] | pds.Partitioning | None = None
partitioning_flavor: str | None = None
compression: str = "zstd"
row_group_size: int | None = 250_000
max_rows_per_file: int | None = 2_500_000
⋮----
is_pydala_dataset: bool = False
⋮----
"""
        Write data to dataset.

        Args:
            data (pl.DataFrame | pl.LazyFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader | pd.DataFrame |
                dict[str, Any] | list[pl.DataFrame | pl.LazyFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader |
                pd.DataFrame | dict[str, Any]] | None, optional): Data to write.
            unique (bool | list[str] | str, optional): Unique columns for deduplication.
            delta_subset (str | None, optional): Delta subset for incremental updates.
            alter_schema (bool, optional): Alter schema for compatibility.
            update_metadata (bool, optional): Update metadata.
            timestamp_column (str | None, optional): Timestamp column for updates.
            verbose (bool, optional): Verbose output.
            **kwargs: Additional keyword arguments.

        Returns:
            dict[str, Any]: Metadata of the written data.
        """
basename = kwargs.pop("basename", self.basename)
schema = kwargs.pop("schema", self.schema_)
partition_by = kwargs.pop("partition_by", self.partition_by)
partitioning_flavor = kwargs.pop(
compression = kwargs.pop("compression", self.compression)
row_group_size = kwargs.pop("row_group_size", self.row_group_size)
max_rows_per_file = kwargs.pop("max_rows_per_file", self.max_rows_per_file)
⋮----
data=data,  # if data is not None else self.data,
⋮----
class BaseDatabaseIO(BaseModel)
⋮----
"""
    Base class for database read/write operations supporting various database systems.
    This class provides a foundation for database read/write operations across different database systems
    including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle.

    Args:
        type_ (str): Database type (sqlite, duckdb, postgres, mysql, mssql, oracle).
        table_name (str): Table name in the database.
        path (str | None, optional): File path for SQLite or DuckDB databases.
        connection_string (str | None, optional): Connection string for SQLAlchemy-based databases.
        username (str | None, optional): Username for the database.
        password (str | None, optional): Password for the database.
        server (str | None, optional): Server address for the database.
        port (str | None, optional): Port number for the database.
        database (str | None, optional): Database name.
        mode (str, optional): Write mode (append, replace, fail).

    Examples:
        ```python
        db_reader = BaseDatabaseIO(
            type_="sqlite",
            table_name="table_name",
            path="path/to/database.db"
        )
        data = db_reader.read()
        ```

    Notes:
        - Supports multiple database systems including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle
        - Automatically handles database initialization based on connection parameters
        - Supports reading data from databases into DataFrames
        - Supports writing data to databases from DataFrames
    """
⋮----
type_: str  # "sqlite", "duckdb", "postgres", "mysql", "mssql", or "oracle"
table_name: str
path: str | None = None  # For sqlite or duckdb file paths
connection_string: str | None = None  # For SQLAlchemy-based databases
username: str | None = None
password: str | None = None
server: str | None = None
port: str | int | None = None
database: str | None = None
ssl: bool = False
⋮----
db = self.type_.lower()
⋮----
ssl_mode = "?sslmode=require" if self.ssl else ""
⋮----
ssl_mode = "?ssl=true" if self.ssl else ""
⋮----
ssl_mode = ";Encrypt=yes;TrustServerCertificate=yes" if self.ssl else ""
⋮----
def execute(self, query: str, cursor: bool = True, **query_kwargs)
⋮----
"""Execute a SQL query.

        Args:
            query (str): SQL query.
            cursor (bool, optional): Use cursor for execution. Default is True.
            **query_kwargs: Additional keyword arguments.
        """
query = query.format(**query_kwargs)
⋮----
cur = conn.cursor()
res = cur.execute(query)
⋮----
res = conn.execute(query)
⋮----
res = cur.execute(text(query))
⋮----
# convert data to pandas DataFrame if needed
⋮----
def create_engine(self)
⋮----
def connect(self)
⋮----
conn = sqlite3.connect(self.path)
# Activate WAL mode:
⋮----
class BaseDatabaseWriter(BaseDatabaseIO)
⋮----
"""
    Base class for database writing operations supporting various database systems.
    This class provides a foundation for database writing operations across different database systems
    including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle.

    Args:
        type_ (str): Database type (sqlite, duckdb, postgres, mysql, mssql, oracle).
        table_name (str): Table name in the database.
        path (str | None, optional): File path for SQLite or DuckDB databases.
        connection_string (str | None, optional): Connection string for SQLAlchemy-based databases.
        username (str | None, optional): Username for the database.
        password (str | None, optional): Password for the database.
        server (str | None, optional): Server address for the database.
        port (str | None, optional): Port number for the database.
        database (str | None, optional): Database name.
        mode (str, optional): Write mode (append, replace, fail).
        concat (bool, optional): Concatenate multiple files into a single DataFrame.
        unique (bool | list[str] | str, optional): Unique columns for deduplication.

    Examples:
        ```python
        db_writer = BaseDatabaseWriter(
            type_="sqlite",
            table_name="table_name",
            path="path/to/database.db"
        )
        db_writer.write(data=df)
        ```

    Notes:
        - Supports multiple database systems including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle
        - Automatically handles database initialization based on connection parameters
        - Supports writing data to databases from DataFrames
    """
⋮----
mode: str = "append"  # append, replace, fail
⋮----
data = to_pyarrow_table(
⋮----
data = [data]
⋮----
# Activate WAL mode:
⋮----
df = self._to_pandas(_data)
⋮----
conn = duckdb.connect(database=self.path)
mode = mode or self.mode
⋮----
engine = create_engine(self.connection_string)
⋮----
"""
        Write data to database.

        Args:
            data (pl.DataFrame | pl.LazyFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader | pd.DataFrame |
                dict[str, Any] | list[pl.DataFrame | pl.LazyFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader |
                pd.DataFrame | dict[str, Any]] | None, optional): Data to write.
            mode (str, optional): Write mode (append, replace, fail).
            concat (bool, optional): Concatenate multiple files into a single DataFrame.
            unique (bool | list[str] | str, optional): Unique columns for deduplication.

        Returns:
            dict[str, Any]: Metadata of the written data
        """
⋮----
class BaseDatabaseReader(BaseDatabaseIO)
⋮----
"""
    Base class for database read operations supporting various database systems.
    This class provides a foundation for database read operations across different database systems
    including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle.

    Args:
        type_ (str): Database type (sqlite, duckdb, postgres, mysql, mssql, oracle).
        table_name (str): Table name in the database.
        path (str | None, optional): File path for SQLite or DuckDB databases.
        connection_string (str | None, optional): Connection string for SQLAlchemy-based databases.
        username (str | None, optional): Username for the database.
        password (str | None, optional): Password for the database.
        server (str | None, optional): Server address for the database.
        port (str | None, optional): Port number for the database.
        database (str | None, optional): Database name.
        query (str | None, optional): SQL query to execute.

    Examples:
        ```python
        db_reader = BaseDatabaseReader(
            type_="sqlite",
            table_name="table_name",
            path="path/to/database.db"
        )
        data = db_reader.read()
        ```
    Notes:
        - Supports multiple database systems including SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, and Oracle
        - Automatically handles database initialization based on connection parameters
        - Supports reading data from databases into DataFrames
    """
⋮----
query: str | None = None
⋮----
def _load(self, query: str | None = None, reload: bool = False, **kwargs) -> None
⋮----
"""Load data from database.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
⋮----
query = f"SELECT * FROM {self.table_name}"
⋮----
query = query.replace("table", self.table_name)
⋮----
engine = kwargs.pop("engine", "adbc")
⋮----
engine = "adbc"
⋮----
cs = self.connection_string.replace("///", "//")
⋮----
cs = self.connection_string
data = (
⋮----
"""Convert data to Polars DataFrame.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            pl.DataFrame | tuple[pl.DataFrame, dict[str, Any]]: Polars DataFrame or tuple of DataFrame and metadata.
        """
⋮----
df = pl.from_arrow(self._data)
⋮----
"""Convert data to Pandas DataFrame.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]: Pandas DataFrame or tuple of DataFrame and metadata.
        """
⋮----
df = self._data.to_pandas()
⋮----
"""Convert data to PyArrow Table.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            pa.Table | tuple[pa.Table, dict[str, Any]]: PyArrow Table or tuple of Table and metadata.
        """
⋮----
"""Convert data to DuckDB relation.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            metadata (bool, optional): Include metadata in the output. Default is False.
            **kwargs: Additional keyword arguments.

        Returns:
            duckdb.DuckDBPyRelation: DuckDB relation.
        """
⋮----
"""Register data in DuckDB.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            conn (duckdb.DuckDBPyConnection, optional): DuckDB connection instance.
            name (str, optional): Name of the relation.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
⋮----
name = f"{self.type_}:{self.table_name}"
⋮----
"""Register data in DataFusion.

        Args:
            query (str, optional): SQL query to execute. If None, loads all data from the table.
            reload (bool, optional): Reload data if True.
            ctx (datafusion.SessionContext, optional): DataFusion session context instance.
            name (str, optional): Name of the relation.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
````

## File: src/flowerpower/plugins/io/metadata.py
````python
"""
    Convert DataFrame dtypes to a serializable dictionary.

    Args:
        data:  DataFrame

    Returns:
        dict mapping column names to dtype strings
    """
⋮----
"""
    Get metadata for a DataFrame.

    Args:
        df: DataFrame
        path: Path to the file(s) that the DataFrame was loaded from
        fs: Optional filesystem
        kwargs: Additional metadata fields

    Returns:
        dict: DataFrame metadata
    """
⋮----
schema = get_serializable_schema(df[0])
num_rows = sum(df_.shape[0] for df_ in df)
⋮----
schema = get_serializable_schema(df)
num_rows = df.shape[0] if hasattr(df, "shape") else None
⋮----
num_files = len(path)
⋮----
path_ = path_to_glob(path=path, format=format)
num_files = len(fs.glob(path_)) if fs is not None else None
⋮----
schema = {k: v for k, v in schema.items() if k not in partition_columns}
⋮----
metadata = {
⋮----
"""
    Get metadata for a DuckDBPyRelation.

    Args:
        rel: DuckDBPyRelation
        path: Path to the file(s) that the DuckDBPyRelation was loaded from
        fs: Filesystem
        include_shape: Include shape in metadata
        include_num_files: Include number of files in metadata
        kwargs: Additional metadata fields

    Returns:
        dict: DuckDBPyRelation metadata
    """
⋮----
schema = get_serializable_schema(rel)
⋮----
shape = rel.shape
⋮----
shape = None
⋮----
schema = get_serializable_schema(ds.schema)
⋮----
dt_meta = dtable.metadata()
dt_schema = dtable.schema().to_pyarrow()
⋮----
payload = orjson.loads(payload)
⋮----
schema = get_serializable_schema(payload)
⋮----
def get_mqtt_metadata(*args, **kwargs)
````

## File: src/flowerpower/web/templates/base.html
````html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}FlowerPower Dashboard{% endblock %}</title>
    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .nav-links {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        
        .nav-links a {
            padding: 10px 15px;
            background-color: #f5f5f5;
            border-radius: 4px;
            text-decoration: none;
            color: #333;
            font-weight: 500;
        }
        
        .nav-links a:hover {
            background-color: #e5e5e5;
        }
        
        .section {
            margin: 20px 0;
        }
        
        .actions {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        
        .btn {
            padding: 10px 15px;
            background-color: #4a7ddd;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            background-color: #3a6dc5;
        }
        
        .btn-danger {
            background-color: #e74c3c;
        }
        
        .btn-danger:hover {
            background-color: #c0392b;
        }
        
        .alert {
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
        
        .alert-success {
            background-color: #d4edda;
            color: #155724;
        }
        
        .alert-danger {
            background-color: #f8d7da;
            color: #721c24;
        }
        
        .alert-warning {
            background-color: #fff3cd;
            color: #856404;
        }
        
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-control {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .schedule-item {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <header>
        <h1>FlowerPower Dashboard</h1>
        <div class="nav-links">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('list_pipelines') }}">Pipelines</a>
            <a href="{{ url_for('list_schedules') }}">Schedules</a>
            <a href="{{ url_for('new_pipeline') }}">Create Pipeline</a>
        </div>
    </header>
    
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category if category != 'message' else 'success' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>
````

## File: src/flowerpower/web/templates/index.html
````html
{% extends "base.html" %}

{% block content %}
    <h2>Welcome to FlowerPower Dashboard</h2>
    <p>Use the navigation to manage your pipelines and schedules.</p>
    
    <div class="section">
        <h3>Quick Links</h3>
        <div class="nav-links">
            <a href="{{ url_for('list_pipelines') }}">View All Pipelines</a>
            <a href="{{ url_for('list_schedules') }}">View All Schedules</a>
            <a href="{{ url_for('new_pipeline') }}">Create New Pipeline</a>
        </div>
    </div>
{% endblock %}
````

## File: src/flowerpower/web/templates/index1.html
````html
{% extends "base.html" %}

{% block title %}FlowerPower Dashboard{% endblock %}

{% block content %}
<div class="space-y-6">
    <!-- Header -->
    <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
            <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
                FlowerPower Dashboard
            </h2>
        </div>
        <div class="flex mt-4 md:mt-0 md:ml-4 space-x-3">
            <a href="/pipelines/">
                <button type="button" class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    View All Pipelines
                </button>
            </a>
            <button type="button" data-ds-toggle="modal" data-ds-target="newPipelineModal" class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                New Pipeline
            </button>
        </div>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <!-- Pipeline stats -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
                <div class="flex items-center">
                    <div class="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                        <svg class="h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path>
                        </svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-gray-500 truncate">
                                Total Pipelines
                            </dt>
                            <dd class="flex items-baseline">
                                <div class="text-2xl font-semibold text-gray-900">
                                    {{ pipelines|default([])|length }}
                                </div>
                            </dd>
                        </dl>
                    </div>
                </div>
            </div>
            <div class="bg-gray-50 px-4 py-4 sm:px-6">
                <div class="text-sm">
                    <a href="/pipelines/" class="font-medium text-indigo-600 hover:text-indigo-500">
                        View all pipelines
                    </a>
                </div>
            </div>
        </div>

        <!-- Scheduled Jobs -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
                <div class="flex items-center">
                    <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
                        <svg class="h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                        <dl>
                            <dt class="text-sm font-medium text-gray-500 truncate">
                                Scheduled Jobs
                            </dt>
                            <dd class="flex items-baseline">
                                <div class="text-2xl font-semibold text-gray-900">
                                    {% if has_scheduler %}
                                        {{ schedules|length }}
                                    {% else %}
                                        N/A
                                    {% endif %}
                                </div>
                            </dd>
                        </dl>
                    </div>
                </div>
            </div>
            <div class="bg-gray-50 px-4 py-4 sm:px-6">
                <div class="text-sm">
                    <a href="/scheduler/" class="font-medium text-green-600 hover:text-green-500">
                        {% if has_scheduler %}
                            View scheduler
                        {% else %}
                            Scheduler not available
                        {% endif %}
                    </a>
                </div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
                <h3 class="text-lg leading-6 font-medium text-gray-900">Quick Actions</h3>
                <div class="mt-4 space-y-2">
                    <a href="/pipelines/" class="block px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-gray-700">
                        <span class="text-indigo-600">→</span> Browse Pipelines
                    </a>
                    {% if has_scheduler %}
                    <a href="/scheduler/" class="block px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-gray-700">
                        <span class="text-green-600">→</span> Manage Schedules
                    </a>
                    {% endif %}
                    <a href="/config/project" class="block px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-gray-700">
                        <span class="text-purple-600">→</span> Edit Project Config
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Recent Pipelines -->
    <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
            <h3 class="text-lg leading-6 font-medium text-gray-900">
                Recent Pipelines
            </h3>
        </div>
        <ul class="divide-y divide-gray-200">
            {% if pipelines %}
                {% for pipeline in pipelines[:5] %}
                <li>
                    <a href="/pipelines/{{ pipeline.name }}" class="block hover:bg-gray-50">
                        <div class="px-4 py-4 sm:px-6">
                            <div class="flex items-center justify-between">
                                <p class="text-sm font-medium text-indigo-600 truncate">
                                    {{ pipeline.name }}
                                </p>
                                <div class="ml-2 flex-shrink-0 flex">
                                    <a href="/pipelines/{{ pipeline.name }}/edit" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 hover:bg-blue-200">
                                        Edit
                                    </a>
                                </div>
                            </div>
                            <div class="mt-2 sm:flex sm:justify-between">
                                <div class="sm:flex">
                                    <p class="flex items-center text-sm text-gray-500">
                                        <svg class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                                        </svg>
                                        {{ pipeline.mod_time if pipeline is defined and pipeline.mod_time is defined else 'No modification time' }}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </a>
                </li>
                {% endfor %}
            {% else %}
                <li class="px-4 py-5 sm:px-6 text-center text-gray-500">
                    No pipelines found. Create one to get started.
                </li>
            {% endif %}
        </ul>
    </div>

    <!-- Recent Scheduled Jobs -->
    {% if has_scheduler and schedules %}
    <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
            <h3 class="text-lg leading-6 font-medium text-gray-900">
                Recent Scheduled Jobs
            </h3>
        </div>
        <ul class="divide-y divide-gray-200">
            {% for schedule in schedules[:5] %}
            <li>
                <div class="px-4 py-4 sm:px-6">
                    <div class="flex items-center justify-between">
                        <p class="text-sm font-medium text-indigo-600 truncate">
                            {{ schedule.id }}
                        </p>
                        <div class="ml-2 flex-shrink-0 flex space-x-2">
                            {% if schedule.paused %}
                            <button data-ds-fetch="/scheduler/resume-schedule/{{ schedule.id }}" data-ds-method="POST" data-ds-target="#scheduleStatus{{ loop.index }}" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800 hover:bg-yellow-200">
                                Resume
                            </button>
                            {% else %}
                            <button data-ds-fetch="/scheduler/pause-schedule/{{ schedule.id }}" data-ds-method="POST" data-ds-target="#scheduleStatus{{ loop.index }}" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 hover:bg-green-200">
                                Pause
                            </button>
                            {% endif %}
                            <button data-ds-fetch="/scheduler/remove-schedule/{{ schedule.id }}" data-ds-method="DELETE" data-ds-target="closest li" data-ds-swap="outerHTML" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800 hover:bg-red-200">
                                Remove
                            </button>
                        </div>
                    </div>
                    <div class="mt-2 sm:flex sm:justify-between">
                        <div class="sm:flex">
                            <p id="scheduleStatus{{ loop.index }}" class="flex items-center text-sm text-gray-500">
                                <svg class="flex-shrink-0 mr-1.5 h-5 w-5 {{ 'text-yellow-400' if schedule.paused else 'text-green-400' }}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                                </svg>
                                {{ 'Paused' if schedule.paused else 'Active' }}
                            </p>
                        </div>
                    </div>
                </div>
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
</div>

<!-- New Pipeline Modal -->
<div id="newPipelineModal" class="hidden fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>

        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
            <div>
                <div class="mt-3 text-center sm:mt-5">
                    <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                        Create New Pipeline
                    </h3>
                    <div class="mt-2">
                        <form data-ds-fetch="/pipelines/new" data-ds-method="POST">
                            <div class="mt-4">
                                <label for="name" class="block text-sm font-medium text-gray-700 text-left">
                                    Pipeline Name
                                </label>
                                <div class="mt-1">
                                    <input type="text" name="name" id="name" class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md" required>
                                </div>
                                <p class="mt-2 text-sm text-gray-500 text-left">
                                    Name of your new pipeline (e.g., "data_processing" or "model_training")
                                </p>
                            </div>

                            <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
                                <button type="submit" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:col-start-2 sm:text-sm">
                                    Create
                                </button>
                                <button type="button" data-ds-toggle="modal" data-ds-target="newPipelineModal" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:col-start-1 sm:text-sm">
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
````

## File: src/flowerpower/web/templates/new_pipeline.html
````html
{% extends "base.html" %}

{% block title %}Create New Pipeline - FlowerPower{% endblock %}

{% block content %}
    <h2>Create New Pipeline</h2>
    
    <form action="{{ url_for('new_pipeline') }}" method="post">
        <div class="form-group">
            <label for="name">Pipeline Name:</label>
            <input type="text" id="name" name="name" class="form-control" required>
        </div>
        
        <div class="actions">
            <button type="submit" class="btn">Create Pipeline</button>
        </div>
    </form>
{% endblock %}
````

## File: src/flowerpower/web/templates/pipeline_detail.html
````html
{% extends "base.html" %}

{% block title %}Pipeline: {{ n }} - FlowerPower{% endblock %}

{% block content %}
    <h2>Pipeline: {{ n }}</h2>
    
    <div class="section">
        <h3>Configuration</h3>
        <ul>
            {% for key, value in info.cfg.items() %}
                {% if value is mapping %}
                    <li>{{ key }}:
                        <ul>
                            {% for subkey, subvalue in value.items() %}
                                <li>{{ subkey }}: {{ subvalue }}</li>
                            {% endfor %}
                        </ul>
                    </li>
                {% else %}
                    <li>{{ key }}: {{ value }}</li>
                {% endif %}
            {% endfor %}
        </ul>
    </div>
    
    <div class="section">
        <h3>Module</h3>
        <pre><code>{{ info.module }}</code></pre>
    </div>
    
    <div class="actions">
        <form id="run-form" action="{{ url_for('run_pipeline', n=n) }}" method="post" style="display: inline;">
            <button type="submit" class="btn">Run Pipeline</button>
        </form>
        
        <a href="{{ url_for('schedule_pipeline', n=n) }}" class="btn">Schedule Pipeline</a>
        
        <form id="delete-form" action="{{ url_for('delete_pipeline', n=n) }}" method="post" style="display: inline;">
            <button type="submit" class="btn btn-danger" onclick="return confirm('Are you sure you want to delete this pipeline?');">Delete Pipeline</button>
        </form>
    </div>
    
    <div id="result"></div>
    
    <script>
        document.getElementById('run-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            fetch(this.action, {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                
                if (data.status === 'success') {
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h3>Pipeline Execution Result</h3>
                            <p>${data.message}</p>
                            <pre><code>${data.result}</code></pre>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <h3>Pipeline Execution Failed</h3>
                            <p>${data.message}</p>
                        </div>
                    `;
                }
            })
            .catch(error => {
                document.getElementById('result').innerHTML = `
                    <div class="alert alert-danger">
                        <h3>Pipeline Execution Failed</h3>
                        <p>An error occurred: ${error}</p>
                    </div>
                `;
            });
        });
    </script>
{% endblock %}
````

## File: src/flowerpower/web/templates/pipelines.html
````html
{% extends "base.html" %}

{% block title %}Pipelines - FlowerPower{% endblock %}

{% block content %}
    <h2>Available Pipelines</h2>
    
    {% if pipelines %}
        <ul>
            {% for pipeline in pipelines %}
                <li><a href="{{ url_for('pipeline_detail', n=pipeline) }}">{{ pipeline }}</a></li>
            {% endfor %}
        </ul>
    {% else %}
        <p>No pipelines found.</p>
    {% endif %}
    
    <div class="actions">
        <a href="{{ url_for('new_pipeline') }}" class="btn">Create New Pipeline</a>
    </div>
{% endblock %}
````

## File: src/flowerpower/web/templates/schedule_pipeline.html
````html
{% extends "base.html" %}

{% block title %}Schedule Pipeline: {{ n }} - FlowerPower{% endblock %}

{% block content %}
    <h2>Schedule Pipeline: {{ n }}</h2>
    
    <form action="{{ url_for('schedule_pipeline', n=n) }}" method="post">
        <div class="form-group">
            <label for="trigger_type">Trigger Type:</label>
            <select id="trigger_type" name="trigger_type" class="form-control" onchange="showTriggerParams()">
                <option value="cron">Cron</option>
                <option value="interval">Interval</option>
                <option value="date">Date</option>
            </select>
        </div>
        
        <div id="cron-params" class="form-group">
            <label for="crontab">Crontab Expression:</label>
            <input type="text" id="crontab" name="crontab" class="form-control" placeholder="*/5 * * * *">
        </div>
        
        <div id="interval-params" class="form-group" style="display: none;">
            <label for="seconds">Interval (seconds):</label>
            <input type="number" id="seconds" name="seconds" class="form-control" value="60">
        </div>
        
        <div id="date-params" class="form-group" style="display: none;">
            <label for="run_date">Run Date:</label>
            <input type="datetime-local" id="run_date" name="run_date" class="form-control">
        </div>
        
        <div class="actions">
            <button type="submit" class="btn">Schedule Pipeline</button>
        </div>
    </form>
    
    <script>
        function showTriggerParams() {
            const triggerType = document.getElementById('trigger_type').value;
            document.getElementById('cron-params').style.display = 'none';
            document.getElementById('interval-params').style.display = 'none';
            document.getElementById('date-params').style.display = 'none';
            
            if (triggerType === 'cron') {
                document.getElementById('cron-params').style.display = 'block';
            } else if (triggerType === 'interval') {
                document.getElementById('interval-params').style.display = 'block';
            } else if (triggerType === 'date') {
                document.getElementById('date-params').style.display = 'block';
            }
        }
    </script>
{% endblock %}
````

## File: src/flowerpower/web/templates/schedules.html
````html
{% extends "base.html" %}

{% block title %}Schedules - FlowerPower{% endblock %}

{% block content %}
    <h2>Schedules</h2>
    
    {% if schedules %}
        <ul>
            {% for schedule in schedules %}
                <li class="schedule-item">
                    <h4>{{ schedule.id }}</h4>
                    <p>Next run: {{ schedule.next_run }}</p>
                </li>
            {% endfor %}
        </ul>
    {% else %}
        <p>No schedules found.</p>
    {% endif %}
{% endblock %}
````

## File: docker/Caddyfile
````
{
	email user@example.com
}

codeserver.flowerpower.local {
	reverse_proxy codeserver:8443
}

minio.flowerpower.local {
	reverse_proxy minio:9001
}


hamilton-ui.flowerpower.local {
	reverse_proxy hamilton-ui-frontend:8242
}

dockge.flowerpower.local {
	reverse_proxy dockge:5001
}
````

## File: examples/apscheduler/hello-world/conf/pipelines/hello_world.yml
````yaml
adapter:
  hamilton_tracker:
    capture_data_statistics: true
    dag_name: null
    max_dict_length_capture: 10
    max_list_length_capture: 50
    project_id: null
    tags: {}
  mlflow:
    experiment_description: null
    experiment_name: null
    experiment_tags: {}
    run_description: null
    run_id: null
    run_name: null
    run_tags: {}
params: 
  avg_x_wk_spend:
    rolling: 3
  spend_zero_mean:
    offset: 0
run:
  cache: false
  config: 
    range: 10_000
  executor:
    max_workers: 40
    num_cpus: 8
    type: threadpool
  final_vars:
    - spend
    - signups
    - avg_x_wk_spend
    - spend_per_signup
    - spend_zero_mean_unit_variance
  inputs: {}
  log_level: null
  with_adapter:
    future: false
    mlflow: false
    opentelemetry: false
    progressbar: false
    ray: false
    tracker: false
schedule:
  cron: "* * * * *"
  interval: null
  date: null
````

## File: examples/apscheduler/hello-world/conf/pipelines/test_mqtt.yml
````yaml
adapter:
  hamilton_tracker:
    capture_data_statistics: true
    dag_name: null
    max_dict_length_capture: 10
    max_list_length_capture: 50
    project_id: null
    tags: {}
  mlflow:
    experiment_description: null
    experiment_name: null
    experiment_tags: {}
    run_description: null
    run_id: null
    run_name: null
    run_tags: {}
params: {}
run:
  cache: false
  config: {}
  executor:
    max_workers: 40
    num_cpus: 8
    type: threadpool
  final_vars: []
  inputs: {}
  log_level: null
  with_adapter:
    future: false
    mlflow: false
    opentelemetry: false
    progressbar: false
    ray: false
    tracker: false
schedule:
  cron: null
  date: null
  interval: null
````

## File: examples/apscheduler/hello-world/conf/project.yml
````yaml
name: apscheduler
job_queue:
  type: apscheduler
  backend:
    data_store:
      type: postgresql
      uri: null
      username: postgres
      password: null
      host: localhost
      port: 5432
      database: null
      ssl: false
      cert_file: null
      key_file: null
      ca_file: null
      verify_ssl: false
      schema: flowerpower
    event_broker:
      type: postgresql
      uri: null
      username: postgres
      password: null
      host: localhost
      port: 5432
      database: null
      ssl: false
      cert_file: null
      key_file: null
      ca_file: null
      verify_ssl: false
      from_ds_sqla: true
    cleanup_interval: 300
    max_concurrent_jobs: 10
    default_job_executor: threadpool
    num_workers: 50
adapter:
  hamilton_tracker:
    username: null
    api_url: http://localhost:8241
    ui_url: http://localhost:8242
    api_key: null
    verify: false
  mlflow:
    tracking_uri: null
    registry_uri: null
    artifact_location: null
  ray:
    ray_init_config: null
    shutdown_ray_on_completion: false
  opentelemetry:
    host: localhost
    port: 6831
````

## File: examples/hello-world/conf/pipelines/test_mqtt.yml
````yaml
adapter:
  hamilton_tracker:
    capture_data_statistics: true
    dag_name: null
    max_dict_length_capture: 10
    max_list_length_capture: 50
    project_id: null
    tags: {}
  mlflow:
    experiment_description: null
    experiment_name: null
    experiment_tags: {}
    run_description: null
    run_id: null
    run_name: null
    run_tags: {}
params: {}
run:
  cache: false
  config: {}
  executor:
    max_workers: 40
    num_cpus: 8
    type: threadpool
  final_vars: []
  inputs: {}
  log_level: null
  with_adapter:
    future: false
    mlflow: false
    opentelemetry: false
    progressbar: false
    ray: false
    tracker: false
schedule:
  cron: null
  date: null
  interval: null
````

## File: examples/rq/hello-world/conf/pipelines/hello_world.yml
````yaml
adapter:
  hamilton_tracker:
    capture_data_statistics: true
    dag_name: null
    max_dict_length_capture: 10
    max_list_length_capture: 50
    project_id: null
    tags: {}
  mlflow:
    experiment_description: null
    experiment_name: null
    experiment_tags: {}
    run_description: null
    run_id: null
    run_name: null
    run_tags: {}
params: 
  avg_x_wk_spend:
    rolling: 3
  spend_zero_mean:
    offset: 0
run:
  cache: false
  config: 
    range: 10_000
  executor:
    max_workers: 40
    num_cpus: 8
    type: threadpool
  final_vars:
    - spend
    - signups
    - avg_x_wk_spend
    - spend_per_signup
    - spend_zero_mean_unit_variance
  inputs: {}
  log_level: null
  with_adapter:
    future: false
    mlflow: false
    opentelemetry: false
    progressbar: false
    ray: false
    tracker: false
schedule:
  cron: "* * * * *"
  interval: null
  date: null
````

## File: examples/rq/hello-world/conf/pipelines/test_mqtt.yml
````yaml
adapter:
  hamilton_tracker:
    capture_data_statistics: true
    dag_name: null
    max_dict_length_capture: 10
    max_list_length_capture: 50
    project_id: null
    tags: {}
  mlflow:
    experiment_description: null
    experiment_name: null
    experiment_tags: {}
    run_description: null
    run_id: null
    run_name: null
    run_tags: {}
params: {}
run:
  cache: false
  config: {}
  executor:
    max_workers: 40
    num_cpus: 8
    type: threadpool
  final_vars: []
  inputs: {}
  log_level: null
  with_adapter:
    future: false
    mlflow: false
    opentelemetry: false
    progressbar: false
    ray: false
    tracker: false
schedule:
  cron: null
  date: null
  interval: null
````

## File: src/flowerpower/cfg/project/job_queue.py
````python
class JobQueueBackendConfig(BaseConfig)
⋮----
"""
    Job Queue backend configuration for FlowerPower.
    Inherits from BaseConfig and adapts Redis logic.
    """
⋮----
type: str | None = msgspec.field(default=None)
uri: str | None = msgspec.field(default=None)
username: str | None = msgspec.field(default=None)
password: str | None = msgspec.field(default=None)
host: str | None = msgspec.field(default=None)
port: int | None = msgspec.field(default=None)
database: int | None = msgspec.field(default=None)
ssl: bool = msgspec.field(default=False)
cert_file: str | None = msgspec.field(default=None)
key_file: str | None = msgspec.field(default=None)
ca_file: str | None = msgspec.field(default=None)
verify_ssl: bool = msgspec.field(default=False)
⋮----
class APSDataStoreConfig(JobQueueBackendConfig)
⋮----
type: str = msgspec.field(default=settings.APS_BACKEND_DS)
host: str = msgspec.field(
port: int = msgspec.field(
schema: str | None = msgspec.field(default=settings.APS_SCHEMA_DS)
username: str = msgspec.field(
⋮----
class APSEventBrokerConfig(JobQueueBackendConfig)
⋮----
type: str = msgspec.field(default=settings.APS_BACKEND_EB)
⋮----
from_ds_sqla: bool = msgspec.field(
⋮----
class APSBackendConfig(BaseConfig)
⋮----
data_store: APSDataStoreConfig = msgspec.field(default_factory=APSDataStoreConfig)
event_broker: APSEventBrokerConfig = msgspec.field(
cleanup_interval: int | float | dt.timedelta = msgspec.field(
⋮----
)  # int in secods
max_concurrent_jobs: int = msgspec.field(default=settings.APS_MAX_CONCURRENT_JOBS)
default_job_executor: str | None = msgspec.field(default=settings.EXECUTOR)
num_workers: int | None = msgspec.field(default=settings.APS_NUM_WORKERS)
⋮----
class RQBackendConfig(JobQueueBackendConfig)
⋮----
type: str = msgspec.field(default="redis")
⋮----
database: int = msgspec.field(
queues: str | list[str] = msgspec.field(default_factory=lambda: settings.RQ_QUEUES)
num_workers: int = msgspec.field(default=settings.RQ_NUM_WORKERS)  # int in secods
⋮----
class HueyBackendConfig(JobQueueBackendConfig)
⋮----
class JobQueueConfig(BaseConfig)
⋮----
type: str | None = msgspec.field(default="rq")
backend: dict | None = msgspec.field(default=None)
⋮----
def __post_init__(self)
⋮----
def update_type(self, type: str)
````

## File: src/flowerpower/job_queue/apscheduler/manager.py
````python
"""
APScheduler implementation for FlowerPower scheduler.

This module implements the scheduler interfaces using APScheduler as the backend.
"""
⋮----
# Check if APScheduler is available
⋮----
# Patch pickle if needed
⋮----
class APSManager(BaseJobQueueManager)
⋮----
"""Implementation of BaseScheduler using APScheduler.

    This worker class uses APScheduler 4.0+ as the backend to schedule and manage jobs.
    It supports different job executors including async, thread pool, and process pool.

    Typical usage:
        ```python
        worker = APSManager(name="my_scheduler")
        worker.start_worker(background=True)

        # Add a job
        def my_job(x: int) -> int:
            return x * 2

        job_id = worker.add_job(my_job, func_args=(10,))
        ```
    """
⋮----
"""Initialize the APScheduler backend.

        Args:
            name: Name of the scheduler instance. Used for identification in logs and data stores.
            base_dir: Base directory for the FlowerPower project. Used for finding configuration files.
            backend: APSBackend instance with data store and event broker configurations,
                or a dictionary with configuration parameters.
            storage_options: Options for configuring file system storage access.
                Example: {"mode": "async", "root": "/tmp"}
            fs: Custom filesystem implementation for storage operations.
            log_level: Logging level to use for this worker instance.
                Example: "DEBUG", "INFO", "WARNING", etc.

        Raises:
            RuntimeError: If backend setup fails due to missing or invalid configurations.
            ImportError: If required dependencies are not installed.

        Example:
            ```python
            # Basic initialization
            worker = APSManager(name="my_scheduler")

            # With custom backend and logging

            # Create a custom backend configuration using dictionaries for data store and event broker
            backend_config = {
                "data_store": {"type": "postgresql", "uri": "postgresql+asyncpg://user:pass@localhost/db"},
                "event_broker": {"type": "redis", "uri": "redis://localhost:6379/0"}
            }

            # Create a custom backend configuration using APSBackend, APSDataStore, and APSEventBroker classes
            from flowerpower.worker.aps import APSBackend, APSDataStore, APSEventBroker
            data_store = APSDataStore(
                type="postgresql",
                uri="postgresql+asyncpg://user:pass@localhost/db"
            )
            event_broker = APSEventBroker(
                from_ds_sqla=True
            )
            backend_config = APSBackend(
                data_store=data_store,
                event_broker=event_broker
            )

            worker = APSManager(
                name="custom_scheduler",
                backend=backend_config,
                log_level="DEBUG"
            )
            ```
        """
⋮----
# Set up job executors
⋮----
def _setup_backend(self) -> None
⋮----
"""
        Set up the data store and SQLAlchemy engine for the scheduler.

        This method initializes the data store and SQLAlchemy engine using configuration
        values. It validates configuration, handles errors, and logs the setup process.

        Raises:
            RuntimeError: If the data store setup fails due to misconfiguration or connection errors.
        """
⋮----
data_store = APSDataStore(**self._backend["data_store"])
⋮----
event_broker = APSEventBroker.from_ds_sqla(
⋮----
event_broker = APSEventBroker(**self._backend["event_broker"])
⋮----
data_store = APSDataStore(**self.cfg.backend.data_store.to_dict())
⋮----
event_broker = APSEventBroker(
⋮----
"""Start the APScheduler worker process.

        This method initializes and starts the worker process that executes scheduled jobs.
        The worker can be started in foreground (blocking) or background mode.

        Args:
            background: If True, runs the worker in a non-blocking background mode.
                If False, runs in the current process and blocks until stopped.
            num_workers: Number of worker processes for the executor pools.
                If None, uses the value from config or defaults to CPU count.

        Raises:
            RuntimeError: If worker fails to start or if multiprocessing setup fails.

        Example:
            ```python
            # Start worker in background with 4 processes
            worker.start_worker(background=True, num_workers=4)

            # Start worker in foreground (blocking)
            worker.start_worker(background=False)

            # Use as a context manager
            with worker.start_worker(background=False):
                # Do some work
                pass
            ```
        """
⋮----
# Allow configuration override for pool sizes
⋮----
num_workers = getattr(self.cfg.backend, "num_workers", None)
⋮----
num_workers = multiprocessing.cpu_count()
⋮----
# Adjust thread and process pool executor sizes
⋮----
threadpool_size = getattr(
⋮----
def stop_worker(self) -> None
⋮----
"""Stop the APScheduler worker process.

        This method stops the worker process and cleans up resources.
        It should be called before program exit to ensure proper cleanup.

        Raises:
            RuntimeError: If worker fails to stop cleanly.

        Example:
            ```python
            try:
                worker.start_worker(background=True)
                # ... do work ...
            finally:
                worker.stop_worker()
            ```
        """
⋮----
"""
        Start a pool of worker processes to handle jobs in parallel.

        APScheduler 4.0 already handles concurrency internally through its executors,
        so this method simply starts a single worker with the appropriate configuration.

        Args:
            num_workers: Number of worker processes (affects executor pool sizes)
            background: Whether to run in background
        """
⋮----
# Start a single worker which will use the configured executors
⋮----
def stop_worker_pool(self) -> None
⋮----
"""
        Stop the worker pool.

        Since APScheduler manages concurrency internally, this just stops the worker.
        """
⋮----
## Jobs
⋮----
"""Add a job for immediate or scheduled execution.

        This method adds a job to the scheduler. The job can be executed immediately
        or scheduled for later execution using run_at or run_in parameters.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            result_ttl: Time to live for the job result, as seconds or timedelta.
                After this time, the result may be removed from storage.
            run_at: Schedule the job to run at a specific datetime.
                Takes precedence over run_in if both are specified.
            run_in: Schedule the job to run after a delay (in seconds).
                Only used if run_at is not specified.
            job_executor: Name of the executor to run the job ("async", "threadpool",
                or "processpool"). If None, uses the default from config.

        Returns:
            str: Unique identifier for the job.

        Raises:
            ValueError: If the function is not serializable or arguments are invalid.
            RuntimeError: If the job cannot be added to the scheduler.

        Note:
            When using run_at or run_in, the job results will not be stored in the data store.

        Example:
            ```python
            # Add immediate job
            def my_task(x: int, y: int) -> int:
                return x + y

            job_id = worker.add_job(
                my_task,
                func_args=(1, 2),
                result_ttl=3600  # Keep result for 1 hour
            )

            # Schedule job for later
            tomorrow = dt.datetime.now() + dt.timedelta(days=1)
            job_id = worker.add_job(
                my_task,
                func_kwargs={"x": 1, "y": 2},
                run_at=tomorrow
            )

            # Run after delay
            job_id = worker.add_job(
                my_task,
                func_args=(1, 2),
                run_in=3600  # Run in 1 hour
            )
            ```
        """
job_executor = job_executor or self.cfg.backend.default_job_executor
⋮----
# Convert result_expiration_time to datetime.timedelta if it's not already
⋮----
result_ttl = dt.timedelta(seconds=result_ttl)
⋮----
run_at = (
run_in = duration_parser.parse(run_in) if isinstance(run_in, str) else run_in
⋮----
run_at = dt.datetime.now() + dt.timedelta(seconds=run_in)
⋮----
job_id = self.add_schedule(
⋮----
job_id = self._worker.add_job(
⋮----
"""Run a job immediately and wait for its result.

        This method executes the job synchronously and returns its result.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            job_executor: Name of the executor to run the job ("async", "threadpool",
                or "processpool"). If None, uses the default from config.

        Returns:
            Any: The result returned by the executed function.

        Raises:
            Exception: Any exception raised by the executed function.

        Example:
            ```python
            def add(x: int, y: int) -> int:
                return x + y

            result = worker.run_job(add, func_args=(1, 2))
            assert result == 3
            ```
        """
⋮----
def get_jobs(self) -> list[Job]
⋮----
"""Get all jobs from the scheduler.

        Returns:
            list[Job]: List of all jobs in the scheduler, including pending,
                running, and completed jobs.

        Example:
            ```python
            jobs = worker.get_jobs()
            for job in jobs:
                print(f"Job {job.id}: {job.status}")
            ```
        """
⋮----
def get_job(self, job_id: str | UUID) -> Job | None
⋮----
"""Get a specific job by its ID.

        Args:
            job_id: Unique identifier of the job, as string or UUID.

        Returns:
            Job | None: The job object if found, None otherwise.

        Example:
            ```python
            # Get job using string ID
            job = worker.get_job("550e8400-e29b-41d4-a716-446655440000")

            # Get job using UUID
            from uuid import UUID
            job = worker.get_job(UUID("550e8400-e29b-41d4-a716-446655440000"))
            ```
        """
jobs = self._worker.get_jobs()
⋮----
job_id = UUID(job_id)
⋮----
def get_job_result(self, job_id: str | UUID, wait: bool = True) -> Any
⋮----
"""Get the result of a specific job.

        Args:
            job_id: Unique identifier of the job, as string or UUID.
            wait: If True, waits for the job to complete before returning.
                If False, returns None if the job is not finished.

        Returns:
            Any: The result of the job if available, None if the job is not
                finished and wait=False.

        Raises:
            ValueError: If the job ID is invalid.
            TimeoutError: If the job takes too long to complete (when waiting).

        Example:
            ```python
            # Wait for result
            result = worker.get_job_result("550e8400-e29b-41d4-a716-446655440000")

            # Check result without waiting
            result = worker.get_job_result(
                "550e8400-e29b-41d4-a716-446655440000",
                wait=False
            )
            if result is None:
                print("Job still running")
            ```
        """
⋮----
def cancel_job(self, job_id: str | UUID) -> bool
⋮----
"""Cancel a running or pending job.

        Note:
            Not currently implemented for APScheduler backend. Jobs must be removed
            manually from the data store.

        Args:
            job_id: Unique identifier of the job to cancel, as string or UUID.

        Returns:
            bool: Always returns False as this operation is not implemented.

        Example:
            ```python
            # This operation is not supported
            success = worker.cancel_job("job-123")
            assert not success
            ```
        """
⋮----
def delete_job(self, job_id: str | UUID) -> bool
⋮----
"""
        Delete a job and its results from storage.

        Note:
            Not currently implemented for APScheduler backend. Jobs must be removed
            manually from the data store.

        Args:
            job_id: Unique identifier of the job to delete, as string or UUID.

        Returns:
            bool: Always returns False as this operation is not implemented.

        Example:
            ```python
            # This operation is not supported
            success = worker.delete_job("job-123")
            assert not success
            ```
        """
⋮----
def cancel_all_jobs(self) -> None
⋮----
"""Cancel all running and pending jobs.

        Note:
            Not currently implemented for APScheduler backend. Jobs must be removed
            manually from the data store.

        Example:
            ```python
            # This operation is not supported
            worker.cancel_all_jobs()  # No effect
            ```
        """
⋮----
def delete_all_jobs(self) -> None
⋮----
"""
        Delete all jobs and their results from storage.

        Note:
            Not currently implemented for APScheduler backend. Jobs must be removed
            manually from the data store.

        Example:
            ```python
            # This operation is not supported
            worker.delete_all_jobs()  # No effect
            ```
        """
⋮----
@property
    def jobs(self) -> list[Job]
⋮----
"""Get all jobs from the scheduler.

        Returns:
            list[Job]: List of all job objects in the scheduler.

        Example:
            ```python
            all_jobs = worker.jobs
            print(f"Total jobs: {len(all_jobs)}")
            for job in all_jobs:
                print(f"Job {job.id}: {job.status}")
            ```
        """
⋮----
@property
    def job_ids(self) -> list[str]
⋮----
"""Get all job IDs from the scheduler.

        Returns:
            list[str]: List of unique identifiers for all jobs.

        Example:
            ```python
            ids = worker.job_ids
            print(f"Job IDs: {', '.join(ids)}")
            ```
        """
⋮----
## Schedules
⋮----
"""Schedule a job for repeated or one-time execution.

        This method adds a scheduled job to the scheduler. The schedule can be defined
        using cron expressions, intervals, or specific dates.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            cron: Cron expression for scheduling. Can be a string (e.g. "* * * * *")
                or a dict with cron parameters. Only one of cron, interval, or date
                should be specified.
            interval: Interval for recurring execution in seconds, or a dict with
                interval parameters. Only one of cron, interval, or date should
                be specified.
            date: Specific datetime for one-time execution. Only one of cron,
                interval, or date should be specified.
            schedule_id: Optional unique identifier for the schedule.
                If None, a UUID will be generated.
            job_executor: Name of the executor to run the job ("async", "threadpool",
                or "processpool"). If None, uses the default from config.
            **schedule_kwargs: Additional scheduling parameters:
                - coalesce: CoalescePolicy = CoalescePolicy.latest
                - misfire_grace_time: float | timedelta | None = None
                - max_jitter: float | timedelta | None = None
                - max_running_jobs: int | None = None
                - conflict_policy: ConflictPolicy = ConflictPolicy.do_nothing
                - paused: bool = False

        Returns:
            str: Unique identifier for the schedule.

        Raises:
            ValueError: If no trigger type is specified or if multiple triggers
                are specified.
            RuntimeError: If the schedule cannot be added to the scheduler.

        Example:
            ```python
            def my_task(msg: str) -> None:
                print(f"Running task: {msg}")

            # Using cron expression (run every minute)
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Cron job"},
                cron="* * * * *"
            )

            # Using cron dict
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Cron job"},
                cron={
                    "minute": "*/15",  # Every 15 minutes
                    "hour": "9-17"     # During business hours
                }
            )

            # Using interval (every 5 minutes)
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Interval job"},
                interval=300  # 5 minutes in seconds
            )

            # Using interval dict
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Interval job"},
                interval={
                    "hours": 1,
                    "minutes": 30
                }
            )

            # One-time future execution
            import datetime as dt
            future_date = dt.datetime.now() + dt.timedelta(days=1)
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "One-time job"},
                date=future_date
            )

            # With additional options
            from apscheduler import CoalescePolicy
            schedule_id = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Advanced job"},
                interval=300,
                coalesce=CoalescePolicy.latest,
                max_jitter=dt.timedelta(seconds=30)
            )
            ```
        """
⋮----
trigger_instance = APSTrigger("cron")
⋮----
cron = {"crontab": cron}
trigger = trigger_instance.get_trigger_instance(**cron)
⋮----
trigger_instance = APSTrigger("interval")
⋮----
interval = {"seconds": int(interval)}
trigger = trigger_instance.get_trigger_instance(**interval)
⋮----
trigger_instance = APSTrigger("date")
trigger = trigger_instance.get_trigger_instance(run_time=date)
⋮----
schedule_id = self._worker.add_schedule(
⋮----
def get_schedules(self, as_dict: bool = False) -> list[Any]
⋮----
"""Get all schedules from the scheduler.

        Args:
            as_dict: If True, returns schedules as dictionaries instead of
                Schedule objects.

        Returns:
            list[Any]: List of all schedules, either as Schedule objects or
                dictionaries depending on as_dict parameter.

        Example:
            ```python
            # Get schedule objects
            schedules = worker.get_schedules()
            for schedule in schedules:
                print(f"Schedule {schedule.id}: Next run at {schedule.next_run_time}")

            # Get as dictionaries
            schedules = worker.get_schedules(as_dict=True)
            for schedule in schedules:
                print(f"Schedule {schedule['id']}: {schedule['trigger']}")
            ```
        """
⋮----
def get_schedule(self, schedule_id: str) -> Any
⋮----
"""Get a specific schedule by its ID.

        Args:
            schedule_id: Unique identifier of the schedule.

        Returns:
            Any: The schedule object if found, None otherwise.

        Example:
            ```python
            schedule = worker.get_schedule("my-daily-job")
            if schedule:
                print(f"Next run at: {schedule.next_run_time}")
            else:
                print("Schedule not found")
            ```
        """
⋮----
def cancel_schedule(self, schedule_id: str) -> bool
⋮----
"""Cancel a schedule.

        This method removes the schedule from the scheduler. This is equivalent
        to delete_schedule and stops any future executions of the schedule.

        Args:
            schedule_id: Unique identifier of the schedule to cancel.

        Returns:
            bool: True if the schedule was successfully canceled,
                False if the schedule was not found.

        Example:
            ```python
            if worker.cancel_schedule("my-daily-job"):
                print("Schedule canceled successfully")
            else:
                print("Schedule not found")
            ```
        """
⋮----
def delete_schedule(self, schedule_id: str) -> bool
⋮----
"""Remove a schedule.

        This method removes the schedule from the scheduler. This is equivalent
        to cancel_schedule and stops any future executions of the schedule.

        Args:
            schedule_id: Unique identifier of the schedule to remove.

        Returns:
            bool: True if the schedule was successfully removed,
                False if the schedule was not found.

        Raises:
            RuntimeError: If removal fails due to data store errors.

        Example:
            ```python
            try:
                if worker.delete_schedule("my-daily-job"):
                    print("Schedule deleted successfully")
                else:
                    print("Schedule not found")
            except RuntimeError as e:
                print(f"Failed to delete schedule: {e}")
            ```
        """
⋮----
def cancel_all_schedules(self) -> None
⋮----
"""Cancel all schedules in the scheduler.

        This method removes all schedules from the scheduler, stopping all future
        executions. This operation cannot be undone.

        Example:
            ```python
            # Cancel all schedules
            worker.cancel_all_schedules()
            assert len(worker.schedules) == 0
            ```
        """
⋮----
def delete_all_schedules(self) -> None
⋮----
"""
        Delete all schedules from the scheduler.

        This method removes all schedules from the scheduler, stopping all future
        executions. This operation cannot be undone.

        Example:
            ```python
            # Delete all schedules
            worker.delete_all_schedules()
            assert len(worker.schedules) == 0
            ```
        """
⋮----
@property
    def schedules(self) -> list[Any]
⋮----
"""Get all schedules from the scheduler.

        Returns:
            list[Any]: List of all schedule objects in the scheduler.

        Example:
            ```python
            schedules = worker.schedules
            print(f"Total schedules: {len(schedules)}")
            ```
        """
⋮----
@property
    def schedule_ids(self) -> list[str]
⋮----
"""Get all schedule IDs from the scheduler.

        Returns:
            list[str]: List of unique identifiers for all schedules.

        Example:
            ```python
            ids = worker.schedule_ids
            print(f"Schedule IDs: {', '.join(ids)}")
            ```
        """
⋮----
def pause_schedule(self, schedule_id: str) -> bool
⋮----
"""Pause a schedule temporarily.

        This method pauses the schedule without removing it. The schedule can be
        resumed later using resume_schedule.

        Args:
            schedule_id: Unique identifier of the schedule to pause.

        Returns:
            bool: True if the schedule was successfully paused,
                False if the schedule was not found.

        Example:
            ```python
            # Pause a schedule temporarily
            if worker.pause_schedule("daily-backup"):
                print("Schedule paused")
            ```
        """
⋮----
def resume_schedule(self, schedule_id: str) -> bool
⋮----
"""Resume a paused schedule.

        Args:
            schedule_id: Unique identifier of the schedule to resume.

        Returns:
            bool: True if the schedule was successfully resumed,
                False if the schedule was not found.

        Example:
            ```python
            # Resume a paused schedule
            if worker.resume_schedule("daily-backup"):
                print("Schedule resumed")
            ```
        """
⋮----
def pause_all_schedules(self) -> None
⋮----
"""Pause all schedules in the scheduler.

        This method pauses all schedules without removing them. They can be
        resumed using resume_all_schedules.

        Example:
            ```python
            # Pause all schedules temporarily
            worker.pause_all_schedules()
            ```
        """
⋮----
def resume_all_schedules(self) -> None
⋮----
"""Resume all paused schedules.

        This method resumes all paused schedules in the scheduler.

        Example:
            ```python
            # Resume all paused schedules
            worker.resume_all_schedules()
            ```
        """
⋮----
def show_schedules(self) -> None
⋮----
"""Display all schedules in a user-friendly format.

        This method prints a formatted view of all schedules including their
        status, next run time, and other relevant information.

        Example:
            ```python
            # Show all schedules in a readable format
            worker.show_schedules()
            ```
        """
⋮----
def show_jobs(self) -> None
⋮----
"""Display all jobs in a user-friendly format.

        This method prints a formatted view of all jobs including their
        status, result, and other relevant information.

        Example:
            ```python
            # Show all jobs in a readable format
            worker.show_jobs()
            ```
        """
````

## File: src/flowerpower/job_queue/apscheduler/utils.py
````python
def humanize_crontab(minute, hour, day, month, day_of_week)
⋮----
days = {
months = {
⋮----
def get_day_name(day_input)
⋮----
day_input = str(day_input).lower().strip()
⋮----
parts = []
⋮----
def format_trigger(trigger)
⋮----
trigger_type = trigger.__class__.__name__
⋮----
cron_parts = dict(
cron_parts = {k: v.strip("'") for k, v in cron_parts.items()}
crontab = f"{cron_parts['minute']} {cron_parts['hour']} {cron_parts['day']} {cron_parts['month']} {cron_parts['day_of_week']}"
human_readable = humanize_crontab(
⋮----
def display_schedules(schedules: List)
⋮----
console = Console()
total_width = console.width - 10
⋮----
width_ratios = {
⋮----
widths = {k: max(10, int(total_width * ratio)) for k, ratio in width_ratios.items()}
⋮----
table = Table(
⋮----
def display_tasks(tasks)
⋮----
table = Table(title="Tasks")
⋮----
widths = {"id": 50, "executor": 15, "max_jobs": 15, "misfire": 20}
⋮----
def display_jobs(jobs)
⋮----
table = Table(title="Jobs")
⋮----
widths = {
⋮----
status = "Running" if job.acquired_by else "Pending"
````

## File: src/flowerpower/job_queue/rq/manager.py
````python
"""
RQSchedulerBackend implementation for FlowerPower using RQ and rq-scheduler.

This module implements the scheduler backend using RQ (Redis Queue) and rq-scheduler.
"""
⋮----
# Check if the start method has already been set to avoid errors
⋮----
# Handle cases where the context might already be started
⋮----
class RQManager(BaseJobQueueManager)
⋮----
"""Implementation of BaseScheduler using Redis Queue (RQ) and rq-scheduler.

    This worker class uses RQ and rq-scheduler as the backend to manage jobs and schedules.
    It supports multiple queues, background workers, and job scheduling capabilities.

    Typical usage:
        ```python
        worker = RQManager(name="my_rq_worker")
        worker.start_worker(background=True)

        # Add a job
        def my_job(x: int) -> int:
            return x * 2

        job_id = worker.add_job(my_job, func_args=(10,))
        ```
    """
⋮----
"""Initialize the RQ scheduler backend.

        Args:
            name: Name of the scheduler instance. Used for identification in logs
                and queue names.
            base_dir: Base directory for the FlowerPower project. Used for finding
                configuration files.
            backend: RQBackend instance for Redis connection configuration.
                If None, configuration is loaded from project settings.
            storage_options: Options for configuring file system storage access.
                Example: {"mode": "async", "root": "/tmp"}
            fs: Custom filesystem implementation for storage operations.
            log_level: Logging level to use for this worker instance.
                Example: "DEBUG", "INFO", "WARNING", etc.

        Raises:
            RuntimeError: If backend setup fails due to Redis connection issues
                or missing configurations.
            ImportError: If required dependencies are not installed.

        Example:
            ```python
            # Basic initialization
            worker = RQManager(name="my_worker")

            # With custom backend and logging
            backend = RQBackend(
                uri="redis://localhost:6379/0",
                queues=["high", "default", "low"]
            )
            worker = RQManager(
                name="custom_worker",
                backend=backend,
                log_level="DEBUG"
            )
            ```
        """
⋮----
redis_conn = self._backend.client
⋮----
self._queue_names = self._backend.queues  # [:-1]
⋮----
queue = Queue(name=queue_name, connection=redis_conn)
⋮----
def _setup_backend(self) -> None
⋮----
"""Set up the Redis backend for the scheduler.

        This internal method initializes the Redis connection and queues based on
        project configuration. It validates configuration, handles errors, and logs
        the setup process.

        Raises:
            RuntimeError: If Redis connection fails or configuration is invalid.
        """
backend_cfg = getattr(self.cfg, "backend", None)
⋮----
"""Start a worker process for processing jobs from the queues.

        Args:
            background: If True, runs the worker in a non-blocking background mode.
                If False, runs in the current process and blocks until stopped.
            queue_names: List of queue names to process. If None, processes all
                queues defined in the backend configuration.
            with_scheduler: Whether to include the scheduler queue for processing
                scheduled jobs.
            **kwargs: Additional arguments passed to RQ's Worker class.
                Example: {"burst": True, "logging_level": "INFO", "job_monitoring_interval": 30}

        Raises:
            RuntimeError: If worker fails to start or if Redis connection fails.

        Example:
            ```python
            # Start worker in background processing all queues
            worker.start_worker(background=True)

            # Start worker for specific queues
            worker.start_worker(
                background=True,
                queue_names=["high", "default"],
                with_scheduler=False
            )

            # Start worker with custom settings
            worker.start_worker(
                background=True,
                max_jobs=100,
                job_monitoring_interval=30
            )
            ```
        """
⋮----
logging_level = kwargs.pop("logging_level", self._log_level)
burst = kwargs.pop("burst", False)
max_jobs = kwargs.pop("max_jobs", None)
# Determine which queues to process
⋮----
# Use all queues by default
queue_names = self._queue_names
queue_names_str = ", ".join(queue_names)
⋮----
# Filter to only include valid queue names
queue_names = [name for name in queue_names if name in self._queue_names]
⋮----
# Add the scheduler queue to the list of queues
⋮----
# Create a worker instance with queue names (not queue objects)
worker = Worker(queue_names, connection=self._backend.client, **kwargs)
⋮----
# We need to use a separate process rather than a thread because
# RQ's signal handler registration only works in the main thread
def run_worker_process(queue_names_arg)
⋮----
# Import RQ inside the process to avoid connection sharing issues
⋮----
# Create a fresh Redis connection in this process
redis_conn = Redis.from_url(self._backend.uri)
⋮----
# Create a worker instance with queue names
worker_proc = Worker(queue_names_arg, connection=redis_conn)
⋮----
# Disable the default signal handlers in RQ worker by patching
# the _install_signal_handlers method to do nothing
⋮----
# Work until terminated
⋮----
# Create and start the process
process = multiprocessing.Process(
# Don't use daemon=True to avoid the "daemonic processes are not allowed to have children" error
⋮----
# Start worker in the current process (blocking)
⋮----
def stop_worker(self) -> None
⋮----
"""Stop the worker process.

        This method stops the worker process if running in background mode and
        performs cleanup. It should be called before program exit.

        Example:
            ```python
            try:
                worker.start_worker(background=True)
                # ... do work ...
            finally:
                worker.stop_worker()
            ```
        """
⋮----
"""Start a pool of worker processes to handle jobs in parallel.

        This implementation uses RQ's WorkerPool class which provides robust worker
        management with proper monitoring and graceful shutdown.

        Args:
            num_workers: Number of worker processes to start. If None, uses CPU
                count or configuration value.
            background: If True, runs the worker pool in background mode.
                If False, runs in the current process and blocks.
            queue_names: List of queue names to process. If None, processes all
                queues defined in the backend configuration.
            with_scheduler: Whether to include the scheduler queue for processing
                scheduled jobs.
            **kwargs: Additional arguments passed to RQ's WorkerPool class.
                Example: {"max_jobs": 100, "job_monitoring_interval": 30}

        Raises:
            RuntimeError: If worker pool fails to start or Redis connection fails.

        Example:
            ```python
            # Start pool with default settings
            worker.start_worker_pool(num_workers=4, background=True)

            # Start pool for specific queues
            worker.start_worker_pool(
                num_workers=4,
                background=True,
                queue_names=["high", "default"],
                with_scheduler=False
            )

            # Start pool with custom settings
            worker.start_worker_pool(
                num_workers=4,
                background=True,
                max_jobs=100,
                job_monitoring_interval=30
            )
            ```
        """
⋮----
backend = getattr(self.cfg, "rq_backend", None)
⋮----
num_workers = getattr(backend, "num_workers", None)
⋮----
num_workers = multiprocessing.cpu_count()
⋮----
queue_list = self._queue_names
queue_names_str = ", ".join(queue_list)
⋮----
queue_list = [name for name in queue_names if name in self._queue_names]
⋮----
# Initialize RQ's WorkerPool
worker_pool = WorkerPool(
# worker_pool.log = logger
⋮----
# Start the worker pool process using multiprocessing to avoid signal handler issues
def run_pool_process()
⋮----
# Start the worker pool in the current process (blocking)
⋮----
def stop_worker_pool(self) -> None
⋮----
"""Stop all worker processes in the pool.

        This method stops all worker processes in the pool and performs cleanup.
        It ensures a graceful shutdown of all workers.

        Example:
            ```python
            try:
                worker.start_worker_pool(num_workers=4, background=True)
                # ... do work ...
            finally:
                worker.stop_worker_pool()
            ```
        """
⋮----
# Terminate the worker pool process
⋮----
def start_scheduler(self, background: bool = False, interval: int = 60) -> None
⋮----
"""Start the RQ scheduler process.

        The scheduler process manages scheduled and recurring jobs. It must be
        running for scheduled jobs to execute.

        Args:
            background: If True, runs the scheduler in a non-blocking background mode.
                If False, runs in the current process and blocks.
            interval: How often to check for scheduled jobs, in seconds.

        Raises:
            RuntimeError: If scheduler fails to start or Redis connection fails.

        Example:
            ```python
            # Start scheduler in background checking every 30 seconds
            worker.start_scheduler(background=True, interval=30)

            # Start scheduler in foreground (blocking)
            worker.start_scheduler(background=False)
            ```
        """
# Create a scheduler instance with the queue name
⋮----
def run_scheduler()
⋮----
def stop_scheduler(self) -> None
⋮----
"""Stop the RQ scheduler process.

        This method stops the scheduler process if running in background mode
        and performs cleanup.

        Example:
            ```python
            try:
                worker.start_scheduler(background=True)
                # ... do work ...
            finally:
                worker.stop_scheduler()
            ```
        """
⋮----
## Jobs ###
⋮----
"""Add a job for immediate or scheduled execution.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            job_id: Optional unique identifier for the job. If None, a UUID is generated.
            result_ttl: Time to live for the job result, as seconds or timedelta.
                After this time, the result may be removed from Redis.
            ttl: Maximum time the job can exist in Redis, as seconds or timedelta.
                After this time, the job will be removed even if not complete.
            queue_name: Name of the queue to place the job in. If None, uses the
                first queue from configuration.
            run_at: Schedule the job to run at a specific datetime.
            run_in: Schedule the job to run after a delay.
            retry: Number of retries or retry configuration dictionary.
                Example dict: {"max": 3, "interval": 60}
            repeat: Number of repetitions or repeat configuration dictionary.
                Example dict: {"max": 5, "interval": 3600}
            meta: Additional metadata to store with the job.
            **job_kwargs: Additional arguments for RQ's Job class.

        Returns:
            Job: The created job instance.

        Raises:
            ValueError: If the function is not serializable or arguments are invalid.
            RuntimeError: If Redis connection fails.

        Example:
            ```python
            def my_task(x: int, y: int = 0) -> int:
                return x + y

            # Add immediate job
            job = worker.add_job(
                my_task,
                func_args=(1,),
                func_kwargs={"y": 2},
                result_ttl=3600  # Keep result for 1 hour
            )

            # Add scheduled job
            tomorrow = dt.datetime.now() + dt.timedelta(days=1)
            job = worker.add_job(
                my_task,
                func_args=(1, 2),
                run_at=tomorrow,
                queue_name="scheduled"
            )

            # Add job with retries
            job = worker.add_job(
                my_task,
                func_args=(1, 2),
                retry={"max": 3, "interval": 60}  # 3 retries, 1 minute apart
            )

            # Add repeating job
            job = worker.add_job(
                my_task,
                func_args=(1, 2),
                repeat={"max": 5, "interval": 3600}  # 5 times, hourly
            )
            ```
        """
job_id = job_id or str(uuid.uuid4())
⋮----
result_ttl = dt.timedelta(seconds=result_ttl)
# args = args or ()
# kwargs = kwargs or {}
⋮----
queue_name = self._queue_names[0]
⋮----
# If repeat is an int, convert it to a Repeat instance
⋮----
repeat = Repeat(max=repeat)
⋮----
# If repeat is a dict, convert it to a Repeat instance
repeat = Repeat(**repeat)
⋮----
retry = Retry(max=retry)
⋮----
# If retry is a dict, convert it to a Retry instance
retry = Retry(**retry)
⋮----
queue = self._queues[queue_name]
⋮----
# Schedule the job to run at a specific time
run_at = (
job = queue.enqueue_at(
⋮----
# Schedule the job to run after a delay
run_in = (
⋮----
job = queue.enqueue_in(
⋮----
# Enqueue the job for immediate execution
job = queue.enqueue(
⋮----
"""Run a job immediately and return its result.

        This method is a wrapper around add_job that waits for the job to complete
        and returns its result.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            job_id: Optional unique identifier for the job.
            result_ttl: Time to live for the job result.
            ttl: Maximum time the job can exist.
            queue_name: Name of the queue to use.
            retry: Number of retries or retry configuration.
            repeat: Number of repetitions or repeat configuration.
            meta: Additional metadata to store with the job.
            **job_kwargs: Additional arguments for RQ's Job class.

        Returns:
            Any: The result returned by the executed function.

        Raises:
            Exception: Any exception raised by the executed function.
            TimeoutError: If the job times out before completion.

        Example:
            ```python
            def add(x: int, y: int) -> int:
                return x + y

            # Run job and get result immediately
            result = worker.run_job(
                add,
                func_args=(1, 2),
                retry=3  # Retry up to 3 times on failure
            )
            assert result == 3
            ```
        """
job = self.add_job(
⋮----
def _get_job_queue_name(self, job: str | Job) -> str | None
⋮----
"""Get the queue name for a job.

        Args:
            job: Job ID or Job object.

        Returns:
            str | None: Name of the queue containing the job, or None if not found.
        """
job_id = job if isinstance(job, str) else job.id
⋮----
"""Get all jobs from specified queues.

        Args:
            queue_name: Optional queue name or list of queue names to get jobs from.
                If None, gets jobs from all queues.

        Returns:
            dict[str, list[Job]]: Dictionary mapping queue names to lists of jobs.

        Example:
            ```python
            # Get jobs from all queues
            jobs = worker.get_jobs()
            for queue_name, queue_jobs in jobs.items():
                print(f"Queue {queue_name}: {len(queue_jobs)} jobs")

            # Get jobs from specific queues
            jobs = worker.get_jobs(["high", "default"])
            ```
        """
⋮----
queue_name = self._queue_names
⋮----
queue_name = [queue_name]
jobs = {
⋮----
def get_job(self, job_id: str) -> Job | None
⋮----
"""Get a specific job by its ID.

        Args:
            job_id: Unique identifier of the job to retrieve.

        Returns:
            Job | None: The job object if found, None otherwise.

        Example:
            ```python
            job = worker.get_job("550e8400-e29b-41d4-a716-446655440000")
            if job:
                print(f"Job status: {job.get_status()}")
            ```
        """
queue_name = self._get_job_queue_name(job=job_id)
⋮----
job = self._queues[queue_name].fetch_job(job_id)
⋮----
def get_job_result(self, job: str | Job, delete_result: bool = False) -> Any
⋮----
"""Get the result of a completed job.

        Args:
            job: Job ID or Job object.
            delete_result: If True, deletes the job and its result after retrieval.

        Returns:
            Any: The result of the job if available.

        Example:
            ```python
            # Get result and keep the job
            result = worker.get_job_result("job-123")

            # Get result and clean up
            result = worker.get_job_result("job-123", delete_result=True)
            ```
        """
⋮----
job = self.get_job(job_id=job)
⋮----
def cancel_job(self, job: str | Job) -> bool
⋮----
"""
        Cancel a job in the queue.

        Args:
            job: Job ID or Job object

        Returns:
            bool: True if the job was canceled, False otherwise
        """
⋮----
def delete_job(self, job: str | Job, ttl: int = 0, **kwargs) -> bool
⋮----
"""
        Remove a job from the queue.

        Args:
            job: Job ID or Job object
            ttl: Optional time to live for the job (in seconds). 0 means no TTL.
                Remove the job immediately.
            **kwargs: Additional parameters for the job removal

        Returns:
            bool: True if the job was removed, False otherwise
        """
⋮----
job = self.get_job(job)
⋮----
def cancel_all_jobs(self, queue_name: str | None = None) -> None
⋮----
"""
        Cancel all jobs in a queue.

        Args:
            queue_name (str | None): Optional name of the queue to cancel jobs from.
                If None, cancels jobs from all queues.
        """
⋮----
def delete_all_jobs(self, queue_name: str | None = None, ttl: int = 0) -> None
⋮----
"""
        Remove all jobs from a queue.

        Args:
            queue_name (str | None): Optional name of the queue to remove jobs from.
                If None, removes jobs from all queues.
            ttl: Optional time to live for the job (in seconds). 0 means no TTL.
                Remove the job immediately.

        """
⋮----
@property
    def job_ids(self)
⋮----
"""Get all job IDs from all queues.

        Returns:
            dict[str, list[str]]: Dictionary mapping queue names to lists of job IDs.

        Example:
            ```python
            all_ids = worker.job_ids
            for queue_name, ids in all_ids.items():
                print(f"Queue {queue_name}: {len(ids)} jobs")
            ```
        """
job_ids = {}
⋮----
@property
    def jobs(self)
⋮----
"""Get all jobs from all queues.

        Returns:
            dict[str, list[Job]]: Dictionary mapping queue names to lists of jobs.

        Example:
            ```python
            all_jobs = worker.jobs
            for queue_name, queue_jobs in all_jobs.items():
                print(f"Queue {queue_name}: {len(queue_jobs)} jobs")
            ```
        """
jobs = {}
⋮----
### Schedules ###
⋮----
cron: str | None = None,  # Cron expression for scheduling
interval: int | None = None,  # Interval in seconds
date: dt.datetime | None = None,  # Date to run the job
⋮----
"""Schedule a job for repeated or one-time execution.

        Args:
            func: Function to execute. Must be importable from the worker process.
            func_args: Positional arguments to pass to the function.
            func_kwargs: Keyword arguments to pass to the function.
            cron: Cron expression for scheduling (e.g. "0 * * * *" for hourly).
            interval: Interval in seconds for recurring execution.
            date: Specific datetime for one-time execution.
            schedule_id: Optional unique identifier for the schedule.
            **schedule_kwargs: Additional scheduling parameters:
                - repeat: Number of repetitions (int or dict)
                - result_ttl: Time to live for results (float or timedelta)
                - ttl: Time to live for the schedule (float or timedelta)
                - use_local_time_zone: Whether to use local time (bool)
                - queue_name: Queue to use for the scheduled jobs

        Returns:
            Job: The scheduled job instance.

        Raises:
            ValueError: If no scheduling method specified or invalid cron expression.
            RuntimeError: If Redis connection fails.

        Example:
            ```python
            def my_task(msg: str) -> None:
                print(f"Task: {msg}")

            # Schedule with cron (every hour)
            job = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Hourly check"},
                cron="0 * * * *"
            )

            # Schedule with interval (every 5 minutes)
            job = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "Regular check"},
                interval=300
            )

            # Schedule for specific time
            tomorrow = dt.datetime.now() + dt.timedelta(days=1)
            job = worker.add_schedule(
                my_task,
                func_kwargs={"msg": "One-time task"},
                date=tomorrow
            )
            ```
        """
schedule_id = schedule_id or str(uuid.uuid4())
func_args = func_args or ()
func_kwargs = func_kwargs or {}
⋮----
# Use the specified scheduler or default to the first one
⋮----
scheduler = self._scheduler
⋮----
use_local_time_zone = schedule_kwargs.get("use_local_time_zone", True)
repeat = schedule_kwargs.get("repeat", None)
result_ttl = schedule_kwargs.get("result_ttl", None)
ttl = schedule_kwargs.get("ttl", None)
⋮----
schedule = scheduler.cron(
⋮----
repeat=repeat,  # Infinite by default
⋮----
schedule = scheduler.schedule(
⋮----
repeat=1,  # Infinite by default
⋮----
def _get_schedule_queue_name(self, schedule: str | Job) -> str | None
⋮----
"""Get the queue name for a schedule.

        Args:
            schedule: Schedule ID or Job object.

        Returns:
            str | None: Name of the scheduler queue.
        """
⋮----
"""Get all schedules from the scheduler.

        Args:
            until: Get schedules until this time.
            with_times: Include next run times in the results.
            offset: Number of schedules to skip.
            length: Maximum number of schedules to return.

        Returns:
            dict[str, list[Job]]: Dictionary mapping queue names to lists of schedules.

        Example:
            ```python
            # Get all schedules
            schedules = worker.get_schedules()

            # Get next 10 schedules with run times
            schedules = worker.get_schedules(
                with_times=True,
                length=10
            )
            ```
        """
schedules = list(
⋮----
def get_schedule(self, schedule_id: str) -> Job | None
⋮----
"""
        Get a schedule by its ID.

        Args:
            schedule_id: ID of the schedule

        Returns:
            Job | None: Schedule object if found, None otherwise
        """
schedule = self.get_job(job_id=schedule_id)
⋮----
def _get_schedule_results(self, schedule: str | Job) -> list[Result]
⋮----
"""Get all results from a schedule's execution history.

        Args:
            schedule: Schedule ID or Job object.

        Returns:
            list[Result]: List of all results from the schedule's executions.

        Raises:
            ValueError: If schedule not found.
        """
⋮----
schedule = self.get_schedule(schedule_id=schedule)
⋮----
"""Get the most recent result of a schedule.

        Args:
            schedule: Schedule ID or Job object.
            delete_result: If True, deletes the schedule and results after retrieval.

        Returns:
            Any: The most recent result of the schedule if available.

        Example:
            ```python
            # Get latest result
            result = worker.get_schedule_latest_result("schedule-123")

            # Get result and clean up
            result = worker.get_schedule_latest_result(
                "schedule-123",
                delete_result=True
            )
            ```
        """
result = self._get_schedule_result(schedule=schedule)[-1]
⋮----
"""Get specific results from a schedule's execution history.

        Args:
            schedule: Schedule ID or Job object.
            index: Which results to retrieve. Can be:
                - int: Specific index
                - list[str]: List of indices
                - slice: Range of indices
                - str: "all", "latest", or "earliest"

        Returns:
            list[Result]: List of requested results.

        Example:
            ```python
            # Get all results
            results = worker.get_schedule_result("schedule-123", "all")

            # Get latest result
            result = worker.get_schedule_result("schedule-123", "latest")

            # Get specific results
            results = worker.get_schedule_result("schedule-123", [0, 2, 4])

            # Get range of results
            results = worker.get_schedule_result("schedule-123", slice(0, 5))
            ```
        """
results = self._get_schedule_results(schedule=schedule)
⋮----
index = [int(i) for i in index.split(":")]
index = slice(index[0], index[1])
⋮----
def cancel_schedule(self, schedule: str | Job) -> bool
⋮----
"""Cancel a schedule.

        This method stops any future executions of the schedule without removing
        past results.

        Args:
            schedule: Schedule ID or Job object to cancel.

        Returns:
            bool: True if successfully canceled, False if schedule not found.

        Example:
            ```python
            # Cancel by ID
            worker.cancel_schedule("schedule-123")

            # Cancel using job object
            schedule = worker.get_schedule("schedule-123")
            if schedule:
                worker.cancel_schedule(schedule)
            ```
        """
⋮----
def cancel_all_schedules(self) -> None
⋮----
"""Cancel all schedules in the scheduler.

        This method stops all future executions of all schedules without removing
        past results.

        Example:
            ```python
            # Stop all scheduled jobs
            worker.cancel_all_schedules()
            ```
        """
⋮----
def delete_schedule(self, schedule: str | Job) -> bool
⋮----
"""Delete a schedule and optionally its results.

        This method removes the schedule and optionally its execution history
        from Redis.

        Args:
            schedule: Schedule ID or Job object to delete.

        Returns:
            bool: True if successfully deleted, False if schedule not found.

        Example:
            ```python
            # Delete schedule and its history
            worker.delete_schedule("schedule-123")
            ```
        """
⋮----
def delete_all_schedules(self) -> None
⋮----
"""Delete all schedules and their results.

        This method removes all schedules and their execution histories from Redis.

        Example:
            ```python
            # Remove all schedules and their histories
            worker.delete_all_schedules()
            ```
        """
⋮----
@property
    def schedules(self)
⋮----
"""Get all schedules from all schedulers.

        Returns:
            list[Job]: List of all scheduled jobs.

        Example:
            ```python
            all_schedules = worker.schedules
            print(f"Total schedules: {len(all_schedules)}")
            ```
        """
schedules = self.get_schedules()
⋮----
@property
    def schedule_ids(self)
⋮----
"""Get all schedule IDs.

        Returns:
            list[str]: List of unique identifiers for all schedules.

        Example:
            ```python
            ids = worker.schedule_ids
            print(f"Schedule IDs: {', '.join(ids)}")
            ```
        """
schedule_ids = [schedule.id for schedule in self.schedules]
````

## File: src/flowerpower/job_queue/rq/setup.py
````python
# Enums for RQ DataStore and EventBroker types
# class RQBackendType(BackendType):
#    REDIS = "redis"
#    MEMORY = "memory"
⋮----
@dataclass  # (slots=True)
@dataclass  # (slots=True)
class RQBackend(BaseBackend)
⋮----
"""RQ Backend implementation for Redis Queue (RQ) job storage and queuing.

    This class provides a Redis-based backend for RQ job storage and queue management.
    It supports both Redis and in-memory storage options for development/testing.

    Args:
        queues (str | list[str] | None): Names of queues to create. Defaults to ["default"].
        num_workers (int): Number of worker processes to use. Defaults to 1.

    Attributes:
        type (str): Backend type, either "redis" or "memory". Inherited from BaseBackend.
        uri (str): Connection URI. Inherited from BaseBackend.
        result_namespace (str): Namespace for storing job results in Redis.
        _client (redis.Redis | dict): Redis client or dict for memory storage.

    Raises:
        ValueError: If an invalid backend type is specified.

    Example:
        ```python
        # Create Redis backend with default queue
        backend = RQBackend(
            type="redis",
            uri="redis://localhost:6379/0"
        )

        # Create Redis backend with multiple queues
        backend = RQBackend(
            type="redis",
            uri="redis://localhost:6379/0",
            queues=["high", "default", "low"]
        )

        # Create in-memory backend for testing
        backend = RQBackend(type="memory", queues=["test"])
        ```
    """
⋮----
queues: str | list[str] | None = field(default_factory=lambda: ["default"])
num_workers: int = field(default=1)
⋮----
def __post_init__(self) -> None
⋮----
"""Initialize and validate the backend configuration.

        This method is called automatically after instance creation. It:
        1. Sets default type to "redis" if not specified
        2. Calls parent class initialization
        3. Validates backend type
        4. Sets default result namespace

        Raises:
            ValueError: If an unsupported backend type is specified.
                Only "redis" and "memory" types are supported.
        """
⋮----
def setup(self) -> None
⋮----
"""Set up the Redis client or in-memory storage.

        This method initializes the backend storage based on the configured type.
        For Redis, it creates a Redis client with the specified connection parameters.
        For in-memory storage, it creates a simple dictionary.

        Raises:
            ValueError: If an unsupported backend type is specified.
            redis.RedisError: If Redis connection fails.

        Example:
            ```python
            backend = RQBackend(
                type="redis",
                host="localhost",
                port=6379,
                password="secret",
                database="0",
                ssl=True
            )
            backend.setup()
            ```
        """
# Use connection info from BaseBackend to create Redis client
⋮----
# Parse db from database or default to 0
db = 0
⋮----
db = int(self.database)
⋮----
# Simple in-memory dict for testing
⋮----
@property
    def client(self) -> redis.Redis | dict
⋮----
"""Get the initialized storage client.

        This property provides access to the Redis client or in-memory dictionary,
            initializing it if needed.

        Returns:
            redis.Redis | dict: The Redis client for Redis backend,
                or dictionary for in-memory backend.

        Example:
            ```python
            backend = RQBackend(type="redis", uri="redis://localhost:6379/0")
            redis_client = backend.client  # Gets Redis client
            redis_client.set("key", "value")

            backend = RQBackend(type="memory")
            mem_dict = backend.client  # Gets dict for testing
            mem_dict["key"] = "value"
            ```
        """
````

## File: src/flowerpower/pipeline/__init__.py
````python
__all__ = [
````

## File: src/flowerpower/plugins/mqtt/__init__.py
````python
MQTTManager = MqttManager
⋮----
__all__ = [
````

## File: src/flowerpower/plugins/mqtt/cfg.py
````python
class MqttConfig(BaseConfig)
⋮----
username: str | None = None
password: str | None = None
host: str | None = "localhost"
port: int | None = 1883
topic: str | None = None
first_reconnect_delay: int = 1
max_reconnect_count: int = 5
reconnect_rate: int = 2
max_reconnect_delay: int = 60
transport: str = "tcp"
clean_session: bool = True
client_id: str | None = None
client_id_suffix: str | None = None
````

## File: src/flowerpower/utils/sql.py
````python
"""
    Converts a timestamp string (ISO 8601 format) into a datetime, date, or time object
    using only standard Python libraries.

    Handles strings with or without timezone information (e.g., '2023-01-01T10:00:00+02:00',
    '2023-01-01', '10:00:00'). Supports timezone offsets like '+HH:MM' or '+HHMM'.
    For named timezones (e.g., 'Europe/Paris'), requires Python 3.9+ and the 'tzdata'
    package to be installed.

    Args:
        timestamp_str (str): The string representation of the timestamp (ISO 8601 format).
        tz (str, optional): Target timezone identifier (e.g., 'UTC', '+02:00', 'Europe/Paris').
            If provided, the output datetime/time will be localized or converted to this timezone.
            Defaults to None.
        naive (bool, optional): If True, return a naive datetime/time (no timezone info),
            even if the input string or `tz` parameter specifies one. Defaults to False.

    Returns:
        Union[dt.datetime, dt.date, dt.time]: The parsed datetime, date, or time object.

    Raises:
        ValueError: If the timestamp string format is invalid or the timezone is
                    invalid/unsupported.
    """
⋮----
# Regex to parse timezone offsets like +HH:MM or +HHMM
_TZ_OFFSET_REGEX = re.compile(r"([+-])(\d{2}):?(\d{2})")
⋮----
def _parse_tz_offset(tz_str: str) -> dt.tzinfo | None
⋮----
"""Parses a timezone offset string into a timezone object."""
match = _TZ_OFFSET_REGEX.fullmatch(tz_str)
⋮----
offset_seconds = (int(hours) * 3600 + int(minutes) * 60) * (
⋮----
def _get_tzinfo(tz_identifier: str | None) -> dt.tzinfo | None
⋮----
"""Gets a tzinfo object from a string (offset or IANA name)."""
⋮----
# Try parsing as offset first
offset_tz = _parse_tz_offset(tz_identifier)
⋮----
# Try parsing as IANA name using zoneinfo (if available)
⋮----
except Exception as e:  # Catch other potential zoneinfo errors
⋮----
# zoneinfo not available
⋮----
target_tz: dt.tzinfo | None = _get_tzinfo(tz)
parsed_obj: dt.datetime | dt.date | dt.time | None = None
⋮----
# Preprocess: Replace space separator, strip whitespace
processed_str = timestamp_str.strip().replace(" ", "T")
⋮----
# Attempt parsing (datetime, date, time) using fromisoformat
⋮----
# Python < 3.11 fromisoformat has limitations (e.g., no Z, no +HHMM offset)
# This implementation assumes Python 3.11+ for full ISO 8601 support via fromisoformat
# or that input strings use formats compatible with older versions (e.g., +HH:MM)
parsed_obj = dt.datetime.fromisoformat(processed_str)
⋮----
parsed_obj = dt.date.fromisoformat(processed_str)
⋮----
# Time parsing needs care, especially with offsets in older Python
parsed_obj = dt.time.fromisoformat(processed_str)
⋮----
# Add fallback for simple HH:MM:SS if needed, though less robust
# try:
#     parsed_obj = dt.datetime.strptime(processed_str, "%H:%M:%S").time()
# except ValueError:
⋮----
# Apply timezone logic if we have a datetime or time object
⋮----
is_aware = (
⋮----
# Convert existing aware object to target timezone (only for datetime)
⋮----
parsed_obj = parsed_obj.astimezone(target_tz)
# else: dt.time cannot be converted without a date context. Keep original tz.
⋮----
# Localize naive object to target timezone
parsed_obj = parsed_obj.replace(tzinfo=target_tz)
is_aware = True  # Object is now considered aware
⋮----
# Handle naive flag: remove tzinfo if requested
⋮----
parsed_obj = parsed_obj.replace(tzinfo=None)
⋮----
# If it's a date object, tz/naive flags are ignored
⋮----
# Compile regex patterns once for efficiency
SPLIT_PATTERN = re.compile(
LOGICAL_OPERATORS_PATTERN = re.compile(
⋮----
def sql2pyarrow_filter(string: str, schema: pa.Schema) -> pc.Expression
⋮----
"""
    Generates a filter expression for PyArrow based on a given string and schema.

    Parameters:
        string (str): The string containing the filter expression.
        schema (pa.Schema): The PyArrow schema used to validate the filter expression.

    Returns:
        pc.Expression: The generated filter expression.

    Raises:
        ValueError: If the input string is invalid or contains unsupported operations.
    """
⋮----
def parse_value(val: str, type_: pa.DataType) -> Any
⋮----
"""Parse and convert value based on the field type."""
⋮----
def _parse_part(part: str) -> pc.Expression
⋮----
match = SPLIT_PATTERN.search(part)
⋮----
sign = match.group().lower().strip()
⋮----
type_ = schema.field(field).type
val = parse_value(val, type_)
⋮----
operations = {
⋮----
parts = LOGICAL_OPERATORS_PATTERN.split(string)
operators = [op.lower().strip() for op in LOGICAL_OPERATORS_PATTERN.findall(string)]
⋮----
expr = _parse_part(parts[0])
⋮----
expr = expr & _parse_part(part)
⋮----
expr = expr & ~_parse_part(part)
⋮----
expr = expr | _parse_part(part)
⋮----
expr = expr | ~_parse_part(part)
⋮----
def sql2polars_filter(string: str, schema: pl.Schema) -> pl.Expr
⋮----
"""
    Generates a filter expression for Polars based on a given string and schema.

    Parameters:
        string (str): The string containing the filter expression.
        schema (pl.Schema): The Polars schema used to validate the filter expression.

    Returns:
        pl.Expr: The generated filter expression.

    Raises:
        ValueError: If the input string is invalid or contains unsupported operations.
    """
⋮----
def parse_value(val: str, dtype: pl.DataType) -> Any
⋮----
def _parse_part(part: str) -> pl.Expr
⋮----
dtype = schema[field]
val = parse_value(val, dtype)
⋮----
def get_table_names(sql_query)
````

## File: examples/rq/hello-world/conf/project.yml
````yaml
name: ewnnesigateway_gdi
job_queue:
  type: rq
  backend:
    type: redis
    uri: null
    username: null
    password: ffGg6X0nUrux
    host: lodl.nes.siemens.de
    port: 6379
    database: 0
    ssl: true
    cert_file: null
    key_file: null
    ca_file: null
    verify_ssl: false
    queues:
    - default
    - high
    - low
    - scheduler
    num_workers: 4
adapter:
  hamilton_tracker:
    username: Lewis
    api_url: https://lodl.nes.siemens.de:8241
    ui_url: https://lodl.nes.siemens.de:8242
    api_key: null
    verify: false
  mlflow:
    tracking_uri: null
    registry_uri: null
    artifact_location: null
  ray:
    ray_init_config: null
    shutdown_ray_on_completion: false
  opentelemetry:
    host: localhost
    port: 6831
````

## File: src/flowerpower/cfg/base.py
````python
class BaseConfig(msgspec.Struct, kw_only=True)
⋮----
def to_dict(self) -> dict[str, Any]
⋮----
def to_yaml(self, path: str, fs: AbstractFileSystem | None = None) -> None
⋮----
"""
        Converts the instance to a YAML file.

        Args:
            path: The path to the YAML file.
            fs: An optional filesystem instance to use for file operations.

        Raises:
            NotImplementedError: If the filesystem does not support writing files.
        """
⋮----
fs = filesystem("file")
⋮----
# yaml.dump(self.to_dict(), f, default_flow_style=False)
⋮----
@classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseConfig"
⋮----
"""
        Converts a dictionary to an instance of the class.
        Args:
            data: The dictionary to convert.

        Returns:
            An instance of the class with the values from the dictionary.
        """
⋮----
@classmethod
    def from_yaml(cls, path: str, fs: AbstractFileSystem | None = None) -> "BaseConfig"
⋮----
"""
        Loads a YAML file and converts it to an instance of the class.

        Args:
            path: The path to the YAML file.
            fs: An optional filesystem instance to use for file operations.

        Returns:
            An instance of the class with the values from the YAML file.

        """
⋮----
# data = yaml.full_load(f)
# return cls.from_dict(data)
⋮----
def update(self, d: dict[str, Any]) -> None
⋮----
current_value = getattr(self, k)
⋮----
def merge_dict(self, d: dict[str, Any]) -> Self
⋮----
"""
        Creates a copy of this instance and updates the copy with values
        from the provided dictionary, only if the dictionary field's value is not
        its default value. The original instance (self) is not modified.

        Args:
            d: The dictionary to get values from.

        Returns:
            A new instance of the struct with updated values.
        """
self_copy = copy.copy(self)
⋮----
current_value = getattr(self_copy, k)
⋮----
def merge(self, source: Self) -> Self
⋮----
"""
        Creates a copy of this instance and updates the copy with values
        from the source struct, only if the source field's value is not
        its default value. The original instance (self) is not modified.

        Args:
            source: The msgspec.Struct instance of the same type to get values from.

        Returns:
            A new instance of the struct with updated values.

        Raises:
            TypeError: If source is not of the same type as self.
        """
⋮----
updated_instance = copy.copy(self)
⋮----
# Get default values if they exist
defaults = getattr(source, "__struct_defaults__", {})
⋮----
source_value = getattr(source, field)
has_explicit_default = field in defaults
is_default_value = False
⋮----
is_default_value = source_value == defaults[field]
⋮----
is_default_value = source_value is None
````

## File: src/flowerpower/cli/job_queue.py
````python
from ..job_queue import JobQueueManager  # Adjust import as needed
⋮----
# Create a Typer app for job queue management commands
app = typer.Typer(help="Job queue management commands")
⋮----
"""
    Start a worker or worker pool to process jobs.

    This command starts a worker process (or a pool of worker processes) that will
    execute jobs from the queue. The worker will continue running until stopped
    or can be run in the background.

    Args:
        type: Type of job queue backend (rq, apscheduler)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        background: Run the worker in the background
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        num_workers: Number of worker processes to start (pool mode)

    Examples:
        # Start a worker with default settings
        $ flowerpower job-queue start-worker

        # Start a worker for a specific backend type
        $ flowerpower job-queue start-worker --type rq

        # Start a worker pool with 4 processes
        $ flowerpower job-queue start-worker --num-workers 4

        # Run a worker in the background
        $ flowerpower job-queue start-worker --background

        # Set a specific logging level
        $ flowerpower job-queue start-worker --log-level debug
    """
parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}
⋮----
num_workers = worker.cfg.backend.num_workers
⋮----
"""
    Start the scheduler process for queued jobs.

    This command starts a scheduler that manages queued jobs and scheduled tasks.
    Note that this is only needed for RQ workers, as APScheduler workers have
    their own built-in scheduler.

    Args:
        type: Type of job queue backend (rq, apscheduler)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        background: Run the scheduler in the background
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        interval: Interval for checking jobs in seconds (RQ only)

    Examples:
        # Start a scheduler with default settings
        $ flowerpower job-queue start-scheduler

        # Start a scheduler for a specific backend type
        $ flowerpower job-queue start-scheduler --type rq

        # Run a scheduler in the background
        $ flowerpower job-queue start-scheduler --background

        # Set a specific scheduler check interval (RQ only)
        $ flowerpower job-queue start-scheduler --interval 30
    """
⋮----
# @app.command()
# def cancel_all_jobs(
#     type: str | None = None,
#     queue_name: str | None = None,
#     name: str | None = None,
#     base_dir: str | None = None,
#     storage_options: str | None = None,
#     log_level: str = "info",
# ):
#     """
#     Cancel all jobs from the scheduler.
⋮----
#     Note: This is different from deleting jobs as it only stops them from running but keeps their history.
⋮----
#     Args:
#         type: Type of the job queue (rq, apscheduler)
#         queue_name: Name of the queue (RQ only)
#         name: Name of the scheduler
#         base_dir: Base directory for the scheduler
#         storage_options: Storage options as JSON or key=value pairs
#         log_level: Logging level
⋮----
#     parsed_storage_options = parse_dict_or_list_param(storage_options, "dict") or {}
⋮----
#     with JobQueueManager(
#         type=type, name=name, base_dir=base_dir, storage_options=parsed_storage_options, log_level=log_level
#     ) as worker:
#         if worker.cfg.backend.type != "rq":
#             logger.info(f"Job cancellation is not supported for {worker.cfg.backend.type} workers. Skipping.")
#             return
⋮----
#         worker.cancel_all_jobs(queue_name=queue_name)
⋮----
# def cancel_all_schedules(
⋮----
#     Cancel all schedules from the scheduler.
⋮----
#     Note: This is different from deleting schedules as it only stops them from running but keeps their configuration.
⋮----
#         worker.cancel_all_schedules()
⋮----
"""
    Cancel a job or multiple jobs in the queue.

    This command stops a job from executing (if it hasn't started yet) or signals
    it to stop (if already running). Canceling is different from deleting as it
    maintains the job history but prevents execution.

    Args:
        job_id: ID of the job to cancel (ignored if --all is used)
        all: Cancel all jobs instead of a specific one
        queue_name: For RQ only, specifies the queue to cancel jobs from
        type: Type of job queue backend (rq, apscheduler)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Cancel a specific job
        $ flowerpower job-queue cancel-job job-123456

        # Cancel all jobs in the default queue
        $ flowerpower job-queue cancel-job --all dummy-id

        # Cancel all jobs in a specific queue (RQ only)
        $ flowerpower job-queue cancel-job --all dummy-id --queue-name high-priority

        # Specify the backend type explicitly
        $ flowerpower job-queue cancel-job job-123456 --type rq
    """
⋮----
count = worker.cancel_all_jobs(
⋮----
"""
    Cancel a specific schedule.

    Note: This is different from deleting a schedule as it only stops it from running but keeps its configuration.

    Args:
        schedule_id: ID of the schedule to cancel
        all: If True, cancel all schedules
        type: Type of the job queue (rq, apscheduler)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
⋮----
# def delete_all_jobs(
⋮----
#     Delete all jobs from the scheduler. Note that this is different from cancelling jobs
#     as it also removes job history and results.
⋮----
#         worker.delete_all_jobs(queue_name=queue_name if worker.cfg.backend.type == "rq" else None)
⋮----
# def delete_all_schedules(
⋮----
#     Delete all schedules from the scheduler.
⋮----
#         worker.delete_all_schedules()
⋮----
"""
    Delete a specific job.

    Args:
        job_id: ID of the job to delete
        all: If True, delete all jobs
        queue_name: Name of the queue (RQ only). If provided and all is True, delete all jobs in the queue
        type: Type of the job queue (rq, apscheduler)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
⋮----
"""
    Delete a specific schedule.

    Args:
        schedule_id: ID of the schedule to delete
        all: If True, delete all schedules
        type: Type of the job queue (rq, apscheduler)
        name: Name of the scheduler
        base_dir: Base directory for the scheduler
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level
    """
⋮----
# def get_job(
#     job_id: str,
⋮----
#     Get information about a specific job.
⋮----
#         job_id: ID of the job
⋮----
#         # show_jobs should display the job info
#         worker.show_jobs(job_id=job_id)
⋮----
# def get_job_result(
⋮----
#     wait: bool = True,
⋮----
#     Get the result of a specific job.
⋮----
#         wait: Wait for the result if job is still running (APScheduler only)
⋮----
#         # worker's get_job_result method will handle the result display
#         worker.get_job_result(job_id, wait=wait if worker.cfg.backend.type == "apscheduler" else False)
⋮----
# def get_jobs(
⋮----
#     List all jobs.
⋮----
#         worker.show_jobs()
⋮----
# def get_schedule(
#     schedule_id: str,
⋮----
#     Get information about a specific schedule.
⋮----
#         schedule_id: ID of the schedule
⋮----
#         # show_schedule should display the schedule info
#         worker.show_schedules(schedule_id=schedule_id)
⋮----
# def get_schedules(
⋮----
#     List all schedules.
⋮----
#         worker.show_schedules()
⋮----
"""
    Show all job IDs in the job queue.

    This command displays all job IDs currently in the system, helping you identify
    jobs for other operations like getting results, canceling, or deleting jobs.

    Args:
        type: Type of job queue backend (rq, apscheduler)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Show job IDs using default settings
        $ flowerpower job-queue show-job-ids

        # Show job IDs for a specific queue type
        $ flowerpower job-queue show-job-ids --type rq

        # Show job IDs with a custom scheduler configuration
        $ flowerpower job-queue show-job-ids --name my-scheduler

        # Show job IDs with debug logging
        $ flowerpower job-queue show-job-ids --log-level debug
    """
⋮----
# worker's job_ids property will print the IDs
ids = worker.job_ids
# Ensure we always print something meaningful
⋮----
# If the worker's property doesn't already print the IDs, print them here
elif not isinstance(ids, type(None)):  # Check if None was returned
⋮----
"""
    Show all schedule IDs in the job queue.

    This command displays all schedule IDs currently in the system, helping you
    identify schedules for other operations like pausing, resuming, or deleting schedules.

    Args:
        type: Type of job queue backend (rq, apscheduler)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Show schedule IDs using default settings
        $ flowerpower job-queue show-schedule-ids

        # Show schedule IDs for a specific queue type
        $ flowerpower job-queue show-schedule-ids --type apscheduler

        # Show schedule IDs with a custom scheduler configuration
        $ flowerpower job-queue show-schedule-ids --name my-scheduler

        # Show schedule IDs with debug logging
        $ flowerpower job-queue show-schedule-ids --log-level debug
    """
⋮----
# worker's schedule_ids property will print the IDs
ids = worker.schedule_ids
⋮----
# def pause_all_schedules(
⋮----
#     Pause all schedules.
⋮----
#     Note: This functionality is only available for APScheduler workers.
⋮----
#         if worker.cfg.backend.type != "apscheduler":
#             logger.info(f"Schedule pausing is not supported for {worker.cfg.backend.type} workers.")
⋮----
#         worker.pause_all_schedules()
⋮----
"""
    Pause a schedule or multiple schedules.

    This command temporarily stops a scheduled job from running while maintaining its
    configuration. Paused schedules can be resumed later. Note that this functionality
    is only available for APScheduler workers.

    Args:
        schedule_id: ID of the schedule to pause (ignored if --all is used)
        all: Pause all schedules instead of a specific one
        type: Type of job queue backend (rq, apscheduler)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Pause a specific schedule
        $ flowerpower job-queue pause-schedule schedule-123456

        # Pause all schedules
        $ flowerpower job-queue pause-schedule --all dummy-id

        # Specify the backend type explicitly
        $ flowerpower job-queue pause-schedule schedule-123456 --type apscheduler
    """
⋮----
count = worker.pause_all_schedules()
⋮----
success = worker.pause_schedule(schedule_id)
⋮----
# def resume_all_schedules(
⋮----
#     Resume all paused schedules.
⋮----
#             logger.info(f"Schedule resuming is not supported for {worker.cfg.backend.type} workers.")
⋮----
#         worker.resume_all_schedules()
⋮----
"""
    Resume a paused schedule or multiple schedules.

    This command restarts previously paused schedules, allowing them to run again according
    to their original configuration. Note that this functionality is only available for
    APScheduler workers.

    Args:
        schedule_id: ID of the schedule to resume (ignored if --all is used)
        all: Resume all schedules instead of a specific one
        type: Type of job queue backend (rq, apscheduler)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)

    Examples:
        # Resume a specific schedule
        $ flowerpower job-queue resume-schedule schedule-123456

        # Resume all schedules
        $ flowerpower job-queue resume-schedule --all dummy-id

        # Specify the backend type explicitly
        $ flowerpower job-queue resume-schedule schedule-123456 --type apscheduler

        # Set a specific logging level
        $ flowerpower job-queue resume-schedule schedule-123456 --log-level debug
    """
⋮----
count = worker.resume_all_schedules()
⋮----
success = worker.resume_schedule(schedule_id)
⋮----
"""
    Display detailed information about all jobs in the queue.

    This command shows comprehensive information about jobs including their status,
    creation time, execution time, and other details in a user-friendly format.

    Args:
        type: Type of job queue backend (rq, apscheduler)
        queue_name: Name of the queue to show jobs from (RQ only)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        format: Output format for the job information

    Examples:
        # Show all jobs using default settings
        $ flowerpower job-queue show-jobs

        # Show jobs for a specific queue type
        $ flowerpower job-queue show-jobs --type rq

        # Show jobs in a specific RQ queue
        $ flowerpower job-queue show-jobs --queue-name high-priority

        # Display jobs in JSON format
        $ flowerpower job-queue show-jobs --format json
    """
⋮----
"""
    Display detailed information about all schedules.

    This command shows comprehensive information about scheduled jobs including their
    timing configuration, status, and other details in a user-friendly format.

    Args:
        type: Type of job queue backend (rq, apscheduler)
        name: Name of the scheduler configuration to use
        base_dir: Base directory for the scheduler configuration
        storage_options: Storage options as JSON or key=value pairs
        log_level: Logging level (debug, info, warning, error, critical)
        format: Output format for the schedule information

    Examples:
        # Show all schedules using default settings
        $ flowerpower job-queue show-schedules

        # Show schedules for a specific queue type
        $ flowerpower job-queue show-schedules --type apscheduler

        # Display schedules in JSON format
        $ flowerpower job-queue show-schedules --format json
    """
````

## File: src/flowerpower/fs/storage_options.py
````python
class BaseStorageOptions(BaseModel)
⋮----
"""Base class for filesystem storage configuration options.

    Provides common functionality for all storage option classes including:
    - YAML serialization/deserialization
    - Dictionary conversion
    - Filesystem instance creation
    - Configuration updates

    Attributes:
        protocol (str): Storage protocol identifier (e.g., "s3", "gs", "file")

    Example:
        >>> # Create and save options
        >>> options = BaseStorageOptions(protocol="s3")
        >>> options.to_yaml("config.yml")
        >>>
        >>> # Load from YAML
        >>> loaded = BaseStorageOptions.from_yaml("config.yml")
        >>> print(loaded.protocol)
        's3'
    """
⋮----
protocol: str
⋮----
def to_dict(self, with_protocol: bool = False) -> dict
⋮----
"""Convert storage options to dictionary.

        Args:
            with_protocol: Whether to include protocol in output dictionary

        Returns:
            dict: Dictionary of storage options with non-None values

        Example:
            >>> options = BaseStorageOptions(protocol="s3")
            >>> print(options.to_dict())
            {}
            >>> print(options.to_dict(with_protocol=True))
            {'protocol': 's3'}
        """
items = self.model_dump().items()
⋮----
"""Load storage options from YAML file.

        Args:
            path: Path to YAML configuration file
            fs: Filesystem to use for reading file

        Returns:
            BaseStorageOptions: Loaded storage options instance

        Example:
            >>> # Load from local file
            >>> options = BaseStorageOptions.from_yaml("config.yml")
            >>> print(options.protocol)
            's3'
        """
⋮----
fs = filesystem("file")
⋮----
data = yaml.safe_load(f)
⋮----
def to_yaml(self, path: str, fs: AbstractFileSystem = None) -> None
⋮----
"""Save storage options to YAML file.

        Args:
            path: Path where to save configuration
            fs: Filesystem to use for writing

        Example:
            >>> options = BaseStorageOptions(protocol="s3")
            >>> options.to_yaml("config.yml")
        """
⋮----
data = self.to_dict()
⋮----
def to_filesystem(self) -> AbstractFileSystem
⋮----
"""Create fsspec filesystem instance from options.

        Returns:
            AbstractFileSystem: Configured filesystem instance

        Example:
            >>> options = BaseStorageOptions(protocol="file")
            >>> fs = options.to_filesystem()
            >>> files = fs.ls("/path/to/data")
        """
⋮----
def update(self, **kwargs: Any) -> None
⋮----
"""Update storage options with new values.

        Args:
            **kwargs: New option values to set

        Example:
            >>> options = BaseStorageOptions(protocol="s3")
            >>> options.update(region="us-east-1")
            >>> print(options.region)
            'us-east-1'
        """
self = self.model_copy(update=kwargs)
⋮----
class AzureStorageOptions(BaseStorageOptions)
⋮----
"""Azure Storage configuration options.

    Provides configuration for Azure storage services:
    - Azure Blob Storage (az://)
    - Azure Data Lake Storage Gen2 (abfs://)
    - Azure Data Lake Storage Gen1 (adl://)

    Supports multiple authentication methods:
    - Connection string
    - Account key
    - Service principal
    - Managed identity
    - SAS token

    Attributes:
        protocol (str): Storage protocol ("az", "abfs", or "adl")
        account_name (str): Storage account name
        account_key (str): Storage account access key
        connection_string (str): Full connection string
        tenant_id (str): Azure AD tenant ID
        client_id (str): Service principal client ID
        client_secret (str): Service principal client secret
        sas_token (str): SAS token for limited access

    Example:
        >>> # Blob Storage with account key
        >>> options = AzureStorageOptions(
        ...     protocol="az",
        ...     account_name="mystorageacct",
        ...     account_key="key123..."
        ... )
        >>>
        >>> # Data Lake with service principal
        >>> options = AzureStorageOptions(
        ...     protocol="abfs",
        ...     account_name="mydatalake",
        ...     tenant_id="tenant123",
        ...     client_id="client123",
        ...     client_secret="secret123"
        ... )
        >>>
        >>> # Simple connection string auth
        >>> options = AzureStorageOptions(
        ...     protocol="az",
        ...     connection_string="DefaultEndpoints..."
        ... )
    """
⋮----
account_name: str | None = None
account_key: str | None = None
connection_string: str | None = None
tenant_id: str | None = None
client_id: str | None = None
client_secret: str | None = None
sas_token: str | None = None
⋮----
@classmethod
    def from_env(cls) -> "AzureStorageOptions"
⋮----
"""Create storage options from environment variables.

        Reads standard Azure environment variables:
        - AZURE_STORAGE_ACCOUNT_NAME
        - AZURE_STORAGE_ACCOUNT_KEY
        - AZURE_STORAGE_CONNECTION_STRING
        - AZURE_TENANT_ID
        - AZURE_CLIENT_ID
        - AZURE_CLIENT_SECRET
        - AZURE_STORAGE_SAS_TOKEN

        Returns:
            AzureStorageOptions: Configured storage options

        Example:
            >>> # With environment variables set:
            >>> options = AzureStorageOptions.from_env()
            >>> print(options.account_name)  # From AZURE_STORAGE_ACCOUNT_NAME
            'mystorageacct'
        """
⋮----
def to_env(self) -> None
⋮----
"""Export options to environment variables.

        Sets standard Azure environment variables.

        Example:
            >>> options = AzureStorageOptions(
            ...     protocol="az",
            ...     account_name="mystorageacct",
            ...     account_key="key123"
            ... )
            >>> options.to_env()
            >>> print(os.getenv("AZURE_STORAGE_ACCOUNT_NAME"))
            'mystorageacct'
        """
env = {
env = {k: v for k, v in env.items() if v is not None}
⋮----
class GcsStorageOptions(BaseStorageOptions)
⋮----
"""Google Cloud Storage configuration options.

    Provides configuration for GCS access with support for:
    - Service account authentication
    - Default application credentials
    - Token-based authentication
    - Project configuration
    - Custom endpoints

    Attributes:
        protocol (str): Storage protocol ("gs" or "gcs")
        token (str): Path to service account JSON file
        project (str): Google Cloud project ID
        access_token (str): OAuth2 access token
        endpoint_url (str): Custom storage endpoint
        timeout (int): Request timeout in seconds

    Example:
        >>> # Service account auth
        >>> options = GcsStorageOptions(
        ...     protocol="gs",
        ...     token="path/to/service-account.json",
        ...     project="my-project-123"
        ... )
        >>>
        >>> # Application default credentials
        >>> options = GcsStorageOptions(
        ...     protocol="gcs",
        ...     project="my-project-123"
        ... )
        >>>
        >>> # Custom endpoint (e.g., test server)
        >>> options = GcsStorageOptions(
        ...     protocol="gs",
        ...     endpoint_url="http://localhost:4443",
        ...     token="test-token.json"
        ... )
    """
⋮----
token: str | None = None
project: str | None = None
access_token: str | None = None
endpoint_url: str | None = None
timeout: int | None = None
⋮----
@classmethod
    def from_env(cls) -> "GcsStorageOptions"
⋮----
"""Create storage options from environment variables.

        Reads standard GCP environment variables:
        - GOOGLE_CLOUD_PROJECT: Project ID
        - GOOGLE_APPLICATION_CREDENTIALS: Service account file path
        - STORAGE_EMULATOR_HOST: Custom endpoint (for testing)
        - GCS_OAUTH_TOKEN: OAuth2 access token

        Returns:
            GcsStorageOptions: Configured storage options

        Example:
            >>> # With environment variables set:
            >>> options = GcsStorageOptions.from_env()
            >>> print(options.project)  # From GOOGLE_CLOUD_PROJECT
            'my-project-123'
        """
⋮----
"""Export options to environment variables.

        Sets standard GCP environment variables.

        Example:
            >>> options = GcsStorageOptions(
            ...     protocol="gs",
            ...     project="my-project",
            ...     token="service-account.json"
            ... )
            >>> options.to_env()
            >>> print(os.getenv("GOOGLE_CLOUD_PROJECT"))
            'my-project'
        """
⋮----
def to_fsspec_kwargs(self) -> dict
⋮----
"""Convert options to fsspec filesystem arguments.

        Returns:
            dict: Arguments suitable for GCSFileSystem

        Example:
            >>> options = GcsStorageOptions(
            ...     protocol="gs",
            ...     token="service-account.json",
            ...     project="my-project"
            ... )
            >>> kwargs = options.to_fsspec_kwargs()
            >>> fs = filesystem("gcs", **kwargs)
        """
kwargs = {
⋮----
class AwsStorageOptions(BaseStorageOptions)
⋮----
"""AWS S3 storage configuration options.

    Provides comprehensive configuration for S3 access with support for:
    - Multiple authentication methods (keys, profiles, environment)
    - Custom endpoints for S3-compatible services
    - Region configuration
    - SSL/TLS settings

    Attributes:
        protocol (str): Always "s3" for S3 storage
        key (str): AWS access key ID (alias for access_key_id)
        access_key_id (str): AWS access key ID
        secret (str): AWS secret access key (alias for secret_access_key)
        secret_access_key (str): AWS secret access key
        token (str): AWS session token (alias for session_token)
        session_token (str): AWS session token
        endpoint_url (str): Custom S3 endpoint URL
        region (str): AWS region name
        allow_invalid_certificates (bool): Skip SSL certificate validation
        allow_http (bool): Allow unencrypted HTTP connections
        profile (str): AWS credentials profile name

    Example:
        >>> # Basic credentials
        >>> options = AwsStorageOptions(
        ...     access_key_id="AKIAXXXXXXXX",
        ...     secret_access_key="SECRETKEY",
        ...     region="us-east-1"
        ... )
        >>>
        >>> # Profile-based auth
        >>> options = AwsStorageOptions(profile="dev")
        >>>
        >>> # S3-compatible service (MinIO)
        >>> options = AwsStorageOptions(
        ...     endpoint_url="http://localhost:9000",
        ...     access_key_id="minioadmin",
        ...     secret_access_key="minioadmin",
        ...     allow_http=True
        ... )
    """
⋮----
protocol: str = "s3"
key: str | None = None
access_key_id: str | None = None
secret: str | None = None
secret_access_key: str | None = None
⋮----
session_token: str | None = None
⋮----
region: str | None = None
allow_invalid_certificates: bool | None = None
allow_http: bool | None = None
profile: str | None = None
⋮----
def model_post_init(self, __context: Any) -> None
⋮----
"""Post-initialization processing of AWS credentials.

        Handles credential aliasing and profile-based loading.
        Called automatically after initialization.

        Args:
            __context: Pydantic validation context (unused)

        Example:
            >>> # Alias handling
            >>> opts = AwsStorageOptions(
            ...     key="ACCESS_KEY",
            ...     secret="SECRET_KEY"
            ... )
            >>> print(opts.access_key_id)  # Normalized
            'ACCESS_KEY'
        """
# Normalize credential aliases
⋮----
# Load profile if specified
⋮----
profile_opts = self.from_aws_credentials(
⋮----
"""Create storage options from AWS credentials file.

        Loads credentials from ~/.aws/credentials and ~/.aws/config files.

        Args:
            profile: AWS credentials profile name
            allow_invalid_certificates: Skip SSL certificate validation
            allow_http: Allow unencrypted HTTP connections

        Returns:
            AwsStorageOptions: Configured storage options

        Raises:
            ValueError: If profile not found
            FileNotFoundError: If credentials files missing

        Example:
            >>> # Load developer profile
            >>> options = AwsStorageOptions.from_aws_credentials(
            ...     profile="dev",
            ...     allow_http=True  # For local testing
            ... )
        """
cp = configparser.ConfigParser()
⋮----
@classmethod
    def from_env(cls) -> "AwsStorageOptions"
⋮----
"""Create storage options from environment variables.

        Reads standard AWS environment variables:
        - AWS_ACCESS_KEY_ID
        - AWS_SECRET_ACCESS_KEY
        - AWS_SESSION_TOKEN
        - AWS_ENDPOINT_URL
        - AWS_DEFAULT_REGION
        - ALLOW_INVALID_CERTIFICATES
        - AWS_ALLOW_HTTP

        Returns:
            AwsStorageOptions: Configured storage options

        Example:
            >>> # Load from environment
            >>> options = AwsStorageOptions.from_env()
            >>> print(options.region)
            'us-east-1'  # From AWS_DEFAULT_REGION
        """
⋮----
"""Convert options to fsspec filesystem arguments.

        Returns:
            dict: Arguments suitable for fsspec S3FileSystem

        Example:
            >>> options = AwsStorageOptions(
            ...     access_key_id="KEY",
            ...     secret_access_key="SECRET",
            ...     region="us-west-2"
            ... )
            >>> kwargs = options.to_fsspec_kwargs()
            >>> fs = filesystem("s3", **kwargs)
        """
fsspec_kwargs = {
⋮----
def to_object_store_kwargs(self, with_conditional_put: bool = False) -> dict
⋮----
"""Convert options to object store arguments.

        Args:
            with_conditional_put: Add etag-based conditional put support

        Returns:
            dict: Arguments suitable for object store clients

        Example:
            >>> options = AwsStorageOptions(
            ...     access_key_id="KEY",
            ...     secret_access_key="SECRET"
            ... )
            >>> kwargs = options.to_object_store_kwargs()
            >>> client = ObjectStore(**kwargs)
        """
⋮----
"""Export options to environment variables.

        Sets standard AWS environment variables.

        Example:
            >>> options = AwsStorageOptions(
            ...     access_key_id="KEY",
            ...     secret_access_key="SECRET",
            ...     region="us-east-1"
            ... )
            >>> options.to_env()
            >>> print(os.getenv("AWS_ACCESS_KEY_ID"))
            'KEY'
        """
⋮----
def to_filesystem(self)
⋮----
class GitHubStorageOptions(BaseStorageOptions)
⋮----
"""GitHub repository storage configuration options.

    Provides access to files in GitHub repositories with support for:
    - Public and private repositories
    - Branch/tag/commit selection
    - Token-based authentication
    - Custom GitHub Enterprise instances

    Attributes:
        protocol (str): Always "github" for GitHub storage
        org (str): Organization or user name
        repo (str): Repository name
        ref (str): Git reference (branch, tag, or commit SHA)
        token (str): GitHub personal access token
        api_url (str): Custom GitHub API URL for enterprise instances

    Example:
        >>> # Public repository
        >>> options = GitHubStorageOptions(
        ...     org="microsoft",
        ...     repo="vscode",
        ...     ref="main"
        ... )
        >>>
        >>> # Private repository
        >>> options = GitHubStorageOptions(
        ...     org="myorg",
        ...     repo="private-repo",
        ...     token="ghp_xxxx",
        ...     ref="develop"
        ... )
        >>>
        >>> # Enterprise instance
        >>> options = GitHubStorageOptions(
        ...     org="company",
        ...     repo="internal",
        ...     api_url="https://github.company.com/api/v3",
        ...     token="ghp_xxxx"
        ... )
    """
⋮----
protocol: str = "github"
org: str | None = None
repo: str | None = None
ref: str | None = None
⋮----
api_url: str | None = None
⋮----
@classmethod
    def from_env(cls) -> "GitHubStorageOptions"
⋮----
"""Create storage options from environment variables.

        Reads standard GitHub environment variables:
        - GITHUB_ORG: Organization or user name
        - GITHUB_REPO: Repository name
        - GITHUB_REF: Git reference
        - GITHUB_TOKEN: Personal access token
        - GITHUB_API_URL: Custom API URL

        Returns:
            GitHubStorageOptions: Configured storage options

        Example:
            >>> # With environment variables set:
            >>> options = GitHubStorageOptions.from_env()
            >>> print(options.org)  # From GITHUB_ORG
            'microsoft'
        """
⋮----
"""Export options to environment variables.

        Sets standard GitHub environment variables.

        Example:
            >>> options = GitHubStorageOptions(
            ...     org="microsoft",
            ...     repo="vscode",
            ...     token="ghp_xxxx"
            ... )
            >>> options.to_env()
            >>> print(os.getenv("GITHUB_ORG"))
            'microsoft'
        """
⋮----
"""Convert options to fsspec filesystem arguments.

        Returns:
            dict: Arguments suitable for GitHubFileSystem

        Example:
            >>> options = GitHubStorageOptions(
            ...     org="microsoft",
            ...     repo="vscode",
            ...     token="ghp_xxxx"
            ... )
            >>> kwargs = options.to_fsspec_kwargs()
            >>> fs = filesystem("github", **kwargs)
        """
⋮----
class GitLabStorageOptions(BaseStorageOptions)
⋮----
"""GitLab repository storage configuration options.

    Provides access to files in GitLab repositories with support for:
    - Public and private repositories
    - Self-hosted GitLab instances
    - Project ID or name-based access
    - Branch/tag/commit selection
    - Token-based authentication

    Attributes:
        protocol (str): Always "gitlab" for GitLab storage
        base_url (str): GitLab instance URL, defaults to gitlab.com
        project_id (str | int): Project ID number
        project_name (str): Project name/path
        ref (str): Git reference (branch, tag, or commit SHA)
        token (str): GitLab personal access token
        api_version (str): API version to use

    Example:
        >>> # Public project on gitlab.com
        >>> options = GitLabStorageOptions(
        ...     project_name="group/project",
        ...     ref="main"
        ... )
        >>>
        >>> # Private project with token
        >>> options = GitLabStorageOptions(
        ...     project_id=12345,
        ...     token="glpat_xxxx",
        ...     ref="develop"
        ... )
        >>>
        >>> # Self-hosted instance
        >>> options = GitLabStorageOptions(
        ...     base_url="https://gitlab.company.com",
        ...     project_name="internal/project",
        ...     token="glpat_xxxx"
        ... )
    """
⋮----
protocol: str = "gitlab"
base_url: str = "https://gitlab.com"
project_id: str | int | None = None
project_name: str | None = None
⋮----
api_version: str = "v4"
⋮----
"""Validate GitLab configuration after initialization.

        Ensures either project_id or project_name is provided.

        Args:
            __context: Pydantic validation context (unused)

        Raises:
            ValueError: If neither project_id nor project_name is provided

        Example:
            >>> # Valid initialization
            >>> options = GitLabStorageOptions(project_id=12345)
            >>>
            >>> # Invalid initialization
            >>> try:
            ...     options = GitLabStorageOptions()
            ... except ValueError as e:
            ...     print(str(e))
            'Either project_id or project_name must be provided'
        """
⋮----
@classmethod
    def from_env(cls) -> "GitLabStorageOptions"
⋮----
"""Create storage options from environment variables.

        Reads standard GitLab environment variables:
        - GITLAB_URL: Instance URL
        - GITLAB_PROJECT_ID: Project ID
        - GITLAB_PROJECT_NAME: Project name/path
        - GITLAB_REF: Git reference
        - GITLAB_TOKEN: Personal access token
        - GITLAB_API_VERSION: API version

        Returns:
            GitLabStorageOptions: Configured storage options

        Example:
            >>> # With environment variables set:
            >>> options = GitLabStorageOptions.from_env()
            >>> print(options.project_id)  # From GITLAB_PROJECT_ID
            '12345'
        """
⋮----
"""Export options to environment variables.

        Sets standard GitLab environment variables.

        Example:
            >>> options = GitLabStorageOptions(
            ...     project_id=12345,
            ...     token="glpat_xxxx"
            ... )
            >>> options.to_env()
            >>> print(os.getenv("GITLAB_PROJECT_ID"))
            '12345'
        """
⋮----
"""Convert options to fsspec filesystem arguments.

        Returns:
            dict: Arguments suitable for GitLabFileSystem

        Example:
            >>> options = GitLabStorageOptions(
            ...     project_id=12345,
            ...     token="glpat_xxxx"
            ... )
            >>> kwargs = options.to_fsspec_kwargs()
            >>> fs = filesystem("gitlab", **kwargs)
        """
⋮----
class LocalStorageOptions(BaseStorageOptions)
⋮----
"""Local filesystem configuration options.

    Provides basic configuration for local file access. While this class
    is simple, it maintains consistency with other storage options and
    enables transparent switching between local and remote storage.

    Attributes:
        protocol (str): Always "file" for local filesystem
        auto_mkdir (bool): Create directories automatically
        mode (int): Default file creation mode (unix-style)

    Example:
        >>> # Basic local access
        >>> options = LocalStorageOptions()
        >>> fs = options.to_filesystem()
        >>> files = fs.ls("/path/to/data")
        >>>
        >>> # With auto directory creation
        >>> options = LocalStorageOptions(auto_mkdir=True)
        >>> fs = options.to_filesystem()
        >>> with fs.open("/new/path/file.txt", "w") as f:
        ...     f.write("test")  # Creates /new/path/ automatically
    """
⋮----
protocol: str = "file"
auto_mkdir: bool = False
mode: int | None = None
⋮----
"""Convert options to fsspec filesystem arguments.

        Returns:
            dict: Arguments suitable for LocalFileSystem

        Example:
            >>> options = LocalStorageOptions(auto_mkdir=True)
            >>> kwargs = options.to_fsspec_kwargs()
            >>> fs = filesystem("file", **kwargs)
        """
⋮----
def from_dict(protocol: str, storage_options: dict) -> BaseStorageOptions
⋮----
"""Create appropriate storage options instance from dictionary.

    Factory function that creates the correct storage options class based on protocol.

    Args:
        protocol: Storage protocol identifier (e.g., "s3", "gs", "file")
        storage_options: Dictionary of configuration options

    Returns:
        BaseStorageOptions: Appropriate storage options instance

    Raises:
        ValueError: If protocol is not supported

    Example:
        >>> # Create S3 options
        >>> options = from_dict("s3", {
        ...     "access_key_id": "KEY",
        ...     "secret_access_key": "SECRET"
        ... })
        >>> print(type(options).__name__)
        'AwsStorageOptions'
    """
⋮----
def from_env(protocol: str) -> BaseStorageOptions
⋮----
"""Create storage options from environment variables.

    Factory function that creates and configures storage options from
    protocol-specific environment variables.

    Args:
        protocol: Storage protocol identifier (e.g., "s3", "github")

    Returns:
        BaseStorageOptions: Configured storage options instance

    Raises:
        ValueError: If protocol is not supported

    Example:
        >>> # With AWS credentials in environment
        >>> options = from_env("s3")
        >>> print(options.access_key_id)  # From AWS_ACCESS_KEY_ID
        'AKIAXXXXXX'
    """
⋮----
class StorageOptions(BaseModel)
⋮----
"""High-level storage options container and factory.

    Provides a unified interface for creating and managing storage options
    for different protocols.

    Attributes:
        storage_options (BaseStorageOptions): Underlying storage options instance

    Example:
        >>> # Create from protocol
        >>> options = StorageOptions(
        ...     protocol="s3",
        ...     access_key_id="KEY",
        ...     secret_access_key="SECRET"
        ... )
        >>>
        >>> # Create from existing options
        >>> s3_opts = AwsStorageOptions(access_key_id="KEY")
        >>> options = StorageOptions(storage_options=s3_opts)
    """
⋮----
storage_options: BaseStorageOptions
⋮----
def __init__(self, **data: Any)
⋮----
"""Initialize storage options from arguments.

        Args:
            **data: Either:
                - protocol and configuration options
                - storage_options=pre-configured instance

        Raises:
            ValueError: If protocol missing or invalid

        Example:
            >>> # Direct protocol config
            >>> options = StorageOptions(
            ...     protocol="s3",
            ...     region="us-east-1"
            ... )
        """
protocol = data.get("protocol")
⋮----
storage_options = AwsStorageOptions(**data)
⋮----
storage_options = GitHubStorageOptions(**data)
⋮----
storage_options = GitLabStorageOptions(**data)
⋮----
storage_options = AzureStorageOptions(**data)
⋮----
storage_options = GcsStorageOptions(**data)
⋮----
storage_options = LocalStorageOptions(**data)
⋮----
@classmethod
    def from_yaml(cls, path: str, fs: AbstractFileSystem = None) -> "StorageOptions"
⋮----
"""Create storage options from YAML configuration.

        Args:
            path: Path to YAML configuration file
            fs: Filesystem for reading configuration

        Returns:
            StorageOptions: Configured storage options

        Example:
            >>> # Load from config file
            >>> options = StorageOptions.from_yaml("storage.yml")
            >>> print(options.storage_options.protocol)
            's3'
        """
⋮----
@classmethod
    def from_env(cls, protocol: str) -> "StorageOptions"
⋮----
"""Create storage options from environment variables.

        Args:
            protocol: Storage protocol to configure

        Returns:
            StorageOptions: Environment-configured options

        Example:
            >>> # Load AWS config from environment
            >>> options = StorageOptions.from_env("s3")
        """
⋮----
"""Create fsspec filesystem instance.

        Returns:
            AbstractFileSystem: Configured filesystem instance

        Example:
            >>> options = StorageOptions(protocol="file")
            >>> fs = options.to_filesystem()
            >>> files = fs.ls("/data")
        """
⋮----
def to_dict(self, protocol: bool = False) -> dict
⋮----
"""Convert storage options to dictionary.

        Args:
            protocol: Whether to include protocol in output

        Returns:
            dict: Storage options as dictionary

        Example:
            >>> options = StorageOptions(
            ...     protocol="s3",
            ...     region="us-east-1"
            ... )
            >>> print(options.to_dict())
            {'region': 'us-east-1'}
        """
⋮----
"""Get options formatted for object store clients.

        Args:
            with_conditional_put: Add etag-based conditional put support

        Returns:
            dict: Object store configuration dictionary

        Example:
            >>> options = StorageOptions(protocol="s3")
            >>> kwargs = options.to_object_store_kwargs()
            >>> store = ObjectStore(**kwargs)
        """
⋮----
def infer_protocol_from_uri(uri: str) -> str
⋮----
"""Infer the storage protocol from a URI string.

    Analyzes the URI to determine the appropriate storage protocol based on
    the scheme or path format.

    Args:
        uri: URI or path string to analyze. Examples:
            - "s3://bucket/path"
            - "gs://bucket/path"
            - "github://org/repo"
            - "/local/path"

    Returns:
        str: Inferred protocol identifier

    Example:
        >>> # S3 protocol
        >>> infer_protocol_from_uri("s3://my-bucket/data")
        's3'
        >>>
        >>> # Local file
        >>> infer_protocol_from_uri("/home/user/data")
        'file'
        >>>
        >>> # GitHub repository
        >>> infer_protocol_from_uri("github://microsoft/vscode")
        'github'
    """
⋮----
def storage_options_from_uri(uri: str) -> BaseStorageOptions
⋮----
"""Create storage options instance from a URI string.

    Infers the protocol and extracts relevant configuration from the URI
    to create appropriate storage options.

    Args:
        uri: URI string containing protocol and optional configuration.
            Examples:
            - "s3://bucket/path"
            - "gs://project/bucket/path"
            - "github://org/repo"

    Returns:
        BaseStorageOptions: Configured storage options instance

    Example:
        >>> # S3 options
        >>> opts = storage_options_from_uri("s3://my-bucket/data")
        >>> print(opts.protocol)
        's3'
        >>>
        >>> # GitHub options
        >>> opts = storage_options_from_uri("github://microsoft/vscode")
        >>> print(opts.org)
        'microsoft'
        >>> print(opts.repo)
        'vscode'
    """
protocol = infer_protocol_from_uri(uri)
options = infer_storage_options(uri)
⋮----
parts = uri.replace("github://", "").split("/")
⋮----
parts = uri.replace("gitlab://", "").split("/")
⋮----
"""Merge multiple storage options into a single configuration.

    Combines options from multiple sources with control over precedence.

    Args:
        *options: Storage options to merge. Can be:
            - BaseStorageOptions instances
            - Dictionaries of options
            - None values (ignored)
        overwrite: Whether later options override earlier ones

    Returns:
        BaseStorageOptions: Combined storage options

    Example:
        >>> # Merge with overwrite
        >>> base = AwsStorageOptions(
        ...     region="us-east-1",
        ...     access_key_id="OLD_KEY"
        ... )
        >>> override = {"access_key_id": "NEW_KEY"}
        >>> merged = merge_storage_options(base, override)
        >>> print(merged.access_key_id)
        'NEW_KEY'
        >>>
        >>> # Preserve existing values
        >>> merged = merge_storage_options(
        ...     base,
        ...     override,
        ...     overwrite=False
        ... )
        >>> print(merged.access_key_id)
        'OLD_KEY'
    """
result = {}
protocol = None
⋮----
opts = opts.to_dict(with_protocol=True)
⋮----
protocol = opts["protocol"]
⋮----
protocol = "file"
````

## File: src/flowerpower/job_queue/apscheduler/__init__.py
````python
__all__ = [
````

## File: src/flowerpower/job_queue/rq/__init__.py
````python
__all__ = [
````

## File: examples/hello-world/conf/pipelines/hello_world.yml
````yaml
adapter:
  hamilton_tracker:
    capture_data_statistics: true
    dag_name: null
    max_dict_length_capture: 10
    max_list_length_capture: 50
    project_id: null
    tags: {}
  mlflow:
    experiment_description: null
    experiment_name: null
    experiment_tags: {}
    run_description: null
    run_id: null
    run_name: null
    run_tags: {}
params: 
  avg_x_wk_spend:
    rolling: 3
  spend_zero_mean:
    offset: 0
run:
  cache: false
  config: 
    range: 10_000
  executor:
    max_workers: 40
    num_cpus: 8
    type: threadpool
  final_vars:
    - spend
    - signups
    - avg_x_wk_spend
    - spend_per_signup
    - spend_zero_mean_unit_variance
  inputs: {}
  log_level: null
  with_adapter:
    future: false
    mlflow: false
    opentelemetry: false
    progressbar: false
    ray: false
    tracker: false
schedule:
  cron: "* * * * *"
  interval: null
  date: null
````

## File: examples/hello-world/pipelines/hello_world.py
````python
# FlowerPower pipeline hello_world.py
# Created on 2024-10-26 12:44:27
⋮----
PARAMS = Config.load(
⋮----
@config.when(range=10_000)
def spend__10000() -> pd.Series
⋮----
"""Returns a series of spend data."""
# time.sleep(2)
⋮----
@config.when(range=10_000)
def signups__10000() -> pd.Series
⋮----
"""Returns a series of signups data."""
⋮----
@config.when(range=1_000)
def spend__1000() -> pd.Series
⋮----
@config.when(range=1_000)
def signups__1000() -> pd.Series
⋮----
)  # (**{"avg_x_wk_spend": {"rolling": value(3)}})  #
def avg_x_wk_spend(spend: pd.Series, rolling: int) -> pd.Series
⋮----
"""Rolling x week average spend."""
⋮----
def spend_per_signup(spend: pd.Series, signups: pd.Series) -> pd.Series
⋮----
"""The cost per signup in relation to spend."""
⋮----
def spend_mean(spend: pd.Series) -> float
⋮----
"""Shows function creating a scalar. In this case it computes the mean of the entire column."""
⋮----
)  # (**{"spend_zero_mean": {"offset": value(0)}})  #
def spend_zero_mean(spend: pd.Series, spend_mean: float, offset: int) -> pd.Series
⋮----
"""Shows function that takes a scalar. In this case to zero mean spend."""
⋮----
def spend_std_dev(spend: pd.Series) -> float
⋮----
"""Function that computes the standard deviation of the spend column."""
⋮----
"""Function showing one way to make spend have zero mean and unit variance."""
````

## File: src/flowerpower/cli/mqtt.py
````python
app = typer.Typer(help="MQTT management commands")
⋮----
"""Start an MQTT client to listen to messages on a topic

    The connection to the MQTT broker is established using the provided configuration o a
    MQTT event broker defined in the project configuration file `conf/project.yml`.
    If not configuration is found, you have to provide the connection parameters,
    such as `host`, `port`, `username`, and `password`.

    The `on_message` module should contain a function `on_message` that will be called
    with the message payload as argument.

    Args:
        on_message: Name of the module containing the on_message function
        topic: MQTT topic to listen to
        base_dir: Base directory for the module
        host: MQTT broker host
        port: MQTT broker port
        username: MQTT broker username
        password: MQTT broker password

    Examples:
        $ flowerpower mqtt start_listener --on-message my_module --topic my_topic --base-dir /path/to/module
    """
⋮----
on_message_module = importlib.import_module(on_message)
⋮----
"""Run a pipeline on a message

    This command sets up an MQTT listener that executes a pipeline whenever a message is
    received on the specified topic. The pipeline can be configured to retry on failure
    using exponential backoff with jitter for better resilience.

    Args:
        name: Name of the pipeline
        topic: MQTT topic to listen to
        executor: Name of the executor
        base_dir: Base directory for the pipeline
        inputs: Inputs as JSON or key=value pairs or dict string
        final_vars: Final variables as JSON or list
        config: Config for the hamilton pipeline executor
        with_tracker: Enable tracking with hamilton ui
        with_opentelemetry: Enable OpenTelemetry tracing
        with_progressbar: Enable progress bar
        storage_options: Storage options as JSON, dict string or key=value pairs
        as_job: Run as a job in the scheduler
        host: MQTT broker host
        port: MQTT broker port
        username: MQTT broker username
        password: MQTT broker password
        clean_session: Whether to start a clean session with the broker
        qos: MQTT Quality of Service level (0, 1, or 2)
        client_id: Custom MQTT client identifier
        client_id_suffix: Optional suffix to append to client_id
        config_hook: Function to process incoming messages into pipeline config
        max_retries: Maximum number of retry attempts if pipeline execution fails
        retry_delay: Base delay between retries in seconds
        jitter_factor: Random factor (0-1) applied to delay for jitter

    Examples:
        # Basic usage with a specific topic
        $ flowerpower mqtt run-pipeline-on-message my_pipeline --topic sensors/data

        # Configure retries for resilience
        $ flowerpower mqtt run-pipeline-on-message my_pipeline --topic sensors/data --max-retries 5 --retry-delay 2.0

        # Run as a job with custom MQTT settings
        $ flowerpower mqtt run-pipeline-on-message my_pipeline --topic events/process --as-job --qos 2 --host mqtt.example.com

        # Use a config hook to process messages
        $ flowerpower mqtt run-pipeline-on-message my_pipeline --topic data/incoming --config-hook process_message


    """
⋮----
parsed_inputs = parse_dict_or_list_param(inputs, "dict")
parsed_config = parse_dict_or_list_param(config, "dict")
parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
⋮----
config_hook_function = None
⋮----
config_hook_function = load_hook(name, config_hook, base_dir, storage_options)
````

## File: src/flowerpower/cli/utils.py
````python
# Parse additional parameters
def parse_param_dict(param_str: str | None) -> dict
⋮----
"""Helper to parse parameter dictionaries"""
⋮----
"""
    Parse dictionary or list parameters from various input formats.

    Supports:
    - JSON string
    - Python literal (dict/list)
    - Comma-separated key=value pairs (for dicts)
    - Comma-separated values (for lists)
    - List-like string with or without quotes

    Args:
        value (str, optional): Input string to parse
        param_type (str): Type of parameter to parse ('dict' or 'list')

    Returns:
        dict | list | None: Parsed parameter or None if parsing fails
    """
⋮----
def convert_string_booleans(obj)
⋮----
# Try parsing as JSON first
parsed = json.loads(value)
⋮----
# Try parsing as Python literal
parsed = ast.literal_eval(value)
⋮----
# Validate type
⋮----
# For dicts, try parsing as comma-separated key=value pairs
⋮----
parsed = dict(
⋮----
# For lists, try multiple parsing strategies
⋮----
# Remove surrounding square brackets and whitespace
value = value.strip()
⋮----
value = value[1:-1].strip()
⋮----
# Parse list-like string with or without quotes
# This regex handles: a,b | 'a','b' | "a","b" | a, b | 'a', 'b'
list_items = re.findall(r"['\"]?(.*?)['\"]?(?=\s*,|\s*$)", value)
⋮----
# Remove any empty strings and strip whitespace
parsed = [item.strip() for item in list_items if item.strip()]
⋮----
# If all parsing fails, log warning and return None
⋮----
"""
    Load a hook function from a specified path.
    This function dynamically imports the module and retrieves the function


    Args:
        pipeline_name (str): Name of the pipeline
        function_path (str): Path to the function in the format 'module_name.function_name'
        base_dir (str, optional): Base directory for the pipeline
        storage_options (str, optional): Storage options as JSON or dict string
    Returns:
        Callable: The loaded hook function
    """
⋮----
path_segments = function_path.rsplit(".", 2)
⋮----
# If the function path is in the format 'module_name.function_name'
⋮----
module_path = ""
⋮----
# If the function path is in the format 'package.[subpackage.]module_name.function_name'
⋮----
hook_module = importlib.import_module(module_name)
hook_function = getattr(hook_module, function_name)
````

## File: src/flowerpower/utils/logging.py
````python
from ..settings import LOG_LEVEL  # Import the setting
⋮----
def setup_logging(level: str = LOG_LEVEL) -> None
⋮----
"""
    Configures the Loguru logger.

    Removes the default handler and adds a new one targeting stderr
    with the level specified by the FP_LOG_LEVEL setting.
    """
logger.remove()  # Remove the default handler added by Loguru
⋮----
level=level.upper(),  # Use the level from the parameter, ensure it's uppercase
format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",  # Example format
⋮----
# logger.info(f"Log level set to: {FP_LOG_LEVEL.upper()}")
````

## File: src/flowerpower/utils/templates.py
````python
PIPELINE_PY_TEMPLATE = """# FlowerPower pipeline {name}.py
⋮----
HOOK_TEMPLATE__MQTT_BUILD_CONFIG = '''
````

## File: src/flowerpower/flowerpower.py
````python
name = str(Path.cwd().name)
base_dir = str(Path.cwd().parent)
⋮----
base_dir = str(Path.cwd())
⋮----
fs = get_filesystem(
⋮----
cfg = ProjectConfig.load(name=name, job_queue_type=job_queue_type, fs=fs)
⋮----
# def find_pipelines(cls):
#     """Find all pipeline modules in the project's pipelines directory."""
#     pipeline_path = Path("pipelines")
#     if not pipeline_path.exists():
#         return []
⋮----
#     pipelines = []
#     for file in pipeline_path.glob("*.py"):
#         if file.name.startswith("_"):
#             continue
⋮----
#         module_name = file.stem
#         try:
#             pipeline = Pipeline(module_name)
#             pipelines.append(pipeline)
#         except Exception as e:
#             rich.print(f"[red]Error loading pipeline {module_name}: {str(e)}[/red]")
⋮----
#     return pipelines
⋮----
# def list_pipelines():
#     pipelines = Pipeline.find_pipelines()
#     if not pipelines:
#         rich.print("\n📭 [yellow]No pipelines found in this project[/yellow]\n")
#         return
⋮----
#     rich.print("\n🌸 [bold magenta]Available Pipelines:[/bold magenta]\n")
#     table = rich.table.Table(show_header=True, header_style="bold cyan")
#     table.add_column("Name")
#     table.add_column("Description")
#     table.add_column("Status")
⋮----
#     for pipeline in pipelines:
#         status = (
#             "[green]Active[/green]" if pipeline.is_active() else "[red]Inactive[/red]"
#         )
#         table.add_row(
#             pipeline.name, pipeline.description or "[dim]No description[/dim]", status
⋮----
#     rich.print(table)
#     rich.print()
````

## File: docker/docker-compose.yml
````yaml
version: "3.8"

## This docker-compose file can be used to run and test FlowerPower locally.
## It is not intended to be used in production.

## The following services are included:
## - python-dev container
## - Code-Server
## - Minio
## - MQTT (Nanomq and Mosquitto)
## - Redis
## - Dragonfly
## - MongoDB
## - NodeRed
## - PostgreSQL
## - Hamilton UI (Backend and Frontend)

services:
  # JupyCode
  # This is a custom image based on JupyterLab that includes VSCodeServer
  # It can be used as the test environment for FlowerPower

  python-dev-worker:
    image: python-dev-worker
    container_name: python-dev-worker
    build:
      context: python-worker
      dockerfile: Dockerfile.dev
    volumes:
      - python-worker:/app # Mount your code directory
    networks:
      - flowerpower-net
    restart: unless-stopped

  # Code-Server
  codeserver:
    image: lscr.io/linuxserver/code-server:latest
    container_name: codeserver
    env_file:
      - .env
    environment:
      - PUID=1000 # Use your user's ID (run `id -u` on VPS)
      - PGID=1000 # Use your user's group ID (run `id -g` on VPS)
      - TZ=Europe/Berlin
      #- PASSWORD=$CS_PW # Set a strong password in the .env file
      #- SUDO_PASSWORD=$CS_SUDO_PW # If you need sudo within code-server
      # - PROXY_DOMAIN=code.yourdomain.com # If using Caddy subdomains
      #- EXTENSIONS_GALLERY=$CS_EXTENSIONS_GALLARY
    volumes:
      - codeserver_config:/config # Persist code-server config
      # --- Option 2: Mount Docker socket to attach to python-dev (more complex/risky) ---
      - /var/run/docker.sock:/var/run/docker.sock # Mount Docker socket
      # You might need another volume to install docker cli if not in base image
    #ports:
    #  - "8443:8443" # Expose code-server port
    restart: unless-stopped
    networks:
      - flowerpower-net # Connect to Caddy's network

  # Minio
  # Often times FlowerPower pipelines will read and/or write to S3.
  # Minio is a local S3 compatible storage solution.  
  minio:
    image: minio/minio
    #ports:
    #  - 9000:9000
    #  - 9001:9001
    environment:
      MINIO_ACCESS_KEY: minio
      MINIO_SECRET_KEY: minio1234
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    networks:
      - flowerpower-net

  # MQTT 
  # When using APScheduler as the FlowerPower worker, MQTT can be used as a event broker
  # nanomq
  mqtt-nanomq:
    image: emqx/nanomq
    ports:
      - 1884:1883
      - 8084:8083
      - 8884:8883
    networks:
      - flowerpower-net

  # mosquitto
  mqtt-mosquitto:
    image: eclipse-mosquitto
    ports:
     - 1883:1883
    command: mosquitto -c /mosquitto/config/mosquitto.conf
  
  #mqtt:
  #  image: emqx/nanomq
  #  ports:
  #    - 1883:1883
  #    - 8083:8083
  #    - 8883:8883
    networks:
      - flowerpower-net

  # Redis
  # When using APScheduler as the FlowerPower worker, Redis can be used as a event broker
  # When using RQ as the FlowerPower worker, Redis is used as the task queue
  # Redis
  redis:
    image: redis
    ports:
     - 6379:6379
    networks:
      - flowerpower-net

  # Valkey - a Redis compatible key-value store
  valkey:
    image: valkey/valkey
    ports:
     - 6379:6379
    networks:
      - flowerpower-net

  # Dragonfly - a Redis compatible key-value store
  dragonfly:
    image: docker.dragonflydb.io/dragonflydb/dragonfly
    ulimits:
      memlock: -1
    ports:
     - 6379:6379
    networks:
      - flowerpower-net

  # MongoDB
  # When using APScheduler as the FlowerPower worker, MongoDB can be used as a data store
  mongodb:
    image: mongo
    ports:
     - 27017:27017
    networks:
      - flowerpower-net

  # PostgreSQL
  # When using RQ as the FlowerPower worker, PostgreSQL can be used as a data store and event broker
  postgres:
    image: postgres
    environment:
      - POSTGRES_HOST_AUTH_METHOD=trust
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
     - 5432:5432
    networks:
      - flowerpower-net

  ## Hamilton UI ##
  # Hamilton UI is a web-based interface for Hamilton, the data pipeline framework used in FlowerPower
  # PosgreSQL
  postgres-hamilton:
    image: postgres
    container_name: hamilton-postgres
    volumes:
      - hamilton_pg_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=flowerpower
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - PGPORT=5433
    #ports:
    #  - 5433:5433
    networks:
      - flowerpower-net

  # Backend
  backend:
    container_name: hamilton-ui-backend
    image: dagworks/ui-backend:latest

    entrypoint: [ "/bin/bash", "-c", "cd /code/server && ls && ./entrypoint.sh" ]
    volumes:
      - hamilton_ui_data:/data/
    ports:
     - 8241:8241
    #env_file: .env
    environment:
      - DB_HOST=postgres-hamilton
      - DB_PORT=5433
      - DB_NAME=flowerpower
      - DB_USER=postgres
      - DB_PASSWORD=password # Purely for local! Do not deploy to production!
      - HAMILTON_BLOB_STORE=local
      - HAMILTON_ENV=local # local env
      - HAMILTON_LOCAL_BLOB_DIR=/data/blobs # TODO -- set this up to be a better one
      - DJANGO_SECRET_KEY=do_not_use_in_production
      - HAMILTON_TELEMETRY_ENABLED=false #${HAMILTON_TELEMETRY_ENABLED}
      - HAMILTON_AUTH_MODE=permissive
      - HAMILTON_ALLOWED_HOSTS=*
      - HAMILTON_CAPTURE_DATA_STATISTICS=false
      - HAMILTON_MAX_LIST_LENGTH_CAPTURE
      - HAMILTON_MAX_DICT_LENGTH_CAPTURE
    networks:
      - flowerpower-net
    restart: unless-stopped

  # Frontend
  frontend:
    container_name: hamilton-ui-frontend
    image: dagworks/ui-frontend:latest
    #ports:
    #  - 8242:8242
    environment:
      - NGINX_PORT=8242
      - NODE_ENV=development
      - REACT_APP_AUTH_MODE=local
      - REACT_APP_USE_POSTHOG=false
      - REACT_APP_API_URL=http://backend:8241
    networks:
      - flowerpower-net
    depends_on:
      - backend
    restart: unless-stopped

  caddy:
    image: caddy:latest
    container_name: caddyP
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp" # Needed for HTTP/3
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile # Mount your Caddy config
      - caddy_data:/data # Persist Caddy's state (certs etc.)
      - caddy_config:/config
    restart: unless-stopped
    networks:
      - flowerpower-net
    environment:
      - HOSTNAME=flowerpower.local

  dockge:
    image: louislam/dockge:latest
    container_name: dockge
    #ports:
    #  - "5001:5001"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - dockge_data:/data
    networks:
      - flowerpower-net
    restart: unless-stopped

networks:
  flowerpower-net:
    driver: bridge

volumes:
  codeserver_config:
  caddy_data:
  caddy_config:
  python-worker:
  minio_data:
  nodered_data:
  postgres_data:
  hamilton_ui_data:
  hamilton_pg_data:
  dockge_data:
````

## File: src/flowerpower/cfg/pipeline/adapter.py
````python
class HamiltonTracerConfig(BaseConfig)
⋮----
project_id: int | None = msgspec.field(default=None)
dag_name: str | None = msgspec.field(default=None)
tags: dict = msgspec.field(default_factory=dict)
capture_data_statistics: bool = msgspec.field(
max_list_length_capture: int = msgspec.field(
max_dict_length_capture: int = msgspec.field(
⋮----
def __post_init__(self)
⋮----
class MLFlowConfig(BaseConfig)
⋮----
experiment_name: str | None = msgspec.field(default=None)
experiment_tags: dict | None = msgspec.field(default_factory=dict)
experiment_description: str | None = msgspec.field(default=None)
run_id: str | None = msgspec.field(default=None)
run_name: str | None = msgspec.field(default=None)
run_tags: dict | None = msgspec.field(default_factory=dict)
run_description: str | None = msgspec.field(default=None)
⋮----
# class OpenLineageConfig(BaseConfig):
#     namespace : str | None = msgspec.field(default=None)
#     job_name : str | None = msgspec.field(default=None)
⋮----
class AdapterConfig(BaseConfig)
⋮----
hamilton_tracker: HamiltonTracerConfig = msgspec.field(
mlflow: MLFlowConfig = msgspec.field(default_factory=MLFlowConfig)
# openlineage: OpenLineageConfig | dict = msgspec.field(default_factory=OpenLineageConfig)
````

## File: src/flowerpower/cfg/pipeline/schedule.py
````python
# class ScheduleCronTriggerConfig(BaseConfig):
#     year: str | int | None = None
#     month: str | int | None = None
#     week: str | int | None = None
#     day: str | int | None = None
#     day_of_week: str | int | None = None
#     hour: str | int | None = None
#     minute: str | int | None = None
#     second: str | int | None = None
#     start_time: dt.datetime | None = None
#     end_time: dt.datetime | None = None
#     timezone: str | None = None
#     crontab: str | None = None
⋮----
# class ScheduleIntervalTriggerConfig(BaseConfig):
#     weeks: int | float | None = None
#     days: int | float | None = None
#     hours: int | float | None = None
#     minutes: int | float | None = None
#     seconds: int | float | None = None
#     microseconds: int | float | None = None
⋮----
# class ScheduleCalendarTriggerConfig(BaseConfig):
#     years: int | float | None = None
#     months: int | float | None = None
⋮----
#     hour: int | float | None = None
#     minute: int | float | None = None
#     second: int | float | None = None
#     start_date: dt.datetime | None = None
#     end_date: dt.datetime | None = None
⋮----
# class ScheduleDateTriggerConfig(BaseConfig):
#     run_time: dt.datetime | None = None
⋮----
class ScheduleConfig(BaseConfig)
⋮----
cron: str | dict | None = msgspec.field(default=None)
interval: str | int | dict | None = msgspec.field(default=None)
date: str | None = msgspec.field(default=None)
⋮----
def __post_init__(self)
⋮----
# class ScheduleConfig(BaseConfig):
#     run: ScheduleRunConfig = msgspec.field(default_factory=ScheduleRunConfig)
#     trigger: ScheduleTriggerConfig = msgspec.field(
#         default_factory=ScheduleTriggerConfig
#     )
````

## File: src/flowerpower/cfg/project/adapter.py
````python
class HamiltonTrackerConfig(BaseConfig)
⋮----
username: str | None = msgspec.field(default=None)
api_url: str = msgspec.field(default=settings.HAMILTON_API_URL)
ui_url: str = msgspec.field(default=settings.HAMILTON_UI_URL)
api_key: str | None = msgspec.field(default=None)
verify: bool = msgspec.field(default=False)
⋮----
class MLFlowConfig(BaseConfig)
⋮----
tracking_uri: str | None = msgspec.field(default=None)
registry_uri: str | None = msgspec.field(default=None)
artifact_location: str | None = msgspec.field(default=None)
⋮----
class OpenTelemetryConfig(BaseConfig)
⋮----
host: str = msgspec.field(default="localhost")
port: int = msgspec.field(default=6831)
⋮----
# class OpenLineageConfig(BaseConfig):
#     from openlineage.client import OpenLineageClientOptions
#     from openlineage.client.transport import Transport
#     from openlineage.client.transport import TransportFactory
#     url: str | None = msgspec.field(default=None)
#     options: OpenLineageClientOptions | None = msgspec.field(
#         default=None)
#     transport: Transport | None = msgspec.field(default=None)
#     factory: TransportFactory | None = msgspec.field(
⋮----
#     config: dict | None = msgspec.field(default=None)
⋮----
class RayConfig(BaseConfig)
⋮----
ray_init_config: dict | None = msgspec.field(default=None)
shutdown_ray_on_completion: bool = msgspec.field(default=False)
⋮----
def __post_init__(self)
⋮----
class AdapterConfig(BaseConfig)
⋮----
hamilton_tracker: HamiltonTrackerConfig = msgspec.field(
mlflow: MLFlowConfig = msgspec.field(default_factory=MLFlowConfig)
ray: RayConfig = msgspec.field(default_factory=RayConfig)
opentelemetry: OpenTelemetryConfig = msgspec.field(
````

## File: src/flowerpower/fs/base.py
````python
class FileNameCacheMapper(AbstractCacheMapper)
⋮----
"""Maps remote file paths to local cache paths while preserving directory structure.

    This cache mapper maintains the original file path structure in the cache directory,
    creating necessary subdirectories as needed.

    Attributes:
        directory (str): Base directory for cached files

    Example:
        >>> # Create cache mapper for S3 files
        >>> mapper = FileNameCacheMapper("/tmp/cache")
        >>>
        >>> # Map remote path to cache path
        >>> cache_path = mapper("bucket/data/file.csv")
        >>> print(cache_path)  # Preserves structure
        'bucket/data/file.csv'
    """
⋮----
def __init__(self, directory: str)
⋮----
"""Initialize cache mapper with base directory.

        Args:
            directory: Base directory where cached files will be stored
        """
⋮----
def __call__(self, path: str) -> str
⋮----
"""Map remote file path to cache file path.

        Creates necessary subdirectories in the cache directory to maintain
        the original path structure.

        Args:
            path: Original file path from remote filesystem

        Returns:
            str: Cache file path that preserves original structure

        Example:
            >>> mapper = FileNameCacheMapper("/tmp/cache")
            >>> # Maps maintain directory structure
            >>> print(mapper("data/nested/file.txt"))
            'data/nested/file.txt'
        """
⋮----
class MonitoredSimpleCacheFileSystem(SimpleCacheFileSystem)
⋮----
"""Enhanced caching filesystem with monitoring and improved path handling.

    This filesystem extends SimpleCacheFileSystem to provide:
    - Verbose logging of cache operations
    - Improved path mapping for cache files
    - Enhanced synchronization capabilities
    - Better handling of parallel operations

    Attributes:
        _verbose (bool): Whether to print verbose cache operations
        _mapper (FileNameCacheMapper): Maps remote paths to cache paths
        storage (list[str]): List of cache storage locations
        fs (AbstractFileSystem): Underlying filesystem being cached

    Example:
        >>> from fsspec import filesystem
        >>> # Create monitored cache for S3
        >>> s3 = filesystem("s3", key="ACCESS_KEY", secret="SECRET_KEY")
        >>> cached_fs = MonitoredSimpleCacheFileSystem(
        ...     fs=s3,
        ...     cache_storage="/tmp/s3_cache",
        ...     verbose=True
        ... )
        >>>
        >>> # Read file (downloads and caches)
        >>> with cached_fs.open("bucket/data.csv") as f:
        ...     data = f.read()
        Downloading s3://bucket/data.csv
        >>>
        >>> # Second read uses cache
        >>> with cached_fs.open("bucket/data.csv") as f:
        ...     data = f.read()  # No download message
    """
⋮----
def __init__(self, **kwargs: Any)
⋮----
"""Initialize monitored cache filesystem.

        Args:
            **kwargs: Configuration options including:
                fs (AbstractFileSystem): Filesystem to cache
                cache_storage (str): Cache directory path
                verbose (bool): Enable verbose logging
                And any other SimpleCacheFileSystem options

        Example:
            >>> # Cache with custom settings
            >>> cached_fs = MonitoredSimpleCacheFileSystem(
            ...     fs=remote_fs,
            ...     cache_storage="/tmp/cache",
            ...     verbose=True,
            ...     same_names=True  # Use original filenames
            ... )
        """
⋮----
def _check_file(self, path: str) -> str | None
⋮----
"""Check if file exists in cache and download if needed.

        Args:
            path: Path to file in the remote filesystem

        Returns:
            str | None: Path to cached file if found/downloaded, None otherwise

        Example:
            >>> fs = MonitoredSimpleCacheFileSystem(
            ...     fs=remote_fs,
            ...     cache_storage="/tmp/cache"
            ... )
            >>> cached_path = fs._check_file("data.csv")
            >>> print(cached_path)
            '/tmp/cache/data.csv'
        """
⋮----
cache_path = self._mapper(path)
⋮----
fn = posixpath.join(storage, cache_path)
⋮----
def size(self, path: str) -> int
⋮----
"""Get size of file in bytes.

        Checks cache first, falls back to remote filesystem.

        Args:
            path: Path to file

        Returns:
            int: Size of file in bytes

        Example:
            >>> fs = MonitoredSimpleCacheFileSystem(
            ...     fs=remote_fs,
            ...     cache_storage="/tmp/cache"
            ... )
            >>> size = fs.size("large_file.dat")
            >>> print(f"File size: {size} bytes")
        """
cached_file = self._check_file(self._strip_protocol(path))
⋮----
def sync_cache(self, reload: bool = False) -> None
⋮----
"""Synchronize cache with remote filesystem.

        Downloads all files in remote path to cache if not present.

        Args:
            reload: Whether to force reload all files, ignoring existing cache

        Example:
            >>> fs = MonitoredSimpleCacheFileSystem(
            ...     fs=remote_fs,
            ...     cache_storage="/tmp/cache"
            ... )
            >>> # Initial sync
            >>> fs.sync_cache()
            >>>
            >>> # Force reload all files
            >>> fs.sync_cache(reload=True)
        """
⋮----
content = self.glob("**/*")
⋮----
def __getattribute__(self, item)
⋮----
# new items
⋮----
# previous
⋮----
# all the methods defined in this class. Note `open` here, since
# it calls `_open`, but is actually in superclass
⋮----
# property
⋮----
# class attributes
⋮----
d = object.__getattribute__(self, "__dict__")
fs = d.get("fs", None)  # fs is not immediately defined
⋮----
# attribute of instance
⋮----
# attributed belonging to the target filesystem
cls = type(fs)
m = getattr(cls, item)
⋮----
# instance method
⋮----
return m  # class method or attribute
⋮----
# attributes of the superclass, while target is being set up
⋮----
class GitLabFileSystem(AbstractFileSystem)
⋮----
"""FSSpec-compatible filesystem interface for GitLab repositories.

    Provides access to files in GitLab repositories through the GitLab API,
    supporting read operations with authentication.

    Attributes:
        project_name (str): Name of the GitLab project
        project_id (str): ID of the GitLab project
        access_token (str): GitLab personal access token
        branch (str): Git branch to read from
        base_url (str): GitLab instance URL

    Example:
        >>> # Access public project
        >>> fs = GitLabFileSystem(
        ...     project_name="my-project",
        ...     access_token="glpat-xxxx"
        ... )
        >>>
        >>> # Read file contents
        >>> with fs.open("path/to/file.txt") as f:
        ...     content = f.read()
        >>>
        >>> # List directory
        >>> files = fs.ls("path/to/dir")
        >>>
        >>> # Access enterprise GitLab
        >>> fs = GitLabFileSystem(
        ...     project_id="12345",
        ...     access_token="glpat-xxxx",
        ...     base_url="https://gitlab.company.com",
        ...     branch="develop"
        ... )
    """
⋮----
"""Initialize GitLab filesystem.

        Args:
            project_name: Name of the GitLab project. Required if project_id not provided.
            project_id: ID of the GitLab project. Required if project_name not provided.
            access_token: GitLab personal access token for authentication.
                Required for private repositories.
            branch: Git branch to read from. Defaults to "main".
            base_url: GitLab instance URL. Defaults to "https://gitlab.com".
            **kwargs: Additional arguments passed to AbstractFileSystem.

        Raises:
            ValueError: If neither project_name nor project_id is provided
            requests.RequestException: If GitLab API request fails
        """
⋮----
def _validate_init(self) -> None
⋮----
"""Validate initialization parameters.

        Ensures that either project_id or project_name is provided.

        Raises:
            ValueError: If neither project_id nor project_name is provided
        """
⋮----
def _get_project_id(self) -> str
⋮----
"""Retrieve project ID from GitLab API using project name.

        Makes an API request to search for projects and find the matching project ID.

        Returns:
            str: The GitLab project ID

        Raises:
            ValueError: If project not found
            requests.RequestException: If API request fails
        """
url = f"{self.base_url}/api/v4/projects"
headers = {"PRIVATE-TOKEN": self.access_token}
params = {"search": self.project_name}
response = requests.get(url, headers=headers, params=params)
⋮----
projects = response.json()
⋮----
def _open(self, path: str, mode: str = "rb", **kwargs) -> MemoryFile
⋮----
"""Open a file from GitLab repository.

        Retrieves file content from GitLab API and returns it as a memory file.

        Args:
            path: Path to file within repository
            mode: File open mode. Only "rb" (read binary) is supported.
            **kwargs: Additional arguments (unused)

        Returns:
            MemoryFile: File-like object containing file content

        Raises:
            NotImplementedError: If mode is not "rb"
            requests.RequestException: If API request fails

        Example:
            >>> fs = GitLabFileSystem(project_id="12345", access_token="glpat-xxxx")
            >>> with fs.open("README.md") as f:
            ...     content = f.read()
            ...     print(content.decode())
        """
⋮----
url = (
⋮----
response = requests.get(url, headers=headers)
⋮----
file_content = base64.b64decode(response.json()["content"])
⋮----
def _ls(self, path: str, detail: bool = False, **kwargs) -> list[str] | list[dict]
⋮----
"""List contents of a directory in GitLab repository.

        Args:
            path: Directory path within repository
            detail: Whether to return detailed information about each entry.
                If True, returns list of dicts with file metadata.
                If False, returns list of filenames.
            **kwargs: Additional arguments (unused)

        Returns:
            list[str] | list[dict]: List of file/directory names or detailed info

        Raises:
            requests.RequestException: If API request fails

        Example:
            >>> fs = GitLabFileSystem(project_id="12345", access_token="glpat-xxxx")
            >>> # List filenames
            >>> files = fs.ls("docs")
            >>> print(files)
            ['README.md', 'API.md']
            >>>
            >>> # List with details
            >>> details = fs.ls("docs", detail=True)
            >>> for item in details:
            ...     print(f"{item['name']}: {item['type']}")
        """
url = f"{self.base_url}/api/v4/projects/{self.project_id}/repository/tree?path={path}&ref={self.branch}"
⋮----
files = response.json()
⋮----
_ = e
⋮----
# Original ls Methode speichern
dirfs_ls_o = DirFileSystem.ls
mscf_ls_o = MonitoredSimpleCacheFileSystem.ls
⋮----
# Neue ls Methode definieren
def dir_ls_p(self, path, detail=False, **kwargs)
⋮----
def mscf_ls_p(self, path, detail=False, **kwargs)
⋮----
# patchen
⋮----
"""Get a filesystem instance based on path or configuration.

    This function creates and configures a filesystem instance based on the provided path
    and options. It supports various filesystem types including local, S3, GCS, Azure,
    and Git-based filesystems.

    Args:
        path: URI or path to the filesystem location. Examples:
            - Local: "/path/to/data"
            - S3: "s3://bucket/path"
            - GCS: "gs://bucket/path"
            - Azure: "abfs://container/path"
            - GitHub: "github://org/repo/path"
        storage_options: Configuration options for the filesystem. Can be:
            - BaseStorageOptions object with protocol-specific settings
            - Dictionary of key-value pairs for authentication/configuration
            - None to use environment variables or default credentials
        dirfs: Whether to wrap filesystem in DirFileSystem for path-based operations.
            Set to False when you need direct protocol-specific features.
        cached: Whether to enable local caching of remote files.
            Useful for frequently accessed remote files.
        cache_storage: Directory path for cached files. Defaults to path-based location
            in current directory if not specified.
        fs: Existing filesystem instance to wrap with caching or dirfs.
            Use this to customize an existing filesystem instance.
        **storage_options_kwargs: Additional keyword arguments for storage options.
            Alternative to passing storage_options dictionary.

    Returns:
        AbstractFileSystem: Configured filesystem instance with requested features.

    Raises:
        ValueError: If storage protocol or options are invalid
        FSSpecError: If filesystem initialization fails
        ImportError: If required filesystem backend is not installed

    Example:
        >>> # Local filesystem
        >>> fs = get_filesystem("/path/to/data")
        >>>
        >>> # S3 with credentials
        >>> fs = get_filesystem(
        ...     "s3://bucket/data",
        ...     storage_options={
        ...         "key": "ACCESS_KEY",
        ...         "secret": "SECRET_KEY"
        ...     }
        ... )
        >>>
        >>> # Cached GCS filesystem
        >>> fs = get_filesystem(
        ...     "gs://bucket/data",
        ...     storage_options=GcsStorageOptions(
        ...         token="service_account.json"
        ...     ),
        ...     cached=True,
        ...     cache_storage="/tmp/gcs_cache"
        ... )
        >>>
        >>> # Azure with environment credentials
        >>> fs = get_filesystem(
        ...     "abfs://container/data",
        ...     storage_options=AzureStorageOptions.from_env()
        ... )
        >>>
        >>> # Wrap existing filesystem
        >>> base_fs = filesystem("s3", key="ACCESS", secret="SECRET")
        >>> cached_fs = get_filesystem(
        ...     fs=base_fs,
        ...     cached=True
        ... )
    """
⋮----
pp = infer_storage_options(str(path) if isinstance(path, Path) else path)
protocol = pp.get("protocol")
⋮----
fs = filesystem(protocol)
⋮----
fs = DirFileSystem(path=path, fs=fs)
⋮----
host = pp.get("host", "")
path = pp.get("path", "").lstrip("/")
⋮----
path = posixpath.join(host, path)
⋮----
storage_options = storage_options_from_dict(protocol, storage_options)
⋮----
storage_options = storage_options_from_dict(protocol, storage_options_kwargs)
⋮----
fs = storage_options.to_filesystem()
⋮----
cache_storage = (Path.cwd() / path).as_posix()
fs = MonitoredSimpleCacheFileSystem(fs=fs, cache_storage=cache_storage)
````

## File: src/flowerpower/fs/ext.py
````python
duckdb = None
⋮----
ParquetDataset = None
⋮----
def path_to_glob(path: str, format: str | None = None) -> str
⋮----
"""Convert a path to a glob pattern for file matching.

    Intelligently converts paths to glob patterns that match files of the specified
    format, handling various directory and wildcard patterns.

    Args:
        path: Base path to convert. Can include wildcards (* or **).
            Examples: "data/", "data/*.json", "data/**"
        format: File format to match (without dot). If None, inferred from path.
            Examples: "json", "csv", "parquet"

    Returns:
        str: Glob pattern that matches files of specified format.
            Examples: "data/**/*.json", "data/*.csv"

    Example:
        >>> # Basic directory
        >>> path_to_glob("data", "json")
        'data/**/*.json'
        >>>
        >>> # With wildcards
        >>> path_to_glob("data/**", "csv")
        'data/**/*.csv'
        >>>
        >>> # Format inference
        >>> path_to_glob("data/file.parquet")
        'data/file.parquet'
    """
path = path.rstrip("/")
⋮----
format = "json"
⋮----
format = "csv"
⋮----
format = "parquet"
⋮----
"""Read a JSON file from any filesystem.

    Internal function that handles both regular JSON and JSON Lines formats.

    Args:
        path: Path to JSON file
        self: Filesystem instance to use for reading
        include_file_path: Whether to return dict with filepath as key
        jsonlines: Whether to read as JSON Lines format

    Returns:
        dict | list[dict]: Parsed JSON data. If include_file_path=True,
            returns {filepath: data}

    Example:
        >>> fs = LocalFileSystem()
        >>> # Regular JSON
        >>> data = _read_json_file("data.json", fs)
        >>> print(type(data))
        <class 'dict'>
        >>>
        >>> # JSON Lines with filepath
        >>> data = _read_json_file(
        ...     "data.jsonl",
        ...     fs,
        ...     include_file_path=True,
        ...     jsonlines=True
        ... )
        >>> print(list(data.keys())[0])
        'data.jsonl'
    """
⋮----
data = [orjson.loads(line) for line in f.readlines()]
⋮----
data = orjson.loads(f.read())
⋮----
"""Read a single JSON file from any filesystem.

    A public wrapper around _read_json_file providing a clean interface for
    reading individual JSON files.

    Args:
        path: Path to JSON file to read
        include_file_path: Whether to return dict with filepath as key
        jsonlines: Whether to read as JSON Lines format

    Returns:
        dict | list[dict]: Parsed JSON data. For regular JSON, returns a dict.
            For JSON Lines, returns a list of dicts. If include_file_path=True,
            returns {filepath: data}.

    Example:
        >>> fs = LocalFileSystem()
        >>> # Read regular JSON
        >>> data = fs.read_json_file("config.json")
        >>> print(data["setting"])
        'value'
        >>>
        >>> # Read JSON Lines with filepath
        >>> data = fs.read_json_file(
        ...     "logs.jsonl",
        ...     include_file_path=True,
        ...     jsonlines=True
        ... )
        >>> print(list(data.keys())[0])
        'logs.jsonl'
    """
⋮----
"""
    Read a JSON file or a list of JSON files.

    Args:
        path: (str | list[str]) Path to the JSON file(s).
        include_file_path: (bool, optional) If True, return a dictionary with the file path as key.
            Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        jsonlines: (bool, optional) If True, read JSON lines. Defaults to False.
        as_dataframe: (bool, optional) If True, return a DataFrame. Defaults to True.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (dict | list[dict] | pl.DataFrame | list[pl.DataFrame]):
            Dictionary, list of dictionaries, DataFrame or list of DataFrames.
    """
⋮----
path = path_to_glob(path, format="json")
path = self.glob(path)
⋮----
data = run_parallel(
data = [
⋮----
data = _read_json_file(
⋮----
data = [pl.DataFrame(d) for d in data]
⋮----
"""Process JSON files in batches with optional parallel reading.

    Internal generator function that handles batched reading of JSON files
    with support for parallel processing within each batch.

    Args:
        path: Path(s) to JSON file(s). Glob patterns supported.
        batch_size: Number of files to process in each batch
        include_file_path: Include source filepath in output
        jsonlines: Whether to read as JSON Lines format
        as_dataframe: Convert output to Polars DataFrame(s)
        concat: Combine files within each batch
        use_threads: Enable parallel file reading within batches
        verbose: Print progress information
        **kwargs: Additional arguments for DataFrame conversion

    Yields:
        Each batch of data in requested format:
        - dict | list[dict]: Raw JSON data
        - pl.DataFrame: Single DataFrame if concat=True
        - list[pl.DataFrame]: List of DataFrames if concat=False

    Example:
        >>> fs = LocalFileSystem()
        >>> # Process large dataset in batches
        >>> for batch in fs._read_json_batches(
        ...     "data/*.json",
        ...     batch_size=100,
        ...     as_dataframe=True,
        ...     verbose=True
        ... ):
        ...     print(f"Batch shape: {batch.shape}")
        >>>
        >>> # Parallel batch processing with filepath tracking
        >>> for batch in fs._read_json_batches(
        ...     ["logs1.jsonl", "logs2.jsonl"],
        ...     batch_size=1,
        ...     include_file_path=True,
        ...     use_threads=True
        ... ):
        ...     print(f"Processing {batch['file_path'][0]}")
    """
# Handle path resolution
⋮----
# Process files in batches
⋮----
batch_paths = path[i : i + batch_size]
⋮----
# Read batch with optional parallelization
⋮----
batch_data = run_parallel(
⋮----
batch_data = [
⋮----
batch_dfs = [pl.DataFrame(d) for d in batch_data]
⋮----
batch_dfs = [
⋮----
"""Read JSON data from one or more files with powerful options.

    Provides a flexible interface for reading JSON data with support for:
    - Single file or multiple files
    - Regular JSON or JSON Lines format
    - Batch processing for large datasets
    - Parallel processing
    - DataFrame conversion
    - File path tracking

    Args:
        path: Path(s) to JSON file(s). Can be:
            - Single path string (globs supported)
            - List of path strings
        batch_size: If set, enables batch reading with this many files per batch
        include_file_path: Include source filepath in output
        jsonlines: Whether to read as JSON Lines format
        as_dataframe: Convert output to Polars DataFrame(s)
        concat: Combine multiple files/batches into single result
        use_threads: Enable parallel file reading
        verbose: Print progress information
        **kwargs: Additional arguments passed to DataFrame conversion

    Returns:
        Various types depending on arguments:
        - dict: Single JSON file as dictionary
        - list[dict]: Multiple JSON files as list of dictionaries
        - pl.DataFrame: Single or concatenated DataFrame
        - list[pl.DataFrame]: List of DataFrames (if concat=False)
        - Generator: If batch_size set, yields batches of above types

    Example:
        >>> fs = LocalFileSystem()
        >>> # Read all JSON files in directory
        >>> df = fs.read_json(
        ...     "data/*.json",
        ...     as_dataframe=True,
        ...     concat=True
        ... )
        >>> print(df.shape)
        (1000, 5)  # Combined data from all files
        >>>
        >>> # Batch process large dataset
        >>> for batch_df in fs.read_json(
        ...     "logs/*.jsonl",
        ...     batch_size=100,
        ...     jsonlines=True,
        ...     include_file_path=True
        ... ):
        ...     print(f"Processing {len(batch_df)} records")
        >>>
        >>> # Parallel read with custom options
        >>> dfs = fs.read_json(
        ...     ["file1.json", "file2.json"],
        ...     use_threads=True,
        ...     concat=False,
        ...     verbose=True
        ... )
        >>> print(f"Read {len(dfs)} files")
    """
⋮----
"""Read a single CSV file from any filesystem.

    Internal function that handles reading individual CSV files and optionally
    adds the source filepath as a column.

    Args:
        path: Path to CSV file
        self: Filesystem instance to use for reading
        include_file_path: Add source filepath as a column
        **kwargs: Additional arguments passed to pl.read_csv()

    Returns:
        pl.DataFrame: DataFrame containing CSV data

    Example:
        >>> fs = LocalFileSystem()
        >>> df = _read_csv_file(
        ...     "data.csv",
        ...     fs,
        ...     include_file_path=True,
        ...     delimiter="|"
        ... )
        >>> print("file_path" in df.columns)
        True
    """
print(path)  # Debug info
⋮----
df = pl.read_csv(f, **kwargs)
⋮----
"""
    Read a CSV file or a list of CSV files into a polars DataFrame.

    Args:
        path: (str | list[str]) Path to the CSV file(s).
        include_file_path: (bool, optional) If True, return a DataFrame with a 'file_path' column.
            Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (pl.DataFrame | list[pl.DataFrame]): Polars DataFrame or list of DataFrames.
    """
⋮----
path = path_to_glob(path, format="csv")
⋮----
dfs = run_parallel(
dfs = [
⋮----
dfs = _read_csv_file(
⋮----
"""Process CSV files in batches with optional parallel reading.

    Internal generator function that handles batched reading of CSV files
    with support for parallel processing within each batch.

    Args:
        path: Path(s) to CSV file(s). Glob patterns supported.
        batch_size: Number of files to process in each batch
        include_file_path: Add source filepath as a column
        concat: Combine files within each batch
        use_threads: Enable parallel file reading within batches
        verbose: Print progress information
        **kwargs: Additional arguments passed to pl.read_csv()

    Yields:
        Each batch of data in requested format:
        - pl.DataFrame: Single DataFrame if concat=True
        - list[pl.DataFrame]: List of DataFrames if concat=False

    Example:
        >>> fs = LocalFileSystem()
        >>> # Process large dataset in batches
        >>> for batch in fs._read_csv_batches(
        ...     "data/*.csv",
        ...     batch_size=100,
        ...     include_file_path=True,
        ...     verbose=True
        ... ):
        ...     print(f"Batch columns: {batch.columns}")
        >>>
        >>> # Parallel processing without concatenation
        >>> for batch in fs._read_csv_batches(
        ...     ["file1.csv", "file2.csv"],
        ...     batch_size=1,
        ...     concat=False,
        ...     use_threads=True
        ... ):
        ...     for df in batch:
        ...         print(f"DataFrame shape: {df.shape}")
    """
⋮----
# Ensure path is a list
⋮----
path = [path]
⋮----
batch_dfs = run_parallel(
⋮----
"""Read CSV data from one or more files with powerful options.

    Provides a flexible interface for reading CSV files with support for:
    - Single file or multiple files
    - Batch processing for large datasets
    - Parallel processing
    - File path tracking
    - Polars DataFrame output

    Args:
        path: Path(s) to CSV file(s). Can be:
            - Single path string (globs supported)
            - List of path strings
        batch_size: If set, enables batch reading with this many files per batch
        include_file_path: Add source filepath as a column
        concat: Combine multiple files/batches into single DataFrame
        use_threads: Enable parallel file reading
        verbose: Print progress information
        **kwargs: Additional arguments passed to pl.read_csv()

    Returns:
        Various types depending on arguments:
        - pl.DataFrame: Single or concatenated DataFrame
        - list[pl.DataFrame]: List of DataFrames (if concat=False)
        - Generator: If batch_size set, yields batches of above types

    Example:
        >>> fs = LocalFileSystem()
        >>> # Read all CSVs in directory
        >>> df = fs.read_csv(
        ...     "data/*.csv",
        ...     include_file_path=True
        ... )
        >>> print(df.columns)
        ['file_path', 'col1', 'col2', ...]
        >>>
        >>> # Batch process large dataset
        >>> for batch_df in fs.read_csv(
        ...     "logs/*.csv",
        ...     batch_size=100,
        ...     use_threads=True,
        ...     verbose=True
        ... ):
        ...     print(f"Processing {len(batch_df)} rows")
        >>>
        >>> # Multiple files without concatenation
        >>> dfs = fs.read_csv(
        ...     ["file1.csv", "file2.csv"],
        ...     concat=False,
        ...     use_threads=True
        ... )
        >>> print(f"Read {len(dfs)} files")
    """
⋮----
"""Read a single Parquet file from any filesystem.

    Internal function that handles reading individual Parquet files and
    optionally adds the source filepath as a column.

    Args:
        path: Path to Parquet file
        self: Filesystem instance to use for reading
        include_file_path: Add source filepath as a column
        **kwargs: Additional arguments passed to pq.read_table()

    Returns:
        pa.Table: PyArrow Table containing Parquet data

    Example:
        >>> fs = LocalFileSystem()
        >>> table = _read_parquet_file(
        ...     "data.parquet",
        ...     fs,
        ...     include_file_path=True,
        ...     use_threads=True
        ... )
        >>> print("file_path" in table.column_names)
        True
    """
table = pq.read_table(path, filesystem=self, **kwargs)
⋮----
"""
    Read a Parquet file or a list of Parquet files into a pyarrow Table.

    Args:
        path: (str | list[str]) Path to the Parquet file(s).
        include_file_path: (bool, optional) If True, return a Table with a 'file_path' column.
            Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        concat: (bool, optional) If True, concatenate the Tables. Defaults to True.
        **kwargs: Additional keyword arguments.

    Returns:
        (pa.Table | list[pa.Table]): Pyarrow Table or list of Pyarrow Tables.
    """
⋮----
path = path.replace("**", "").replace("*.parquet", "")
⋮----
path = path_to_glob(path, format="parquet")
⋮----
table = run_parallel(
⋮----
table = [
⋮----
table = _read_parquet_file(
⋮----
"""Process Parquet files in batches with performance optimizations.

    Internal generator function that handles batched reading of Parquet files
    with support for:
    - Parallel processing within batches
    - Metadata-based optimizations
    - Memory-efficient processing
    - Progress tracking

    Uses fast path for simple cases:
    - Single directory with _metadata
    - No need for filepath column
    - Concatenated output

    Args:
        path: Path(s) to Parquet file(s). Glob patterns supported.
        batch_size: Number of files to process in each batch
        include_file_path: Add source filepath as a column
        use_threads: Enable parallel file reading within batches
        concat: Combine files within each batch
        verbose: Print progress information
        **kwargs: Additional arguments passed to pq.read_table()

    Yields:
        Each batch of data in requested format:
        - pa.Table: Single Table if concat=True
        - list[pa.Table]: List of Tables if concat=False

    Example:
        >>> fs = LocalFileSystem()
        >>> # Fast path for simple case
        >>> next(_read_parquet_batches(
        ...     fs,
        ...     "data/",  # Contains _metadata
        ...     batch_size=1000
        ... ))
        >>>
        >>> # Parallel batch processing
        >>> for batch in fs._read_parquet_batches(
        ...     fs,
        ...     ["file1.parquet", "file2.parquet"],
        ...     batch_size=1,
        ...     include_file_path=True,
        ...     use_threads=True
        ... ):
        ...     print(f"Batch schema: {batch.schema}")
    """
# Fast path for simple cases
⋮----
# Resolve path(s) to list
⋮----
# Process in batches
⋮----
batch_tables = run_parallel(
⋮----
batch_tables = [
⋮----
"""Read Parquet data with advanced features and optimizations.

    Provides a high-performance interface for reading Parquet files with support for:
    - Single file or multiple files
    - Batch processing for large datasets
    - Parallel processing
    - File path tracking
    - Automatic concatenation
    - PyArrow Table output

    The function automatically uses optimal reading strategies:
    - Direct dataset reading for simple cases
    - Parallel processing for multiple files
    - Batched reading for memory efficiency

    Args:
        path: Path(s) to Parquet file(s). Can be:
            - Single path string (globs supported)
            - List of path strings
            - Directory containing _metadata file
        batch_size: If set, enables batch reading with this many files per batch
        include_file_path: Add source filepath as a column
        concat: Combine multiple files/batches into single Table
        use_threads: Enable parallel file reading
        verbose: Print progress information
        **kwargs: Additional arguments passed to pq.read_table()

    Returns:
        Various types depending on arguments:
        - pa.Table: Single or concatenated Table
        - list[pa.Table]: List of Tables (if concat=False)
        - Generator: If batch_size set, yields batches of above types

    Example:
        >>> fs = LocalFileSystem()
        >>> # Read all Parquet files in directory
        >>> table = fs.read_parquet(
        ...     "data/*.parquet",
        ...     include_file_path=True
        ... )
        >>> print(table.column_names)
        ['file_path', 'col1', 'col2', ...]
        >>>
        >>> # Batch process large dataset
        >>> for batch in fs.read_parquet(
        ...     "data/*.parquet",
        ...     batch_size=100,
        ...     use_threads=True
        ... ):
        ...     print(f"Processing {batch.num_rows} rows")
        >>>
        >>> # Read from directory with metadata
        >>> table = fs.read_parquet(
        ...     "data/",  # Contains _metadata
        ...     use_threads=True
        ... )
        >>> print(f"Total rows: {table.num_rows}")
    """
⋮----
"""Universal interface for reading data files of any supported format.

    A unified API that automatically delegates to the appropriate reading function
    based on file format, while preserving all advanced features like:
    - Batch processing
    - Parallel reading
    - File path tracking
    - Format-specific optimizations

    Args:
        path: Path(s) to data file(s). Can be:
            - Single path string (globs supported)
            - List of path strings
        format: File format to read. Supported values:
            - "json": Regular JSON or JSON Lines
            - "csv": CSV files
            - "parquet": Parquet files
        batch_size: If set, enables batch reading with this many files per batch
        include_file_path: Add source filepath as column/field
        concat: Combine multiple files/batches into single result
        jsonlines: For JSON format, whether to read as JSON Lines
        use_threads: Enable parallel file reading
        verbose: Print progress information
        **kwargs: Additional format-specific arguments

    Returns:
        Various types depending on format and arguments:
        - pl.DataFrame: For CSV and optionally JSON
        - pa.Table: For Parquet
        - list[pl.DataFrame | pa.Table]: Without concatenation
        - Generator: If batch_size set, yields batches

    Example:
        >>> fs = LocalFileSystem()
        >>> # Read CSV files
        >>> df = fs.read_files(
        ...     "data/*.csv",
        ...     format="csv",
        ...     include_file_path=True
        ... )
        >>> print(type(df))
        <class 'polars.DataFrame'>
        >>>
        >>> # Batch process Parquet files
        >>> for batch in fs.read_files(
        ...     "data/*.parquet",
        ...     format="parquet",
        ...     batch_size=100,
        ...     use_threads=True
        ... ):
        ...     print(f"Batch type: {type(batch)}")
        >>>
        >>> # Read JSON Lines
        >>> df = fs.read_files(
        ...     "logs/*.jsonl",
        ...     format="json",
        ...     jsonlines=True,
        ...     concat=True
        ... )
        >>> print(df.columns)
    """
⋮----
"""Create a PyArrow dataset from files in any supported format.

    Creates a dataset that provides optimized reading and querying capabilities
    including:
    - Schema inference and enforcement
    - Partition discovery and pruning
    - Predicate pushdown
    - Column projection

    Args:
        path: Base path to dataset files
        format: File format. Currently supports:
            - "parquet" (default)
            - "csv"
            - "json" (experimental)
        schema: Optional schema to enforce. If None, inferred from data.
        partitioning: How the dataset is partitioned. Can be:
            - str: Single partition field
            - list[str]: Multiple partition fields
            - pds.Partitioning: Custom partitioning scheme
        **kwargs: Additional arguments for dataset creation

    Returns:
        pds.Dataset: PyArrow dataset instance

    Example:
        >>> fs = LocalFileSystem()
        >>> # Simple Parquet dataset
        >>> ds = fs.pyarrow_dataset("data/")
        >>> print(ds.schema)
        >>>
        >>> # Partitioned dataset
        >>> ds = fs.pyarrow_dataset(
        ...     "events/",
        ...     partitioning=["year", "month"]
        ... )
        >>> # Query with partition pruning
        >>> table = ds.to_table(
        ...     filter=(ds.field("year") == 2024)
        ... )
        >>>
        >>> # CSV with schema
        >>> ds = fs.pyarrow_dataset(
        ...     "logs/",
        ...     format="csv",
        ...     schema=pa.schema([
        ...         ("timestamp", pa.timestamp("s")),
        ...         ("level", pa.string()),
        ...         ("message", pa.string())
        ...     ])
        ... )
    """
⋮----
"""Create a PyArrow dataset optimized for Parquet files.

    Creates a dataset specifically for Parquet data, automatically handling
    _metadata files for optimized reading.

    This function is particularly useful for:
    - Datasets with existing _metadata files
    - Multi-file datasets that should be treated as one
    - Partitioned Parquet datasets

    Args:
        path: Path to dataset directory or _metadata file
        schema: Optional schema to enforce. If None, inferred from data.
        partitioning: How the dataset is partitioned. Can be:
            - str: Single partition field
            - list[str]: Multiple partition fields
            - pds.Partitioning: Custom partitioning scheme
        **kwargs: Additional dataset arguments

    Returns:
        pds.Dataset: PyArrow dataset instance

    Example:
        >>> fs = LocalFileSystem()
        >>> # Dataset with _metadata
        >>> ds = fs.pyarrow_parquet_dataset("data/_metadata")
        >>> print(ds.files)  # Shows all data files
        >>>
        >>> # Partitioned dataset directory
        >>> ds = fs.pyarrow_parquet_dataset(
        ...     "sales/",
        ...     partitioning=["year", "region"]
        ... )
        >>> # Query with partition pruning
        >>> table = ds.to_table(
        ...     filter=(
        ...         (ds.field("year") == 2024) &
        ...         (ds.field("region") == "EMEA")
        ...     )
        ... )
    """
⋮----
path = posixpath.join(path, "_metadata")
⋮----
) -> ParquetDataset:  # type: ignore
"""Create a Pydala dataset for advanced Parquet operations.

    Creates a dataset with additional features beyond PyArrow including:
    - Delta table support
    - Schema evolution
    - Advanced partitioning
    - Metadata management
    - Sort key optimization

    Args:
        path: Path to dataset directory
        partitioning: How the dataset is partitioned. Can be:
            - str: Single partition field
            - list[str]: Multiple partition fields
            - pds.Partitioning: Custom partitioning scheme
        **kwargs: Additional dataset configuration

    Returns:
        ParquetDataset: Pydala dataset instance

    Example:
        >>> fs = LocalFileSystem()
        >>> # Create dataset
        >>> ds = fs.pydala_dataset(
        ...     "data/",
        ...     partitioning=["date"]
        ... )
        >>>
        >>> # Write with delta support
        >>> ds.write_to_dataset(
        ...     new_data,
        ...     mode="delta",
        ...     delta_subset=["id"]
        ... )
        >>>
        >>> # Read with metadata
        >>> df = ds.to_polars()
        >>> print(df.columns)
    """
⋮----
"""Write data to a Parquet file with automatic format conversion.

    Handles writing data from multiple input formats to Parquet with:
    - Automatic conversion to PyArrow
    - Schema validation/coercion
    - Metadata collection
    - Compression and encoding options

    Args:
        data: Input data in various formats:
            - Polars DataFrame/LazyFrame
            - PyArrow Table
            - Pandas DataFrame
            - Dict or list of dicts
        path: Output Parquet file path
        schema: Optional schema to enforce on write
        **kwargs: Additional arguments for pq.write_table()

    Returns:
        pq.FileMetaData: Metadata of written Parquet file

    Raises:
        SchemaError: If data doesn't match schema
        ValueError: If data cannot be converted

    Example:
        >>> fs = LocalFileSystem()
        >>> # Write Polars DataFrame
        >>> df = pl.DataFrame({
        ...     "id": range(1000),
        ...     "value": pl.Series(np.random.randn(1000))
        ... })
        >>> metadata = fs.write_parquet(
        ...     df,
        ...     "data.parquet",
        ...     compression="zstd",
        ...     compression_level=3
        ... )
        >>> print(f"Rows: {metadata.num_rows}")
        >>>
        >>> # Write with schema
        >>> schema = pa.schema([
        ...     ("id", pa.int64()),
        ...     ("value", pa.float64())
        ... ])
        >>> metadata = fs.write_parquet(
        ...     {"id": [1, 2], "value": [0.1, 0.2]},
        ...     "data.parquet",
        ...     schema=schema
        ... )
    """
data = to_pyarrow_table(data, concat=False, unique=False)
⋮----
data = data.cast(schema)
metadata = []
⋮----
metadata = metadata[0]
⋮----
"""Write data to a JSON file with flexible input support.

    Handles writing data in various formats to JSON or JSON Lines,
    with optional appending for streaming writes.

    Args:
        data: Input data in various formats:
            - Dict or list of dicts
            - Polars DataFrame/LazyFrame
            - PyArrow Table
            - Pandas DataFrame
        path: Output JSON file path
        append: Whether to append to existing file (JSON Lines mode)

    Example:
        >>> fs = LocalFileSystem()
        >>> # Write dictionary
        >>> data = {"name": "test", "values": [1, 2, 3]}
        >>> fs.write_json(data, "config.json")
        >>>
        >>> # Stream records
        >>> df1 = pl.DataFrame({"id": [1], "value": ["first"]})
        >>> df2 = pl.DataFrame({"id": [2], "value": ["second"]})
        >>> fs.write_json(df1, "stream.jsonl", append=False)
        >>> fs.write_json(df2, "stream.jsonl", append=True)
        >>>
        >>> # Convert PyArrow
        >>> table = pa.table({"a": [1, 2], "b": ["x", "y"]})
        >>> fs.write_json(table, "data.json")
    """
⋮----
data = data.collect()
⋮----
data = data.to_arrow()
data = data.cast(convert_large_types_to_standard(data.schema)).to_pydict()
⋮----
data = pa.Table.from_pandas(data, preserve_index=False).to_pydict()
⋮----
data = data.to_pydict()
⋮----
"""Write data to a CSV file with flexible input support.

    Handles writing data from multiple formats to CSV with options for:
    - Appending to existing files
    - Custom delimiters and formatting
    - Automatic type conversion
    - Header handling

    Args:
        data: Input data in various formats:
            - Polars DataFrame/LazyFrame
            - PyArrow Table
            - Pandas DataFrame
            - Dict or list of dicts
        path: Output CSV file path
        append: Whether to append to existing file
        **kwargs: Additional arguments for CSV writing:
            - delimiter: Field separator (default ",")
            - header: Whether to write header row
            - quote_char: Character for quoting fields
            - date_format: Format for date/time fields
            - float_precision: Decimal places for floats

    Example:
        >>> fs = LocalFileSystem()
        >>> # Write Polars DataFrame
        >>> df = pl.DataFrame({
        ...     "id": range(100),
        ...     "name": ["item_" + str(i) for i in range(100)]
        ... })
        >>> fs.write_csv(df, "items.csv")
        >>>
        >>> # Append records
        >>> new_items = pl.DataFrame({
        ...     "id": range(100, 200),
        ...     "name": ["item_" + str(i) for i in range(100, 200)]
        ... })
        >>> fs.write_csv(
        ...     new_items,
        ...     "items.csv",
        ...     append=True,
        ...     header=False
        ... )
        >>>
        >>> # Custom formatting
        >>> data = pa.table({
        ...     "date": [datetime.now()],
        ...     "value": [123.456]
        ... })
        >>> fs.write_csv(
        ...     data,
        ...     "formatted.csv",
        ...     date_format="%Y-%m-%d",
        ...     float_precision=2
        ... )
    """
⋮----
"""
    Write a DataFrame to a file in the given format.

    Args:
        data: (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame) Data to write.
        path (str): Path to write the data.
        format (str): Format of the file.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
⋮----
mode: str = "append",  # append, overwrite, delete_matching, error_if_exists
⋮----
"""Write a DataFrame or a list of DataFrames to a file or a list of files.

    Args:
        data: (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict | list[pl.DataFrame | pl.LazyFrame |
            pa.Table | pd.DataFrame | dict]) Data to write.
        path: (str | list[str]) Path to write the data.
        basename: (str, optional) Basename of the files. Defaults to None.
        format: (str, optional) Format of the data. Defaults to None.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        unique: (bool, optional) If True, remove duplicates. Defaults to False.
        mode: (str, optional) Write mode. Defaults to 'append'. Options: 'append', 'overwrite', 'delete_matching',
            'error_if_exists'.
        use_threads: (bool, optional) If True, use parallel processing. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        None

    Raises:
        FileExistsError: If file already exists and mode is 'error_if_exists'.
    """
⋮----
data = [data]
⋮----
data = _dict_to_dataframe(data)
⋮----
data = pl.concat([d.collect() for d in data], how="diagonal_relaxed")
⋮----
data = pl.concat([pl.from_arrow(d) for d in data], how="diagonal_relaxed")
⋮----
data = pl.concat([pl.from_pandas(d) for d in data], how="diagonal_relaxed")
⋮----
data = data.unique(
⋮----
format = (
⋮----
def _write(d, p, basename, i)
⋮----
basename = f"data-{dt.datetime.now().strftime('%Y%m%d_%H%M%S%f')[:-3]}-{uuid.uuid4().hex[:16]}"
p = f"{p}/{basename}-{i}.{format}"
⋮----
p = p.replace(f".{format}", f"-{i}.{format}")
⋮----
# Remove existing files
⋮----
# Remove existing files
⋮----
"""
    Write a tabluar data to a PyArrow dataset.

    Args:
        data: (pl.DataFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader |
            pd.DataFrame | list[pl.DataFrame] | list[pa.Table] | list[pa.RecordBatch] |
            list[pa.RecordBatchReader] | list[pd.DataFrame]) Data to write.
        path: (str) Path to write the data.
        basename: (str, optional) Basename of the files. Defaults to None.
        schema: (pa.Schema, optional) Schema of the data. Defaults to None.
        partition_by: (str | list[str] | pds.Partitioning, optional) Partitioning of the data.
            Defaults to None.
        partitioning_flavor: (str, optional) Partitioning flavor. Defaults to 'hive'.
        mode: (str, optional) Write mode. Defaults to 'append'.
        format: (str, optional) Format of the data. Defaults to 'parquet'.
        compression: (str, optional) Compression algorithm. Defaults to 'zstd'.
        max_rows_per_file: (int, optional) Maximum number of rows per file. Defaults to 2_500_000.
        row_group_size: (int, optional) Row group size. Defaults to 250_000.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        unique: (bool | str | list[str], optional) If True, remove duplicates. Defaults to False.
        **kwargs: Additional keyword arguments for `pds.write_dataset`.

    Returns:
        (list[pq.FileMetaData] | None): List of Parquet file metadata or None.
    """
data = to_pyarrow_table(data, concat=concat, unique=unique)
⋮----
existing_data_behavior = "delete_matching"
⋮----
existing_data_behavior = "overwrite_or_ignore"
⋮----
existing_data_behavior = mode
⋮----
basename_template = (
⋮----
basename_template = f"{basename}-{{i}}.parquet"
⋮----
file_options = pds.ParquetFileFormat().make_write_options(compression=compression)
⋮----
create_dir: bool = (False,)
⋮----
create_dir = True
⋮----
def file_visitor(written_file)
⋮----
file_metadata = written_file.metadata
⋮----
mode: str = "append",  # "delta", "overwrite"
⋮----
"""Write a tabular data to a Pydala dataset.

    Args:
        data: (pl.DataFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader |
            pd.DataFrame | list[pl.DataFrame] | list[pa.Table] | list[pa.RecordBatch] |
            list[pa.RecordBatchReader] | list[pd.DataFrame]) Data to write.
        path: (str) Path to write the data.
        mode: (str, optional) Write mode. Defaults to 'append'. Options: 'delta', 'overwrite'.
        basename: (str, optional) Basename of the files. Defaults to None.
        partition_by: (str | list[str], optional) Partitioning of the data. Defaults to None.
        partitioning_flavor: (str, optional) Partitioning flavor. Defaults to 'hive'.
        max_rows_per_file: (int, optional) Maximum number of rows per file. Defaults to 2_500_000.
        row_group_size: (int, optional) Row group size. Defaults to 250_000.
        compression: (str, optional) Compression algorithm. Defaults to 'zstd'.
        sort_by: (str | list[str] | list[tuple[str, str]], optional) Columns to sort by. Defaults to None.
        unique: (bool | str | list[str], optional) If True, ensure unique values. Defaults to False.
        delta_subset: (str | list[str], optional) Subset of columns to include in delta table. Defaults to None.
        update_metadata: (bool, optional) If True, update metadata. Defaults to True.
        alter_schema: (bool, optional) If True, alter schema. Defaults to False.
        timestamp_column: (str, optional) Timestamp column. Defaults to None.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments for `ParquetDataset.write_to_dataset`.

    Returns:
        None
    """
⋮----
ds = pydala_dataset(self=self, path=path, partitioning=partitioning_flavor)
````

## File: src/flowerpower/utils/misc.py
````python
# import tqdm
⋮----
def convert_large_types_to_standard(schema: pa.Schema) -> pa.Schema
⋮----
# Define mapping of large types to standard types
type_mapping = {
⋮----
# Convert fields
new_fields = []
⋮----
field_type = field.type
# Check if type exists in mapping
⋮----
new_field = pa.field(
⋮----
# Handle large lists with nested types
⋮----
def convert_large_types_to_standard(*args, **kwargs)
⋮----
"""
        Convert a dictionary or list of dictionaries to a polars DataFrame.

        Args:
            data: (dict | list[dict]) Data to convert.

        Returns:
            pl.DataFrame: Converted data.

        Examples:
            >>> # Single dict with list values
            >>> data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
            >>> _dict_to_dataframe(data)
            shape: (3, 2)
            ┌─────┬─────┐
            │ a   ┆ b   │
            │ --- ┆ --- │
            │ i64 ┆ i64 │
            ╞═════╪═════╡
            │ 1   ┆ 4   │
            │ 2   ┆ 5   │
            │ 3   ┆ 6   │
            └─────┴─────┘

            >>> # Single dict with scalar values
            >>> data = {'a': 1, 'b': 2}
            >>> _dict_to_dataframe(data)
            shape: (1, 2)
            ┌─────┬─────┐
            │ a   ┆ b   │
            │ --- ┆ --- │
            │ i64 ┆ i64 │
            ╞═════╪═════╡
            │ 1   ┆ 2   │
            └─────┴─────┘

            >>> # List of dicts with scalar values
            >>> data = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
            >>> _dict_to_dataframe(data)
            shape: (2, 2)
            ┌─────┬─────┐
            │ a   ┆ b   │
            │ --- ┆ --- │
            │ i64 ┆ i64 │
            ╞═════╪═════╡
            │ 1   ┆ 2   │
            │ 3   ┆ 4   │
            └─────┴─────┘

            >>> # List of dicts with list values
            >>> data = [{'a': [1, 2], 'b': [3, 4]}, {'a': [5, 6], 'b': [7, 8]}]
            >>> _dict_to_dataframe(data)
            shape: (2, 2)
            ┌───────┬───────┐
            │ a     ┆ b     │
            │ ---   ┆ ---   │
            │ list  ┆ list  │
            ╞═══════╪═══════╡
            │ [1,2] ┆ [3,4] │
            │ [5,6] ┆ [7,8] │
            └───────┴───────┘
        """
⋮----
# If it's a single-element list, just use the first element
⋮----
data = data[0]
# If it's a list of dicts
⋮----
first_item = data[0]
# Check if the dict values are lists/tuples
⋮----
# Each dict becomes a row with list/tuple values
data = pl.DataFrame(data)
⋮----
# If values are scalars, convert list of dicts to DataFrame
⋮----
data = data.unique(
⋮----
# If it's a single dict
⋮----
# Check if values are lists/tuples
⋮----
# Get the length of any list value (assuming all lists have same length)
length = len(
# Convert to DataFrame where each list element becomes a row
data = pl.DataFrame(
⋮----
# If values are scalars, wrap them in a list to create a single row
data = pl.DataFrame({k: [v] for k, v in data.items()})
⋮----
def _dict_to_dataframe(*args, **kwargs)
⋮----
data = _dict_to_dataframe(data)
⋮----
data = _dict_to_dataframe(data, unique=unique)
⋮----
data = [data]
⋮----
data = [dd.collect() for dd in data]
⋮----
data = pl.concat(data, how="diagonal_relaxed")
⋮----
data = data.to_arrow()
data = data.cast(convert_large_types_to_standard(data.schema))
⋮----
data = [dd.to_arrow() for dd in data]
data = [
⋮----
data = [pa.Table.from_pandas(dd, preserve_index=False) for dd in data]
⋮----
data = pa.concat_tables(data, promote_options="permissive")
⋮----
data = (
⋮----
data = pa.Table.from_batches(data)
⋮----
data = [pa.Table.from_batches([dd]) for dd in data]
⋮----
def to_pyarrow_table(*args, **kwargs)
⋮----
"""Runs a function for a list of parameters in parallel.

        Args:
            func (Callable): function to run in parallel
            *args: Positional arguments. Can be single values or iterables
            n_jobs (int, optional): Number of joblib workers. Defaults to -1
            backend (str, optional): joblib backend. Valid options are
                `loky`,`threading`, `mutliprocessing` or `sequential`. Defaults to "threading"
            verbose (bool, optional): Show progress bar. Defaults to True
            **kwargs: Keyword arguments. Can be single values or iterables

        Returns:
            list[any]: Function output

        Examples:
            >>> # Single iterable argument
            >>> run_parallel(func, [1,2,3], fixed_arg=42)

            >>> # Multiple iterables in args and kwargs
            >>> run_parallel(func, [1,2,3], val=[7,8,9], fixed=42)

            >>> # Only kwargs iterables
            >>> run_parallel(func, x=[1,2,3], y=[4,5,6], fixed=42)
        """
# Special kwargs for run_parallel itself
parallel_kwargs = {"n_jobs": n_jobs, "backend": backend, "verbose": 0}
⋮----
# Process args and kwargs to separate iterables and fixed values
iterables = []
fixed_args = []
iterable_kwargs = {}
fixed_kwargs = {}
⋮----
# Get the length of the first iterable to determine number of iterations
first_iterable_len = None
⋮----
# Process args
⋮----
first_iterable_len = len(arg)
⋮----
# Process kwargs
⋮----
first_iterable_len = len(value)
⋮----
# Create parameter combinations
all_iterables = iterables + list(iterable_kwargs.values())
param_combinations = list(zip(*all_iterables))  # Convert to list for tqdm
⋮----
# if verbose:
#    param_combinations = tqdm.tqdm(param_combinations)
⋮----
def run_parallel(*args, **kwargs)
⋮----
"""Get the dataset partitions from the file path.

    Args:
        path (str): File path.
        partitioning (str | list[str] | None, optional): Partitioning type. Defaults to None.

    Returns:
        list[tuple]: Partitions.
    """
⋮----
path = os.path.dirname(path)
⋮----
parts = path.split("/")
⋮----
def view_img(data: str | bytes, format: str = "svg")
⋮----
# Create a temporary file with .svg extension
⋮----
tmp_path = tmp.name
⋮----
# Open with default application on macOS
⋮----
# Optional: Remove the temp file after a delay
⋮----
time.sleep(2)  # Wait for viewer to open
⋮----
"""
    Updates a msgspec.Struct instance with values from a dictionary.
    Handles nested msgspec.Struct objects and nested dictionaries.

    Args:
        obj: The msgspec.Struct object to update
        update_dict: Dictionary containing update values

    Returns:
        Updated msgspec.Struct instance
    """
# Convert the struct to a dictionary for easier manipulation
obj_dict = msgspec.to_builtins(struct)
⋮----
# Update the dictionary recursively
⋮----
# Handle nested dictionaries
⋮----
# Direct update for non-nested values
⋮----
# Convert back to the original struct type
⋮----
"""Helper function to update nested dictionaries"""
result = original.copy()
⋮----
# Recursively update nested dictionaries
⋮----
# Direct update
````

## File: src/flowerpower/cli/__init__.py
````python
app = typer.Typer(
⋮----
"""
    Initialize a new FlowerPower project.

    This command creates a new FlowerPower project with the necessary directory structure
    and configuration files. If no project name is provided, the current directory name
    will be used as the project name.

    Args:
        project_name: Name of the FlowerPower project to create. If not provided,
                      the current directory name will be used
        base_dir: Base directory where the project will be created. If not provided,
                  the current directory's parent will be used
        storage_options: Storage options for filesystem access, as a JSON or dict string
        job_queue_type: Type of job queue backend to use (rq, apscheduler)

    Examples:
        # Create a project in the current directory using its name
        $ flowerpower init

        # Create a project with a specific name
        $ flowerpower init --name my-awesome-project

        # Create a project in a specific location
        $ flowerpower init --name my-project --base-dir /path/to/projects

        # Create a project with APScheduler as the job queue backend
        $ flowerpower init --job-queue-type apscheduler
    """
parsed_storage_options = {}
⋮----
parsed_storage_options = (
⋮----
"""
    Start the Hamilton UI web application.

    This command launches the Hamilton UI, which provides a web interface for
    visualizing and interacting with your FlowerPower pipelines. The UI allows you
    to explore pipeline execution graphs, view results, and manage jobs.

    Args:
        port: Port to run the UI server on
        base_dir: Base directory where the UI will store its data
        no_migration: Skip running database migrations on startup
        no_open: Prevent automatically opening the browser
        settings_file: Settings profile to use (mini, dev, prod)
        config_file: Optional custom configuration file path

    Examples:
        # Start the UI with default settings
        $ flowerpower ui

        # Run the UI on a specific port
        $ flowerpower ui --port 9000

        # Use a custom data directory
        $ flowerpower ui --base-dir ~/my-project/.hamilton-data

        # Start without opening a browser
        $ flowerpower ui --no-open

        # Use production settings
        $ flowerpower ui --settings prod
    """
````

## File: src/flowerpower/job_queue/__init__.py
````python
APSBackend = None
APSManager = None
⋮----
RQBackend = None
RQManager = None
⋮----
class JobQueueManager
⋮----
"""A factory class for creating job queue instances for job scheduling and execution.

    This class provides a unified interface for creating different types of job queue instances
    (RQ, APScheduler, Huey) based on the specified backend type. Each job queue type provides
    different capabilities for job scheduling and execution.

    The job queue instances handle:
    - Job scheduling and execution
    - Background task processing
    - Job queue management
    - Result storage and retrieval

    Example:
        ```python
        # Create an RQ job queue
        rq_worker = JobQueueManager(
            type="rq",
            name="my_worker",
            log_level="DEBUG"
        )

        # Create an APScheduler job queue with custom backend
        from flowerpower.job_queue.apscheduler import APSBackend
        backend_config = APSBackend(
            data_store={"type": "postgresql", "uri": "postgresql+asyncpg://user:pass@localhost/db"},
            event_broker={"type": "redis", "uri": "redis://localhost:6379/0"}
        )
        aps_worker = JobQueueManager(
            type="apscheduler",
            name="scheduler",
            backend=backend_config
        )

        ```
    """
⋮----
"""Create a new job queue instance based on the specified backend type.

        Args:
            type: The type of job queue to create. Valid values are:
                - "rq": Redis Queue job queue for Redis-based job queuing
                - "apscheduler": APScheduler job queue for advanced job scheduling
            name: Name of the job queue instance. Used for identification in logs
                and monitoring.
            base_dir: Base directory for job queue files and configuration. Defaults
                to current working directory if not specified.
            backend: Pre-configured backend instance. If not provided, one will
                be created based on configuration settings.
            storage_options: Options for configuring filesystem storage access.
                Example: {"mode": "async", "root": "/tmp", "protocol": "s3"}
            fs: Custom filesystem implementation for storage operations.
                Example: S3FileSystem, LocalFileSystem, etc.
            log_level: Logging level for the job queue. Valid values are:
                "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            **kwargs: Additional configuration options passed to the specific
                job queue implementation.

        Returns:
            BaseJobQueueManager: An instance of the specified job queue type (RQManager,
                APSManager).

        Raises:
            ValueError: If an invalid job queue type is specified.
            ImportError: If required dependencies for the chosen job queue type
                are not installed.
            RuntimeError: If job queue initialization fails due to configuration
                or connection issues.

        Example:
            ```python
            # Basic RQ job queue
            worker = JobQueueManager(type="rq", name="basic_worker")

            # APScheduler with custom logging and storage
            worker = JobQueueManager(
                type="apscheduler",
                name="scheduler",
                base_dir="/app/data",
                storage_options={"mode": "async"},
                log_level="DEBUG"
            )

            ```
        """
⋮----
type = ProjectConfig.load(
⋮----
class Backend
⋮----
"""A factory class for creating backend instances for different job queue types.

    This class provides a unified interface for creating backend instances that handle
    the storage, queuing, and event management for different job queue types. Each backend
    type provides specific implementations for:
    - Job storage and persistence
    - Queue management
    - Event handling and communication
    - Result storage

    Example:
        ```python
        # Create RQ backend with Redis
        rq_backend = Backend(
            job_queue_type="rq",
            uri="redis://localhost:6379/0",
            queues=["high", "default", "low"]
        )

        # Create APScheduler backend with PostgreSQL and Redis
        aps_backend = Backend(
            job_queue_type="apscheduler",
            data_store={
                "type": "postgresql",
                "uri": "postgresql+asyncpg://user:pass@localhost/db"
            },
            event_broker={
                "type": "redis",
                "uri": "redis://localhost:6379/0"
            }
        )
        ```
    """
⋮----
"""Create a new backend instance based on the specified job queue type.

        Args:
            job_queue_type: The type of backend to create. Valid values are:
                - "rq": Redis Queue backend using Redis
                - "apscheduler": APScheduler backend supporting various databases
                    and event brokers
            **kwargs: Backend-specific configuration options:
                For RQ:
                    - uri (str): Redis connection URI
                    - queues (list[str]): List of queue names
                    - result_ttl (int): Time to live for results in seconds
                For APScheduler:
                    - data_store (dict): Data store configuration
                    - event_broker (dict): Event broker configuration
                    - cleanup_interval (int): Cleanup interval in seconds
                    - max_concurrent_jobs (int): Maximum concurrent jobs

        Returns:
            BaseBackend: An instance of RQBackend or APSBackend depending on
                the specified job queue type.

        Raises:
            ValueError: If an invalid job queue type is specified.
            RuntimeError: If backend initialization fails due to configuration
                or connection issues.

        Example:
            ```python
            # Create RQ backend
            rq_backend = Backend(
                job_queue_type="rq",
                uri="redis://localhost:6379/0",
                queues=["high", "default", "low"],
                result_ttl=3600
            )

            # Create APScheduler backend with PostgreSQL and Redis
            aps_backend = Backend(
                job_queue_type="apscheduler",
                data_store={
                    "type": "postgresql",
                    "uri": "postgresql+asyncpg://user:pass@localhost/db",
                    "schema": "scheduler"
                },
                event_broker={
                    "type": "redis",
                    "uri": "redis://localhost:6379/0"
                },
                cleanup_interval=300,
                max_concurrent_jobs=10
            )
            ```
        """
⋮----
__all__ = [
⋮----
# "HueyWorker",
````

## File: src/flowerpower/plugins/mqtt/manager.py
````python
class MqttManager
⋮----
username = kwargs["user"]
⋮----
password = kwargs["pw"]
⋮----
@classmethod
    def from_event_broker(cls, base_dir: str | None = None)
⋮----
base_dir = base_dir or str(Path.cwd())
⋮----
jq_backend = ProjectConfig.load(base_dir=base_dir).job_queue.backend
⋮----
event_broker_cfg = jq_backend.event_broker
⋮----
fs = get_filesystem(
⋮----
cfg = MqttConfig.from_yaml(path=os.path.basename(path), fs=fs)
⋮----
@classmethod
    def from_dict(cls, cfg: dict)
⋮----
def __enter__(self) -> "MqttManager"
⋮----
# Add any cleanup code here if needed
⋮----
@staticmethod
    def _on_connect(client, userdata, flags, rc, properties)
⋮----
@staticmethod
    def _on_disconnect(client, userdata, disconnect_flags, rc, properties=None)
⋮----
reconnect_delay = min(reconnect_delay, userdata.max_reconnect_delay)
⋮----
@staticmethod
    def _on_publish(client, userdata, mid, rc, properties)
⋮----
@staticmethod
    def _on_subscribe(client, userdata, mid, qos, properties)
⋮----
qos_msg = str(qos[0])
⋮----
qos_msg = f"and granted QoS {qos[0]}"
⋮----
def connect(self) -> Client
⋮----
# Random Client ID when clean session is True
⋮----
# Deterministic Client ID when clean session is False
⋮----
client = Client(
⋮----
client.on_connect = self._on_connect  # self._on_connect
client.on_disconnect = self._on_disconnect  # self._on_disconnect
⋮----
# topic = topic or topic
⋮----
def disconnect(self)
⋮----
def reconnect(self)
⋮----
def publish(self, topic, payload)
⋮----
# elif self._client.is_connected() is False:
#    self.reconnect()
⋮----
def subscribe(self, topic: str | None = None, qos: int = 2)
⋮----
def unsubscribe(self, topic: str | None = None)
⋮----
def register_on_message(self, on_message: Callable)
⋮----
"""
        Run the MQTT client in the background.

        Args:
            on_message: Callback function to run when a message is received
            topic: MQTT topic to listen to

        Returns:
            None


        """
⋮----
"""
        Run the MQTT client until a break signal is received.

        Args:
            on_message: Callback function to run when a message is received
            topic: MQTT topic to listen to

        Returns:
            None
        """
⋮----
"""
        Start the MQTT listener.

        Args:
            on_message: Callback function to run when a message is received
            topic: MQTT topic to listen to
            background: Run the listener in the background

        Returns:
            None
        """
⋮----
"""
        Stop the MQTT listener.

        Returns:
            None
        """
⋮----
"""
        Start a pipeline listener that listens to a topic and processes the message using a pipeline.

        Args:
            name (str): Name of the pipeline
            topic (str | None): MQTT topic to listen to
            inputs (dict | None): Inputs for the pipeline
            final_vars (list | None): Final variables for the pipeline
            config (dict | None): Configuration for the pipeline driver
            cache (bool | dict): Cache for the pipeline
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration
            with_adapter_cfg (dict | WithAdapterConfig | None): With adapter configuration
            pipeline_adapter_cfg (dict | AdapterConfig | None): Pipeline adapter configuration
            project_adapter_cfg (dict | AdapterConfig | None): Project adapter configuration
            adapter (dict[str, Any] | None): Adapter configuration
            reload (bool): Reload the pipeline
            log_level (str | None): Log level for the pipeline
            result_ttl (float | dt.timedelta): Result expiration time for the pipeline
            run_in (int | str | dt.timedelta | None): Run in time for the pipeline
            max_retries (int | None): Maximum number of retries for the pipeline
            retry_delay (float | None): Delay between retries for the pipeline
            jitter_factor (float | None): Jitter factor for the pipeline
            retry_exceptions (tuple | list | None): Exceptions to retry for the pipeline
            as_job (bool): Run the pipeline as a job
            base_dir (str | None): Base directory for the pipeline
            storage_options (dict): Storage options for the pipeline
            fs (AbstractFileSystem | None): File system for the pipeline
            background (bool): Run the listener in the background
            qos (int): Quality of Service for the MQTT client
            config_hook (Callable[[bytes, int], dict] | None): Hook function to modify the configuration of the pipeline
            **kwargs: Additional keyword arguments

        Returns:
            None

        Raises:
            ValueError: If the config_hook is not callable

        Example:
            ```python
            from flowerpower.plugins.mqtt import MqttManager
            mqtt = MqttManager()
            mqtt.run_pipeline_on_message(
                name="my_pipeline",
                topic="my_topic",
                inputs={"key": "value"},
                config={"param": "value"},
                as_job=True,
            )
            ```
        """
⋮----
inputs = {}
⋮----
config = {}
⋮----
def on_message(client, userdata, msg)
⋮----
config_ = config_hook(inputs["payload"], inputs["topic"])
⋮----
_ = e
⋮----
"""
    Start the MQTT listener.

    The connection to the MQTT broker is established using the provided configuration of a
    MQTT event broker defined in the project configuration file `conf/project.toml`.
    If no configuration is found, you have to provide either the argument `mqtt_cfg`, dict with the
    connection parameters or the arguments `username`, `password`, `host`, and `port`.

    Args:
        on_message (Callable): Callback function to run when a message is received
        topic (str | None): MQTT topic to listen to
        background (bool): Run the listener in the background
        mqtt_cfg (dict | MqttConfig): MQTT client configuration. Use either this or arguments
            username, password, host, and port.
        base_dir (str | None): Base directory for the module
        username (str | None): Username for the MQTT client
        password (str | None): Password for the MQTT client
        host (str | None): Host for the MQTT client
        port (int | None): Port for the MQTT client
        clean_session (bool): Clean session flag for the MQTT client
        qos (int): Quality of Service for the MQTT client
        client_id (str | None): Client ID for the MQTT client
        client_id_suffix (str | None): Client ID suffix for the MQTT client
        config_hook (Callable[[bytes, int], dict] | None): Hook function to modify the configuration of the pipeline
        **kwargs: Additional keyword arguments

    Returns:
        None

    Raises:
        ValueError: If the config_hook is not callable
        ValueError: If no client configuration is found

    Example:
        ```python
        from flowerpower.plugins.mqtt import start_listener

        start_listener(
            on_message=my_on_message_function,
            topic="my_topic",
            background=True,
            mqtt_cfg={"host": "localhost", "port": 1883},
        )
        ```
    """
⋮----
client = MqttManager.from_event_broker(base_dir)
⋮----
client = MqttManager.from_config(mqtt_cfg)
⋮----
client = MqttManager.from_dict(mqtt_cfg)
⋮----
client = MqttManager(
⋮----
"""
    Start a pipeline listener that listens to a topic and processes the message using a pipeline.

    Args:
        name (str): Name of the pipeline
        topic (str | None): MQTT topic to listen to
        inputs (dict | None): Inputs for the pipeline
        final_vars (list | None): Final variables for the pipeline
        config (dict | None): Configuration for the pipeline driver
        cache (bool | dict): Cache for the pipeline
        executor_cfg (str | dict | ExecutorConfig | None): Executor configuration
        with_adapter_cfg (dict | WithAdapterConfig | None): With adapter configuration
        pipeline_adapter_cfg (dict | AdapterConfig | None): Pipeline adapter configuration
        project_adapter_cfg (dict | AdapterConfig | None): Project adapter configuration
        adapter (dict[str, Any] | None): Adapter configuration
        reload (bool): Reload the pipeline
        log_level (str | None): Log level for the pipeline
        result_ttl (float | dt.timedelta): Result expiration time for the pipeline
        run_in (int | str | dt.timedelta | None): Run in time for the pipeline
        max_retries (int | None): Maximum number of retries for the pipeline
        retry_delay (float | None): Delay between retries for the pipeline
        jitter_factor (float | None): Jitter factor for the pipeline
        retry_exceptions (tuple | list | None): Exceptions to retry for the pipeline
        as_job (bool): Run the pipeline as a job
        base_dir (str | None): Base directory for the pipeline
        storage_options (dict): Storage options for the pipeline
        fs (AbstractFileSystem | None): File system for the pipeline
        background (bool): Run the listener in the background
        mqtt_cfg (dict | MqttConfig): MQTT client configuration. Use either this or arguments
            username, password, host, and port.
        host (str | None): Host for the MQTT client
        port (int | None): Port for the MQTT client
        username (str | None): Username for the MQTT client
        password (str | None): Password for the MQTT client
        clean_session (bool): Clean session flag for the MQTT client
        qos (int): Quality of Service for the MQTT client
        client_id (str | None): Client ID for the MQTT client
        client_id_suffix (str | None): Client ID suffix for the MQTT client
        config_hook (Callable[[bytes, int], dict] | None): Hook function to modify the configuration of the pipeline
        **kwargs: Additional keyword arguments

    Returns:
        None

    Raises:
        ValueError: If the config_hook is not callable
        ValueError: If no client configuration is found

    Example:
        ```python
        from flowerpower.plugins.mqtt import run_pipeline_on_message

        run_pipeline_on_message(
            name="my_pipeline",
            topic="my_topic",
            inputs={"key": "value"},
            config={"param": "value"},
            as_job=True,
        )
        ```
    """
⋮----
"""
    cli_clean_session | config_clean_session | result
    TRUE		        TRUE		           TRUE
    FALSE		        FALSE                  FALSE
    FALSE               TRUE                   FALSE
    TRUE                FALSE                  FALSE

    Clean session should only use default value if neither cli nor config source says otherwise
    """
````

## File: examples/hello-world/conf/project.yml
````yaml
name: null
worker:
  type: apscheduler
  backend:
    data_store:
      type: postgresql
      uri: null
      username: postgres
      password: null
      host: localhost
      port: 5432
      database: null
      ssl: false
      cert_file: null
      key_file: null
      ca_file: null
      verify_ssl: false
      schema: flowerpower
    event_broker:
      type: postgresql
      uri: null
      username: postgres
      password: null
      host: localhost
      port: 5432
      database: null
      ssl: false
      cert_file: null
      key_file: null
      ca_file: null
      verify_ssl: false
      from_ds_sqla: true
    cleanup_interval: 300
    max_concurrent_jobs: 10
    default_job_executor: threadpool
    num_workers: 100
adapter:
  hamilton_tracker:
    username: null
    api_url: http://localhost:8241
    ui_url: http://localhost:8242
    api_key: null
    verify: false
  mlflow:
    tracking_uri: null
    registry_uri: null
    artifact_location: null
  ray:
    ray_init_config: null
    shutdown_ray_on_completion: false
  opentelemetry:
    host: localhost
    port: 6831
````

## File: src/flowerpower/pipeline/base.py
````python
def load_module(name: str, reload: bool = False)
⋮----
"""
    Load a module.

    Args:
        name (str): The name of the module.

    Returns:
        module: The loaded module.
    """
⋮----
class BasePipeline
⋮----
"""
    Base class for all pipelines.
    """
⋮----
job_queue_type: str | None = None,  # New parameter for worker backend
⋮----
fs = get_filesystem(self._base_dir, **self._storage_options)
⋮----
def __enter__(self) -> "BasePipeline"
⋮----
def _add_modules_path(self)
⋮----
"""
        Sync the filesystem.

        Returns:
            None
        """
⋮----
modules_path = posixpath.join(self._fs.path, self._pipelines_dir)
⋮----
def _load_project_cfg(self) -> ProjectConfig
⋮----
"""
        Load the project configuration.

        Returns:
            ProjectConfig: The loaded project configuration.
        """
⋮----
def _load_pipeline_cfg(self, name: str) -> PipelineConfig
⋮----
"""
        Load the pipeline configuration.

        Args:
            name (str): The name of the pipeline.

        Returns:
            PipelineConfig: The loaded pipeline configuration.
        """
````

## File: src/flowerpower/__init__.py
````python
from .flowerpower import init as init_project  # noqa: E402
from .job_queue import JobQueueManager  # noqa: E402
⋮----
__version__ = importlib.metadata.version("FlowerPower")
⋮----
__all__ = [
````

## File: src/flowerpower/pipeline/visualizer.py
````python
# Import necessary config types and utility functions
⋮----
from .base import load_module  # Import module loading utility
⋮----
class PipelineVisualizer
⋮----
"""Handles the visualization of pipeline DAGs."""
⋮----
def __init__(self, project_cfg: ProjectConfig, fs: AbstractFileSystem)
⋮----
"""
        Initializes the PipelineVisualizer.

        Args:
            project_cfg: The project configuration object.
            fs: The filesystem instance.
        """
⋮----
# Attributes like fs and base_dir are accessed via self.project_cfg
⋮----
def _display_all_function(self, name: str, reload: bool = False)
⋮----
"""Internal helper to load module/config and get the Hamilton DAG object.

        Args:
            name (str): The name of the pipeline.
            reload (bool): Whether to reload the module.

        Returns:
            Hamilton DAG object.

        Raises:
            ImportError: If the module cannot be loaded.

        """
# Load pipeline-specific config
pipeline_cfg = PipelineConfig.load(name=name, fs=self._fs)
⋮----
# Load the pipeline module
# Ensure the pipelines directory is in sys.path (handled by PipelineManager usually)
module = load_module(name=name, reload=reload)
⋮----
# Create a basic driver builder for visualization purposes
# Use the run config from the loaded pipeline_cfg
builder = (
⋮----
# No adapters or complex executors needed for display_all_functions
⋮----
# Build the driver
dr = builder.build()
⋮----
# Return the visualization object
⋮----
"""
        Save an image of the graph of functions for a given pipeline name.

        Args:
            name (str): The name of the pipeline graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            reload (bool, optional): Whether to reload the pipeline data. Defaults to False.

        Raises:
            ImportError: If the module cannot be loaded.

        Example:
            >>> from flowerpower.pipeline.visualizer import PipelineVisualizer
            >>> visualizer = PipelineVisualizer(project_cfg, fs)
            >>> visualizer.save_dag(name="example_pipeline", format="png")
        """
dag = self._display_all_function(name=name, reload=reload)
⋮----
# Use project_cfg attributes for path and filesystem access
graph_dir = posixpath.join(self.project_cfg.base_dir, "graphs")
⋮----
output_path = posixpath.join(
⋮----
)  # Output filename is just the pipeline name
output_path_with_ext = f"{output_path}.{format}"
⋮----
# Render the DAG using the graphviz object returned by display_all_functions
⋮----
output_path,  # graphviz appends the format automatically
⋮----
"""
        Display the graph of functions for a given pipeline name.

        Args:
            name (str): The name of the pipeline graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            reload (bool, optional): Whether to reload the pipeline data. Defaults to False.
            raw (bool, optional): Whether to return the raw graph object instead of displaying. Defaults to False.

        Returns:
            Optional[graphviz.Digraph]: The generated graph object if raw=True, else None.

        Raises:
            ImportError: If the module cannot be loaded.

        Example:
            >>> from flowerpower.pipeline.visualizer import PipelineVisualizer
            >>> visualizer = PipelineVisualizer(project_cfg, fs)
            >>> visualizer.show_dag(name="example_pipeline", format="png")
        """
⋮----
# Use view_img utility to display the rendered graph
⋮----
return None  # Explicitly return None when not raw
````

## File: src/flowerpower/cfg/pipeline/__init__.py
````python
class PipelineConfig(BaseConfig)
⋮----
"""Configuration class for managing pipeline settings in FlowerPower.

    This class handles pipeline-specific configuration including run settings, scheduling,
    parameters, and adapter settings. It supports Hamilton-style parameter configuration
    and YAML serialization.

    Attributes:
        name (str | None): The name of the pipeline.
        run (RunConfig): Configuration for pipeline execution.
        schedule (ScheduleConfig): Configuration for pipeline scheduling.
        params (dict): Pipeline parameters.
        adapter (AdapterConfig): Configuration for the pipeline adapter.
        h_params (dict): Hamilton-formatted parameters.

    Example:
        ```python
        # Create a new pipeline config
        pipeline = PipelineConfig(name="data-transform")

        # Set parameters
        pipeline.params = {
            "input_path": "data/input",
            "batch_size": 100
        }

        # Save configuration
        pipeline.save(name="data-transform")
        ```
    """
⋮----
name: str | None = msgspec.field(default=None)
run: RunConfig = msgspec.field(default_factory=RunConfig)
schedule: ScheduleConfig = msgspec.field(default_factory=ScheduleConfig)
params: dict = msgspec.field(default_factory=dict)
adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)
h_params: dict = msgspec.field(default_factory=dict)
⋮----
def __post_init__(self)
⋮----
def to_yaml(self, path: str, fs: AbstractFileSystem)
⋮----
d = self.to_dict()
⋮----
@classmethod
    def from_dict(cls, name: str, data: dict | Munch)
⋮----
@classmethod
    def from_yaml(cls, name: str, path: str, fs: AbstractFileSystem)
⋮----
data = yaml.full_load(f)
⋮----
def update(self, d: dict | Munch)
⋮----
# self.params = munchify(self.params)
⋮----
@staticmethod
    def to_h_params(d: dict) -> dict
⋮----
"""Convert a dictionary of parameters to Hamilton-compatible format.

        This method transforms regular parameter dictionaries into Hamilton's function parameter
        format, supporting nested parameters and source/value decorators.

        Args:
            d (dict): The input parameter dictionary.

        Returns:
            dict: Hamilton-formatted parameter dictionary.

        Example:
            ```python
            params = {
                "batch_size": 100,
                "paths": {"input": "data/in", "output": "data/out"}
            }
            h_params = PipelineConfig.to_h_params(params)
            ```
        """
⋮----
def transform_recursive(val, original_dict, depth=1)
⋮----
# If we're at depth 3, wrap the entire dictionary in value()
⋮----
# Otherwise, continue recursing
⋮----
# If it's a string and matches a key in the original dictionary
⋮----
# For non-dictionary values at depth 3
⋮----
# For all other values
⋮----
# Step 1: Replace each value with a dictionary containing key and value
result = {k: {k: d[k]} for k in d}
⋮----
# Step 2: Transform all values recursively
⋮----
"""Load pipeline configuration from a YAML file.

        Args:
            base_dir (str, optional): Base directory for the pipeline. Defaults to ".".
            name (str | None, optional): Pipeline name. Defaults to None.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Returns:
            PipelineConfig: Loaded pipeline configuration.

        Example:
            ```python
            pipeline = PipelineConfig.load(
                base_dir="my_project",
                name="data-pipeline"
            )
            ```
        """
⋮----
fs = get_filesystem(
⋮----
pipeline = PipelineConfig.from_yaml(
⋮----
pipeline = PipelineConfig(name=name)
⋮----
"""Save pipeline configuration to a YAML file.

        Args:
            name (str | None, optional): Pipeline name. Defaults to None.
            base_dir (str, optional): Base directory for the pipeline. Defaults to ".".
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Raises:
            ValueError: If pipeline name is not set.

        Example:
            ```python
            pipeline_config.save(name="data-pipeline", base_dir="my_project")
            ```
        """
⋮----
h_params = getattr(self, "h_params")
⋮----
"""Initialize a new pipeline configuration.

    This function creates a new pipeline configuration and saves it to disk.

    Args:
        base_dir (str, optional): Base directory for the pipeline. Defaults to ".".
        name (str | None, optional): Pipeline name. Defaults to None.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

    Returns:
        PipelineConfig: The initialized pipeline configuration.

    Example:
        ```python
        pipeline = init_pipeline_config(
            base_dir="my_project",
            name="etl-pipeline"
        )
        ```
    """
pipeline = PipelineConfig.load(
````

## File: src/flowerpower/cfg/__init__.py
````python
class Config(BaseConfig)
⋮----
"""Main configuration class for FlowerPower, combining project and pipeline settings.

    This class serves as the central configuration manager, handling both project-wide
    and pipeline-specific settings. It provides functionality for loading and saving
    configurations using various filesystem abstractions.

    Attributes:
        pipeline (PipelineConfig): Configuration for the pipeline.
        project (ProjectConfig): Configuration for the project.
        fs (AbstractFileSystem | None): Filesystem abstraction for I/O operations.
        base_dir (str | Path | None): Base directory for the configuration.
        storage_options (dict | Munch): Options for filesystem operations.

    Example:
        ```python
        # Load configuration
        config = Config.load(
            base_dir="my_project",
            name="project1",
            pipeline_name="data-pipeline"
        )

        # Save configuration
        config.save(project=True, pipeline=True)
        ```
    """
⋮----
pipeline: PipelineConfig = msgspec.field(default_factory=PipelineConfig)
project: ProjectConfig = msgspec.field(default_factory=ProjectConfig)
fs: AbstractFileSystem | None = None
base_dir: str | Path | None = None
storage_options: dict | Munch = msgspec.field(default_factory=Munch)
⋮----
"""Load both project and pipeline configurations.

        Args:
            base_dir (str, optional): Base directory for configurations. Defaults to ".".
            name (str | None, optional): Project name. Defaults to None.
            pipeline_name (str | None, optional): Pipeline name. Defaults to None.
            job_queue_type (str | None, optional): Type of job queue to use. Defaults to None.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Returns:
            Config: Combined configuration instance.

        Example:
            ```python
            config = Config.load(
                base_dir="my_project",
                name="test_project",
                pipeline_name="etl",
                job_queue_type="rq"
            )
            ```
        """
⋮----
fs = get_filesystem(
project = ProjectConfig.load(
pipeline = PipelineConfig.load(
⋮----
"""Save project and/or pipeline configurations.

        Args:
            project (bool, optional): Whether to save project config. Defaults to False.
            pipeline (bool, optional): Whether to save pipeline config. Defaults to True.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Example:
            ```python
            config.save(project=True, pipeline=True)
            ```
        """
⋮----
h_params = self.pipeline.pop("h_params") if self.pipeline.h_params else None
⋮----
"""Helper function to load configuration.

    This is a convenience wrapper around Config.load().

    Args:
        base_dir (str): Base directory for configurations.
        name (str | None, optional): Project name. Defaults to None.
        pipeline_name (str | None, optional): Pipeline name. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.

    Returns:
        Config: Combined configuration instance.

    Example:
        ```python
        config = load(base_dir="my_project", name="test", pipeline_name="etl")
        ```
    """
⋮----
"""Helper function to save configuration.

    This is a convenience wrapper around Config.save().

    Args:
        config (Config): Configuration instance to save.
        project (bool, optional): Whether to save project config. Defaults to False.
        pipeline (bool, optional): Whether to save pipeline config. Defaults to True.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

    Example:
        ```python
        config = load(base_dir="my_project")
        save(config, project=True, pipeline=True)
        ```
    """
⋮----
"""Initialize a new configuration with both project and pipeline settings.

    This function creates and initializes both project and pipeline configurations,
    combining them into a single Config instance.

    Args:
        base_dir (str, optional): Base directory for configurations. Defaults to ".".
        name (str | None, optional): Project name. Defaults to None.
        pipeline_name (str | None, optional): Pipeline name. Defaults to None.
        job_queue_type (str | None, optional): Type of job queue to use. Defaults to None.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

    Returns:
        Config: The initialized configuration instance.

    Example:
        ```python
        config = init_config(
            base_dir="my_project",
            name="test_project",
            pipeline_name="data-pipeline",
            job_queue_type="rq"
        )
        ```
    """
pipeline_cfg = init_pipeline_config(
project_cfg = init_project_config(
````

## File: src/flowerpower/job_queue/base.py
````python
"""
Base scheduler interface for FlowerPower.

This module defines the abstract base classes for scheduling operations
that can be implemented by different backend providers (APScheduler, RQ, etc.).
"""
⋮----
create_async_engine = None
AsyncEngine = TypeVar("AsyncEngine")
⋮----
# from ..utils.misc import update_config_from_dict
⋮----
class BackendType(str, Enum)
⋮----
POSTGRESQL = "postgresql"
MYSQL = "mysql"
SQLITE = "sqlite"
MONGODB = "mongodb"
MQTT = "mqtt"
REDIS = "redis"
NATS_KV = "nats_kv"
MEMORY = "memory"
⋮----
@property
    def properties(self)
⋮----
@property
    def uri_prefix(self) -> str
⋮----
@property
    def default_port(self)
⋮----
@property
    def default_host(self) -> str
⋮----
@property
    def default_username(self) -> str
⋮----
@property
    def default_password(self) -> str
⋮----
@property
    def default_database(self) -> str
⋮----
@property
    def is_sqla_type(self) -> bool
⋮----
@property
    def is_mongodb_type(self) -> bool
⋮----
@property
    def is_mqtt_type(self) -> bool
⋮----
@property
    def is_redis_type(self) -> bool
⋮----
@property
    def is_nats_kv_type(self) -> bool
⋮----
@property
    def is_memory_type(self) -> bool
⋮----
@property
    def is_sqlite_type(self) -> bool
⋮----
# Handle host and port
host = host or self.default_host
port = port or self.default_port
database = database or self.default_database
username = username or self.default_username
password = password or self.default_password
⋮----
# components: List[str] = []
# Get the appropriate URI prefix based on backend type and SSL setting
⋮----
uri_prefix = "rediss://" if ssl else "redis://"
⋮----
uri_prefix = "nats+tls://" if ssl else "nats://"
⋮----
uri_prefix = "mqtts://" if ssl else "mqtt://"
⋮----
port = 8883
⋮----
uri_prefix = self.uri_prefix
⋮----
# Handle authentication
⋮----
auth = f"{urllib.parse.quote(username)}:{urllib.parse.quote(password)}@"
⋮----
auth = f"{urllib.parse.quote(username)}@"
⋮----
auth = f":{urllib.parse.quote(password)}@"
⋮----
auth = ""
⋮----
port_part = f":{port}"  # if port is not None else self.default_port
⋮----
# Special handling for SQLite and memory types
⋮----
# Build path component
⋮----
path = f"/{database}" if database else ""
⋮----
# Construct base URI
base_uri = f"{uri_prefix}{auth}{host}{port_part}{path}"
⋮----
# Prepare query parameters for SSL files
query_params: list[str] = []
⋮----
# Always add ssl query parameter if ssl=True
⋮----
# Compose query string if Any params exist
query_string = ""
⋮----
query_string = "?" + "&".join(query_params)
⋮----
@dataclass(slots=True)
class BaseBackend
⋮----
type: BackendType | str | None = None
uri: str | None = None
username: str | None = None
password: str | None = None
host: str | None = None
port: int | None = None
database: str | None = None
ssl: bool = False
ca_file: str | None = None
cert_file: str | None = None
key_file: str | None = None
verify_ssl: bool = False
_kwargs: dict = field(default_factory=dict)
_sqla_engine: AsyncEngine | None = (
⋮----
None  # SQLAlchemy async engine instance for SQL backends
⋮----
_client: Any | None = None  # Native client instance for non-SQL backends
⋮----
def __post_init__(self)
⋮----
# Setup is handled by backend-specific implementations
⋮----
@classmethod
    def from_dict(cls, d: dict) -> "BaseBackend"
⋮----
class BaseTrigger(abc.ABC)
⋮----
"""
    Abstract base class for schedule triggers.

    A trigger determines when a scheduled job should be executed.
    """
⋮----
def __init__(self, trigger_type: str)
⋮----
@abc.abstractmethod
    def get_trigger_instance(self, **kwargs) -> Any
⋮----
"""
        Get the backend-specific trigger instance.

        Args:
            **kwargs: Keyword arguments specific to the trigger type

        Returns:
            Any: A backend-specific trigger instance
        """
⋮----
class BaseJobQueueManager
⋮----
"""
    Abstract base class for scheduler workers (APScheduler, RQ, etc.).
    Defines the required interface for all scheduler backends.

    Can be used as a context manager:

    ```python
    with RQManager(name="test") as manager:
        manager.add_job(job1)
    ```
    """
⋮----
def __enter__(self)
⋮----
"""Context manager entry - returns self for use in with statement."""
⋮----
def __exit__(self, exc_type, exc_val, exc_tb)
⋮----
"""Context manager exit - ensures workers are stopped."""
⋮----
return False  # Don't suppress exceptions
⋮----
"""
        Initialize the APScheduler backend.

        Args:
            name: Name of the scheduler
            base_dir: Base directory for the FlowerPower project
            backend: APSBackend instance with data store and event broker
            storage_options: Storage options for filesystem access
            fs: Filesystem to use
            cfg_override: Configuration overrides for the worker
        """
⋮----
fs = get_filesystem(self._base_dir, **(self._storage_options or {}))
⋮----
def _load_config(self) -> None
⋮----
"""Load the configuration.

        Args:
            cfg_updates: Configuration updates to apply
        """
⋮----
def _add_modules_path(self)
⋮----
"""
        Sync the filesystem.

        Returns:
            None
        """
⋮----
modules_path = posixpath.join(self._fs.path, self._pipelines_dir)
````

## File: src/flowerpower/pipeline/job_queue.py
````python
# -*- coding: utf-8 -*-
# pylint: disable=logging-fstring-interpolation
# flake8: noqa: E501
"""Pipeline Job Queue."""
⋮----
# Import necessary config types
⋮----
class PipelineJobQueue
⋮----
"""Handles scheduling of pipeline runs via a configured job queue backend."""
⋮----
"""Initialize PipelineJobQueue.

        Args:
            project_cfg: The project configuration object.
            fs: The file system to use for file operations.
            cfg_dir: The directory for configuration files.
            pipelines_dir: The directory for pipeline files.
            job_queue_type: The type of job queue to use (e.g., 'rq', 'apscheduler'). If None, defaults to the project config.
        """
⋮----
# Fallback or default if not specified in project config
⋮----
@property
    def job_queue(self)
⋮----
"""
        Lazily instantiate and cache a Job queue instance.
        """
# Lazily instantiate job queue using project_cfg attributes
⋮----
# Pass the necessary parts of project_cfg to the Job queue
⋮----
def _get_schedule_ids(self) -> list[Any]
⋮----
"""Get all schedules from the job queue backend."""
⋮----
name: str,  # name: str,
⋮----
"""
        Add a job to run the pipeline immediately via the job queue queue.

        Args:
            run_func (Callable): The function to execute in the job queue (e.g., a configured PipelineRunner.run).
            name (str): The name of the pipeline (used for logging).
            inputs (dict | None): Inputs for the pipeline run.
            final_vars (list | None): Final variables for the pipeline run.
            config (dict | None): Hamilton driver config.
            cache (bool | dict): Cache configuration.
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration.
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter configuration.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline adapter configuration.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project adapter configuration.
            adapter (dict[str, Any] | None): Additional adapter configuration.
            reload (bool): Whether to reload the pipeline module.
            log_level (str | None): Log level for the run.
            max_retries (int): Maximum number of retries for the job.
            retry_delay (float): Delay between retries.
            jitter_factor (float): Jitter factor for retry delay.
            retry_exceptions (tuple): Exceptions that should trigger a retry.
            **kwargs: Additional keyword arguments passed directly to the job queue's add_job method.

        Returns:
            dict[str, Any]: The result of the job execution.
        """
⋮----
pipeline_run_args = {
⋮----
# 'name' is not passed to run_func, it's part of the context already in PipelineRunner
⋮----
res = job_queue.run_job(
⋮----
run_func: Callable,  # The actual function to run (e.g., PipelineRunner(...).run)
⋮----
**kwargs,  # Allow other job queue-specific args if needed
⋮----
"""
        Add a job to run the pipeline immediately via the job queue, storing the result.

        Executes the job immediately and returns the job id (UUID). The job result will be stored
        by the job queue backend for the given `result_ttl` and can be fetched using the job id.

        Args:
            run_func (Callable): The function to execute in the job queue (e.g., a configured PipelineRunner.run).
            name (str): The name of the pipeline (used for logging).
            inputs (dict | None): Inputs for the pipeline run.
            final_vars (list | None): Final variables for the pipeline run.
            config (dict | None): Hamilton driver config.
            cache (bool | dict): Cache configuration.
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration.
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter configuration.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline adapter configuration.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project adapter configuration.
            adapter (dict[str, Any] | None): Additional adapter configuration.
            reload (bool): Whether to reload the pipeline module.
            log_level (str | None): Log level for the run.
            result_ttl (int | dt.timedelta): How long the job result should be stored. Defaults to 0 (don't store).
            run_at (dt.datetime | None): Optional datetime to run the job at.
            run_in (float | dt.timedelta | None): Optional delay before running the job.
            max_retries (int): Maximum number of retries for the job.
            retry_delay (float): Delay between retries.
            jitter_factor (float): Jitter factor for retry delay.
            retry_exceptions (tuple): Exceptions that should trigger a retry.
            **kwargs: Additional keyword arguments passed directly to the job queue's add_job method.

        Returns:
            Any: The ID of the added job or the job object itself, depending on the job queue backend.
        """
⋮----
job = job_queue.add_job(
⋮----
# --- End Moved from PipelineManager ---
⋮----
# --- Run Parameters (passed to run_func) ---
⋮----
config: dict | None = None,  # Driver config
⋮----
# --- Schedule Parameters (passed to job queue.add_schedule) ---
⋮----
"""
        Schedule a pipeline for execution using the configured job queue.

        Args:
            run_func (Callable): The function to execute in the job queue.
            pipeline_cfg (PipelineConfig): The pipeline configuration object.
            inputs (dict | None): Inputs for the pipeline run (overrides config).
            final_vars (list | None): Final variables for the pipeline run (overrides config).
            config (dict | None): Hamilton driver config (overrides config).
            cache (bool | dict): Cache configuration (overrides config).
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration (overrides config).
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter configuration (overrides config).
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline adapter configuration (overrides config).
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project adapter configuration (overrides config).
            adapter (dict | None): Additional Hamilton adapters (overrides config).
            reload (bool): Whether to reload module (overrides config).
            log_level (str | None): Log level for the run (overrides config).
            max_retries (int): Maximum number of retries for the job.
            retry_delay (float): Delay between retries.
            jitter_factor (float): Jitter factor for retry delay.
            retry_exceptions (tuple): Exceptions that should trigger a retry.
            cron (str | dict | None): Cron expression or dict for cron trigger.
            interval (int | str | dict | None): Interval in seconds or dict for interval trigger.
            date (dt.datetime | None): Date for date trigger.
            overwrite (bool): If True and id_ is None, generates ID '{name}-1', potentially overwriting.
            schedule_id (str | None): Optional ID for the schedule. If None, generates a new ID.
            **kwargs: Additional keyword arguments passed to the job queue's add_schedule method,
                For RQ this includes:
                    - repeat: Repeat count (int or dict)
                    - result_ttl: Time to live for the job result (float or timedelta)
                    - ttl: Time to live for the job (float or timedelta)
                    - use_local_time_zone: Whether to use local time zone for scheduling (bool)
                For APScheduler, this includes:
                    - misfire_grace_time: Grace time for misfires (timedelta)
                    - coalesce: Whether to coalesce jobs (bool)
                    - max_running_jobs: Maximum instances of the job (int)
                    - max_jitter: Maximum jitter for scheduling (int)
                    - conflict_policy: Policy for conflicting jobs (str)
                    - paused: Whether to pause the job (bool)


        Returns:
            str | UUID: The ID of the scheduled pipeline.

        Raises:
            ValueError: If trigger_type is invalid or required args are missing.
            Exception: Can raise exceptions from the job queue backend.
        """
⋮----
project_name = self.project_cfg.name
name = pipeline_cfg.name
⋮----
# --- Resolve Parameters using pipeline_cfg for defaults ---
schedule_cfg = pipeline_cfg.schedule
# run_cfg = pipeline_cfg.run
⋮----
cron = cron if cron is not None else schedule_cfg.cron
interval = interval if interval is not None else schedule_cfg.interval
date = date if date is not None else schedule_cfg.date
⋮----
# --- Generate ID if not provided ---
# (Keep _generate_id function as is, it uses self._get_schedules())
⋮----
base_id = f"{pipeline_name}-1"
⋮----
existing_ids = self._get_schedule_ids()
⋮----
# Find highest existing number for this pipeline name
max_num = 0
⋮----
num_part = id_val.split("-")[-1]
num = int(num_part)
⋮----
max_num = num
⋮----
continue  # Skip malformed IDs
⋮----
new_id = f"{pipeline_name}-{max_num + 1}"
⋮----
# Fallback in case of error fetching schedules
⋮----
schedule_id = _generate_id(name, schedule_id, overwrite)
⋮----
# --- Add Schedule via Job queue ---
⋮----
# Job queue is now responsible for creating the trigger object
# Pass trigger type and kwargs directly
added_id = job_queue.add_schedule(
⋮----
func_kwargs=pipeline_run_args,  # Pass resolved run parameters
⋮----
**kwargs,  # Pass resolved schedule run parameters
⋮----
# --- schedule_all method removed ---
# PipelineManager will be responsible for iterating and calling schedule()
⋮----
def schedule_all(self, registry: PipelineRegistry, **kwargs)
⋮----
"""
        Schedule all pipelines found by the registry.

        Args:
            **kwargs: Arguments passed directly to the `schedule` method for each pipeline.
                      Note: Pipeline-specific configurations will still take precedence for
                      defaults if not overridden by kwargs.
        """
⋮----
registry = self._get_registry_func()
names = registry._get_names()  # Use registry to find pipelines
⋮----
scheduled_ids = []
errors = []
⋮----
# Load config specifically for this pipeline to get defaults
# Note: schedule() will load it again, potential optimization later
cfg = self._load_config_func(name=name)
⋮----
# Pass kwargs, allowing overrides of config defaults
schedule_id = self.schedule(name=name, **kwargs)
````

## File: src/flowerpower/fs/__init__.py
````python
has_orjson = importlib.util.find_spec("orjson") is not None
has_polars = importlib.util.find_spec("polars") is not None
⋮----
from .base import get_filesystem  # noqa: E402
from .storage_options import AwsStorageOptions  # noqa: E402
from .storage_options import AzureStorageOptions  # noqa: E402
⋮----
__all__ = [
````

## File: src/flowerpower/settings.py
````python
PIPELINES_DIR = os.getenv("FP_PIPELINES_DIR", "pipelines")
CONFIG_DIR = os.getenv("FP_CONFIG_DIR", "conf")
HOOKS_DIR = os.getenv("FP_HOOKS_DIR", "hooks")
⋮----
# EXECUTOR
EXECUTOR = os.getenv("FP_EXECUTOR", "threadpool")
EXECUTOR_MAX_WORKERS = int(
EXECUTOR_NUM_CPUS = int(os.getenv("FP_EXECUTOR_NUM_CPUS", os.cpu_count() or 1))
⋮----
# RETRY
MAX_RETRIES = int(os.getenv("FP_MAX_RETRIES", 1))
RETRY_DELAY = float(os.getenv("FP_RETRY_DELAY", 1.0))
JITTER_FACTOR = float(os.getenv("FP_JITTER_FACTOR", 0.1))
⋮----
# LOGGING
LOG_LEVEL = os.getenv("FP_LOG_LEVEL", "INFO")
⋮----
# WORKER
DEFAULT_JOB_QUEUE = os.getenv("FP_JOB_QUEUE_TYPE", "rq")
# RQ WORKER
RQ_BACKEND = os.getenv("FP_RQ_BACKEND", "redis")
RQ_QUEUES = (
RQ_NUM_WORKERS = int(os.getenv("FP_RQ_NUM_WORKERS", EXECUTOR_NUM_CPUS))
⋮----
# APS WORKER
APS_BACKEND_DS = os.getenv("FP_APS_DS_BACKEND", "postgresql")
APS_SCHEMA_DS = os.getenv("FP_APS_SCHEMA", "flowerpower")
APS_BACKEND_EB = os.getenv("FP_APS_EB_BACKEND", "postgresql")
APS_CLEANUP_INTERVAL = int(os.getenv("FP_APS_CLEANUP_INTERVAL", 300))
APS_MAX_CONCURRENT_JOBS = int(os.getenv("FP_APS_MAX_CONCURRENT_JOBS", 10))
APS_DEFAULT_EXECUTOR = os.getenv("FP_APS_DEFAULT_EXECUTOR", EXECUTOR)
APS_NUM_WORKERS = int(os.getenv("FP_APS_NUM_WORKERS", EXECUTOR_MAX_WORKERS))
⋮----
# Define backend properties in a dictionary for easier maintenance
BACKEND_PROPERTIES = {
⋮----
# HAMILTON
HAMILTON_MAX_LIST_LENGTH_CAPTURE = int(
HAMILTON_MAX_DICT_LENGTH_CAPTURE = int(
HAMILTON_CAPTURE_DATA_STATISTICS = bool(
⋮----
HAMILTON_AUTOLOAD_EXTENSIONS = int(os.getenv("HAMILTON_AUTOLOAD_EXTENSIONS", 0))
HAMILTON_TELEMETRY_ENABLED = bool(os.getenv("HAMILTON_TELEMETRY_ENABLED", False))
HAMILTON_API_URL = os.getenv("HAMILTON_API_URL", "http://localhost:8241")
HAMILTON_UI_URL = os.getenv("HAMILTON_UI_URL", "http://localhost:8242")
````

## File: src/flowerpower/cfg/project/__init__.py
````python
class ProjectConfig(BaseConfig)
⋮----
"""A configuration class for managing project-level settings in FlowerPower.

    This class handles project-wide configuration including job queue and adapter settings.
    It supports loading from and saving to YAML files, with filesystem abstraction.

    Attributes:
        name (str | None): The name of the project.
        job_queue (JobQueueConfig): Configuration for the job queue component.
        adapter (AdapterConfig): Configuration for the adapter component.

    Example:
        ```python
        # Create a new project config
        project = ProjectConfig(name="my-project")

        # Load existing project config
        project = ProjectConfig.load(base_dir="path/to/project")

        # Save project config
        project.save(base_dir="path/to/project")
        ```
    """
⋮----
name: str | None = msgspec.field(default=None)
job_queue: JobQueueConfig = msgspec.field(default_factory=JobQueueConfig)
adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)
⋮----
def __post_init__(self)
⋮----
"""Load project configuration from a YAML file.

        Args:
            base_dir (str, optional): Base directory for the project. Defaults to ".".
            name (str | None, optional): Project name. Defaults to None.
            job_queue_type (str | None, optional): Type of job queue to use. Defaults to None.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Returns:
            ProjectConfig: Loaded project configuration.

        Example:
            ```python
            project = ProjectConfig.load(
                base_dir="my_project",
                name="pipeline1",
                job_queue_type="rq"
                )
            ```
        """
⋮----
fs = get_filesystem(
⋮----
project = ProjectConfig.from_yaml(path="conf/project.yml", fs=fs)
⋮----
project = ProjectConfig(name=name)
⋮----
"""Save project configuration to a YAML file.

        Args:
            base_dir (str, optional): Base directory for the project. Defaults to ".".
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Example:
            ```python
            project_config.save(base_dir="my_project")
            ```
        """
⋮----
"""Initialize a new project configuration.

    This function creates a new project configuration and saves it to disk.

    Args:
        base_dir (str, optional): Base directory for the project. Defaults to ".".
        name (str | None, optional): Project name. Defaults to None.
        job_queue_type (str | None, optional): Type of job queue to use. Defaults to None.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

    Returns:
        ProjectConfig: The initialized project configuration.

    Example:
        ```python
        project = init_project_config(
            base_dir="my_project",
            name="test_project",
            job_queue_type="rq"
        )
        ```
    """
project = ProjectConfig.load(
````

## File: src/flowerpower/cli/pipeline.py
````python
# Import necessary libraries
⋮----
from .utils import parse_dict_or_list_param  # , parse_param_dict
⋮----
app = typer.Typer(help="Pipeline management commands")
⋮----
"""
    Run a pipeline immediately.

    This command executes a pipeline with the specified configuration and inputs.
    The pipeline will run synchronously, and the command will wait for completion.

    Args:
        name: Name of the pipeline to run
        executor: Type of executor to use
        base_dir: Base directory containing pipelines and configurations
        inputs: Input parameters for the pipeline
        final_vars: Final variables to request from the pipeline
        config: Configuration for the Hamilton executor
        cache: Cache configuration for improved performance
        storage_options: Options for storage backends
        log_level: Set the logging level
        with_adapter: Configuration for adapters like trackers or monitors
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Base delay between retries in seconds
        jitter_factor: Random factor applied to delay for jitter (0-1)

    Examples:
        # Run a pipeline with default settings
        $ pipeline run my_pipeline

        # Run with custom inputs
        $ pipeline run my_pipeline --inputs '{"data_path": "data/myfile.csv", "limit": 100}'

        # Specify which final variables to calculate
        $ pipeline run my_pipeline --final-vars '["output_table", "summary_metrics"]'

        # Configure caching
        $ pipeline run my_pipeline --cache '{"type": "memory", "ttl": 3600}'

        # Use a different executor
        $ pipeline run my_pipeline --executor distributed

        # Enable adapters for monitoring/tracking
        $ pipeline run my_pipeline --with-adapter '{"tracker": true, "opentelemetry": true}'

        # Set a specific logging level
        $ pipeline run my_pipeline --log-level debug

        # Configure automatic retries on failure
        $ pipeline run my_pipeline --max-retries 3 --retry-delay 2.0 --jitter-factor 0.2
    """
parsed_inputs = parse_dict_or_list_param(inputs, "dict")
parsed_config = parse_dict_or_list_param(config, "dict")
parsed_cache = parse_dict_or_list_param(cache, "dict")
parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")
parsed_with_adapter = parse_dict_or_list_param(with_adapter, "dict")
⋮----
_ = manager.run(
⋮----
"""
    Run a specific pipeline job.

    This command runs an existing job by its ID. The job should have been previously
    added to the system via the add-job command or through scheduling.

    Args:
        name: Job ID to run
        executor: Type of executor to use (maps to executor_cfg in manager)
        base_dir: Base directory containing pipelines and configurations
        inputs: Input parameters for the pipeline
        final_vars: Final variables to request from the pipeline
        config: Configuration for the Hamilton executor
        cache: Cache configuration
        storage_options: Options for storage backends
        log_level: Set the logging level
        with_adapter: Configuration for adapters like trackers or monitors
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Base delay between retries in seconds
        jitter_factor: Random factor applied to delay for jitter (0-1)

    Examples:
        # Run a job with a specific ID
        $ pipeline run-job job-123456

        # Run a job with custom inputs
        $ pipeline run-job job-123456 --inputs '{"data_path": "data/myfile.csv"}'

        # Specify a different executor
        $ pipeline run-job job-123456 --executor local

        # Use caching for better performance
        $ pipeline run-job job-123456 --cache '{"type": "memory"}'

        # Configure adapters for monitoring
        $ pipeline run-job job-123456 --with-adapter '{"tracker": true, "opentelemetry": false}'

        # Set up automatic retries for resilience
        $ pipeline run-job job-123456 --max-retries 3 --retry-delay 2.0
    """
⋮----
_ = manager.run_job(
⋮----
"""
    Add a pipeline job to the queue.

    This command adds a job to the queue for later execution. The job is based on
    an existing pipeline with customized inputs and configuration.

    Args:
        name: Pipeline name to add as a job
        executor: Type of executor to use
        base_dir: Base directory containing pipelines and configurations
        inputs: Input parameters for the pipeline
        final_vars: Final variables to request from the pipeline
        config: Configuration for the Hamilton executor
        cache: Cache configuration
        storage_options: Options for storage backends
        log_level: Set the logging level
        with_adapter: Configuration for adapters like trackers or monitors
        run_at: Run the job at a specific time (ISO format)
        run_in: Run the job in a specific interval (e.g., '5m', '1h')
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Base delay between retries in seconds
        jitter_factor: Random factor applied to delay for jitter (0-1)

    Examples:
        # Add a basic job
        $ pipeline add-job my_pipeline

        # Add a job with custom inputs
        $ pipeline add-job my_pipeline --inputs '{"data_path": "data/myfile.csv"}'

        # Specify final variables to calculate
        $ pipeline add-job my_pipeline --final-vars '["output_table", "metrics"]'

        # Configure caching
        $ pipeline add-job my_pipeline --cache '{"type": "memory", "ttl": 3600}'

        # Use a specific log level
        $ pipeline add-job my_pipeline --log-level debug

        # Configure automatic retries for resilience
        $ pipeline add-job my_pipeline --max-retries 5 --retry-delay 2.0 --jitter-factor 0.2
    """
⋮----
run_at = dt.datetime.fromisoformat(run_at) if run_at else None
run_in = duration_parser.parse(run_in) if run_in else None
⋮----
job_id = manager.add_job(
⋮----
"""
    Schedule a pipeline to run at specified times.

    This command schedules a pipeline to run automatically based on various
    scheduling triggers like cron expressions, time intervals, or specific dates.

    Args:
        name: Pipeline name to schedule
        executor: Type of executor to use
        base_dir: Base directory containing pipelines and configurations
        inputs: Input parameters for the pipeline
        final_vars: Final variables to request from the pipeline
        config: Configuration for the Hamilton executor
        cache: Cache configuration
        cron: Cron expression for scheduling (e.g., "0 * * * *")
        interval: Interval for scheduling (e.g., "5m", "1h")
        date: Specific date and time for scheduling (ISO format)
        storage_options: Options for storage backends
        log_level: Set the logging level
        with_adapter: Configuration for adapters like trackers or monitors
        overwrite: Overwrite existing schedule with same ID
        schedule_id: Custom identifier for the schedule
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Base delay between retries in seconds
        jitter_factor: Random factor applied to delay for jitter (0-1)

    Examples:
        # Schedule with cron expression (every hour)
        $ pipeline schedule my_pipeline --trigger-type cron --crontab "0 * * * *"

        # Schedule to run every 15 minutes
        $ pipeline schedule my_pipeline --trigger-type interval --interval_params minutes=15

        # Schedule to run at a specific date and time
        $ pipeline schedule my_pipeline --trigger-type date --date_params run_date="2025-12-31 23:59:59"

        # Schedule with custom inputs and cache settings
        $ pipeline schedule my_pipeline --inputs '{"source": "database"}' --cache '{"type": "redis"}'

        # Create a schedule in paused state
        $ pipeline schedule my_pipeline --crontab "0 9 * * 1-5" --paused

        # Set a custom schedule ID
        $ pipeline schedule my_pipeline --crontab "0 12 * * *" --schedule_id "daily-noon-run"

        # Configure automatic retries for resilience
        $ pipeline schedule my_pipeline --max-retries 5 --retry-delay 2.0 --jitter-factor 0.2
    """
⋮----
interval = duration_parser.parse(interval) if interval else None
cron = cron if cron else None
date = dt.datetime.fromisoformat(date) if date else None
⋮----
# Combine common schedule kwargs
⋮----
id_ = manager.schedule(
⋮----
"""
    Schedule all pipelines based on their individual configurations.

    This command reads the configuration files for all pipelines in the project
    and schedules them based on their individual scheduling settings. This is useful
    for setting up all scheduled pipelines at once after deployment or system restart.

    Args:
        executor: Override executor specified in pipeline configs
        base_dir: Base directory containing pipelines and configurations
        storage_options: Options for storage backends
        log_level: Set the logging level
        overwrite: Whether to overwrite existing schedules

    Examples:
        # Schedule all pipelines using their configurations
        $ pipeline schedule-all

        # Force overwrite of existing schedules
        $ pipeline schedule-all --overwrite

        # Override executor for all pipelines
        $ pipeline schedule-all --executor distributed

        # Set custom base directory
        $ pipeline schedule-all --base-dir /path/to/project
    """
⋮----
"""
    Create a new pipeline structure.

    This command creates a new pipeline with the necessary directory structure,
    configuration file, and skeleton module file. It prepares all the required
    components for you to start implementing your pipeline logic.

    Args:
        name: Name for the new pipeline
        base_dir: Base directory to create the pipeline in
        storage_options: Options for storage backends
        log_level: Set the logging level
        overwrite: Whether to overwrite existing pipeline with the same name

    Examples:
        # Create a new pipeline with default settings
        $ pipeline new my_new_pipeline

        # Create a pipeline, overwriting if it exists
        $ pipeline new my_new_pipeline --overwrite

        # Create a pipeline in a specific directory
        $ pipeline new my_new_pipeline --base-dir /path/to/project
    """
⋮----
"""
    Delete a pipeline's configuration and/or module files.

    This command removes a pipeline's configuration file and/or module file from the project.
    If neither --cfg nor --module is specified, both will be deleted.

    Args:
        name: Name of the pipeline to delete
        base_dir: Base directory containing the pipeline
        cfg: Delete only the configuration file
        module: Delete only the pipeline module
        storage_options: Options for storage backends
        log_level: Set the logging level

    Examples:
        # Delete a pipeline (both config and module)
        $ pipeline delete my_pipeline

        # Delete only the configuration file
        $ pipeline delete my_pipeline --cfg

        # Delete only the module file
        $ pipeline delete my_pipeline --module
    """
⋮----
# If neither flag is set, default to deleting both
delete_cfg = cfg or not (cfg or module)
delete_module = module or not (cfg or module)
⋮----
deleted_parts = []
⋮----
"""
    Show the DAG (Directed Acyclic Graph) of a pipeline.

    This command generates and displays a visual representation of the pipeline's
    execution graph, showing how nodes are connected and dependencies between them.

    Args:
        name: Name of the pipeline to visualize
        base_dir: Base directory containing the pipeline
        storage_options: Options for storage backends
        log_level: Set the logging level
        format: Output format for the visualization

    Examples:
        # Show pipeline DAG in PNG format (default)
        $ pipeline show-dag my_pipeline

        # Generate SVG format visualization
        $ pipeline show-dag my_pipeline --format svg

        # Get raw graphviz object
        $ pipeline show-dag my_pipeline --format raw
    """
⋮----
is_raw = format.lower() == "raw"
⋮----
# Manager's show_dag likely handles rendering or returning raw object
⋮----
graph_or_none = manager.show_dag(
⋮----
# print(graph_or_none) # Or handle as needed
⋮----
"""
    Save the DAG (Directed Acyclic Graph) of a pipeline to a file.

    This command generates a visual representation of the pipeline's execution graph
    and saves it to a file in the specified format.

    Args:
        name: Name of the pipeline to visualize
        base_dir: Base directory containing the pipeline
        storage_options: Options for storage backends
        log_level: Set the logging level
        format: Output format for the visualization
        output_path: Custom file path to save the output (defaults to pipeline name)

    Examples:
        # Save pipeline DAG in PNG format (default)
        $ pipeline save-dag my_pipeline

        # Save in SVG format
        $ pipeline save-dag my_pipeline --format svg

        # Save to a custom location
        $ pipeline save-dag my_pipeline --output-path ./visualizations/my_graph.png
    """
⋮----
file_path = manager.save_dag(
⋮----
"""
    List all available pipelines in the project.

    This command displays a list of all pipelines defined in the project,
    providing an overview of what pipelines are available to run or schedule.

    Args:
        base_dir: Base directory containing pipelines
        storage_options: Options for storage backends
        log_level: Set the logging level
        format: Output format for the list (table, json, yaml)

    Examples:
        # List all pipelines in table format (default)
        $ pipeline show-pipelines

        # Output in JSON format
        $ pipeline show-pipelines --format json

        # List pipelines from a specific directory
        $ pipeline show-pipelines --base-dir /path/to/project
    """
⋮----
"""
    Show summary information for one or all pipelines.

    This command displays detailed information about pipelines including their
    configuration, code structure, and project context. You can view information
    for a specific pipeline or get an overview of all pipelines.

    Args:
        name: Name of specific pipeline to summarize (all if not specified)
        cfg: Include configuration details
        code: Include code/module details
        project: Include project context information
        base_dir: Base directory containing pipelines
        storage_options: Options for storage backends
        log_level: Set the logging level
        to_html: Generate HTML output instead of text
        to_svg: Generate SVG output (where applicable)
        output_file: File path to save the output instead of printing to console

    Examples:
        # Show summary for all pipelines
        $ pipeline show-summary

        # Show summary for a specific pipeline
        $ pipeline show-summary --name my_pipeline

        # Show only configuration information
        $ pipeline show-summary --name my_pipeline --cfg --no-code --no-project

        # Generate HTML report
        $ pipeline show-summary --to-html --output-file pipeline_report.html
    """
⋮----
# Assumes manager.show_summary handles printing/returning formatted output
summary_output = manager.show_summary(
⋮----
# Otherwise, assume manager printed the summary
⋮----
"""
    Add a hook to a pipeline configuration.

    This command adds a hook function to a pipeline's configuration. Hooks are functions
    that are called at specific points during pipeline execution to perform additional
    tasks like logging, monitoring, or data validation.

    Args:
        name: Name of the pipeline to add the hook to
        function_name: Name of the hook function (must be defined in the pipeline module)
        type: Type of hook (determines when the hook is called during execution)
        to: Target node or tag (required for node-specific hooks)
        base_dir: Base directory containing the pipeline
        storage_options: Options for storage backends
        log_level: Set the logging level

    Examples:
        # Add a post-run hook
        $ pipeline add-hook my_pipeline --function log_results

        # Add a pre-run hook
        $ pipeline add-hook my_pipeline --function validate_inputs --type PRE_RUN

        # Add a node-specific hook (executed before a specific node runs)
        $ pipeline add-hook my_pipeline --function validate_data --type NODE_PRE_EXECUTE --to data_processor

        # Add a hook for all nodes with a specific tag
        $ pipeline add-hook my_pipeline --function log_metrics --type NODE_POST_EXECUTE --to @metrics
    """
⋮----
# Validate 'to' argument for node hooks
````

## File: src/flowerpower/cfg/pipeline/run.py
````python
class WithAdapterConfig(BaseConfig)
⋮----
tracker: bool = msgspec.field(default=False)
mlflow: bool = msgspec.field(default=False)
# openlineage: bool = msgspec.field(default=False)
ray: bool = msgspec.field(default=False)
opentelemetry: bool = msgspec.field(default=False)
progressbar: bool = msgspec.field(default=False)
future: bool = msgspec.field(default=False)
⋮----
class ExecutorConfig(BaseConfig)
⋮----
type: str | None = msgspec.field(default=settings.EXECUTOR)
max_workers: int | None = msgspec.field(default=settings.EXECUTOR_MAX_WORKERS)
num_cpus: int | None = msgspec.field(default=settings.EXECUTOR_NUM_CPUS)
⋮----
class RunConfig(BaseConfig)
⋮----
inputs: dict | None = msgspec.field(default_factory=dict)
final_vars: list[str] | None = msgspec.field(default_factory=list)
config: dict | None = msgspec.field(default_factory=dict)
cache: dict | bool | None = msgspec.field(default=False)
with_adapter: WithAdapterConfig = msgspec.field(default_factory=WithAdapterConfig)
executor: ExecutorConfig = msgspec.field(default_factory=ExecutorConfig)
log_level: str | None = msgspec.field(default=None)
max_retries: int = msgspec.field(default=3)
retry_delay: int | float = msgspec.field(default=1)
jitter_factor: float | None = msgspec.field(default=0.1)
retry_exceptions: tuple[str] = msgspec.field(default_factory=lambda: ("Exception",))
⋮----
def __post_init__(self)
````

## File: src/flowerpower/pipeline/io.py
````python
# -*- coding: utf-8 -*-
# mypy: disable-error-code="attr-defined"
# pylint: disable=no-member, E1136, W0212, W0201
"""
Manages the import and export of pipelines.
"""
⋮----
# Import necessary config types and utility functions
⋮----
console = Console()
⋮----
class PipelineIOManager
⋮----
"""Handles importing and exporting pipeline configurations and code."""
⋮----
"""
        Initializes the PipelineIOManager.

        Args:
            registry: The pipeline registry instance.
        """
⋮----
"""
        Synchronizes the source and destination filesystems.

        Args:
            src_base_dir (str): The source base directory.
            dest_base_dir (str): The destination base directory.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
            src_storage_options (dict | BaseStorageOptions | None, optional): Storage options for the source filesystem. Defaults to None.
            dest_storage_options (dict | BaseStorageOptions | None, optional): Storage options for the destination filesystem. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files. Defaults to False.
        Returns:
            tuple: A tuple containing the source and destination filesystems.
        """
⋮----
def _get_filesystem(base_dir, fs, storage_options)
⋮----
fs = get_filesystem(base_dir, storage_options=storage_options)
⋮----
fs = DirFileSystem(base_dir, fs=fs)
⋮----
src_fs = _get_filesystem(src_base_dir, src_fs, src_storage_options)
⋮----
dest_fs = _get_filesystem(dest_base_dir, dest_fs, dest_storage_options)
⋮----
# try:
#     src_mapper = src_fs.get_mapper(check=True, create=True)
# except NotImplementedError:
⋮----
#     src_mapper = src_fs.get_mapper(check=True, create=False)
⋮----
#     src_mapper = src_fs.get_mapper(check=False, create=False)
⋮----
#     dest_mapper = dest_fs.get_mapper(check=True, create=False)
⋮----
#     raise NotImplementedError(
#         f"The destination filesystem {dest_fs }does not support get_mapper."
#     )
⋮----
files = src_fs.glob("**/*.py")
⋮----
content = src_fs.read_bytes(file)
⋮----
"""
        Import a pipeline from a given path.

        Args:
            name (str): The name of the pipeline.
            src_base_dir (str): The path of the flowerpower project directory.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
            src_storage_options (BaseStorageOptions | None, optional): The storage options. Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing pipeline. Defaults to False.

        Returns:
            None

        Raises:
            ValueError: If the pipeline already exists and overwrite is False.

        Examples:
            ```python
            pm = PipelineManager()
            pm.import_pipeline("my_pipeline", "/path/to/pipeline")
            ```
        """
files = [
⋮----
# Use project_cfg.name directly
⋮----
"""
        Import multiple pipelines from given paths.

        Args:
            names (list[str]): A list of pipeline names to import.
            src_base_dir (str): The base path of the flowerpower project directory.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
            src_storage_options (BaseStorageOptions | None, optional): The storage options. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing pipelines. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()


            # Import multiple pipelines from a list
            pipelines_to_import = ["pipeline1", "pipeline2"]
            pm.import_many(pipelines_to_import, "/path/to/fp_project", overwrite=True)
            ```
        """
⋮----
files = ["conf/project.yml"]
⋮----
# Sync the filesystem
⋮----
"""Import all pipelines from a given path.

        Args:
            src_base_dir (str): The base path containing pipeline modules and configurations.
            src_fs (AbstractFileSystem | None, optional): The source filesystem. Defaults to None.
            src_storage_options (BaseStorageOptions | None, optional): Storage options for the source path. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing pipelines. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            # Import all pipelines from a local directory
            pm.import_all("/path/to/exported_pipelines", overwrite=True)
            # Import all pipelines from an S3 bucket
            # pm.import_all("s3://my-bucket/pipelines_backup", storage_options={"key": "...", "secret": "..."}, overwrite=False)
            ```
        """
⋮----
"""
        Export a pipeline to a given path.

        Args:
            name (str): The name of the pipeline.
            dest_base_dir (str): The destination path.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
            dest_storage_options (BaseStorageOptions | None, optional): Storage options for the destination path. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files at the destination. Defaults to False.

        Returns:
            None

        Raises:
            ValueError: If the pipeline does not exist or if the destination exists and overwrite is False.

        Examples:
            ```python
            pm = PipelineManager()
            pm.export("my_pipeline", "/path/to/export_dir")
            # Export to S3
            # pm.export("my_pipeline", "s3://my-bucket/exports", storage_options={"key": "...", "secret": "..."})
            ```
        """
⋮----
"""
        Export multiple pipelines to a directory.

        Args:
            pipelines (list[str]): A list of pipeline names to export.
            dest_base_dir (str): The destination directory path.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
            dest_storage_options (BaseStorageOptions | None, optional): Storage options for the destination path. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files at the destination. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            pipelines_to_export = ["pipeline1", "pipeline2.subpipeline"]
            pm.export_many(pipelines_to_export, "/path/to/export_dir", overwrite=True)
            ```
        """
⋮----
# Check if the pipeline exists in the registry
⋮----
# Add pipeline files to the list
⋮----
"""Export all pipelines to a given path.

        Args:
            dest_base_dir (str): The destination directory path.
            dest_fs (AbstractFileSystem | None, optional): The destination filesystem. Defaults to None.
            dest_storage_options (BaseStorageOptions | None, optional): Storage options for the destination path. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files at the destination. Defaults to False.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            # Export all pipelines to a local directory
            pm.export_all("/path/to/backup_dir", overwrite=True)
            # Export all pipelines to S3
            # pm.export_all("s3://my-bucket/pipelines_backup", storage_options={"key": "...", "secret": "..."}, overwrite=False)
            ```
        """
# sync the filesystem
````

## File: src/flowerpower/mqtt.py
````python
from flowerpower.plugins.mqtt import MqttManager  # noqa: E402
⋮----
__all__ = ["MqttConfig", "MqttManager", "MQTTManager"]
````

## File: src/flowerpower/pipeline/registry.py
````python
# -*- coding: utf-8 -*-
"""Pipeline Registry for discovery, listing, creation, and deletion."""
⋮----
# Import necessary config types and utility functions
⋮----
# Assuming view_img might be used indirectly or needed later
⋮----
# Keep this for type hinting if needed elsewhere, though Config is imported directly now
⋮----
class HookType(str, Enum)
⋮----
MQTT_BUILD_CONFIG = "mqtt-build-config"
⋮----
def default_function_name(self) -> str
⋮----
def __str__(self) -> str
⋮----
class PipelineRegistry
⋮----
"""Manages discovery, listing, creation, and deletion of pipelines."""
⋮----
"""
        Initializes the PipelineRegistry.

        Args:
            project_cfg: The project configuration object.
            fs: The filesystem instance.
            cfg_dir: The configuration directory path.
            pipelines_dir: The pipelines directory path.
        """
⋮----
# --- Methods moved from PipelineManager ---
def new(self, name: str, overwrite: bool = False)
⋮----
"""
        Adds a pipeline with the given name.

        Args:
            name (str): The name of the pipeline.
            overwrite (bool): Whether to overwrite an existing pipeline. Defaults to False.
            job_queue_type (str | None): The type of worker to use. Defaults to None.

        Raises:
            ValueError: If the configuration or pipeline path does not exist, or if the pipeline already exists.

        Examples:
            >>> pm = PipelineManager()
            >>> pm.new("my_pipeline")
        """
# Use attributes derived from self.project_cfg
⋮----
formatted_name = name.replace(".", "/").replace("-", "_")
pipeline_file = posixpath.join(self._pipelines_dir, f"{formatted_name}.py")
cfg_file = posixpath.join(self._cfg_dir, "pipelines", f"{formatted_name}.yml")
⋮----
def check_and_handle(path: str)
⋮----
# Ensure directories for the new files exist
⋮----
# Write pipeline code template
⋮----
# Create default pipeline config and save it directly
new_pipeline_cfg = PipelineConfig(name=name)
new_pipeline_cfg.save(fs=self._fs)  # Save only the pipeline part
⋮----
def delete(self, name: str, cfg: bool = True, module: bool = False)
⋮----
"""
        Delete a pipeline.

        Args:
            name (str): The name of the pipeline.
            cfg (bool, optional): Whether to delete the config file. Defaults to True.
            module (bool, optional): Whether to delete the module file. Defaults to False.

        Returns:
            None

        Raises:
            FileNotFoundError: If the specified files do not exist.

        Examples:
            >>> pm = PipelineManager()
            >>> pm.delete("my_pipeline")
        """
deleted_files = []
⋮----
pipeline_cfg_path = posixpath.join(
⋮----
)  # Changed to DEBUG
⋮----
pipeline_py_path = posixpath.join(self._pipelines_dir, f"{name}.py")
⋮----
# Sync filesystem if needed (using _fs)
⋮----
def _get_files(self) -> list[str]
⋮----
"""
        Get the list of pipeline files.

        Returns:
            list[str]: The list of pipeline files.
        """
⋮----
def _get_names(self) -> list[str]
⋮----
"""
        Get the list of pipeline names.

        Returns:
            list[str]: The list of pipeline names.
        """
files = self._get_files()
⋮----
"""
        Get a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            cfg (bool, optional): Whether to show the configuration. Defaults to True.
            code (bool, optional): Whether to show the module. Defaults to True.
            project (bool, optional): Whether to show the project configuration. Defaults to True.
        Returns:
            dict[str, dict | str]: A dictionary containing the pipeline summary.

        Examples:
            ```python
            pm = PipelineManager()
            summary=pm.get_summary()
            ```
        """
⋮----
pipeline_names = [name]
⋮----
pipeline_names = self._get_names()
⋮----
summary = {}
⋮----
# Use self.project_cfg directly
⋮----
# Load pipeline config directly
⋮----
pipeline_summary = {}
⋮----
pipeline_cfg = PipelineConfig.load(name=name, fs=self._fs)
⋮----
module_content = self._fs.cat(
⋮----
if pipeline_summary:  # Only add if cfg or code was requested and found
⋮----
"""
        Show a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            cfg (bool, optional): Whether to show the configuration. Defaults to True.
            code (bool, optional): Whether to show the module. Defaults to True.
            project (bool, optional): Whether to show the project configuration. Defaults to True.
            to_html (bool, optional): Whether to export the summary to HTML. Defaults to False.
            to_svg (bool, optional): Whether to export the summary to SVG. Defaults to False.

        Returns:
            None | str: The summary of the pipelines. If `to_html` is True, returns the HTML string.
                If `to_svg` is True, returns the SVG string.

        Examples:
            ```python
            pm = PipelineManager()
            pm.show_summary()
            ```
        """
⋮----
summary = self.get_summary(name=name, cfg=cfg, code=code, project=project)
project_summary = summary.get("project", {})
pipeline_summary = summary["pipelines"]
⋮----
def add_dict_to_tree(tree, dict_data, style="green")
⋮----
branch = tree.add(f"[cyan]{key}:", style="bold cyan")
⋮----
console = Console()
⋮----
# Create tree for project config
project_tree = Tree("📁 Project Configuration", style="bold magenta")
⋮----
# Print project configuration
⋮----
# Create tree for config
config_tree = Tree("📋 Pipeline Configuration", style="bold magenta")
⋮----
# Create syntax-highlighted code view
code_view = Syntax(
⋮----
# console.print(f"🔄 Pipeline: {pipeline}", style="bold blue")
⋮----
@property
    def summary(self) -> dict[str, dict | str]
⋮----
"""
        Get a summary of the pipelines.

        Returns:
            dict: A dictionary containing the pipeline summary.
        """
⋮----
"""
        Print all available pipelines in a formatted table.

        Args:
            show (bool, optional): Whether to print the table. Defaults to True.
            to_html (bool, optional): Whether to export the table to HTML. Defaults to False.
            to_svg (bool, optional): Whether to export the table to SVG. Defaults to False.

        Returns:
            list[str] | None: A list of pipeline names if `show` is False.

        Examples:
            ```python
            pm = PipelineManager()
            all_pipelines = pm._pipelines(show=False)
            ```
        """
⋮----
show = True
⋮----
pipeline_files = [
pipeline_names = [
⋮----
]  # Simplified name extraction
⋮----
return []  # Return empty list for consistency
⋮----
pipeline_info = []
⋮----
mod_time = self._fs.modified(path).strftime("%Y-%m-%d %H:%M:%S")
⋮----
mod_time = "N/A"
⋮----
size_bytes = self._fs.size(path)
size = f"{size_bytes / 1024:.1f} KB" if size_bytes else "0.0 KB"
⋮----
size = "N/A"
⋮----
size = "Error"
⋮----
table = Table(title="Available Pipelines")
⋮----
console = Console(record=True)
⋮----
def show_pipelines(self) -> None
⋮----
"""
        Print all available pipelines in a formatted table.

        Examples:
            ```python
            pm = PipelineManager()
            pm.show_pipelines()
            ```
        """
⋮----
def list_pipelines(self) -> list[str]
⋮----
"""
        Get a list of all available pipelines.

        Returns:
            list[str] | None: A list of pipeline names.

        Examples:
            ```python
            pm = PipelineManager()
            pipelines = pm.list_pipelines()
            ```
        """
⋮----
@property
    def pipelines(self) -> list[str]
⋮----
"""
        Get a list of all available pipelines.

        Returns:
            list[str] | None: A list of pipeline names.

        Examples:
            ```python
            pm = PipelineManager()
            pipelines = pm.pipelines
            ```
        """
⋮----
"""
        Add a hook to the pipeline module.

        Args:
            name (str): The name of the pipeline
            type (HookType): The type of the hook.
            to (str | None, optional): The name of the file to add the hook to. Defaults to the hook.py file in the pipelines hooks folder.
            function_name (str | None, optional): The name of the function. If not provided uses default name of hook type.

        Returns:
            None

        Examples:
            ```python
            pm = PipelineManager()
            pm.add_hook(HookType.PRE_EXECUTE)
            ```
        """
⋮----
to = f"hooks/{name}/hook.py"
⋮----
to = f"hooks/{name}/{to}"
⋮----
template = HOOK_TEMPLATE__MQTT_BUILD_CONFIG
⋮----
function_name = type.default_function_name()
````

## File: src/flowerpower/pipeline/runner.py
````python
# -*- coding: utf-8 -*-
"""Pipeline Runner."""
⋮----
h_opentelemetry = None
init_tracer = None
⋮----
h_mlflow = None
⋮----
distributed = None
⋮----
h_ray = None
⋮----
# from .executor import get_executor
⋮----
class PipelineRunner
⋮----
"""PipelineRunner is responsible for executing a specific pipeline run.
    It handles the loading of the pipeline module, configuration, and execution"""
⋮----
def __enter__(self)
⋮----
"""Enable use as a context manager."""
⋮----
def __exit__(self, exc_type, exc_val, exc_tb)
⋮----
"""No special cleanup required."""
⋮----
"""
        Get the executor based on the provided configuration.

        Args:
            executor (dict | None): Executor configuration.

        Returns:
            tuple[executors.BaseExecutor, Callable | None]: A tuple containing the executor and shutdown function.
        """
⋮----
executor_cfg = ExecutorConfig(type=executor_cfg)
⋮----
executor_cfg = ExecutorConfig.from_dict(executor_cfg)
⋮----
executor_cfg = self.pipeline_cfg.run.executor.merge(executor_cfg)
⋮----
executor_cfg = self.pipeline_cfg.run.executor
⋮----
cluster = distributed.LocalCluster()
client = distributed.Client(cluster)
⋮----
"""
        Set the adapters for the pipeline.

        Args:
            with_adapter_cfg (dict | WithAdapterConfig | None): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): The pipeline adapter configuration.
                Overrides the adapter settings in the pipeline config.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): The project adapter configuration.
                Overrides the adapter settings in the project config.
            adapter (dict[str, Any] | None): Any additional hamilton adapters can be passed here.
        """
⋮----
with_adapter_cfg = WithAdapterConfig.from_dict(with_adapter_cfg)
⋮----
with_adapter_cfg = self.pipeline_cfg.run.with_adapter.merge(
⋮----
with_adapter_cfg = self.pipeline_cfg.run.with_adapter
⋮----
pipeline_adapter_cfg = PipelineAdapterConfig.from_dict(
⋮----
pipeline_adapter_cfg = self.pipeline_cfg.adapter.merge(pipeline_adapter_cfg)
⋮----
pipeline_adapter_cfg = self.pipeline_cfg.adapter
⋮----
project_adapter_cfg = ProjectAdapterConfig.from_dict(
⋮----
project_adapter_cfg = self.project_cfg.adapter.merge(project_adapter_cfg)
⋮----
project_adapter_cfg = self.project_cfg.adapter
⋮----
adapters = []
⋮----
tracker_kwargs = project_adapter_cfg.tracker.to_dict()
⋮----
tracker = HamiltonTracker(**tracker_kwargs)
⋮----
mlflow_kwargs = project_adapter_cfg.mlflow.to_dict()
⋮----
mlflow_adapter = h_mlflow.MLFlowTracker(**mlflow_kwargs)
⋮----
otel_kwargs = project_adapter_cfg.opentelemetry.to_dict()
⋮----
trace = init_tracer(**otel_kwargs, name=self.project_cfg.name)
tracer = trace.get_tracer(self.name)
otel_adapter = h_opentelemetry.OpenTelemetryTracer(
⋮----
ray_kwargs = project_adapter_cfg.ray.to_dict()
⋮----
ray_adapter = h_ray.RayGraphAdapter(**ray_kwargs)
⋮----
all_adapters = [
⋮----
"""
        Get the driver and shutdown function for a given pipeline.

        Args:
            config (dict | None): The configuration for the pipeline.
            cache (bool): Use cache or not.
                To fine tune the cache settings, pass a dictionary with the cache settings
                or adjust the pipeline config.
                If set to True, the default cache settings will be used.
            executor_cfg (str | dict | ExecutorConfig | None): The executor to use.
                Overrides the executor settings in the pipeline config.
            with_adapter_cfg (dict | WithAdapterConfig | None): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): The pipeline adapter configuration.
                Overrides the adapter settings in the pipeline config.
            project_adapter_cfg (dict | ProjectAdapterConfig | None): The project adapter configuration.
                Overrides the adapter settings in the project config.
            adapter (dict[str, Any] | None): Any additional Hamilton adapters can be passed here.
            reload (bool): Whether to reload the module.


        Returns:
            tuple[driver.Driver, Callable | None]: A tuple containing the driver and shutdown function.
        """
⋮----
module = load_module(name=self.name, reload=reload)
⋮----
adapters = self._get_adapters(
⋮----
config = config or self.pipeline_cfg.run.config
⋮----
dr = (
⋮----
cache = cache or self.pipeline_cfg.run.cache
dr = dr.with_cache(**cache)
⋮----
dr = dr.with_cache()
⋮----
dr = dr.with_remote_executor(executor)
⋮----
dr = dr.with_adapters(*adapters)
⋮----
dr = dr.build()
⋮----
"""
        Run the pipeline with the given parameters.
        Args:
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            config (dict | None, optional): The config for the hamilton driver. Defaults to None.
            cache (dict | None, optional): The cache configuration. Defaults to None.
            executor_cfg (str | dict | ExecutorConfig | None, optional): The executor to use.
                Overrides the executor settings in the pipeline config. Defaults to None.
            with_adapter_cfg (dict | WithAdapterConfig | None, optional): The adapter configuration.
                Overrides the with_adapter settings in the pipeline config. Defaults to None.
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None, optional): The pipeline adapter configuration.
                Overrides the adapter settings in the pipeline config. Defaults to None.
            project_adapter_cfg (dict | ProjectAdapterConfig | None, optional): The project adapter configuration.
                Overrides the adapter settings in the project config. Defaults to None.
            adapter (dict[str, Any] | None, optional): Any additional Hamilton adapters can be passed here. Defaults to None.
            reload (bool, optional): Whether to reload the module. Defaults to False.
            log_level (str | None, optional): The log level to use. Defaults to None.

        Returns:
            dict[str, Any]: The result of executing the pipeline.
        """
⋮----
final_vars = final_vars or self.pipeline_cfg.run.final_vars
inputs = {
⋮----
}  # <-- inputs override and/or extend config inputs
⋮----
max_retries = max_retries or self.pipeline_cfg.run.max_retries
retry_delay = retry_delay or self.pipeline_cfg.run.retry_delay
jitter_factor = jitter_factor or self.pipeline_cfg.run.jitter_factor
retry_exceptions = retry_exceptions or self.pipeline_cfg.run.retry_exceptions
⋮----
attempts = 1
last_exception = None
⋮----
res = dr.execute(final_vars=final_vars, inputs=inputs)
⋮----
last_exception = e
⋮----
# Calculate base delay with exponential backoff
base_delay = retry_delay * (2 ** (attempts - 1))
⋮----
# Add jitter: random value between -jitter_factor and +jitter_factor of the base delay
jitter = base_delay * jitter_factor * (2 * random.random() - 1)
actual_delay = max(
⋮----
)  # Ensure non-negative delay
⋮----
# Last attempt failed
⋮----
),  # Adjust to specific exceptions
⋮----
"""Run the pipeline with the given parameters.

    Args:

        project_cfg (ProjectConfig): The project configuration.
        pipeline_cfg (PipelineConfig): The pipeline configuration.
        inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
        final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
        config (dict | None, optional): The config for the hamilton driver. Defaults to None.
        cache (dict | None, optional): The cache configuration. Defaults to None.
        executor_cfg (str | dict | ExecutorConfig | None, optional): The executor to use.
            Overrides the executor settings in the pipeline config. Defaults to None.
        with_adapter_cfg (dict | WithAdapterConfig | None, optional): The adapter configuration.
            Overrides the with_adapter settings in the pipeline config. Defaults to None.
        pipeline_adapter_cfg (dict | PipelineAdapterConfig | None, optional): The pipeline adapter configuration.
            Overrides the adapter settings in the pipeline config. Defaults to None.
        project_adapter_cfg (dict | ProjectAdapterConfig | None, optional): The project adapter configuration.
            Overrides the adapter settings in the project config. Defaults to None.
        adapter (dict[str, Any] | None, optional): Any additional Hamilton adapters can be passed here. Defaults to None.
        reload (bool, optional): Whether to reload the module. Defaults to False.
        log_level (str | None, optional): The log level to use. Defaults to None.
        max_retries (int, optional): The maximum number of retry attempts. Defaults to 0.
        retry_delay (float, optional): The base delay between retries in seconds. Defaults to 1.0.
        jitter_factor (float, optional): The factor to apply for jitter. Defaults to 0.1.
        retry_exceptions (tuple, optional): A tuple of exception classes to catch for retries. Defaults to (Exception,).

    Returns:

        dict[str, Any]: The result of executing the pipeline.

    Raises:
        Exception: If the pipeline execution fails after the maximum number of retries.
    """
````

## File: src/flowerpower/pipeline/manager.py
````python
Digraph = Any  # Type alias for when graphviz isn't installed
⋮----
GraphType = TypeVar("GraphType")  # Type variable for graphviz.Digraph
⋮----
class PipelineManager
⋮----
"""Central manager for FlowerPower pipeline operations.

    This class provides a unified interface for managing pipelines, including:
    - Configuration management and loading
    - Pipeline creation, deletion, and discovery
    - Pipeline execution via PipelineRunner
    - Job scheduling via PipelineScheduler
    - Visualization via PipelineVisualizer
    - Import/export operations via PipelineIOManager

    Attributes:
        registry (PipelineRegistry): Handles pipeline registration and discovery
        scheduler (PipelineScheduler): Manages job scheduling and execution
        visualizer (PipelineVisualizer): Handles pipeline visualization
        io (PipelineIOManager): Manages pipeline import/export operations
        project_cfg (ProjectConfig): Current project configuration
        pipeline_cfg (PipelineConfig): Current pipeline configuration
        pipelines (list[str]): List of available pipeline names
        current_pipeline_name (str): Name of the currently loaded pipeline
        summary (dict[str, dict | str]): Summary of all pipelines

    Example:
        >>> from flowerpower.pipeline import PipelineManager
        >>>
        >>> # Create manager with default settings
        >>> manager = PipelineManager()
        >>>
        >>> # Create manager with custom settings
        >>> manager = PipelineManager(
        ...     base_dir="/path/to/project",
        ...     job_queue_type="rq",
        ...     log_level="DEBUG"
        ... )
    """
⋮----
"""Initialize the PipelineManager.

        Args:
            base_dir: Root directory for the FlowerPower project. Defaults to current
                working directory if not specified.
            storage_options: Configuration options for filesystem access. Can be:
                - dict: Raw key-value options
                - Munch: Dot-accessible options object
                - BaseStorageOptions: Structured options class
                Used for S3, GCS, etc. Example: {"key": "abc", "secret": "xyz"}
            fs: Pre-configured fsspec filesystem instance. If provided, used instead
                of creating new filesystem from base_dir and storage_options.
            cfg_dir: Override default configuration directory name ('conf').
                Example: "config" or "settings".
            pipelines_dir: Override default pipelines directory name ('pipelines').
                Example: "flows" or "dags".
            job_queue_type: Override worker type from project config/settings.
                Valid values: "rq", "apscheduler", or "huey".
            log_level: Set logging level for the manager.
                Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

        Raises:
            ValueError: If provided configuration paths don't exist or can't be created
            RuntimeError: If filesystem operations fail during initialization
            ImportError: If required dependencies for specified worker type not installed

        Example:
            >>> # Basic initialization
            >>> manager = PipelineManager()
            >>>
            >>> # Custom configuration with S3 storage
            >>> manager = PipelineManager(
            ...     base_dir="s3://my-bucket/project",
            ...     storage_options={
            ...         "key": "ACCESS_KEY",
            ...         "secret": "SECRET_KEY"
            ...     },
            ...     job_queue_type="rq",
            ...     log_level="DEBUG"
            ... )
        """
⋮----
fs = get_filesystem(self._base_dir, storage_options=storage_options)
⋮----
# Store overrides for ProjectConfig loading
⋮----
self._load_project_cfg(reload=True)  # Load project config
⋮----
# Ensure essential directories exist (using paths from loaded project_cfg)
⋮----
# Consider raising an error here depending on desired behavior
⋮----
# Ensure pipeline modules can be imported
⋮----
# Instantiate components using the loaded project config
⋮----
def __enter__(self) -> "PipelineManager"
⋮----
"""Enter the context manager.

        Enables use of the manager in a with statement for automatic resource cleanup.

        Returns:
            PipelineManager: Self for use in context manager.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> with PipelineManager() as manager:
            ...     result = manager.run("my_pipeline")
        """
⋮----
"""Exit the context manager.

        Handles cleanup of resources when exiting a with statement.

        Args:
            exc_type: Type of exception that occurred, if any
            exc_val: Exception instance that occurred, if any
            exc_tb: Traceback of exception that occurred, if any

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> with PipelineManager() as manager:
            ...     try:
            ...         result = manager.run("my_pipeline")
            ...     except Exception as e:
            ...         print(f"Error: {e}")
            ...     # Resources automatically cleaned up here
        """
# Add cleanup code if needed
⋮----
def _get_run_func_for_job(self, name: str, reload: bool = False) -> Callable
⋮----
"""Create a PipelineRunner instance and return its run method.

        This internal helper method ensures that each job gets a fresh runner
        with the correct configuration state.

        Args:
            name: Name of the pipeline to create runner for
            reload: Whether to reload pipeline configuration

        Returns:
            Callable: Bound run method from a fresh PipelineRunner instance

        Example:
            >>> # Internal usage
            >>> manager = PipelineManager()
            >>> run_func = manager._get_run_func_for_job("data_pipeline")
            >>> result = run_func(inputs={"date": "2025-04-28"})
        """
⋮----
pipeline_cfg = self._load_pipeline_cfg(name=name, reload=reload)
⋮----
def _add_modules_path(self) -> None
⋮----
"""Add pipeline module paths to Python path.

        This internal method ensures that pipeline modules can be imported by:
        1. Syncing filesystem cache if needed
        2. Adding project root to Python path
        3. Adding pipelines directory to Python path

        Raises:
            RuntimeError: If filesystem sync fails or paths are invalid

        Example:
            >>> # Internal usage
            >>> manager = PipelineManager()
            >>> manager._add_modules_path()
            >>> import my_pipeline  # Now importable
        """
⋮----
modules_path = posixpath.join(self._fs.path, self._pipelines_dir)
⋮----
def _load_project_cfg(self, reload: bool = False) -> ProjectConfig
⋮----
"""Load or reload the project configuration.

        This internal method handles loading project-wide settings from the config
        directory, applying overrides, and maintaining configuration state.

        Args:
            reload: Force reload configuration even if already loaded.
                Defaults to False for caching behavior.

        Returns:
            ProjectConfig: The loaded project configuration object with any
                specified overrides applied.

        Raises:
            FileNotFoundError: If project configuration file doesn't exist
            ValueError: If configuration format is invalid
            RuntimeError: If filesystem operations fail during loading

        Example:
            >>> # Internal usage
            >>> manager = PipelineManager()
            >>> project_cfg = manager._load_project_cfg(reload=True)
            >>> print(project_cfg.worker.type)
            'rq'
        """
⋮----
# Pass overrides to ProjectConfig.load
⋮----
fs=self._fs,  # Pass pre-configured fs if provided
⋮----
# Update internal fs reference in case ProjectConfig loaded/created one
⋮----
def _load_pipeline_cfg(self, name: str, reload: bool = False) -> PipelineConfig
⋮----
"""Load or reload configuration for a specific pipeline.

        This internal method handles loading pipeline-specific settings from the config
        directory and maintaining the configuration cache state.

        Args:
            name: Name of the pipeline whose configuration to load
            reload: Force reload configuration even if already loaded.
                When False, returns cached config if available.

        Returns:
            PipelineConfig: The loaded pipeline configuration object

        Raises:
            FileNotFoundError: If pipeline configuration file doesn't exist
            ValueError: If configuration format is invalid
            RuntimeError: If filesystem operations fail during loading

        Example:
            >>> # Internal usage
            >>> manager = PipelineManager()
            >>> cfg = manager._load_pipeline_cfg("data_pipeline", reload=True)
            >>> print(cfg.run.executor.type)
            'async'
        """
⋮----
@property
    def current_pipeline_name(self) -> str
⋮----
"""Get the name of the currently loaded pipeline.

        Returns:
            str: Name of the currently loaded pipeline, or empty string if none loaded.

        Example:
            >>> manager = PipelineManager()
            >>> manager._load_pipeline_cfg("example_pipeline")
            >>> print(manager.current_pipeline_name)
            'example_pipeline'
        """
⋮----
@property
    def project_cfg(self) -> ProjectConfig
⋮----
"""Get the project configuration.

        Loads configuration if not already loaded.

        Returns:
            ProjectConfig: Project-wide configuration object.

        Raises:
            RuntimeError: If configuration loading fails.

        Example:
            >>> manager = PipelineManager()
            >>> cfg = manager.project_cfg
            >>> print(cfg.worker.type)
            'rq'
        """
⋮----
@property
    def pipeline_cfg(self) -> PipelineConfig
⋮----
"""Get the configuration for the currently loaded pipeline.

        Returns:
            PipelineConfig: Pipeline-specific configuration object.

        Warns:
            UserWarning: If no pipeline is currently loaded.

        Example:
            >>> manager = PipelineManager()
            >>> manager._load_pipeline_cfg("example_pipeline")
            >>> cfg = manager.pipeline_cfg
            >>> print(cfg.run.executor)
            'local'
        """
⋮----
# --- Core Execution Method ---
⋮----
"""Execute a pipeline synchronously and return its results.

        This is the main method for running pipelines directly. It handles configuration
        loading, adapter setup, and execution via PipelineRunner.

        Args:
            name (str): Name of the pipeline to run. Must be a valid identifier.
            inputs (dict | None): Override pipeline input values. Example: {"data_date": "2025-04-28"}
            final_vars (list[str] | None): Specify which output variables to return.
                Example: ["model", "metrics"]
            config (dict | None): Configuration for Hamilton pipeline executor.
                Example: {"model": "LogisticRegression"}
            cache (dict | None): Cache configuration for results. Example: {"recompute": ["node1", "final_node"]}
            executor_cfg (str | dict | ExecutorConfig | None): Execution configuration, can be:
                - str: Executor name, e.g. "threadpool", "local"
                - dict: Raw config, e.g. {"type": "threadpool", "max_workers": 4}
                - ExecutorConfig: Structured config object
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter settings for pipeline execution.
                Example: {"opentelemetry": True, "tracker": False}
             pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline-specific adapter settings.
                Example: {"tracker": {"project_id": "123", "tags": {"env": "prod"}}}
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project-level adapter settings.
                Example: {"opentelemetry": {"host": "http://localhost:4317"}}
            adapter (dict[str, Any] | None): Custom adapter instance for pipeline
                Example: {"ray_graph_adapter": RayGraphAdapter()}
            reload (bool): Force reload of pipeline configuration.
            log_level (str | None): Logging level for the execution. Default None uses project config.
                Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            max_retries (int): Maximum number of retries for execution.
            retry_delay (float): Delay between retries in seconds.
            jitter_factor (float): Random jitter factor to add to retry delay
            retry_exceptions (tuple): Exceptions that trigger a retry.

        Returns:
            dict[str, Any]: Pipeline execution results, mapping output variable names
                to their computed values.

        Raises:
            ValueError: If pipeline name doesn't exist or configuration is invalid
            ImportError: If pipeline module cannot be imported
            RuntimeError: If execution fails due to pipeline or adapter errors

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Basic pipeline run
            >>> results = manager.run("data_pipeline")
            >>>
            >>> # Complex run with overrides
            >>> results = manager.run(
            ...     name="ml_pipeline",
            ...     inputs={
            ...         "training_date": "2025-04-28",
            ...         "model_params": {"n_estimators": 100}
            ...     },
            ...     final_vars=["model", "metrics"],
            ...     executor_cfg={"type": "threadpool", "max_workers": 4},
            ...     with_adapter_cfg={"tracker": True},
            ...     reload=True
            ... )
        """
# pipeline_cfg = self._load_pipeline_cfg(name=name, reload=reload)
run_func = self._get_run_func_for_job(name=name, reload=reload)
res = run_func(
⋮----
# reload=reload,  # Runner handles module reload if needed
⋮----
# --- Delegated Methods ---
⋮----
# Registry Delegations
def new(self, name: str, overwrite: bool = False) -> None
⋮----
"""Create a new pipeline with the given name.

        Creates necessary configuration files and pipeline module template.

        Args:
            name: Name for the new pipeline. Must be a valid Python identifier.
            overwrite: Whether to overwrite existing pipeline with same name.
                Default False for safety.

        Raises:
            ValueError: If name is invalid or pipeline exists and overwrite=False
            RuntimeError: If file creation fails
            PermissionError: If lacking write permissions

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> # Create new pipeline
            >>> manager = PipelineManager()
            >>> manager.new("data_transformation")
            >>>
            >>> # Overwrite existing pipeline
            >>> manager.new("data_transformation", overwrite=True)
        """
⋮----
def delete(self, name: str, cfg: bool = True, module: bool = False) -> None
⋮----
"""
        Delete a pipeline and its associated files.

        Args:
            name: Name of the pipeline to delete
            cfg: Whether to delete configuration files. Default True.
            module: Whether to delete Python module file. Default False
                for safety since it may contain custom code.

        Raises:
            FileNotFoundError: If specified pipeline files don't exist
            PermissionError: If lacking delete permissions
            RuntimeError: If deletion fails partially, leaving inconsistent state

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> # Delete pipeline config only
            >>> manager = PipelineManager()
            >>> manager.delete("old_pipeline")
            >>>
            >>> # Delete both config and module
            >>> manager.delete("test_pipeline", module=True)
        """
⋮----
"""Get a detailed summary of pipeline(s) configuration and code.

        Args:
            name: Specific pipeline to summarize. If None, summarizes all.
            cfg: Include pipeline configuration details. Default True.
            code: Include pipeline module code. Default True.
            project: Include project configuration. Default True.

        Returns:
            dict[str, dict | str]: Nested dictionary containing requested
                summaries. Structure varies based on input parameters:
                - With name: {"config": dict, "code": str, "project": dict}
                - Without name: {pipeline_name: {"config": dict, ...}, ...}

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Get summary of specific pipeline
            >>> summary = manager.get_summary("data_pipeline")
            >>> print(summary["config"]["schedule"]["enabled"])
            True
            >>>
            >>> # Get summary of all pipelines' code
            >>> all_code = manager.get_summary(
            ...     cfg=False,
            ...     code=True,
            ...     project=False
            ... )
        """
⋮----
"""
        Show a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            cfg (bool, optional): Whether to show the configuration. Defaults to True.
            code (bool, optional): Whether to show the module. Defaults to True.
            project (bool, optional): Whether to show the project configuration. Defaults to True.
            to_html (bool, optional): Whether to export the summary to HTML. Defaults to False.
            to_svg (bool, optional): Whether to export the summary to SVG. Defaults to False.

        Returns:
            None | str: The summary of the pipelines. If `to_html` is True, returns the HTML string.
                If `to_svg` is True, returns the SVG string.

        Examples:
            >>> pm = PipelineManager()
            >>> pm.show_summary()
        """
⋮----
def show_pipelines(self) -> None
⋮----
"""Display all available pipelines in a formatted table.

        The table includes pipeline names, types, and enablement status.
        Uses rich formatting for terminal display.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> manager.show_pipelines()

        """
⋮----
def list_pipelines(self) -> list[str]
⋮----
"""Get list of all available pipeline names.

        Returns:
            list[str]: Names of all registered pipelines, sorted alphabetically.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> pipelines = manager.list_pipelines()
            >>> print(pipelines)
            ['data_ingestion', 'model_training', 'reporting']
        """
⋮----
@property
    def pipelines(self) -> list[str]
⋮----
"""Get list of all available pipeline names.

        Similar to list_pipelines() but as a property.

        Returns:
            list[str]: Names of all registered pipelines, sorted alphabetically.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> print(manager.pipelines)
            ['data_ingestion', 'model_training', 'reporting']
        """
⋮----
@property
    def summary(self) -> dict[str, dict | str]
⋮----
"""Get complete summary of all pipelines.

        Returns:
            dict[str, dict | str]: Full summary including configuration,
            code, and project settings for all pipelines.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> summary = manager.summary
            >>> for name, details in summary.items():
            ...     print(f"{name}: {details['config']['type']}")
            data_pipeline: batch
            ml_pipeline: streaming
        """
⋮----
"""Add a hook to the pipeline module.

        Args:
            name (str): The name of the pipeline
            type (HookType): The type of the hook.
            to (str | None, optional): The name of the file to add the hook to. Defaults to the hook.py file in the pipelines hooks folder.
            function_name (str | None, optional): The name of the function. If not provided uses default name of hook type.

        Returns:
            None

        Raises:
            ValueError: If the hook type is not valid

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> manager.add_hook(
            ...     name="data_pipeline",
            ...     type=HookType.PRE_EXECUTE,
            ...     to="pre_execute_hook",
            ...     function_name="my_pre_execute_function"
            ... )
        """
⋮----
# IO Delegations
⋮----
"""Import a pipeline from another FlowerPower project.

        Copies both pipeline configuration and code files from the source location
        to the current project.

        Args:
            name (str): Name for the new pipeline in the current project
            src_base_dir (str): Source FlowerPower project directory or URI
                Examples:
                    - Local: "/path/to/other/project"
                    - S3: "s3://bucket/project"
                    - GitHub: "github://org/repo/project"
            src_fs (AbstractFileSystem | None): Pre-configured source filesystem
                Example: S3FileSystem(key='ACCESS_KEY', secret='SECRET_KEY')
            src_storage_options (dict | BaseStorageOptions | None): Options for source filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite: Whether to replace existing pipeline if name exists

        Raises:
            ValueError: If pipeline name exists and overwrite=False
            FileNotFoundError: If source pipeline not found
            RuntimeError: If import fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>> from s3fs import S3FileSystem
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Import from local filesystem
            >>> manager.import_pipeline(
            ...     "new_pipeline",
            ...     "/path/to/other/project"
            ... )
            >>>
            >>> # Import from S3 with custom filesystem
            >>> s3 = S3FileSystem(anon=False)
            >>> manager.import_pipeline(
            ...     "s3_pipeline",
            ...     "s3://bucket/project",
            ...     src_fs=s3
            ... )
        """
⋮----
src_base_dir: str,  # Base dir for source if pipelines is a list
⋮----
"""Import multiple pipelines from another project or location.


        Args:
            pipelines(list[str]): List of pipeline names to import
            src_base_dir (str, optional): Source project directory or URI
                Examples:
                    - Local: "/path/to/other/project"
                    - S3: "s3://bucket/project"
                    - GitHub: "github://org/repo/project"
            src_fs (AbstractFileSystem | None, optional): Pre-configured source filesystem
                Example: S3FileSystem(key='ACCESS_KEY', secret="SECRET_KEY")
            storage_options (dict | BaseStorageOptions | None, optional): Options for source filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite (bool, optional): Whether to replace existing pipelines

        Raises:
            ValueError: If any pipeline exists and overwrite=False
            FileNotFoundError: If source pipelines not found
            RuntimeError: If import operation fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Import keeping original names
            >>> manager.import_many(
            ...     names=["pipeline1", "pipeline2"],
            ...     src_base_dir="s3://bucket/source",
            ...     src_storage_options={
            ...         "key": "ACCESS_KEY",
            ...         "secret": "SECRET_KEY"
            ...     }
            ... )
        """
⋮----
"""Import all pipelines from another FlowerPower project.

        Args:
            src_base_dir (str): Source project directory or URI
                Examples:
                    - Local: "/path/to/other/project"
                    - S3: "s3://bucket/project"
                    - GitHub: "github://org/repo/project"
            src_fs (AbstractFileSystem | None): Pre-configured source filesystem
                Example: S3FileSystem(key='KEY',secret='SECRET')
            src_storage_options (dict | BaseStorageOptions | None): Options for source filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite (bool): Whether to replace existing pipelines

        Raises:
            FileNotFoundError: If source location not found
            RuntimeError: If import fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Import all from backup
            >>> manager.import_all("/path/to/backup")
            >>>
            >>> # Import all from S3 with credentials
            >>> manager.import_all(
            ...     "s3://bucket/backup",
            ...     src_storage_options={
            ...         "key": "ACCESS_KEY",
            ...         "secret": "SECRET_KEY"
            ...     }
            ... )
        """
⋮----
"""Export a pipeline to another location or project.

        Copies pipeline configuration and code files to the destination location
        while preserving directory structure.

        Args:
            name (str): Name of the pipeline to export
            dest_base_dir (str): Destination directory or URI
                Examples:
                    - Local: "/path/to/exports"
                    - S3: "s3://bucket/exports"
                    - Azure: "abfs://container/exports"
            dest_fs (AbstractFileSystem | None): Pre-configured destination filesystem
                Example: S3FileSystem(key='ACCESS_KEY', secret='SECRET_KEY')
            dest_storage_options (dict | BaseStorageOptions | None): Options for destination filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite (bool): Whether to replace existing files at destination

        Raises:
            ValueError: If pipeline doesn't exist
            FileNotFoundError: If destination not accessible
            RuntimeError: If export fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>> from gcsfs import GCSFileSystem
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Export to local backup
            >>> manager.export_pipeline(
            ...     "my_pipeline",
            ...     "/path/to/backup"
            ... )
            >>>
            >>> # Export to Google Cloud Storage
            >>> gcs = GCSFileSystem(project='my-project')
            >>> manager.export_pipeline(
            ...     "prod_pipeline",
            ...     "gs://my-bucket/backups",
            ...     dest_fs=gcs
            ... )
        """
⋮----
"""Export multiple pipelines to another location.

        Efficiently exports multiple pipelines in a single operation,
        preserving directory structure and metadata.

        Args:
            names (list[str]): List of pipeline names to export
            dest_base_dir (str): Destination directory or URI
                Examples:
                    - Local: "/path/to/exports"
                    - S3: "s3://bucket/exports"
                    - Azure: "abfs://container/exports"
            dest_fs (AbstractFileSystem | None): Pre-configured destination filesystem
                Example: S3FileSystem(key='ACCESS_KEY', secret='SECRET_KEY')
            dest_storage_options (dict | BaseStorageOptions | None): Options for destination filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite (bool): Whether to replace existing files at destination

        Raises:
            ValueError: If any pipeline doesn't exist
            FileNotFoundError: If destination not accessible
            RuntimeError: If export operation fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>> from azure.storage.filedatalake import DataLakeServiceClient
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Export multiple pipelines to Azure Data Lake
            >>> manager.export_many(
            ...     pipelines=["ingest", "process", "report"],
            ...     base_dir="abfs://data/backups",
            ...     dest_storage_options={
            ...         "account_name": "myaccount",
            ...         "sas_token": "...",
            ...     }
            ... )
        """
⋮----
"""Export all pipelines to another location.

        Args:
            dest_base_dir (str): Destination directory or URI
                Examples:
                    - Local: "/path/to/exports"
                    - S3: "s3://bucket/exports"
                    - Azure: "abfs://container/exports"
            dest_fs (AbstractFileSystem | None): Pre-configured destination filesystem
                Example: S3FileSystem(key='ACCESS_KEY', secret='SECRET_KEY')
            dest_storage_options (dict | BaseStorageOptions | None): Options for destination filesystem access
                Example: {"key": "ACCESS_KEY", "secret": "SECRET_KEY"}
            overwrite (bool): Whether to replace existing files at destination

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Export all to backup directory
            >>> manager.export_all("/path/to/backup")
            >>>
            >>> # Export all to cloud storage
            >>> manager.export_all(
            ...     "gs://bucket/pipelines",
            ...     dest_storage_options={
            ...         "token": "SERVICE_ACCOUNT_TOKEN",
            ...         "project": "my-project"
            ...     }
            ... )
        """
⋮----
# Visualizer Delegations
def save_dag(self, name: str, format: str = "png", reload: bool = False) -> None
⋮----
"""Save pipeline DAG visualization to a file.

        Creates a visual representation of the pipeline's directed acyclic graph (DAG)
        showing function dependencies and data flow.

        Args:
            name: Name of the pipeline to visualize
            format: Output file format. Supported formats:
                - "png": Standard bitmap image
                - "svg": Scalable vector graphic
                - "pdf": Portable document format
                - "dot": Graphviz DOT format
            reload: Whether to reload pipeline before visualization

        Raises:
            ValueError: If pipeline name doesn't exist
            ImportError: If required visualization dependencies missing
            RuntimeError: If graph generation fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Save as PNG
            >>> manager.save_dag("data_pipeline")
            >>>
            >>> # Save as SVG with reload
            >>> manager.save_dag(
            ...     name="ml_pipeline",
            ...     format="svg",
            ...     reload=True
            ... )
        """
⋮----
"""Display pipeline DAG visualization interactively.

        Similar to save_dag() but displays the graph immediately in notebook
        environments or returns the raw graph object for custom rendering.

        Args:
            name: Name of the pipeline to visualize
            format: Output format (see save_dag() for options)
            reload: Whether to reload pipeline before visualization
            raw: If True, return the raw graph object instead of displaying

        Returns:
            Union[GraphType, None]: Raw graph object if raw=True, else None after
                displaying the visualization

        Raises:
            ValueError: If pipeline name doesn't exist
            ImportError: If visualization dependencies missing
            RuntimeError: If graph generation fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Display in notebook
            >>> manager.show_dag("data_pipeline")
            >>>
            >>> # Get raw graph for custom rendering
            >>> graph = manager.show_dag(
            ...     name="ml_pipeline",
            ...     format="svg",
            ...     raw=True
            ... )
            >>> # Custom rendering
            >>> graph.render("custom_vis", view=True)
        """
⋮----
"""Execute a pipeline job immediately through the task queue.

        Unlike the run() method which executes synchronously, this method runs
        the pipeline through the configured worker system (RQ, APScheduler, etc.).

        Args:
            name (str): Name of the pipeline to run. Must be a valid identifier.
            inputs (dict | None): Override pipeline input values. Example: {"data_date": "2025-04-28"}
            final_vars (list[str] | None): Specify which output variables to return.
                Example: ["model", "metrics"]
            config (dict | None): Configuration for Hamilton pipeline executor.
                Example: {"model": "LogisticRegression"}
            cache (dict | None): Cache configuration for results. Example: {"recompute": ["node1", "final_node"]}
            executor_cfg (str | dict | ExecutorConfig | None): Execution configuration, can be:
                - str: Executor name, e.g. "threadpool", "local"
                - dict: Raw config, e.g. {"type": "threadpool", "max_workers": 4}
                - ExecutorConfig: Structured config object
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter settings for pipeline execution.
                Example: {"opentelemetry": True, "tracker": False}
             pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline-specific adapter settings.
                Example: {"tracker": {"project_id": "123", "tags": {"env": "prod"}}}
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project-level adapter settings.
                Example: {"opentelemetry": {"host": "http://localhost:4317"}}
            adapter (dict[str, Any] | None): Custom adapter instance for pipeline
                Example: {"ray_graph_adapter": RayGraphAdapter()}
            reload (bool): Force reload of pipeline configuration.
            log_level (str | None): Logging level for the execution. Default None uses project config.
                Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            max_retries (int): Maximum number of retries for execution.
            retry_delay (float): Delay between retries in seconds.
            jitter_factor (float): Random jitter factor to add to retry delay
            retry_exceptions (tuple): Exceptions that trigger a retry.

            **kwargs: JobQueue-specific arguments
                For RQ:
                    - queue_name: Queue to use (str)
                    - retry: Number of retries (int)
                For APScheduler:
                    - job_executor: Executor type (str)

        Returns:
            dict[str, Any]: Job execution results

        Raises:
            ValueError: If pipeline or configuration is invalid
            RuntimeError: If job execution fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Simple job execution
            >>> result = manager.run_job("data_pipeline")
            >>>
            >>> # Complex job with retry logic
            >>> result = manager.run_job(
            ...     name="ml_training",
            ...     inputs={"training_date": "2025-04-28"},
            ...     executor_cfg={"type": "async"},
            ...     with_adapter_cfg={"enable_tracking": True},
            ...     retry=3,
            ...     queue_name="ml_jobs"
            ... )
        """
⋮----
# run_func=run_func,
⋮----
# reload=reload,
⋮----
reload: bool = False,  # Reload config/module before creating run_func
⋮----
**kwargs,  # JobQueue specific args
⋮----
"""Adds a jobt to the task queue.

        Args:
            name (str): Name of the pipeline to run. Must be a valid identifier.
            inputs (dict | None): Override pipeline input values. Example: {"data_date": "2025-04-28"}
            final_vars (list[str] | None): Specify which output variables to return.
                Example: ["model", "metrics"]
            config (dict | None): Configuration for Hamilton pipeline executor.
                Example: {"model": "LogisticRegression"}
            cache (dict | None): Cache configuration for results. Example: {"recompute": ["node1", "final_node"]}
            executor_cfg (str | dict | ExecutorConfig | None): Execution configuration, can be:
                - str: Executor name, e.g. "threadpool", "local"
                - dict: Raw config, e.g. {"type": "threadpool", "max_workers": 4}
                - ExecutorConfig: Structured config object
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter settings for pipeline execution.
                Example: {"opentelemetry": True, "tracker": False}
             pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline-specific adapter settings.
                Example: {"tracker": {"project_id": "123", "tags": {"env": "prod"}}}
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project-level adapter settings.
                Example: {"opentelemetry": {"host": "http://localhost:4317"}}
            adapter (dict[str, Any] | None): Custom adapter instance for pipeline
                Example: {"ray_graph_adapter": RayGraphAdapter()}
            reload (bool): Force reload of pipeline configuration.
            run_at (dt.datetime | str | None): Future date to run the job.
                Example: datetime(2025, 4, 28, 12, 0)
                Example str: "2025-04-28T12:00:00" (ISO format)
            run_in (dt.datetime | str | None): Time interval to run the job.
                Example: 3600 (every hour in seconds)
                Example: datetime.timedelta(days=1)
                Example str: "1d" (1 day)
            result_ttl (int | dt.timedelta): Time to live for the job result.
                Example: 3600 (1 hour in seconds)
            log_level (str | None): Logging level for the execution. Default None uses project config.
                Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            max_retries (int): Maximum number of retries for execution.
            retry_delay (float): Delay between retries in seconds.
            jitter_factor (float): Random jitter factor to add to retry delay
            retry_exceptions (tuple): Exceptions that trigger a retry.
            **kwargs: Additional keyword arguments passed to the worker's add_job method.
                For RQ this includes:
                    - result_ttl: Time to live for the job result (float or timedelta)
                    - ttl: Time to live for the job (float or timedelta)
                    - queue_name: Name of the queue to use (str)
                    - retry: Number of retries (int)
                    - repeat: Repeat count (int or dict)
                For APScheduler, this includes:
                    - job_executor: Job executor to use (str)

        Returns:
            str | UUID: The ID of the job.

        Raises:
            ValueError: If the job ID is not valid or if the job cannot be scheduled.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>> pm = PipelineManager()
            >>> job_id = pm.add_job("example_pipeline", inputs={"input1": 42})

        """
⋮----
run_in = (
⋮----
)  # convert to seconds
run_at = (
⋮----
name=name,  # Pass name for logging
# Pass run parameters
⋮----
# reload=reload,  # Note: reload already happened
⋮----
**kwargs,  # Pass worker args
⋮----
"""Schedule a pipeline to run on a recurring or future basis.

        Args:
            name (str): The name of the pipeline to run.
            inputs (dict | None): Inputs for the pipeline run (overrides config).
            final_vars (list[str] | None): Final variables for the pipeline run (overrides config).
            config (dict | None): Hamilton driver config (overrides config).
            cache (bool | dict): Cache settings (overrides config).
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration (overrides config).
            with_adapter_cfg (dict | WithAdapterConfig | None): Adapter configuration (overrides config).
            pipeline_adapter_cfg (dict | PipelineAdapterConfig | None): Pipeline adapter configuration (overrides config).
            project_adapter_cfg (dict | ProjectAdapterConfig | None): Project adapter configuration (overrides config).
            adapter (dict[str, Any] | None): Additional Hamilton adapters (overrides config).
            reload (bool): Whether to reload module and pipeline config. Defaults to False.
            log_level (str | None): Log level for the run (overrides config).
            cron (str | dict[str, str | int] | None): Cron expression or settings
                Example string: "0 0 * * *" (daily at midnight)
                Example dict: {"minute": "0", "hour": "*/2"} (every 2 hours)
            interval (int | str | dict[str, str | int] | None): Time interval for recurring execution
                Example int: 3600 (every hour in seconds)
                Example str: "1h" (every hour)
                Example dict: {"hours": 1, "minutes": 30} (every 90 minutes)
            date (dt.datetime | str | None): Future date for
                Example: datetime(2025, 4, 28, 12, 0)
                Example str: "2025-04-28T12:00:00" (ISO format)
            overwrite (bool): Whether to overwrite existing schedule with the same ID
            schedule_id (str | None): Unique identifier for the schedule
            max_retries (int): Maximum number of retries for execution
            retry_delay (float): Delay between retries in seconds
            jitter_factor (float): Random jitter factor to add to retry delay
            retry_exceptions (tuple): Exceptions that trigger a retry
            **kwargs: JobQueue-specific scheduling options
                For RQ:
                    - result_ttl: Result lifetime (int seconds)
                    - queue_name: Queue to use (str)
                For APScheduler:
                    - misfire_grace_time: Late execution window
                    - coalesce: Combine missed executions (bool)
                    - max_running_jobs: Concurrent instances limit (int)

        Returns:
            str | UUID: Unique identifier for the created schedule

        Raises:
            ValueError: If schedule parameters are invalid
            RuntimeError: If scheduling fails

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>> from datetime import datetime, timedelta
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Daily schedule with cron
            >>> schedule_id = manager.schedule(
            ...     name="daily_metrics",
            ...     cron="0 0 * * *",
            ...     inputs={"date": "{{ execution_date }}"}
            ... )
            >>>
            >>> # Interval-based schedule
            >>> schedule_id = manager.schedule(
            ...     name="monitoring",
            ...     interval={"minutes": 15},
            ...     with_adapter_cfg={"enable_alerts": True}
            ... )
            >>>
            >>> # Future one-time execution
            >>> future_date = datetime.now() + timedelta(days=1)
            >>> schedule_id = manager.schedule(
            ...     name="batch_process",
            ...     date=future_date,
            ...     executor_cfg={"type": "async"}
            ... )
        """
⋮----
run_func = self._get_run_func_for_job(name.name, reload=reload)
interval = (
date = dt.datetime.fromisoformat(date) if isinstance(date, str) else date
⋮----
def schedule_all(self, **kwargs: Any) -> None
⋮----
"""Schedule all pipelines that are enabled in their configuration.

        For each enabled pipeline, applies its configured schedule settings
        and any provided overrides.

        Args:
            **kwargs: Overrides for schedule settings that apply to all pipelines.
                See schedule() method for supported arguments.

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>>
            >>> # Schedule all with default settings
            >>> manager.schedule_all()
            >>>
            >>> # Schedule all with common overrides
            >>> manager.schedule_all(
            ...     max_running_jobs=2,
            ...     coalesce=True,
            ...     misfire_grace_time=300
            ... )
        """
scheduled_ids = []
errors = []
pipeline_names = self.list_pipelines()
⋮----
pipeline_cfg = self._load_pipeline_cfg(name=name, reload=True)
⋮----
schedule_id = self.schedule(name=name, reload=False, **kwargs)
⋮----
@property
    def schedules(self) -> list[Any]
⋮----
"""Get list of current pipeline schedules.

        Retrieves all active schedules from the worker system.

        Returns:
            list[Any]: List of schedule objects. Exact type depends on worker:
                - RQ: List[rq.job.Job]
                - APScheduler: List[apscheduler.schedulers.base.Schedule]

        Example:
            >>> from flowerpower.pipeline import PipelineManager
            >>>
            >>> manager = PipelineManager()
            >>> for schedule in manager.schedules:
            ...     print(f"{schedule.id}: Next run at {schedule.next_run_time}")
        """
````
