import datetime as dt

import msgspec

from .. import BaseConfig


class ScheduleCronTriggerConfig(BaseConfig):
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


class ScheduleIntervalTriggerConfig(BaseConfig):
    weeks: int | float | None = None
    days: int | float | None = None
    hours: int | float | None = None
    minutes: int | float | None = None
    seconds: int | float | None = None
    microseconds: int | float | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None


class ScheduleCalendarTriggerConfig(BaseConfig):
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


class ScheduleDateTriggerConfig(BaseConfig):
    run_time: dt.datetime | None = None


class ScheduleTriggerConfig(BaseConfig):
    cron: ScheduleCronTriggerConfig = msgspec.field(
        default_factory=ScheduleCronTriggerConfig
    )
    interval: ScheduleIntervalTriggerConfig = msgspec.field(
        default_factory=ScheduleIntervalTriggerConfig
    )
    calendar: ScheduleCalendarTriggerConfig = msgspec.field(
        default_factory=ScheduleCalendarTriggerConfig
    )
    date: ScheduleDateTriggerConfig = msgspec.field(
        default_factory=ScheduleDateTriggerConfig
    )
    type_: str | None = None


class ScheduleRunConfig(BaseConfig):
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


class ScheduleConfig(BaseConfig):
    run: ScheduleRunConfig = msgspec.field(default_factory=ScheduleRunConfig)
    trigger: ScheduleTriggerConfig = msgspec.field(
        default_factory=ScheduleTriggerConfig
    )
