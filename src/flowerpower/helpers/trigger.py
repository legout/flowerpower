import datetime as dt
from tzlocal import get_localzone

ALL_TRIGGER_TYPES = [
    "cron",
    "interval",
    "calendarinterval",
    "date",
]
ALL_TRIGGER_KWARGS = {
    "cron": [
        "year",
        "month",
        "week",
        "day",
        "days_of_week",
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
        "weeks",
        "days",
        "hours",
        "minutes",
        "seconds",
        "start_time",
        "end_time",
        "timezone",
    ],
    "date": [
        "start_time",
    ],
}


class Trigger:
    def __init__(
        self,
        type: str,
    ):
        if type not in ALL_TRIGGER_TYPES:
            raise ValueError(
                f"Invalid trigger type: {type}. Valid trigger types are: {ALL_TRIGGER_TYPES}"
            )
        self.trigger_type = type

    def _check_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            if k not in ALL_TRIGGER_KWARGS[self.trigger_type]:
                raise ValueError(
                    f"Invalid argument: {k}. Valid arguments are: {ALL_TRIGGER_KWARGS[self.trigger_type]}"
                )

    def get(self, **kwargs):
        self._check_kwargs(**kwargs)
        if self.trigger_type == "cron":
            return self._get_cron_trigger(**kwargs)
        elif self.trigger_type == "interval":
            return self._get_interval_trigger(**kwargs)
        elif self.trigger_type == "calendarinterval":
            return self._get_calendar_trigger(**kwargs)
        elif self.trigger_type == "date":
            return self._get_date_trigger(**kwargs)

    def _get_cron_trigger(
        self,
        start_time: dt.datetime | None = dt.datetime.now(),
        end_time: dt.datetime | None = None,
        timezone: str | None = None,
        **kwargs,
    ):
        from apscheduler.triggers.cron import CronTrigger

        if timezone is None:
            timezone = get_localzone().key

        crontab = kwargs.pop("crontab", None)

        if crontab is not None:
            return (CronTrigger.from_crontab(crontab), kwargs)
        else:
            return CronTrigger(
                year=kwargs.pop("year", None),
                month=kwargs.pop("month", None),
                week=kwargs.pop("week", None),
                day=kwargs.pop("day", None),
                day_of_week=kwargs.pop("days_of_week", None),
                hour=kwargs.pop("hour", None),
                minute=kwargs.pop("minute", None),
                second=kwargs.pop("second", None),
                start_time=start_time,
                end_time=end_time,
                timezone=timezone,
            )

    def _get_interval_trigger(
        self,
        start_time: dt.datetime | None = dt.datetime.now(),
        end_time: dt.datetime | None = None,
        **kwargs,
    ):
        from apscheduler.triggers.interval import IntervalTrigger

        return IntervalTrigger(
            weeks=kwargs.pop("weeks", 0),
            days=kwargs.pop("days", 0),
            hours=kwargs.pop("hours", 0),
            minutes=kwargs.pop("minutes", 0),
            seconds=kwargs.pop("seconds", 0),
            microseconds=kwargs.pop("microseconds", 0),
            start_time=start_time,
            end_time=end_time,
        )

    def _get_calendar_trigger(
        self,
        start_time: dt.datetime | None = dt.datetime.now(),
        end_time: dt.datetime | None = None,
        timezone: str | None = None,
        **kwargs,
    ):
        from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger

        return CalendarIntervalTrigger(
            weeks=kwargs.pop("weeks", 0),
            days=kwargs.pop("days", 0),
            hours=kwargs.pop("hours", 0),
            minutes=kwargs.pop("minutes", 0),
            seconds=kwargs.pop("seconds", 0),
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
        )

    def _get_date_trigger(self, start_time: dt.datetime, **kwargs):
        from apscheduler.triggers.date import DateTrigger

        return DateTrigger(run_time=start_time)


def get_trigger(trigger_type: str, **kwargs):
    trigger = Trigger(trigger_type)
    return trigger.get(**kwargs)
