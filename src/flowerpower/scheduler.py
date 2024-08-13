import sys
import importlib.util

if importlib.util.find_spec("apscheduler"):
    from apscheduler import Scheduler, current_scheduler
    from apscheduler.executors.async_ import AsyncJobExecutor
    from apscheduler.executors.thread import ThreadPoolJobExecutor
    from apscheduler.executors.subprocess import ProcessPoolJobExecutor

else:
    raise ImportError(
        "APScheduler is not installed. Please install it using `pip install"
        "'apscheduler>4.0.0a1'`, 'conda install apscheduler4' or `pip install flowerpower[scheduler]`"
    )

from .cfg import Config
import os
from loguru import logger
import uuid
from typing import Any


class SchedulerManager(Scheduler):
    def __init__(
        self,
        name: str | None = None,
        base_path: str | None = None,
        # conf_path: str | None = None,
        # pipelines_path: str = None,
    ):
        self.name = name

        if base_path is None:
            base_path = os.getcwd()

        self._base_path = base_path
        self._conf_path = os.path.join(base_path, "conf")  # or conf_path
        self._pipelines_path = os.path.join(base_path, "pipelines")  # or pipelines_path

        self.cfg = Config(path=self._conf_path).scheduler
        self._data_store = None
        self._event_broker = None
        self._sqla_engine = None
        # self.scheduler = None
        self.init_scheduler()

        sys.path.append(self._pipelines_path)

    def setup_data_store(self):
        if "data_store" in self.cfg:
            if "type" in self.cfg.data_store:
                if self.cfg.data_store.type == "sqlalchemy":
                    self._setup_sqlalchemy_data_store()
                elif self.cfg.data_store.type == "mongodb":
                    self._setup_mongodb_data_store()
                else:
                    self._setup_memory_data_store()

    def _setup_sqlalchemy_data_store(self):
        from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
        from sqlalchemy.ext.asyncio import create_async_engine

        if "url" not in self.cfg.data_store:
            raise ValueError("No URL specified for SQLAlchemy data_store")
        self._sqla_engine = create_async_engine(self.cfg.data_store.url)
        self._data_store = SQLAlchemyDataStore(engine_or_url=self._sqla_engine)

    def _setup_mongodb_data_store(self):
        from apscheduler.datastores.mongodb import MongoDBDataStore

        if "url" not in self.cfg.data_store:
            raise ValueError("No URL specified for MongoDB data_store")
        self._data_store = MongoDBDataStore(self.cfg.data_store.url)

    def _setup_memory_data_store(self):
        from apscheduler.datastores.memory import MemoryDataStore

        self._data_store = MemoryDataStore()

    def setup_event_broker(self):
        if "event_broker" in self.cfg:
            if "type" in self.cfg.event_broker:
                if self.cfg.event_broker.type == "asyncpg":
                    self._setup_asyncpg_event_broker()
                elif self.cfg.event_broker.type == "mqtt":
                    self._setup_mqtt_event_broker()
                elif self.cfg.event_broker.type == "redis":
                    self._setup_redis_event_broker()
                else:
                    self._setup_local_event_broker()

    def _setup_asyncpg_event_broker(self):
        from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

        if self._sqla_engine is None:
            if "url" not in self.cfg.event_broker:
                raise ValueError("No URL specified for AsyncPG event broker")
            self._event_broker = AsyncpgEventBroker.from_dsn(
                dsn=self.cfg.event_broker.url
            )
        else:
            self._event_broker = AsyncpgEventBroker.from_async_sqla_engine(
                engine=self._sqla_engine
            )

    def _setup_mqtt_event_broker(self):
        from apscheduler.eventbrokers.mqtt import MQTTEventBroker

        host = self.cfg.event_broker.get("host", "localhost")
        port = self.cfg.event_broker.get("port", 1883)
        self._event_broker = MQTTEventBroker(host, port, topic="flowerpower/scheduler")
        if "username" in self.cfg.event_broker and "password" in self.cfg.event_broker:
            self._event_broker._client.username_pw_set(
                self.cfg.event_broker.username,
                self.cfg.event_broker.password,
            )

    def _setup_redis_event_broker(self):
        from apscheduler.eventbrokers.redis import RedisEventBroker

        if "host" in self.cfg.event_broker:
            port = self.cfg.event_broker.get("port", 6379)
            self.cfg.event_broker.url = f"redis://{self.cfg.event_broker.host}:{port}"
        url = self.cfg.event_broker.get("url", "redis://localhost:6379")
        self._event_broker = RedisEventBroker(url)

    def _setup_local_event_broker(self):
        from apscheduler.eventbrokers.local import LocalEventBroker

        self._event_broker = LocalEventBroker()

    def setup_job_executors(self):
        self._job_executors = {
            "async": AsyncJobExecutor(),
            "threadpool": ThreadPoolJobExecutor(),
            "processpool": ProcessPoolJobExecutor(),
        }

    def init_scheduler(self, **kwargs):
        self.setup_data_store()
        self.setup_event_broker()
        self.setup_job_executors()
        super().__init__(
            data_store=self._data_store,
            event_broker=self._event_broker,
            job_executors=self._job_executors,
            identity=self.name,
            logger=logger,
            **kwargs,
        )
        # return self.scheduler

    def start_worker(self, background: bool = False, *args, **kwargs):
        # if not self.scheduler:
        #    self.init_scheduler(*args, **kwargs)
        if background:
            self.start_in_background()
        else:
            self.run_until_stopped()
        # return self.scheduler

    # def get_current_scheduler(self):
    #    self = current_scheduler.get()

    # def stop_scheduler(self):
    #     if not self.scheduler:
    #         self.get_current_scheduler()
    #     self.scheduler.stop()

    def remove_all_schedules(self):
        for sched in self.get_schedules():
            self.remove_schedule(sched.id)
        # return self.scheduler

    # def add_schedule(self, *args, **kwargs) -> str:
    #     if not self.scheduler:
    #         self.init_scheduler()
    #     return self.scheduler.add_schedule(*args, **kwargs)
    #     # return self.scheduler

    # def add_job(self, *args, **kwargs) -> str:
    #     if not self.scheduler:
    #         self.init_scheduler()
    #     return self.scheduler.add_job(*args, **kwargs)

    # def run_job(self, *args, **kwargs) -> Any:
    #     if not self.scheduler:
    #         self.init_scheduler()
    #     return self.scheduler.run_job(*args, **kwargs)
    #     # return self.scheduler

    # def get_job_result(self, job_id: str) -> Any:
    #     if not self.scheduler:
    #         self.init_scheduler()
    #     return self.scheduler.get_job_result(job_id)

    # def get_jobs(self) -> Any:
    #     if not self.scheduler:
    #         self.init_scheduler()
    #     return self.scheduler.get_jobs()

    # def get_schedules(self) -> Any:
    #     if not self.scheduler:
    #         self.init_scheduler()
    #     return self.scheduler.get_schedules()

    # def get_schedule(self, schedule_id: str) -> Any:
    #     if not self.scheduler:
    #         self.init_scheduler()
    #     return self.scheduler.get_schedule(schedule_id)

    # def get_tasks(
    #     self,
    # ) -> Any:
    #     if not self.scheduler:
    #         self.init_scheduler()
    #     return self.scheduler.get_tasks()


# Wrapper functions for backward compatibility
def get_schedule_manager(
    name: str | None = None,
    base_path: str | None = None,
    *args,
    **kwargs,
) -> SchedulerManager:
    manager = SchedulerManager(name, base_path)
    manager.init_scheduler(*args, **kwargs)
    return manager


def get_current_scheduler_manager() -> SchedulerManager | None:
    return current_scheduler.get()


def get_scheduler(
    name: str | None = None,
    base_path: str | None = None,
    *args,
    **kwargs,
) -> Scheduler:
    manager = get_schedule_manager(name, base_path, *args, **kwargs)
    return manager.scheduler


def start_scheduler(
    name: str | None = None,
    base_path: str | None = None,
    background: bool = False,
    *args,
    **kwargs,
) -> Scheduler:
    manager = get_schedule_manager(name, base_path, *args, **kwargs)
    manager.start_worker(background)
    return manager.scheduler


def get_current_scheduler() -> Scheduler | None:
    return SchedulerManager.get_current_scheduler()


def remove_all_schedules(
    name: str | None = None,
    base_path: str | None = None,
    *args,
    **kwargs,
):
    manager = get_schedule_manager(name, base_path, *args, **kwargs)
    return manager.remove_all_schedules()


def add_schedule(
    name: str | None = None,
    base_path: str | None = None,
    *args,
    **kwargs,
) -> uuid.UUID:
    manager = SchedulerManager(name, base_path)
    id_ = manager.add_schedule(*args, **kwargs)
    return id_, manager


def add_job(
    name: str | None = None,
    base_path: str | None = None,
    *args,
    **kwargs,
) -> uuid.UUID:
    manager = SchedulerManager(name, base_path)
    id_ = manager.add_job(*args, **kwargs)
    return id_, manager


def run_job(
    name: str | None = None,
    base_path: str | None = None,
    *args,
    **kwargs,
) -> Any:
    manager = SchedulerManager(name, base_path)
    manager.run_job(*args, **kwargs)
    return manager
