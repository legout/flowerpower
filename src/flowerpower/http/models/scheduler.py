from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SchedulerBase(BaseModel):
    name: str
    executor: Optional[str] = "local"
    inputs: Optional[Dict[str, Any]] = None
    final_vars: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    with_tracker: bool = False
    with_opentelemetry: bool = False


class SchedulerAdd(SchedulerBase):
    type: str = "cron"
    paused: bool = False
    coalesce: str = "latest"
    misfire_grace_time: Optional[float] = None
    max_jitter: Optional[float] = None
    max_running_jobs: Optional[int] = None
    conflict_policy: str = "do_nothing"
    crontab: Optional[str] = None
    cron_params: Optional[Dict[str, Any]] = None
    interval_params: Optional[Dict[str, Any]] = None
    calendarinterval_params: Optional[Dict[str, Any]] = None
    date_params: Optional[Dict[str, Any]] = None
    storage_options: Optional[Dict[str, Any]] = None


class SchedulerModify(BaseModel):
    name: str
    paused: Optional[bool] = None
    next_run_time: Optional[datetime] = None


class SchedulerDelete(BaseModel):
    name: str


class SchedulerList(BaseModel):
    pattern: Optional[str] = None


class SchedulerInfo(BaseModel):
    name: str
