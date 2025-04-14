# src/flowerpower/worker/huey/trigger.py
"""
Huey-specific trigger implementations for FlowerPower.

Maps FlowerPower's abstract trigger concepts to Huey's scheduling mechanisms.
"""

import datetime as dt
from typing import Any, Dict, Optional

from huey import crontab

from ..base import BaseTrigger


class HueyCronTrigger(BaseTrigger):
    """
    Represents a cron-style trigger for Huey.

    Uses huey.crontab for scheduling.
    Note: Huey's crontab does not support seconds.
    """

    def __init__(
        self,
        minute: str = "*",
        hour: str = "*",
        day: str = "*",
        day_of_week: str = "*",
        month: str = "*",
        # Huey crontab doesn't support seconds, so we don't accept it here.
    ):
        super().__init__(trigger_type="cron")
        self.minute = minute
        self.hour = hour
        self.day = day
        self.day_of_week = day_of_week
        self.month = month

    def get_trigger_instance(self, **kwargs) -> crontab:
        """
        Returns a huey.crontab instance configured with the stored parameters.
        """
        return crontab(
            minute=self.minute,
            hour=self.hour,
            day=self.day,
            day_of_week=self.day_of_week,
            month=self.month,
        )


class HueyIntervalTrigger(BaseTrigger):
    """
    Represents an interval-based trigger for Huey.

    Uses a simple delay in seconds.
    """

    def __init__(
        self,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        super().__init__(trigger_type="interval")
        self.interval = dt.timedelta(
            weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds
        )

    def get_trigger_instance(self, **kwargs) -> Dict[str, float]:
        """
        Calculates the total delay in seconds and returns it in a dictionary
        suitable for Huey's simple schedule (delay).
        """
        total_seconds = self.interval.total_seconds()
        # Huey's simple schedule uses 'delay' for intervals
        return {"delay": total_seconds}


class HueyDateTrigger(BaseTrigger):
    """
    Represents a specific date/time trigger for Huey.

    Uses the 'eta' parameter for scheduling.
    """

    def __init__(self, run_date: dt.datetime):
        super().__init__(trigger_type="date")
        if not isinstance(run_date, dt.datetime):
            raise TypeError("run_date must be a datetime object")
        self.run_date = run_date

    def get_trigger_instance(self, **kwargs) -> Dict[str, dt.datetime]:
        """
        Returns a dictionary with the 'eta' key set to the specific run date,
        suitable for Huey's schedule.
        """
        return {"eta": self.run_date}