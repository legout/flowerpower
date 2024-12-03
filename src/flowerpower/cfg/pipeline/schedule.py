import datetime as dt

from pydantic import Field

from ..base import BaseConfig


class PipelineScheduleCronTriggerConfig(BaseConfig):
    year: str | int | None = None
    month: str | int | None = None
    week: str | int | None = None
    day: str | int | None = None
    day_of_week: str | int | None = None
    hour: str | int | None = None
    minute: str | int | None = None
    second: str | int | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None
    timezone: str | None = None
    crontab: str | None = None


class PipelineScheduleIntervalTriggerConfig(BaseConfig):
    weeks: int | float | None = None
    days: int | float | None = None
    hours: int | float | None = None
    minutes: int | float | None = None
    seconds: int | float | None = None
    microseconds: int | float | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None


class PipelineScheduleCalendarTriggerConfig(BaseConfig):
    years: int | float | None = None
    months: int | float | None = None
    weeks: int | float | None = None
    days: int | float | None = None
    hour: int | float | None = None
    minute: int | float | None = None
    second: int | float | None = None
    start_date: dt.datetime | None = None
    end_date: dt.datetime | None = None
    timezone: str | None = None


class PipelineScheduleDateTriggerConfig(BaseConfig):
    run_time: dt.datetime | None = None


class PipelineScheduleTriggerConfig(BaseConfig):
    cron: PipelineScheduleCronTriggerConfig = Field(
        default_factory=PipelineScheduleCronTriggerConfig
    )
    interval: PipelineScheduleIntervalTriggerConfig = Field(
        default_factory=PipelineScheduleIntervalTriggerConfig
    )
    calendar: PipelineScheduleCalendarTriggerConfig = Field(
        default_factory=PipelineScheduleCalendarTriggerConfig
    )
    date: PipelineScheduleDateTriggerConfig = Field(
        default_factory=PipelineScheduleDateTriggerConfig
    )
    type_: str | None = None


class PipelineScheduleRunConfig(BaseConfig):
    id_: str | None = None
    executor: str | None = None
    paused: bool = False
    coalesce: str = "latest"  # other options are "all" and "earliest"
    misfire_grace_time: int | float | dt.timedelta | None = None
    max_jitter: int | float | dt.timedelta | None = None
    max_running_jobs: int | None = None
    conflict_policy: str | None = (
        "do_nothing"  # other options are "replace" and "exception"
    )


class PipelineScheduleConfig(BaseConfig):
    run: PipelineScheduleRunConfig = Field(default_factory=PipelineScheduleRunConfig)
    trigger: PipelineScheduleTriggerConfig = Field(
        default_factory=PipelineScheduleTriggerConfig
    )
