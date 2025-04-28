import datetime as dt
from enum import Enum
from typing import Any, Dict, Type

from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from ..base import BaseTrigger


class TriggerType(Enum):
    CRON = "cron"
    INTERVAL = "interval"
    CALENDARINTERVAL = "calendarinterval"
    DATE = "date"


# Mapping of trigger type to its class and allowed kwargs
TRIGGER_CONFIG: Dict[TriggerType, Dict[str, Any]] = {
    TriggerType.CRON: {
        "class": CronTrigger,
        "kwargs": [
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
    },
    TriggerType.INTERVAL: {
        "class": IntervalTrigger,
        "kwargs": [
            "weeks",
            "days",
            "hours",
            "minutes",
            "seconds",
            "microseconds",
            "start_time",
            "end_time",
        ],
    },
    TriggerType.CALENDARINTERVAL: {
        "class": CalendarIntervalTrigger,
        "kwargs": [
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
    },
    TriggerType.DATE: {
        "class": DateTrigger,
        "kwargs": [
            "run_time",
        ],
    },
}


class APSTrigger(BaseTrigger):
    """
    Implementation of BaseTrigger for APScheduler.

    Provides a factory for creating APScheduler trigger instances
    with validation and filtering of keyword arguments.
    """

    trigger_type: TriggerType

    def __init__(self, trigger_type: str):
        """
        Initialize APSchedulerTrigger with a trigger type.

        Args:
            trigger_type (str): The type of trigger (cron, interval, calendarinterval, date).

        Raises:
            ValueError: If the trigger_type is invalid.
        """
        try:
            self.trigger_type = TriggerType(trigger_type.lower())
        except ValueError:
            valid_types = [t.value for t in TriggerType]
            raise ValueError(
                f"Invalid trigger type '{trigger_type}'. Valid types are: {valid_types}"
            )

    def _get_allowed_kwargs(self) -> set:
        """Return the set of allowed kwargs for the current trigger type."""
        return set(TRIGGER_CONFIG[self.trigger_type]["kwargs"])

    def _check_kwargs(self, **kwargs) -> None:
        """
        Validate that all provided kwargs are allowed for the trigger type.

        Raises:
            ValueError: If any kwarg is not allowed.
        """
        allowed = self._get_allowed_kwargs()
        invalid = [k for k in kwargs if k not in allowed]
        if invalid:
            raise ValueError(
                f"Invalid argument(s) for trigger type '{self.trigger_type.value}': {invalid}. "
                f"Allowed arguments are: {sorted(allowed)}"
            )

    def _filter_kwargs(self, **kwargs) -> Dict[str, Any]:
        """
        Filter kwargs to only those allowed for the trigger type and not None.

        Returns:
            Dict[str, Any]: Filtered kwargs.
        """
        allowed = self._get_allowed_kwargs()
        return {k: v for k, v in kwargs.items() if k in allowed and v is not None}

    def get_trigger_instance(self, **kwargs) -> Any:
        """
        Create and return an APScheduler trigger instance based on the trigger type.

        Args:
            **kwargs: Keyword arguments for the trigger.

        Returns:
            Any: An APScheduler trigger instance.

        Raises:
            ValueError: If invalid arguments are provided or trigger type is unknown.
        """
        self._check_kwargs(**kwargs)
        filtered_kwargs = self._filter_kwargs(**kwargs)
        trigger_cls: Type = TRIGGER_CONFIG[self.trigger_type]["class"]

        if self.trigger_type == TriggerType.CRON:
            crontab = filtered_kwargs.pop("crontab", None)
            if crontab:
                return trigger_cls.from_crontab(crontab)
            return trigger_cls(**filtered_kwargs)
        elif self.trigger_type == TriggerType.INTERVAL:
            return trigger_cls(**filtered_kwargs)
        elif self.trigger_type == TriggerType.CALENDARINTERVAL:
            return trigger_cls(**filtered_kwargs)
        elif self.trigger_type == TriggerType.DATE:
            # Default to now if not specified
            if "run_time" not in filtered_kwargs:
                filtered_kwargs["run_time"] = dt.datetime.now()
            return trigger_cls(**filtered_kwargs)
        else:
            # This should never be reached due to Enum validation in __init__
            raise ValueError(f"Unknown trigger type: {self.trigger_type.value}")


# End of file
