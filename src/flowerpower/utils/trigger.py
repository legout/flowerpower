import datetime as dt

# from tzlocal import get_localzone

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


class Trigger:
    def __init__(
        self,
        type_: str,
    ):
        if type_ not in ALL_TRIGGER_TYPES:
            raise ValueError(
                f"Invalid trigger type: {type_}. Valid trigger types are: {ALL_TRIGGER_TYPES}"
            )
        self.trigger_type = type_

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

    def get(self, **kwargs):
        #
        kwargs = self._filter_kwargs(**kwargs)
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
        **kwargs,
    ):
        from apscheduler.triggers.cron import CronTrigger

        crontab = kwargs.pop("crontab", None)
        print(crontab)

        if crontab is not None:
            return CronTrigger.from_crontab(crontab)  # , kwargs)
        else:
            return CronTrigger(
                **kwargs,
            )

    def _get_interval_trigger(
        self,
        **kwargs,
    ):
        from apscheduler.triggers.interval import IntervalTrigger

        return IntervalTrigger(
            **kwargs,
        )

    def _get_calendar_trigger(
        self,
        **kwargs,
    ):
        from apscheduler.triggers.calendarinterval import \
            CalendarIntervalTrigger

        return CalendarIntervalTrigger(
            **kwargs,
        )

    def _get_date_trigger(self, **kwargs):
        from apscheduler.triggers.date import DateTrigger

        if "run_time" not in kwargs:
            kwargs["run_time"] = dt.datetime.now()
        return DateTrigger(**kwargs)


def get_trigger(type_: str, **kwargs):
    trigger = Trigger(type_)
    return trigger.get(**kwargs)
