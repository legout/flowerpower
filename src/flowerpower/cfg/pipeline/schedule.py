import datetime as dt

import msgspec
from munch import munchify

from ..base import BaseConfig

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


# class ScheduleIntervalTriggerConfig(BaseConfig):
#     weeks: int | float | None = None
#     days: int | float | None = None
#     hours: int | float | None = None
#     minutes: int | float | None = None
#     seconds: int | float | None = None
#     microseconds: int | float | None = None
#     start_time: dt.datetime | None = None
#     end_time: dt.datetime | None = None


# class ScheduleCalendarTriggerConfig(BaseConfig):
#     years: int | float | None = None
#     months: int | float | None = None
#     weeks: int | float | None = None
#     days: int | float | None = None
#     hour: int | float | None = None
#     minute: int | float | None = None
#     second: int | float | None = None
#     start_date: dt.datetime | None = None
#     end_date: dt.datetime | None = None
#     timezone: str | None = None


# class ScheduleDateTriggerConfig(BaseConfig):
#     run_time: dt.datetime | None = None


class ScheduleConfig(BaseConfig):
    cron: str | dict | None = msgspec.field(default=None)
    interval: str | int | dict | None = msgspec.field(default=None)
    date: str | None = msgspec.field(default=None)

    def __post_init__(self):
        if isinstance(self.date, str):
            try:
                self.date = dt.datetime.fromisoformat(self.date)
            except ValueError:
                raise ValueError(
                    f"Invalid date format: {self.date}. Expected ISO format."
                )
        if isinstance(self.cron, dict):
            self.cron = munchify(self.cron)
        if isinstance(self.interval, dict):
            self.interval = munchify(self.interval)


# class ScheduleConfig(BaseConfig):
#     run: ScheduleRunConfig = msgspec.field(default_factory=ScheduleRunConfig)
#     trigger: ScheduleTriggerConfig = msgspec.field(
#         default_factory=ScheduleTriggerConfig
#     )
