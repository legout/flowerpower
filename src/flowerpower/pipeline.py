import datetime as dt
import importlib.util
import importlib
import os
import sys
from typing import Optional, List, Dict, Any

from dateutil import tz
from hamilton import driver
from hamilton.execution import executors
from hamilton_sdk import adapters
from loguru import logger
from munch import munchify, unmunchify
from .constants import PIPELINE_PY_TEMPLATE
from .cfg import Config
  

if importlib.util.find_spec("apscheduler"):
    from .scheduler import get_scheduler
else:
    get_scheduler = None

from .helpers import _get_executor



class PipelineManager:
    def __init__(self,pipeline:str, base_path: str|None = None):
        self.name = pipeline
        self._base_path = base_path
        self._conf_path = os.path.join(base_path, "conf")
        self._pipeline_path = os.path.join(base_path, "pipelines")
        sys.path.append(self._pipeline_path)

        self._load_module()
        self._load_config()

    def _load_module(self):
        if not hasattr(self, "_module"):
            self._module = importlib.import_module(self.name)
        else:
            self._module = importlib.reload(self._module)
            
    def _load_config(self):
        self.cfg = Config(path=self._conf_path)
        
            
    def reload_module(self):
        self._load_module()
        
    def reload_config(self):
        self.cfg = Config(path=self._conf_path)
        

   

    def _get_driver(self, executor: str|None = None, with_tracker: bool = False, **kwargs) -> tuple[driver.Driver, callable|None]:

        
        max_tasks = kwargs.pop("max_tasks", 20)
        num_cpus = kwargs.pop("num_cpus", 4)
        executor_, shutdown = _get_executor(executor or "local", max_tasks=max_tasks, num_cpus=num_cpus)

        if with_tracker:
            project_id = kwargs.pop("project_id", None) or self.cfg.tracker.pipeline[self.name].get("project_id", None)
            username = kwargs.pop("username", None) or self.cfg.tracker.get("username", None)
            dag_name = kwargs.pop("dag_name", None) or self.cfg.tracker.pipeline[self.name].get("dag_name", None)
            tags = kwargs.pop("tags", None) or self.cfg.tracker.pipeline[self.name].get("tags", None)
            api_url = kwargs.pop("api_url", None) or self.cfg.tracker.get("api_url", None)
            ui_url = kwargs.pop("ui_url", None) or self.cfg.tracker.get("ui_url", None)

            if project_id is None:
                raise ValueError("Please provide a project_id if you want to use the tracker")

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

    def run(self, environment: str = "prod", executor: str|None = None,
            inputs: dict|None = None, final_vars: list|None = None,
            with_tracker: bool|None = None, **kwargs) -> Any:
       

        logger.info(f"Starting pipeline {self.name} in environment {environment}")

        run_params = getattr(self.cfg.pipeline.run, self.name)[environment]

        final_vars = final_vars or run_params.get("final_vars", [])
        inputs = {**(run_params.get("inputs", {}) or {}), **(inputs or {})}
        with_tracker = with_tracker or run_params.get("with_tracker", False)

        dr, shutdown = self._get_driver(pipeline=self.name, executor=executor, with_tracker=with_tracker, **kwargs)

        res = dr.execute(final_vars=final_vars, inputs=unmunchify(inputs))

        logger.success(f"Finished pipeline {self.name}")

        if shutdown is not None:
            shutdown()

        return res

    def schedule(self, environment: str = "prod", executor: str|None = None,
                 type: str = "cron", auto_start: bool = True, background: bool = False,
                 inputs: dict|None = None, final_vars: list|None = None,
                 with_tracker: bool|None = None, **kwargs):
        if get_scheduler is None:
            raise ValueError("APScheduler not installed. Please install it first.")

    
        start_time = kwargs.pop("start_time", dt.datetime.now()) or self.cfg.scheduler.pipeline[pipeline].get("start_time", dt.datetime.now())
        end_time = kwargs.pop("end_time", None) or self.cfg.scheduler.pipeline[pipeline].get("end_time", None)

        scheduler = get_scheduler(conf_path=self._conf_path, pipelines_path=self._pipeline_path)
        trigger = self._get_trigger(type, self.cfg.scheduler.pipeline[pipeline], start_time, end_time, **kwargs)

        id_ = scheduler.add_schedule(
            self.run,
            trigger=trigger,
            args=(pipeline, environment, executor, inputs, final_vars, with_tracker),
            kwargs=kwargs,
        )
        logger.success(f"Added scheduler for {pipeline} in environment {environment} with id {id_}")
        
        if auto_start:
            if background:
                scheduler.start_in_background()
                return scheduler, id_
            else:
                scheduler.run_until_stopped()

    def _get_trigger(self, type: str, start_time: dt.datetime, end_time: Optional[dt.datetime], **kwargs):
        if type == "cron":
            return self._get_cron_trigger(self.cfg.scheduler.pipeline[pipeline], start_time, end_time, **kwargs)
        elif type == "interval":
            return self._get_interval_trigger(self.cfg.scheduler.pipeline[pipeline], start_time, end_time, **kwargs)
        elif type == "calendar":
            return self._get_calendar_trigger(self.cfg.scheduler.pipeline[pipeline], start_time, end_time, **kwargs)
        elif type == "date":
            return self._get_date_trigger(start_time)
        else:
            raise ValueError(f"Unknown trigger type: {type}")

    def _get_cron_trigger(self, self.cfg.scheduler.pipeline[pipeline]: Dict, start_time: dt.datetime, end_time: Optional[dt.datetime], **kwargs):
        from apscheduler.triggers.cron import CronTrigger
        crontab = kwargs.pop("crontab", None) or self.cfg.scheduler.pipeline[pipeline].get("crontab", None)
        if crontab is not None:
            return CronTrigger.from_crontab(crontab)
        else:
            return CronTrigger(
                year=kwargs.pop("year", None) or self.cfg.scheduler.pipeline[pipeline].get("year", None),
                month=kwargs.pop("month", None) or self.cfg.scheduler.pipeline[pipeline].get("month", None),
                week=kwargs.pop("week", None) or self.cfg.scheduler.pipeline[pipeline].get("week", None),
                day=kwargs.pop("day", None) or self.cfg.scheduler.pipeline[pipeline].get("day", None),
                day_of_week=kwargs.pop("days_of_week", None) or self.cfg.scheduler.pipeline[pipeline].get("days_of_week", None),
                hour=kwargs.pop("hour", None) or self.cfg.scheduler.pipeline[pipeline].get("hour", None),
                minute=kwargs.pop("minute", None) or self.cfg.scheduler.pipeline[pipeline].get("minute", None),
                second=kwargs.pop("second", None) or self.cfg.scheduler.pipeline[pipeline].get("second", None),
                start_time=start_time,
                end_time=end_time,
                timezone=kwargs.pop("timezone", tz.gettz("Europe/Berlin")) or self.cfg.scheduler.pipeline[pipeline].get("timezone", tz.gettz("Europe/Berlin")),
            )

    def _get_interval_trigger(self, self.cfg.scheduler.pipeline[pipeline]: Dict, start_time: dt.datetime, end_time: Optional[dt.datetime], **kwargs):
        from apscheduler.triggers.interval import IntervalTrigger
        return IntervalTrigger(
            weeks=kwargs.pop("weeks", 0) or self.cfg.scheduler.pipeline[pipeline].get("weeks", 0),
            days=kwargs.pop("days", 0) or self.cfg.scheduler.pipeline[pipeline].get("days", 0),
            hours=kwargs.pop("hours", 0) or self.cfg.scheduler.pipeline[pipeline].get("hours", 0),
            minutes=kwargs.pop("minutes", 0) or self.cfg.scheduler.pipeline[pipeline].get("minutes", 0),
            seconds=kwargs.pop("seconds", 0) or self.cfg.scheduler.pipeline[pipeline].get("seconds", 0),
            microseconds=kwargs.pop("microseconds", 0) or self.cfg.scheduler.pipeline[pipeline].get("microseconds", 0),
            start_time=start_time,
            end_time=end_time,
        )

    def _get_calendar_trigger(self, self.cfg.scheduler.pipeline[pipeline]: Dict, start_time: dt.datetime, end_time: Optional[dt.datetime], **kwargs):
        from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger
        return CalendarIntervalTrigger(
            weeks=kwargs.pop("weeks", 0) or self.cfg.scheduler.pipeline[pipeline].get("weeks", 0),
            days=kwargs.pop("days", 0) or self.cfg.scheduler.pipeline[pipeline].get("days", 0),
            hours=kwargs.pop("hours", 0) or self.cfg.scheduler.pipeline[pipeline].get("hours", 0),
            minutes=kwargs.pop("minutes", 0) or self.cfg.scheduler.pipeline[pipeline].get("minutes", 0),
            seconds=kwargs.pop("seconds", 0) or self.cfg.scheduler.pipeline[pipeline].get("seconds", 0),
            start_time=start_time,
            end_time=end_time,
            timezone=kwargs.pop("timezone", tz.gettz("Europe/Berlin")) or self.cfg.scheduler.pipeline[pipeline].get("timezone", tz.gettz("Europe/Berlin")),
        )

    def _get_date_trigger(self, start_time: dt.datetime):
        from apscheduler.triggers.date import DateTrigger
        return DateTrigger(run_time=start_time)

    def add(self, name: str, overwrite: bool = False, params: dict|None = None,
            run: dict|None = None, schedule: dict|None = None,
            tracker: dict|None = None):
        logger.info(f"Creating new pipeline {name}")

        if not os.path.exists(self._conf_path):
            raise ValueError(f"Configuration path {self._conf_path} does not exist. Please run flowerpower init first.")
        if not os.path.exists(self._pipeline_path):
            raise ValueError(f"Pipeline path {self._pipeline_path} does not exist. Please run flowerpower init first.")

        if os.path.exists(f"{self._pipeline_path}/{name}.py") and not overwrite:
            raise ValueError(f"Pipeline {name} already exists. Use `overwrite=True` to overwrite.")

        os.makedirs(self._pipeline_path, exist_ok=True)
        with open(f"{self._pipeline_path}/{name}.py", "w") as f:
            f.write(PIPELINE_PY_TEMPLATE.format(name=name, date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        logger.info(f"Created pipeline module {name}.py")

        self._update_pipeline_config(name, params, run)
        self._update_scheduler_config(name, schedule)
        self._update_tracker_config(name, tracker)

        logger.success(f"Created pipeline {name}")

    def _update_pipeline_config(self, name: str, params: dict|None, run: dict|None):
        pipeline_cfg = load_pipeline_cfg(path=self._conf_path) or munchify({"run": {}, "params": {}})
        if pipeline_cfg.params is None:
            pipeline_cfg.params = {}
        if pipeline_cfg.run is None:
            pipeline_cfg.run = {}

        pipeline_cfg.params[name] = params or None
        pipeline_cfg.run[name] = run or munchify({
            "dev": {"inputs": None, "final_vars": None, "with_tracker": False},
            "prod": {"inputs": None, "final_vars": None, "with_tracker": True},
        })

        write(pipeline_cfg, "pipeline", self._conf_path)
        logger.info(f"Updated pipeline configuration {self._conf_path}/pipeline.yml")

    def _update_scheduler_config(self, name: str, schedule: dict|None):
        self.cfg.scheduler = load_self.cfg.scheduler(path=self._conf_path) or munchify({
            "data_store": {"type": "memory"},
            "event_broker": {"type": "local"},
            "pipeline": {},
        })
        if self.cfg.scheduler.pipeline is None:
            self.cfg.scheduler.pipeline = {}
        self.cfg.scheduler.pipeline[name] = schedule or {"type": None}

        write(self.cfg.scheduler, "scheduler", self._conf_path)
        logger.info(f"Updated scheduler configuration {self._conf_path}/scheduler.yml")

    def _update_tracker_config(self, name: str, tracker: dict|None):
        tracker_cfg = load_tracker_cfg(path=self._conf_path) or munchify({
            "username": None,
            "api_url": "http://localhost:8241",
            "ui_url": "http://localhost:8242",
            "api_key": None,
            "pipeline": {},
        })
        if tracker_cfg.pipeline is None:
            tracker_cfg.pipeline = {}

        tracker_cfg.pipeline[name] = tracker or {
            "project_id": None,
            "dag_name": None,
            "tags": None,
        }

        write(tracker_cfg, "tracker", self._conf_path)
        logger.info(f"Updated tracker configuration {self._conf_path}/tracker.yml")

    def delete(self):
        # TODO: Implement delete functionality
        pass

    def show(self, pipeline: str, format: str = "png", view: bool = False):
        os.makedirs("graphs", exist_ok=True)
        dr, _ = self._get_driver(pipeline=pipeline, executor=None, with_tracker=False)
        if view:
            pass