from pydantic import Field
from ..base import BaseConfig
import datetime as dt


class PipelineScheduleCronTriggerConfig(BaseConfig):
    year: str | int | None = Field(default=None)
    month: str | int | None = Field(default=None)
    week: str | int | None = Field(default=None)
    day: str | int | None = Field(default=None)
    day_of_week: str | int | None = Field(default=None)
    hour: str | int | None = Field(default=None)
    minute: str | int | None = Field(default=None)
    second: str | int | None = Field(default=None)
    start_time: dt.datetime | None = Field(default=None)
    end_time: dt.datetime | None = Field(default=None)
    timezone: str | None = Field(default=None)
    crontab: str | None = Field(default=None)


class PipelineScheduleIntervalTriggerConfig(BaseConfig):
    weeks: int | float | None = Field(default=None)
    days: int | float | None = Field(default=None)
    hours: int | float | None = Field(default=None)
    minutes: int | float | None = Field(default=None)
    seconds: int | float | None = Field(default=None)
    microseconds: int | float | None = Field(default=None)
    start_time: dt.datetime | None = Field(default=None)
    end_time: dt.datetime | None = Field(default=None)


class PipelineScheduleCalendarTriggerConfig(BaseConfig):
    years: int | float | None = Field(default=None)
    months: int | float | None = Field(default=None)
    weeks: int | float | None = Field(default=None)
    days: int | float | None = Field(default=None)
    hour: int | float | None = Field(default=None)
    minute: int | float | None = Field(default=None)
    second: int | float | None = Field(default=None)
    start_date: dt.datetime | None = Field(default=None)
    end_date: dt.datetime | None = Field(default=None)
    timezone: str | None = Field(default=None)


class PipelineScheduleDateTriggerConfig(BaseConfig):
    run_time: dt.datetime | None = Field(default=None)


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
    type_: str | None = Field(default=None)


class PipelineScheduleRunConfig(BaseConfig):
    id_: str | None = Field(default=None)
    executor: str | None = Field(default=None)
    paused: bool = Field(default=False)
    coalesce: str = Field(default="latest")  # other options are "all" and "earliest"
    misfire_grace_time: int | float | dt.timedelta | None = Field(default=None)
    max_jitter: int | float | dt.timedelta | None = Field(default=None)
    max_running_jobs: int | None = Field(default=None)
    conflict_policy: str | None = Field(
        default="do_nothing"
    )  # other options are "replace" and "exception"


class PipelineScheduleConfig(BaseConfig):
    run: PipelineScheduleRunConfig = Field(default_factory=PipelineScheduleRunConfig)
    trigger: PipelineScheduleTriggerConfig = Field(
        default_factory=PipelineScheduleTriggerConfig
    )
