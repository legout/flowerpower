import datetime as dt
import importlib.util
import importlib
import os
import sys
from typing import Optional, Any, Callable

from dateutil import tz
from hamilton import driver
from hamilton_sdk import adapters
from loguru import logger
from munch import munchify, unmunchify
from .constants import PIPELINE_PY_TEMPLATE
from .cfg import Config


if importlib.util.find_spec("apscheduler"):
    from .scheduler import get_scheduler
else:
    get_scheduler = None


from .helpers import get_executor


class PipelineManager:
    def __init__(self, base_path: str | None = None):
        # self.name = pipeline.split(".")[-1]
        self._base_path = base_path or ""
        self._conf_path = os.path.join(self._base_path, "conf")
        self._pipeline_path = os.path.join(self._base_path, "pipelines")
        sys.path.append(self._pipeline_path)

        # self._load_module()
        self._load_config()

    def _load_module(self, name: str):
        if not hasattr(self, "_module"):
            self._module = importlib.import_module(name)
        else:
            self._module = importlib.reload(self._modul)

    def _load_config(self):
        self.cfg = Config(path=self._conf_path)

    def reload_module(self, name: str):
        self._load_module(name)

    def reload_config(self):
        self.cfg = Config(path=self._conf_path)

    def _get_driver(
        self,
        name: str,
        executor: str | None = None,
        with_tracker: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> tuple[driver.Driver, Callable | None]:
        max_tasks = kwargs.pop("max_tasks", 20)
        num_cpus = kwargs.pop("num_cpus", 4)
        executor_, shutdown = get_executor(
            executor or "local", max_tasks=max_tasks, num_cpus=num_cpus
        )
        if reload or not hasattr(self, "_module"):
            self._load_module(name)

        if with_tracker:
            project_id = kwargs.pop("project_id", None) or self.cfg.tracker.pipeline[
                name
            ].get("project_id", None)
            username = kwargs.pop("username", None) or self.cfg.tracker.get(
                "username", None
            )
            dag_name = kwargs.pop("dag_name", None) or self.cfg.tracker.pipeline[
                name
            ].get("dag_name", None)
            tags = kwargs.pop("tags", None) or self.cfg.tracker.pipeline[name].get(
                "tags", None
            )
            api_url = kwargs.pop("api_url", None) or self.cfg.tracker.get(
                "api_url", None
            )
            ui_url = kwargs.pop("ui_url", None) or self.cfg.tracker.get("ui_url", None)

            if project_id is None:
                raise ValueError(
                    "Please provide a project_id if you want to use the tracker"
                )

            tracker = adapters.HamiltonTracker(
                project_id=project_id,
                username=username,
                dag_name=dag_name,
                tags=tags,
                hamilton_api_url=api_url,
                hamilton_ui_url=ui_url,
            )

            dr = (
                driver.Builder()
                .with_modules(self._module)
                .enable_dynamic_execution(allow_experimental_mode=True)
                .with_adapters(tracker)
                .with_remote_executor(executor_)
                .build()
            )
        else:
            dr = (
                driver.Builder()
                .with_modules(self._module)
                .enable_dynamic_execution(allow_experimental_mode=True)
                .with_remote_executor(executor_)
                .build()
            )

        return dr, shutdown

    def run(
        self,
        name: str,
        environment: str = "prod",
        executor: str | None = None,
        inputs: dict | None = None,
        final_vars: list | None = None,
        with_tracker: bool | None = None,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        logger.info(f"Starting pipeline {name} in environment {environment}")

        run_params = self.cfg.pipeline.run.get(name)[environment]

        final_vars = final_vars or run_params.get("final_vars", [])
        inputs = {**(run_params.get("inputs", {}) or {}), **(inputs or {})}
        with_tracker = with_tracker or run_params.get("with_tracker", False)

        dr, shutdown = self._get_driver(
            name=name,
            executor=executor,
            with_tracker=with_tracker,
            reload=reload,
            **kwargs,
        )

        res = dr.execute(final_vars=final_vars, inputs=unmunchify(inputs))

        logger.success(f"Finished pipeline {name}")

        if shutdown is not None:
            shutdown()

        return res

    def schedule(
        self,
        name: str,
        environment: str = "prod",
        executor: str | None = None,
        type: str = "cron",
        auto_start: bool = True,
        background: bool = False,
        inputs: dict | None = None,
        final_vars: list | None = None,
        with_tracker: bool | None = None,
        **kwargs,
    ):
        if get_scheduler is None:
            raise ValueError("APScheduler4 not installed. Please install it first.")

        start_time = kwargs.pop(
            "start_time", dt.datetime.now()
        ) or self.cfg.scheduler.pipeline[name].get("start_time", dt.datetime.now())
        end_time = kwargs.pop("end_time", None) or self.cfg.scheduler.pipeline[
            name
        ].get("end_time", None)

        scheduler = get_scheduler(
            name=name, conf_path=self._conf_path, pipelines_path=self._pipeline_path
        )
        trigger = self._get_trigger(name, type, start_time, end_time, **kwargs)

        id_ = scheduler.add_schedule(
            self.run,
            trigger=trigger,
            args=(name, environment, executor, inputs, final_vars, with_tracker),
            kwargs=kwargs,
        )
        logger.success(
            f"Added scheduler for {name} in environment {environment} with id {id_}"
        )

        if auto_start:
            if background:
                scheduler.start_in_background()
                return scheduler, id_
            else:
                scheduler.run_until_stopped()

    def _get_trigger(
        self,
        name: str,
        type: str,
        start_time: dt.datetime,
        end_time: Optional[dt.datetime],
        **kwargs,
    ):
        if type == "cron":
            return self._get_cron_trigger(name, start_time, end_time, **kwargs)
        elif type == "interval":
            return self._get_interval_trigger(name, start_time, end_time, **kwargs)
        elif type == "calendar":
            return self._get_calendar_trigger(name, start_time, end_time, **kwargs)
        elif type == "date":
            return self._get_date_trigger(start_time)
        else:
            raise ValueError(f"Unknown trigger type: {type}")

    def _get_cron_trigger(
        self,
        name: str,
        start_time: dt.datetime,
        end_time: Optional[dt.datetime],
        **kwargs,
    ):
        from apscheduler.triggers.cron import CronTrigger

        crontab = kwargs.pop("crontab", None) or self.cfg.scheduler.pipeline[name].get(
            "crontab", None
        )
        if crontab is not None:
            return CronTrigger.from_crontab(crontab)
        else:
            return CronTrigger(
                year=kwargs.pop("year", None)
                or self.cfg.scheduler.pipeline[name].get("year", None),
                month=kwargs.pop("month", None)
                or self.cfg.scheduler.pipeline[name].get("month", None),
                week=kwargs.pop("week", None)
                or self.cfg.scheduler.pipeline[name].get("week", None),
                day=kwargs.pop("day", None)
                or self.cfg.scheduler.pipeline[name].get("day", None),
                day_of_week=kwargs.pop("days_of_week", None)
                or self.cfg.scheduler.pipeline[name].get("days_of_week", None),
                hour=kwargs.pop("hour", None)
                or self.cfg.scheduler.pipeline[name].get("hour", None),
                minute=kwargs.pop("minute", None)
                or self.cfg.scheduler.pipeline[name].get("minute", None),
                second=kwargs.pop("second", None)
                or self.cfg.scheduler.pipeline[name].get("second", None),
                start_time=start_time,
                end_time=end_time,
                timezone=kwargs.pop("timezone", tz.gettz("Europe/Berlin"))
                or self.cfg.scheduler.pipeline[name].get(
                    "timezone", tz.gettz("Europe/Berlin")
                ),
            )

    def _get_interval_trigger(
        self,
        name: str,
        start_time: dt.datetime,
        end_time: Optional[dt.datetime],
        **kwargs,
    ):
        from apscheduler.triggers.interval import IntervalTrigger

        return IntervalTrigger(
            weeks=kwargs.pop("weeks", 0)
            or self.cfg.scheduler.pipeline[name].get("weeks", 0),
            days=kwargs.pop("days", 0)
            or self.cfg.scheduler.pipeline[name].get("days", 0),
            hours=kwargs.pop("hours", 0)
            or self.cfg.scheduler.pipeline[name].get("hours", 0),
            minutes=kwargs.pop("minutes", 0)
            or self.cfg.scheduler.pipeline[name].get("minutes", 0),
            seconds=kwargs.pop("seconds", 0)
            or self.cfg.scheduler.pipeline[name].get("seconds", 0),
            microseconds=kwargs.pop("microseconds", 0)
            or self.cfg.scheduler.pipeline[name].get("microseconds", 0),
            start_time=start_time,
            end_time=end_time,
        )

    def _get_calendar_trigger(
        self,
        name: str,
        start_time: dt.datetime,
        end_time: Optional[dt.datetime],
        **kwargs,
    ):
        from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger

        return CalendarIntervalTrigger(
            weeks=kwargs.pop("weeks", 0)
            or self.cfg.scheduler.pipeline[name].get("weeks", 0),
            days=kwargs.pop("days", 0)
            or self.cfg.scheduler.pipeline[name].get("days", 0),
            hours=kwargs.pop("hours", 0)
            or self.cfg.scheduler.pipeline[name].get("hours", 0),
            minutes=kwargs.pop("minutes", 0)
            or self.cfg.scheduler.pipeline[name].get("minutes", 0),
            seconds=kwargs.pop("seconds", 0)
            or self.cfg.scheduler.pipeline[name].get("seconds", 0),
            start_time=start_time,
            end_time=end_time,
            timezone=kwargs.pop("timezone", tz.gettz("Europe/Berlin"))
            or self.cfg.scheduler.pipeline[name].get(
                "timezone", tz.gettz("Europe/Berlin")
            ),
        )

    def _get_date_trigger(self, start_time: dt.datetime):
        from apscheduler.triggers.date import DateTrigger

        return DateTrigger(run_time=start_time)

    def new(
        self,
        name: str,
        overwrite: bool = False,
        params: dict | None = None,
        run: dict | None = None,
        schedule: dict | None = None,
        tracker: dict | None = None,
    ):
        self.add(name, overwrite, params, run, schedule, tracker)

    def add(
        self,
        name: str,
        overwrite: bool = False,
        params: dict | None = None,
        run: dict | None = None,
        schedule: dict | None = None,
        tracker: dict | None = None,
    ):
        logger.info(f"Creating new pipeline {name}")

        if not os.path.exists(self._conf_path):
            raise ValueError(
                f"Configuration path {self._conf_path} does not exist. Please run flowerpower init first."
            )
        if not os.path.exists(self._pipeline_path):
            raise ValueError(
                f"Pipeline path {self._pipeline_path} does not exist. Please run flowerpower init first."
            )

        if os.path.exists(f"{self._pipeline_path}/{name}.py") and not overwrite:
            raise ValueError(
                f"Pipeline {name} already exists. Use `overwrite=True` to overwrite."
            )

        os.makedirs(self._pipeline_path, exist_ok=True)
        with open(f"{self._pipeline_path}/{name}.py", "w") as f:
            f.write(
                PIPELINE_PY_TEMPLATE.format(
                    name=name, date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
        logger.info(f"Created pipeline module {name}.py")

        self._update_pipeline_config(name, params, run)
        self._update_scheduler_config(name, schedule)
        self._update_tracker_config(name, tracker)

        logger.success(f"Created pipeline {name}")

    def _update_pipeline_config(self, name: str, params: dict | None, run: dict | None):
        pipeline_cfg = self.cfg.get("pipeline", None) or munchify(
            {"run": {}, "params": {}}
        )
        if pipeline_cfg.params is None:
            pipeline_cfg.params = {}
        if pipeline_cfg.run is None:
            pipeline_cfg.run = {}

        pipeline_cfg.params[name] = params or None
        pipeline_cfg.run[name] = run or munchify(
            {
                "dev": {"inputs": None, "final_vars": None, "with_tracker": False},
                "prod": {"inputs": None, "final_vars": None, "with_tracker": True},
            }
        )

        self.cfg.write(pipeline_cfg, "pipeline", self._conf_path)
        logger.info(f"Updated pipeline configuration {self._conf_path}/pipeline.yml")

    def _update_scheduler_config(self, name: str, schedule: dict | None):
        self.cfg.scheduler = self.cfg.get("scheduler", None) or munchify(
            {
                "data_store": {"type": "memory"},
                "event_broker": {"type": "local"},
                "pipeline": {},
            }
        )
        if self.cfg.scheduler.pipeline is None:
            self.cfg.scheduler.pipeline = {}
        self.cfg.scheduler.pipeline[name] = schedule or {"type": None}

        self.cfg.write(self.cfg.scheduler, "scheduler", self._conf_path)
        logger.info(f"Updated scheduler configuration {self._conf_path}/scheduler.yml")

    def _update_tracker_config(self, name: str, tracker: dict | None):
        tracker_cfg = self.cfg.get("tracker", None) or munchify(
            {
                "username": None,
                "api_url": "http://localhost:8241",
                "ui_url": "http://localhost:8242",
                "api_key": None,
                "pipeline": {},
            }
        )
        if tracker_cfg.pipeline is None:
            tracker_cfg.pipeline = {}

        tracker_cfg.pipeline[name] = tracker or {
            "project_id": None,
            "dag_name": None,
            "tags": None,
        }

        self.cfg.write(tracker_cfg, "tracker", self._conf_path)
        logger.info(f"Updated tracker configuration {self._conf_path}/tracker.yml")

    def delete(self):
        # TODO: Implement delete functionality
        pass

    def show(self, name, format: str = "png", view: bool = False, reload: bool = False):
        os.makedirs("graphs", exist_ok=True)
        dr, _ = self._get_driver(
            name=name, executor=None, with_tracker=False, reload=reload
        )
        if view:
            pass


class Pipeline(PipelineManager):
    def __init__(self, name: str, base_path: str | None = None):
        super().__init__(base_path)
        self.name = name
        self._load_module(name)

    def run(
        self,
        environment: str = "prod",
        executor: str | None = None,
        inputs: dict | None = None,
        final_vars: list | None = None,
        with_tracker: bool = False,
        reload: bool = False,
        **kwargs,
    ) -> Any:
        return super().run(
            name=self.name,
            environment=environment,
            executor=executor,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            reload=reload,
            **kwargs,
        )

    def schedule(
        self,
        environment: str = "prod",
        executor: str | None = None,
        type: str = "cron",
        auto_start: bool = True,
        background: bool = False,
        inputs: dict | None = None,
        final_vars: list | None = None,
        with_tracker: bool = False,
        **kwargs,
    ):
        return super().schedule(
            name=self.name,
            environment=environment,
            executor=executor,
            type=type,
            auto_start=auto_start,
            background=background,
            inputs=inputs,
            final_vars=final_vars,
            with_tracker=with_tracker,
            **kwargs,
        )

    def show(self, format: str = "png", view: bool = False, reload: bool = False):
        return super().show(self.name, format=format, view=view, reload=reload)

    def reload_module(self, name: str):
        return super().reload_module(name)


def add(
    name: str,
    overwrite: bool = False,
    params: dict | None = None,
    run: dict | None = None,
    schedule: dict | None = None,
    tracker: dict | None = None,
    base_path: str | None = None,
):
    pm = PipelineManager(base_path=base_path)
    pm.add(name, overwrite, params, run, schedule, tracker)

def new(
    name: str,
    overwrite: bool = False,
    params: dict | None = None,
    run: dict | None = None,
    schedule: dict | None = None,
    tracker: dict | None = None,
    base_path: str | None = None,
):
    pm = PipelineManager(base_path=base_path)
    pm.new(name, overwrite, params, run, schedule, tracker)

def run(
    name: str,
    environment: str = "prod",
    executor: str | None = None,
    inputs: dict | None = None,
    final_vars: list | None = None,
    with_tracker: bool = False,
    base_path: str | None = None,
    reload: bool = False,
    **kwargs,
) -> Any:
    p = Pipeline(name=name, base_path=base_path)
    return p.run(
        environment, executor, inputs, final_vars, with_tracker, reload, **kwargs
    )


def schedule(
    name: str,
    environment: str = "prod",
    executor: str | None = None,
    type: str = "cron",
    auto_start: bool = True,
    background: bool = False,
    inputs: dict | None = None,
    final_vars: list | None = None,
    with_tracker: bool = False,
    base_path: str | None = None,
    **kwargs,
):
    p = Pipeline(name=name, base_path=base_path)
    p.schedule(
        environment,
        executor,
        type,
        auto_start,
        background,
        inputs,
        final_vars,
        with_tracker,
        **kwargs,
    )


def show(
    name: str,
    format: str = "png",
    view: bool = False,
    base_path: str | None = None,
    reload: bool = False,
):
    pm = PipelineManager(base_path=base_path)
    pm.show(name, format=format, view=view, reload=reload)
