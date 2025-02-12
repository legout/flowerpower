import datetime as dt

from pydantic import BaseModel, Field


class PipelineRun(BaseModel):
    inputs: dict | None = None
    final_vars: list | None = None
    executor: str | None = None
    config: dict | None = None
    with_tracker: bool | None = None
    with_opentelemetry: bool | None = None
    with_progressbar: bool | None = None


class PipelineAddJob(PipelineRun):
    result_expiration_time: float | dt.timedelta = 0


class PipelineSchedule(PipelineRun):
    trigger_type: str | None = None
    paused: bool = False
    coalesce: str = "latest"
    misfire_grace_time: float | dt.timedelta | None = None
    max_jitter: float | dt.timedelta | None = Field
    max_running_jobs: int | None = None
    conflict_policy: str = "do_nothing"


class PipelineManagerNew(BaseModel):
    overwrite: bool = False


class PipelineManagerImportExport(BaseModel):
    path: str
    name: str | None = None
    names: list[str] | None = None
    cfg_dir: str = "conf"
    pipeline_dir: str = "pipelines"
    storage_options: dict | None = None
    overwrite: bool = False


class PipelineDelete(BaseModel):
    name: str
    cfg: bool = False
    module: bool = False


class PipelineManagerSummary(BaseModel):
    cfg: bool = True
    module: bool = True
