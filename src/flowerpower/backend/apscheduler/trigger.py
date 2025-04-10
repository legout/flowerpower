import datetime as dt
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger

from ..base import BaseTrigger
from typing import Any

ALL_TRIGGER_TYPES = [
    "cron",
    "interval",
    "calendarinterval",
    "date",
]
ALL_TRIGGER_KWARGS = {
    "cron": [
        "crontab",
        "year",
        "month",
        "week",
        "day",
        "day_of_week",
        "hour",
        "minute",
        "second",
        "start_time",
        "end_time",
        "timezone",
    ],
    "interval": [
        "weeks",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "start_time",
        "end_time",
    ],
    "calendarinterval": [
        "years",
        "months",
        "weeks",
        "days",
        "hour",
        "minute",
        "second",
        "start_date",
        "end_date",
        "timezone",
    ],
    "date": [
        "run_time",
    ],
}


class APSchedulerTrigger(BaseTrigger):
    """Implementation of BaseTrigger for APScheduler."""
    

    def _check_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            if k not in ALL_TRIGGER_KWARGS[self.trigger_type]:
                raise ValueError(
                    f"Invalid argument: {k}. Valid arguments are: {ALL_TRIGGER_KWARGS[self.trigger_type]}"
                )

    def _filter_kwargs(self, **kwargs):
        return {
            k: v
            for k, v in kwargs.items()
            if k in ALL_TRIGGER_KWARGS[self.trigger_type] and v is not None
        }

    def get_trigger_instance(self, **kwargs) -> Any:
        """
        Get an APScheduler trigger instance based on the trigger type.
        
        Args:
            **kwargs: Keyword arguments for the trigger
            
        Returns:
            Any: An APScheduler trigger instance
        """
        
        self._check_kwargs(**kwargs)
        
        kwargs = self._filter_kwargs(**kwargs)

        if self.trigger_type == "cron":
            crontab = kwargs.pop("crontab", None)
            if crontab:
                return CronTrigger.from_crontab(crontab)
            return CronTrigger(**kwargs)
        elif self.trigger_type == "interval":
            return IntervalTrigger(**kwargs)
        elif self.trigger_type == "calendarinterval":
            return CalendarIntervalTrigger(**kwargs)
        elif self.trigger_type == "date":
            # Default to now if not specified
            if "run_time" not in kwargs:
                kwargs["run_time"] = dt.datetime.now()
            return DateTrigger(**kwargs)
        else:
            raise ValueError(f"Unknown trigger type: {self.trigger_type}")


#def get_trigger(type_: str, **kwargs):
#    trigger = Trigger(type_)
#    return trigger.get(**kwargs)
