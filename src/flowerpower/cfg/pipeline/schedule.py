import datetime as dt

import msgspec
from munch import munchify

from ..base import BaseConfig


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
